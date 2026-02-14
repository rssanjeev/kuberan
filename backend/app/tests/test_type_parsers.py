"""
Unit Tests for TypeParsers

Tests all 8 type parsing methods with edge cases.

Run:
    cd backend
    python3 -m pytest app/tests/test_type_parsers.py -v
"""

import pytest
from datetime import datetime
from app.services.cartographer.type_parsers import TypeParsers


class TestParseString:
    """Test parse_string() method."""
    
    def test_basic_string(self):
        assert TypeParsers.parse_string("Hello World") == "Hello World"
    
    def test_whitespace_trimming(self):
        assert TypeParsers.parse_string("  trimmed  ") == "trimmed"
    
    def test_multiline_string(self):
        result = TypeParsers.parse_string("Line 1\nLine 2")
        assert result == "Line 1\nLine 2"
    
    def test_none_value(self):
        assert TypeParsers.parse_string(None) is None
    
    def test_empty_string(self):
        assert TypeParsers.parse_string("") is None
    
    def test_whitespace_only(self):
        assert TypeParsers.parse_string("   ") is None


class TestParseInteger:
    """Test parse_integer() method."""
    
    def test_basic_integer(self):
        assert TypeParsers.parse_integer("42") == 42
    
    def test_negative_integer(self):
        assert TypeParsers.parse_integer("-123") == -123
    
    def test_with_commas(self):
        assert TypeParsers.parse_integer("1,234,567") == 1234567
    
    def test_with_spaces(self):
        assert TypeParsers.parse_integer("  999  ") == 999
    
    def test_invalid_integer(self):
        assert TypeParsers.parse_integer("abc") is None
    
    def test_float_string(self):
        # Should fail - floats not allowed
        assert TypeParsers.parse_integer("123.45") is None
    
    def test_none_value(self):
        assert TypeParsers.parse_integer(None) is None
    
    def test_empty_string(self):
        assert TypeParsers.parse_integer("") is None


class TestParseFloat:
    """Test parse_float() method."""
    
    def test_basic_float(self):
        assert TypeParsers.parse_float("3.14") == 3.14
    
    def test_negative_float(self):
        assert TypeParsers.parse_float("-9.99") == -9.99
    
    def test_integer_as_float(self):
        assert TypeParsers.parse_float("42") == 42.0
    
    def test_with_commas(self):
        assert TypeParsers.parse_float("1,234.56") == 1234.56
    
    def test_scientific_notation(self):
        assert TypeParsers.parse_float("1.5e3") == 1500.0
    
    def test_invalid_float(self):
        assert TypeParsers.parse_float("not a number") is None
    
    def test_none_value(self):
        assert TypeParsers.parse_float(None) is None
    
    def test_empty_string(self):
        assert TypeParsers.parse_float("") is None


class TestParsePercentage:
    """Test parse_percentage() method."""
    
    def test_basic_percentage(self):
        assert TypeParsers.parse_percentage("75.5%") == 75.5
    
    def test_without_percent_sign(self):
        # Should still work if number without %
        assert TypeParsers.parse_percentage("25.0") == 25.0
    
    def test_negative_percentage(self):
        assert TypeParsers.parse_percentage("-10.5%") == -10.5
    
    def test_with_spaces(self):
        assert TypeParsers.parse_percentage("  50 %  ") == 50.0
    
    def test_zero_percent(self):
        assert TypeParsers.parse_percentage("0%") == 0.0
    
    def test_over_100_percent(self):
        assert TypeParsers.parse_percentage("150.75%") == 150.75
    
    def test_invalid_percentage(self):
        assert TypeParsers.parse_percentage("N/A") is None
    
    def test_none_value(self):
        assert TypeParsers.parse_percentage(None) is None


