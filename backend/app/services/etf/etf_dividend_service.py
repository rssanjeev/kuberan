"""
ETF Dividend Service

Track and analyze dividend income from ETFs:
- Dividend history and trends
- Yield analysis (current, trailing, forward)
- Dividend growth rates (1Y, 3Y, 5Y)
- Payment schedules and ex-dividend dates
- Portfolio income projections

Phase: 8 of 15
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from calendar import month_name
import numpy as np
from app.core.logging_config import get_logger
from app.repositories.etf_repository import etf_repository
from app.repositories.provider_repository import provider_repository
from app.services.etf.etf_profile_service import etf_profile_service
from app.services.providers import provider_manager
from app.models.provider import DataSource

logger = get_logger(__name__)


class ETFDividendService:
    """
    Service for ETF dividend analysis and income tracking.
    
    Provides:
    - Dividend history fetching (with caching)
    - Yield calculations (current, TTM, forward)
    - Dividend growth analysis
    - Payment calendar generation
    - Portfolio income projections
    """
    
    def __init__(self):
        """Initialize dividend service."""
        pass
    
    async def get_etf_dividend_history(
        self,
        ticker: str,
        years: int = 5,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Get dividend payment history for an ETF.
        
        Returns:
        - Payment history (date, amount, type)
        - Current dividend yield
        - Payment frequency (monthly, quarterly, annual)
        - Dividend growth rate
        - Payout consistency score
        
        Args:
            ticker: ETF ticker symbol
            years: Number of years of history (default: 5)
            force_refresh: If True, bypass cache and fetch fresh data
            
        Returns:
            Dividend history with analysis
            
        Example:
            >>> hist = await get_etf_dividend_history("SCHD")
            >>> print(hist['current_yield'])
            0.0382  # 3.82% yield
            >>> print(hist['payment_frequency'])
            "Quarterly"
        """
        # Input validation
        if not ticker or not isinstance(ticker, str):
            raise ValueError("Ticker symbol must be a non-empty string")
        
        ticker = ticker.upper().strip()
        
        if not ticker.isalnum() or len(ticker) > 5:
            raise ValueError(f"Invalid ticker format: {ticker}")
        
        if years < 1 or years > 20:
            raise ValueError(f"Years must be between 1 and 20, got {years}")
        
        logger.info(
            "Fetching dividend history",
            extra={"ticker": ticker, "years": years, "force_refresh": force_refresh}
        )
        
        try:
            # Get ETF profile for current yield
            profile = await etf_profile_service.get_etf_profile(ticker, force_refresh=force_refresh)
            current_yield = profile.get('fundamentals', {}).get('dividend_yield')
            current_price = profile.get('fundamentals', {}).get('nav')
            
            # Fetch dividend history from cache or API
            dividends = await self._fetch_dividend_history(ticker, years, force_refresh)
            
            if not dividends:
                logger.warning(
                    "No dividend history found",
                    extra={"ticker": ticker}
                )
                return {
                    "ticker": ticker,
                    "current_yield": current_yield,
                    "current_price": current_price,
                    "dividend_count": 0,
                    "dividends": [],
                    "analysis": {
                        "payment_frequency": "Unknown",
                        "annual_dividend": None,
                        "dividend_growth_1y": None,
                        "dividend_growth_3y": None,
                        "payout_consistency": None
                    },
                    "note": "No dividend data available. ETF may not pay dividends or data not yet fetched.",
                    "calculation_timestamp": datetime.utcnow().isoformat()
                }
            
            # Analyze dividend payments
            analysis = self._analyze_dividend_history(dividends, current_price)
            
            logger.info(
                "Dividend history fetched",
                extra={
                    "ticker": ticker,
                    "dividend_count": len(dividends),
                    "annual_dividend": analysis.get('annual_dividend')
                }
            )
            
            return {
                "ticker": ticker,
                "current_yield": current_yield,
                "current_price": current_price,
                "dividend_count": len(dividends),
                "dividends": dividends[:20],  # Limit to 20 most recent
                "analysis": analysis,
                "calculation_timestamp": datetime.utcnow().isoformat()
            }
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(
                "Failed to get dividend history",
                extra={"ticker": ticker, "error": str(e)},
                exc_info=True
            )
            raise Exception(f"Dividend history fetch failed for {ticker}: {str(e)}")
    
    async def analyze_dividend_growth(
        self,
        ticker: str,
        periods: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Analyze dividend growth over multiple time periods.
        
        Calculates compound annual growth rate (CAGR) for dividends.
        
        Args:
            ticker: ETF ticker symbol
            periods: List of years to analyze (default: [1, 3, 5, 10])
            
        Returns:
            Dividend growth analysis with CAGR for each period
            
        Example:
            >>> growth = await analyze_dividend_growth("VYM")
            >>> print(growth['growth_rates']['3Y'])
            0.0687  # 6.87% CAGR over 3 years
        """
        if periods is None:
            periods = [1, 3, 5, 10]
        
        ticker = ticker.upper().strip()
        
        logger.info(
            "Analyzing dividend growth",
            extra={"ticker": ticker, "periods": periods}
        )
        
        try:
            # Get dividend history
            hist = await self.get_etf_dividend_history(ticker, years=max(periods) + 1)
            
            if not hist['dividends'] or len(hist['dividends']) < 4:
                return {
                    "ticker": ticker,
                    "growth_rates": {f"{p}Y": None for p in periods},
                    "note": "Insufficient dividend history for growth analysis",
                    "calculation_timestamp": datetime.utcnow().isoformat()
                }
            
            dividends = hist['dividends']
            
            # Calculate growth rates
            growth_rates = {}
            for period in periods:
                cagr = self._calculate_dividend_cagr(dividends, period)
                growth_rates[f"{period}Y"] = round(cagr, 6) if cagr is not None else None
            
            # Calculate dividend increases/decreases
            increases = 0
            decreases = 0
            unchanged = 0
            
            for i in range(1, len(dividends)):
                if dividends[i]['amount'] > dividends[i-1]['amount']:
                    increases += 1
                elif dividends[i]['amount'] < dividends[i-1]['amount']:
                    decreases += 1
                else:
                    unchanged += 1
            
            consistency_score = (increases / len(dividends)) * 100 if dividends else 0
            
            logger.info(
                "Dividend growth analysis complete",
                extra={"ticker": ticker, "growth_1Y": growth_rates.get('1Y')}
            )
            
            return {
                "ticker": ticker,
                "growth_rates": growth_rates,
                "payment_history": {
                    "total_payments": len(dividends),
                    "increases": increases,
                    "decreases": decreases,
                    "unchanged": unchanged,
                    "consistency_score": round(consistency_score, 2)
                },
                "current_annual_dividend": hist['analysis'].get('annual_dividend'),
                "interpretation": self._interpret_dividend_growth(growth_rates),
                "calculation_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(
                "Failed to analyze dividend growth",
                extra={"ticker": ticker, "error": str(e)},
                exc_info=True
            )
            raise
    
    async def compare_dividend_yields(
        self,
        tickers: List[str]
    ) -> Dict[str, Any]:
        """
        Compare dividend yields across multiple ETFs.
        
        Useful for building income-focused portfolios.
        
        Args:
            tickers: List of ETF ticker symbols (max 10)
            
        Returns:
            Yield comparison with rankings
            
        Example:
            >>> comp = await compare_dividend_yields(["VYM", "SCHD", "DGRO"])
            >>> print(comp['ranked_by_yield'][0])
            {"ticker": "SCHD", "yield": 0.0382, "rank": 1}
        """
        if not tickers or len(tickers) == 0:
            raise ValueError("Must provide at least one ticker")
        
        if len(tickers) > 10:
            raise ValueError("Maximum 10 tickers allowed")
        
        tickers = [t.upper().strip() for t in tickers]
        
        logger.info(
            "Comparing dividend yields",
            extra={"ticker_count": len(tickers)}
        )
        
        try:
            # Fetch dividend data for all ETFs
            etf_data = []
            for ticker in tickers:
                try:
                    hist = await self.get_etf_dividend_history(ticker, years=1)
                    etf_data.append({
                        "ticker": ticker,
                        "current_yield": hist.get('current_yield'),
                        "annual_dividend": hist['analysis'].get('annual_dividend'),
                        "payment_frequency": hist['analysis'].get('payment_frequency'),
                        "dividend_growth_1y": hist['analysis'].get('dividend_growth_1y'),
                        "payout_consistency": hist['analysis'].get('payout_consistency')
                    })
                except Exception as e:
                    logger.warning(
                        "Failed to fetch dividend data",
                        extra={"ticker": ticker, "error": str(e)}
                    )
                    etf_data.append({
                        "ticker": ticker,
                        "current_yield": None,
                        "annual_dividend": None,
                        "payment_frequency": "Unknown",
                        "dividend_growth_1y": None,
                        "payout_consistency": None,
                        "error": str(e)
                    })
            
            # Rank by yield
            valid_etfs = [e for e in etf_data if e['current_yield'] is not None]
            ranked_by_yield = sorted(
                valid_etfs,
                key=lambda x: x['current_yield'],
                reverse=True
            )
            
            for i, etf in enumerate(ranked_by_yield, start=1):
                etf['yield_rank'] = i
            
            # Find highest yield
            highest_yield = ranked_by_yield[0] if ranked_by_yield else None
            
            # Calculate average yield
            avg_yield = np.mean([e['current_yield'] for e in valid_etfs]) if valid_etfs else None
            
            logger.info(
                "Dividend yield comparison complete",
                extra={
                    "etf_count": len(etf_data),
                    "avg_yield": avg_yield
                }
            )
            
            return {
                "tickers": tickers,
                "etf_count": len(etf_data),
                "comparison": etf_data,
                "ranked_by_yield": ranked_by_yield,
                "highest_yield": highest_yield,
                "average_yield": round(avg_yield, 6) if avg_yield else None,
                "calculation_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(
                "Failed to compare dividend yields",
                extra={"error": str(e)},
                exc_info=True
            )
            raise
    
    async def calculate_portfolio_income(
        self,
        holdings: str,
        investment_amount: float = 100000.0
    ) -> Dict[str, Any]:
        """
        Calculate projected income from a dividend portfolio.
        
        Args:
            holdings: Comma-separated holdings with weights (e.g., "VYM:40,SCHD:30,DGRO:30")
            investment_amount: Total portfolio value (default: $100,000)
            
        Returns:
            Income projection with monthly/quarterly/annual breakdown
            
        Example:
            >>> income = await calculate_portfolio_income("VYM:50,SCHD:50", 100000)
            >>> print(income['annual_income'])
            3420.50  # $3,420.50 per year
        """
        # Parse holdings
        parsed_holdings = self._parse_holdings(holdings)
        
        if investment_amount <= 0:
            raise ValueError("Investment amount must be positive")
        
        logger.info(
            "Calculating portfolio income",
            extra={
                "etf_count": len(parsed_holdings),
                "investment_amount": investment_amount
            }
        )
        
        try:
            # Fetch dividend data for each holding
            holding_details = []
            total_weighted_yield = 0.0
            
            for ticker, weight in parsed_holdings.items():
                hist = await self.get_etf_dividend_history(ticker, years=1)
                
                current_yield = hist.get('current_yield', 0) or 0
                annual_dividend = hist['analysis'].get('annual_dividend', 0) or 0
                payment_freq = hist['analysis'].get('payment_frequency', 'Unknown')
                
                allocation = investment_amount * (weight / 100)
                annual_income = allocation * current_yield
                
                holding_details.append({
                    "ticker": ticker,
                    "weight": weight,
                    "allocation": round(allocation, 2),
                    "current_yield": current_yield,
                    "annual_income": round(annual_income, 2),
                    "payment_frequency": payment_freq
                })
                
                total_weighted_yield += (weight / 100) * current_yield
            
            # Calculate total annual income
            total_annual_income = sum(h['annual_income'] for h in holding_details)
            
            # Estimate monthly and quarterly income (average)
            monthly_income = total_annual_income / 12
            quarterly_income = total_annual_income / 4
            
            logger.info(
                "Portfolio income calculated",
                extra={
                    "annual_income": total_annual_income,
                    "weighted_yield": total_weighted_yield
                }
            )
            
            return {
                "investment_amount": investment_amount,
                "portfolio_yield": round(total_weighted_yield, 6),
                "income_projections": {
                    "annual": round(total_annual_income, 2),
                    "quarterly": round(quarterly_income, 2),
                    "monthly": round(monthly_income, 2)
                },
                "holdings": holding_details,
                "income_growth_potential": self._assess_income_growth(holding_details),
                "calculation_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(
                "Failed to calculate portfolio income",
                extra={"error": str(e)},
                exc_info=True
            )
            raise
    
    async def get_dividend_calendar(
        self,
        tickers: List[str],
        months: int = 12
    ) -> Dict[str, Any]:
        """
        Generate dividend payment calendar for portfolio planning.
        
        Shows expected dividend payments by month.
        
        Args:
            tickers: List of ETF ticker symbols
            months: Number of months to project (default: 12)
            
        Returns:
            Payment calendar with monthly breakdown
            
        Example:
            >>> cal = await get_dividend_calendar(["VYM", "SCHD", "DGRO"])
            >>> print(cal['monthly_calendar']['2025-12'])
            [{"ticker": "VYM", "ex_date": "2025-12-15", "estimated_amount": 0.85}]
        """
        if not tickers or len(tickers) == 0:
            raise ValueError("Must provide at least one ticker")
        
        if months < 1 or months > 24:
            raise ValueError("Months must be between 1 and 24")
        
        tickers = [t.upper().strip() for t in tickers]
        
        logger.info(
            "Generating dividend calendar",
            extra={"ticker_count": len(tickers), "months": months}
        )
        
        try:
            # Fetch dividend history for pattern analysis
            etf_schedules = []
            for ticker in tickers:
                hist = await self.get_etf_dividend_history(ticker, years=2)
                
                if hist['dividends']:
                    schedule = self._estimate_future_payments(
                        ticker,
                        hist['dividends'],
                        months
                    )
                    etf_schedules.append(schedule)
            
            # Build monthly calendar
            monthly_calendar = {}
            current_date = datetime.utcnow()
            
            for i in range(months):
                month_date = current_date + timedelta(days=30 * i)
                month_key = month_date.strftime('%Y-%m')
                monthly_calendar[month_key] = []
            
            # Add payments to calendar
            for schedule in etf_schedules:
                for payment in schedule['estimated_payments']:
                    month_key = payment['month']
                    if month_key in monthly_calendar:
                        monthly_calendar[month_key].append({
                            "ticker": schedule['ticker'],
                            "estimated_date": payment['estimated_date'],
                            "estimated_amount": payment['estimated_amount']
                        })
            
            # Calculate monthly totals
            monthly_totals = {}
            for month, payments in monthly_calendar.items():
                total = sum(p['estimated_amount'] for p in payments)
                monthly_totals[month] = round(total, 2)
            
            logger.info(
                "Dividend calendar generated",
                extra={"month_count": len(monthly_calendar)}
            )
            
            return {
                "tickers": tickers,
                "projection_months": months,
                "monthly_calendar": monthly_calendar,
                "monthly_totals": monthly_totals,
                "note": "Dates and amounts are estimates based on historical patterns",
                "calculation_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(
                "Failed to generate dividend calendar",
                extra={"error": str(e)},
                exc_info=True
            )
            raise
    
    # ==================== Private Helper Methods ====================
    
    async def _fetch_dividend_history(
        self,
        ticker: str,
        years: int,
        force_refresh: bool = False
    ) -> List[Dict]:
        """
        Fetch dividend history from cache or API.
        
        Returns list of dividend payments sorted by date (newest first).
        """
        try:
            # Calculate start year
            current_year = datetime.utcnow().year
            start_year = current_year - years
            
            # Check database cache first
            if not force_refresh:
                logger.info(
                    "Checking database for dividend history",
                    extra={"ticker": ticker, "start_year": start_year}
                )
                
                cached_dividends = await provider_repository.get_dividends(
                    ticker=ticker,
                    start_year=start_year
                )
                
                if cached_dividends and len(cached_dividends) > 0:
                    formatted = [
                        {
                            'date': str(div.ex_date),
                            'amount': div.amount,
                            'type': div.dividend_type or 'DIVIDEND'
                        }
                        for div in cached_dividends
                    ]
                    
                    # Sort by date (newest first)
                    formatted.sort(key=lambda x: x['date'], reverse=True)
                    
                    logger.info(
                        "Dividend history found in cache",
                        extra={"ticker": ticker, "dividend_count": len(formatted)}
                    )
                    return formatted
            
            # Not in cache - fetch from API
            logger.info(
                "Dividend history not in cache, fetching from provider",
                extra={"ticker": ticker}
            )
            
            # Get Alpha Vantage provider
            alpha_vantage_provider = provider_manager._get_provider_by_name("AlphaVantageProvider")
            if not alpha_vantage_provider:
                logger.warning("Alpha Vantage provider not available")
                return []
            
            # Fetch dividends from provider
            raw_dividends = await alpha_vantage_provider.get_dividends(ticker)
            
            if not raw_dividends:
                logger.info(
                    "No dividend data returned from provider",
                    extra={"ticker": ticker}
                )
                return []
            
            # Convert and save to cache
            formatted = []
            start_date = datetime(start_year, 1, 1).date()
            
            for div in raw_dividends:
                div_date = div.get('date') or div.get('ex_date')
                if not div_date:
                    continue
                
                # Check if in date range
                div_datetime = datetime.strptime(div_date, '%Y-%m-%d').date()
                if div_datetime < start_date:
                    continue
                
                amount = div.get('amount', 0)
                div_type = div.get('type', 'DIVIDEND')
                
                formatted.append({
                    'date': div_date,
                    'amount': amount,
                    'type': div_type
                })
                
                # Save to database
                try:
                    await provider_repository.save_dividend(
                        {
                            'ticker': ticker,
                            'ex_date': div_date,
                            'amount': amount,
                            'dividend_type': div_type
                        },
                        DataSource.ALPHA_VANTAGE
                    )
                except Exception as save_error:
                    logger.warning(
                        "Failed to save dividend to cache",
                        extra={"ticker": ticker, "date": div_date, "error": str(save_error)}
                    )
            
            # Sort by date (newest first)
            formatted.sort(key=lambda x: x['date'], reverse=True)
            
            logger.info(
                "Dividend history fetched from API and cached",
                extra={"ticker": ticker, "dividend_count": len(formatted)}
            )
            
            return formatted
            
        except Exception as e:
            logger.error(
                "Failed to fetch dividend history",
                extra={"ticker": ticker, "error": str(e)},
                exc_info=True
            )
            return []
    
    def _analyze_dividend_history(
        self,
        dividends: List[Dict],
        current_price: Optional[float]
    ) -> Dict[str, Any]:
        """Analyze dividend payment patterns."""
        if not dividends:
            return {
                "payment_frequency": "Unknown",
                "annual_dividend": None,
                "dividend_growth_1y": None,
                "dividend_growth_3y": None,
                "payout_consistency": None
            }
        
        # Determine payment frequency
        payment_count = len(dividends)
        latest_date = datetime.strptime(dividends[0]['date'], '%Y-%m-%d')
        oldest_date = datetime.strptime(dividends[-1]['date'], '%Y-%m-%d')
        days_span = (latest_date - oldest_date).days
        
        if days_span > 0:
            payments_per_year = (payment_count / days_span) * 365
            
            if payments_per_year >= 11:
                frequency = "Monthly"
            elif payments_per_year >= 3.5:
                frequency = "Quarterly"
            elif payments_per_year >= 1.5:
                frequency = "Semi-Annual"
            elif payments_per_year >= 0.8:
                frequency = "Annual"
            else:
                frequency = "Irregular"
        else:
            frequency = "Unknown"
        
        # Calculate annual dividend (last 12 months)
        one_year_ago = datetime.utcnow() - timedelta(days=365)
        recent_dividends = [
            d for d in dividends
            if datetime.strptime(d['date'], '%Y-%m-%d') >= one_year_ago
        ]
        annual_dividend = sum(d['amount'] for d in recent_dividends)
        
        # Calculate dividend growth (1Y)
        growth_1y = self._calculate_dividend_cagr(dividends, 1)
        growth_3y = self._calculate_dividend_cagr(dividends, 3)
        
        # Assess payout consistency (0-100 score)
        consistency = self._calculate_consistency_score(dividends)
        
        return {
            "payment_frequency": frequency,
            "annual_dividend": round(annual_dividend, 4) if annual_dividend else None,
            "dividend_growth_1y": round(growth_1y, 6) if growth_1y is not None else None,
            "dividend_growth_3y": round(growth_3y, 6) if growth_3y is not None else None,
            "payout_consistency": round(consistency, 2) if consistency is not None else None
        }
    
    def _calculate_dividend_cagr(
        self,
        dividends: List[Dict],
        years: int
    ) -> Optional[float]:
        """Calculate compound annual growth rate for dividends."""
        try:
            # Get dividends from target year ago
            target_date = datetime.utcnow() - timedelta(days=365 * years)
            
            # Get most recent annual dividend
            recent_annual = sum(
                d['amount'] for d in dividends[:12]
            )
            
            # Get annual dividend from years ago
            past_divs = [
                d for d in dividends
                if datetime.strptime(d['date'], '%Y-%m-%d') <= target_date
            ]
            
            if not past_divs or len(past_divs) < 4:
                return None
            
            past_annual = sum(d['amount'] for d in past_divs[:12])
            
            if past_annual <= 0:
                return None
            
            # CAGR formula: (ending / beginning)^(1/years) - 1
            cagr = (recent_annual / past_annual) ** (1 / years) - 1
            
            return cagr
            
        except Exception:
            return None
    
    def _calculate_consistency_score(self, dividends: List[Dict]) -> Optional[float]:
        """Calculate dividend consistency score (0-100)."""
        if not dividends or len(dividends) < 4:
            return None
        
        # Check for missed payments (expect quarterly = 4/year)
        recent_divs = dividends[:20]  # Last 5 years
        dates = [datetime.strptime(d['date'], '%Y-%m-%d') for d in recent_divs]
        
        # Calculate average gap between payments
        gaps = []
        for i in range(1, len(dates)):
            gap_days = (dates[i-1] - dates[i]).days
            gaps.append(gap_days)
        
        if not gaps:
            return None
        
        avg_gap = np.mean(gaps)
        std_gap = np.std(gaps)
        
        # Lower std = more consistent
        # Score: 100 - (std / avg * 100)
        if avg_gap > 0:
            consistency = max(0, 100 - (std_gap / avg_gap * 100))
            return consistency
        
        return None
    
    def _parse_holdings(self, holdings: str) -> Dict[str, float]:
        """Parse holdings string into ticker->weight dict."""
        parsed = {}
        
        for holding in holdings.split(','):
            parts = holding.strip().split(':')
            if len(parts) != 2:
                raise ValueError(f"Invalid holding format: {holding}. Expected 'TICKER:WEIGHT'")
            
            ticker = parts[0].strip().upper()
            try:
                weight = float(parts[1].strip())
            except ValueError:
                raise ValueError(f"Invalid weight for {ticker}: {parts[1]}")
            
            if weight < 0 or weight > 100:
                raise ValueError(f"Weight must be 0-100 for {ticker}")
            
            parsed[ticker] = weight
        
        # Validate weights sum to 100
        total_weight = sum(parsed.values())
        if abs(total_weight - 100) > 0.01:
            raise ValueError(f"Weights must sum to 100, got {total_weight}")
        
        return parsed
    
    def _assess_income_growth(self, holdings: List[Dict]) -> str:
        """Assess portfolio's income growth potential."""
        # Simple heuristic based on yields
        avg_yield = np.mean([h['current_yield'] for h in holdings if h['current_yield']])
        
        if avg_yield >= 0.04:
            return "High - Portfolio focused on current income"
        elif avg_yield >= 0.025:
            return "Moderate - Balanced income and growth"
        else:
            return "Low - Portfolio focused on growth over income"
    
    def _estimate_future_payments(
        self,
        ticker: str,
        dividends: List[Dict],
        months: int
    ) -> Dict[str, Any]:
        """Estimate future dividend payments based on historical pattern."""
        if not dividends or len(dividends) < 4:
            return {
                "ticker": ticker,
                "estimated_payments": []
            }
        
        # Analyze payment pattern
        recent_divs = dividends[:12]
        dates = [datetime.strptime(d['date'], '%Y-%m-%d') for d in recent_divs]
        amounts = [d['amount'] for d in recent_divs]
        
        # Calculate average amount and gap
        avg_amount = np.mean(amounts)
        
        gaps = []
        for i in range(1, len(dates)):
            gap_days = (dates[i-1] - dates[i]).days
            gaps.append(gap_days)
        
        avg_gap = int(np.mean(gaps)) if gaps else 90
        
        # Project future payments
        estimated_payments = []
        last_payment_date = dates[0]
        
        for i in range(1, months + 1):
            next_date = last_payment_date + timedelta(days=avg_gap * i)
            month_key = next_date.strftime('%Y-%m')
            
            estimated_payments.append({
                "month": month_key,
                "estimated_date": next_date.strftime('%Y-%m-%d'),
                "estimated_amount": round(avg_amount, 4)
            })
        
        return {
            "ticker": ticker,
            "estimated_payments": estimated_payments
        }
    
    def _interpret_dividend_growth(self, growth_rates: Dict[str, Optional[float]]) -> str:
        """Interpret dividend growth rates."""
        growth_1y = growth_rates.get('1Y')
        
        if growth_1y is None:
            return "Insufficient data"
        elif growth_1y >= 0.10:
            return "Strong dividend growth (>10% CAGR)"
        elif growth_1y >= 0.05:
            return "Moderate dividend growth (5-10% CAGR)"
        elif growth_1y >= 0:
            return "Stable dividends with modest growth"
        else:
            return "Declining dividends - caution advised"


# Singleton instance
etf_dividend_service = ETFDividendService()
