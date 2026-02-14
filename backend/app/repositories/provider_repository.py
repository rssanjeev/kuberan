"""
Repository for multi-provider data models.

Handles CRUD operations for all provider data models:
- Stock models: StockQuote, StockHistoricalPrice, StockDividend, StockSplit, StockEarnings
- Technical indicators: TechnicalIndicator
- Fundamental data: CompanyOverview
- News & analyst: NewsArticle, AnalystRating, PriceTarget
- Forex/Crypto/Commodity: ForexRate, CryptoPrice, CommodityPrice
- Economic: EconomicIndicator

Architecture: Follow existing repository patterns
- Async methods for all database operations
- Singleton instance exported
- Type hints for all methods
- Proper error handling
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from app.models.provider import (
    DataSource,
    StockQuote,
    StockHistoricalPrice,
    StockDividend,
    StockSplit,
    StockEarnings,
    TechnicalIndicator,
    CompanyOverview,
    NewsArticle,
    AnalystRating,
    PriceTarget,
    ForexRate,
    CryptoPrice,
    CommodityPrice,
    EconomicIndicator,
)
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class ProviderRepository:
    """Repository for multi-provider data persistence in MongoDB."""
    
    # ============================================================================
    # Stock Quote Operations
    # ============================================================================
    
    async def save_stock_quote(self, quote_data: Dict[str, Any], source: DataSource) -> StockQuote:
        """
        Save or update stock quote.
        
        Args:
            quote_data: Dictionary with quote data
            source: DataSource enum (YFINANCE, ALPHA_VANTAGE, FINNHUB)
            
        Returns:
            Saved StockQuote document
        """
        ticker = quote_data["ticker"]
        quote_timestamp = quote_data.get("quote_timestamp", datetime.utcnow())
        
        # Check if quote already exists for this ticker/timestamp/source
        existing = await StockQuote.find_one(
            StockQuote.ticker == ticker,
            StockQuote.quote_timestamp == quote_timestamp,
            StockQuote.source_provider == source
        )
        
        if existing:
            # Update existing quote
            for key, value in quote_data.items():
                if hasattr(existing, key) and value is not None:
                    setattr(existing, key, value)
            existing.fetched_at = datetime.utcnow()
            await existing.save()
            logger.debug("Updated stock quote", extra={"ticker": ticker, "source": source})
            return existing
        else:
            # Create new quote
            quote = StockQuote(
                ticker=ticker,
                price=quote_data["price"],
                open=quote_data.get("open"),
                high=quote_data.get("high"),
                low=quote_data.get("low"),
                previous_close=quote_data.get("previous_close"),
                volume=quote_data.get("volume"),
                change=quote_data.get("change"),
                change_percent=quote_data.get("change_percent"),
                source_provider=source,
                quote_timestamp=quote_timestamp,
                is_delayed=quote_data.get("is_delayed", False),
                delay_minutes=quote_data.get("delay_minutes"),
                market_cap=quote_data.get("market_cap"),
                pe_ratio=quote_data.get("pe_ratio"),
                dividend_yield=quote_data.get("dividend_yield"),
                fifty_two_week_high=quote_data.get("fifty_two_week_high"),
                fifty_two_week_low=quote_data.get("fifty_two_week_low"),
            )
            await quote.insert()
            logger.info("Saved new stock quote", extra={"ticker": ticker, "source": source})
            return quote
    
    async def get_latest_quote(self, ticker: str, source: Optional[DataSource] = None) -> Optional[StockQuote]:
        """
        Get latest quote for ticker (optionally filtered by source).
        
        Args:
            ticker: Stock ticker
            source: Optional DataSource filter
            
        Returns:
            Latest StockQuote or None
        """
        query = StockQuote.find(StockQuote.ticker == ticker)
        
        if source:
            query = query.find(StockQuote.source_provider == source)
        
        # Use find_one() instead of first()
        result = await query.sort(-StockQuote.quote_timestamp).limit(1).to_list()
        return result[0] if result else None
    
    async def get_quotes_in_range(
        self, 
        ticker: str, 
        start_date: datetime, 
        end_date: datetime,
        source: Optional[DataSource] = None
    ) -> List[StockQuote]:
        """Get quotes for ticker within date range."""
        query = StockQuote.find(
            StockQuote.ticker == ticker,
            StockQuote.quote_timestamp >= start_date,
            StockQuote.quote_timestamp <= end_date
        )
        
        if source:
            query = query.find(StockQuote.source_provider == source)
        
        return await query.sort(+StockQuote.quote_timestamp).to_list()
    
    # ============================================================================
    # Historical Price Operations
    # ============================================================================
    
    async def save_historical_price(self, price_data: Dict[str, Any], source: DataSource) -> StockHistoricalPrice:
        """Save or update historical price data."""
        ticker = price_data["ticker"]
        date = price_data["date"]
        interval = price_data.get("interval", "1d")
        
        # Check for existing record
        existing = await StockHistoricalPrice.find_one(
            StockHistoricalPrice.ticker == ticker,
            StockHistoricalPrice.date == date,
            StockHistoricalPrice.interval == interval,
            StockHistoricalPrice.source_provider == source
        )
        
        if existing:
            # Update existing
            for key, value in price_data.items():
                if hasattr(existing, key) and value is not None:
                    setattr(existing, key, value)
            existing.fetched_at = datetime.utcnow()
            await existing.save()
            return existing
        else:
            # Create new
            price = StockHistoricalPrice(
                ticker=ticker,
                date=date,
                timestamp=price_data.get("timestamp", datetime.utcnow()),
                open=price_data["open"],
                high=price_data["high"],
                low=price_data["low"],
                close=price_data["close"],
                volume=price_data["volume"],
                adjusted_close=price_data.get("adjusted_close"),
                source_provider=source,
                interval=interval,
            )
            await price.insert()
            logger.debug("Saved historical price", extra={"ticker": ticker, "date": date})
            return price
    
    async def get_historical_prices(
        self,
        ticker: str,
        start_date: str,
        end_date: str,
        interval: str = "1d",
        source: Optional[DataSource] = None
    ) -> List[StockHistoricalPrice]:
        """Get historical prices for ticker in date range."""
        query = StockHistoricalPrice.find(
            StockHistoricalPrice.ticker == ticker,
            StockHistoricalPrice.date >= start_date,
            StockHistoricalPrice.date <= end_date,
            StockHistoricalPrice.interval == interval
        )
        
        if source:
            query = query.find(StockHistoricalPrice.source_provider == source)
        
        return await query.sort(+StockHistoricalPrice.date).to_list()
    
    async def save_historical_prices_bulk(
        self,
        ticker: str,
        historical_data: List[Dict[str, Any]],
        source: DataSource,
        interval: str = "1d"
    ) -> int:
        """
        Bulk save historical prices from Yahoo Finance or other sources.
        
        Args:
            ticker: Stock ticker symbol
            historical_data: List of OHLCV records from yfinance
            source: Data source provider
            interval: Time interval (1d, 1wk, 1mo, etc.)
            
        Returns:
            Number of records saved
        """
        if not historical_data:
            return 0
        
        saved_count = 0
        for record in historical_data:
            try:
                # Check if record already exists
                date_str = record.get('Date') or record.get('date')
                if isinstance(date_str, datetime):
                    date_str = date_str.strftime('%Y-%m-%d')
                elif not isinstance(date_str, str):
                    continue
                
                existing = await StockHistoricalPrice.find_one(
                    StockHistoricalPrice.ticker == ticker,
                    StockHistoricalPrice.date == date_str,
                    StockHistoricalPrice.interval == interval
                )
                
                if existing:
                    continue
                
                # Create new record
                price = StockHistoricalPrice(
                    ticker=ticker,
                    date=date_str,
                    timestamp=datetime.fromisoformat(date_str) if isinstance(date_str, str) else record.get('Date'),
                    open=float(record.get('Open', 0)),
                    high=float(record.get('High', 0)),
                    low=float(record.get('Low', 0)),
                    close=float(record.get('Close', 0)),
                    volume=int(record.get('Volume', 0)),
                    adjusted_close=float(record.get('Adj Close')) if record.get('Adj Close') else None,
                    source_provider=source,
                    interval=interval,
                )
                await price.insert()
                saved_count += 1
                
            except Exception as e:
                logger.error(
                    "Failed to save historical price record",
                    extra={"ticker": ticker, "date": date_str, "error": str(e)},
                    exc_info=True
                )
                continue
        
        logger.info(
            "Bulk saved historical prices",
            extra={"ticker": ticker, "saved_count": saved_count, "total_records": len(historical_data)}
        )
        return saved_count
    
    # ============================================================================
    # Dividend Operations
    # ============================================================================
    
    async def save_dividend(self, dividend_data: Dict[str, Any], source: DataSource) -> StockDividend:
        """Save or update dividend data."""
        ticker = dividend_data["ticker"]
        ex_date = dividend_data["ex_date"]
        
        # Check for existing
        existing = await StockDividend.find_one(
            StockDividend.ticker == ticker,
            StockDividend.ex_date == ex_date
        )
        
        if existing:
            # Update
            for key, value in dividend_data.items():
                if hasattr(existing, key) and value is not None:
                    setattr(existing, key, value)
            existing.source_provider = source
            existing.fetched_at = datetime.utcnow()
            await existing.save()
            return existing
        else:
            # Create new
            dividend = StockDividend(
                ticker=ticker,
                ex_date=ex_date,
                payment_date=dividend_data.get("payment_date"),
                record_date=dividend_data.get("record_date"),
                declaration_date=dividend_data.get("declaration_date"),
                amount=dividend_data["amount"],
                currency=dividend_data.get("currency", "USD"),
                dividend_type=dividend_data.get("dividend_type"),
                frequency=dividend_data.get("frequency"),
                source_provider=source,
            )
            await dividend.insert()
            logger.info("Saved dividend", extra={"ticker": ticker, "ex_date": ex_date, "amount": dividend_data["amount"]})
            return dividend
    
    async def get_dividends(self, ticker: str, start_year: Optional[int] = None) -> List[StockDividend]:
        """Get dividend history for ticker."""
        query = StockDividend.find(StockDividend.ticker == ticker)
        
        if start_year:
            start_date = f"{start_year}-01-01"
            query = query.find(StockDividend.ex_date >= start_date)
        
        return await query.sort(-StockDividend.ex_date).to_list()
    
    # ============================================================================
    # Split Operations
    # ============================================================================
    
    async def save_split(self, split_data: Dict[str, Any], source: DataSource) -> StockSplit:
        """Save or update split data."""
        ticker = split_data["ticker"]
        split_date = split_data["split_date"]
        
        # Check for existing
        existing = await StockSplit.find_one(
            StockSplit.ticker == ticker,
            StockSplit.split_date == split_date
        )
        
        if existing:
            # Update
            for key, value in split_data.items():
                if hasattr(existing, key) and value is not None:
                    setattr(existing, key, value)
            existing.source_provider = source
            existing.fetched_at = datetime.utcnow()
            await existing.save()
            return existing
        else:
            # Create new
            split = StockSplit(
                ticker=ticker,
                split_date=split_date,
                split_ratio=split_data["split_ratio"],
                split_from=split_data.get("split_from"),
                split_to=split_data.get("split_to"),
                description=split_data["description"],
                is_reverse_split=split_data.get("is_reverse_split", False),
                source_provider=source,
            )
            await split.insert()
            logger.info("Saved split", extra={"ticker": ticker, "split_date": split_date, "ratio": split_data["split_ratio"]})
            return split
    
    async def get_splits(self, ticker: str, start_year: Optional[int] = None) -> List[StockSplit]:
        """Get split history for ticker."""
        query = StockSplit.find(StockSplit.ticker == ticker)
        
        if start_year:
            start_date = f"{start_year}-01-01"
            query = query.find(StockSplit.split_date >= start_date)
        
        return await query.sort(-StockSplit.split_date).to_list()
    
    # ============================================================================
    # Earnings Operations
    # ============================================================================
    
    async def save_earnings(self, earnings_data: Dict[str, Any], source: DataSource) -> StockEarnings:
        """Save or update earnings data."""
        ticker = earnings_data["ticker"]
        fiscal_year = earnings_data["fiscal_year"]
        fiscal_quarter = earnings_data.get("fiscal_quarter")
        
        # Check for existing
        query_conditions = [
            StockEarnings.ticker == ticker,
            StockEarnings.fiscal_year == fiscal_year
        ]
        
        if fiscal_quarter:
            query_conditions.append(StockEarnings.fiscal_quarter == fiscal_quarter)
        
        existing = await StockEarnings.find_one(*query_conditions)
        
        if existing:
            # Update
            for key, value in earnings_data.items():
                if hasattr(existing, key) and value is not None:
                    setattr(existing, key, value)
            existing.source_provider = source
            existing.fetched_at = datetime.utcnow()
            await existing.save()
            return existing
        else:
            # Create new
            earnings = StockEarnings(
                ticker=ticker,
                fiscal_year=fiscal_year,
                fiscal_quarter=fiscal_quarter,
                fiscal_period=earnings_data.get("fiscal_period"),
                report_date=earnings_data["report_date"],
                fiscal_date_ending=earnings_data.get("fiscal_date_ending"),
                reported_eps=earnings_data.get("reported_eps"),
                estimated_eps=earnings_data.get("estimated_eps"),
                surprise=earnings_data.get("surprise"),
                surprise_percent=earnings_data.get("surprise_percent"),
                reported_revenue=earnings_data.get("reported_revenue"),
                estimated_revenue=earnings_data.get("estimated_revenue"),
                net_income=earnings_data.get("net_income"),
                ebitda=earnings_data.get("ebitda"),
                source_provider=source,
            )
            await earnings.insert()
            logger.info("Saved earnings", extra={"ticker": ticker, "fiscal_year": fiscal_year, "quarter": fiscal_quarter})
            return earnings
    
    async def get_earnings(self, ticker: str, limit: int = 8) -> List[StockEarnings]:
        """Get recent earnings for ticker."""
        return await StockEarnings.find(
            StockEarnings.ticker == ticker
        ).sort(-StockEarnings.report_date).limit(limit).to_list()
    
    # ============================================================================
    # Company Overview Operations
    # ============================================================================
    
    async def save_company_overview(self, overview_data: Dict[str, Any], source: DataSource) -> CompanyOverview:
        """Save or update company overview (fundamental data)."""
        ticker = overview_data["ticker"]
        
        # Check for existing (ticker is unique)
        existing = await CompanyOverview.find_one(CompanyOverview.ticker == ticker)
        
        if existing:
            # Update existing
            for key, value in overview_data.items():
                if hasattr(existing, key) and value is not None:
                    setattr(existing, key, value)
            existing.source_provider = source
            existing.fetched_at = datetime.utcnow()
            await existing.save()
            logger.debug("Updated company overview", extra={"ticker": ticker})
            return existing
        else:
            # Create new
            overview = CompanyOverview(
                ticker=ticker,
                name=overview_data["name"],
                description=overview_data.get("description"),
                sector=overview_data.get("sector"),
                industry=overview_data.get("industry"),
                country=overview_data.get("country"),
                address=overview_data.get("address"),
                city=overview_data.get("city"),
                state=overview_data.get("state"),
                zip_code=overview_data.get("zip_code"),
                website=overview_data.get("website"),
                phone=overview_data.get("phone"),
                exchange=overview_data.get("exchange"),
                currency=overview_data.get("currency", "USD"),
                market_cap=overview_data.get("market_cap"),
                pe_ratio=overview_data.get("pe_ratio"),
                peg_ratio=overview_data.get("peg_ratio"),
                book_value=overview_data.get("book_value"),
                dividend_yield=overview_data.get("dividend_yield"),
                eps=overview_data.get("eps"),
                revenue_ttm=overview_data.get("revenue_ttm"),
                profit_margin=overview_data.get("profit_margin"),
                beta=overview_data.get("beta"),
                shares_outstanding=overview_data.get("shares_outstanding"),
                fiscal_year_end=overview_data.get("fiscal_year_end"),
                extended_data=overview_data.get("extended_data", {}),
                source_provider=source,
            )
            await overview.insert()
            logger.info("Saved company overview", extra={"ticker": ticker, "name": overview_data["name"]})
            return overview
    
    async def get_company_overview(self, ticker: str) -> Optional[CompanyOverview]:
        """Get company overview for ticker."""
        return await CompanyOverview.find_one(CompanyOverview.ticker == ticker)
    
    # ============================================================================
    # News Operations
    # ============================================================================
    
    async def save_news_article(self, news_data: Dict[str, Any], source: DataSource) -> NewsArticle:
        """Save news article (URL is unique)."""
        url = news_data["url"]
        
        # Check if article already exists
        existing = await NewsArticle.find_one(NewsArticle.url == url)
        
        if existing:
            # Update existing article
            for key, value in news_data.items():
                if hasattr(existing, key) and value is not None:
                    setattr(existing, key, value)
            existing.source_provider = source
            existing.fetched_at = datetime.utcnow()
            await existing.save()
            logger.debug("Updated news article", extra={"url": url})
            return existing
        else:
            # Create new article
            article = NewsArticle(
                url=url,
                title=news_data["title"],
                summary=news_data.get("summary"),
                content=news_data.get("content"),
                tickers=news_data.get("tickers", []),
                published_at=news_data["published_at"],
                source_name=news_data.get("source_name"),
                source_domain=news_data.get("source_domain"),
                author=news_data.get("author"),
                sentiment_label=news_data.get("sentiment_label"),
                sentiment_score=news_data.get("sentiment_score"),
                topics=news_data.get("topics", []),
                source_provider=source,
            )
            await article.insert()
            logger.info("Saved news article", extra={"url": url, "tickers": news_data.get("tickers", [])})
            return article
    
    async def get_news_for_ticker(self, ticker: str, limit: int = 20) -> List[NewsArticle]:
        """Get recent news articles mentioning ticker."""
        return await NewsArticle.find(
            NewsArticle.tickers == ticker  # Array contains
        ).sort(-NewsArticle.published_at).limit(limit).to_list()
    
    async def get_recent_news(self, hours: int = 24, limit: int = 50) -> List[NewsArticle]:
        """Get recent news articles across all tickers."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return await NewsArticle.find(
            NewsArticle.published_at >= cutoff_time
        ).sort(-NewsArticle.published_at).limit(limit).to_list()


# Singleton instance
provider_repository = ProviderRepository()
