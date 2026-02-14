"""
Stock data services.
"""
from app.services.stock.fetcher import stock_fetcher

# For backwards compatibility
__all__ = ['stock_fetcher']
