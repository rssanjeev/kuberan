"""
Unit Tests for SmartParser

Tests the parse() and validate_result() methods with all 8 DataTypes.

Run:
    cd backend
    python3 -m pytest app/tests/test_smart_parser.py -v
"""

import pytest
from datetime import datetime
from app.services.cartographer.smart_parser import SmartParser
from app.models.cartographer import DataType


class TestParseWithoutTransformation:
    """Test parse() method with direct type parsing (no transformations)."""
    
    def test_parse_string(self):
        result = SmartParser.parse("  Hello World  ", DataType.STRING)
        assert result == "Hello World"
    
    def test_parse_integer(self):
        result = SmartParser.parse("1,234,567", DataType.INTEGER)
        assert result == 1234567
    
    def test_parse_float(self):
        result = SmartParser.parse("123.456", DataType.FLOAT)
        assert result == 123.456
    
    def test_parse_percentage(self):
        result = SmartParser.parse("25.5%", DataType.PERCENTAGE)
        assert result == 25.5
    
    def test_parse_currency(self):
        result = SmartParser.parse("$2.5M", DataType.CURRENCY)
        assert result == 2500000.0
    
    def test_parse_date(self):
        result = SmartParser.parse("2025-12-21", DataType.DATE)
        assert isinstance(result, datetime)
        assert result.year == 2025
        assert result.month == 12
        assert result.day == 21
    
    def test_parse_boolean(self):
        assert SmartParser.parse("true", DataType.BOOLEAN) is True
        assert SmartParser.parse("false", DataType.BOOLEAN) is False
    
    def test_parse_list(self):
        result = SmartParser.parse("apple, banana, cherry", DataType.LIST)
        assert result == ["apple", "banana", "cherry"]


class TestParseWithTransformation:
    """Test parse() method with transformations."""
    
    def test_market_cap_transformation(self):
        result = SmartParser.parse("2.77T", DataType.CURRENCY, transformation="parse_market_cap")
        assert result == 2.77e12
    
    def test_volume_transformation(self):
        result = SmartParser.parse("15.3M", DataType.INTEGER, transformation="parse_volume")
        assert result == 15300000
    
    def test_dividend_ttm_transformation(self):
        result = SmartParser.parse("3.75 (1.11%)", DataType.STRING, transformation="parse_dividend_ttm")
        assert result == {"amount": 3.75, "yield_pct": 1.11}
    
    def test_flows_transformation(self):
        result = SmartParser.parse("10.25%", DataType.PERCENTAGE, transformation="parse_flows")
        assert result == 10.25
    
    def test_pe_ratio_transformation(self):
        result = SmartParser.parse("45.23", DataType.FLOAT, transformation="parse_pe_ratio")
        assert result == 45.23
    
    def test_percentage_change_transformation(self):
        result = SmartParser.parse("-3.75%", DataType.PERCENTAGE, transformation="parse_percentage_change")
        assert result == -3.75


class TestParseNoneValues:
    """Test parse() method with None and empty values."""
    
    def test_parse_none_string(self):
        assert SmartParser.parse(None, DataType.STRING) is None
    
    def test_parse_none_integer(self):
        assert SmartParser.parse(None, DataType.INTEGER) is None
    
    def test_parse_none_float(self):
        assert SmartParser.parse(None, DataType.FLOAT) is None
    
    def test_parse_none_percentage(self):
        assert SmartParser.parse(None, DataType.PERCENTAGE) is None
    
    def test_parse_none_currency(self):
        assert SmartParser.parse(None, DataType.CURRENCY) is None
    
    def test_parse_none_date(self):
        assert SmartParser.parse(None, DataType.DATE) is None
    
    def test_parse_none_boolean(self):
        assert SmartParser.parse(None, DataType.BOOLEAN) is None
    
    def test_parse_none_list(self):
        assert SmartParser.parse(None, DataType.LIST) is None
    
    def test_parse_empty_string(self):
        assert SmartParser.parse("", DataType.STRING) is None


