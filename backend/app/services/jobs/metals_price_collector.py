"""
Precious metals price collector job - Daily fetching of gold and silver prices.
Runs once per day including weekends (no market calendar check needed).
"""
from datetime import datetime
from typing import Optional
import pytz
from app.services.precious_metals.metals_price_service import metals_price_service
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class MetalsPriceCollectorJob:
    """
    Scheduled job to collect precious metals prices daily.
    
    Unlike stock prices, gold/silver prices are available 24/7,
    so this runs every day including weekends.
    """
    
    def __init__(self):
        """Initialize job state."""
        self.earliest_run: Optional[datetime] = None
        self.latest_run: Optional[datetime] = None
        self.run_count: int = 0
        self.successful_runs: int = 0
        self.failed_runs: int = 0
        self.is_running: bool = False
    
    async def run(self):
        """
        Execute the scheduled price collection.
        Fetches gold and silver prices from goodreturns.in via Brave Search.
        """
        # Prevent concurrent runs
        if self.is_running:
            logger.warning("Metals price collection already in progress")
            return
        
        self.is_running = True
        
        try:
            # Get current time in IST
            ist = pytz.timezone('Asia/Kolkata')
            current_time = datetime.now(ist)
            
            logger.info(
                "Starting precious metals price collection",
                extra={"timestamp": current_time.strftime('%Y-%m-%d %H:%M:%S IST')}
            )
            
            # Fetch and save all prices
            result = await metals_price_service.fetch_and_save_all_prices()
            
            # Update job state
            if self.earliest_run is None:
                self.earliest_run = current_time
            self.latest_run = current_time
            self.run_count += 1
            
            if result["overall_status"] == "success":
                self.successful_runs += 1
                logger.info(
                    "Metals price collection completed successfully",
                    extra={
                        "gold_status": result["gold"]["status"],
                        "silver_status": result["silver"]["status"]
                    }
                )
            else:
                self.failed_runs += 1
                logger.error(
                    "Metals price collection failed or partial",
                    extra={
                        "gold_status": result["gold"]["status"],
                        "silver_status": result["silver"]["status"],
                        "overall_status": result["overall_status"]
                    }
                )
            
        except Exception as e:
            self.failed_runs += 1
            logger.error(
                "Unexpected error in metals price collection",
                extra={"error": str(e)},
                exc_info=True
            )
        finally:
            self.is_running = False
    
    async def run_manual(self):
        """
        Manually trigger price collection.
        Useful for testing and immediate updates.
        """
        logger.info("Manual metals price collection triggered")
        
        # Get current time in IST
        ist = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(ist)
        
        result = await metals_price_service.fetch_and_save_all_prices()
        
        # Update stats
        if self.earliest_run is None:
            self.earliest_run = current_time
        self.latest_run = current_time
        self.run_count += 1
        if result["overall_status"] == "success":
            self.successful_runs += 1
        else:
            self.failed_runs += 1
        
        logger.info(
            "Manual collection complete",
            extra={"result": result}
        )
        
        return result
    
    def get_stats(self) -> dict:
        """
        Get job statistics for monitoring.
        
        Returns:
            Dictionary with job metrics including earliest and latest run times
        """
        return {
            "earliest_run": self.earliest_run.isoformat() if self.earliest_run else None,
            "latest_run": self.latest_run.isoformat() if self.latest_run else None,
            "run_count": self.run_count,
            "successful_runs": self.successful_runs,
            "failed_runs": self.failed_runs,
            "is_running": self.is_running,
            "success_rate": (
                round(self.successful_runs / self.run_count * 100, 2)
                if self.run_count > 0
                else 0
            )
        }
    
    def reset_stats(self):
        """Reset job statistics."""
        self.earliest_run = None
        self.latest_run = None
        self.run_count = 0
        self.successful_runs = 0
        self.failed_runs = 0


# Singleton instance
metals_price_collector_job = MetalsPriceCollectorJob()
