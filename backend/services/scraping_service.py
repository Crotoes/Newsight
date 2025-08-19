 
"""
뉴스 및 논문 스크래핑 서비스 - TYPE_CHECKING을 사용한 임포트 경고 해결
"""
from typing import List, Optional, Dict, Any, TYPE_CHECKING
import asyncio
import logging
import re
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass
from datetime import datetime, timezone

# 타입 체킹 시에만 임포트 (런타임에는 임포트되지 않음)
if TYPE_CHECKING:
    import aiohttp  # type: ignore
    import feedparser  # type: ignore
    import requests  # type: ignore
    from bs4 import BeautifulSoup  # type: ignore

# from core.config import settings

logger = logging.getLogger(__name__)

@dataclass
class ScrapedArticle:
    """스크래핑된 기사 데이터 클래스"""
    title: str
    content: str
    url: str
    published_date: Optional[datetime] = None
    author: Optional[str] = None
    summary: Optional[str] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

@dataclass
class RSSFeed:
    """RSS 피드 데이터 클래스"""
    title: str
    description: str
    link: str
    items: List[Dict[str, Any]]


class NewsScraper:
    """뉴스 스크래핑 서비스"""
    
    def __init__(self):
        self.session: Optional["aiohttp.ClientSession"] = None
        self._aiohttp_available = False
        self._feedparser_available = False
        self._bs4_available = False
        self._requests_available = False
        
    def _check_aiohttp_availability(self) -> bool:
        """aiohttp 라이브러리 사용 가능 여부 확인"""
        if self._aiohttp_available:
            return True
            
        try:
            import aiohttp  # type: ignore # noqa: F401
            self._aiohttp_available = True
            return True
        except ImportError:
            logger.info("aiohttp not installed. Install with: pip install -e '.[scraping]'")
            return False

    def _check_feedparser_availability(self) -> bool:
        """feedparser 라이브러리 사용 가능 여부 확인"""
        if self._feedparser_available:
            return True
            
        try:
            import feedparser  # type: ignore # noqa: F401
            self._feedparser_available = True
            return True
        except ImportError:
            logger.info("feedparser not installed. Install with: pip install -e '.[scraping]'")
            return False

    def _check_bs4_availability(self) -> bool:
        """BeautifulSoup 라이브러리 사용 가능 여부 확인"""
        if self._bs4_available:
            return True
            
        try:
            from bs4 import BeautifulSoup  # type: ignore # noqa: F401
            self._bs4_available = True
            return True
        except ImportError:
            logger.info("BeautifulSoup not installed. Install with: pip install -e '.[scraping]'")
            return False

    def _check_requests_availability(self) -> bool:
        """requests 라이브러리 사용 가능 여부 확인"""
        if self._requests_available:
            return True
            
        try:
            import requests  # type: ignore # noqa: F401
            self._requests_available = True
            return True
        except ImportError:
            logger.info("requests not installed. Install with: pip install -e '.[scraping]'")
            return False

    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        if self._check_aiohttp_availability():
            try:
                import aiohttp  # type: ignore
                timeout = aiohttp.ClientTimeout(total=30)
                self.session = aiohttp.ClientSession(timeout=timeout)
            except Exception as e:
                logger.error(f"Failed to create aiohttp session: {e}")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        if self.session:
            await self.session.close()

    async def parse_rss_feed(self, rss_url: str) -> Optional[RSSFeed]:
        """RSS 피드 파싱"""
        if not self._check_feedparser_availability():
            logger.error("feedparser not available for RSS parsing")
            return None
            
        try:
            import feedparser  # type: ignore
            
            # RSS 피드 파싱
            feed = await asyncio.to_thread(feedparser.parse, rss_url)
            
            if not hasattr(feed, 'entries') or not feed.entries:
                logger.warning(f"No entries found in RSS feed: {rss_url}")
                return None
                
            # RSS 피드 정보 추출
            rss_feed = RSSFeed(
                title=feed.feed.get('title', ''),
                description=feed.feed.get('description', ''),
                link=feed.feed.get('link', ''),
                items=[]
            )
            
            # 각 항목 처리
            for entry in feed.entries[:10]:  # 최대 10개 항목
                item = {
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'description': entry.get('description', ''),
                    'published': entry.get('published', ''),
                    'author': entry.get('author', ''),
                }
                rss_feed.items.append(item)
                
            return rss_feed
            
        except Exception as e:
            logger.error(f"RSS feed parsing failed: {e}")
            return None

    async def scrape_article_content(self, url: str) -> Optional[ScrapedArticle]:
        """웹페이지에서 기사 내용 스크래핑"""
        if not self._check_aiohttp_availability() or not self._check_bs4_availability():
            logger.error("Required libraries not available for web scraping")
            return None
            
        if not self.session:
            logger.error("HTTP session not initialized")
            return None
            
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.warning(f"HTTP {response.status} for URL: {url}")
                    return None
                    
                html_content = await response.text()
                
            # BeautifulSoup으로 HTML 파싱
            from bs4 import BeautifulSoup  # type: ignore
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 제목 추출
            title = ""
            title_selectors = ['h1', 'title', '.title', '#title', '[class*="title"]']
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem and title_elem.get_text().strip():
                    title = title_elem.get_text().strip()
                    break
                    
            # 본문 내용 추출
            content = ""
            content_selectors = [
                'article', '.article', '#article',
                '.content', '#content', '[class*="content"]',
                '.post-content', '.entry-content', '.article-body'
            ]
            
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # 스크립트, 스타일, 광고 등 제거
                    for unwanted in content_elem.find_all(['script', 'style', 'nav', 'aside', 'footer', '.ad', '.advertisement']):
                        unwanted.decompose()
                        
                    content = content_elem.get_text().strip()
                    if len(content) > 100:  # 충분한 내용이 있을 때만
                        break
                        
            if not content:
                # 폴백: 모든 p 태그에서 텍스트 추출
                paragraphs = soup.find_all('p')
                content = '\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                
            if not title or not content:
                logger.warning(f"Failed to extract sufficient content from: {url}")
                return None
                
            # 기사 객체 생성
            article = ScrapedArticle(
                title=title,
                content=content,
                url=url,
                published_date=datetime.now(timezone.utc)
            )
            
            return article
            
        except Exception as e:
            logger.error(f"Article scraping failed for {url}: {e}")
            return None

    async def scrape_multiple_articles(self, urls: List[str]) -> List[ScrapedArticle]:
        """여러 기사 동시 스크래핑"""
        if not urls:
            return []
            
        tasks = []
        semaphore = asyncio.Semaphore(5)  # 동시 요청 수 제한
        
        async def scrape_with_semaphore(url):
            async with semaphore:
                return await self.scrape_article_content(url)
                
        for url in urls:
            tasks.append(scrape_with_semaphore(url))
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 성공한 결과만 반환
        articles = []
        for result in results:
            if isinstance(result, ScrapedArticle):
                articles.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Scraping error: {result}")
                
        return articles

    def get_status(self) -> dict:
        """스크래핑 서비스 상태 반환"""
        return {
            "aiohttp_available": self._check_aiohttp_availability(),
            "feedparser_available": self._check_feedparser_availability(),
            "bs4_available": self._check_bs4_availability(),
            "requests_available": self._check_requests_availability(),
            "session_active": self.session is not None and not self.session.closed if self.session else False,
        }