class TestParseCurrency:
    """Test parse_currency() method."""
    
    def test_basic_currency(self):
        assert TypeParsers.parse_currency("$123.45") == 123.45
    
    def test_with_k_suffix(self):
        assert TypeParsers.parse_currency("$50K") == 50000.0
    
    def test_with_m_suffix(self):
        assert TypeParsers.parse_currency("$2.5M") == 2500000.0
    
    def test_with_b_suffix(self):
        assert TypeParsers.parse_currency("$1.2B") == 1200000000.0
    
    def test_with_t_suffix(self):
        assert TypeParsers.parse_currency("$3.75T") == 3750000000000.0
    
    def test_without_dollar_sign(self):
        assert TypeParsers.parse_currency("999.99") == 999.99
    
    def test_with_commas(self):
        assert TypeParsers.parse_currency("$1,234,567.89") == 1234567.89
    
    def test_negative_currency(self):
        assert TypeParsers.parse_currency("-$50.00") == -50.0
    
    def test_invalid_currency(self):
        assert TypeParsers.parse_currency("invalid") is None
    
    def test_none_value(self):
        assert TypeParsers.parse_currency(None) is None


class TestParseDate:
    """Test parse_date() method."""
    
    def test_iso_format(self):
        result = TypeParsers.parse_date("2025-12-20")
        assert result == datetime(2025, 12, 20)
    
    def test_us_format(self):
        result = TypeParsers.parse_date("Dec 20, 2025")
        assert result.year == 2025
        assert result.month == 12
        assert result.day == 20
    
    def test_slash_format(self):
        result = TypeParsers.parse_date("12/20/2025")
        # Depends on dateutil parsing
        assert result is not None
    
    def test_invalid_date(self):
        assert TypeParsers.parse_date("not a date") is None
    
    def test_none_value(self):
        assert TypeParsers.parse_date(None) is None
    
    def test_empty_string(self):
        assert TypeParsers.parse_date("") is None


class TestParseBoolean:
    """Test parse_boolean() method."""
    
    def test_true_values(self):
        assert TypeParsers.parse_boolean("true") is True
        assert TypeParsers.parse_boolean("True") is True
        assert TypeParsers.parse_boolean("TRUE") is True
        assert TypeParsers.parse_boolean("yes") is True
        assert TypeParsers.parse_boolean("Yes") is True
        assert TypeParsers.parse_boolean("1") is True
    
    def test_false_values(self):
        assert TypeParsers.parse_boolean("false") is False
        assert TypeParsers.parse_boolean("False") is False
        assert TypeParsers.parse_boolean("FALSE") is False
        assert TypeParsers.parse_boolean("no") is False
        assert TypeParsers.parse_boolean("No") is False
        assert TypeParsers.parse_boolean("0") is False
    
    def test_invalid_boolean(self):
        assert TypeParsers.parse_boolean("maybe") is None
    
    def test_none_value(self):
        assert TypeParsers.parse_boolean(None) is None
    
    def test_empty_string(self):
        assert TypeParsers.parse_boolean("") is None


class TestParseList:
    """Test parse_list() method."""
    
    def test_comma_separated(self):
        result = TypeParsers.parse_list("apple, banana, cherry")
        assert result == ["apple", "banana", "cherry"]
    
    def test_semicolon_separated(self):
        result = TypeParsers.parse_list("item1; item2; item3")
        assert result == ["item1", "item2", "item3"]
    
    def test_pipe_separated(self):
        result = TypeParsers.parse_list("A | B | C")
        assert result == ["A", "B", "C"]
    
    def test_single_item(self):
        result = TypeParsers.parse_list("single")
        assert result == ["single"]
    
    def test_with_whitespace(self):
        result = TypeParsers.parse_list("  one  ,  two  ,  three  ")
        assert result == ["one", "two", "three"]
    
    def test_empty_items_filtered(self):
        result = TypeParsers.parse_list("a, , b, , c")
        assert result == ["a", "b", "c"]
    
    def test_none_value(self):
        assert TypeParsers.parse_list(None) is None
    
    def test_empty_string(self):
        assert TypeParsers.parse_list("") is None


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_special_characters(self):
        # Strings with special chars should be preserved
        result = TypeParsers.parse_string("$100 & <tag>")
        assert result == "$100 & <tag>"
    
    def test_unicode(self):
        result = TypeParsers.parse_string("Hello 世界 🌍")
        assert result == "Hello 世界 🌍"
    
    def test_very_large_numbers(self):
        result = TypeParsers.parse_integer("999999999999")
        assert result == 999999999999
    
    def test_very_small_float(self):
        result = TypeParsers.parse_float("0.0000001")
        assert result == 0.0000001
    
    def test_mixed_case_boolean(self):
        assert TypeParsers.parse_boolean("TrUe") is True
        assert TypeParsers.parse_boolean("FaLsE") is False
