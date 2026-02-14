"""Smart Parser

Universal type casting and data transformation for config-driven web scraping.
Supports FinViz, Yahoo Finance, Alpha Vantage, and other sources.

This parser is SOURCE-AGNOSTIC - it uses DataType enums and transformation
functions to intelligently cast raw HTML strings into typed values.

Last Updated: December 20, 2025
Status: Active
"""

from typing import Any
from app.models.cartographer import DataType
from app.core.logging_config import get_logger
from app.services.cartographer.type_parsers import TypeParsers
from app.services.cartographer.transformations import Transformations

logger = get_logger(__name__)


class SmartParser:
    """Intelligently casts raw HTML strings to typed values."""
    
    # Type dispatch map
    _TYPE_DISPATCH = {
        DataType.STRING: TypeParsers.parse_string,
        DataType.INTEGER: TypeParsers.parse_integer,
        DataType.FLOAT: TypeParsers.parse_float,
        DataType.PERCENTAGE: TypeParsers.parse_percentage,
        DataType.CURRENCY: TypeParsers.parse_currency,
        DataType.DATE: TypeParsers.parse_date,
        DataType.BOOLEAN: TypeParsers.parse_boolean,
        DataType.LIST: TypeParsers.parse_list
    }
    
    @staticmethod
    def parse(raw_value: str, data_type: DataType, transformation: str = None) -> Any:
        """
        Parse raw string value to typed value.
        
        Args:
            raw_value: Raw string from HTML
            data_type: Target data type
            transformation: Optional transformation function name
            
        Returns:
            Typed value or None if parsing fails
        """
        if not raw_value or raw_value.strip() in ["-", "N/A", "", "n/a"]:
            return None
        
        try:
            # Apply transformation if specified
            if transformation:
                transformer = getattr(Transformations, transformation, None)
                if transformer:
                    return transformer(raw_value)
                logger.warning("Transformation not found", extra={"transformation": transformation})
            
            # Dispatch to type parser
            parser = SmartParser._TYPE_DISPATCH.get(data_type)
            if parser:
                return parser(raw_value)
            
            logger.warning("Unknown data type", extra={"data_type": data_type})
            return raw_value
                
        except Exception as e:
            logger.error("Parsing failed", extra={"data_type": data_type, "error": str(e)}, exc_info=True)
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
