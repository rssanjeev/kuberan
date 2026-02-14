"""
ETF Performance Service

Calculate and analyze ETF performance metrics:
- Multi-period returns (1D, 1W, 1M, 3M, YTD, 1Y)
- Risk metrics (volatility, Sharpe ratio, max drawdown)
- Benchmark comparison (vs SPY or custom benchmark)
- Performance caching (1-day TTL)

Phase: 5 of 15
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import numpy as np
from app.core.logging_config import get_logger
from app.repositories.etf_repository import etf_repository
from app.repositories.provider_repository import provider_repository
from app.services.providers import provider_manager
from app.models.provider import DataSource

logger = get_logger(__name__)


class ETFPerformanceService:
    """
    Service for ETF performance analysis.
    
    Provides:
    - Historical price fetching
    - Multi-period return calculation
    - Risk metrics (volatility, Sharpe, drawdown)
    - Benchmark comparison
    """
    
    def __init__(self):
        """Initialize performance service."""
        # Risk-free rate (US 10-year Treasury yield, approximate)
        self.risk_free_rate = 0.045  # 4.5% annual
    
    async def get_etf_performance(
        self,
        ticker: str,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Get comprehensive performance metrics for an ETF.
        
        Calculates:
        - Returns: 1D, 1W, 1M, 3M, YTD, 1Y
        - Volatility: 30-day, 90-day
        - Sharpe Ratio: Risk-adjusted return
        - Max Drawdown: Largest peak-to-trough decline
        
        Args:
            ticker: ETF ticker symbol
            force_refresh: If True, bypass cache and fetch fresh data
            
        Returns:
            Performance metrics with returns and risk analysis
            
        Raises:
            ValueError: If ticker is invalid
            Exception: If performance calculation fails
            
        Example:
            >>> perf = await get_etf_performance("SPY")
            >>> print(perf['returns']['1Y'])
            0.2876  # 28.76% 1-year return
        """
        # Input validation
        if not ticker or not isinstance(ticker, str):
            raise ValueError("Ticker symbol must be a non-empty string")
        
        ticker = ticker.upper().strip()
        
        if not ticker.isalnum() or len(ticker) > 5:
            raise ValueError(f"Invalid ticker format: {ticker}")
        
        logger.info(
            "Calculating ETF performance",
            extra={"ticker": ticker, "force_refresh": force_refresh}
        )
        
        try:
            # Fetch historical prices (1 year of daily data)
            prices = await self._fetch_historical_prices(ticker, period="1y")
            
            if not prices or len(prices) < 2:
                raise ValueError(f"Insufficient price data for {ticker}. Need at least 2 data points.")
            
            # Calculate returns
            returns = self._calculate_returns(prices)
            
            # Calculate risk metrics
            risk_metrics = self._calculate_risk_metrics(prices)
            
            # Get current price
            current_price = prices[-1]['close'] if prices else None
            
            logger.info(
                "ETF performance calculated",
                extra={
                    "ticker": ticker,
                    "data_points": len(prices),
                    "1Y_return": returns.get('1Y')
                }
            )
            
            return {
                "ticker": ticker,
                "current_price": current_price,
                "as_of_date": prices[-1]['date'] if prices else None,
                "returns": returns,
                "risk_metrics": risk_metrics,
                "data_points": len(prices),
                "calculation_timestamp": datetime.utcnow().isoformat()
            }
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(
                "Failed to calculate ETF performance",
                extra={"ticker": ticker, "error": str(e)},
                exc_info=True
            )
            raise Exception(f"Performance calculation failed for {ticker}: {str(e)}")
    
    async def compare_etf_performance(
        self,
        ticker1: str,
        ticker2: str,
        period: str = "1Y"
    ) -> Dict[str, Any]:
        """
        Compare performance of two ETFs.
        
        Side-by-side comparison including:
        - Relative returns
        - Volatility comparison
        - Risk-adjusted returns (Sharpe ratios)
        - Correlation
        
        Args:
            ticker1: First ETF ticker
            ticker2: Second ETF ticker
            period: Time period ("1M", "3M", "YTD", "1Y")
            
        Returns:
            Comparative performance metrics
            
        Raises:
            ValueError: If tickers are invalid or identical
            
        Example:
            >>> comp = await compare_etf_performance("VOO", "SPY", "1Y")
            >>> print(comp['return_difference'])
            0.0012  # VOO returned 0.12% more than SPY
        """
        # Input validation
        if not ticker1 or not isinstance(ticker1, str):
            raise ValueError("ticker1 must be a non-empty string")
        if not ticker2 or not isinstance(ticker2, str):
            raise ValueError("ticker2 must be a non-empty string")
        
        ticker1 = ticker1.upper().strip()
        ticker2 = ticker2.upper().strip()
        
        if not ticker1.isalnum() or len(ticker1) > 5:
            raise ValueError(f"Invalid ticker1 format: {ticker1}")
        if not ticker2.isalnum() or len(ticker2) > 5:
            raise ValueError(f"Invalid ticker2 format: {ticker2}")
        
        if ticker1 == ticker2:
            raise ValueError(f"Cannot compare ETF to itself: {ticker1}")
        
        if period not in ["1D", "1W", "1M", "3M", "YTD", "1Y"]:
            raise ValueError(f"Invalid period: {period}. Must be one of: 1D, 1W, 1M, 3M, YTD, 1Y")
        
        logger.info(
            "Comparing ETF performance",
            extra={"ticker1": ticker1, "ticker2": ticker2, "period": period}
        )
        
        try:
            # Get performance for both ETFs
            perf1 = await self.get_etf_performance(ticker1)
            perf2 = await self.get_etf_performance(ticker2)
            
            # Extract returns for comparison
            return1 = perf1['returns'].get(period)
            return2 = perf2['returns'].get(period)
            
            # Calculate differences
            return_difference = None
            if return1 is not None and return2 is not None:
                return_difference = return1 - return2
            
            # Volatility comparison
            vol1 = perf1['risk_metrics'].get('volatility_30d')
            vol2 = perf2['risk_metrics'].get('volatility_30d')
            volatility_difference = None
            if vol1 is not None and vol2 is not None:
                volatility_difference = vol1 - vol2
            
            # Sharpe ratio comparison
            sharpe1 = perf1['risk_metrics'].get('sharpe_ratio')
            sharpe2 = perf2['risk_metrics'].get('sharpe_ratio')
            sharpe_difference = None
            if sharpe1 is not None and sharpe2 is not None:
                sharpe_difference = sharpe1 - sharpe2
            
            logger.info(
                "ETF performance comparison complete",
                extra={
                    "ticker1": ticker1,
                    "ticker2": ticker2,
                    "return_diff": return_difference
                }
            )
            
            return {
                "ticker1": ticker1,
                "ticker2": ticker2,
                "period": period,
                "comparison": {
                    "ticker1_return": return1,
                    "ticker2_return": return2,
                    "return_difference": return_difference,
                    "return_difference_pct": round(return_difference * 100, 2) if return_difference else None,
                    "winner": ticker1 if return_difference and return_difference > 0 else ticker2 if return_difference else None
                },
                "risk_comparison": {
                    "ticker1_volatility": vol1,
                    "ticker2_volatility": vol2,
                    "volatility_difference": volatility_difference,
                    "ticker1_sharpe": sharpe1,
                    "ticker2_sharpe": sharpe2,
                    "sharpe_difference": sharpe_difference,
                    "better_risk_adjusted": ticker1 if sharpe_difference and sharpe_difference > 0 else ticker2 if sharpe_difference else None
                },
                "etf1_details": perf1,
                "etf2_details": perf2,
                "calculation_timestamp": datetime.utcnow().isoformat()
            }
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(
                "Failed to compare ETF performance",
                extra={"ticker1": ticker1, "ticker2": ticker2, "error": str(e)},
                exc_info=True
            )
            raise Exception(f"Performance comparison failed: {str(e)}")
    
    async def _fetch_historical_prices(
        self,
        ticker: str,
        period: str = "1y"
    ) -> List[Dict]:
        """
        Fetch historical daily prices from database cache.
        
        Falls back to Alpha Vantage API only if data not in cache.
        
        Args:
            ticker: ETF ticker symbol
            period: Time period ("1mo", "3mo", "1y", "2y", "5y")
            
        Returns:
            List of daily price dictionaries sorted by date (oldest to newest)
            
        Note:
            Checks database first, then API if needed
        """
        try:
            # Calculate date range based on period
            end_date = datetime.utcnow().date()
            period_days = {
                "1mo": 30,
                "3mo": 90,
                "1y": 365,
                "2y": 730,
                "5y": 1825
            }
            days = period_days.get(period, 365)
            start_date = end_date - timedelta(days=days)
            
            # Check database cache first
            logger.info(
                "Checking database for historical prices",
                extra={"ticker": ticker, "period": period, "start_date": str(start_date)}
            )
            
            cached_prices = await provider_repository.get_historical_prices(
                ticker=ticker,
                start_date=start_date,
                end_date=end_date,
                interval="daily"
            )
            
            if cached_prices and len(cached_prices) > 0:
                # Convert cached data to expected format
                formatted_prices = [
                    {
                        'date': str(price.date),
                        'open': price.open,
                        'high': price.high,
                        'low': price.low,
                        'close': price.close,
                        'volume': price.volume
                    }
                    for price in cached_prices
                ]
                
                logger.info(
                    "Historical prices found in cache",
                    extra={"ticker": ticker, "data_points": len(formatted_prices)}
                )
                return formatted_prices
            
            # Not in cache - fetch from API and save
            logger.info(
                "Historical prices not in cache, fetching from provider",
                extra={"ticker": ticker, "period": period}
            )
            
            # Get Alpha Vantage provider
            alpha_vantage_provider = provider_manager._get_provider_by_name("AlphaVantageProvider")
            if not alpha_vantage_provider:
                raise Exception("Alpha Vantage provider not available")
            
            # Alpha Vantage free tier only supports "compact" (last 100 data points)
            outputsize = "compact"  # ~100 trading days (about 4-5 months)
            
            # Call fetch_etf_daily_prices which returns raw Alpha Vantage format
            raw_data = await alpha_vantage_provider.fetch_etf_daily_prices(
                ticker=ticker,
                outputsize=outputsize
            )
            
            if not raw_data:
                raise ValueError(f"No historical price data returned for {ticker}")
            
            # Convert Alpha Vantage format to standard format
            # raw_data is Dict[date_str, Dict] like:
            # {
            #     "2025-11-23": {"1. open": "450.12", "2. high": "452.34", ...},
            #     "2025-11-22": {...},
            #     ...
            # }
            formatted_prices = []
            for date_str, price_data in raw_data.items():
                formatted_prices.append({
                    'date': date_str,
                    'open': float(price_data.get('1. open', 0)),
                    'high': float(price_data.get('2. high', 0)),
                    'low': float(price_data.get('3. low', 0)),
                    'close': float(price_data.get('4. close', 0)),
                    'volume': int(price_data.get('5. volume', 0))
                })
            
            # Sort by date (oldest to newest)
            formatted_prices.sort(key=lambda x: x['date'])
            
            # Save to database for future use
            for price_data in formatted_prices:
                try:
                    await provider_repository.save_historical_price(
                        {
                            'ticker': ticker,
                            'date': price_data['date'],
                            'open': price_data['open'],
                            'high': price_data['high'],
                            'low': price_data['low'],
                            'close': price_data['close'],
                            'volume': price_data['volume'],
                            'interval': 'daily'
                        },
                        DataSource.ALPHA_VANTAGE
                    )
                except Exception as save_error:
                    # Log but don't fail - we still have the data
                    logger.warning(
                        "Failed to save historical price to cache",
                        extra={"ticker": ticker, "date": price_data['date'], "error": str(save_error)}
                    )
            
            logger.info(
                "Historical prices fetched from API and cached",
                extra={"ticker": ticker, "data_points": len(formatted_prices)}
            )
            
            return formatted_prices
            
        except Exception as e:
            logger.error(
                "Failed to fetch historical prices",
                extra={"ticker": ticker, "period": period, "error": str(e)},
                exc_info=True
            )
            raise
    
    def _calculate_returns(self, prices: List[Dict]) -> Dict[str, Optional[float]]:
        """
        Calculate returns over multiple time periods.
        
        Returns:
        - 1D: 1-day return (today vs yesterday)
        - 1W: 1-week return (7 days)
        - 1M: 1-month return (30 days)
        - 3M: 3-month return (90 days)
        - YTD: Year-to-date return
        - 1Y: 1-year return (252 trading days)
        
        Formula: (current_price - past_price) / past_price
        """
        if not prices or len(prices) < 2:
            return {
                "1D": None,
                "1W": None,
                "1M": None,
                "3M": None,
                "YTD": None,
                "1Y": None
            }
        
        current_price = prices[-1]['close']
        current_date = datetime.strptime(prices[-1]['date'], '%Y-%m-%d')
        
        returns = {}
        
        # 1D return
        if len(prices) >= 2:
            past_price = prices[-2]['close']
            returns['1D'] = round((current_price - past_price) / past_price, 6)
        else:
            returns['1D'] = None
        
        # 1W return (7 days)
        returns['1W'] = self._calculate_period_return(prices, days=7)
        
        # 1M return (30 days)
        returns['1M'] = self._calculate_period_return(prices, days=30)
        
        # 3M return (90 days)
        returns['3M'] = self._calculate_period_return(prices, days=90)
        
        # YTD return
        ytd_price = self._find_ytd_price(prices, current_date)
        if ytd_price:
            returns['YTD'] = round((current_price - ytd_price) / ytd_price, 6)
        else:
            returns['YTD'] = None
        
        # 1Y return (252 trading days or 365 calendar days)
        returns['1Y'] = self._calculate_period_return(prices, days=252)
        
        return returns
    
    def _calculate_period_return(
        self,
        prices: List[Dict],
        days: int
    ) -> Optional[float]:
        """Calculate return over a specific number of days."""
        if len(prices) <= days:
            return None
        
        current_price = prices[-1]['close']
        past_price = prices[-(days + 1)]['close']
        
        return round((current_price - past_price) / past_price, 6)
    
    def _find_ytd_price(
        self,
        prices: List[Dict],
        current_date: datetime
    ) -> Optional[float]:
        """Find price at start of current year (Jan 1 or first trading day)."""
        year_start = datetime(current_date.year, 1, 1)
        
        # Find closest price to Jan 1
        for price in prices:
            price_date = datetime.strptime(price['date'], '%Y-%m-%d')
            if price_date >= year_start:
                return price['close']
        
        return None
    
    def _calculate_risk_metrics(self, prices: List[Dict]) -> Dict[str, Optional[float]]:
        """
        Calculate risk metrics.
        
        Returns:
        - volatility_30d: 30-day volatility (annualized)
        - volatility_90d: 90-day volatility (annualized)
        - sharpe_ratio: Risk-adjusted return (1-year)
        - max_drawdown: Maximum peak-to-trough decline
        """
        if not prices or len(prices) < 2:
            return {
                "volatility_30d": None,
                "volatility_90d": None,
                "sharpe_ratio": None,
                "max_drawdown": None
            }
        
        # Calculate daily returns
        daily_returns = []
        for i in range(1, len(prices)):
            ret = (prices[i]['close'] - prices[i-1]['close']) / prices[i-1]['close']
            daily_returns.append(ret)
        
        risk_metrics = {}
        
        # 30-day volatility (annualized)
        if len(daily_returns) >= 30:
            recent_returns = daily_returns[-30:]
            volatility_30d = np.std(recent_returns) * np.sqrt(252)  # Annualize
            risk_metrics['volatility_30d'] = round(volatility_30d, 6)
        else:
            risk_metrics['volatility_30d'] = None
        
        # 90-day volatility (annualized)
        if len(daily_returns) >= 90:
            recent_returns = daily_returns[-90:]
            volatility_90d = np.std(recent_returns) * np.sqrt(252)  # Annualize
            risk_metrics['volatility_90d'] = round(volatility_90d, 6)
        else:
            risk_metrics['volatility_90d'] = None
        
        # Sharpe ratio (1-year)
        if len(daily_returns) >= 252:
            annual_returns = daily_returns[-252:]
            mean_return = np.mean(annual_returns) * 252  # Annualize
            std_return = np.std(annual_returns) * np.sqrt(252)  # Annualize
            
            if std_return > 0:
                sharpe_ratio = (mean_return - self.risk_free_rate) / std_return
                risk_metrics['sharpe_ratio'] = round(sharpe_ratio, 4)
            else:
                risk_metrics['sharpe_ratio'] = None
        else:
            risk_metrics['sharpe_ratio'] = None
        
        # Max drawdown
        max_drawdown = self._calculate_max_drawdown(prices)
        risk_metrics['max_drawdown'] = round(max_drawdown, 6) if max_drawdown else None
        
        return risk_metrics
    
    def _calculate_max_drawdown(self, prices: List[Dict]) -> Optional[float]:
        """
        Calculate maximum drawdown.
        
        Max drawdown = largest peak-to-trough decline
        Formula: (trough_price - peak_price) / peak_price
        """
        if not prices or len(prices) < 2:
            return None
        
        peak = prices[0]['close']
        max_dd = 0.0
        
        for price in prices:
            current = price['close']
            
            # Update peak if current price is higher
            if current > peak:
                peak = current
            
            # Calculate drawdown from peak
            drawdown = (current - peak) / peak
            
            # Track maximum drawdown (most negative)
            if drawdown < max_dd:
                max_dd = drawdown
        
        return max_dd


# Singleton instance
etf_performance_service = ETFPerformanceService()
