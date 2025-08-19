"""
Newsight 서비스 테스트 스크립트
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(__file__))

from services.embedding_service import embedding_service
from services.scraping_service import scraping_service

async def test_embedding_service():
    """임베딩 서비스 테스트"""
    print("=== Embedding Service Test ===")
    
    try:
        # Initialize service
        await embedding_service.initialize(use_openai=False)
        print(f"✓ Service initialized: {embedding_service.current_model}")
        
        # Test single embedding
        test_text = "이것은 테스트 텍스트입니다."
        embedding = await embedding_service.get_embedding(test_text)
        
        if embedding:
            print(f"✓ Embedding generated: dimension={len(embedding)}")
        else:
            print("✗ Failed to generate embedding")
        
        # Test similarity
        if embedding:
            test_text2 = "이것은 다른 테스트 텍스트입니다."
            embedding2 = await embedding_service.get_embedding(test_text2)
            
            if embedding2:
                similarity = embedding_service.calculate_similarity(embedding, embedding2)
                print(f"✓ Similarity calculated: {similarity:.3f}")
        
        # Get model info
        info = embedding_service.get_model_info()
        print(f"✓ Model info: {info}")
        
    except Exception as e:
        print(f"✗ Embedding service test failed: {e}")

async def test_scraping_service():
    """스크래핑 서비스 테스트"""
    print("\n=== Scraping Service Test ===")
    
    try:
        # Test basic functionality (without actual scraping)
        print("✓ Scraping service imported successfully")
        
        # Test with mock data
        from services.scraping_service import ScrapedArticle
        from datetime import datetime
        
        mock_article = ScrapedArticle(
            title="Test Article",
            content="This is test content",
            url="http://example.com",
            source="Test Source",
            category="Test",
            published_at=datetime.now()
        )
        
        print(f"✓ ScrapedArticle created: {mock_article.title}")
        
    except Exception as e:
        print(f"✗ Scraping service test failed: {e}")

async def main():
    """메인 테스트 함수"""
    print("Newsight Services Test\n")
    
    await test_embedding_service()
    await test_scraping_service()
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    asyncio.run(main())