class TestValidateResult:
    """Test validate_result() method."""
    
    def test_validate_string(self):
        assert SmartParser.validate_result("Hello", DataType.STRING) is True
        assert SmartParser.validate_result(123, DataType.STRING) is False
    
    def test_validate_integer(self):
        assert SmartParser.validate_result(123, DataType.INTEGER) is True
        assert SmartParser.validate_result(123.45, DataType.INTEGER) is False
        assert SmartParser.validate_result("123", DataType.INTEGER) is False
    
    def test_validate_float(self):
        assert SmartParser.validate_result(123.45, DataType.FLOAT) is True
        assert SmartParser.validate_result(123, DataType.FLOAT) is True  # int is acceptable as float
        assert SmartParser.validate_result("123.45", DataType.FLOAT) is False
    
    def test_validate_percentage(self):
        assert SmartParser.validate_result(25.5, DataType.PERCENTAGE) is True
        assert SmartParser.validate_result(0.0, DataType.PERCENTAGE) is True
        assert SmartParser.validate_result(-10.5, DataType.PERCENTAGE) is True
        assert SmartParser.validate_result("25.5%", DataType.PERCENTAGE) is False
    
    def test_validate_currency(self):
        assert SmartParser.validate_result(1234567.89, DataType.CURRENCY) is True
        assert SmartParser.validate_result(100, DataType.CURRENCY) is True
        assert SmartParser.validate_result("$100", DataType.CURRENCY) is False
    
    def test_validate_date(self):
        assert SmartParser.validate_result(datetime.now(), DataType.DATE) is True
        assert SmartParser.validate_result("2025-12-21", DataType.DATE) is False
    
    def test_validate_boolean(self):
        assert SmartParser.validate_result(True, DataType.BOOLEAN) is True
        assert SmartParser.validate_result(False, DataType.BOOLEAN) is True
        assert SmartParser.validate_result(1, DataType.BOOLEAN) is False
        assert SmartParser.validate_result("true", DataType.BOOLEAN) is False
    
    def test_validate_list(self):
        assert SmartParser.validate_result(["a", "b", "c"], DataType.LIST) is True
        assert SmartParser.validate_result([], DataType.LIST) is True
        assert SmartParser.validate_result("a,b,c", DataType.LIST) is False
    
    def test_validate_none_values(self):
        # None is acceptable for all types (represents missing data)
        assert SmartParser.validate_result(None, DataType.STRING) is True
        assert SmartParser.validate_result(None, DataType.INTEGER) is True
        assert SmartParser.validate_result(None, DataType.FLOAT) is True
        assert SmartParser.validate_result(None, DataType.PERCENTAGE) is True
        assert SmartParser.validate_result(None, DataType.CURRENCY) is True
        assert SmartParser.validate_result(None, DataType.DATE) is True
        assert SmartParser.validate_result(None, DataType.BOOLEAN) is True
        assert SmartParser.validate_result(None, DataType.LIST) is True


class TestTypeDispatch:
    """Test _TYPE_DISPATCH dictionary routing."""
    
    def test_all_datatypes_have_parsers(self):
        # Verify all 8 DataTypes are in _TYPE_DISPATCH
        from app.services.cartographer.smart_parser import _TYPE_DISPATCH
        
        expected_types = [
            DataType.STRING,
            DataType.INTEGER,
            DataType.FLOAT,
            DataType.PERCENTAGE,
            DataType.CURRENCY,
            DataType.DATE,
            DataType.BOOLEAN,
            DataType.LIST
        ]
        
        for data_type in expected_types:
            assert data_type in _TYPE_DISPATCH, f"{data_type} missing from _TYPE_DISPATCH"
    
    def test_dispatch_calls_correct_parser(self):
        # Test that dispatch routes to correct parser by checking results
        assert isinstance(SmartParser.parse("123", DataType.INTEGER), int)
        assert isinstance(SmartParser.parse("123.45", DataType.FLOAT), float)
        assert isinstance(SmartParser.parse("2025-12-21", DataType.DATE), datetime)
        assert isinstance(SmartParser.parse("true", DataType.BOOLEAN), bool)
        assert isinstance(SmartParser.parse("a,b,c", DataType.LIST), list)


