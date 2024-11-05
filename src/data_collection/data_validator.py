import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DataValidator:
    """
    Validates transport data for consistency and correctness.
    
    This class provides methods to validate individual data records
    and entire DataFrames of transport data.
    
    Attributes:
        required_fields (list): List of required fields in the data
        min_content_length (int): Minimum required length for content field
        date_format (str): Expected format for date fields
    """
    
    def __init__(self, required_fields=None, min_content_length=20):
        """
        Initialize the DataValidator with configuration.
        
        Args:
            required_fields (list, optional): List of required field names.
                Defaults to ['title', 'content', 'date'].
            min_content_length (int, optional): Minimum content length.
                Defaults to 20.
        """
        self.required_fields = required_fields or ['title', 'content', 'date']
        self.min_content_length = min_content_length
        self.date_format = '%d-%m-%Y'  # Changed to day-month-year format
        
    def validate_data(self, data):
        """
        Validate a single data record.
        
        Args:
            data (dict): Data record to validate
            
        Returns:
            bool: True if data is valid, False otherwise
        """
        # Check required fields
        if not all(field in data for field in self.required_fields):
            logger.warning(f"Missing required fields in data: {data}")
            return False

        # Validate date format
        try:
            parsed_date = datetime.strptime(data['date'], self.date_format)
            # Additional check for valid date range if needed
            if parsed_date.year < 2000 or parsed_date.year > 2100:
                logger.warning(f"Date out of acceptable range: {data['date']}")
                return False
        except ValueError:
            logger.warning(f"Invalid date format in data: {data['date']}. Expected format: DD-MM-YYYY")
            return False
            
        # Validate content length
        if len(str(data['content'])) < self.min_content_length:
            logger.warning(f"Content too short: {len(str(data['content']))} characters")
            return False
            
        # Validate title is not empty
        if not data['title'] or pd.isna(data['title']):
            logger.warning("Empty or missing title")
            return False
            
        return True
        
    def validate_dataframe(self, df):
        """
        Validate and clean a DataFrame of transport data.
        
        Args:
            df (pandas.DataFrame): DataFrame to validate
            
        Returns:
            pandas.DataFrame: Cleaned DataFrame with only valid records
        """
        # Create a copy to avoid modifying the original
        cleaned_df = df.copy()
        
        # Remove duplicates
        initial_len = len(cleaned_df)
        cleaned_df = cleaned_df.drop_duplicates()
        if len(cleaned_df) < initial_len:
            logger.info(f"Removed {initial_len - len(cleaned_df)} duplicate records")
            
        # Apply validation to each row
        valid_mask = cleaned_df.apply(lambda row: self.validate_data(row.to_dict()), axis=1)
        
        # Filter out invalid records
        cleaned_df = cleaned_df[valid_mask]
        logger.info(f"Kept {len(cleaned_df)} valid records out of {initial_len} total")
        
        return cleaned_df