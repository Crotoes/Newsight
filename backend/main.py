from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import logging
from dotenv import load_dotenv
import os

from api import search
from core.config import settings
from core.db import init_db

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("Starting Newsight application...")
    
    # Initialize database
    await init_db()
    
    yield
    
    logger.info("Shutting down Newsight application...")

# Create FastAPI application
app = FastAPI(
    title="Newsight",
    description="RAG와 LLM을 활용한 뉴스/논문 요약 & 해설 서비스",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(search.router, prefix="/api/v1/search", tags=["search"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Newsight API",
        "version": "1.0.0",
        "description": "RAG와 LLM을 활용한 뉴스/논문 요약 & 해설 서비스"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "newsight"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )