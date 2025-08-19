"""
임베딩 서비스 - TYPE_CHECKING을 사용한 임포트 경고 완전 해결
"""
from typing import List, Optional, TYPE_CHECKING
import logging
import asyncio

# 타입 체킹 시에만 임포트 (실제 런타임에는 임포트되지 않음)
if TYPE_CHECKING:
    from openai import OpenAI  # type: ignore
    from sentence_transformers import SentenceTransformer  # type: ignore
    import numpy as np  # type: ignore

logger = logging.getLogger(__name__)

class EmbeddingService:
    """임베딩 생성 서비스 - 런타임 임포트로 의존성 경고 해결"""
    
    def __init__(self):
        self._openai_client: Optional["OpenAI"] = None
        self._sentence_model: Optional["SentenceTransformer"] = None
        self._openai_available = False
        self._sentence_transformers_available = False
        self._numpy_available = False
        
    def _check_openai_availability(self) -> bool:
        """OpenAI 라이브러리 사용 가능 여부 확인"""
        if self._openai_available:
            return True
            
        try:
            import openai  # type: ignore # noqa: F401
            from ..core.config import settings
            
            if not settings.openai_api_key:
                logger.warning("OpenAI API key not configured")
                return False
                
            self._openai_available = True
            return True
            
        except ImportError:
            logger.info("OpenAI library not installed. Install with: pip install -e '.[ai]'")
            return False

    def _get_openai_client(self) -> Optional["OpenAI"]:
        """OpenAI 클라이언트 가져오기"""
        if self._openai_client:
            return self._openai_client
            
        if not self._check_openai_availability():
            return None
            
        try:
            from openai import OpenAI  # type: ignore
            from ..core.config import settings
            
            self._openai_client = OpenAI(api_key=settings.openai_api_key)
            logger.info("OpenAI client initialized")
            return self._openai_client
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            return None

    def _check_sentence_transformers_availability(self) -> bool:
        """Sentence Transformers 라이브러리 사용 가능 여부 확인"""
        if self._sentence_transformers_available:
            return True
            
        try:
            import sentence_transformers  # type: ignore # noqa: F401
            self._sentence_transformers_available = True
            return True
        except ImportError:
            logger.info("sentence-transformers not installed. Install with: pip install -e '.[ai]'")
            return False

    def _get_sentence_transformer(self) -> Optional["SentenceTransformer"]:
        """Sentence Transformer 모델 가져오기"""
        if self._sentence_model:
            return self._sentence_model
            
        if not self._check_sentence_transformers_availability():
            return None
            
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore
            
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
            self._sentence_model = SentenceTransformer(model_name)
            logger.info(f"Sentence transformer model loaded: {model_name}")
            return self._sentence_model
            
        except Exception as e:
            logger.error(f"Failed to load sentence transformer: {e}")
            return None

    def _check_numpy_availability(self) -> bool:
        """NumPy 라이브러리 사용 가능 여부 확인"""
        if self._numpy_available:
            return True
            
        try:
            import numpy  # type: ignore # noqa: F401
            self._numpy_available = True
            return True
        except ImportError:
            logger.info("NumPy not available. Install with: pip install -e '.[ai]'")
            return False

    async def generate_embedding_openai(
        self, text: str, model: str = "text-embedding-ada-002"
    ) -> Optional[List[float]]:
        """OpenAI를 사용한 임베딩 생성"""
        client = self._get_openai_client()
        if not client:
            return None
            
        try:
            response = await asyncio.to_thread(
                client.embeddings.create,
                input=[text],
                model=model
            )
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"OpenAI embedding generation failed: {e}")
            return None

    async def generate_embedding_local(self, text: str) -> Optional[List[float]]:
        """로컬 모델을 사용한 임베딩 생성"""
        model = self._get_sentence_transformer()
        if not model:
            return None
            
        try:
            embedding = await asyncio.to_thread(model.encode, text)
            return embedding.tolist()
            
        except Exception as e:
            logger.error(f"Local embedding generation failed: {e}")
            return None

    async def generate_embedding(
        self, text: str, use_openai: bool = True
    ) -> Optional[List[float]]:
        """임베딩 생성 (OpenAI 우선, 실패시 로컬 모델)"""
        if use_openai:
            embedding = await self.generate_embedding_openai(text)
            if embedding:
                return embedding
                
        # OpenAI 실패 또는 비활성화시 로컬 모델 시도
        return await self.generate_embedding_local(text)

    async def compute_similarity(
        self, embedding1: List[float], embedding2: List[float]
    ) -> float:
        """두 임베딩 간 코사인 유사도 계산"""
        if not self._check_numpy_availability():
            logger.warning("NumPy not available for similarity calculation")
            return 0.0
            
        try:
            import numpy as np  # type: ignore
            
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
                
            return float(dot_product / (norm1 * norm2))
            
        except Exception as e:
            logger.error(f"Similarity calculation failed: {e}")
            return 0.0

    async def find_similar_embeddings(
        self, 
        query_embedding: List[float], 
        embeddings: List[List[float]], 
        top_k: int = 5
    ) -> List[int]:
        """쿼리 임베딩과 유사한 임베딩들의 인덱스 반환"""
        if not embeddings:
            return []
            
        try:
            similarities = []
            for i, embedding in enumerate(embeddings):
                similarity = await self.compute_similarity(query_embedding, embedding)
                similarities.append((i, similarity))
                
            # 유사도 기준으로 정렬하고 top_k 반환
            similarities.sort(key=lambda x: x[1], reverse=True)
            return [idx for idx, _ in similarities[:top_k]]
            
        except Exception as e:
            logger.error(f"Similar embedding search failed: {e}")
            return []

    def get_status(self) -> dict:
        """서비스 상태 정보 반환"""
        return {
            "openai_available": self._check_openai_availability(),
            "sentence_transformers_available": self._check_sentence_transformers_availability(),
            "numpy_available": self._check_numpy_availability(),
            "openai_client_loaded": self._openai_client is not None,
            "sentence_model_loaded": self._sentence_model is not None,
        }
