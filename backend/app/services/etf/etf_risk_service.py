"""
ETF Risk Analysis Service.

Provides risk metrics, volatility analysis, and correlation calculations for ETFs.

SECURITY: No sensitive data handling required.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import numpy as np
from app.core.logging_config import get_logger
from app.services.etf.etf_profile_service import etf_profile_service
from app.services.etf.etf_performance_service import etf_performance_service
from app.repositories.provider_repository import provider_repository

logger = get_logger(__name__)


class ETFRiskService:
    """
    Service for ETF risk analysis and correlation calculations.
    
    Features:
    - Volatility metrics (standard deviation, variance)
    - Beta calculation (vs SPY benchmark)
    - Sharpe ratio calculation
    - Correlation matrix for multiple ETFs
    - Portfolio-level risk metrics
    """
    
    # Risk-free rate (US 10-year Treasury approximate)
    RISK_FREE_RATE = 0.045  # 4.5% annual
    
    # Default benchmark for beta calculation
    DEFAULT_BENCHMARK = "SPY"
    
    async def get_risk_metrics(
        self,
        ticker: str,
        period_days: int = 252,
        benchmark: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive risk metrics for an ETF.
        
        Args:
            ticker: ETF ticker symbol
            period_days: Analysis period in trading days (default 252 = 1 year)
            benchmark: Benchmark ticker for beta (default SPY)
            
        Returns:
            Risk metrics including volatility, beta, Sharpe ratio, VaR, etc.
            
        Example:
            >>> metrics = await risk_service.get_risk_metrics("VOO", period_days=252)
            >>> print(metrics['volatility_annual'])
            0.185  # 18.5% annual volatility
        """
        logger.info(
            "Calculating risk metrics",
            extra={"ticker": ticker, "period_days": period_days}
        )
        
        try:
            # Get ETF profile for basic info
            profile = await etf_profile_service.get_etf_profile(ticker)
            
            # Get historical returns (simulated for now - will use real data later)
            returns = await self._get_historical_returns(ticker, period_days)
            
            if not returns or len(returns) < 30:
                logger.warning(
                    "Insufficient data for risk analysis",
                    extra={"ticker": ticker, "data_points": len(returns) if returns else 0}
                )
                return self._generate_fallback_risk_metrics(ticker, profile)
            
            # Calculate volatility metrics
            volatility_daily = np.std(returns)
            volatility_annual = volatility_daily * np.sqrt(252)  # Annualize
            variance_annual = volatility_annual ** 2
            
            # Calculate mean return
            mean_return_daily = np.mean(returns)
            mean_return_annual = mean_return_daily * 252
            
            # Calculate Sharpe ratio
            excess_return = mean_return_annual - self.RISK_FREE_RATE
            sharpe_ratio = excess_return / volatility_annual if volatility_annual > 0 else 0
            
            # Calculate beta (vs benchmark)
            benchmark_ticker = benchmark or self.DEFAULT_BENCHMARK
            beta = await self._calculate_beta(ticker, benchmark_ticker, period_days)
            
            # Calculate Value at Risk (VaR) - 95% confidence
            var_95 = np.percentile(returns, 5) * np.sqrt(252)  # Annualized
            
            # Calculate Conditional VaR (Expected Shortfall)
            cvar_95 = np.mean([r for r in returns if r <= np.percentile(returns, 5)]) * np.sqrt(252)
            
            # Calculate Maximum Drawdown
            max_drawdown = await self._calculate_max_drawdown(ticker, period_days)
            
            # Determine risk level
            risk_level = self._classify_risk_level(volatility_annual, beta)
            
            result = {
                "ticker": ticker,
                "etf_name": profile.get('name'),
                "analysis_period_days": period_days,
                "data_points": len(returns),
                "volatility": {
                    "daily": round(volatility_daily, 6),
                    "daily_pct": round(volatility_daily * 100, 4),
                    "annual": round(volatility_annual, 6),
                    "annual_pct": round(volatility_annual * 100, 2),
                    "variance_annual": round(variance_annual, 6)
                },
                "returns": {
                    "mean_daily": round(mean_return_daily, 6),
                    "mean_daily_pct": round(mean_return_daily * 100, 4),
                    "mean_annual": round(mean_return_annual, 6),
                    "mean_annual_pct": round(mean_return_annual * 100, 2)
                },
                "risk_adjusted": {
                    "sharpe_ratio": round(sharpe_ratio, 4),
                    "sharpe_interpretation": self._interpret_sharpe_ratio(sharpe_ratio)
                },
                "market_risk": {
                    "beta": round(beta, 4),
                    "beta_vs": benchmark_ticker,
                    "beta_interpretation": self._interpret_beta(beta)
                },
                "downside_risk": {
                    "var_95_annual": round(var_95, 6),
                    "var_95_annual_pct": round(var_95 * 100, 2),
                    "cvar_95_annual": round(cvar_95, 6),
                    "cvar_95_annual_pct": round(cvar_95 * 100, 2),
                    "max_drawdown": round(max_drawdown, 6),
                    "max_drawdown_pct": round(max_drawdown * 100, 2)
                },
                "risk_classification": {
                    "level": risk_level,
                    "description": self._get_risk_description(risk_level)
                },
                "calculation_timestamp": datetime.now().isoformat()
            }
            
            logger.info(
                "Risk metrics calculated",
                extra={
                    "ticker": ticker,
                    "volatility": volatility_annual,
                    "sharpe": sharpe_ratio,
                    "risk_level": risk_level
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(
                "Failed to calculate risk metrics",
                extra={"ticker": ticker, "error": str(e)},
                exc_info=True
            )
            raise
    
    async def calculate_correlation_matrix(
        self,
        tickers: List[str],
        period_days: int = 252
    ) -> Dict[str, Any]:
        """
        Calculate correlation matrix for multiple ETFs.
        
        Args:
            tickers: List of ETF ticker symbols (2-20 ETFs)
            period_days: Analysis period in trading days
            
        Returns:
            Correlation matrix with coefficients and interpretations
            
        Example:
            >>> matrix = await risk_service.calculate_correlation_matrix(
            ...     ["VOO", "VTI", "VXUS"], period_days=252
            ... )
            >>> print(matrix['correlations']['VOO']['VTI'])
            0.98  # Highly correlated
        """
        logger.info(
            "Calculating correlation matrix",
            extra={"tickers": tickers, "count": len(tickers)}
        )
        
        if len(tickers) < 2:
            raise ValueError("Need at least 2 ETFs for correlation analysis")
        
        if len(tickers) > 20:
            raise ValueError("Maximum 20 ETFs allowed for correlation matrix")
        
        try:
            # Get returns for all ETFs
            all_returns = {}
            for ticker in tickers:
                returns = await self._get_historical_returns(ticker, period_days)
                if returns and len(returns) >= 30:
                    all_returns[ticker] = returns
                else:
                    logger.warning(
                        "Insufficient data for correlation",
                        extra={"ticker": ticker}
                    )
            
            if len(all_returns) < 2:
                raise ValueError("Insufficient data for at least 2 ETFs")
            
            # Ensure all return arrays have the same length
            min_length = min(len(returns) for returns in all_returns.values())
            aligned_returns = {
                ticker: returns[-min_length:] 
                for ticker, returns in all_returns.items()
            }
            
            # Build correlation matrix
            tickers_with_data = list(aligned_returns.keys())
            n = len(tickers_with_data)
            correlations = {}
            
            for i, ticker1 in enumerate(tickers_with_data):
                correlations[ticker1] = {}
                for ticker2 in tickers_with_data:
                    if ticker1 == ticker2:
                        correlations[ticker1][ticker2] = 1.0
                    else:
                        corr = np.corrcoef(
                            aligned_returns[ticker1],
                            aligned_returns[ticker2]
                        )[0, 1]
                        correlations[ticker1][ticker2] = round(float(corr), 4)
            
            # Find highest and lowest correlations (excluding self-correlation)
            all_pairs = []
            for ticker1 in tickers_with_data:
                for ticker2 in tickers_with_data:
                    if ticker1 < ticker2:  # Avoid duplicates
                        corr = correlations[ticker1][ticker2]
                        all_pairs.append({
                            "etf1": ticker1,
                            "etf2": ticker2,
                            "correlation": corr,
                            "interpretation": self._interpret_correlation(corr)
                        })
            
            all_pairs.sort(key=lambda x: abs(x['correlation']), reverse=True)
            
            # Calculate average correlation
            if all_pairs:
                avg_correlation = np.mean([pair['correlation'] for pair in all_pairs])
            else:
                avg_correlation = 0
            
            result = {
                "tickers": tickers_with_data,
                "analysis_period_days": period_days,
                "data_points": min_length,
                "correlations": correlations,
                "summary": {
                    "average_correlation": round(float(avg_correlation), 4),
                    "highest_correlation": all_pairs[0] if all_pairs else None,
                    "lowest_correlation": all_pairs[-1] if all_pairs else None
                },
                "all_pairs": all_pairs,
                "diversification_score": self._calculate_diversification_score(correlations),
                "calculation_timestamp": datetime.now().isoformat()
            }
            
            logger.info(
                "Correlation matrix calculated",
                extra={
                    "tickers": len(tickers_with_data),
                    "avg_correlation": avg_correlation
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(
                "Failed to calculate correlation matrix",
                extra={"tickers": tickers, "error": str(e)},
                exc_info=True
            )
            raise
    
    async def analyze_portfolio_risk(
        self,
        holdings: Dict[str, float],
        period_days: int = 252,
        benchmark: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate portfolio-level risk metrics.
        
        Args:
            holdings: Dictionary of {ticker: weight} (weights sum to 1.0)
            period_days: Analysis period in trading days
            benchmark: Benchmark ticker for beta
            
        Returns:
            Portfolio risk metrics including volatility, Sharpe, diversification
            
        Example:
            >>> risk = await risk_service.analyze_portfolio_risk(
            ...     {"VOO": 0.6, "VTI": 0.3, "VXUS": 0.1}
            ... )
            >>> print(risk['portfolio_volatility_annual_pct'])
            15.2  # Portfolio volatility
        """
        logger.info(
            "Analyzing portfolio risk",
            extra={"holdings": len(holdings), "period_days": period_days}
        )
        
        if not holdings:
            raise ValueError("Holdings cannot be empty")
        
        # Validate weights sum to ~1.0
        total_weight = sum(holdings.values())
        if abs(total_weight - 1.0) > 0.01:
            logger.warning(
                "Weights don't sum to 1.0, normalizing",
                extra={"total_weight": total_weight}
            )
            holdings = {ticker: weight / total_weight for ticker, weight in holdings.items()}
        
        try:
            tickers = list(holdings.keys())
            
            # Get returns for all holdings
            all_returns = {}
            for ticker in tickers:
                returns = await self._get_historical_returns(ticker, period_days)
                if returns and len(returns) >= 30:
                    all_returns[ticker] = returns
            
            if len(all_returns) < len(tickers):
                logger.warning(
                    "Some ETFs lack data",
                    extra={"requested": len(tickers), "available": len(all_returns)}
                )
            
            # Align returns to same length
            min_length = min(len(returns) for returns in all_returns.values())
            aligned_returns = {
                ticker: returns[-min_length:]
                for ticker, returns in all_returns.items()
            }
            
            # Calculate portfolio returns
            portfolio_returns = np.zeros(min_length)
            for ticker, returns in aligned_returns.items():
                weight = holdings.get(ticker, 0)
                portfolio_returns += np.array(returns) * weight
            
            # Calculate portfolio volatility
            portfolio_vol_daily = np.std(portfolio_returns)
            portfolio_vol_annual = portfolio_vol_daily * np.sqrt(252)
            
            # Calculate portfolio mean return
            portfolio_mean_daily = np.mean(portfolio_returns)
            portfolio_mean_annual = portfolio_mean_daily * 252
            
            # Calculate portfolio Sharpe ratio
            excess_return = portfolio_mean_annual - self.RISK_FREE_RATE
            portfolio_sharpe = excess_return / portfolio_vol_annual if portfolio_vol_annual > 0 else 0
            
            # Calculate portfolio beta
            benchmark_ticker = benchmark or self.DEFAULT_BENCHMARK
            benchmark_returns = await self._get_historical_returns(benchmark_ticker, period_days)
            if benchmark_returns and len(benchmark_returns) >= min_length:
                benchmark_returns_aligned = benchmark_returns[-min_length:]
                covariance = np.cov(portfolio_returns, benchmark_returns_aligned)[0, 1]
                benchmark_variance = np.var(benchmark_returns_aligned)
                portfolio_beta = covariance / benchmark_variance if benchmark_variance > 0 else 1.0
            else:
                portfolio_beta = 1.0
            
            # Get individual ETF risk metrics
            individual_metrics = []
            for ticker, weight in holdings.items():
                try:
                    metrics = await self.get_risk_metrics(ticker, period_days, benchmark)
                    individual_metrics.append({
                        "ticker": ticker,
                        "weight": weight,
                        "weight_pct": round(weight * 100, 2),
                        "volatility_annual_pct": metrics['volatility']['annual_pct'],
                        "sharpe_ratio": metrics['risk_adjusted']['sharpe_ratio'],
                        "beta": metrics['market_risk']['beta']
                    })
                except Exception as e:
                    logger.warning(
                        "Could not get risk metrics for ETF",
                        extra={"ticker": ticker, "error": str(e)}
                    )
            
            # Calculate correlation matrix for diversification benefit
            correlation_result = await self.calculate_correlation_matrix(tickers, period_days)
            
            # Calculate weighted average metrics
            weighted_volatility = sum(
                m['volatility_annual_pct'] * m['weight']
                for m in individual_metrics
            ) if individual_metrics else 0
            
            weighted_beta = sum(
                m['beta'] * m['weight']
                for m in individual_metrics
            ) if individual_metrics else portfolio_beta
            
            # Diversification benefit (reduction in volatility vs weighted average)
            diversification_benefit = weighted_volatility - (portfolio_vol_annual * 100)
            
            result = {
                "holdings": holdings,
                "holdings_count": len(holdings),
                "analysis_period_days": period_days,
                "data_points": min_length,
                "portfolio_metrics": {
                    "volatility_daily": round(portfolio_vol_daily, 6),
                    "volatility_daily_pct": round(portfolio_vol_daily * 100, 4),
                    "volatility_annual": round(portfolio_vol_annual, 6),
                    "volatility_annual_pct": round(portfolio_vol_annual * 100, 2),
                    "mean_return_annual_pct": round(portfolio_mean_annual * 100, 2),
                    "sharpe_ratio": round(portfolio_sharpe, 4),
                    "beta": round(portfolio_beta, 4),
                    "beta_vs": benchmark_ticker
                },
                "individual_etfs": individual_metrics,
                "diversification": {
                    "weighted_avg_volatility_pct": round(weighted_volatility, 2),
                    "portfolio_volatility_pct": round(portfolio_vol_annual * 100, 2),
                    "diversification_benefit_pct": round(diversification_benefit, 2),
                    "benefit_interpretation": (
                        f"Portfolio is {abs(diversification_benefit):.2f}% "
                        f"{'less' if diversification_benefit > 0 else 'more'} volatile "
                        "than weighted average"
                    ),
                    "average_correlation": correlation_result['summary']['average_correlation'],
                    "diversification_score": correlation_result['diversification_score']
                },
                "risk_classification": {
                    "level": self._classify_risk_level(portfolio_vol_annual, portfolio_beta),
                    "description": self._get_risk_description(
                        self._classify_risk_level(portfolio_vol_annual, portfolio_beta)
                    )
                },
                "calculation_timestamp": datetime.now().isoformat()
            }
            
            logger.info(
                "Portfolio risk analysis complete",
                extra={
                    "portfolio_vol": portfolio_vol_annual,
                    "sharpe": portfolio_sharpe,
                    "diversification_benefit": diversification_benefit
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(
                "Failed to analyze portfolio risk",
                extra={"holdings": len(holdings), "error": str(e)},
                exc_info=True
            )
            raise
    
    # -------------------- Helper Methods --------------------
    
    async def _get_historical_returns(
        self,
        ticker: str,
        period_days: int
    ) -> Optional[List[float]]:
        """
        Get historical daily returns for a ticker.
        
        For now, generates simulated returns. Will be replaced with real data.
        """
        # TODO: Replace with actual historical price data from provider
        # For now, generate realistic simulated returns
        
        # Use ticker hash for consistent but varied returns
        seed = sum(ord(c) for c in ticker)
        np.random.seed(seed)
        
        # Different profiles for different ETFs
        if ticker in ["SPY", "VOO", "VTI", "IVV"]:
            # Large cap US - moderate volatility
            returns = np.random.normal(0.0004, 0.010, period_days)  # 10% annual return, 16% vol
        elif ticker in ["VXUS", "VEA", "VWO"]:
            # International - higher volatility
            returns = np.random.normal(0.0003, 0.013, period_days)  # 8% return, 20% vol
        elif ticker in ["AGG", "BND", "TLT"]:
            # Bonds - lower volatility
            returns = np.random.normal(0.0001, 0.004, period_days)  # 3% return, 6% vol
        elif ticker in ["QQQ", "VGT", "XLK"]:
            # Tech - high volatility
            returns = np.random.normal(0.0005, 0.015, period_days)  # 12% return, 24% vol
        elif ticker in ["ARKK", "ARKG"]:
            # Innovation - very high volatility
            returns = np.random.normal(0.0002, 0.025, period_days)  # 5% return, 40% vol
        else:
            # Default profile
            returns = np.random.normal(0.0003, 0.012, period_days)  # 8% return, 19% vol
        
        return returns.tolist()
    
    async def _calculate_beta(
        self,
        ticker: str,
        benchmark: str,
        period_days: int
    ) -> float:
        """Calculate beta vs benchmark."""
        try:
            etf_returns = await self._get_historical_returns(ticker, period_days)
            benchmark_returns = await self._get_historical_returns(benchmark, period_days)
            
            if not etf_returns or not benchmark_returns:
                return 1.0
            
            # Align lengths
            min_length = min(len(etf_returns), len(benchmark_returns))
            etf_returns = etf_returns[-min_length:]
            benchmark_returns = benchmark_returns[-min_length:]
            
            # Calculate beta: Cov(ETF, Benchmark) / Var(Benchmark)
            covariance = np.cov(etf_returns, benchmark_returns)[0, 1]
            benchmark_variance = np.var(benchmark_returns)
            
            if benchmark_variance == 0:
                return 1.0
            
            beta = covariance / benchmark_variance
            return float(beta)
            
        except Exception as e:
            logger.warning(
                "Beta calculation failed, using default",
                extra={"ticker": ticker, "error": str(e)}
            )
            return 1.0
    
    async def _calculate_max_drawdown(
        self,
        ticker: str,
        period_days: int
    ) -> float:
        """Calculate maximum drawdown."""
        try:
            returns = await self._get_historical_returns(ticker, period_days)
            if not returns:
                return 0.0
            
            # Calculate cumulative returns
            cumulative = np.cumprod(1 + np.array(returns))
            running_max = np.maximum.accumulate(cumulative)
            drawdowns = (cumulative - running_max) / running_max
            
            max_drawdown = float(np.min(drawdowns))
            return max_drawdown
            
        except Exception as e:
            logger.warning(
                "Max drawdown calculation failed",
                extra={"ticker": ticker, "error": str(e)}
            )
            return 0.0
    
    def _classify_risk_level(self, volatility_annual: float, beta: float) -> str:
        """Classify overall risk level."""
        if volatility_annual < 0.10 and abs(beta) < 0.5:
            return "Very Low"
        elif volatility_annual < 0.15 and abs(beta) < 0.8:
            return "Low"
        elif volatility_annual < 0.20 and abs(beta) < 1.2:
            return "Moderate"
        elif volatility_annual < 0.30 and abs(beta) < 1.5:
            return "High"
        else:
            return "Very High"
    
    def _get_risk_description(self, risk_level: str) -> str:
        """Get description for risk level."""
        descriptions = {
            "Very Low": "Suitable for conservative investors seeking capital preservation",
            "Low": "Appropriate for income-focused investors with low risk tolerance",
            "Moderate": "Balanced risk suitable for most long-term investors",
            "High": "Higher volatility requiring longer investment horizon",
            "Very High": "Speculative - suitable only for aggressive investors"
        }
        return descriptions.get(risk_level, "Unknown risk profile")
    
    def _interpret_sharpe_ratio(self, sharpe: float) -> str:
        """Interpret Sharpe ratio value."""
        if sharpe < 0:
            return "Negative - Returns below risk-free rate"
        elif sharpe < 1.0:
            return "Poor - Low risk-adjusted returns"
        elif sharpe < 2.0:
            return "Good - Adequate risk-adjusted returns"
        elif sharpe < 3.0:
            return "Very Good - Strong risk-adjusted returns"
        else:
            return "Excellent - Exceptional risk-adjusted returns"
    
    def _interpret_beta(self, beta: float) -> str:
        """Interpret beta value."""
        if beta < 0:
            return "Negative correlation with market (defensive)"
        elif beta < 0.5:
            return "Low market sensitivity (defensive)"
        elif beta < 0.8:
            return "Below-market volatility (moderately defensive)"
        elif beta < 1.2:
            return "Market-like volatility (neutral)"
        elif beta < 1.5:
            return "Above-market volatility (aggressive)"
        else:
            return "High market sensitivity (very aggressive)"
    
    def _interpret_correlation(self, corr: float) -> str:
        """Interpret correlation coefficient."""
        abs_corr = abs(corr)
        if abs_corr < 0.3:
            return "Weak correlation - good diversification"
        elif abs_corr < 0.7:
            return "Moderate correlation - some diversification"
        elif abs_corr < 0.9:
            return "Strong correlation - limited diversification"
        else:
            return "Very strong correlation - minimal diversification"
    
    def _calculate_diversification_score(self, correlations: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """Calculate diversification score (0-100)."""
        # Extract all correlation values (excluding self-correlation of 1.0)
        all_corrs = []
        for ticker1, corr_dict in correlations.items():
            for ticker2, corr in corr_dict.items():
                if ticker1 != ticker2:
                    all_corrs.append(abs(corr))
        
        if not all_corrs:
            return {"score": 50, "interpretation": "Insufficient data"}
        
        avg_abs_corr = np.mean(all_corrs)
        
        # Score: 100 = no correlation (perfect diversification)
        #        0 = perfect correlation (no diversification)
        score = max(0, min(100, (1 - avg_abs_corr) * 100))
        
        if score >= 70:
            interpretation = "Excellent diversification"
        elif score >= 50:
            interpretation = "Good diversification"
        elif score >= 30:
            interpretation = "Moderate diversification"
        else:
            interpretation = "Limited diversification"
        
        return {
            "score": round(score, 1),
            "interpretation": interpretation,
            "average_correlation": round(avg_abs_corr, 4)
        }
    
    def _generate_fallback_risk_metrics(
        self,
        ticker: str,
        profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate fallback metrics when insufficient data."""
        return {
            "ticker": ticker,
            "etf_name": profile.get('name'),
            "error": "Insufficient historical data for risk analysis",
            "minimum_required_days": 30,
            "volatility": None,
            "returns": None,
            "risk_adjusted": None,
            "market_risk": None,
            "downside_risk": None,
            "risk_classification": {
                "level": "Unknown",
                "description": "Insufficient data for risk assessment"
            },
            "calculation_timestamp": datetime.now().isoformat()
        }


# Singleton instance
etf_risk_service = ETFRiskService()
