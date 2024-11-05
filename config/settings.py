# config/settings.py
import os
from pathlib import Path
import yaml

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
REPORTS_DIR = DATA_DIR / 'reports'

# Create directories if they don't exist
for dir_path in [DATA_DIR / sub_dir for sub_dir in ['raw', 'processed', 'reports']]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Load research config
with open(BASE_DIR / 'config' / 'research_config.yaml', 'r') as file:
    RESEARCH_CONFIG = yaml.safe_load(file)

# API Settings
API_SETTINGS = {
    'base_url': os.getenv('API_BASE_URL', 'https://api.transport-data.com'),
    'api_key': os.getenv('API_KEY', ''),
    'timeout': 30,
    'retry_attempts': 3
}

# Scraping Settings
SCRAPING_SETTINGS = {
    'user_agent': 'TransportResearchBot/1.0',
    'request_delay': 2,  # seconds between requests
    'max_retries': 3,
    'timeout': 30,
    'headers': {
        'User-Agent': 'TransportResearchBot/1.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    }
}

# Analysis Settings
ANALYSIS_SETTINGS = {
    'min_data_points': 100,
    'confidence_threshold': 0.8,
    'outlier_threshold': 2.5,
    'trend_detection': {
        'window_size': 7,
        'min_periods': 3
    }
}

# Visualization Settings
VISUALIZATION_SETTINGS = {
    'theme': 'streamlit',
    'colors': {
        'primary': '#1f77b4',
        'secondary': '#ff7f0e',
        'background': '#ffffff'
    },
    'chart_defaults': {
        'width': 800,
        'height': 400
    }
}

# Logging Settings
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'app.log',
            'mode': 'a',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default', 'file'],
            'level': 'INFO',
            'propagate': True
        }
    }
}