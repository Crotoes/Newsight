'use client';

import React from 'react';
import { Layout } from '@/components/Layout';
import { SearchBar } from '@/components/SearchBar';
import { ArticleList } from '@/components/ArticleList';
import { useArticleSearch } from '@/hooks/useArticles';
import { useSearchStore } from '@/store';

export default function HomePage() {
  const [searchQuery, setSearchQuery] = React.useState('');
  const [isSearching, setIsSearching] = React.useState(false);
  const { setQuery, setResults } = useSearchStore();
  
  const {
    data: response,
    isLoading,
    error,
    refetch,
  } = useArticleSearch({
    query: searchQuery,
    enabled: false, // 수동으로 검색 실행
  });

  const articles = response?.results || [];

  const handleSearch = async (query: string) => {
    if (!query.trim()) return;
    
    setIsSearching(true);
    setSearchQuery(query);
    setQuery(query);
    
    try {
      // 검색 실행
      const result = await refetch();
      if (result.data?.results) {
        setResults(result.data.results);
      }
    } catch (error) {
      console.error('검색 중 오류:', error);
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <Layout>
      <div className="space-y-8">
        {/* 헤더 섹션 */}
        <div className="text-center py-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            AI 뉴스 요약 & 해설 서비스
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            복잡한 뉴스와 논문을 AI가 쉽고 빠르게 요약해드립니다. 
            핵심 내용을 한눈에 파악하세요.
          </p>
          
          {/* 검색바 */}
          <div className="max-w-2xl mx-auto">
            <SearchBar
              onSearch={handleSearch}
              placeholder="관심 있는 뉴스나 논문을 검색하세요..."
              loading={isSearching || isLoading}
            />
          </div>
        </div>

        {/* 추천 키워드 */}
        {!searchQuery && (
          <div className="text-center">
            <h2 className="text-lg font-semibold text-gray-700 mb-4">
              인기 검색어
            </h2>
            <div className="flex flex-wrap justify-center gap-2">
              {['AI', '인공지능', '머신러닝', '딥러닝', '블록체인', '메타버스', '웹3', 'NFT'].map((keyword) => (
                <button
                  key={keyword}
                  onClick={() => handleSearch(keyword)}
                  className="px-4 py-2 bg-primary-100 text-primary-700 rounded-full text-sm
                           hover:bg-primary-200 transition-colors"
                >
                  {keyword}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* 검색 결과 */}
        {searchQuery && (
          <div>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900">
                "{searchQuery}" 검색 결과
              </h2>
              {articles && articles.length > 0 && (
                <p className="text-gray-600">
                  총 {articles.length}개의 결과
                </p>
              )}
            </div>

            <ArticleList
              articles={articles}
              loading={isSearching || isLoading}
              error={error ? String(error) : null}
            />
          </div>
        )}

        {/* 소개 섹션 (검색 전에만 표시) */}
        {!searchQuery && (
          <div className="grid md:grid-cols-3 gap-8 mt-16">
            <div className="text-center">
              <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">빠른 요약</h3>
              <p className="text-gray-600">
                복잡한 뉴스와 논문을 몇 초 만에 핵심만 추려서 요약합니다.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-secondary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-secondary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">AI 해설</h3>
              <p className="text-gray-600">
                전문적인 내용도 쉽게 이해할 수 있도록 AI가 친절하게 해설합니다.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-accent-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-accent-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 4V2a1 1 0 011-1h8a1 1 0 011 1v2m0 0V1a1 1 0 011-1h2a1 1 0 011 1v18a1 1 0 01-1 1H4a1 1 0 01-1-1V1a1 1 0 011-1h2a1 1 0 011 1v3m0 0h8m-8 0V1" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">정확한 정보</h3>
              <p className="text-gray-600">
                RAG 기술로 신뢰할 수 있는 출처의 정보만을 제공합니다.
              </p>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}
