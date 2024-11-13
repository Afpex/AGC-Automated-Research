# tests/test_scraper.py
import os
import sys

# Add the project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from src.data_collection.scraper import TransportScraper
import yaml
import json
from datetime import datetime
import os

def load_config():
    config_path = os.path.join(project_root, 'config', 'research_config.yaml')
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def test_scraper():
    # Initialize scraper
    scraper = TransportScraper()
    config = load_config()
    
    # Create a results directory
    results_dir = os.path.join(project_root, 'data', f"scraped_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    os.makedirs(results_dir, exist_ok=True)
    
    all_data = []
    
    # Test scraping for each site
    for category, sites in config['data_sources'][0]['sites'].items():
        print(f"\nScraping category: {category}")
        for site in sites:
            print(f"\nScraping: {site['name']} ({site['url']})")
            data = scraper.scrape_site_with_microsites(site)
            
            # Save individual site results
            site_filename = os.path.join(results_dir, f"{category}_{site['name'].lower().replace(' ', '_')}.json")
            with open(site_filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"Found {len(data)} articles")
            all_data.extend(data)
    
    # Save complete results
    with open(os.path.join(results_dir, 'all_results.json'), 'w') as f:
        json.dump(all_data, f, indent=2)
    
    print(f"\nTotal articles scraped: {len(all_data)}")
    print(f"Results saved in: {results_dir}")

if __name__ == "__main__":
    test_scraper()