"""
Smart Parser

Universal type casting and data transformation for config-driven web scraping.
Supports FinViz, Yahoo Finance, Alpha Vantage, and other sources.

This parser is SOURCE-AGNOSTIC - it uses DataType enums and transformation
functions to intelligently cast raw HTML strings into typed values.

Last Updated: December 20, 2025
Status: 🟢 Active
"""

import re
from typing import Any, Optional, List
from datetime import datetime
from app.models.cartographer import DataType
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class SmartParser:
    """Intelligently casts raw HTML strings to typed values."""
    
    @staticmethod
    def parse(
        raw_value: str,
        data_type: DataType,
        transformation: Optional[str] = None
    ) -> Any:
        """
        Parse raw string value to typed value.
        
        Args:
            raw_value: Raw string from HTML
            data_type: Target data type
            transformation: Optional transformation function name
            
        Returns:
            Typed value or None if parsing fails
            
        Example:
            >>> SmartParser.parse("5.5%", DataType.PERCENTAGE)
            5.5
            >>> SmartParser.parse("2.77T", DataType.CURRENCY, "parse_market_cap")
            2.77e12
        """
        if not raw_value or raw_value.strip() in ["-", "N/A", "", "n/a"]:
            return None
        
        try:
            # Apply transformation first if specified
            if transformation:
                transformer = getattr(SmartParser, transformation, None)
                if transformer:
                    return transformer(raw_value)
                else:
                    logger.warning(
                        "Transformation function not found",
                        extra={"function": transformation, "raw_value": raw_value}
                    )
            
            # Standard type casting
            if data_type == DataType.STRING:
                return SmartParser._parse_string(raw_value)
            elif data_type == DataType.INTEGER:
                return SmartParser._parse_integer(raw_value)
            elif data_type == DataType.FLOAT:
                return SmartParser._parse_float(raw_value)
            elif data_type == DataType.PERCENTAGE:
                return SmartParser._parse_percentage(raw_value)
            elif data_type == DataType.CURRENCY:
                return SmartParser._parse_currency(raw_value)
            elif data_type == DataType.DATE:
                return SmartParser._parse_date(raw_value)
            elif data_type == DataType.BOOLEAN:
                return SmartParser._parse_boolean(raw_value)
            elif data_type == DataType.LIST:
                return SmartParser._parse_list(raw_value)
            else:
                logger.warning(
                    "Unknown data type",
                    extra={"data_type": data_type, "raw_value": raw_value}
                )
                return raw_value
                
        except Exception as e:
            logger.error(
                "Parsing failed",
                extra={
                    "raw_value": raw_value,
                    "data_type": data_type,
                    "error": str(e)
                },
                exc_info=True
            )
            return None
    
    @staticmethod
    def _parse_string(value: str) -> str:
        """Clean and return string."""
        return value.strip()
    
    @staticmethod
    def _parse_integer(value: str) -> Optional[int]:
        """Parse integer with comma/space removal."""
        cleaned = re.sub(r'[,\s]', '', value.strip())
        try:
            return int(float(cleaned))
        except ValueError:
            return None
    
    @staticmethod
    def _parse_float(value: str) -> Optional[float]:
        """Parse float with comma/space removal."""
        cleaned = re.sub(r'[,\s]', '', value.strip())
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    @staticmethod
    def _parse_percentage(value: str) -> Optional[float]:
        """Parse percentage string to float (e.g., '5.5%' -> 5.5)."""
        cleaned = value.strip().replace('%', '').replace(',', '')
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    @staticmethod
    def _parse_currency(value: str) -> Optional[float]:
        """Parse currency (removes $, commas)."""
        cleaned = re.sub(r'[$,\s]', '', value.strip())
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    @staticmethod
    def _parse_date(value: str) -> Optional[str]:
        """Parse date string (returns ISO format)."""
        # Try common date formats
        formats = [
            "%b %d, %Y",      # Dec 13, 2025
            "%Y-%m-%d",       # 2025-12-13
            "%m/%d/%Y",       # 12/13/2025
            "%d/%m/%Y",       # 13/12/2025
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(value.strip(), fmt)
                return dt.isoformat()
            except ValueError:
                continue
        
        logger.warning("Date parsing failed", extra={"value": value})
        return value.strip()
    
    @staticmethod
    def _parse_boolean(value: str) -> Optional[bool]:
        """Parse boolean from string."""
        lower = value.strip().lower()
        if lower in ['yes', 'true', '1', 'y']:
            return True
        elif lower in ['no', 'false', '0', 'n']:
            return False
        return None
    
    @staticmethod
    def _parse_list(value: str, delimiter: str = ",") -> List[str]:
        """Parse comma-separated list."""
        items = [item.strip() for item in value.split(delimiter)]
        return [item for item in items if item]
    
    # Transformation Functions (source-specific)
    
    @staticmethod
    def parse_market_cap(value: str) -> Optional[float]:
        """
        Parse market cap with B/M/T suffixes.
        
        Examples:
            '2.77T' -> 2.77e12
            '45.2B' -> 45.2e9
            '123.45M' -> 123.45e6
        """
        value = value.strip().upper()
        
        # Extract numeric part and suffix
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
        
        Examples:
            '4.06M' -> 4060000
            '45.2K' -> 45200
        """
        result = SmartParser.parse_market_cap(value)
        return int(result) if result else None
    
    @staticmethod
    def parse_dividend_ttm(value: str) -> Optional[dict]:
        """
        Parse dividend TTM format: '3.75 (1.11%)'.
        
        Returns:
            {'amount': 3.75, 'yield': 1.11}
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
    def parse_dividend_growth(value: str) -> Optional[dict]:
        """
        Parse dividend growth format: '7.83% / 4.81%'.
        
        Returns:
            {'growth_3y': 7.83, 'growth_5y': 4.81}
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
    def parse_volatility(value: str) -> Optional[dict]:
        """
        Parse volatility format: '0.99% 1.26%'.
        
        Returns:
            {'short_term': 0.99, 'long_term': 1.26}
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
    def parse_price_range(value: str) -> Optional[dict]:
        """
        Parse price range format: '280.00 - 345.00'.
        
        Returns:
            {'low': 280.00, 'high': 345.00}
        """
        match = re.match(r'([\d.]+)\s*-\s*([\d.]+)', value.strip())
        if match:
            low, high = match.groups()
            return {
                'low': float(low),
                'high': float(high)
            }
        return None
    
    @staticmethod
    def validate_result(result: Any, data_type: DataType) -> bool:
        """
        Validate that parsed result matches expected type.
        
        Args:
            result: Parsed value
            data_type: Expected data type
            
        Returns:
            True if valid, False otherwise
        """
        if result is None:
            return True  # None is valid for optional fields
        
        type_map = {
            DataType.STRING: str,
            DataType.INTEGER: int,
            DataType.FLOAT: (int, float),
            DataType.PERCENTAGE: (int, float),
            DataType.CURRENCY: (int, float),
            DataType.DATE: str,
            DataType.BOOLEAN: bool,
            DataType.LIST: list
        }
        
        expected_type = type_map.get(data_type)
        if expected_type:
            return isinstance(result, expected_type)
        
        return False
