"""
Email Parser Module

This module provides functionality to parse and manage emails from an Excel file.
It supports grouping emails by ID, retrieving first emails, and paginated reading.
"""

import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
import logging
from pathlib import Path


class EmailParserError(Exception):
    """Custom exception for EmailParser errors."""
    pass


class EmailParser:
    """
    A class to parse and manage emails from an Excel file.
    
    This class provides functionality to:
    - Load emails from Excel file
    - Group emails by Email ID
    - Retrieve first email by ID
    - Support paginated reading of emails
    """
    
    def __init__(self, file_path: str):
        """
        Initialize the EmailParser with an Excel file.
        
        Args:
            file_path (str): Path to the Excel file containing email data
            
        Raises:
            EmailParserError: If file doesn't exist or can't be loaded
        """
        self.file_path = Path(file_path)
        self.df: Optional[pd.DataFrame] = None
        self.grouped_emails: Optional[Dict[str, pd.DataFrame]] = None
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Expected columns in the Excel file
        self.expected_columns = [
            'email-id', 'converse-time', 'cs-id', 
            'sender', 'receiver', 'email-content'
        ]
        
        # Load the data
        self._load_data()
    
    def _load_data(self) -> None:
        """
        Load data from the Excel file and validate structure.
        
        Raises:
            EmailParserError: If file doesn't exist, can't be read, or has invalid structure
        """
        try:
            if not self.file_path.exists():
                raise EmailParserError(f"File not found: {self.file_path}")
            
            self.logger.info(f"Loading data from {self.file_path}")
            self.df = pd.read_excel(self.file_path)
            
            # Validate columns
            missing_columns = set(self.expected_columns) - set(self.df.columns)
            if missing_columns:
                raise EmailParserError(f"Missing required columns: {missing_columns}")
            
            # Clean data
            self.df = self.df.dropna(subset=['email-id'])  # Remove rows without email-id
            
            # Group emails by email-id
            self._group_emails()
            
            self.logger.info(f"Successfully loaded {len(self.df)} emails with {len(self.grouped_emails)} unique email IDs")
            
        except pd.errors.EmptyDataError:
            raise EmailParserError("The Excel file is empty")
        except pd.errors.ParserError as e:
            raise EmailParserError(f"Error parsing Excel file: {str(e)}")
        except Exception as e:
            raise EmailParserError(f"Unexpected error loading data: {str(e)}")
    
    def _group_emails(self) -> None:
        """Group emails by email-id for efficient retrieval."""
        if self.df is None:
            raise EmailParserError("No data loaded")
        
        self.grouped_emails = {}
        for email_id, group in self.df.groupby('email-id'):
            # Sort by index to maintain order (assuming original order is meaningful)
            self.grouped_emails[str(email_id)] = group.sort_index()
    
    def get_email_ids(self) -> List[str]:
        """
        Get all unique email IDs.
        
        Returns:
            List[str]: List of all unique email IDs
        """
        if self.grouped_emails is None:
            raise EmailParserError("No data loaded")
        
        return list(self.grouped_emails.keys())
    
    def get_first_email_by_id(self, email_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve the first email for a given email ID.
        
        Args:
            email_id (str): The email ID to search for
            
        Returns:
            Optional[Dict[str, Any]]: Dictionary containing email data, or None if not found
        """
        if self.grouped_emails is None:
            raise EmailParserError("No data loaded")
        
        email_id_str = str(email_id)
        if email_id_str not in self.grouped_emails:
            self.logger.warning(f"Email ID '{email_id}' not found")
            return None
        
        first_email = self.grouped_emails[email_id_str].iloc[0]
        return first_email.to_dict()
    
    def get_emails_by_id(self, email_id: str, page: int = 1, page_size: int = 10) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Retrieve emails for a given email ID with pagination support.
        
        Args:
            email_id (str): The email ID to search for
            page (int): Page number (1-based)
            page_size (int): Number of emails per page
            
        Returns:
            Tuple[List[Dict[str, Any]], Dict[str, Any]]: 
                - List of email dictionaries for the requested page
                - Pagination metadata (total_emails, total_pages, current_page, has_next, has_previous)
                
        Raises:
            EmailParserError: If page number is invalid
        """
        if self.grouped_emails is None:
            raise EmailParserError("No data loaded")
        
        if page < 1:
            raise EmailParserError("Page number must be >= 1")
        
        if page_size < 1:
            raise EmailParserError("Page size must be >= 1")
        
        email_id_str = str(email_id)
        if email_id_str not in self.grouped_emails:
            self.logger.warning(f"Email ID '{email_id}' not found")
            return [], {
                'total_emails': 0,
                'total_pages': 0,
                'current_page': page,
                'has_next': False,
                'has_previous': False
            }
        
        emails_df = self.grouped_emails[email_id_str]
        total_emails = len(emails_df)
        total_pages = (total_emails + page_size - 1) // page_size  # Ceiling division
        
        if page > total_pages and total_pages > 0:
            raise EmailParserError(f"Page {page} does not exist. Total pages: {total_pages}")
        
        # Calculate start and end indices
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        # Get the page data
        page_emails = emails_df.iloc[start_idx:end_idx]
        emails_list = [email.to_dict() for _, email in page_emails.iterrows()]
        
        # Pagination metadata
        pagination_info = {
            'total_emails': total_emails,
            'total_pages': total_pages,
            'current_page': page,
            'has_next': page < total_pages,
            'has_previous': page > 1,
            'page_size': page_size
        }
        
        return emails_list, pagination_info
    
    def get_all_emails_by_id(self, email_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve all emails for a given email ID.
        
        Args:
            email_id (str): The email ID to search for
            
        Returns:
            List[Dict[str, Any]]: List of all email dictionaries for the given ID
        """
        if self.grouped_emails is None:
            raise EmailParserError("No data loaded")
        
        email_id_str = str(email_id)
        if email_id_str not in self.grouped_emails:
            self.logger.warning(f"Email ID '{email_id}' not found")
            return []
        
        emails_df = self.grouped_emails[email_id_str]
        return [email.to_dict() for _, email in emails_df.iterrows()]
    
    def get_email_count_by_id(self, email_id: str) -> int:
        """
        Get the count of emails for a given email ID.
        
        Args:
            email_id (str): The email ID to count emails for
            
        Returns:
            int: Number of emails for the given ID
        """
        if self.grouped_emails is None:
            raise EmailParserError("No data loaded")
        
        email_id_str = str(email_id)
        if email_id_str not in self.grouped_emails:
            return 0
        
        return len(self.grouped_emails[email_id_str])
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """
        Get summary statistics about the email data.
        
        Returns:
            Dict[str, Any]: Dictionary containing summary statistics
        """
        if self.df is None or self.grouped_emails is None:
            raise EmailParserError("No data loaded")
        
        email_counts = [len(group) for group in self.grouped_emails.values()]
        
        return {
            'total_emails': len(self.df),
            'unique_email_ids': len(self.grouped_emails),
            'unique_senders': self.df['sender'].nunique(),
            'unique_receivers': self.df['receiver'].nunique(),
            'avg_emails_per_id': sum(email_counts) / len(email_counts) if email_counts else 0,
            'max_emails_per_id': max(email_counts) if email_counts else 0,
            'min_emails_per_id': min(email_counts) if email_counts else 0
        }
    
    def search_emails(self, search_term: str, search_in: List[str] = None) -> List[Dict[str, Any]]:
        """
        Search for emails containing a specific term.
        
        Args:
            search_term (str): Term to search for
            search_in (List[str]): Columns to search in. Defaults to ['sender', 'receiver', 'email-content']
            
        Returns:
            List[Dict[str, Any]]: List of matching email dictionaries
        """
        if self.df is None:
            raise EmailParserError("No data loaded")
        
        if search_in is None:
            search_in = ['sender', 'receiver', 'email-content']
        
        # Validate search columns
        invalid_columns = set(search_in) - set(self.df.columns)
        if invalid_columns:
            raise EmailParserError(f"Invalid search columns: {invalid_columns}")
        
        # Create a mask for rows containing the search term
        mask = pd.Series([False] * len(self.df))
        
        for column in search_in:
            # Convert to string and search (case-insensitive)
            column_mask = self.df[column].astype(str).str.contains(
                search_term, case=False, na=False
            )
            mask = mask | column_mask
        
        matching_emails = self.df[mask]
        return [email.to_dict() for _, email in matching_emails.iterrows()]
