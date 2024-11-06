import logging
from pathlib import Path
from datetime import datetime
from data_collection.scraper import TransportScraper
from data_collection.api_client import TransportAPIClient
from data_collection.data_validator import DataValidator
import pandas as pd
from config.settings import RESEARCH_CONFIG, API_SETTINGS

logger = logging.getLogger(__name__)

class TransportDataCollector:
    """Main class for collecting and processing transport data."""
    
    def __init__(self):
        self.scraper = TransportScraper()
        self.api_client = TransportAPIClient()
        self.validator = DataValidator()
        self.config = RESEARCH_CONFIG
        
    def collect_data(self):
        """Collect data from all configured sources."""
        all_data = []
        
        # Collect API data
        if self.config['data_sources'][0]['enabled']:  # transport_api
            try:
                api_data = self._collect_api_data()
                all_data.extend(api_data)
                logger.info(f"Collected {len(api_data)} records from API")
            except Exception as e:
                logger.error(f"Error collecting API data: {str(e)}")
        
        # Collect scraped data
        if self.config['data_sources'][1]['enabled']:  # transport_websites
            try:
                scraped_data = self._collect_scraped_data()
                all_data.extend(scraped_data)
                logger.info(f"Collected {len(scraped_data)} records from websites")
            except Exception as e:
                logger.error(f"Error collecting scraped data: {str(e)}")
        
        # Convert to DataFrame and validate
        if all_data:
            df = pd.DataFrame(all_data)
            validated_df = self.validator.validate_dataframe(df)
            self._save_data(validated_df)
            return validated_df
        return pd.DataFrame()
    
    def _collect_api_data(self):
        """Collect data from the transport API."""
        data = []
        for endpoint in self.config['data_sources'][0]['endpoints']:
            try:
                response = self.api_client.fetch_data(endpoint)
                data.extend(response.get('data', []))
            except Exception as e:
                logger.error(f"Error fetching from endpoint {endpoint}: {str(e)}")
        return data
    
    def _collect_scraped_data(self):
        """Collect data from configured websites."""
        data = []
        for url in self.config['data_sources'][1]['urls']:
            try:
                scraped = self.scraper.scrape_url(url)
                if scraped:
                    data.append(scraped)
            except Exception as e:
                logger.error(f"Error scraping {url}: {str(e)}")
        return data
    
    def _save_data(self, df):
        """Save the collected data to a CSV file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'transport_data_{timestamp}.csv'
        filepath = Path('data/processed') / filename
        df.to_csv(filepath, index=False)
        logger.info(f"Saved {len(df)} records to {filepath}")

def main():
    """Main entry point for the data collection process."""
    collector = TransportDataCollector()
    data = collector.collect_data()
    print(f"Collected and processed {len(data)} records")

if __name__ == "__main__":
    main()