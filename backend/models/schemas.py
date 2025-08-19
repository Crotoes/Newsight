from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from core.db import BaseModel as DBBaseModel


# SQLAlchemy Models (Database)
class User(DBBaseModel):
    __tablename__ = "users"
    
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Relationships
    summaries = relationship("Summary", back_populates="user")


class Article(DBBaseModel):
    __tablename__ = "articles"
    
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    title = Column(String, nullable=False, index=True)
    content = Column(Text, nullable=False)
    url = Column(String, unique=True, index=True)
    source = Column(String, index=True)  # news, paper
    category = Column(String, index=True)  # technology, science, etc.
    author = Column(String)
    published_at = Column(DateTime)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    
    # Metadata
    meta_data = Column(JSON)  # Additional metadata (renamed to avoid conflict)
    embedding_processed = Column(Boolean, default=False)
    
    # Relationships
    summaries = relationship("Summary", back_populates="article")
    vector_embeddings = relationship("VectorEmbedding", back_populates="article")


class Summary(DBBaseModel):
    __tablename__ = "summaries"
    
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Summary content
    summary_text = Column(Text, nullable=False)
    key_points = Column(JSON)  # List of key points
    analysis = Column(Text)  # Detailed analysis
    sentiment = Column(String)  # positive, negative, neutral
    confidence_score = Column(Float)
    
    # Generation metadata
    model_used = Column(String)  # Model name used for generation
    prompt_version = Column(String)
    generation_time = Column(Float)  # Time taken to generate
    
    # Relationships
    article = relationship("Article", back_populates="summaries")
    user = relationship("User", back_populates="summaries")


class VectorEmbedding(DBBaseModel):
    __tablename__ = "vector_embeddings"
    
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    
    # Embedding data
    chunk_text = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    embedding_vector = Column(JSON)  # Store as JSON array
    model_used = Column(String)  # Embedding model name
    
    # Relationships
    article = relationship("Article", back_populates="vector_embeddings")


# Pydantic Models (API)
class ArticleBase(BaseModel):
    title: str
    content: str
    url: Optional[str] = None
    source: str = "manual"
    category: Optional[str] = None
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    meta_data: Optional[Dict[str, Any]] = None


class ArticleCreate(ArticleBase):
    pass


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    author: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None


class ArticleResponse(ArticleBase):
    id: int
    uuid: str
    scraped_at: datetime
    embedding_processed: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class SummaryBase(BaseModel):
    summary_text: str
    key_points: Optional[List[str]] = None
    analysis: Optional[str] = None
    sentiment: Optional[str] = None
    confidence_score: Optional[float] = None


class SummaryCreate(SummaryBase):
    article_id: int
    user_id: Optional[int] = None


class SummaryResponse(SummaryBase):
    id: int
    uuid: str
    article_id: int
    user_id: Optional[int] = None
    model_used: Optional[str] = None
    prompt_version: Optional[str] = None
    generation_time: Optional[float] = None
    created_at: datetime
    
    model_config = {"from_attributes": True}


class UserBase(BaseModel):
    email: str
    username: str
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    uuid: str
    created_at: datetime
    
    model_config = {"from_attributes": True}


# Search and RAG related models
class SearchQuery(BaseModel):
    query: str = Field(..., description="검색 쿼리")
    source_filter: Optional[str] = Field(None, description="소스 필터 (news, paper)")
    category_filter: Optional[str] = Field(None, description="카테고리 필터")
    limit: int = Field(10, ge=1, le=50, description="결과 개수 제한")
    include_summary: bool = Field(True, description="요약 포함 여부")


class SearchResult(BaseModel):
    articles: List[ArticleResponse]
    summaries: Optional[List[SummaryResponse]] = None
    total_count: int
    query_time: float
    
    
class RAGQuery(BaseModel):
    question: str = Field(..., description="질문")
    context_limit: int = Field(5, ge=1, le=20, description="컨텍스트로 사용할 문서 수")
    model: Optional[str] = Field(None, description="사용할 LLM 모델")


class RAGResponse(BaseModel):
    answer: str
    source_articles: List[ArticleResponse]
    confidence_score: float
    processing_time: float