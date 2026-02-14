"""
Transformations
Source-specific data transformation functions.
"""

import re
from typing import Optional, Dict
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class Transformations:
    """Collection of source-specific transformation functions."""
    
    @staticmethod
    def parse_market_cap(value: str) -> Optional[float]:
        """
        Parse market cap with K/M/B/T suffixes.
        Examples: '2.77T' -> 2.77e12, '45.2B' -> 45.2e9
        """
        value = value.strip().upper()
        match = re.match(r'([\d,.]+)\s*([KMBT])?', value)
        if not match:
            return None
        
        number_str, suffix = match.groups()
        number = float(number_str.replace(',', ''))
        
        multipliers = {
            'K': 1e3,
            'M': 1e6,
            'B': 1e9,
            'T': 1e12
        }
        
        multiplier = multipliers.get(suffix, 1.0)
        return number * multiplier
    
    @staticmethod
    def parse_volume(value: str) -> Optional[int]:
        """
        Parse volume with K/M/B suffixes.
        Examples: '4.06M' -> 4060000, '45.2K' -> 45200
        """
        result = Transformations.parse_market_cap(value)
        return int(result) if result else None
    
    @staticmethod
    def parse_dividend_ttm(value: str) -> Optional[Dict]:
        """
        Parse dividend TTM format: '3.75 (1.11%)'.
        Returns: {'amount': 3.75, 'yield': 1.11}
        """
        match = re.match(r'([\d.]+)\s*\(([\d.]+)%\)', value.strip())
        if match:
            amount_str, yield_str = match.groups()
            return {
                'amount': float(amount_str),
                'yield': float(yield_str)
            }
        return None
    
    @staticmethod
    def parse_dividend_growth(value: str) -> Optional[Dict]:
        """
        Parse dividend growth format: '7.83% / 4.81%'.
        Returns: {'growth_3y': 7.83, 'growth_5y': 4.81}
        """
        match = re.match(r'([\d.]+)%\s*/\s*([\d.]+)%', value.strip())
        if match:
            growth_3y, growth_5y = match.groups()
            return {
                'growth_3y': float(growth_3y),
                'growth_5y': float(growth_5y)
            }
        return None
    
    @staticmethod
    def parse_volatility(value: str) -> Optional[Dict]:
        """
        Parse volatility format: '0.99% 1.26%'.
        Returns: {'short_term': 0.99, 'long_term': 1.26}
        """
        parts = value.strip().replace('%', '').split()
        if len(parts) == 2:
            try:
                return {
                    'short_term': float(parts[0]),
                    'long_term': float(parts[1])
                }
            except ValueError:
                pass
        return None
    
    @staticmethod
    def parse_price_range(value: str) -> Optional[Dict]:
        """
        Parse price range format: '280.00 - 345.00'.
        Returns: {'low': 280.00, 'high': 345.00}
        """
        match = re.match(r'([\d.]+)\s*-\s*([\d.]+)', value.strip())
        if match:
            low, high = match.groups()
            return {
                'low': float(low),
                'high': float(high)
            }
        return None
