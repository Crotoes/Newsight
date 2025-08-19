import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { articleApi } from '@/lib/api';
import type { Article, Summary, SortOptions, FilterOptions, PaginatedResponse } from '@/types';

// 기사 목록 조회 훅
export function useArticles(
  page: number = 1,
  size: number = 20,
  sort?: SortOptions,
  filters?: FilterOptions
) {
  return useQuery({
    queryKey: ['articles', page, size, sort, filters],
    queryFn: () => articleApi.getArticles(page, size, sort, filters),
    staleTime: 5 * 60 * 1000, // 5분
  });
}

// 기사 검색 훅 (페이지에서 사용)
export function useArticleSearch(options: {
  query: string;
  enabled?: boolean;
  category?: string;
  page?: number;
  limit?: number;
}) {
  const { query, enabled = true, category, page = 1, limit = 20 } = options;
  
  return useQuery({
    queryKey: ['articles', 'search', { query, category, page, limit }],
    queryFn: async () => {
      const params = new URLSearchParams({
        query,
        limit: limit.toString(),
      });
      
      if (category) {
        params.append('category_filter', category);
      }
      
      const response = await fetch(`/api/v1/search?${params}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    },
    enabled: Boolean(enabled && query),
    staleTime: 1000 * 60 * 5, // 5분
  });
}

// 기사 상세 조회 훅
export function useArticle(id: number) {
  return useQuery({
    queryKey: ['article', id],
    queryFn: () => articleApi.getArticle(id),
    enabled: !!id,
    staleTime: 10 * 60 * 1000, // 10분
  });
}

// 기사 요약 목록 조회 훅
export function useArticleSummaries(articleId: number) {
  return useQuery({
    queryKey: ['article-summaries', articleId],
    queryFn: () => articleApi.getArticleSummaries(articleId),
    enabled: !!articleId,
    staleTime: 15 * 60 * 1000, // 15분
  });
}

// 기사 요약 생성 뮤테이션 훅
export function useCreateSummary() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ articleId, summaryType }: { 
      articleId: number; 
      summaryType: 'brief' | 'detailed' | 'key_points' 
    }) => articleApi.createSummary(articleId, summaryType),
    
    onSuccess: (data, variables) => {
      // 기사 요약 목록 캐시 무효화
      queryClient.invalidateQueries(['article-summaries', variables.articleId]);
      
      // 새 요약을 캐시에 추가
      queryClient.setQueryData(
        ['article-summaries', variables.articleId], 
        (oldData: Summary[] | undefined) => {
          if (oldData) {
            return [...oldData, data];
          }
          return [data];
        }
      );
    },
  });
}
