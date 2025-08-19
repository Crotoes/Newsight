import { Article } from '@/types';
import { ArticleCard } from './ArticleCard';
import { Spinner } from './ui/Spinner';

interface ArticleListProps {
  articles: Article[];
  loading?: boolean;
  error?: string | null;
  onLoadMore?: () => void;
  hasMore?: boolean;
  loadingMore?: boolean;
}

export function ArticleList({
  articles,
  loading = false,
  error = null,
  onLoadMore,
  hasMore = false,
  loadingMore = false,
}: ArticleListProps) {
  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <div className="text-red-500 text-lg font-semibold mb-4">오류가 발생했습니다</div>
        <div className="text-gray-600 text-sm">{error}</div>
      </div>
    );
  }

  if (!articles || articles.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <div className="text-gray-500 text-lg font-semibold mb-2">검색 결과가 없습니다</div>
        <div className="text-gray-400 text-sm">다른 키워드로 검색해보세요</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 기사 목록 */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {articles.map((article) => (
          <ArticleCard key={article.id} article={article} />
        ))}
      </div>

      {/* 더 보기 버튼 */}
      {hasMore && onLoadMore && (
        <div className="flex justify-center py-6">
          <button
            onClick={onLoadMore}
            disabled={loadingMore}
            className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 
                     disabled:opacity-50 disabled:cursor-not-allowed transition-colors
                     flex items-center space-x-2"
          >
            {loadingMore ? (
              <>
                <Spinner size="sm" />
                <span>로딩 중...</span>
              </>
            ) : (
              <span>더 보기</span>
            )}
          </button>
        </div>
      )}

      {/* 로딩 더 표시 */}
      {loadingMore && (
        <div className="flex justify-center py-6">
          <Spinner size="md" />
        </div>
      )}
    </div>
  );
}
