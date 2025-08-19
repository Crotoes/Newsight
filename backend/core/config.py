from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Newsight"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "RAG와 LLM을 활용한 뉴스/논문 요약 & 해설 서비스"
    
    # Database Settings
    DATABASE_URL: Optional[str] = None
    POSTGRES_USER: str = "newsight"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "newsight"
    
    # Redis Settings
    REDIS_URL: str = "redis://localhost:6379"
    
    # OpenAI Settings
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-ada-002"
    
    # LangChain Settings
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_API_KEY: Optional[str] = None
    
    # Vector Database Settings
    VECTOR_DB_TYPE: str = "chroma"  # chroma, faiss
    VECTOR_DB_PATH: str = "./data/vector_db"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # Scraping Settings
    NEWS_SOURCES: list = [
        "https://feeds.yna.co.kr/original",
        "https://rss.cnn.com/rss/edition.rss",
        "https://feeds.bbci.co.uk/news/rss.xml"
    ]
    PAPER_SOURCES: list = [
        "https://arxiv.org/rss/cs.AI",
        "https://arxiv.org/rss/cs.CL",
        "https://arxiv.org/rss/cs.LG"
    ]
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600  # 1 hour in seconds
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    @property
    def database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Allow extra environment variables


# Create settings instance
settings = Settings()