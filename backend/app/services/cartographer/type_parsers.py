"""
Type Parsers
Basic type casting functions for smart parser.
"""

import re
from typing import Optional, List
from datetime import datetime
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class TypeParsers:
    """Collection of basic type parsing functions."""
    
    @staticmethod
    def parse_string(value: str) -> str:
        """Clean and return string."""
        return value.strip()
    
    @staticmethod
    def parse_integer(value: str) -> Optional[int]:
        """Parse integer, removing commas and spaces."""
        cleaned = re.sub(r'[,\s]', '', value.strip())
        try:
            return int(float(cleaned))
        except ValueError:
            return None
    
    @staticmethod
    def parse_float(value: str) -> Optional[float]:
        """Parse float, removing commas and spaces."""
        cleaned = re.sub(r'[,\s]', '', value.strip())
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    @staticmethod
    def parse_percentage(value: str) -> Optional[float]:
        """Parse percentage, removing % symbol."""
        cleaned = value.strip().replace('%', '').replace(',', '')
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    @staticmethod
    def parse_currency(value: str) -> Optional[float]:
        """Parse currency, removing $ and commas."""
        cleaned = value.strip().replace('$', '').replace(',', '')
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    @staticmethod
    def parse_date(value: str) -> Optional[str]:
        """
        Parse date string to ISO format.
        Tries multiple formats: 'Dec 13, 2025', '12/13/2025', '2025-12-13'.
        """
        formats = [
            '%b %d, %Y',
            '%B %d, %Y',
            '%m/%d/%Y',
            '%Y-%m-%d'
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(value.strip(), fmt)
                return dt.date().isoformat()
            except ValueError:
                continue
        
        return None
    
    @staticmethod
    def parse_boolean(value: str) -> Optional[bool]:
        """Parse boolean from yes/no/true/false variants."""
        v = value.strip().lower()
        if v in ['yes', 'true', '1', 'y']:
            return True
        elif v in ['no', 'false', '0', 'n']:
            return False
        return None
    
    @staticmethod
    def parse_list(value: str, delimiter: str = ',') -> List[str]:
        """Parse delimited string into list."""
        return [item.strip() for item in value.split(delimiter) if item.strip()]
