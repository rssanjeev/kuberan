"""
MASSIVE Ticker Discovery Job - Bulk ticker ingestion using Polygon.io.

Uses Polygon.io /v3/reference/tickers API to discover all US stocks and ETFs.
Designed for one-time bulk discovery to populate database with ~10,000 tickers.

Process:
1. Paginate through Polygon.io ticker list (1,000 tickers per call)
2. Save minimal ticker metadata to database for base collection queue
3. Respect 5 calls/minute rate limit (12 seconds between calls)

SECURITY: No sensitive data stored, only public ticker information.
"""

import asyncio
from datetime import datetime
from typing import List, Dict, Optional
import time

from app.core.logging_config import get_logger
from app.services.providers.provider_registry import provider_registry
from app.models.provider import CompanyOverview

logger = get_logger(__name__)


# ============================================================================
# Core Logic: Pure Functions (Easy to test, reusable)
# ============================================================================

async def save_ticker_placeholder(ticker_data: Dict) -> bool:
    """
    Save minimal ticker placeholder to database for base collection queue.
    
    Creates a CompanyOverview document with just ticker and basic info,
    marking it as needing base metadata collection.
    
    Args:
        ticker_data: Ticker info from Polygon.io
        
    Returns:
        True if successful, False otherwise
    """
    try:
        ticker = ticker_data.get("ticker", "").strip().upper()
        
        if not ticker:
            logger.warning("Empty ticker symbol, skipping")
            return False
        
        # Check if ticker already exists
        existing = await CompanyOverview.find_one(CompanyOverview.ticker == ticker)
        
        if existing:
            logger.debug(
                f"Ticker {ticker} already exists, skipping",
                extra={"ticker": ticker, "status": existing.enrichment_status}
            )
            return True  # Not an error, just already exists
        
        # Create minimal placeholder for base collection
        placeholder = CompanyOverview(
            ticker=ticker,
            name=ticker_data.get("name", ""),
            exchange=ticker_data.get("primary_exchange", ""),
            asset_type=_classify_asset_type(ticker_data.get("type", "")),
            currency=ticker_data.get("currency_name", "USD").upper(),
            country="US",
            source_provider="polygon",  # Use 'polygon' not 'MASSIVE' (enum validation)
            enrichment_status=None,  # Will be set to "base" by base collection
            extended_data={
                "discovered_via": "massive_bulk_discovery",
                "polygon_type": ticker_data.get("type", ""),
                "market": ticker_data.get("market", ""),
                "locale": ticker_data.get("locale", ""),
                "active": ticker_data.get("active", True),
                "cik": ticker_data.get("cik", ""),
                "composite_figi": ticker_data.get("composite_figi", ""),
                "last_updated_utc": ticker_data.get("last_updated_utc", "")
            }
        )
        
        await placeholder.insert()
        
        logger.info(
            f"Created placeholder for {ticker}",
            extra={
                "ticker": ticker,
                "name": ticker_data.get("name", ""),
                "asset_type": placeholder.asset_type
            }
        )
        
        return True
    
    except Exception as e:
        logger.error(
            f"Failed to save ticker placeholder",
            extra={"ticker": ticker_data.get("ticker"), "error": str(e)},
            exc_info=True
        )
        return False


def _classify_asset_type(polygon_type: str) -> str:
    """
    Classify Polygon.io ticker type to Kuberan asset type.
    
    Polygon types: CS (Common Stock), ETF, ADRC, etc.
    Kuberan types: Stock, ETF, Other
    
    Args:
        polygon_type: Type from Polygon.io (e.g., "CS", "ETF", "ADRC")
        
    Returns:
        Kuberan asset type (Stock, ETF, or Other)
    """
    polygon_type = polygon_type.upper()
    
    if polygon_type == "ETF":
        return "ETF"
    elif polygon_type in ["CS", "COMMON STOCK", "EQUITY"]:
        return "Stock"
    elif polygon_type in ["ADRC", "GDR", "ADR"]:
        return "Stock"  # ADRs are stocks
    else:
        return "Other"


