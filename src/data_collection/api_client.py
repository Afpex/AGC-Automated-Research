import requests
import logging
from config.settings import API_SETTINGS

# Initialize logger for this module
logger = logging.getLogger(__name__)

class TransportAPIClient:
    """
    Client for interacting with the Transport API.
    
    This class handles all API interactions including authentication,
    request retry logic, and response handling.
    
    Attributes:
        api_key (str): Authentication key for the API
        settings (dict): Configuration settings from API_SETTINGS
        session (requests.Session): Persistent session for making HTTP requests
    """

    def __init__(self, api_key=None):
        """
        Initialize the API client with authentication and configuration.
        
        Args:
            api_key (str, optional): API authentication key. If not provided,
                                   falls back to the key in API_SETTINGS.
        """
        self.api_key = api_key or API_SETTINGS['api_key']
        self.settings = API_SETTINGS
        
        # Initialize a persistent session for better performance
        self.session = requests.Session()
        
        # Set default headers for all requests
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        })
        
    def fetch_data(self, endpoint, params=None):
        """
        Fetch data from the transport API with retry logic.
        
        This method handles the core API interaction, including:
        - URL construction
        - Request execution
        - Error handling
        - Automatic retries on failure
        
        Args:
            endpoint (str): API endpoint to call (e.g., 'vehicles', 'routes')
            params (dict, optional): Query parameters for the request
            
        Returns:
            dict: JSON response from the API
            
        Raises:
            requests.exceptions.RequestException: If all retry attempts fail
        """
        retry_attempts = self.settings['retry_attempts']
        timeout = self.settings['timeout']
        
        for attempt in range(retry_attempts):
            try:
                # Construct the full URL
                url = f"{self.settings['base_url']}/{endpoint}"
                logger.info(f"Fetching data from {url} (attempt {attempt + 1}/{retry_attempts})")
                
                # Make the request with timeout
                response = self.session.get(
                    url,
                    params=params,
                    timeout=timeout
                )
                
                # Raise an exception for bad status codes
                response.raise_for_status()
                
                # Return parsed JSON response
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {str(e)}")
                
                # On last attempt, raise the exception
                if attempt == retry_attempts - 1:
                    raise
                    
                logger.info(f"Retrying... ({attempt + 1}/{retry_attempts})")