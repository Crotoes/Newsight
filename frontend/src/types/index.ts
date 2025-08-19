// API 응답 타입
export interface Article {
  id: number;
  title: string;
  content: string;
  summary?: string;
  url: string;
  published_date: string;
  author?: string;
  source?: string;
  category?: string;
  image_url?: string;
  tags: string[];
  created_at: string;
  updated_at: string;
}

export interface Summary {
  id: number;
  article_id: number;
  content: string;
  summary_type: 'brief' | 'detailed' | 'key_points';
  created_at: string;
  article?: Article;
}

export interface User {
  id: number;
  email: string;
  username: string;
  created_at: string;
  is_active: boolean;
}

export interface VectorEmbedding {
  id: number;
  article_id: number;
  embedding: number[];
  model_name: string;
  created_at: string;
  article?: Article;
}

// API 요청/응답 타입
export interface SearchRequest {
  query: string;
  limit?: number;
  offset?: number;
}

export interface SearchResponse {
  results: Article[];
  total: number;
  query: string;
  took_ms: number;
}

export interface RAGRequest {
  question: string;
  max_articles?: number;
  include_sources?: boolean;
}

export interface RAGResponse {
  answer: string;
  sources: Article[];
  confidence: number;
  took_ms: number;
}

// 컴포넌트 프롭스 타입
export interface ArticleCardProps {
  article: Article;
  onSummary?: (articleId: number) => void;
  showSummary?: boolean;
}

export interface SearchBarProps {
  onSearch: (query: string) => void;
  placeholder?: string;
  loading?: boolean;
}

export interface SummaryCardProps {
  summary: Summary;
  article?: Article;
}

// 상태 관리 타입
export interface AppState {
  user: User | null;
  articles: Article[];
  summaries: Summary[];
  loading: boolean;
  error: string | null;
}

export interface SearchState {
  query: string;
  results: Article[];
  loading: boolean;
  error: string | null;
  hasMore: boolean;
  total: number;
}

export interface RAGState {
  question: string;
  answer: string | null;
  sources: Article[];
  loading: boolean;
  error: string | null;
  confidence: number;
}

// API 클라이언트 타입
export interface ApiError {
  message: string;
  status: number;
  code?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// 유틸리티 타입
export type SortOrder = 'asc' | 'desc';
export type SortField = 'created_at' | 'published_date' | 'title';

export interface SortOptions {
  field: SortField;
  order: SortOrder;
}

export interface FilterOptions {
  tags?: string[];
  author?: string;
  category?: string;
  search?: string;
  dateFrom?: string;
  dateTo?: string;
}
