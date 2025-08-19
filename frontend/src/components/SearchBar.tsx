'use client';

import React from 'react';
import { MagnifyingGlassIcon, XMarkIcon } from '@heroicons/react/24/outline';

interface SearchBarProps {
  onSearch: (query: string) => void;
  placeholder?: string;
  initialValue?: string;
  loading?: boolean;
  className?: string;
}

export function SearchBar({
  onSearch,
  placeholder = '검색어를 입력하세요...',
  initialValue = '',
  loading = false,
  className = '',
}: SearchBarProps) {
  const [query, setQuery] = React.useState(initialValue);
  const inputRef = React.useRef<HTMLInputElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim());
    }
  };

  const handleClear = () => {
    setQuery('');
    inputRef.current?.focus();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      handleClear();
    }
  };

  return (
    <form onSubmit={handleSubmit} className={`relative ${className}`}>
      <div className="relative">
        {/* 검색 아이콘 */}
        <div className="absolute inset-y-0 left-0 flex items-center pl-4">
          <MagnifyingGlassIcon 
            className={`h-5 w-5 ${loading ? 'animate-pulse text-primary-500' : 'text-gray-400'}`} 
          />
        </div>

        {/* 입력 필드 */}
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={loading}
          className={`block w-full pl-12 pr-12 py-3 border border-gray-300 rounded-lg 
                   placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 
                   focus:border-transparent disabled:opacity-50 text-sm transition-all duration-200
                   ${loading ? 'cursor-wait' : 'cursor-text'}`}
        />

        {/* 클리어 버튼 */}
        {query && !loading && (
          <button
            type="button"
            onClick={handleClear}
            className="absolute inset-y-0 right-0 flex items-center pr-4 text-gray-400 
                     hover:text-gray-600 transition-colors"
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
        )}

        {/* 로딩 스피너 */}
        {loading && (
          <div className="absolute inset-y-0 right-0 flex items-center pr-4">
            <div className="animate-spin rounded-full h-5 w-5 border-2 border-primary-500 border-t-transparent" />
          </div>
        )}
      </div>
    </form>
  );
}
