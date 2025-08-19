import type { Metadata, Viewport } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Providers } from '@/providers';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Newsight - AI 뉴스 요약 & 해설',
  description: 'RAG와 LLM을 활용한 뉴스/논문 요약 & 해설 서비스',
  keywords: '뉴스, 논문, AI, 요약, 해설, RAG, LLM',
  authors: [{ name: 'Newsight Team' }],
  robots: 'index, follow',
  openGraph: {
    title: 'Newsight - AI 뉴스 요약 & 해설',
    description: 'RAG와 LLM을 활용한 뉴스/논문 요약 & 해설 서비스',
    type: 'website',
    locale: 'ko_KR',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Newsight - AI 뉴스 요약 & 해설',
    description: 'RAG와 LLM을 활용한 뉴스/논문 요약 & 해설 서비스',
  }
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body className={inter.className}>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}
