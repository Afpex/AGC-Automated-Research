import pandas as pd
from datetime import datetime
import logging
from dateutil import parser

logger = logging.getLogger(__name__)

class DataValidator:
    """
    Validates transport data for consistency and correctness.
    """
    
    def __init__(self, required_fields=None, min_content_length=20):
        """Initialize the DataValidator with configuration."""
        self.required_fields = required_fields or ['title', 'content', 'date']
        self.min_content_length = min_content_length
        
    def validate_data(self, data):
        """Validate a single data record."""
        # Check required fields
        if not all(field in data for field in self.required_fields):
            logger.warning(f"Missing required fields in data")
            return False

        # Validate date
        try:
            date_str = data['date']
            # Try to parse any date format
            parsed_date = parser.parse(date_str)
            
            # Convert to standard format YYYY-MM-DD
            data['date'] = parsed_date.strftime('%Y-%m-%d')
            
            # Check if date is within reasonable range
            if parsed_date.year < 2000 or parsed_date.year > 2100:
                logger.warning(f"Date out of acceptable range: {date_str}")
                return False
                
        except (ValueError, TypeError):
            logger.warning(f"Invalid date format: {date_str}")
            return False
            
        # Validate content length
        if not data['content'] or len(str(data['content'])) < self.min_content_length:
            logger.warning(f"Content too short or empty")
            return False
            
        # Validate title is not empty
        if not data['title'] or pd.isna(data['title']):
            logger.warning("Empty or missing title")
            return False
            
        return True
        
    def validate_dataframe(self, df):
        """Validate and clean a DataFrame of transport data."""
        # Create a copy to avoid modifying the original
        cleaned_df = df.copy()
        
        # Remove duplicates
        initial_len = len(cleaned_df)
        cleaned_df = cleaned_df.drop_duplicates(subset=['title', 'content'], keep='first')
        if len(cleaned_df) < initial_len:
            logger.info(f"Removed {initial_len - len(cleaned_df)} duplicate records")
            
        # Apply validation to each row
        valid_records = []
        for _, row in cleaned_df.iterrows():
            record = row.to_dict()
            if self.validate_data(record):
                valid_records.append(record)
                
        # Create new DataFrame from valid records
        validated_df = pd.DataFrame(valid_records)
        
        if len(validated_df) > 0:
            logger.info(f"Kept {len(validated_df)} valid records out of {initial_len} total")
        else:
            logger.warning("No valid records found after validation")
            
        return validated_df