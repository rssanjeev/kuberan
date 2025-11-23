"""
ETF Portfolio Backtesting Service.

Provides historical performance simulation, Monte Carlo scenarios, and drawdown analysis
for ETF portfolios to evaluate past performance and future projections.

Features:
- Historical backtesting with custom date ranges
- Monte Carlo simulation for portfolio projections
- Drawdown analysis and recovery metrics
- Risk-adjusted performance metrics
- Rebalancing simulation
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import random
import statistics
import math

from app.core.logging_config import get_logger

logger = get_logger(__name__)


class ETFBacktestingService:
    """Service for portfolio backtesting and scenario analysis."""
    
    def __init__(self):
        """Initialize the backtesting service."""
        logger.info("ETF Backtesting Service initialized")
    
    async def run_historical_backtest(
        self,
        portfolio: Dict[str, float],
        start_date: str,
        end_date: str,
        initial_investment: float = 10000.0,
        rebalance_frequency: str = "quarterly"
    ) -> Dict[str, Any]:
        """
        Run historical backtest for a portfolio allocation.
        
        Simulates portfolio performance over historical period with optional rebalancing.
        
        Args:
            portfolio: Dict of ticker -> weight (e.g., {"VOO": 0.6, "BND": 0.4})
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            initial_investment: Starting portfolio value in dollars
            rebalance_frequency: "never", "monthly", "quarterly", "annually"
        
        Returns:
            Comprehensive backtest results with performance metrics
        """
        logger.info(
            "Running historical backtest",
            extra={
                "tickers": list(portfolio.keys()),
                "start_date": start_date,
                "end_date": end_date,
                "initial_investment": initial_investment,
                "rebalance_frequency": rebalance_frequency
            }
        )
        
        # Validate inputs
        if sum(portfolio.values()) != 1.0:
            raise ValueError("Portfolio weights must sum to 1.0")
        
        if initial_investment <= 0:
            raise ValueError("Initial investment must be positive")
        
        # Parse dates
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        if end_dt <= start_dt:
            raise ValueError("End date must be after start date")
        
        # Generate sample price history for each ETF
        price_history = self._generate_historical_prices(portfolio, start_dt, end_dt)
        
        # Run backtest simulation
        backtest_results = self._simulate_portfolio(
            portfolio=portfolio,
            price_history=price_history,
            initial_investment=initial_investment,
            rebalance_frequency=rebalance_frequency,
            start_dt=start_dt,
            end_dt=end_dt
        )
        
        # Calculate performance metrics
        performance_metrics = self._calculate_backtest_metrics(
            backtest_results=backtest_results,
            initial_investment=initial_investment
        )
        
        # Calculate risk metrics
        risk_metrics = self._calculate_risk_metrics(backtest_results)
        
        # Calculate rebalancing impact
        rebalancing_analysis = self._analyze_rebalancing(
            portfolio=portfolio,
            backtest_results=backtest_results,
            rebalance_frequency=rebalance_frequency
        )
        
        logger.info(
            "Historical backtest completed",
            extra={
                "final_value": performance_metrics["final_value"],
                "total_return_pct": performance_metrics["total_return_pct"]
            }
        )
        
        return {
            "portfolio": portfolio,
            "period": {
                "start_date": start_date,
                "end_date": end_date,
                "trading_days": len(backtest_results["daily_values"])
            },
            "initial_investment": initial_investment,
            "rebalance_frequency": rebalance_frequency,
            "performance_metrics": performance_metrics,
            "risk_metrics": risk_metrics,
            "rebalancing_analysis": rebalancing_analysis,
            "daily_values": backtest_results["daily_values"][-30:],  # Last 30 days
            "monthly_returns": backtest_results["monthly_returns"],
            "rebalance_dates": backtest_results["rebalance_dates"],
            "calculation_timestamp": datetime.now().isoformat()
        }
    
    async def run_monte_carlo_simulation(
        self,
        portfolio: Dict[str, float],
        initial_investment: float = 10000.0,
        years: int = 10,
        simulations: int = 1000,
        confidence_level: float = 0.95
    ) -> Dict[str, Any]:
        """
        Run Monte Carlo simulation for portfolio projections.
        
        Simulates multiple possible future scenarios to estimate potential outcomes.
        
        Args:
            portfolio: Dict of ticker -> weight (e.g., {"VOO": 0.6, "BND": 0.4})
            initial_investment: Starting portfolio value in dollars
            years: Projection period in years
            simulations: Number of simulation runs (default 1000)
            confidence_level: Confidence level for intervals (default 0.95)
        
        Returns:
            Monte Carlo simulation results with projections and confidence intervals
        """
        logger.info(
            "Running Monte Carlo simulation",
            extra={
                "tickers": list(portfolio.keys()),
                "years": years,
                "simulations": simulations,
                "confidence_level": confidence_level
            }
        )
        
        # Validate inputs
        if sum(portfolio.values()) != 1.0:
            raise ValueError("Portfolio weights must sum to 1.0")
        
        if initial_investment <= 0:
            raise ValueError("Initial investment must be positive")
        
        if simulations < 100:
            raise ValueError("At least 100 simulations required")
        
        # Get expected returns and volatility for each ETF
        etf_parameters = self._get_etf_simulation_parameters(portfolio)
        
        # Run Monte Carlo simulations
        simulation_results = self._run_monte_carlo_simulations(
            portfolio=portfolio,
            etf_parameters=etf_parameters,
            initial_investment=initial_investment,
            years=years,
            simulations=simulations
        )
        
        # Calculate statistics from simulations
        simulation_statistics = self._calculate_monte_carlo_statistics(
            simulation_results=simulation_results,
            confidence_level=confidence_level
        )
        
        # Calculate probability metrics
        probability_metrics = self._calculate_probability_metrics(
            simulation_results=simulation_results,
            initial_investment=initial_investment
        )
        
        logger.info(
            "Monte Carlo simulation completed",
            extra={
                "median_final_value": simulation_statistics["median_final_value"],
                "probability_of_profit_pct": probability_metrics["probability_of_profit_pct"]
            }
        )
        
        return {
            "portfolio": portfolio,
            "initial_investment": initial_investment,
            "projection_years": years,
            "simulations_run": simulations,
            "confidence_level": confidence_level,
            "simulation_statistics": simulation_statistics,
            "probability_metrics": probability_metrics,
            "percentile_outcomes": simulation_statistics["percentiles"],
            "expected_returns": {
                ticker: params["expected_return"]
                for ticker, params in etf_parameters.items()
            },
            "calculation_timestamp": datetime.now().isoformat()
        }
    
    async def analyze_drawdowns(
        self,
        portfolio: Dict[str, float],
        start_date: str,
        end_date: str,
        initial_investment: float = 10000.0
    ) -> Dict[str, Any]:
        """
        Analyze portfolio drawdowns and recovery periods.
        
        Identifies worst drawdowns, recovery times, and underwater periods.
        
        Args:
            portfolio: Dict of ticker -> weight (e.g., {"VOO": 0.6, "BND": 0.4})
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            initial_investment: Starting portfolio value in dollars
        
        Returns:
            Comprehensive drawdown analysis with recovery metrics
        """
        logger.info(
            "Analyzing drawdowns",
            extra={
                "tickers": list(portfolio.keys()),
                "start_date": start_date,
                "end_date": end_date
            }
        )
        
        # Validate inputs
        if sum(portfolio.values()) != 1.0:
            raise ValueError("Portfolio weights must sum to 1.0")
        
        # Parse dates
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Generate price history
        price_history = self._generate_historical_prices(portfolio, start_dt, end_dt)
        
        # Calculate portfolio values over time
        portfolio_values = self._calculate_portfolio_values(
            portfolio=portfolio,
            price_history=price_history,
            initial_investment=initial_investment
        )
        
        # Identify drawdowns
        drawdowns = self._identify_drawdowns(portfolio_values)
        
        # Calculate drawdown statistics
        drawdown_statistics = self._calculate_drawdown_statistics(drawdowns)
        
        # Analyze recovery periods
        recovery_analysis = self._analyze_recovery_periods(drawdowns, portfolio_values)
        
        # Calculate underwater periods
        underwater_analysis = self._analyze_underwater_periods(portfolio_values)
        
        logger.info(
            "Drawdown analysis completed",
            extra={
                "max_drawdown_pct": drawdown_statistics["max_drawdown_pct"],
                "total_drawdowns": len(drawdowns)
            }
        )
        
        return {
            "portfolio": portfolio,
            "period": {
                "start_date": start_date,
                "end_date": end_date,
                "trading_days": len(portfolio_values)
            },
            "initial_investment": initial_investment,
            "drawdown_statistics": drawdown_statistics,
            "major_drawdowns": drawdowns[:5],  # Top 5 worst drawdowns
            "recovery_analysis": recovery_analysis,
            "underwater_analysis": underwater_analysis,
            "current_drawdown": self._get_current_drawdown(portfolio_values),
            "calculation_timestamp": datetime.now().isoformat()
        }
    
    # =========================================================================
    # HISTORICAL BACKTEST HELPERS
    # =========================================================================
    
    def _generate_historical_prices(
        self,
        portfolio: Dict[str, float],
        start_dt: datetime,
        end_dt: datetime
    ) -> Dict[str, List[Dict]]:
        """Generate sample historical price data for each ETF."""
        price_history = {}
        trading_days = (end_dt - start_dt).days
        
        for ticker in portfolio.keys():
            # Get base parameters for ETF type
            params = self._get_etf_base_parameters(ticker)
            
            # Generate daily prices with trend and volatility
            prices = []
            current_price = 100.0
            current_date = start_dt
            
            for day in range(trading_days):
                if current_date.weekday() < 5:  # Trading days only
                    # Daily return: drift + random shock
                    daily_return = (
                        params["annual_return"] / 252 +  # Daily drift
                        random.gauss(0, params["volatility"] / math.sqrt(252))  # Daily shock
                    )
                    current_price *= (1 + daily_return)
                    
                    prices.append({
                        "date": current_date.strftime("%Y-%m-%d"),
                        "price": current_price
                    })
                
                current_date += timedelta(days=1)
            
            price_history[ticker] = prices
        
        return price_history
    
    def _get_etf_base_parameters(self, ticker: str) -> Dict[str, float]:
        """Get base parameters for ETF type."""
        # ETF type detection and parameters
        etf_params = {
            "VOO": {"annual_return": 0.10, "volatility": 0.15},  # S&P 500
            "SPY": {"annual_return": 0.10, "volatility": 0.15},  # S&P 500
            "QQQ": {"annual_return": 0.13, "volatility": 0.20},  # Tech-heavy
            "VTI": {"annual_return": 0.10, "volatility": 0.16},  # Total market
            "BND": {"annual_return": 0.03, "volatility": 0.04},  # Bonds
            "AGG": {"annual_return": 0.03, "volatility": 0.04},  # Bonds
            "VTV": {"annual_return": 0.09, "volatility": 0.14},  # Value
            "VUG": {"annual_return": 0.12, "volatility": 0.18},  # Growth
            "VWO": {"annual_return": 0.08, "volatility": 0.22},  # Emerging
            "GLD": {"annual_return": 0.05, "volatility": 0.16},  # Gold
        }
        
        # Default parameters for unknown tickers
        return etf_params.get(ticker, {"annual_return": 0.08, "volatility": 0.15})
    
    def _simulate_portfolio(
        self,
        portfolio: Dict[str, float],
        price_history: Dict[str, List[Dict]],
        initial_investment: float,
        rebalance_frequency: str,
        start_dt: datetime,
        end_dt: datetime
    ) -> Dict[str, Any]:
        """Simulate portfolio performance with rebalancing."""
        # Initialize portfolio holdings
        holdings = {}
        for ticker, weight in portfolio.items():
            initial_price = price_history[ticker][0]["price"]
            holdings[ticker] = (initial_investment * weight) / initial_price
        
        daily_values = []
        monthly_returns = []
        rebalance_dates = []
        
        # Track rebalancing schedule
        last_rebalance = start_dt
        current_month = start_dt.month
        
        # Simulate each trading day
        num_days = len(price_history[list(portfolio.keys())[0]])
        
        for day_idx in range(num_days):
            # Calculate current portfolio value
            total_value = 0.0
            for ticker, shares in holdings.items():
                current_price = price_history[ticker][day_idx]["price"]
                total_value += shares * current_price
            
            date_str = price_history[list(portfolio.keys())[0]][day_idx]["date"]
            current_date = datetime.strptime(date_str, "%Y-%m-%d")
            
            daily_values.append({
                "date": date_str,
                "value": total_value
            })
            
            # Track monthly returns
            if current_date.month != current_month:
                if len(daily_values) >= 2:
                    month_start_value = daily_values[-30]["value"] if len(daily_values) >= 30 else daily_values[0]["value"]
                    monthly_return = ((total_value - month_start_value) / month_start_value) * 100
                    monthly_returns.append({
                        "month": current_date.strftime("%Y-%m"),
                        "return_pct": monthly_return
                    })
                current_month = current_date.month
            
            # Check if rebalancing is needed
            should_rebalance = self._should_rebalance(
                current_date=current_date,
                last_rebalance=last_rebalance,
                rebalance_frequency=rebalance_frequency
            )
            
            if should_rebalance:
                # Rebalance to target weights
                for ticker, weight in portfolio.items():
                    target_value = total_value * weight
                    current_price = price_history[ticker][day_idx]["price"]
                    holdings[ticker] = target_value / current_price
                
                rebalance_dates.append(date_str)
                last_rebalance = current_date
        
        return {
            "daily_values": daily_values,
            "monthly_returns": monthly_returns,
            "rebalance_dates": rebalance_dates
        }
    
    def _should_rebalance(
        self,
        current_date: datetime,
        last_rebalance: datetime,
        rebalance_frequency: str
    ) -> bool:
        """Determine if rebalancing should occur."""
        if rebalance_frequency == "never":
            return False
        
        days_since_rebalance = (current_date - last_rebalance).days
        
        if rebalance_frequency == "monthly":
            return days_since_rebalance >= 30
        elif rebalance_frequency == "quarterly":
            return days_since_rebalance >= 90
        elif rebalance_frequency == "annually":
            return days_since_rebalance >= 365
        
        return False
    
    def _calculate_backtest_metrics(
        self,
        backtest_results: Dict[str, Any],
        initial_investment: float
    ) -> Dict[str, Any]:
        """Calculate performance metrics from backtest results."""
        daily_values = backtest_results["daily_values"]
        final_value = daily_values[-1]["value"]
        
        total_return = final_value - initial_investment
        total_return_pct = (total_return / initial_investment) * 100
        
        # Calculate CAGR
        years = len(daily_values) / 252
        cagr = (math.pow(final_value / initial_investment, 1 / years) - 1) * 100 if years > 0 else 0
        
        # Calculate daily returns for Sharpe ratio
        daily_returns = []
        for i in range(1, len(daily_values)):
            daily_return = (daily_values[i]["value"] - daily_values[i-1]["value"]) / daily_values[i-1]["value"]
            daily_returns.append(daily_return)
        
        avg_daily_return = statistics.mean(daily_returns) if daily_returns else 0
        std_daily_return = statistics.stdev(daily_returns) if len(daily_returns) > 1 else 0
        
        # Sharpe ratio (assuming 2% risk-free rate)
        risk_free_daily = 0.02 / 252
        sharpe_ratio = ((avg_daily_return - risk_free_daily) / std_daily_return * math.sqrt(252)) if std_daily_return > 0 else 0
        
        # Annualized volatility
        annualized_vol = std_daily_return * math.sqrt(252) * 100
        
        return {
            "final_value": round(final_value, 2),
            "total_return": round(total_return, 2),
            "total_return_pct": round(total_return_pct, 2),
            "cagr_pct": round(cagr, 2),
            "annualized_volatility_pct": round(annualized_vol, 2),
            "sharpe_ratio": round(sharpe_ratio, 2),
            "best_day_return_pct": round(max(daily_returns) * 100, 2) if daily_returns else 0,
            "worst_day_return_pct": round(min(daily_returns) * 100, 2) if daily_returns else 0
        }
    
    def _calculate_risk_metrics(self, backtest_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate risk metrics from backtest results."""
        daily_values = backtest_results["daily_values"]
        
        # Calculate daily returns
        daily_returns = []
        for i in range(1, len(daily_values)):
            daily_return = (daily_values[i]["value"] - daily_values[i-1]["value"]) / daily_values[i-1]["value"]
            daily_returns.append(daily_return)
        
        # Downside returns (negative only)
        downside_returns = [r for r in daily_returns if r < 0]
        downside_volatility = statistics.stdev(downside_returns) * math.sqrt(252) * 100 if len(downside_returns) > 1 else 0
        
        # Sortino ratio
        avg_daily_return = statistics.mean(daily_returns) if daily_returns else 0
        risk_free_daily = 0.02 / 252
        sortino_ratio = ((avg_daily_return - risk_free_daily) / (statistics.stdev(downside_returns))) * math.sqrt(252) if len(downside_returns) > 1 else 0
        
        # Value at Risk (95% confidence)
        var_95 = sorted(daily_returns)[int(len(daily_returns) * 0.05)] * 100 if daily_returns else 0
        
        # Max drawdown
        peak = daily_values[0]["value"]
        max_dd = 0
        for val in daily_values:
            if val["value"] > peak:
                peak = val["value"]
            dd = ((val["value"] - peak) / peak) * 100
            if dd < max_dd:
                max_dd = dd
        
        return {
            "downside_volatility_pct": round(downside_volatility, 2),
            "sortino_ratio": round(sortino_ratio, 2),
            "value_at_risk_95_pct": round(var_95, 2),
            "max_drawdown_pct": round(max_dd, 2),
            "negative_days_pct": round((len(downside_returns) / len(daily_returns)) * 100, 2) if daily_returns else 0
        }
    
    def _analyze_rebalancing(
        self,
        portfolio: Dict[str, float],
        backtest_results: Dict[str, Any],
        rebalance_frequency: str
    ) -> Dict[str, Any]:
        """Analyze impact of rebalancing."""
        rebalance_dates = backtest_results["rebalance_dates"]
        
        return {
            "rebalance_count": len(rebalance_dates),
            "rebalance_frequency": rebalance_frequency,
            "avg_days_between_rebalances": round(252 / len(rebalance_dates), 1) if len(rebalance_dates) > 0 else 0,
            "interpretation": self._get_rebalancing_interpretation(rebalance_frequency, len(rebalance_dates))
        }
    
    def _get_rebalancing_interpretation(self, frequency: str, count: int) -> str:
        """Get interpretation of rebalancing strategy."""
        if frequency == "never":
            return "Buy and hold strategy - no rebalancing costs, may drift from target allocation"
        elif frequency == "monthly" and count > 0:
            return f"Frequent rebalancing ({count} times) - maintains target allocation, higher transaction costs"
        elif frequency == "quarterly" and count > 0:
            return f"Moderate rebalancing ({count} times) - balances allocation maintenance with transaction costs"
        elif frequency == "annually" and count > 0:
            return f"Minimal rebalancing ({count} times) - low transaction costs, may allow allocation drift"
        else:
            return "No rebalancing occurred during backtest period"
    
    # =========================================================================
    # MONTE CARLO SIMULATION HELPERS
    # =========================================================================
    
    def _get_etf_simulation_parameters(self, portfolio: Dict[str, float]) -> Dict[str, Dict]:
        """Get expected returns and volatility for Monte Carlo simulation."""
        parameters = {}
        
        for ticker in portfolio.keys():
            base_params = self._get_etf_base_parameters(ticker)
            parameters[ticker] = {
                "expected_return": base_params["annual_return"],
                "volatility": base_params["volatility"]
            }
        
        return parameters
    
    def _run_monte_carlo_simulations(
        self,
        portfolio: Dict[str, float],
        etf_parameters: Dict[str, Dict],
        initial_investment: float,
        years: int,
        simulations: int
    ) -> List[Dict[str, Any]]:
        """Run Monte Carlo simulations."""
        results = []
        
        for sim in range(simulations):
            portfolio_value = initial_investment
            annual_values = [initial_investment]
            
            for year in range(years):
                # Calculate portfolio return for the year
                portfolio_return = 0.0
                
                for ticker, weight in portfolio.items():
                    params = etf_parameters[ticker]
                    # Annual return: expected return + random shock
                    etf_return = random.gauss(
                        params["expected_return"],
                        params["volatility"]
                    )
                    portfolio_return += weight * etf_return
                
                portfolio_value *= (1 + portfolio_return)
                annual_values.append(portfolio_value)
            
            results.append({
                "simulation_id": sim + 1,
                "final_value": portfolio_value,
                "annual_values": annual_values
            })
        
        return results
    
    def _calculate_monte_carlo_statistics(
        self,
        simulation_results: List[Dict[str, Any]],
        confidence_level: float
    ) -> Dict[str, Any]:
        """Calculate statistics from Monte Carlo simulations."""
        final_values = [sim["final_value"] for sim in simulation_results]
        final_values.sort()
        
        # Calculate percentiles
        percentiles = {}
        for p in [5, 10, 25, 50, 75, 90, 95]:
            idx = int(len(final_values) * (p / 100))
            percentiles[f"p{p}"] = round(final_values[idx], 2)
        
        # Calculate statistics
        mean_value = statistics.mean(final_values)
        median_value = statistics.median(final_values)
        std_value = statistics.stdev(final_values)
        
        # Confidence interval
        lower_idx = int(len(final_values) * ((1 - confidence_level) / 2))
        upper_idx = int(len(final_values) * (confidence_level + (1 - confidence_level) / 2))
        
        return {
            "mean_final_value": round(mean_value, 2),
            "median_final_value": round(median_value, 2),
            "std_dev": round(std_value, 2),
            "min_final_value": round(min(final_values), 2),
            "max_final_value": round(max(final_values), 2),
            "percentiles": percentiles,
            "confidence_interval": {
                "lower_bound": round(final_values[lower_idx], 2),
                "upper_bound": round(final_values[upper_idx], 2),
                "confidence_level": confidence_level
            }
        }
    
    def _calculate_probability_metrics(
        self,
        simulation_results: List[Dict[str, Any]],
        initial_investment: float
    ) -> Dict[str, Any]:
        """Calculate probability metrics from simulations."""
        final_values = [sim["final_value"] for sim in simulation_results]
        
        # Probability of profit
        profitable_simulations = [v for v in final_values if v > initial_investment]
        prob_profit = (len(profitable_simulations) / len(final_values)) * 100
        
        # Probability of doubling
        doubled_simulations = [v for v in final_values if v >= initial_investment * 2]
        prob_double = (len(doubled_simulations) / len(final_values)) * 100
        
        # Probability of loss
        loss_simulations = [v for v in final_values if v < initial_investment]
        prob_loss = (len(loss_simulations) / len(final_values)) * 100
        
        # Probability of 50% loss
        major_loss_simulations = [v for v in final_values if v < initial_investment * 0.5]
        prob_major_loss = (len(major_loss_simulations) / len(final_values)) * 100
        
        return {
            "probability_of_profit_pct": round(prob_profit, 2),
            "probability_of_doubling_pct": round(prob_double, 2),
            "probability_of_loss_pct": round(prob_loss, 2),
            "probability_of_major_loss_pct": round(prob_major_loss, 2),
            "interpretation": self._get_probability_interpretation(prob_profit, prob_loss)
        }
    
    def _get_probability_interpretation(self, prob_profit: float, prob_loss: float) -> str:
        """Get interpretation of probability metrics."""
        if prob_profit >= 90:
            return "Very high probability of profit - portfolio has strong expected returns"
        elif prob_profit >= 75:
            return "High probability of profit - portfolio likely to generate positive returns"
        elif prob_profit >= 60:
            return "Moderate probability of profit - portfolio has reasonable upside potential"
        elif prob_profit >= 50:
            return "Balanced risk/reward - equal chance of profit or loss"
        else:
            return "Lower probability of profit - portfolio may face challenges"
    
    # =========================================================================
    # DRAWDOWN ANALYSIS HELPERS
    # =========================================================================
    
    def _calculate_portfolio_values(
        self,
        portfolio: Dict[str, float],
        price_history: Dict[str, List[Dict]],
        initial_investment: float
    ) -> List[Dict[str, Any]]:
        """Calculate portfolio values over time."""
        # Initialize holdings
        holdings = {}
        for ticker, weight in portfolio.items():
            initial_price = price_history[ticker][0]["price"]
            holdings[ticker] = (initial_investment * weight) / initial_price
        
        portfolio_values = []
        num_days = len(price_history[list(portfolio.keys())[0]])
        
        for day_idx in range(num_days):
            total_value = 0.0
            for ticker, shares in holdings.items():
                current_price = price_history[ticker][day_idx]["price"]
                total_value += shares * current_price
            
            date_str = price_history[list(portfolio.keys())[0]][day_idx]["date"]
            portfolio_values.append({
                "date": date_str,
                "value": total_value
            })
        
        return portfolio_values
    
    def _identify_drawdowns(self, portfolio_values: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify all drawdown periods."""
        drawdowns = []
        peak_value = portfolio_values[0]["value"]
        peak_date = portfolio_values[0]["date"]
        in_drawdown = False
        drawdown_start_idx = 0
        
        for idx, val in enumerate(portfolio_values):
            if val["value"] > peak_value:
                # New peak - end of drawdown if we were in one
                if in_drawdown:
                    trough_value = min(portfolio_values[drawdown_start_idx:idx], key=lambda x: x["value"])
                    trough_idx = next(i for i, v in enumerate(portfolio_values[drawdown_start_idx:idx], drawdown_start_idx) if v["value"] == trough_value["value"])
                    
                    drawdown_pct = ((trough_value["value"] - peak_value) / peak_value) * 100
                    recovery_days = idx - trough_idx
                    
                    drawdowns.append({
                        "peak_date": peak_date,
                        "trough_date": trough_value["date"],
                        "recovery_date": val["date"],
                        "peak_value": round(peak_value, 2),
                        "trough_value": round(trough_value["value"], 2),
                        "recovery_value": round(val["value"], 2),
                        "drawdown_pct": round(drawdown_pct, 2),
                        "duration_days": idx - drawdown_start_idx,
                        "recovery_days": recovery_days
                    })
                    
                    in_drawdown = False
                
                peak_value = val["value"]
                peak_date = val["date"]
            elif val["value"] < peak_value:
                # In drawdown
                if not in_drawdown:
                    in_drawdown = True
                    drawdown_start_idx = idx - 1
        
        # Sort by drawdown magnitude
        drawdowns.sort(key=lambda x: x["drawdown_pct"])
        
        return drawdowns
    
    def _calculate_drawdown_statistics(self, drawdowns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate statistics from drawdowns."""
        if not drawdowns:
            return {
                "max_drawdown_pct": 0,
                "avg_drawdown_pct": 0,
                "total_drawdowns": 0,
                "avg_duration_days": 0,
                "avg_recovery_days": 0
            }
        
        drawdown_pcts = [abs(dd["drawdown_pct"]) for dd in drawdowns]
        durations = [dd["duration_days"] for dd in drawdowns]
        recoveries = [dd["recovery_days"] for dd in drawdowns]
        
        return {
            "max_drawdown_pct": round(max(drawdown_pcts), 2),
            "avg_drawdown_pct": round(statistics.mean(drawdown_pcts), 2),
            "total_drawdowns": len(drawdowns),
            "avg_duration_days": round(statistics.mean(durations), 1),
            "avg_recovery_days": round(statistics.mean(recoveries), 1)
        }
    
    def _analyze_recovery_periods(
        self,
        drawdowns: List[Dict[str, Any]],
        portfolio_values: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze recovery periods from drawdowns."""
        if not drawdowns:
            return {
                "fastest_recovery_days": 0,
                "slowest_recovery_days": 0,
                "avg_recovery_days": 0
            }
        
        recovery_days = [dd["recovery_days"] for dd in drawdowns]
        
        return {
            "fastest_recovery_days": min(recovery_days),
            "slowest_recovery_days": max(recovery_days),
            "avg_recovery_days": round(statistics.mean(recovery_days), 1),
            "interpretation": self._get_recovery_interpretation(statistics.mean(recovery_days))
        }
    
    def _get_recovery_interpretation(self, avg_recovery_days: float) -> str:
        """Get interpretation of recovery periods."""
        if avg_recovery_days < 30:
            return "Quick recovery - portfolio bounces back rapidly from drawdowns"
        elif avg_recovery_days < 90:
            return "Moderate recovery - portfolio typically recovers within 3 months"
        elif avg_recovery_days < 180:
            return "Slower recovery - portfolio needs several months to recover"
        else:
            return "Extended recovery - portfolio takes significant time to reach new highs"
    
    def _analyze_underwater_periods(self, portfolio_values: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze periods when portfolio is below previous peak."""
        peak_value = portfolio_values[0]["value"]
        underwater_days = 0
        total_days = len(portfolio_values)
        
        for val in portfolio_values:
            if val["value"] > peak_value:
                peak_value = val["value"]
            elif val["value"] < peak_value:
                underwater_days += 1
        
        underwater_pct = (underwater_days / total_days) * 100
        
        return {
            "underwater_days": underwater_days,
            "total_days": total_days,
            "underwater_pct": round(underwater_pct, 2),
            "interpretation": self._get_underwater_interpretation(underwater_pct)
        }
    
    def _get_underwater_interpretation(self, underwater_pct: float) -> str:
        """Get interpretation of underwater periods."""
        if underwater_pct < 20:
            return "Portfolio spends most time at all-time highs - strong consistent performance"
        elif underwater_pct < 40:
            return "Portfolio frequently reaches new highs - good recovery characteristics"
        elif underwater_pct < 60:
            return "Portfolio spends moderate time below peaks - normal volatility patterns"
        else:
            return "Portfolio spends significant time in drawdown - challenging market conditions"
    
    def _get_current_drawdown(self, portfolio_values: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate current drawdown from most recent peak."""
        peak_value = max(v["value"] for v in portfolio_values)
        current_value = portfolio_values[-1]["value"]
        current_drawdown_pct = ((current_value - peak_value) / peak_value) * 100
        
        # Find peak date
        peak_date = next(v["date"] for v in portfolio_values if v["value"] == peak_value)
        
        return {
            "current_value": round(current_value, 2),
            "peak_value": round(peak_value, 2),
            "drawdown_pct": round(current_drawdown_pct, 2),
            "peak_date": peak_date,
            "status": "at_peak" if current_drawdown_pct >= -0.5 else "in_drawdown"
        }


# Singleton instance
etf_backtesting_service = ETFBacktestingService()
