# test_script.py
from src.data_collection.scraper import TransportScraper
from src.data_collection.api_client import TransportAPIClient
from src.data_collection.data_validator import DataValidator
from src.main import TransportDataCollector
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_components():
    logger.info("Testing individual components...")
    
    # 1. Test Scraper
    logger.info("\nTesting Scraper:")
    scraper = TransportScraper()
    try:
        data = scraper.scrape_url("https://example.com/transport/news")  # Replace with actual URL
        logger.info(f"Scraped data: {data}")
    except Exception as e:
        logger.error(f"Scraper test failed: {str(e)}")
    
    # 2. Test API Client
    logger.info("\nTesting API Client:")
    api_client = TransportAPIClient()
    try:
        data = api_client.fetch_data("vehicles")  # Replace with actual endpoint
        logger.info(f"API data: {data}")
    except Exception as e:
        logger.error(f"API client test failed: {str(e)}")
    
    # 3. Test Data Validator
    logger.info("\nTesting Data Validator:")
    validator = DataValidator()
    test_data = {
        'title': 'Test Title',
        'content': 'This is a test content that should be long enough',
        'date': '01-01-2024'
    }
    try:
        is_valid = validator.validate_data(test_data)
        logger.info(f"Data validation result: {is_valid}")
    except Exception as e:
        logger.error(f"Validator test failed: {str(e)}")
    
    # 4. Test Complete Pipeline
    logger.info("\nTesting Complete Pipeline:")
    collector = TransportDataCollector()
    try:
        data = collector.collect_data()
        logger.info(f"Collected {len(data)} records")
    except Exception as e:
        logger.error(f"Pipeline test failed: {str(e)}")

if __name__ == "__main__":
    test_components()