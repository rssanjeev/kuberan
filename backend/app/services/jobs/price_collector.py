"""
Price collector job - Automated stock price polling during market hours.
Hybrid approach: Class for state management + pure functions for core logic.
"""
import asyncio
from datetime import datetime
from typing import List, Dict, Optional
import pytz
from app.core.market_calendar import is_market_open
from app.services.stock.fetcher import stock_fetcher
from app.repositories.stock_repository import stock_repository
from app.config_loader import config_loader


# ============================================================================
# Core Logic: Pure Functions (Easy to test, reusable)
# ============================================================================

async def fetch_and_save_price(ticker: str) -> bool:
    """
    Fetch price for a single ticker and save to MongoDB.
    Pure business logic - no state dependencies.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Fetch just the price (lightweight)
        price_data = await stock_fetcher.get_stock_price(ticker)
        
        if not price_data:
            print(f"Failed to fetch price for {ticker}")
            return False
        
        # Save to MongoDB
        await stock_repository.save_stock_price(price_data)
        print(f"✓ Saved price for {ticker}: ${price_data['current_price']}")
        return True
        
    except Exception as e:
        print(f"Error fetching/saving price for {ticker}: {e}")
        return False


async def fetch_and_save_prices_batch(tickers: List[str]) -> Dict[str, int]:
    """
    Fetch prices for multiple tickers concurrently.
    Pure function - orchestrates async operations.
    
    Args:
        tickers: List of ticker symbols
        
    Returns:
        Dictionary with success/failure counts
    """
    tasks = [fetch_and_save_price(ticker) for ticker in tickers]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return {
        "success": sum(1 for r in results if r is True),
        "failed": sum(1 for r in results if r is not True),
        "total": len(tickers)
    }


# ============================================================================
# Job Wrapper: Class for State and Lifecycle Management
# ============================================================================

class PriceCollectorJob:
    """
    Scheduled job to collect stock prices during market hours.
    
    This class provides:
    - State tracking (last run time, total collected)
    - Job lifecycle management
    - Status reporting for monitoring
    """
    
    def __init__(self):
        """Initialize job state."""
        self.last_run: Optional[datetime] = None
        self.run_count: int = 0
        self.total_collected: int = 0
        self.total_failed: int = 0
        self.is_running: bool = False
    
    async def run(self):
        """
        Execute the scheduled price collection job.
        Checks market status and collects prices if open.
        """
        # Prevent concurrent runs
        if self.is_running:
            print("⚠️  Price collection already in progress, skipping...")
            return
        
        self.is_running = True
        
        try:
            # Check if market is open today
            if not is_market_open():
                return  # Skip polling on market holidays
            
            # Get current time in EST
            est = pytz.timezone('US/Eastern')
            current_time = datetime.now(est)
            
            print(f"[{current_time.strftime('%Y-%m-%d %H:%M:%S EST')}] Polling stock prices...")
            
            # Get tickers from config
            tickers = await config_loader.get_tickers()
            if not tickers:
                print("No tickers configured for polling")
                return
            
            # Fetch and save prices (pure function)
            results = await fetch_and_save_prices_batch(tickers)
            
            # Update job state
            self.last_run = current_time
            self.run_count += 1
            self.total_collected += results["success"]
            self.total_failed += results["failed"]
            
            print(f"Poll complete: {results['success']} successful, {results['failed']} failed")
            
        finally:
            self.is_running = False
    
    async def run_manual(self):
        """
        Manually trigger price collection (bypasses market check).
        Useful for testing and manual data collection.
        """
        print("Manual price poll triggered...")
        
        est = pytz.timezone('US/Eastern')
        current_time = datetime.now(est)
        print(f"[{current_time.strftime('%Y-%m-%d %H:%M:%S EST')}] Manual price collection...")
        
        tickers = await config_loader.get_tickers()
        if not tickers:
            print("No tickers configured")
            return {"error": "No tickers configured"}
        
        results = await fetch_and_save_prices_batch(tickers)
        
        # Update stats
        self.total_collected += results["success"]
        self.total_failed += results["failed"]
        
        return {
            "message": "Manual poll complete",
            "results": results,
            "tickers": tickers
        }
    
    def get_stats(self) -> Dict:
        """
        Get job statistics for monitoring.
        
        Returns:
            Dictionary with job metrics
        """
        return {
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "run_count": self.run_count,
            "total_collected": self.total_collected,
            "total_failed": self.total_failed,
            "is_running": self.is_running,
            "success_rate": (
                round(self.total_collected / (self.total_collected + self.total_failed) * 100, 2)
                if (self.total_collected + self.total_failed) > 0
                else 0
            )
        }
    
    def reset_stats(self):
        """Reset job statistics (useful for testing)."""
        self.run_count = 0
        self.total_collected = 0
        self.total_failed = 0


# Singleton instance for scheduler
price_collector_job = PriceCollectorJob()

# Export both the job and the pure functions for flexibility
__all__ = ['price_collector_job', 'fetch_and_save_price', 'fetch_and_save_prices_batch']
