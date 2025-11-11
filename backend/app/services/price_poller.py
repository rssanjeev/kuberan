"""
Background service to poll stock prices during market hours.
Fetches prices for configured tickers every 60 seconds from 9 AM to 5 PM EST.
Respects NYSE market holidays and trading calendar.
"""
import asyncio
from datetime import datetime, date
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
import pandas_market_calendars as mcal
from app.config_loader import config_loader
from app.services.stock_service import stock_service
from app.repositories.stock_repository import stock_repository


class PricePollerService:
    """Service to poll stock prices during market hours."""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone=pytz.timezone('US/Eastern'))
        self.is_running = False
        self.nyse_calendar = mcal.get_calendar('NYSE')
        
    def is_market_open_today(self) -> bool:
        """
        Check if the NYSE is open today.
        
        Returns:
            True if market is open, False if closed (holiday/weekend)
        """
        try:
            est = pytz.timezone('US/Eastern')
            today = datetime.now(est).date()
            
            # Get NYSE schedule for today
            schedule = self.nyse_calendar.schedule(start_date=today, end_date=today)
            
            # If schedule is empty, market is closed
            is_open = len(schedule) > 0
            
            if not is_open:
                print(f"[{today}] NYSE is closed today (holiday or weekend)")
            
            return is_open
            
        except Exception as e:
            print(f"Error checking market calendar: {e}")
            # Default to allowing polling if calendar check fails
            return True
        
    async def poll_prices(self):
        """
        Poll prices for all configured tickers and save to MongoDB.
        This runs every 60 seconds during market hours.
        Skips polling if NYSE is closed (holidays/weekends).
        """
        try:
            # Check if market is open today
            if not self.is_market_open_today():
                return  # Skip polling on market holidays
            
            # Get current time in EST
            est = pytz.timezone('US/Eastern')
            current_time = datetime.now(est)
            
            print(f"[{current_time.strftime('%Y-%m-%d %H:%M:%S EST')}] Polling stock prices...")
            
            # Get tickers from config (now async)
            tickers = await config_loader.get_tickers()
            if not tickers:
                print("No tickers configured for polling")
                return
            
            # Fetch prices for all tickers concurrently
            tasks = []
            for ticker in tickers:
                tasks.append(self._fetch_and_save_price(ticker))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Count successes and failures
            successes = sum(1 for r in results if r is True)
            failures = sum(1 for r in results if r is not True)
            
            print(f"Poll complete: {successes} successful, {failures} failed")
            
        except Exception as e:
            print(f"Error during price polling: {e}")
    
    async def _fetch_and_save_price(self, ticker: str) -> bool:
        """
        Fetch price for a single ticker and save to MongoDB.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Fetch just the price (lightweight)
            price_data = await stock_service.get_stock_price(ticker)
            
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
    
    def start(self):
        """
        Start the price polling scheduler.
        Polls every 60 seconds from 9 AM to 5 PM EST, Monday-Friday.
        """
        if self.is_running:
            print("Price poller is already running")
            return
        
        # Schedule polling every 60 seconds during market hours
        # Monday-Friday, 9:00 AM - 5:00 PM EST
        self.scheduler.add_job(
            self.poll_prices,
            trigger=CronTrigger(
                day_of_week='mon-fri',  # Monday to Friday
                hour='9-16',            # 9 AM to 4:59 PM
                minute='*',             # Every minute
                second='0',             # At the start of each minute
                timezone='US/Eastern'
            ),
            id='stock_price_poller',
            name='Stock Price Polling',
            replace_existing=True
        )
        
        # Also add a job for 5:00 PM (market close)
        self.scheduler.add_job(
            self.poll_prices,
            trigger=CronTrigger(
                day_of_week='mon-fri',
                hour='17',
                minute='0',
                second='0',
                timezone='US/Eastern'
            ),
            id='market_close_poll',
            name='Market Close Polling',
            replace_existing=True
        )
        
        self.scheduler.start()
        self.is_running = True
        
        est = pytz.timezone('US/Eastern')
        current_time = datetime.now(est)
        print(f"✓ Price poller started at {current_time.strftime('%Y-%m-%d %H:%M:%S EST')}")
        print("  Polling every 60 seconds during market hours (9 AM - 5 PM EST, Mon-Fri)")
        print("  Monitoring tickers will be loaded from MongoDB")
        print("  NYSE market holiday calendar integrated - polling skipped on holidays")
    
    def stop(self):
        """Stop the price polling scheduler."""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            print("✓ Price poller stopped")
    
    async def run_now(self):
        """
        Manually trigger a price poll (for testing).
        Can be called anytime, regardless of market hours.
        """
        print("Manual price poll triggered...")
        await self.poll_prices()


# Singleton instance
price_poller = PricePollerService()