class PaperScraper:
    """학술 논문 스크래핑 서비스"""
    
    def __init__(self):
        self.arxiv_base_url = "http://export.arxiv.org/api/query"
        self.pubmed_base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        
    def _check_requests_availability(self) -> bool:
        """requests 라이브러리 사용 가능 여부 확인"""
        try:
            import requests  # type: ignore # noqa: F401
            return True
        except ImportError:
            logger.info("requests not installed. Install with: pip install -e '.[scraping]'")
            return False

    async def search_arxiv_papers(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """arXiv에서 논문 검색"""
        if not self._check_requests_availability():
            logger.error("requests not available for arXiv search")
            return []
            
        try:
            import requests  # type: ignore
            from xml.etree import ElementTree as ET
            
            params = {
                'search_query': query,
                'start': 0,
                'max_results': max_results,
                'sortBy': 'lastUpdatedDate',
                'sortOrder': 'descending'
            }
            
            response = await asyncio.to_thread(
                requests.get, self.arxiv_base_url, params=params
            )
            
            if response.status_code != 200:
                logger.error(f"arXiv API error: {response.status_code}")
                return []
                
            # XML 파싱
            root = ET.fromstring(response.content)
            
            papers = []
            for entry in root.findall('.//{http://www.w3.org/2005/Atom}entry'):
                paper = {
                    'title': entry.find('.//{http://www.w3.org/2005/Atom}title').text.strip(),
                    'summary': entry.find('.//{http://www.w3.org/2005/Atom}summary').text.strip(),
                    'authors': [author.find('.//{http://www.w3.org/2005/Atom}name').text 
                               for author in entry.findall('.//{http://www.w3.org/2005/Atom}author')],
                    'link': entry.find('.//{http://www.w3.org/2005/Atom}id').text,
                    'published': entry.find('.//{http://www.w3.org/2005/Atom}published').text,
                    'updated': entry.find('.//{http://www.w3.org/2005/Atom}updated').text,
                }
                papers.append(paper)
                
            return papers
            
        except Exception as e:
            logger.error(f"arXiv search failed: {e}")
            return []

    async def get_paper_details(self, arxiv_id: str) -> Optional[Dict[str, Any]]:
        """특정 arXiv 논문의 상세 정보 가져오기"""
        if not self._check_requests_availability():
            logger.error("requests not available for paper details")
            return None
            
        try:
            import requests  # type: ignore
            from xml.etree import ElementTree as ET
            
            url = f"{self.arxiv_base_url}?id_list={arxiv_id}"
            response = await asyncio.to_thread(requests.get, url)
            
            if response.status_code != 200:
                logger.error(f"arXiv API error: {response.status_code}")
                return None
                
            root = ET.fromstring(response.content)
            entry = root.find('.//{http://www.w3.org/2005/Atom}entry')
            
            if entry is None:
                logger.warning(f"Paper not found: {arxiv_id}")
                return None
                
            paper_details = {
                'title': entry.find('.//{http://www.w3.org/2005/Atom}title').text.strip(),
                'summary': entry.find('.//{http://www.w3.org/2005/Atom}summary').text.strip(),
                'authors': [author.find('.//{http://www.w3.org/2005/Atom}name').text 
                           for author in entry.findall('.//{http://www.w3.org/2005/Atom}author')],
                'link': entry.find('.//{http://www.w3.org/2005/Atom}id').text,
                'published': entry.find('.//{http://www.w3.org/2005/Atom}published').text,
                'categories': [cat.get('term') for cat in entry.findall('.//{http://arxiv.org/schemas/atom}primary_category')],
                'pdf_url': None
            }
            
            # PDF 링크 찾기
            for link in entry.findall('.//{http://www.w3.org/2005/Atom}link'):
                if link.get('type') == 'application/pdf':
                    paper_details['pdf_url'] = link.get('href')
                    break
                    
            return paper_details
            
        except Exception as e:
            logger.error(f"Paper details retrieval failed: {e}")
            return None

    def get_status(self) -> dict:
        """논문 스크래핑 서비스 상태 반환"""
        return {
            "requests_available": self._check_requests_availability(),
            "arxiv_url": self.arxiv_base_url,
            "pubmed_url": self.pubmed_base_url,
        }
