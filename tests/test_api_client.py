# tests/test_api_client.py
import pytest
from unittest.mock import Mock, patch
import requests
from src.data_collection.api_client import TransportAPIClient
from config.settings import API_SETTINGS

# Fixtures
@pytest.fixture
def api_client():
    """
    Fixture providing a TransportAPIClient instance for testing.
    
    Returns:
        TransportAPIClient: Configured client instance with test API key
    """
    return TransportAPIClient(api_key="test_api_key")

@pytest.fixture
def mock_response():
    """
    Fixture providing a mock API response.
    
    Returns:
        Mock: Configured mock response object with test data
    """
    response = Mock()
    response.json.return_value = {'data': 'test_data'}
    response.status_code = 200
    return response

# Tests
def test_api_client_initialization():
    """
    Test that the API client initializes correctly with settings.
    
    Verifies:
    - Settings are properly loaded
    - API key is correctly set
    - Session headers are properly configured
    """
    test_key = "test_api_key"
    client = TransportAPIClient(api_key=test_key)
    
    assert client.settings == API_SETTINGS
    assert client.api_key == test_key
    assert client.session.headers['Authorization'] == f'Bearer {test_key}'
    assert client.session.headers['Content-Type'] == 'application/json'

def test_api_client_default_initialization():
    """
    Test that the API client can initialize with default settings.
    
    Verifies:
    - Client falls back to API key from settings when none provided
    """
    client = TransportAPIClient()
    assert client.api_key == API_SETTINGS['api_key']

@patch('requests.Session.get')
def test_fetch_data_success(mock_get, api_client, mock_response):
    """
    Test successful API data fetch.
    
    Verifies:
    - Successful API call returns expected data
    - Request is made with correct parameters
    """
    mock_get.return_value = mock_response
    
    result = api_client.fetch_data('test_endpoint')
    
    assert result == {'data': 'test_data'}
    mock_get.assert_called_once_with(
        f"{API_SETTINGS['base_url']}/test_endpoint",
        params=None,
        timeout=API_SETTINGS['timeout']
    )

@patch('requests.Session.get')
def test_fetch_data_retry(mock_get, api_client, mock_response):
    """
    Test API retry mechanism.
    
    Verifies:
    - Failed request is retried
    - Successful retry returns expected data
    """
    mock_get.side_effect = [
        requests.exceptions.RequestException("Network error"),
        mock_response
    ]
    
    result = api_client.fetch_data('test_endpoint')
    
    assert result == {'data': 'test_data'}
    assert mock_get.call_count == 2

@patch('requests.Session.get')
def test_fetch_data_with_params(mock_get, api_client, mock_response):
    """
    Test API call with query parameters.
    
    Verifies:
    - Query parameters are properly passed to the request
    - Response handling works with parameters
    """
    mock_get.return_value = mock_response
    test_params = {'date': '2024-01-01', 'location': 'test'}
    
    result = api_client.fetch_data('test_endpoint', params=test_params)
    
    assert result == {'data': 'test_data'}
    mock_get.assert_called_once_with(
        f"{API_SETTINGS['base_url']}/test_endpoint",
        params=test_params,
        timeout=API_SETTINGS['timeout']
    )

@patch('requests.Session.get')
def test_fetch_data_max_retries_failure(mock_get, api_client):
    """
    Test that API client raises exception after max retries.
    
    Verifies:
    - Client attempts correct number of retries
    - Exception is raised after all retries fail
    """
    mock_get.side_effect = requests.exceptions.RequestException("Network error")
    
    with pytest.raises(requests.exceptions.RequestException):
        api_client.fetch_data('test_endpoint')
    
    assert mock_get.call_count == API_SETTINGS['retry_attempts']