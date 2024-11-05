import pytest
import pandas as pd
from src.data_collection.data_validator import DataValidator

@pytest.fixture
def validator():
    """
    Fixture providing a DataValidator instance for testing.
    
    Returns:
        DataValidator: Configured validator instance
    """
    return DataValidator()

@pytest.fixture
def valid_data():
    """
    Fixture providing valid test data.
    
    Returns:
        dict: Valid test data record
    """
    return {
        'title': 'Test Title',
        'content': 'Test content that is long enough',
        'date': '01-01-2024'  # Changed to DD-MM-YYYY format
    }

def test_validator_initialization():
    """Test validator initializes with correct default values"""
    validator = DataValidator()
    assert validator.required_fields == ['title', 'content', 'date']
    assert validator.min_content_length == 20
    assert validator.date_format == '%d-%m-%Y'

def test_validate_data_success(validator, valid_data):
    """Test validation passes with valid data"""
    assert validator.validate_data(valid_data) is True

def test_validate_data_missing_field(validator, valid_data):
    """Test validation fails when required field is missing"""
    invalid_data = valid_data.copy()
    del invalid_data['title']
    assert validator.validate_data(invalid_data) is False

def test_validate_data_invalid_date(validator, valid_data):
    """Test validation fails with invalid date format"""
    invalid_data = valid_data.copy()
    invalid_data['date'] = 'invalid-date'
    assert validator.validate_data(invalid_data) is False

def test_validate_data_invalid_date_format(validator, valid_data):
    """Test validation fails with wrong date format (YYYY-MM-DD)"""
    invalid_data = valid_data.copy()
    invalid_data['date'] = '2024-01-01'  # Wrong format
    assert validator.validate_data(invalid_data) is False

def test_validate_data_invalid_future_date(validator, valid_data):
    """Test validation fails with date too far in the future"""
    invalid_data = valid_data.copy()
    invalid_data['date'] = '01-01-2101'  # Date too far in future
    assert validator.validate_data(invalid_data) is False

def test_validate_content_length(validator, valid_data):
    """Test validation fails when content is too short"""
    invalid_data = valid_data.copy()
    invalid_data['content'] = 'short'
    assert validator.validate_data(invalid_data) is False

def test_validate_dataframe(validator):
    """Test DataFrame validation and cleaning"""
    df = pd.DataFrame([
        {'title': 'Title 1', 'content': 'Content 1 that is long enough', 'date': '01-01-2024'},
        {'title': 'Title 2', 'content': 'Content 2 that is long enough', 'date': '02-01-2024'},
        {'title': 'Title 1', 'content': 'Content 1 that is long enough', 'date': '01-01-2024'},  # duplicate
        {'title': None, 'content': 'Content 3 that is long enough', 'date': '03-01-2024'}  # missing title
    ])
    
    cleaned_df = validator.validate_dataframe(df)
    
    # Check number of rows (should remove duplicate and invalid row)
    assert len(cleaned_df) == 2
    
    # Check no duplicates remain
    assert not cleaned_df.duplicated().any()
    
    # Check all remaining rows are valid
    assert cleaned_df['title'].notna().all()

def test_validate_data_edge_dates(validator, valid_data):
    """Test validation of edge case dates"""
    # Test end of month
    valid_data['date'] = '31-12-2023'
    assert validator.validate_data(valid_data) is True
    
    # Test invalid day for month
    invalid_data = valid_data.copy()
    invalid_data['date'] = '31-11-2023'  # November has 30 days
    assert validator.validate_data(invalid_data) is False