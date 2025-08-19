import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import type { Article, SearchState, RAGState, ApiError } from '@/types';
import { searchApi, isApiError } from '@/lib/api';

interface SearchStore extends SearchState {
  // 액션들
  setQuery: (query: string) => void;
  setResults: (results: Article[]) => void;
  keywordSearch: (query: string, offset?: number) => Promise<void>;
  semanticSearch: (query: string, offset?: number) => Promise<void>;
  clearResults: () => void;
  clearError: () => void;
}

export const useSearchStore = create<SearchStore>()(
  devtools(
    (set, get) => ({
      // 초기 상태
      query: '',
      results: [],
      loading: false,
      error: null,
      hasMore: true,
      total: 0,

      // 액션들
      setQuery: (query: string) => {
        set({ query });
      },

      setResults: (results: Article[]) => {
        set({ results });
      },

      keywordSearch: async (query: string, offset: number = 0) => {
        const currentResults = offset > 0 ? get().results : [];
        
        set({ 
          loading: true, 
          error: null,
          query: query,
          results: offset === 0 ? [] : currentResults
        });

        try {
          const response = await searchApi.keywordSearch({
            query,
            limit: 20,
            offset,
          });

          set({
            results: offset === 0 ? response.results : [...currentResults, ...response.results],
            total: response.total,
            hasMore: offset + response.results.length < response.total,
            loading: false,
          });
        } catch (error) {
          const errorMessage = isApiError(error) ? error.message : '검색 중 오류가 발생했습니다.';
          set({
            error: errorMessage,
            loading: false,
            hasMore: false,
          });
        }
      },

      semanticSearch: async (query: string, offset: number = 0) => {
        const currentResults = offset > 0 ? get().results : [];
        
        set({ 
          loading: true, 
          error: null,
          query: query,
          results: offset === 0 ? [] : currentResults
        });

        try {
          const response = await searchApi.semanticSearch({
            query,
            limit: 20,
            offset,
          });

          set({
            results: offset === 0 ? response.results : [...currentResults, ...response.results],
            total: response.total,
            hasMore: offset + response.results.length < response.total,
            loading: false,
          });
        } catch (error) {
          const errorMessage = isApiError(error) ? error.message : '시맨틱 검색 중 오류가 발생했습니다.';
          set({
            error: errorMessage,
            loading: false,
            hasMore: false,
          });
        }
      },

      clearResults: () => {
        set({
          results: [],
          total: 0,
          hasMore: true,
          error: null,
        });
      },

      clearError: () => {
        set({ error: null });
      },
    }),
    {
      name: 'search-store',
    }
  )
);

interface RAGStore extends RAGState {
  // 액션들
  setQuestion: (question: string) => void;
  askQuestion: (question: string, maxArticles?: number) => Promise<void>;
  clearAnswer: () => void;
  clearError: () => void;
}

export const useRAGStore = create<RAGStore>()(
  devtools(
    (set, get) => ({
      // 초기 상태
      question: '',
      answer: null,
      sources: [],
      loading: false,
      error: null,
      confidence: 0,

      // 액션들
      setQuestion: (question: string) => {
        set({ question });
      },

      askQuestion: async (question: string, maxArticles: number = 5) => {
        set({ 
          loading: true, 
          error: null,
          question,
          answer: null,
          sources: [],
          confidence: 0,
        });

        try {
          const response = await searchApi.ragSearch({
            question,
            max_articles: maxArticles,
            include_sources: true,
          });

          set({
            answer: response.answer,
            sources: response.sources,
            confidence: response.confidence,
            loading: false,
          });
        } catch (error) {
          const errorMessage = isApiError(error) ? error.message : 'AI 답변 생성 중 오류가 발생했습니다.';
          set({
            error: errorMessage,
            loading: false,
          });
        }
      },

      clearAnswer: () => {
        set({
          answer: null,
          sources: [],
          confidence: 0,
          error: null,
        });
      },

      clearError: () => {
        set({ error: null });
      },
    }),
    {
      name: 'rag-store',
    }
  )
);

// 전역 앱 상태 스토어
interface AppStore {
  // 상태
  sidebarOpen: boolean;
  theme: 'light' | 'dark';
  
  // 액션들
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  setTheme: (theme: 'light' | 'dark') => void;
  toggleTheme: () => void;
}

export const useAppStore = create<AppStore>()(
  devtools(
    persist(
      (set, get) => ({
        // 초기 상태
        sidebarOpen: false,
        theme: 'light',

        // 액션들
        toggleSidebar: () => {
          set({ sidebarOpen: !get().sidebarOpen });
        },

        setSidebarOpen: (open: boolean) => {
          set({ sidebarOpen: open });
        },

        setTheme: (theme: 'light' | 'dark') => {
          set({ theme });
        },

        toggleTheme: () => {
          const newTheme = get().theme === 'light' ? 'dark' : 'light';
          set({ theme: newTheme });
        },
      }),
      {
        name: 'app-store',
        partialize: (state) => ({ theme: state.theme }),
      }
    ),
    {
      name: 'app-store',
    }
  )
);
