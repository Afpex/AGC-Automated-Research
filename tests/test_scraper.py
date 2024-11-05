import pytest
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup
from src.data_collection.scraper import TransportDataScraper
from config.settings import SCRAPING_SETTINGS

@pytest.fixture
def mock_response():
    response = Mock()
    response.text = """
        <html>
            <head><title>Test Article</title></head>
            <body>
                <h1>Test Title</h1>
                <article>Test Content</article>
                <time>2024-01-01</time>
                <span class="author">John Doe</span>
            </body>
        </html>
    """
    return response

@pytest.fixture
def scraper():
    return TransportDataScraper()

def test_scraper_initialization():
    scraper = TransportDataScraper()
    assert scraper.settings == SCRAPING_SETTINGS
    assert scraper.session.headers['User-Agent'] == SCRAPING_SETTINGS['headers']['User-Agent']

@patch('requests.Session.get')
def test_scrape_url_success(mock_get, scraper, mock_response):
    mock_get.return_value = mock_response
    mock_response.status_code = 200
    
    result = scraper.scrape_url('http://test.com')
    
    assert result is not None
    assert result['title'] == 'Test Title'
    assert result['content'] == 'Test Content'
    assert result['date'] == '2024-01-01'
    assert result['author'] == 'John Doe'

@patch('requests.Session.get')
def test_scrape_url_failure(mock_get, scraper):
    mock_get.side_effect = Exception('Connection error')
    
    result = scraper.scrape_url('http://test.com')
    assert result is None