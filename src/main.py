import logging
from pathlib import Path
from datetime import datetime
from .data_collection.scraper import TransportScraper
from .data_collection.api_client import TransportAPIClient
from .data_collection.data_validator import DataValidator
import pandas as pd
from config.settings import RESEARCH_CONFIG
import time

logger = logging.getLogger(__name__)

class TransportDataCollector:
    def __init__(self):
        self.scraper = TransportScraper()
        self.api_client = TransportAPIClient()
        self.validator = DataValidator()
        self.config = RESEARCH_CONFIG
        
    def collect_data(self):
        """Collect data from all configured sources."""
        all_data = []
        start_time = time.time()
        
        print("\nStarting data collection process...")
        
        # Collect website data if enabled
        web_source = next((source for source in self.config['data_sources'] 
                          if source['name'] == 'transport_websites'), None)
        if web_source and web_source.get('enabled', True):
            try:
                print("\nCollecting data from websites...")
                for category, sites in web_source['sites'].items():
                    print(f"\nProcessing {category}...")
                    for site in sites:
                        try:
                            site_data = self.scraper.scrape_site_with_microsites({
                                'url': site['url'],
                                'name': site['name'],
                                'priority': site.get('priority', 2),
                                'include_microsites': web_source.get('include_microsites', True)
                            })
                            if site_data:
                                all_data.extend(site_data)
                        except Exception as e:
                            logger.error(f"Error scraping {site['name']}: {str(e)}")
                            continue
                
            except Exception as e:
                logger.error(f"Error in website scraping: {str(e)}")
        
        # Process and save data
        if all_data:
            print("\nProcessing collected data...")
            df = pd.DataFrame(all_data)
            validated_df = self.validator.validate_dataframe(df)
            self._save_data(validated_df)
            
            # Print summary
            elapsed_time = time.time() - start_time
            print(f"\nCollection completed in {elapsed_time:.1f} seconds")
            print(f"Total records collected: {len(validated_df)}")
            print(f"Records by source:")
            print(df['category'].value_counts().to_string())
            
            return validated_df
        else:
            print("\nNo data was collected")
            return pd.DataFrame()
    
    def _save_data(self, df):
        """Save the collected data to a CSV file."""
        if len(df) > 0:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'transport_data_{timestamp}.csv'
            filepath = Path('data/processed') / filename
            filepath.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(filepath, index=False)
            print(f"\nSaved {len(df)} records to {filepath}")
        else:
            print("\nNo data to save")

def main():
    """Main entry point for the data collection process."""
    collector = TransportDataCollector()
    data = collector.collect_data()
    if len(data) > 0:
        print(f"\nSuccessfully collected and processed {len(data)} records")
    else:
        print("\nNo data was collected")

if __name__ == "__main__":
    main()