class TestInvalidTransformation:
    """Test parse() with invalid transformation names."""
    
    def test_nonexistent_transformation(self):
        # Invalid transformation should fall back to type parser
        result = SmartParser.parse("123.45", DataType.FLOAT, transformation="invalid_function")
        assert result == 123.45  # Falls back to type parser
    
    def test_transformation_with_none_value(self):
        result = SmartParser.parse(None, DataType.CURRENCY, transformation="parse_market_cap")
        assert result is None


class TestTransformationFallback:
    """Test transformation failure fallback to type parser."""
    
    def test_transformation_failure_falls_back(self):
        # If transformation fails, should fall back to type parser
        result = SmartParser.parse("invalid_value", DataType.FLOAT, transformation="parse_pe_ratio")
        # Transformation fails (returns None), parse() should handle gracefully
        assert result is None or isinstance(result, float)
    
    def test_na_value_with_transformation(self):
        result = SmartParser.parse("N/A", DataType.FLOAT, transformation="parse_pe_ratio")
        assert result is None


class TestEdgeCases:
    """Test edge cases and complex scenarios."""
    
    def test_very_large_integer(self):
        result = SmartParser.parse("999999999999", DataType.INTEGER)
        assert result == 999999999999
    
    def test_very_small_float(self):
        result = SmartParser.parse("0.0000001", DataType.FLOAT)
        assert result == 0.0000001
    
    def test_negative_currency(self):
        result = SmartParser.parse("-$50.25", DataType.CURRENCY)
        assert result == -50.25
    
    def test_list_with_empty_items(self):
        result = SmartParser.parse("a,,b,,c", DataType.LIST)
        assert result == ["a", "b", "c"]  # Empty items filtered
    
    def test_percentage_over_100(self):
        result = SmartParser.parse("250.5%", DataType.PERCENTAGE)
        assert result == 250.5
    
    def test_unicode_string(self):
        result = SmartParser.parse("Hello 世界 🌍", DataType.STRING)
        assert result == "Hello 世界 🌍"


class TestRealWorldScenarios:
    """Test with actual FinViz data scenarios."""
    
    def test_nvidia_market_cap(self):
        # NVDA: Market Cap = "2.77T"
        result = SmartParser.parse("2.77T", DataType.CURRENCY, transformation="parse_market_cap")
        assert result == 2.77e12
    
    def test_vti_dividend(self):
        # VTI: Dividend TTM = "3.75 (1.11%)"
        result = SmartParser.parse("3.75 (1.11%)", DataType.STRING, transformation="parse_dividend_ttm")
        assert result == {"amount": 3.75, "yield_pct": 1.11}
    
    def test_apple_pe_ratio(self):
        # AAPL: P/E = "45.23"
        result = SmartParser.parse("45.23", DataType.FLOAT, transformation="parse_pe_ratio")
        assert result == 45.23
    
    def test_stock_percentage_change(self):
        # Daily change = "-1.14%"
        result = SmartParser.parse("-1.14%", DataType.PERCENTAGE, transformation="parse_percentage_change")
        assert result == -1.14
    
    def test_volume_with_suffix(self):
        # Volume = "48.3M"
        result = SmartParser.parse("48.3M", DataType.INTEGER, transformation="parse_volume")
        assert result == 48300000
    
    def test_etf_flows(self):
        # VTI Flows 1Y = "10.25%"
        result = SmartParser.parse("10.25%", DataType.PERCENTAGE, transformation="parse_flows")
        assert result == 10.25
    
    def test_sector_string(self):
        # Sector = "Technology"
        result = SmartParser.parse("Technology", DataType.STRING)
        assert result == "Technology"
    
    def test_peers_list(self):
        # Peers = "AMD, AVGO, INTC, QCOM"
        result = SmartParser.parse("AMD, AVGO, INTC, QCOM", DataType.LIST)
        assert result == ["AMD", "AVGO", "INTC", "QCOM"]
