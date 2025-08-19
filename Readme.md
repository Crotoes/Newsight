# 🔍 Newsight

**RAG와 LLM을 활용한 뉴스/논문 요약 & 해설 서비스**

Newsight는 최신 뉴스와 학술 논문을 자동으로 수집하고, AI를 활용하여 핵심 내용을 요약하며, 사용자의 질문에 대해 관련 문서를 기반으로 답변을 제공하는 서비스입니다.

## 🚀 현재 상태

✅ **완료된 기능들**
- FastAPI 기반 백엔드 서버 (http://localhost:8000)
- SQLite 데이터베이스 (PostgreSQL 지원)
- RESTful API 엔드포인트
- 자동 API 문서화 (http://localhost:8000/docs)
- 선택적 의존성 관리 (pyproject.toml)
- TYPE_CHECKING을 통한 import 경고 해결
- 서비스별 모듈화된 아키텍처

🔄 **구현된 서비스들**
- 임베딩 서비스 (OpenAI + Sentence Transformers)
- 스크래핑 서비스 (뉴스 + 논문)
- 요약 서비스 (AI 기반)
- RAG 서비스 (문서 검색 + 답변 생성)

## ✨ 주요 기능

- 🗞️ **뉴스 자동 수집**: RSS 피드를 통한 실시간 뉴스 수집
- 📄 **논문 자동 수집**: arXiv 등에서 최신 학술 논문 수집
- 🤖 **AI 요약**: OpenAI GPT를 활용한 지능적인 요약 생성
- 🔍 **의미 검색**: 벡터 임베딩을 활용한 의미 기반 검색
- 💬 **RAG 기반 Q&A**: 수집된 문서를 기반으로 한 질의응답
- 📊 **감정 분석**: 기사의 감정 톤 분석
- ⚡ **실시간 처리**: 백그라운드 작업을 통한 자동 업데이트

## 🏗️ 시스템 아키텍처

```
Frontend (React/Next.js)
    ↕
Backend (FastAPI)
    ├── API Layer (검색, RAG, 요약)
    ├── Services Layer (스크래핑, 임베딩, 요약)
    ├── Database Layer (PostgreSQL)
    ├── Vector Store (ChromaDB/FAISS)
    └── Background Tasks (Celery + Redis)
```

## 🛠️ 기술 스택

### Backend
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **Vector DB**: ChromaDB / FAISS
- **Cache/Queue**: Redis
- **Background Tasks**: Celery
- **AI/ML**: OpenAI GPT, LangChain, Sentence Transformers

### Frontend
- **Framework**: Next.js / React
- **Styling**: Tailwind CSS
- **State Management**: Zustand

## 🚀 설치 및 실행

### 1. 환경 설정

```bash
# 1. 저장소 클론
git clone https://github.com/Crotoes/Newsight.git
cd Newsight

# 2. Python 환경 설정
conda create -n newsight python=3.12
conda activate newsight

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 환경 변수 설정
cp backend/.env.example backend/.env
# .env 파일을 편집하여 API 키 등을 설정
```

### 2. 데이터베이스 설정

```bash
# PostgreSQL 설치 및 데이터베이스 생성
createdb newsight

# Redis 설치 및 실행
redis-server
```

### 3. 백엔드 실행

```bash
# 메인 API 서버 실행
cd backend
python main.py

# 백그라운드 작업자 실행 (별도 터미널)
celery -A scheduler.tasks worker --loglevel=info

# 스케줄러 실행 (별도 터미널)
celery -A scheduler.tasks beat --loglevel=info
```

### 4. 프론트엔드 실행

```bash
cd frontend
npm install
npm run dev
```

## 📡 API 엔드포인트

### 검색 API
- `GET /api/v1/search/` - 키워드 검색
- `POST /api/v1/search/semantic` - 의미 기반 검색
- `POST /api/v1/search/rag` - RAG 기반 질의응답
- `GET /api/v1/search/suggestions` - 검색 제안
- `GET /api/v1/search/trending` - 트렌딩 토픽

### 기본 엔드포인트
- `GET /` - API 정보
- `GET /health` - 헬스 체크

## 🔧 구성 요소

### 서비스 레이어

1. **ScrapingService** (`services/scraping_service.py`)
   - RSS 피드 파싱
   - 웹 스크래핑
   - arXiv 논문 수집

2. **SummaryService** (`services/summary_service.py`)
   - AI 요약 생성
   - 핵심 포인트 추출
   - 감정 분석

3. **EmbeddingService** (`services/embedding_service.py`)
   - 텍스트 임베딩 생성
   - 유사도 계산
   - 벡터 검색

4. **RAGService** (`services/rag_service.py`)
   - 문서 검색
   - 컨텍스트 구성
   - LLM 답변 생성

### 백그라운드 작업

- **뉴스 스크래핑**: 1시간마다 실행
- **논문 스크래핑**: 1일마다 실행
- **임베딩 업데이트**: 1일마다 실행

## 🗄️ 데이터베이스 스키마

### 주요 테이블
- **articles**: 수집된 뉴스/논문
- **summaries**: AI 생성 요약
- **users**: 사용자 정보
- **vector_embeddings**: 벡터 임베딩

## 🔐 환경 변수

```env
# OpenAI API
OPENAI_API_KEY=your_key_here

# Database
DATABASE_URL=postgresql://user:pass@localhost/newsight

# Redis
REDIS_URL=redis://localhost:6379
```

## 📊 모니터링 및 로깅

- 구조화된 로깅 (JSON 형태)
- 성능 메트릭 수집
- 에러 추적 및 알림

## 🚧 개발 로드맵

- [ ] 사용자 인증 시스템
- [ ] 개인화 추천 시스템
- [ ] 다국어 지원
- [ ] 모바일 앱
- [ ] 고급 분석 대시보드

## 🤝 기여하기

1. Fork 프로젝트
2. Feature 브랜치 생성 (`git checkout -b feature/AmazingFeature`)
3. 변경사항 커밋 (`git commit -m 'Add some AmazingFeature'`)
4. 브랜치에 Push (`git push origin feature/AmazingFeature`)
5. Pull Request 생성

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 문의

프로젝트에 대한 문의사항이나 제안이 있으시면 이슈를 생성해주세요.

---
⭐ 이 프로젝트가 도움이 되셨다면 스타를 눌러주세요!