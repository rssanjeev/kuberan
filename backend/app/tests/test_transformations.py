"""
Unit Tests for Transformations

Tests all 6 financial transformation methods with edge cases.

Run:
    cd backend
    python3 -m pytest app/tests/test_transformations.py -v
"""

import pytest
from app.services.cartographer.transformations import Transformations


class TestParseMarketCap:
    """Test parse_market_cap() method."""
    
    def test_trillion_suffix(self):
        assert Transformations.parse_market_cap("2.77T") == 2.77e12
    
    def test_billion_suffix(self):
        assert Transformations.parse_market_cap("45.5B") == 45.5e9
    
    def test_million_suffix(self):
        assert Transformations.parse_market_cap("150.25M") == 150.25e6
    
    def test_thousand_suffix(self):
        assert Transformations.parse_market_cap("500K") == 500000.0
    
    def test_no_suffix(self):
        # Raw numbers without suffix
        assert Transformations.parse_market_cap("1234567") == 1234567.0
    
    def test_with_dollar_sign(self):
        assert Transformations.parse_market_cap("$1.5T") == 1.5e12
    
    def test_with_spaces(self):
        assert Transformations.parse_market_cap("  3.2 B  ") == 3.2e9
    
    def test_lowercase_suffix(self):
        assert Transformations.parse_market_cap("10.5t") == 10.5e12
        assert Transformations.parse_market_cap("25m") == 25e6
    
    def test_invalid_value(self):
        assert Transformations.parse_market_cap("N/A") is None
    
    def test_none_value(self):
        assert Transformations.parse_market_cap(None) is None
    
    def test_empty_string(self):
        assert Transformations.parse_market_cap("") is None


class TestParseVolume:
    """Test parse_volume() method."""
    
    def test_million_suffix(self):
        assert Transformations.parse_volume("15.3M") == 15300000
    
    def test_billion_suffix(self):
        assert Transformations.parse_volume("2.5B") == 2500000000
    
    def test_thousand_suffix(self):
        assert Transformations.parse_volume("750K") == 750000
    
    def test_no_suffix(self):
        assert Transformations.parse_volume("123456") == 123456
    
    def test_with_commas(self):
        assert Transformations.parse_volume("1,234,567") == 1234567
    
    def test_with_spaces(self):
        assert Transformations.parse_volume("  10.5 M  ") == 10500000
    
    def test_lowercase_suffix(self):
        assert Transformations.parse_volume("5.2m") == 5200000
    
    def test_invalid_value(self):
        assert Transformations.parse_volume("invalid") is None
    
    def test_none_value(self):
        assert Transformations.parse_volume(None) is None
    
    def test_empty_string(self):
        assert Transformations.parse_volume("") is None


class TestParseDividendTTM:
    """Test parse_dividend_ttm() method."""
    
    def test_amount_with_yield(self):
        # Format: "3.75 (1.11%)"
        result = Transformations.parse_dividend_ttm("3.75 (1.11%)")
        assert result == {"amount": 3.75, "yield_pct": 1.11}
    
    def test_amount_only(self):
        result = Transformations.parse_dividend_ttm("2.50")
        assert result == {"amount": 2.50, "yield_pct": None}
    
    def test_yield_only(self):
        result = Transformations.parse_dividend_ttm("(1.5%)")
        assert result == {"amount": None, "yield_pct": 1.5}
    
    def test_no_dividend(self):
        assert Transformations.parse_dividend_ttm("N/A") is None
        assert Transformations.parse_dividend_ttm("-") is None
    
    def test_with_dollar_sign(self):
        result = Transformations.parse_dividend_ttm("$4.25 (2.3%)")
        assert result == {"amount": 4.25, "yield_pct": 2.3}
    
    def test_none_value(self):
        assert Transformations.parse_dividend_ttm(None) is None
    
    def test_empty_string(self):
        assert Transformations.parse_dividend_ttm("") is None


class TestParseFlows:
    """Test parse_flows() method."""
    
    def test_positive_percentage(self):
        assert Transformations.parse_flows("10.25%") == 10.25
    
    def test_negative_percentage(self):
        assert Transformations.parse_flows("-5.50%") == -5.50
    
    def test_without_percent_sign(self):
        assert Transformations.parse_flows("8.75") == 8.75
    
    def test_with_spaces(self):
        assert Transformations.parse_flows("  12.5 %  ") == 12.5
    
    def test_no_flow_data(self):
        assert Transformations.parse_flows("N/A") is None
        assert Transformations.parse_flows("-") is None
    
    def test_none_value(self):
        assert Transformations.parse_flows(None) is None
    
    def test_empty_string(self):
        assert Transformations.parse_flows("") is None


