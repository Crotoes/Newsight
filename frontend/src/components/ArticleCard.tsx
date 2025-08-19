import { Article } from '@/types';
import { formatDistanceToNow } from 'date-fns';
import { ko } from 'date-fns/locale';
import { ArrowTopRightOnSquareIcon, ClockIcon } from '@heroicons/react/24/outline';

interface ArticleCardProps {
  article: Article;
  onClick?: (article: Article) => void;
}

export function ArticleCard({ article, onClick }: ArticleCardProps) {
  const handleClick = () => {
    if (onClick) {
      onClick(article);
    }
  };

  return (
    <div
      className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200 
                 border border-gray-200 overflow-hidden cursor-pointer"
      onClick={handleClick}
    >
      {/* 이미지 영역 */}
      {article.image_url && (
        <div className="relative h-48 overflow-hidden">
          <img
            src={article.image_url}
            alt={article.title}
            className="w-full h-full object-cover hover:scale-105 transition-transform duration-200"
            onError={(e) => {
              const target = e.target as HTMLImageElement;
              target.style.display = 'none';
            }}
          />
        </div>
      )}

      {/* 콘텐츠 영역 */}
      <div className="p-6">
        {/* 소스와 날짜 */}
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm font-medium text-primary-600 bg-primary-50 px-2 py-1 rounded-md">
            {article.source}
          </span>
          <div className="flex items-center text-xs text-gray-500">
            <ClockIcon className="w-4 h-4 mr-1" />
            {formatDistanceToNow(new Date(article.published_date), {
              addSuffix: true,
              locale: ko,
            })}
          </div>
        </div>

        {/* 제목 */}
        <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2 leading-tight">
          {article.title}
        </h3>

        {/* 요약 */}
        {article.summary && (
          <p className="text-sm text-gray-600 mb-4 line-clamp-3 leading-relaxed">
            {article.summary}
          </p>
        )}

        {/* 카테고리와 원본 링크 */}
        <div className="flex items-center justify-between">
          <div className="flex flex-wrap gap-2">
            {article.category && (
              <span className="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded-md">
                {article.category}
              </span>
            )}
          </div>
          
          <a
            href={article.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center text-sm text-primary-600 hover:text-primary-700 
                     transition-colors"
            onClick={(e) => e.stopPropagation()}
          >
            <span className="mr-1">원문 보기</span>
            <ArrowTopRightOnSquareIcon className="w-4 h-4" />
          </a>
        </div>
      </div>

      {/* AI 요약 상태 표시 */}
      {article.summary && (
        <div className="px-6 pb-4">
          <div className="flex items-center text-xs text-green-600 bg-green-50 px-2 py-1 rounded-md w-fit">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
            AI 요약 완료
          </div>
        </div>
      )}
    </div>
  );
}
