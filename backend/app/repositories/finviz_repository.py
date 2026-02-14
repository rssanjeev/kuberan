"""
Repository for FinViz snapshot data.

Handles CRUD operations for FinViz scraped data:
- Save/update snapshots from quote page extraction
- Query snapshots by ticker, sector, industry
- Get latest snapshot for standardization pipeline
- Bulk operations for batch updates

Architecture:
- Async methods for all database operations
- Singleton instance exported
- Type hints for all methods
- Structured logging with context
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from app.models.cartographer import FinvizSnapshot
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class FinvizRepository:
    """Repository for FinViz snapshot persistence in MongoDB."""
    
    # ============================================================================
    # Save/Update Operations
    # ============================================================================
    
    async def save_snapshot(
        self,
        ticker: str,
        entity_type: str,
        fields: Dict[str, Any],
        display_name: Optional[str] = None,
        sector: Optional[str] = None,
        industry: Optional[str] = None,
        country: Optional[str] = None,
        exchange: Optional[str] = None,
        peers: Optional[List[str]] = None,
        held_by_etfs: Optional[List[str]] = None,
        page_url: Optional[str] = None,
        paywalled_fields: Optional[List[str]] = None,
        errors: Optional[List[str]] = None,
    ) -> FinvizSnapshot:
        """
        Save or update FinViz snapshot for a ticker.
        
        Uses upsert logic: updates if snapshot exists for same ticker+date,
        otherwise creates new document.
        
        Args:
            ticker: Stock/ETF ticker symbol
            entity_type: "stock" or "etf"
            fields: Extracted fields from snapshot table
            display_name: Company/fund name
            sector: Business sector
            industry: Industry classification
            country: Country code
            exchange: Exchange (NASDAQ, NYSE, etc.)
            peers: List of peer ticker symbols
            held_by_etfs: List of ETFs holding this stock
            page_url: Source URL
            paywalled_fields: Fields behind Elite paywall
            errors: Any extraction errors
            
        Returns:
            Saved FinvizSnapshot document
        """
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Check for existing snapshot from today
        existing = await FinvizSnapshot.find_one(
            FinvizSnapshot.ticker == ticker.upper(),
            FinvizSnapshot.as_of >= today
        )
        
        if existing:
            # Update existing snapshot
            existing.fields = fields
            existing.display_name = display_name or existing.display_name
            existing.sector = sector or existing.sector
            existing.industry = industry or existing.industry
            existing.country = country or existing.country
            existing.exchange = exchange or existing.exchange
            existing.peers = peers or existing.peers
            existing.held_by_etfs = held_by_etfs or existing.held_by_etfs
            existing.page_url = page_url or existing.page_url
            existing.paywalled_fields = paywalled_fields or existing.paywalled_fields
            existing.errors = errors or existing.errors
            existing.as_of = datetime.utcnow()
            
            await existing.save()
            logger.info(
                "Updated FinViz snapshot",
                extra={"ticker": ticker, "field_count": len(fields)}
            )
            return existing
        else:
            # Create new snapshot
            snapshot = FinvizSnapshot(
                ticker=ticker.upper(),
                entity_type=entity_type,
                display_name=display_name,
                sector=sector,
                industry=industry,
                country=country,
                exchange=exchange,
                fields=fields,
                peers=peers or [],
                held_by_etfs=held_by_etfs or [],
                page_url=page_url,
                paywalled_fields=paywalled_fields or [],
                errors=errors or [],
            )
            await snapshot.insert()
            logger.info(
                "Saved new FinViz snapshot",
                extra={"ticker": ticker, "entity_type": entity_type, "field_count": len(fields)}
            )
            return snapshot
    
    async def save_from_parsed_json(
        self,
        parsed_data: Dict[str, Any]
    ) -> FinvizSnapshot:
        """
        Save snapshot from parsed FinViz JSON output.
        
        This is the primary method for saving data from the extraction pipeline.
        
        Args:
            parsed_data: Output from finviz_parser.parse_finviz_files()
            
        Returns:
            Saved FinvizSnapshot document
        """
        ticker = parsed_data.get("ticker", "UNKNOWN")
        
        # Flatten all field categories into single dict
        fields = {}
        
        # Add snapshot table fields
        if "snapshot" in parsed_data:
            fields.update(parsed_data["snapshot"])
        
        # Add financial statement summaries (key metrics only)
        for statement_type in ["income_statement", "balance_sheet", "cash_flow"]:
            if statement_type in parsed_data and parsed_data[statement_type]:
                statement_data = parsed_data[statement_type]
                # Store TTM or most recent period
                if "TTM" in statement_data:
                    fields[f"{statement_type}_ttm"] = statement_data["TTM"]
                elif statement_data:
                    # Get first available period
                    first_key = next(iter(statement_data))
                    fields[f"{statement_type}_latest"] = statement_data[first_key]
        
        # Extract metadata
        metadata = parsed_data.get("metadata", {})
        
        return await self.save_snapshot(
            ticker=ticker,
            entity_type="stock",  # Default; could be derived from data
            fields=fields,
            paywalled_fields=["paywall_detected"] if metadata.get("paywall_detected") else [],
        )
    
    # ============================================================================
    # Query Operations
    # ============================================================================
    
    async def get_latest_snapshot(
        self,
        ticker: str
    ) -> Optional[FinvizSnapshot]:
        """
        Get the most recent snapshot for a ticker.
        
        Args:
            ticker: Stock/ETF ticker symbol
            
        Returns:
            Latest FinvizSnapshot or None if not found
        """
        snapshot = await FinvizSnapshot.find_one(
            FinvizSnapshot.ticker == ticker.upper(),
            sort=[("as_of", -1)]
        )
        
        if snapshot:
            logger.debug(
                "Found FinViz snapshot",
                extra={"ticker": ticker, "as_of": str(snapshot.as_of)}
            )
        else:
            logger.debug("No FinViz snapshot found", extra={"ticker": ticker})
            
        return snapshot
    
    async def get_snapshot_by_date(
        self,
        ticker: str,
        date: datetime
    ) -> Optional[FinvizSnapshot]:
        """
        Get snapshot for a specific date.
        
        Args:
            ticker: Stock/ETF ticker symbol
            date: Target date
            
        Returns:
            FinvizSnapshot for that date or None
        """
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        return await FinvizSnapshot.find_one(
            FinvizSnapshot.ticker == ticker.upper(),
            FinvizSnapshot.as_of >= start_of_day,
            FinvizSnapshot.as_of < end_of_day
        )
    
    async def get_snapshots_by_sector(
        self,
        sector: str,
        limit: int = 100
    ) -> List[FinvizSnapshot]:
        """
        Get latest snapshots for all tickers in a sector.
        
        Args:
            sector: Sector name (e.g., "Technology", "Healthcare")
            limit: Maximum number of results
            
        Returns:
            List of FinvizSnapshots
        """
        # Get distinct tickers in sector, then fetch latest for each
        snapshots = await FinvizSnapshot.find(
            FinvizSnapshot.sector == sector
        ).sort([("as_of", -1)]).limit(limit * 2).to_list()
        
        # Dedupe to get latest per ticker
        seen_tickers = set()
        unique_snapshots = []
        for snapshot in snapshots:
            if snapshot.ticker not in seen_tickers:
                seen_tickers.add(snapshot.ticker)
                unique_snapshots.append(snapshot)
                if len(unique_snapshots) >= limit:
                    break
        
        logger.info(
            "Fetched sector snapshots",
            extra={"sector": sector, "count": len(unique_snapshots)}
        )
        return unique_snapshots
    
    async def get_snapshots_by_industry(
        self,
        industry: str,
        limit: int = 100
    ) -> List[FinvizSnapshot]:
        """
        Get latest snapshots for all tickers in an industry.
        
        Args:
            industry: Industry name
            limit: Maximum number of results
            
        Returns:
            List of FinvizSnapshots
        """
        snapshots = await FinvizSnapshot.find(
            FinvizSnapshot.industry == industry
        ).sort([("as_of", -1)]).limit(limit * 2).to_list()
        
        # Dedupe to get latest per ticker
        seen_tickers = set()
        unique_snapshots = []
        for snapshot in snapshots:
            if snapshot.ticker not in seen_tickers:
                seen_tickers.add(snapshot.ticker)
                unique_snapshots.append(snapshot)
                if len(unique_snapshots) >= limit:
                    break
        
        return unique_snapshots
    
    async def get_all_tickers(self) -> List[str]:
        """
        Get list of all tickers with FinViz snapshots.
        
        Returns:
            List of ticker symbols
        """
        snapshots = await FinvizSnapshot.find_all().to_list()
        tickers = list(set(s.ticker for s in snapshots))
        tickers.sort()
        return tickers
    
    async def get_stale_snapshots(
        self,
        days_old: int = 7
    ) -> List[FinvizSnapshot]:
        """
        Get snapshots that haven't been updated recently.
        
        Args:
            days_old: Consider stale if older than this many days
            
        Returns:
            List of stale FinvizSnapshots
        """
        cutoff = datetime.utcnow() - timedelta(days=days_old)
        
        snapshots = await FinvizSnapshot.find(
            FinvizSnapshot.as_of < cutoff
        ).to_list()
        
        logger.info(
            "Found stale snapshots",
            extra={"count": len(snapshots), "days_threshold": days_old}
        )
        return snapshots
    
    # ============================================================================
    # Field Access Helpers
    # ============================================================================
    
    async def get_field_value(
        self,
        ticker: str,
        field_name: str
    ) -> Optional[Any]:
        """
        Get a specific field value from the latest snapshot.
        
        Args:
            ticker: Stock/ETF ticker symbol
            field_name: Name of the field to retrieve
            
        Returns:
            Field value or None if not found
        """
        snapshot = await self.get_latest_snapshot(ticker)
        if not snapshot:
            return None
        
        return snapshot.fields.get(field_name)
    
    async def get_multiple_fields(
        self,
        ticker: str,
        field_names: List[str]
    ) -> Dict[str, Any]:
        """
        Get multiple field values from the latest snapshot.
        
        Args:
            ticker: Stock/ETF ticker symbol
            field_names: List of field names to retrieve
            
        Returns:
            Dictionary of field_name -> value (missing fields not included)
        """
        snapshot = await self.get_latest_snapshot(ticker)
        if not snapshot:
            return {}
        
        return {
            name: snapshot.fields.get(name)
            for name in field_names
            if name in snapshot.fields
        }
    
    # ============================================================================
    # Statistics & Maintenance
    # ============================================================================
    
    async def get_snapshot_count(self) -> int:
        """Get total number of snapshots in database."""
        return await FinvizSnapshot.count()
    
    async def get_unique_ticker_count(self) -> int:
        """Get count of unique tickers with snapshots."""
        tickers = await self.get_all_tickers()
        return len(tickers)
    
    async def get_sector_distribution(self) -> Dict[str, int]:
        """Get count of snapshots per sector."""
        snapshots = await FinvizSnapshot.find_all().to_list()
        
        distribution = {}
        for snapshot in snapshots:
            sector = snapshot.sector or "Unknown"
            distribution[sector] = distribution.get(sector, 0) + 1
        
        return distribution
    
    async def delete_old_snapshots(
        self,
        days_to_keep: int = 30
    ) -> int:
        """
        Delete snapshots older than specified days.
        
        Args:
            days_to_keep: Keep snapshots newer than this
            
        Returns:
            Number of deleted snapshots
        """
        cutoff = datetime.utcnow() - timedelta(days=days_to_keep)
        
        result = await FinvizSnapshot.find(
            FinvizSnapshot.as_of < cutoff
        ).delete()
        
        deleted_count = result.deleted_count if result else 0
        logger.info(
            "Deleted old FinViz snapshots",
            extra={"deleted": deleted_count, "days_threshold": days_to_keep}
        )
        return deleted_count


# Singleton instance
finviz_repository = FinvizRepository()