async def fetch_ticker_batch(
    provider,
    limit: int = 1000,
    next_url: Optional[str] = None
) -> Optional[Dict]:
    """
    Fetch one batch of tickers from Polygon.io.
    
    Args:
        provider: MASSIVE provider instance
        limit: Number of tickers per batch (max 1000)
        next_url: Pagination URL from previous response
        
    Returns:
        Response dict with "results" and "next_url", or None if failed
    """
    try:
        # MASSIVE provider's fetch_all_tickers() returns parsed results
        # But we need raw response with pagination URL
        # So we'll call the underlying API directly
        
        import httpx
        
        await provider.rate_limiter.acquire(priority=0)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            if next_url:
                # Pagination URL - add API key as query param
                separator = "&" if "?" in next_url else "?"
                url_with_key = f"{next_url}{separator}apiKey={provider.api_key}"
                response = await client.get(url_with_key)
            else:
                # First request
                params = {
                    "apiKey": provider.api_key,
                    "active": "true",
                    "limit": limit,
                    "market": "stocks"
                }
                response = await client.get(
                    f"{provider.base_url}/v3/reference/tickers",
                    params=params
                )
            
            provider.rate_limiter.update_from_response(response.headers)
            
            if response.status_code == 429:
                logger.warning("Rate limit exceeded, will retry after delay")
                return None
            
            response.raise_for_status()
            data = response.json()
        
        if not data or "results" not in data:
            logger.warning("No results in response")
            return None
        
        return {
            "results": data.get("results", []),
            "next_url": data.get("next_url"),
            "count": data.get("count", 0),
            "status": data.get("status", "")
        }
    
    except Exception as e:
        logger.error(
            "Failed to fetch ticker batch",
            extra={"error": str(e), "next_url": next_url if next_url else "None"},
            exc_info=True
        )
        return None


async def discover_and_save_batch(
    provider,
    limit: int = 1000,
    next_url: Optional[str] = None
) -> Dict:
    """
    Discover one batch of tickers and save placeholders.
    
    Args:
        provider: MASSIVE provider instance
        limit: Number of tickers per batch
        next_url: Pagination URL from previous batch
        
    Returns:
        Statistics dict with results and next_url
    """
    # Fetch batch
    batch_response = await fetch_ticker_batch(provider, limit, next_url)
    
    if not batch_response:
        return {
            "success": 0,
            "failure": 0,
            "total": 0,
            "next_url": None
        }
    
    tickers = batch_response["results"]
    
    # Save placeholders concurrently
    tasks = [save_ticker_placeholder(ticker) for ticker in tickers]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Count successes
    success_count = sum(1 for r in results if r is True)
    failure_count = len(results) - success_count
    
    logger.info(
        f"Batch processing complete",
        extra={
            "batch_size": len(tickers),
            "success": success_count,
            "failure": failure_count,
            "has_next": bool(batch_response.get("next_url"))
        }
    )
    
    return {
        "success": success_count,
        "failure": failure_count,
        "total": len(tickers),
        "next_url": batch_response.get("next_url")
    }


# ============================================================================
# Job Class: State Management and Orchestration
# ============================================================================

