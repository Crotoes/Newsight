import * as React from 'react';

interface LayoutProps {
  children: React.ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* 헤더 */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* 로고 */}
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-primary-600">Newsight</h1>
              <span className="ml-2 text-sm text-gray-500">
                AI 뉴스 요약 & 해설
              </span>
            </div>

            {/* 네비게이션 */}
            <nav className="hidden md:flex items-center space-x-8">
              <a
                href="/"
                className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium 
                         transition-colors"
              >
                홈
              </a>
              <a
                href="/search"
                className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium 
                         transition-colors"
              >
                검색
              </a>
              <a
                href="/categories"
                className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium 
                         transition-colors"
              >
                카테고리
              </a>
              <a
                href="/about"
                className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium 
                         transition-colors"
              >
                소개
              </a>
            </nav>

            {/* 모바일 메뉴 버튼 */}
            <div className="md:hidden">
              <button
                type="button"
                className="text-gray-700 hover:text-primary-600 focus:outline-none focus:text-primary-600"
              >
                <span className="sr-only">메뉴 열기</span>
                <svg
                  className="h-6 w-6"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 6h16M4 12h16M4 18h16"
                  />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* 메인 콘텐츠 */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      {/* 푸터 */}
      <footer className="bg-white border-t border-gray-200 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {/* 로고 및 설명 */}
            <div className="md:col-span-2">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Newsight</h2>
              <p className="text-gray-600 text-sm leading-relaxed">
                AI 기술을 활용하여 뉴스와 논문을 빠르고 정확하게 요약하고 해설하는 서비스입니다. 
                복잡한 정보를 쉽게 이해할 수 있도록 도와드립니다.
              </p>
            </div>

            {/* 빠른 링크 */}
            <div>
              <h3 className="text-sm font-semibold text-gray-900 mb-4">빠른 링크</h3>
              <ul className="space-y-2">
                <li>
                  <a href="/" className="text-gray-600 hover:text-primary-600 text-sm transition-colors">
                    홈
                  </a>
                </li>
                <li>
                  <a href="/search" className="text-gray-600 hover:text-primary-600 text-sm transition-colors">
                    검색
                  </a>
                </li>
                <li>
                  <a href="/categories" className="text-gray-600 hover:text-primary-600 text-sm transition-colors">
                    카테고리
                  </a>
                </li>
              </ul>
            </div>

            {/* 지원 */}
            <div>
              <h3 className="text-sm font-semibold text-gray-900 mb-4">지원</h3>
              <ul className="space-y-2">
                <li>
                  <a href="/help" className="text-gray-600 hover:text-primary-600 text-sm transition-colors">
                    도움말
                  </a>
                </li>
                <li>
                  <a href="/contact" className="text-gray-600 hover:text-primary-600 text-sm transition-colors">
                    문의하기
                  </a>
                </li>
                <li>
                  <a href="/privacy" className="text-gray-600 hover:text-primary-600 text-sm transition-colors">
                    개인정보처리방침
                  </a>
                </li>
              </ul>
            </div>
          </div>

          {/* 저작권 */}
          <div className="border-t border-gray-200 mt-8 pt-8">
            <p className="text-center text-gray-500 text-sm">
              © 2024 Newsight. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
