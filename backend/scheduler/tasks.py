import asyncio
import logging
from datetime import datetime, timedelta
from typing import List
from celery import Celery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.config import settings
from core.db import AsyncSessionLocal
from models.schemas import Article, Summary
from services.scraping_service import scraping_service, ScrapedArticle
from services.summary_service import summary_service
from services.embedding_service import embedding_service
from services.rag_service import rag_service

logger = logging.getLogger(__name__)

# Celery 앱 생성
celery_app = Celery(
    "newsight",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["scheduler.tasks"]
)

# Celery 설정
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "scrape-news-hourly": {
            "task": "scheduler.tasks.scrape_and_process_news",
            "schedule": 3600.0,  # 1시간마다
        },
        "scrape-papers-daily": {
            "task": "scheduler.tasks.scrape_and_process_papers",
            "schedule": 86400.0,  # 1일마다
        },
        "update-embeddings-daily": {
            "task": "scheduler.tasks.update_embeddings",
            "schedule": 86400.0,  # 1일마다
        },
    },
)


@celery_app.task(bind=True)
def scrape_and_process_news(self):
    """뉴스 스크래핑 및 처리 태스크"""
    try:
        logger.info("Starting news scraping task...")
        asyncio.run(_scrape_and_process_news())
        logger.info("News scraping task completed successfully")
        return {"status": "success", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"News scraping task failed: {e}")
        return {"status": "error", "error": str(e)}


@celery_app.task(bind=True)
def scrape_and_process_papers(self):
    """논문 스크래핑 및 처리 태스크"""
    try:
        logger.info("Starting paper scraping task...")
        asyncio.run(_scrape_and_process_papers())
        logger.info("Paper scraping task completed successfully")
        return {"status": "success", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Paper scraping task failed: {e}")
        return {"status": "error", "error": str(e)}


@celery_app.task(bind=True)
def update_embeddings(self):
    """임베딩 업데이트 태스크"""
    try:
        logger.info("Starting embedding update task...")
        asyncio.run(_update_embeddings())
        logger.info("Embedding update task completed successfully")
        return {"status": "success", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Embedding update task failed: {e}")
        return {"status": "error", "error": str(e)}


async def _scrape_and_process_news():
    """뉴스 스크래핑 및 처리 내부 함수"""
    async with AsyncSessionLocal() as db:
        try:
            # 뉴스 스크래핑
            scraped_data = await scraping_service.scrape_all_sources()
            news_articles = scraped_data.get('news', [])
            
            if not news_articles:
                logger.warning("No news articles scraped")
                return
            
            # 기사 저장
            saved_articles = []
            for scraped_article in news_articles:
                # 중복 확인
                existing = await db.execute(
                    select(Article).where(Article.url == scraped_article.url)
                )
                if existing.scalar():
                    continue
                
                # 새 기사 생성
                article = Article(
                    title=scraped_article.title,
                    content=scraped_article.content,
                    url=scraped_article.url,
                    source=scraped_article.source,
                    category=scraped_article.category,
                    author=scraped_article.author,
                    published_at=scraped_article.published_at,
                    meta_data=scraped_article.meta_data
                )
                
                db.add(article)
                saved_articles.append(article)
            
            await db.commit()
            logger.info(f"Saved {len(saved_articles)} new news articles")
            
            # 요약 생성
            if saved_articles:
                await _generate_summaries_for_articles(saved_articles, db)
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error in news scraping: {e}")
            raise


async def _scrape_and_process_papers():
    """논문 스크래핑 및 처리 내부 함수"""
    async with AsyncSessionLocal() as db:
        try:
            # 논문 스크래핑
            scraped_data = await scraping_service.scrape_all_sources()
            papers = scraped_data.get('papers', [])
            
            if not papers:
                logger.warning("No papers scraped")
                return
            
            # 논문 저장
            saved_papers = []
            for scraped_paper in papers:
                # 중복 확인
                existing = await db.execute(
                    select(Article).where(Article.url == scraped_paper.url)
                )
                if existing.scalar():
                    continue
                
                # 새 논문 생성
                article = Article(
                    title=scraped_paper.title,
                    content=scraped_paper.content,
                    url=scraped_paper.url,
                    source=scraped_paper.source,
                    category=scraped_paper.category,
                    author=scraped_paper.author,
                    published_at=scraped_paper.published_at,
                    meta_data=scraped_paper.meta_data
                )
                
                db.add(article)
                saved_papers.append(article)
            
            await db.commit()
            logger.info(f"Saved {len(saved_papers)} new papers")
            
            # 요약 생성
            if saved_papers:
                await _generate_summaries_for_articles(saved_papers, db)
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error in paper scraping: {e}")
            raise


async def _generate_summaries_for_articles(articles: List[Article], db: AsyncSession):
    """기사들에 대한 요약 생성"""
    try:
        if not summary_service.initialized:
            await summary_service.initialize()
        
        # 배치로 요약 생성
        summary_results = await summary_service.batch_generate_summaries(
            articles, include_analysis=True, batch_size=3
        )
        
        # 요약 저장
        for article, summary_result in zip(articles, summary_results):
            summary = Summary(
                article_id=article.id,
                summary_text=summary_result.summary_text,
                key_points=summary_result.key_points,
                analysis=summary_result.analysis,
                sentiment=summary_result.sentiment,
                confidence_score=summary_result.confidence_score,
                model_used=summary_result.model_used,
                generation_time=summary_result.generation_time,
                prompt_version="v1.0"
            )
            
            db.add(summary)
        
        await db.commit()
        logger.info(f"Generated and saved summaries for {len(articles)} articles")
        
    except Exception as e:
        logger.error(f"Error generating summaries: {e}")
        await db.rollback()


async def _update_embeddings():
    """임베딩 업데이트 내부 함수"""
    async with AsyncSessionLocal() as db:
        try:
            # 임베딩이 처리되지 않은 기사들 가져오기
            stmt = select(Article).where(Article.embedding_processed == False).limit(100)
            result = await db.execute(stmt)
            articles_to_process = result.scalars().all()
            
            if not articles_to_process:
                logger.info("No articles need embedding processing")
                return
            
            # 임베딩 서비스 초기화
            if not embedding_service.initialized:
                await embedding_service.initialize()
            
            # RAG 서비스에 문서 추가
            if not rag_service.initialized:
                await rag_service.initialize()
            
            # 벡터 스토어에 문서 추가
            success = await rag_service.add_documents_to_vector_store(articles_to_process)
            
            if success:
                # 처리 완료 마킹
                for article in articles_to_process:
                    article.embedding_processed = True
                
                await db.commit()
                logger.info(f"Updated embeddings for {len(articles_to_process)} articles")
            else:
                logger.warning("Failed to update embeddings")
            
        except Exception as e:
            logger.error(f"Error updating embeddings: {e}")
            await db.rollback()


# 수동 실행 함수들
async def manual_scrape_news():
    """수동 뉴스 스크래핑"""
    await _scrape_and_process_news()


async def manual_scrape_papers():
    """수동 논문 스크래핑"""
    await _scrape_and_process_papers()


async def manual_update_embeddings():
    """수동 임베딩 업데이트"""
    await _update_embeddings()


# Celery worker 실행 명령어:
# celery -A scheduler.tasks worker --loglevel=info
# 
# Celery beat (스케줄러) 실행 명령어:
# celery -A scheduler.tasks beat --loglevel=info
