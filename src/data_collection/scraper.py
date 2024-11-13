import requests
from bs4 import BeautifulSoup
import logging
from config.settings import SCRAPING_SETTINGS
from urllib.parse import urljoin, urlparse
import time
from datetime import datetime
import re
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import random
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# Initialize logger
logger = logging.getLogger(__name__)

class TransportScraper:
    """Web scraper for collecting transport-related information with improved robustness."""
    
    def __init__(self, settings=None):
        """Initialize the scraper with settings and configure session."""
        self.settings = settings or SCRAPING_SETTINGS
        self.visited_urls = set()
        self.max_depth = 2
        self.max_retries = 2
        self.timeout = 20
        
        # Initialize session with retry strategy
        self.session = self._create_robust_session()
        
        # Initialize logger for the instance
        self.logger = logging.getLogger(__name__)
        
        # Initialize progress bar
        self.pbar = None

        # Rotate user agents
        try:
            self.ua = UserAgent()
        except Exception:
            self.ua = None
            self.logger.warning("Could not initialize UserAgent, using fallback headers")
    
    def _create_robust_session(self):
        """Create a requests session with retry strategy."""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def scrape_site_with_microsites(self, site_config):
        """Scrape a site and its microsites according to configuration."""
        base_url = site_config['url']
        data = []
        
        try:
            self.logger.info(f"starting to scrape: {site_config['name']} ({base_url})")

            # Scrape main page with timeout
            main_data = self.scrape_url(base_url)
            if main_data:
                main_data['source_url'] = base_url
                main_data['category'] = site_config.get('name', 'Uncategorized')
                main_data['priority'] = site_config.get('priority', 3)
                data.append(main_data)
                print(f"✓ Successfully scraped main page: {site_config['name']}")
            else:
                print(f"× Failed to scrape main page: {site_config['name']}")
            # Scrape microsites if enabled
            if site_config.get('include_microsites', True):
                microsite_data = self._scrape_microsites_parallel(base_url)
                if microsite_data:
                    data.extend(microsite_data)
                    print(f"✓ Found {len(microsite_data)} related pages for {site_config['name']}")
            
        except Exception as e:
            self.logger.error(f"Error scraping {site_config['name']} ({base_url}): {str(e)}")
            print(f"× Error scraping {site_config['name']}: {str(e)}")
        
        return data

    def _scrape_microsites_parallel(self, url, max_workers=3):
        """Scrape microsites in parallel."""
        data = []
        links = self._get_links(url)
        
        if not links:
            return data
        
        print(f"Found {len(links)} links to process from {url}")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(self.scrape_url, link): link 
                for link in links 
                if self._should_scrape_url(link, url)
            }
            
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    page_data = future.result()
                    if page_data:
                        data.append(page_data)
                        print(f"  ✓ Scraped: {url}")
                except Exception as e:
                    print(f"  × Failed: {url} - {str(e)}")
        
        return data

    def _get_links(self, url):
        """Get all links from a page."""
        try:
            response = self.session.get(
                url,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a', href=True)
            
            return [urljoin(url, link['href']) for link in links]
        except Exception as e:
            self.logger.error(f"Error getting links from {url}: {str(e)}")
            return []

    def scrape_url(self, url):
        """Scrape data from a given URL with improved error handling."""
        if url in self.visited_urls:
            return None
            
        self.visited_urls.add(url)
        
        try:
            # Random delay between requests
            time.sleep(random.uniform(1, 2))
            
            headers = self._get_headers()
            response = self.session.get(
                url, 
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            if self._is_blocked(soup, response):
                self.logger.warning(f"Possible anti-bot detection on {url}")
                return None
            
            data = {
                'title': self._extract_title(soup),
                'content': self._extract_content(soup),
                'date': self._extract_date(soup),
                'source_url': url,
                'scrape_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            if data['title'] and data['content']:
                return data
            return None
            
        except requests.exceptions.Timeout:
            self.logger.warning(f"Timeout while scraping {url}")
            return None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error scraping {url}: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error scraping {url}: {str(e)}")
            return None
            
    def get_delay(self):
        """Get the request delay, handling both callable and static values."""
        delay = self.settings.get('request_delay', 2)
        if callable(delay):
            return delay()
        return delay
    
    def _get_headers(self):
        """Get randomized headers for requests."""
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'User-Agent': self.ua.random if self.ua else self.settings['headers']['User-Agent']
        }
        return headers
    
    def scrape_site_with_microsites(self, site_config):
        """Scrape a site and its microsites according to configuration."""
        base_url = site_config['url']
        data = []
        
        try:
            # Add random delay before starting
            time.sleep(random.uniform(1, 3))
            
            self.logger.info(f"Starting to scrape main site: {base_url}")
            main_data = self.scrape_url(base_url)
            if main_data:
                main_data['source_url'] = base_url
                main_data['category'] = site_config.get('name', 'Uncategorized')
                main_data['priority'] = site_config.get('priority', 3)
                data.append(main_data)
            
            # Scrape microsites if enabled
            if site_config.get('include_microsites', True):
                self.logger.info(f"Starting to scrape microsites for: {base_url}")
                microsite_data = self._scrape_microsites(base_url, depth=0)
                if microsite_data:
                    data.extend(microsite_data)
            
        except Exception as e:
            self.logger.error(f"Error scraping {base_url}: {str(e)}")
        
        return data
    
    def scrape_url(self, url):
        """Scrape data from a given URL with improved error handling."""
        if url in self.visited_urls:
            return None
            
        self.visited_urls.add(url)
        
        try:
            # Random delay between requests
            time.sleep(self.get_delay())
            
            headers = self._get_headers()
            response = self.session.get(
                url, 
                headers=headers,
                timeout=self.settings.get('timeout', 30)
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check for anti-bot measures
            if self._is_blocked(soup, response):
                self.logger.warning(f"Possible anti-bot detection on {url}")
                return None
            
            data = {
                'title': self._extract_title(soup),
                'content': self._extract_content(soup),
                'date': self._extract_date(soup),
                'source_url': url,
                'scrape_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            if data['title'] and data['content']:
                self.logger.info(f"Successfully scraped {url}")
                return data
            return None
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error scraping {url}: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error scraping {url}: {str(e)}")
            return None
    
    def _is_blocked(self, soup, response):
        """Check if we're being blocked or rate limited."""
        block_indicators = [
            'captcha',
            'blocked',
            'rate limit',
            'too many requests',
            'access denied'
        ]
        
        # Check response headers
        if response.status_code == 429:
            return True
            
        # Check page content
        page_text = soup.get_text().lower()
        return any(indicator in page_text for indicator in block_indicators)
    
    def _scrape_microsites(self, url, depth=0):
        """Recursively scrape microsites with improved handling."""
        if depth >= self.max_depth:
            return []
        
        data = []
        try:
            time.sleep(self.get_delay())
            
            headers = self._get_headers()
            response = self.session.get(
                url, 
                headers=headers,
                timeout=self.settings.get('timeout', 30)
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all links
            links = soup.find_all('a', href=True)
            for link in links:
                next_url = urljoin(url, link['href'])
                
                if self._should_scrape_url(next_url, url):
                    page_data = self.scrape_url(next_url)
                    if page_data:
                        data.append(page_data)
                        # Recursively scrape more microsites
                        sub_data = self._scrape_microsites(next_url, depth + 1)
                        if sub_data:
                            data.extend(sub_data)
                    
        except Exception as e:
            self.logger.error(f"Error scraping microsites from {url}: {str(e)}")
        
        return data
    
    def _should_scrape_url(self, url, base_url):
        """Enhanced URL filtering."""
        if not url:
            return False
            
        parsed_url = urlparse(url)
        base_parsed = urlparse(base_url)
        
        # Must be same domain
        if parsed_url.netloc != base_parsed.netloc:
            return False
            
        path = parsed_url.path.lower()
        
        # Excluded patterns
        excluded_patterns = [
            '/login', '/search', '/page/', 
            'javascript:', 'mailto:', 'tel:',
            '/tag/', '/category/', '/author/',
            '.pdf', '.jpg', '.png', '.gif',
            '/feed/', '/rss/', '/xml/', '/raw/',
            '/wp-content/', '/wp-includes/',
            '/comment', '/trackback', '/cart',
            '/account', '/profile', '/user'
        ]
        
        if any(pattern in path for pattern in excluded_patterns):
            return False
        
        # Included patterns
        included_patterns = [
            '/projects/', '/research/', '/publications/',
            '/news/', '/transport/', '/mobility/',
            '/sustainable/', '/africa/', '/east-africa/',
            '/report', '/study', '/analysis',
            '/policy', '/strategy', '/program'
        ]
        
        return any(pattern in path for pattern in included_patterns)
    
    def _extract_title(self, soup):
        """Extract title with improved handling."""
        for title_tag in [
            soup.find('h1'),
            soup.find('meta', property='og:title'),
            soup.find('title')
        ]:
            if title_tag:
                title = title_tag.get('content', '') or title_tag.text
                title = re.sub(r'\s+', ' ', title).strip()
                if title and len(title) > 5:
                    return title
        return None
    
    def _extract_content(self, soup):
        """Extract main content with improved cleaning."""
        # Remove unwanted elements
        for element in soup.find_all([
            'script', 'style', 'nav', 'header', 'footer',
            'form', 'iframe', 'noscript', 'aside'
        ]):
            element.decompose()
        
        # Try multiple content containers
        for container in [
            soup.find('article'),
            soup.find('main'),
            soup.find('div', class_=re.compile(r'content|article|post|entry')),
            soup.find('div', id=re.compile(r'content|article|post|entry'))
        ]:
            if container:
                paragraphs = container.find_all(['p', 'div'])
                if paragraphs:
                    text = ' '.join(p.text.strip() for p in paragraphs)
                    text = re.sub(r'\s+', ' ', text).strip()
                    if len(text) > 100:  # Minimum content length
                        return text
        return None
    
    def _extract_date(self, soup):
        """Extract date with improved format handling."""
        for date_tag in [
            soup.find('time'),
            soup.find(class_=re.compile(r'date|posted|published')),
            soup.find('meta', property='article:published_time'),
            soup.find('meta', property='og:published_time')
        ]:
            if date_tag:
                date_text = date_tag.get('datetime') or date_tag.get('content') or date_tag.text
                date_text = date_text.strip()
                
                # Try different date formats
                date_formats = [
                    '%Y-%m-%d',
                    '%Y/%m/%d',
                    '%d-%m-%Y',
                    '%d/%m/%Y',
                    '%B %d, %Y',
                    '%b %d, %Y',
                    '%Y-%m-%dT%H:%M:%S',
                    '%Y-%m-%dT%H:%M:%S.%fZ'
                ]
                
                for fmt in date_formats:
                    try:
                        return datetime.strptime(date_text, fmt).strftime('%Y-%m-%d')
                    except ValueError:
                        continue
                        
        return datetime.now().strftime('%Y-%m-%d')