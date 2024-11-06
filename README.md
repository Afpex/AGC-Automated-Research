# Transport Data Collector

A Python-based tool for collecting, validating, and analyzing transport-related data from multiple sources. This tool helps researchers and analysts gather and process transport policy information efficiently.

## Features

+ Multi-source data collection (APIs and web scraping)
+ Automated data validation and cleaning
+ Configurable data sources and validation rules
+ Logging and error handling
+ Basic data analysis capabilities
+ CLI interface for easy operation

## Quick Start

1. Clone the repository
2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Windows
   source venv/bin/activate      # Unix
3. Install dependencies:
  ```bash
    pip install -r requirements.txt
4. Set up environment variables:
  ```bash
    # Create .env file and add your configurations
    cp .env.example .env
    # Edit .env with your API keys and settings

## Project Structure

transport_analytics/
├── config/
│   ├── settings.py
│   └── research_config.yaml
├── data/
│   ├── raw/
│   ├── processed/
│   └── reports/
├── src/
│   ├── data_collection/
│   │   ├── api_client.py
│   │   ├── data_validator.py
│   │   └── scraper.py
│   ├── main.py
│   └── cli.py
├── tests/
│   ├── test_api_client.py
│   ├── test_data_validator.py
│   └── test_scraper.py
├── requirements.txt
└── README.md

## Usage 

1. Collect data from all sources:
  ```bash
    python src/cli.py collect
2. Analyze collected data:
  ```bash
    python src/cli.py analyze <filename>

## Configuration
  # Environment Variables
  + API_KEY: Your transport data API key
  + API_BASE_URL: Base URL for the transport API

  # Research Configuration
  Edit config/research_config.yaml to:
  + Add/modify data sources
  + Configure validation rules
  + Set analysis parameters

## Testing 
Run the test suite:
pytest tests/ -v

## Development

1. Create a new feature branch:
 git checkout -b feature/your-feature-name

2. Make your changes and commit:
  git add .
  git commit -m "Description of changes"

3. Push changes and create a pull request:
  git push origin feature/your-feature-name

## Contributing
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request


## Contact 
Anthony Ndolo - bondolo90@gmail.com 