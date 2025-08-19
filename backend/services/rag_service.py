from typing import List, Optional, Tuple
import asyncio
import time
import logging
from langchain.llms import OpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma, FAISS
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.config import settings
from models.schemas import Article, ArticleResponse
from .embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class RAGService:
    """RAG (Retrieval Augmented Generation) 서비스"""
    
    def __init__(self):
        self.llm = None
        self.embeddings = None
        self.vector_store = None
        self.text_splitter = None
        self.embedding_service = EmbeddingService()
        self.initialized = False
    
    async def initialize(self):
        """서비스 초기화"""
        try:
            # Initialize OpenAI LLM
            if settings.OPENAI_API_KEY:
                self.llm = OpenAI(
                    openai_api_key=settings.OPENAI_API_KEY,
                    model_name=settings.OPENAI_MODEL,
                    temperature=0.7
                )
                
                self.embeddings = OpenAIEmbeddings(
                    openai_api_key=settings.OPENAI_API_KEY,
                    model=settings.OPENAI_EMBEDDING_MODEL
                )
            
            # Initialize text splitter
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP,
                separators=["\n\n", "\n", ".", "!", "?", " ", ""]
            )
            
            # Initialize vector store based on config
            await self._initialize_vector_store()
            
            self.initialized = True
            logger.info("RAG Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG Service: {e}")
            raise
    
    async def _initialize_vector_store(self):
        """벡터 스토어 초기화"""
        try:
            if settings.VECTOR_DB_TYPE.lower() == "chroma":
                self.vector_store = Chroma(
                    persist_directory=settings.VECTOR_DB_PATH,
                    embedding_function=self.embeddings
                )
            elif settings.VECTOR_DB_TYPE.lower() == "faiss":
                # FAISS implementation would go here
                pass
            else:
                logger.warning(f"Unknown vector DB type: {settings.VECTOR_DB_TYPE}")
                
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            # Continue without vector store for basic functionality
            self.vector_store = None
    
    async def add_documents_to_vector_store(
        self, 
        articles: List[Article]
    ) -> bool:
        """문서를 벡터 스토어에 추가"""
        if not self.vector_store or not self.embeddings:
            logger.warning("Vector store or embeddings not initialized")
            return False
        
        try:
            documents = []
            for article in articles:
                # Split article content into chunks
                chunks = self.text_splitter.split_text(article.content)
                
                for i, chunk in enumerate(chunks):
                    doc = Document(
                        page_content=chunk,
                        metadata={
                            "article_id": article.id,
                            "title": article.title,
                            "source": article.source,
                            "category": article.category,
                            "url": article.url,
                            "chunk_index": i,
                            "total_chunks": len(chunks)
                        }
                    )
                    documents.append(doc)
            
            # Add documents to vector store
            if documents:
                self.vector_store.add_documents(documents)
                logger.info(f"Added {len(documents)} document chunks to vector store")
                return True
            
        except Exception as e:
            logger.error(f"Failed to add documents to vector store: {e}")
            return False
        
        return False
    
    async def generate_answer(
        self,
        question: str,
        context_limit: int = 5,
        model: Optional[str] = None,
        db_session: Optional[AsyncSession] = None
    ) -> Tuple[str, List[ArticleResponse], float]:
        """
        RAG를 사용하여 질문에 대한 답변 생성
        
        Args:
            question: 사용자 질문
            context_limit: 컨텍스트로 사용할 문서 수
            model: 사용할 LLM 모델 (선택사항)
            db_session: 데이터베이스 세션
            
        Returns:
            답변, 소스 문서들, 신뢰도 점수
        """
        if not self.initialized:
            raise Exception("RAG Service not initialized")
        
        try:
            start_time = time.time()
            
            # 1. Retrieve relevant documents
            relevant_docs = await self._retrieve_relevant_documents(
                question, context_limit
            )
            
            # 2. Generate context from retrieved documents
            context = self._build_context_from_documents(relevant_docs)
            
            # 3. Generate answer using LLM
            answer = await self._generate_llm_answer(question, context, model)
            
            # 4. Get source articles
            source_articles = await self._get_source_articles(
                relevant_docs, db_session
            )
            
            # 5. Calculate confidence score (simplified)
            confidence_score = self._calculate_confidence_score(
                question, answer, relevant_docs
            )
            
            processing_time = time.time() - start_time
            logger.info(f"RAG answer generated in {processing_time:.2f}s")
            
            return answer, source_articles, confidence_score
            
        except Exception as e:
            logger.error(f"Failed to generate RAG answer: {e}")
            raise Exception("답변 생성 중 오류가 발생했습니다.")
    
    async def _retrieve_relevant_documents(
        self, 
        question: str, 
        limit: int
    ) -> List[Document]:
        """관련 문서 검색"""
        if not self.vector_store:
            return []
        
        try:
            # Use vector store similarity search
            docs = self.vector_store.similarity_search(
                question, 
                k=limit
            )
            return docs
            
        except Exception as e:
            logger.error(f"Failed to retrieve documents: {e}")
            return []
    
    def _build_context_from_documents(self, docs: List[Document]) -> str:
        """문서들로부터 컨텍스트 구성"""
        if not docs:
            return ""
        
        context_parts = []
        for i, doc in enumerate(docs, 1):
            title = doc.metadata.get('title', 'Unknown')
            content = doc.page_content
            
            context_part = f"[문서 {i}: {title}]\n{content}\n"
            context_parts.append(context_part)
        
        return "\n".join(context_parts)
    
    async def _generate_llm_answer(
        self,
        question: str,
        context: str,
        model: Optional[str] = None
    ) -> str:
        """LLM을 사용하여 답변 생성"""
        if not self.llm:
            return "LLM이 초기화되지 않았습니다."
        
        try:
            # Build prompt
            prompt = f"""
다음 문서들을 참고하여 질문에 답변해주세요.

컨텍스트:
{context}

질문: {question}

답변 가이드라인:
- 제공된 문서의 정보만을 활용하여 답변하세요
- 정확하고 구체적인 답변을 제공하세요
- 답변의 근거가 되는 문서를 언급하세요
- 불확실한 정보는 추측하지 마세요

답변:"""

            # Generate answer
            response = await asyncio.get_event_loop().run_in_executor(
                None, self.llm, prompt
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Failed to generate LLM answer: {e}")
            return "답변 생성 중 오류가 발생했습니다."
    
    async def _get_source_articles(
        self, 
        docs: List[Document],
        db_session: Optional[AsyncSession]
    ) -> List[ArticleResponse]:
        """소스 기사들 가져오기"""
        if not docs or not db_session:
            return []
        
        try:
            article_ids = list(set([
                doc.metadata.get('article_id') 
                for doc in docs 
                if doc.metadata.get('article_id')
            ]))
            
            if not article_ids:
                return []
            
            stmt = select(Article).where(Article.id.in_(article_ids))
            result = await db_session.execute(stmt)
            articles = result.scalars().all()
            
            return [ArticleResponse.model_validate(article) for article in articles]
            
        except Exception as e:
            logger.error(f"Failed to get source articles: {e}")
            return []
    
    def _calculate_confidence_score(
        self,
        question: str,
        answer: str,
        docs: List[Document]
    ) -> float:
        """신뢰도 점수 계산 (간단한 구현)"""
        # This is a simplified implementation
        # In production, you might use more sophisticated methods
        
        if not docs or not answer:
            return 0.0
        
        # Basic confidence based on number of source documents
        doc_confidence = min(len(docs) / 5.0, 1.0)  # Max confidence at 5 docs
        
        # Basic confidence based on answer length
        answer_confidence = min(len(answer) / 200.0, 1.0)  # Max at 200 chars
        
        # Average the scores
        confidence = (doc_confidence + answer_confidence) / 2.0
        
        return round(confidence, 2)


# Global instance
rag_service = RAGService()