class TestParsePERatio:
    """Test parse_pe_ratio() method."""
    
    def test_standard_pe(self):
        assert Transformations.parse_pe_ratio("25.5") == 25.5
    
    def test_negative_pe(self):
        # Negative P/E means negative earnings
        assert Transformations.parse_pe_ratio("-10.2") == -10.2
    
    def test_very_high_pe(self):
        assert Transformations.parse_pe_ratio("500.75") == 500.75
    
    def test_with_spaces(self):
        assert Transformations.parse_pe_ratio("  18.3  ") == 18.3
    
    def test_na_value(self):
        assert Transformations.parse_pe_ratio("N/A") is None
    
    def test_dash_value(self):
        assert Transformations.parse_pe_ratio("-") is None
    
    def test_none_value(self):
        assert Transformations.parse_pe_ratio(None) is None
    
    def test_empty_string(self):
        assert Transformations.parse_pe_ratio("") is None


class TestParsePercentageChange:
    """Test parse_percentage_change() method."""
    
    def test_positive_change(self):
        assert Transformations.parse_percentage_change("+5.25%") == 5.25
    
    def test_negative_change(self):
        assert Transformations.parse_percentage_change("-3.75%") == -3.75
    
    def test_without_sign(self):
        assert Transformations.parse_percentage_change("2.5%") == 2.5
    
    def test_without_percent_sign(self):
        assert Transformations.parse_percentage_change("+10.0") == 10.0
    
    def test_zero_change(self):
        assert Transformations.parse_percentage_change("0%") == 0.0
    
    def test_with_spaces(self):
        assert Transformations.parse_percentage_change("  + 7.5 %  ") == 7.5
    
    def test_invalid_value(self):
        assert Transformations.parse_percentage_change("invalid") is None
    
    def test_none_value(self):
        assert Transformations.parse_percentage_change(None) is None
    
    def test_empty_string(self):
        assert Transformations.parse_percentage_change("") is None


class TestEdgeCases:
    """Test edge cases and complex scenarios."""
    
    def test_market_cap_with_decimal_suffix(self):
        # Very precise values
        assert Transformations.parse_market_cap("1.2345T") == 1.2345e12
    
    def test_volume_integer_result(self):
        # Volume should return integers
        result = Transformations.parse_volume("10.5M")
        assert result == 10500000
        assert isinstance(result, int)
    
    def test_dividend_complex_format(self):
        # Real-world format from FinViz
        result = Transformations.parse_dividend_ttm("$0.98 (0.35%)")
        assert result == {"amount": 0.98, "yield_pct": 0.35}
    
    def test_flows_very_large_percentage(self):
        # ETFs can have large flow percentages
        assert Transformations.parse_flows("250.5%") == 250.5
    
    def test_pe_ratio_zero_earnings(self):
        # Company with zero earnings (undefined P/E)
        assert Transformations.parse_pe_ratio("N/A") is None
    
    def test_percentage_change_large_swing(self):
        # Large price swings
        assert Transformations.parse_percentage_change("+150.0%") == 150.0
        assert Transformations.parse_percentage_change("-80.5%") == -80.5


class TestRealWorldData:
    """Test with actual data from FinViz."""
    
    def test_nvidia_market_cap(self):
        # NVDA market cap example
        assert Transformations.parse_market_cap("2.77T") == 2.77e12
    
    def test_vti_dividend(self):
        # VTI dividend example
        result = Transformations.parse_dividend_ttm("3.75 (1.11%)")
        assert result == {"amount": 3.75, "yield_pct": 1.11}
    
    def test_vti_flows(self):
        # VTI flow examples
        assert Transformations.parse_flows("10.25%") == 10.25
    
    def test_apple_pe_ratio(self):
        # AAPL P/E example
        assert Transformations.parse_pe_ratio("45.23") == 45.23
    
    def test_stock_percentage_change(self):
        # Daily price change
        assert Transformations.parse_percentage_change("-1.14%") == -1.14
