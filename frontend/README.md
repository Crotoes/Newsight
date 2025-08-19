# Newsight Frontend

Newsight 프론트엔드는 Next.js 14와 React 18을 기반으로 한 현대적인 웹 애플리케이션입니다.

## 기술 스택

### 핵심 프레임워크
- **Next.js 14**: React 프레임워크 (App Router 사용)
- **React 18**: UI 라이브러리
- **TypeScript**: 타입 안전성

### 스타일링
- **Tailwind CSS**: 유틸리티 CSS 프레임워크
- **PostCSS**: CSS 후처리기
- **Autoprefixer**: 브라우저 호환성

### 상태 관리 & 데이터 페칭
- **Zustand**: 클라이언트 상태 관리
- **TanStack Query (React Query)**: 서버 상태 관리
- **Axios**: HTTP 클라이언트

### UI/UX
- **Heroicons**: 아이콘 라이브러리
- **React Hot Toast**: 알림 시스템
- **date-fns**: 날짜 포맷팅

### 개발 도구
- **ESLint**: 코드 품질 검사
- **TypeScript ESLint**: TypeScript 린팅
- **React Query Devtools**: 개발 도구

## 프로젝트 구조

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx          # 루트 레이아웃
│   │   ├── page.tsx            # 홈페이지
│   │   └── globals.css         # 글로벌 스타일
│   ├── components/             # React 컴포넌트
│   │   ├── ui/                 # 재사용 가능한 UI 컴포넌트
│   │   ├── ArticleCard.tsx     # 기사 카드
│   │   ├── ArticleList.tsx     # 기사 목록
│   │   ├── SearchBar.tsx       # 검색바
│   │   └── Layout.tsx          # 레이아웃 컴포넌트
│   ├── hooks/                  # 커스텀 훅
│   │   ├── useArticles.ts      # 기사 관련 훅
│   │   └── useCommon.ts        # 공통 훅
│   ├── lib/                    # 라이브러리 및 유틸리티
│   │   └── api.ts              # API 클라이언트
│   ├── providers/              # Context 프로바이더
│   │   └── index.tsx           # React Query & Toast 프로바이더
│   ├── store/                  # Zustand 스토어
│   │   └── index.ts            # 상태 스토어
│   └── types/                  # TypeScript 타입 정의
│       └── index.ts            # 공통 타입
├── public/                     # 정적 자산
├── .eslintrc.json             # ESLint 설정
├── next.config.js             # Next.js 설정
├── package.json               # 의존성 및 스크립트
├── postcss.config.js          # PostCSS 설정
├── tailwind.config.js         # Tailwind CSS 설정
└── tsconfig.json              # TypeScript 설정
```

## 주요 기능

### 1. 검색 기능
- 실시간 검색
- 검색어 디바운싱
- 로딩 상태 표시
- 검색 결과 캐싱

### 2. 기사 표시
- 그리드 레이아웃
- 반응형 디자인
- 이미지 최적화
- 무한 스크롤 (준비 중)

### 3. AI 요약
- 기사 요약 표시
- 요약 상태 표시
- 원문 링크 제공

### 4. 사용자 경험
- 다크/라이트 모드 대응
- 오프라인 상태 감지
- 키보드 단축키
- 클립보드 복사
- 로컬 스토리지 활용

## 시작하기

### 1. 의존성 설치

```bash
cd frontend
npm install
```

### 2. 개발 서버 실행

```bash
npm run dev
```

### 3. 빌드

```bash
npm run build
npm run start
```

### 4. 타입 체크

```bash
npm run type-check
```

### 5. 린팅

```bash
npm run lint
```

## API 통합

### 백엔드 연결
- 프록시 설정으로 CORS 문제 해결
- Axios 인터셉터로 에러 처리
- React Query로 캐싱 및 재요청 관리

### 환경 변수
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Newsight
```

## 성능 최적화

### 1. 코드 분할
- Next.js 자동 코드 분할
- 동적 import 활용
- 페이지별 번들 최적화

### 2. 이미지 최적화
- Next.js Image 컴포넌트
- WebP 포맷 지원
- 반응형 이미지

### 3. 캐싱 전략
- React Query 캐싱
- 로컬 스토리지 활용
- 브라우저 캐시 최적화

## 배포

### Vercel (권장)
```bash
npm install -g vercel
vercel
```

### Docker
```bash
docker build -t newsight-frontend .
docker run -p 3000:3000 newsight-frontend
```

### 정적 배포
```bash
npm run build
npm run export
```

## 개발 가이드라인

### 1. 컴포넌트 작성
- 함수형 컴포넌트 사용
- Props 인터페이스 정의
- 재사용성 고려

### 2. 스타일링
- Tailwind CSS 클래스 사용
- 반응형 디자인 적용
- 일관된 색상 팔레트

### 3. 상태 관리
- 로컬 상태: useState, useReducer
- 글로벌 상태: Zustand
- 서버 상태: React Query

### 4. 에러 처리
- Error Boundary 활용
- Toast 알림 사용
- 사용자 친화적 에러 메시지

## 트러블슈팅

### 1. TypeScript 에러
```bash
# 타입 정의 재설치
npm install --save-dev @types/react @types/react-dom @types/node
```

### 2. 빌드 에러
```bash
# 캐시 클리어
rm -rf .next
npm run build
```

### 3. 스타일링 이슈
```bash
# Tailwind CSS 재빌드
npm run build
```

## 참고 자료

- [Next.js 문서](https://nextjs.org/docs)
- [React 문서](https://react.dev)
- [Tailwind CSS 문서](https://tailwindcss.com/docs)
- [React Query 문서](https://tanstack.com/query/latest)
- [Zustand 문서](https://github.com/pmndrs/zustand)