class MassiveTickerDiscoveryJob:
    """
    Bulk ticker discovery job using MASSIVE/Polygon.io.
    
    Process:
    1. Paginate through Polygon.io ticker list (1,000 per call)
    2. Save minimal placeholders to database
    3. Respect 5 calls/minute rate limit
    
    Timeline:
    - 10,000 tickers ÷ 1,000 per call = 10 API calls
    - 5 calls/minute = 2 minutes total for discovery
    - Placeholder saves: concurrent, ~30 seconds
    - Total: ~2.5 minutes for full discovery
    """
    
    def __init__(self):
        """Initialize discovery job."""
        self.is_running = False
        self.last_run: Optional[datetime] = None
        self.total_discovered: int = 0
    
    async def run(
        self,
        limit_per_batch: int = 1000,
        max_batches: Optional[int] = None,
        test_mode: bool = False
    ) -> Dict:
        """
        Execute bulk ticker discovery.
        
        Args:
            limit_per_batch: Tickers per API call (max 1000)
            max_batches: Maximum batches to process (None = all)
            test_mode: If True, process only 1 batch for testing
            
        Returns:
            Statistics dictionary with discovery results
        """
        if self.is_running:
            logger.warning("Ticker discovery job already running")
            return {"status": "error", "message": "Job already running"}
        
        self.is_running = True
        start_time = time.time()
        
        try:
            logger.info(
                "Starting MASSIVE bulk ticker discovery",
                extra={
                    "limit_per_batch": limit_per_batch,
                    "max_batches": max_batches,
                    "test_mode": test_mode
                }
            )
            
            # Get MASSIVE provider
            provider = provider_registry.get_provider_by_name("MassiveProvider")
            
            if not provider:
                logger.error("MASSIVE provider not available")
                return {
                    "status": "error",
                    "message": "MASSIVE provider not available"
                }
            
            # Initialize statistics
            total_success = 0
            total_failure = 0
            total_tickers = 0
            batch_count = 0
            next_url = None
            
            # Test mode: process only 1 batch
            if test_mode:
                max_batches = 1
            
            # Pagination loop
            while True:
                batch_count += 1
                
                logger.info(
                    f"Processing batch {batch_count}",
                    extra={"batch_number": batch_count}
                )
                
                # Fetch and save batch
                batch_stats = await discover_and_save_batch(
                    provider=provider,
                    limit=limit_per_batch,
                    next_url=next_url
                )
                
                # Update totals
                total_success += batch_stats["success"]
                total_failure += batch_stats["failure"]
                total_tickers += batch_stats["total"]
                next_url = batch_stats["next_url"]
                
                logger.info(
                    f"Batch {batch_count} complete",
                    extra={
                        "batch_number": batch_count,
                        "batch_success": batch_stats["success"],
                        "batch_failure": batch_stats["failure"],
                        "total_so_far": total_success,
                        "has_next": bool(next_url)
                    }
                )
                
                # Check if done
                if not next_url:
                    logger.info("No more pages, discovery complete")
                    break
                
                # Check max batches limit
                if max_batches and batch_count >= max_batches:
                    logger.info(
                        f"Reached max batches limit ({max_batches})",
                        extra={"max_batches": max_batches}
                    )
                    break
                
                # Rate limit delay: 5 calls/minute = 12 seconds between calls
                logger.info("Waiting 12 seconds for rate limit...")
                await asyncio.sleep(12)
            
            # Update job state
            self.last_run = datetime.utcnow()
            self.total_discovered += total_success
            
            elapsed_time = time.time() - start_time
            
            # Get database statistics
            db_count = await CompanyOverview.count()
            base_count = await CompanyOverview.find(
                {"enrichment_status": None}
            ).count()
            
            result = {
                "status": "success",
                "batches_processed": batch_count,
                "tickers_discovered": total_tickers,
                "placeholders_created": total_success,
                "failures": total_failure,
                "elapsed_seconds": round(elapsed_time, 2),
                "database_stats": {
                    "total_tickers": db_count,
                    "needs_base_metadata": base_count
                },
                "rate_info": {
                    "tickers_per_minute": round(total_tickers / (elapsed_time / 60), 2),
                    "api_calls": batch_count,
                    "rate_limit": "5 calls/minute"
                }
            }
            
            logger.info(
                "MASSIVE bulk ticker discovery complete",
                extra=result
            )
            
            return result
        
        except Exception as e:
            logger.error(
                "MASSIVE ticker discovery failed",
                extra={"error": str(e)},
                exc_info=True
            )
            return {
                "status": "error",
                "message": str(e)
            }
        
        finally:
            self.is_running = False
    
    def get_job_status(self) -> Dict:
        """Get current job status and statistics."""
        return {
            "is_running": self.is_running,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "total_discovered": self.total_discovered
        }


# Singleton instance
massive_ticker_discovery = MassiveTickerDiscoveryJob()
