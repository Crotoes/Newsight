from typing import List, Optional, Dict, Any, Tuple
import asyncio
import time
import logging
from dataclasses import dataclass
from langchain.llms import OpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.prompts import PromptTemplate
import openai
import re

from core.config import settings
from models.schemas import Article, Summary, SummaryCreate

logger = logging.getLogger(__name__)


@dataclass
class SummaryResult:
    """요약 결과 데이터 클래스"""
    summary_text: str
    key_points: List[str]
    analysis: str
    sentiment: str
    confidence_score: float
    model_used: str
    generation_time: float


class SummaryService:
    """기사/논문 요약 생성 서비스"""
    
    def __init__(self):
        self.llm = None
        self.text_splitter = None
        self.initialized = False
        
        # 프롬프트 템플릿들
        self.summary_prompt = PromptTemplate(
            input_variables=["text"],
            template="""
다음 텍스트를 읽고 포괄적이고 정확한 요약을 작성해주세요.

원문:
{text}

요약 작성 가이드라인:
1. 핵심 내용과 주요 포인트를 포함하세요
2. 객관적이고 중립적인 톤을 유지하세요
3. 3-5문장의 간결한 요약을 작성하세요
4. 전문 용어는 쉽게 설명하세요

요약:"""
        )
        
        self.key_points_prompt = PromptTemplate(
            input_variables=["text"],
            template="""
다음 텍스트에서 핵심 포인트들을 추출해주세요.

원문:
{text}

핵심 포인트 추출 가이드라인:
1. 가장 중요한 3-5개의 포인트를 선별하세요
2. 각 포인트는 한 문장으로 표현하세요
3. 구체적이고 실용적인 정보를 우선시하세요
4. 번호나 불릿 포인트 없이 각 라인에 하나씩 작성하세요

핵심 포인트:"""
        )
        
        self.analysis_prompt = PromptTemplate(
            input_variables=["text", "summary"],
            template="""
다음 텍스트와 요약을 바탕으로 심층 분석을 제공해주세요.

원문: {text}

요약: {summary}

분석 가이드라인:
1. 배경 컨텍스트와 중요성을 설명하세요
2. 잠재적인 영향과 시사점을 논의하세요
3. 관련 분야나 이해관계자에게 미칠 영향을 분석하세요
4. 객관적이고 균형잡힌 관점을 유지하세요
5. 2-3문단으로 작성하세요

심층 분석:"""
        )
    
    async def initialize(self):
        """서비스 초기화"""
        try:
            if settings.OPENAI_API_KEY:
                self.llm = OpenAI(
                    openai_api_key=settings.OPENAI_API_KEY,
                    model_name=settings.OPENAI_MODEL,
                    temperature=0.3,  # 요약에는 낮은 temperature 사용
                    max_tokens=1000
                )
            
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP,
                separators=["\n\n", "\n", ".", "!", "?", " ", ""]
            )
            
            self.initialized = True
            logger.info("Summary Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Summary Service: {e}")
            raise
    
    async def generate_summary(
        self, 
        article: Article,
        user_id: Optional[int] = None,
        include_analysis: bool = True
    ) -> SummaryResult:
        """
        기사의 종합 요약 생성
        
        Args:
            article: 요약할 기사
            user_id: 사용자 ID (선택적)
            include_analysis: 심층 분석 포함 여부
            
        Returns:
            SummaryResult 객체
        """
        if not self.initialized:
            await self.initialize()
        
        if not self.llm:
            raise Exception("LLM이 초기화되지 않았습니다.")
        
        start_time = time.time()
        
        try:
            # 1. 기본 요약 생성
            summary_text = await self._generate_basic_summary(article.content)
            
            # 2. 핵심 포인트 추출
            key_points = await self._extract_key_points(article.content)
            
            # 3. 감정 분석
            sentiment = await self._analyze_sentiment(article.content)
            
            # 4. 심층 분석 (선택적)
            analysis = ""
            if include_analysis:
                analysis = await self._generate_analysis(article.content, summary_text)
            
            # 5. 신뢰도 점수 계산
            confidence_score = self._calculate_confidence_score(
                article.content, summary_text, key_points
            )
            
            generation_time = time.time() - start_time
            
            return SummaryResult(
                summary_text=summary_text,
                key_points=key_points,
                analysis=analysis,
                sentiment=sentiment,
                confidence_score=confidence_score,
                model_used=settings.OPENAI_MODEL,
                generation_time=generation_time
            )
            
        except Exception as e:
            logger.error(f"Failed to generate summary for article {article.id}: {e}")
            raise Exception("요약 생성 중 오류가 발생했습니다.")
    
    async def _generate_basic_summary(self, text: str) -> str:
        """기본 요약 생성"""
        try:
            # 텍스트가 너무 긴 경우 청킹
            if len(text) > settings.CHUNK_SIZE:
                chunks = self.text_splitter.split_text(text)
                
                # 각 청크를 요약하고 결합
                chunk_summaries = []
                for chunk in chunks[:3]:  # 최대 3개 청크만 처리
                    chunk_summary = await self._summarize_chunk(chunk)
                    if chunk_summary:
                        chunk_summaries.append(chunk_summary)
                
                # 청크 요약들을 최종 요약으로 결합
                if chunk_summaries:
                    combined_text = " ".join(chunk_summaries)
                    final_summary = await self._summarize_chunk(combined_text)
                    return final_summary if final_summary else chunk_summaries[0]
            else:
                return await self._summarize_chunk(text)
            
        except Exception as e:
            logger.error(f"Failed to generate basic summary: {e}")
            return "요약 생성 중 오류가 발생했습니다."
    
    async def _summarize_chunk(self, text: str) -> str:
        """텍스트 청크 요약"""
        try:
            prompt = self.summary_prompt.format(text=text)
            
            response = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.llm(prompt)
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Failed to summarize chunk: {e}")
            return ""
    
    async def _extract_key_points(self, text: str) -> List[str]:
        """핵심 포인트 추출"""
        try:
            # 텍스트가 너무 긴 경우 앞부분만 사용
            if len(text) > settings.CHUNK_SIZE:
                text = text[:settings.CHUNK_SIZE]
            
            prompt = self.key_points_prompt.format(text=text)
            
            response = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.llm(prompt)
            )
            
            # 응답을 줄별로 분할하여 리스트로 변환
            key_points = [
                point.strip() 
                for point in response.split('\n') 
                if point.strip() and not point.strip().startswith('-') and not point.strip().startswith('•')
            ]
            
            # 빈 문자열이나 너무 짧은 포인트 제거
            key_points = [point for point in key_points if len(point) > 10]
            
            return key_points[:5]  # 최대 5개까지
            
        except Exception as e:
            logger.error(f"Failed to extract key points: {e}")
            return []
    
    async def _generate_analysis(self, text: str, summary: str) -> str:
        """심층 분석 생성"""
        try:
            # 텍스트가 너무 긴 경우 요약을 기반으로 분석
            analysis_text = text
            if len(text) > settings.CHUNK_SIZE:
                analysis_text = text[:settings.CHUNK_SIZE] + "..."
            
            prompt = self.analysis_prompt.format(text=analysis_text, summary=summary)
            
            response = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.llm(prompt)
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Failed to generate analysis: {e}")
            return ""
    
    async def _analyze_sentiment(self, text: str) -> str:
        """감정 분석"""
        try:
            # 간단한 키워드 기반 감정 분석 (실제로는 더 정교한 모델 사용 가능)
            text_lower = text.lower()
            
            positive_words = [
                'good', 'great', 'excellent', 'positive', 'success', 'achievement',
                'breakthrough', 'improvement', 'growth', 'benefit', 'advantage'
            ]
            
            negative_words = [
                'bad', 'terrible', 'negative', 'failure', 'problem', 'issue',
                'concern', 'risk', 'threat', 'decline', 'loss', 'disadvantage'
            ]
            
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            if positive_count > negative_count + 2:
                return "positive"
            elif negative_count > positive_count + 2:
                return "negative"
            else:
                return "neutral"
                
        except Exception as e:
            logger.error(f"Failed to analyze sentiment: {e}")
            return "neutral"
    
    def _calculate_confidence_score(
        self, 
        original_text: str, 
        summary_text: str, 
        key_points: List[str]
    ) -> float:
        """신뢰도 점수 계산"""
        try:
            score = 0.5  # 기본 점수
            
            # 요약 길이 기반 점수
            if summary_text and len(summary_text) > 50:
                score += 0.2
            
            # 핵심 포인트 개수 기반 점수
            if len(key_points) >= 3:
                score += 0.2
            
            # 원문 대비 요약 비율
            if len(original_text) > 0 and len(summary_text) > 0:
                ratio = len(summary_text) / len(original_text)
                if 0.1 <= ratio <= 0.5:  # 적절한 압축 비율
                    score += 0.1
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Failed to calculate confidence score: {e}")
            return 0.5
    
    async def batch_generate_summaries(
        self, 
        articles: List[Article],
        include_analysis: bool = True,
        batch_size: int = 5
    ) -> List[SummaryResult]:
        """배치로 여러 기사 요약 생성"""
        all_results = []
        
        for i in range(0, len(articles), batch_size):
            batch_articles = articles[i:i + batch_size]
            batch_tasks = [
                self.generate_summary(article, include_analysis=include_analysis)
                for article in batch_articles
            ]
            
            try:
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                for j, result in enumerate(batch_results):
                    if isinstance(result, Exception):
                        logger.error(f"Failed to summarize article {batch_articles[j].id}: {result}")
                        # 기본 결과 생성
                        all_results.append(self._create_fallback_summary(batch_articles[j]))
                    else:
                        all_results.append(result)
                        
                logger.info(f"Processed batch {i//batch_size + 1}/{(len(articles)-1)//batch_size + 1}")
                
                # 배치 간 대기 (API 제한 고려)
                if i + batch_size < len(articles):
                    await asyncio.sleep(1)
                    
            except Exception as e:
                logger.error(f"Failed to process batch: {e}")
                # 배치 전체에 대해 fallback 결과 생성
                for article in batch_articles:
                    all_results.append(self._create_fallback_summary(article))
        
        return all_results
    
    def _create_fallback_summary(self, article: Article) -> SummaryResult:
        """요약 생성 실패 시 fallback 결과 생성"""
        # 기사 내용의 첫 200자를 요약으로 사용
        content_preview = article.content[:200] + "..." if len(article.content) > 200 else article.content
        
        return SummaryResult(
            summary_text=content_preview,
            key_points=[article.title],
            analysis="자동 분석을 사용할 수 없습니다.",
            sentiment="neutral",
            confidence_score=0.3,
            model_used="fallback",
            generation_time=0.0
        )


# Global instance
summary_service = SummaryService()
