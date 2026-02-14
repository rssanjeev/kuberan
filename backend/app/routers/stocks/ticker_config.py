"""
Ticker Config Module - System configuration and market status

Endpoints:
    - GET /market/status: Check if NYSE market is open
    - GET /config/routing: Get provider routing configuration
"""
from fastapi import APIRouter
from datetime import datetime
import pytz
from app.core.market_calendar import is_market_open
from typing import Dict, Any

router = APIRouter()


@router.get("/market/status")
async def get_market_status():
    """
    Check if the NYSE market is open today.
    """
    est = pytz.timezone('US/Eastern')
    today = datetime.now(est).date()
    is_open = is_market_open(today)
    
    return {
        "date": today.isoformat(),
        "is_market_open": is_open,
        "message": "Market is open for trading" if is_open else "Market is closed (holiday or weekend)"
    }


@router.get("/config/routing")
async def get_provider_routing_config():
    """
    Get provider routing configuration showing which data source is used for each data type.
    
    Returns the system's current strategy for selecting providers:
    - Which provider is preferred for each data type (price, fundamentals, news, etc.)
    - Fallback providers if primary fails
    - Reasoning behind each choice
    
    This endpoint provides transparency into multi-provider data sourcing.
    
    Example response:
    {
        "routing_strategy": {
            "quote": {
                "primary": "yfinance",
                "fallback": ["alpha_vantage", "finnhub"],
                "reason": "YFinance free tier, good coverage for prices"
            },
            "company_overview": {
                "primary": "alpha_vantage",
                "fallback": ["finnhub"],
                "reason": "AlphaVantage provides more comprehensive company data"
            }
        },
        "last_updated": "2025-11-17T10:00:00Z"
    }
    """
    # Define provider routing configuration
    routing_config = {
        "quote": {
            "primary": "yfinance",
            "fallback": ["alpha_vantage", "finnhub"],
            "reason": "YFinance free tier with good coverage, unlimited API calls",
            "data_points": ["price", "open", "high", "low", "volume", "change", "change_percent"]
        },
        "historical_prices": {
            "primary": "yfinance",
            "fallback": ["alpha_vantage"],
            "reason": "YFinance has 20+ years of historical data, free and unlimited",
            "data_points": ["OHLCV data", "adjusted close", "split/dividend adjustments"]
        },
        "company_overview": {
            "primary": "alpha_vantage",
            "fallback": ["finnhub"],
            "reason": "AlphaVantage provides comprehensive company fundamentals",
            "data_points": ["sector", "industry", "description", "market_cap", "pe_ratio", "address", "website"]
        },
        "fundamentals": {
            "primary": "alpha_vantage",
            "fallback": [],
            "reason": "Only AlphaVantage provides complete financial statements via MCP tools",
            "data_points": ["income_statement", "balance_sheet", "cash_flow", "earnings"]
        },
        "technical_indicators": {
            "primary": "alpha_vantage",
            "fallback": [],
            "reason": "AlphaVantage has 50+ technical indicators via MCP tools",
            "data_points": ["SMA", "EMA", "RSI", "MACD", "Bollinger Bands", "40+ more"]
        },
        "dividends": {
            "primary": "yfinance",
            "fallback": ["alpha_vantage"],
            "reason": "YFinance has complete dividend history, free and unlimited",
            "data_points": ["dividend_date", "dividend_amount", "historical_dividends"]
        },
        "splits": {
            "primary": "yfinance",
            "fallback": ["alpha_vantage"],
            "reason": "YFinance provides detailed split history with ratios",
            "data_points": ["split_date", "split_ratio", "split_description"]
        },
        "earnings": {
            "primary": "alpha_vantage",
            "fallback": ["finnhub"],
            "reason": "AlphaVantage provides both historical and estimated earnings",
            "data_points": ["quarterly_earnings", "annual_earnings", "earnings_estimates"]
        },
        "news": {
            "primary": "finnhub",
            "fallback": ["alpha_vantage"],
            "reason": "Finnhub specializes in financial news with excellent coverage",
            "data_points": ["headline", "summary", "source", "timestamp", "sentiment"]
        },
        "analyst_ratings": {
            "primary": "finnhub",
            "fallback": [],
            "reason": "Only Finnhub provides analyst recommendations and upgrades/downgrades",
            "data_points": ["buy", "hold", "sell", "strong_buy", "strong_sell"]
        },
        "price_targets": {
            "primary": "finnhub",
            "fallback": [],
            "reason": "Finnhub provides analyst price targets",
            "data_points": ["target_high", "target_low", "target_mean", "target_median"]
        },
        "etf_holdings": {
            "primary": "alpha_vantage",
            "fallback": [],
            "reason": "Only AlphaVantage provides ETF holdings via ETF_PROFILE MCP tool",
            "data_points": ["holdings", "asset_allocation", "sector_weights", "top_10_holdings"]
        }
    }
    
    return {
        "routing_strategy": routing_config,
        "active_providers": ["yfinance", "alpha_vantage", "finnhub"],
        "can_switch_providers": True,
        "switch_method": "Update provider_routing_config.py or modify preferred_provider parameter in API calls",
        "last_updated": "2025-11-17T00:00:00Z",
        "documentation": "See docs/MULTI_PROVIDER_ARCHITECTURE.md for detailed architecture"
    }
