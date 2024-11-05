# src/data_collection/scraper.py
import requests
from bs4 import BeautifulSoup
import pandas as pd
from typing import List, Dict
import logging
from config.settings import SCRAPING_SETTINGS
from time import sleep

logger = logging.getLogger(__name__)

class TransportDataScraper:
    def __init__(self, settings: Dict = None):
        self.settings = settings or SCRAPING_SETTINGS
        self.session = self._init_session()
        
    def _init_session(self) -> requests.Session:
        """Initialize requests session with default headers"""
        session = requests.Session()
        session.headers.update(self.settings['headers'])
        return session
    
    def scrape_url(self, url: str) -> Dict:
        """Scrape data from a single URL"""
        try:
            response = self.session.get(
                url, 
                timeout=self.settings['timeout']
            )
            response.raise_for_status()
            
            # Add delay between requests
            sleep(self.settings['request_delay'])
            
            soup = BeautifulSoup(response.text, 'html.parser')
            return self._parse_content(soup)
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return None
    
    def _parse_content(self, soup: BeautifulSoup) -> Dict:
        """Parse the BeautifulSoup object and extract relevant data"""
        try:
            data = {
                'title': self._extract_title(soup),
                'content': self._extract_content(soup),
                'date': self._extract_date(soup),
                'author': self._extract_author(soup)
            }
            return data
        except Exception as e:
            logger.error(f"Error parsing content: {str(e)}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract title from the page"""
        title_tag = soup.find('h1') or soup.find('title')
        return title_tag.text.strip() if title_tag else ''
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from the page"""
        # Implement based on specific website structure
        content_div = soup.find('article') or soup.find('main')
        return content_div.text.strip() if content_div else ''
    
    def _extract_date(self, soup: BeautifulSoup) -> str:
        """Extract publication date"""
        date_tag = soup.find('time') or soup.find(class_='date')
        return date_tag.text.strip() if date_tag else ''
    
    def _extract_author(self, soup: BeautifulSoup) -> str:
        """Extract author information"""
        author_tag = soup.find(class_='author') or soup.find(rel='author')
        return author_tag.text.strip() if author_tag else ''

# src/data_collection/api_client.py
import requests
from typing import Dict, Optional, List
import logging
from config.settings import API_SETTINGS
from time import sleep

logger = logging.getLogger(__name__)

class TransportAPIClient:
    def __init__(self, settings: Dict = None):
        self.settings = settings or API_SETTINGS
        self.session = self._init_session()
    
    def _init_session(self) -> requests.Session:
        """Initialize API session"""
        session = requests.Session()
        session.headers.update({
            'Authorization': f'Bearer {self.settings["api_key"]}',
            'Content-Type': 'application/json'
        })
        return session
    
    def fetch_data(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Fetch data from API endpoint"""
        url = f"{self.settings['base_url']}/{endpoint.lstrip('/')}"
        
        for attempt in range(self.settings['retry_attempts']):
            try:
                response = self.session.get(
                    url,
                    params=params,
                    timeout=self.settings['timeout']
                )
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.error(f"API request failed (attempt {attempt + 1}): {str(e)}")
                if attempt < self.settings['retry_attempts'] - 1:
                    sleep(2 ** attempt)  # Exponential backoff
                continue
                
        logger.error(f"All attempts failed for endpoint: {endpoint}")
        return None
    
    def post_data(self, endpoint: str, data: Dict) -> Optional[Dict]:
        """Post data to API endpoint"""
        url = f"{self.settings['base_url']}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.post(
                url,
                json=data,
                timeout=self.settings['timeout']
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API post failed: {str(e)}")
            return None

# src/data_collection/data_validator.py
from typing import Dict, List, Optional
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class DataValidator:
    def __init__(self, required_fields: List[str] = None):
        self.required_fields = required_fields or ['title', 'content', 'date']
    
    def validate_data(self, data: Dict) -> bool:
        """Validate collected data"""
        # Check required fields
        for field in self.required_fields:
            if field not in data or not data[field]:
                logger.error(f"Missing required field: {field}")
                return False
        
        # Validate date format
        if not self._validate_date(data.get('date')):
            return False
        
        # Validate content length
        if not self._validate_content_length(data.get('content')):
            return False
        
        return True
    
    def _validate_date(self, date_str: str) -> bool:
        """Validate date format"""
        try:
            pd.to_datetime(date_str)
            return True
        except (ValueError, TypeError):
            logger.error(f"Invalid date format: {date_str}")
            return False
    
    def _validate_content_length(self, content: str) -> bool:
        """Validate content length"""
        if not content or len(content.strip()) < 10:
            logger.error("Content too short or empty")
            return False
        return True
    
    def validate_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate and clean DataFrame"""
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Handle missing values
        for field in self.required_fields:
            if field in df.columns:
                df = df.dropna(subset=[field])
        
        return df