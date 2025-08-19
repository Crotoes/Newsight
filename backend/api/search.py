from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import List, Optional
import time
import logging

from core.db import get_db
from models.schemas import (
    Article, Summary, 
    SearchQuery, SearchResult, 
    RAGQuery, RAGResponse,
    ArticleResponse, SummaryResponse
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Placeholder services for now
rag_service = None
embedding_service = None


@router.get("/", response_model=SearchResult)
async def search_articles(
    query: str = Query(..., description="검색 쿼리"),
    source_filter: Optional[str] = Query(None, description="소스 필터 (news, paper)"),
    category_filter: Optional[str] = Query(None, description="카테고리 필터"),
    limit: int = Query(10, ge=1, le=50, description="결과 개수 제한"),
    include_summary: bool = Query(True, description="요약 포함 여부"),
    db: AsyncSession = Depends(get_db)
):
    """
    기사 검색 API
    - 키워드 기반 검색
    - 소스 및 카테고리 필터링
    - 요약 정보 포함 옵션
    """
    start_time = time.time()
    
    try:
        # Build query
        stmt = select(Article).where(
            or_(
                Article.title.ilike(f"%{query}%"),
                Article.content.ilike(f"%{query}%")
            )
        )
        
        # Apply filters
        if source_filter:
            stmt = stmt.where(Article.source == source_filter)
        
        if category_filter:
            stmt = stmt.where(Article.category == category_filter)
        
        # Execute query with limit
        stmt = stmt.limit(limit).order_by(Article.created_at.desc())
        result = await db.execute(stmt)
        articles = result.scalars().all()
        
        # Get total count
        count_stmt = select(func.count(Article.id)).where(
            or_(
                Article.title.ilike(f"%{query}%"),
                Article.content.ilike(f"%{query}%")
            )
        )
        if source_filter:
            count_stmt = count_stmt.where(Article.source == source_filter)
        if category_filter:
            count_stmt = count_stmt.where(Article.category == category_filter)
            
        count_result = await db.execute(count_stmt)
        total_count = count_result.scalar()
        
        # Convert to response models
        article_responses = [
            ArticleResponse.model_validate(article) for article in articles
        ]
        
        summaries = None
        if include_summary:
            # Get summaries for found articles
            article_ids = [article.id for article in articles]
            if article_ids:
                summary_stmt = select(Summary).where(
                    Summary.article_id.in_(article_ids)
                )
                summary_result = await db.execute(summary_stmt)
                summary_list = summary_result.scalars().all()
                summaries = [
                    SummaryResponse.model_validate(summary) for summary in summary_list
                ]
        
        query_time = time.time() - start_time
        
        return SearchResult(
            articles=article_responses,
            summaries=summaries,
            total_count=total_count,
            query_time=query_time
        )
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail="검색 중 오류가 발생했습니다.")


@router.post("/semantic", response_model=SearchResult)
async def semantic_search(
    search_query: SearchQuery,
    db: AsyncSession = Depends(get_db)
):
    """
    의미 기반 검색 API (벡터 검색)
    - 임베딩을 활용한 의미 기반 검색
    - 유사도 기반 결과 반환
    """
    start_time = time.time()
    
    try:
        # TODO: Implement semantic search using embedding service
        # This is a placeholder implementation
        
        if not embedding_service:
            raise HTTPException(
                status_code=503, 
                detail="임베딩 서비스가 초기화되지 않았습니다."
            )
        
        # Get query embedding
        query_embedding = await embedding_service.get_embedding(search_query.query)
        
        # Find similar documents (placeholder)
        # In real implementation, use vector database
        similar_articles = []  # TODO: Implement vector search
        
        query_time = time.time() - start_time
        
        return SearchResult(
            articles=similar_articles,
            summaries=None,
            total_count=len(similar_articles),
            query_time=query_time
        )
        
    except Exception as e:
        logger.error(f"Semantic search error: {e}")
        raise HTTPException(status_code=500, detail="의미 검색 중 오류가 발생했습니다.")


@router.post("/rag", response_model=RAGResponse)
async def rag_query(
    rag_query: RAGQuery,
    db: AsyncSession = Depends(get_db)
):
    """
    RAG 기반 질문 답변 API
    - 검색된 문서를 컨텍스트로 활용
    - LLM을 통한 답변 생성
    """
    start_time = time.time()
    
    try:
        if not rag_service:
            raise HTTPException(
                status_code=503,
                detail="RAG 서비스가 초기화되지 않았습니다."
            )
        
        # Use RAG service to generate answer
        answer, source_articles, confidence = await rag_service.generate_answer(
            question=rag_query.question,
            context_limit=rag_query.context_limit,
            model=rag_query.model
        )
        
        processing_time = time.time() - start_time
        
        return RAGResponse(
            answer=answer,
            source_articles=source_articles,
            confidence_score=confidence,
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"RAG query error: {e}")
        raise HTTPException(status_code=500, detail="답변 생성 중 오류가 발생했습니다.")


@router.get("/suggestions")
async def get_search_suggestions(
    query: str = Query(..., min_length=1),
    limit: int = Query(5, ge=1, le=10),
    db: AsyncSession = Depends(get_db)
):
    """
    검색 제안 API
    - 실시간 검색어 제안
    - 인기 검색어 및 관련 키워드
    """
    try:
        # Get article titles and keywords that match query
        stmt = select(Article.title).where(
            Article.title.ilike(f"%{query}%")
        ).limit(limit)
        
        result = await db.execute(stmt)
        suggestions = [title for (title,) in result.fetchall()]
        
        return {"suggestions": suggestions, "query": query}
        
    except Exception as e:
        logger.error(f"Suggestions error: {e}")
        raise HTTPException(status_code=500, detail="제안 검색 중 오류가 발생했습니다.")


@router.get("/trending")
async def get_trending_topics(
    limit: int = Query(10, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    """
    인기 토픽 API
    - 최근 인기 기사 및 키워드
    - 트렌딩 토픽 분석
    """
    try:
        # Get recent popular articles (simplified)
        stmt = select(Article).order_by(
            Article.created_at.desc()
        ).limit(limit)
        
        result = await db.execute(stmt)
        trending_articles = result.scalars().all()
        
        article_responses = [
            ArticleResponse.model_validate(article) for article in trending_articles
        ]
        
        return {
            "trending_articles": article_responses,
            "generated_at": time.time()
        }
        
    except Exception as e:
        logger.error(f"Trending topics error: {e}")
        raise HTTPException(status_code=500, detail="트렌딩 토픽 조회 중 오류가 발생했습니다.")