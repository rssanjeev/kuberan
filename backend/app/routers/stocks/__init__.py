"""
Stock Router Package - Modular stock-related API endpoints

IMPORTANT: When modifying endpoints in this package, update the API documentation:
    docs/API.md

This package is split into focused modules for maintainability:
    - ticker_list.py: Listing and filtering tickers
    - ticker_info.py: Individual ticker information
    - ticker_history.py: Historical price data
    - ticker_config.py: System configuration and market status

Each module is kept under 300 lines for better AI/human readability.
"""
from fastapi import APIRouter
from .ticker_list import router as ticker_list_router
from .ticker_info import router as ticker_info_router
from .ticker_history import router as ticker_history_router
from .ticker_config import router as ticker_config_router

# Main router that aggregates all sub-routers
router = APIRouter(prefix="/stocks", tags=["stocks"])

# Include all sub-routers
router.include_router(ticker_list_router)
router.include_router(ticker_info_router)
router.include_router(ticker_history_router)
router.include_router(ticker_config_router)

__all__ = ["router"]
