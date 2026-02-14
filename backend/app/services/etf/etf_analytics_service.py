"""
ETF Advanced Analytics Service.

Provides momentum indicators, liquidity analysis, and smart beta factor scoring
for ETF evaluation and selection.

Phase 13 Features:
1. Momentum Indicators - RSI, MACD, moving averages
2. Liquidity Analysis - Volume, spreads, AUM trends
3. Smart Beta Factors - Value, momentum, quality, low-volatility
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import statistics
import math

from app.core.logging_config import get_logger

logger = get_logger(__name__)


class ETFAdvancedAnalyticsService:
    """
    Advanced analytics for ETF evaluation.
    
    Provides technical indicators, liquidity metrics, and factor-based
    scoring to help investors make data-driven ETF selection decisions.
    """
    
    def __init__(self):
        """Initialize ETF advanced analytics service."""
        logger.info("ETF Advanced Analytics Service initialized")
    
    
    # ========================================================================
    # METHOD 1: Momentum Indicators (RSI, MACD, Moving Averages)
    # ========================================================================
    
    async def get_momentum_indicators(
        self,
        ticker: str,
        period: str = "6m"
    ) -> Dict[str, Any]:
        """
        Calculate momentum indicators for an ETF.
        
        Provides RSI (Relative Strength Index), MACD (Moving Average 
        Convergence Divergence), and multiple moving averages to assess
        price momentum and trend strength.
        
        Args:
            ticker: ETF ticker symbol
            period: Analysis period (1m, 3m, 6m, 1y, 2y)
            
        Returns:
            Dict containing:
            - rsi: Current RSI value (0-100)
            - rsi_signal: Overbought/oversold/neutral
            - macd: MACD indicator values
            - moving_averages: SMA and EMA values
            - trend_analysis: Overall trend assessment
            - momentum_score: Composite momentum score (0-100)
        """
        try:
            logger.info(
                "Calculating momentum indicators",
                extra={"ticker": ticker, "period": period}
            )
            
            # Get sample price data
            price_data = self._get_sample_price_data(ticker, period)
            
            # Calculate RSI
            rsi_value = self._calculate_rsi(price_data["prices"])
            rsi_signal = self._interpret_rsi(rsi_value)
            
            # Calculate MACD
            macd_data = self._calculate_macd(price_data["prices"])
            
            # Calculate moving averages
            moving_averages = self._calculate_moving_averages(price_data["prices"])
            
            # Trend analysis
            trend = self._analyze_trend(
                price_data["prices"],
                moving_averages
            )
            
            # Composite momentum score
            momentum_score = self._calculate_momentum_score(
                rsi_value,
                macd_data,
                moving_averages,
                trend
            )
            
            result = {
                "ticker": ticker,
                "period": period,
                "price_data": {
                    "current_price": price_data["current_price"],
                    "period_high": price_data["high"],
                    "period_low": price_data["low"],
                    "price_change_pct": price_data["change_pct"],
                    "data_points": len(price_data["prices"])
                },
                "rsi": {
                    "value": round(rsi_value, 2),
                    "signal": rsi_signal,
                    "interpretation": self._get_rsi_interpretation(rsi_signal)
                },
                "macd": {
                    "macd_line": round(macd_data["macd"], 4),
                    "signal_line": round(macd_data["signal"], 4),
                    "histogram": round(macd_data["histogram"], 4),
                    "signal": macd_data["signal_type"],
                    "interpretation": self._get_macd_interpretation(macd_data["signal_type"])
                },
                "moving_averages": {
                    "sma_20": round(moving_averages["sma_20"], 2),
                    "sma_50": round(moving_averages["sma_50"], 2),
                    "sma_200": round(moving_averages["sma_200"], 2),
                    "ema_12": round(moving_averages["ema_12"], 2),
                    "ema_26": round(moving_averages["ema_26"], 2),
                    "golden_cross": moving_averages["golden_cross"],
                    "death_cross": moving_averages["death_cross"]
                },
                "trend_analysis": {
                    "short_term": trend["short_term"],
                    "medium_term": trend["medium_term"],
                    "long_term": trend["long_term"],
                    "overall_trend": trend["overall"],
                    "trend_strength": trend["strength"]
                },
                "momentum_score": {
                    "value": round(momentum_score, 1),
                    "rating": self._get_momentum_rating(momentum_score),
                    "interpretation": self._get_momentum_interpretation(momentum_score)
                },
                "trading_signals": self._generate_trading_signals(
                    rsi_value,
                    macd_data,
                    moving_averages,
                    trend
                ),
                "calculation_timestamp": datetime.now().isoformat()
            }
            
            logger.info(
                "Momentum indicators calculated",
                extra={
                    "ticker": ticker,
                    "momentum_score": momentum_score,
                    "rsi": rsi_value,
                    "trend": trend["overall"]
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(
                "Failed to calculate momentum indicators",
                extra={"ticker": ticker, "error": str(e)},
                exc_info=True
            )
            raise
    
    
    # ========================================================================
    # METHOD 2: Liquidity Analysis (Volume, Spreads, AUM Trends)
    # ========================================================================
    
    async def analyze_liquidity(
        self,
        ticker: str,
        period: str = "3m"
    ) -> Dict[str, Any]:
        """
        Analyze ETF liquidity metrics.
        
        Evaluates trading volume, bid-ask spreads, AUM flows, and overall
        liquidity to assess ease of trading and market depth.
        
        Args:
            ticker: ETF ticker symbol
            period: Analysis period (1m, 3m, 6m, 1y)
            
        Returns:
            Dict containing:
            - volume_metrics: Trading volume statistics
            - spread_analysis: Bid-ask spread data
            - aum_trends: AUM growth/decline trends
            - liquidity_score: Composite liquidity score (0-100)
            - liquidity_rating: Excellent/Good/Fair/Poor
        """
        try:
            logger.info(
                "Analyzing liquidity metrics",
                extra={"ticker": ticker, "period": period}
            )
            
            # Get sample liquidity data
            liquidity_data = self._get_sample_liquidity_data(ticker, period)
            
            # Volume analysis
            volume_metrics = self._analyze_volume(liquidity_data["volume"])
            
            # Spread analysis
            spread_metrics = self._analyze_spreads(liquidity_data["spreads"])
            
            # AUM trends
            aum_analysis = self._analyze_aum_trends(liquidity_data["aum"])
            
            # Liquidity score
            liquidity_score = self._calculate_liquidity_score(
                volume_metrics,
                spread_metrics,
                aum_analysis
            )
            
            result = {
                "ticker": ticker,
                "period": period,
                "volume_metrics": {
                    "avg_daily_volume": volume_metrics["avg_volume"],
                    "current_volume": volume_metrics["current_volume"],
                    "volume_trend": volume_metrics["trend"],
                    "volume_volatility": round(volume_metrics["volatility"], 2),
                    "high_volume_days_pct": round(volume_metrics["high_volume_pct"], 1),
                    "volume_score": round(volume_metrics["score"], 1)
                },
                "spread_analysis": {
                    "avg_spread_bps": round(spread_metrics["avg_spread"], 2),
                    "current_spread_bps": round(spread_metrics["current_spread"], 2),
                    "spread_volatility": round(spread_metrics["volatility"], 2),
                    "tight_spread_days_pct": round(spread_metrics["tight_spread_pct"], 1),
                    "spread_score": round(spread_metrics["score"], 1),
                    "interpretation": self._interpret_spread(spread_metrics["avg_spread"])
                },
                "aum_trends": {
                    "current_aum_millions": aum_analysis["current_aum"],
                    "period_flow_millions": aum_analysis["period_flow"],
                    "flow_pct": round(aum_analysis["flow_pct"], 2),
                    "trend": aum_analysis["trend"],
                    "consistency": aum_analysis["consistency"],
                    "aum_score": round(aum_analysis["score"], 1)
                },
                "liquidity_score": {
                    "value": round(liquidity_score, 1),
                    "rating": self._get_liquidity_rating(liquidity_score),
                    "interpretation": self._get_liquidity_interpretation(liquidity_score)
                },
                "trading_recommendations": self._generate_liquidity_recommendations(
                    volume_metrics,
                    spread_metrics,
                    aum_analysis,
                    liquidity_score
                ),
                "calculation_timestamp": datetime.now().isoformat()
            }
            
            logger.info(
                "Liquidity analysis completed",
                extra={
                    "ticker": ticker,
                    "liquidity_score": liquidity_score,
                    "volume": volume_metrics["avg_volume"],
                    "spread_bps": spread_metrics["avg_spread"]
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(
                "Failed to analyze liquidity",
                extra={"ticker": ticker, "error": str(e)},
                exc_info=True
            )
            raise
    
    
    # ========================================================================
    # METHOD 3: Smart Beta Factor Analysis (Value, Momentum, Quality, Low-Vol)
    # ========================================================================
    
    async def analyze_smart_beta_factors(
        self,
        ticker: str
    ) -> Dict[str, Any]:
        """
        Analyze smart beta factor exposures.
        
        Evaluates ETF exposure to systematic factors like value, momentum,
        quality, and low-volatility to understand return drivers and risk.
        
        Args:
            ticker: ETF ticker symbol
            
        Returns:
            Dict containing:
            - value_factor: Value score and metrics
            - momentum_factor: Momentum score and metrics
            - quality_factor: Quality score and metrics
            - low_volatility_factor: Low-vol score and metrics
            - size_factor: Size (large/mid/small cap) exposure
            - composite_score: Overall factor score
            - factor_tilt: Primary factor exposure
        """
        try:
            logger.info(
                "Analyzing smart beta factors",
                extra={"ticker": ticker}
            )
            
            # Get sample factor data
            factor_data = self._get_sample_factor_data(ticker)
            
            # Value factor analysis
            value_factor = self._analyze_value_factor(factor_data)
            
            # Momentum factor analysis
            momentum_factor = self._analyze_momentum_factor(factor_data)
            
            # Quality factor analysis
            quality_factor = self._analyze_quality_factor(factor_data)
            
            # Low-volatility factor analysis
            low_vol_factor = self._analyze_low_volatility_factor(factor_data)
            
            # Size factor analysis
            size_factor = self._analyze_size_factor(factor_data)
            
            # Composite factor score
            composite_score = self._calculate_composite_factor_score(
                value_factor,
                momentum_factor,
                quality_factor,
                low_vol_factor
            )
            
            # Determine primary factor tilt
            primary_tilt = self._determine_primary_tilt(
                value_factor,
                momentum_factor,
                quality_factor,
                low_vol_factor
            )
            
            result = {
                "ticker": ticker,
                "etf_type": factor_data["etf_type"],
                "value_factor": {
                    "score": round(value_factor["score"], 1),
                    "rating": value_factor["rating"],
                    "metrics": {
                        "avg_pe_ratio": round(value_factor["pe_ratio"], 2),
                        "avg_pb_ratio": round(value_factor["pb_ratio"], 2),
                        "dividend_yield_pct": round(value_factor["div_yield"], 2)
                    },
                    "interpretation": value_factor["interpretation"]
                },
                "momentum_factor": {
                    "score": round(momentum_factor["score"], 1),
                    "rating": momentum_factor["rating"],
                    "metrics": {
                        "returns_12m_pct": round(momentum_factor["returns_12m"], 2),
                        "returns_6m_pct": round(momentum_factor["returns_6m"], 2),
                        "price_momentum": round(momentum_factor["price_momentum"], 2)
                    },
                    "interpretation": momentum_factor["interpretation"]
                },
                "quality_factor": {
                    "score": round(quality_factor["score"], 1),
                    "rating": quality_factor["rating"],
                    "metrics": {
                        "avg_roe_pct": round(quality_factor["roe"], 2),
                        "avg_debt_to_equity": round(quality_factor["debt_equity"], 2),
                        "earnings_stability": round(quality_factor["earnings_stability"], 2)
                    },
                    "interpretation": quality_factor["interpretation"]
                },
                "low_volatility_factor": {
                    "score": round(low_vol_factor["score"], 1),
                    "rating": low_vol_factor["rating"],
                    "metrics": {
                        "volatility_pct": round(low_vol_factor["volatility"], 2),
                        "beta": round(low_vol_factor["beta"], 2),
                        "max_drawdown_pct": round(low_vol_factor["max_drawdown"], 2)
                    },
                    "interpretation": low_vol_factor["interpretation"]
                },
                "size_factor": {
                    "primary_exposure": size_factor["primary"],
                    "market_cap_breakdown": {
                        "large_cap_pct": round(size_factor["large_cap"], 1),
                        "mid_cap_pct": round(size_factor["mid_cap"], 1),
                        "small_cap_pct": round(size_factor["small_cap"], 1)
                    },
                    "avg_market_cap_millions": size_factor["avg_market_cap"]
                },
                "composite_analysis": {
                    "overall_score": round(composite_score, 1),
                    "rating": self._get_factor_rating(composite_score),
                    "primary_factor_tilt": primary_tilt["factor"],
                    "tilt_strength": primary_tilt["strength"],
                    "factor_diversification": self._calculate_factor_diversification(
                        value_factor,
                        momentum_factor,
                        quality_factor,
                        low_vol_factor
                    )
                },
                "investment_characteristics": self._describe_investment_characteristics(
                    primary_tilt,
                    value_factor,
                    momentum_factor,
                    quality_factor,
                    low_vol_factor
                ),
                "comparison_to_market": self._compare_to_market_factors(
                    value_factor,
                    momentum_factor,
                    quality_factor,
                    low_vol_factor
                ),
                "calculation_timestamp": datetime.now().isoformat()
            }
            
            logger.info(
                "Smart beta factor analysis completed",
                extra={
                    "ticker": ticker,
                    "composite_score": composite_score,
                    "primary_tilt": primary_tilt["factor"]
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(
                "Failed to analyze smart beta factors",
                extra={"ticker": ticker, "error": str(e)},
                exc_info=True
            )
            raise
    
    
    # ========================================================================
    # HELPER METHODS: Momentum Indicators
    # ========================================================================
    
    def _get_sample_price_data(self, ticker: str, period: str) -> Dict:
        """Generate sample price data for momentum calculations."""
        # In production, fetch from StockHistoricalPrice collection
        
        period_days = {
            "1m": 30,
            "3m": 90,
            "6m": 180,
            "1y": 365,
            "2y": 730
        }
        
        days = period_days.get(period, 180)
        
        # Sample prices with realistic variation
        base_price = 150.0
        prices = []
        
        for i in range(days):
            # Simulate trending price with noise
            trend = (i / days) * 10  # Upward trend
            noise = (hash(f"{ticker}{i}") % 100 - 50) / 10  # Random noise
            price = base_price + trend + noise
            prices.append(price)
        
        current_price = prices[-1]
        high = max(prices)
        low = min(prices)
        change_pct = ((current_price - prices[0]) / prices[0]) * 100
        
        return {
            "prices": prices,
            "current_price": current_price,
            "high": high,
            "low": low,
            "change_pct": change_pct
        }
    
    def _calculate_rsi(self, prices: List[float]) -> float:
        """Calculate Relative Strength Index (RSI)."""
        if len(prices) < 14:
            return 50.0  # Neutral if insufficient data
        
        # Calculate price changes
        changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        # Separate gains and losses
        gains = [change if change > 0 else 0 for change in changes]
        losses = [abs(change) if change < 0 else 0 for change in changes]
        
        # Calculate average gains and losses (14-period)
        avg_gain = sum(gains[-14:]) / 14
        avg_loss = sum(losses[-14:]) / 14
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _interpret_rsi(self, rsi: float) -> str:
        """Interpret RSI value."""
        if rsi >= 70:
            return "overbought"
        elif rsi <= 30:
            return "oversold"
        else:
            return "neutral"
    
    def _get_rsi_interpretation(self, signal: str) -> str:
        """Get RSI interpretation text."""
        interpretations = {
            "overbought": "RSI above 70 suggests the ETF may be overvalued and due for a pullback",
            "oversold": "RSI below 30 suggests the ETF may be undervalued and due for a bounce",
            "neutral": "RSI between 30-70 indicates balanced momentum without extreme conditions"
        }
        return interpretations.get(signal, "")
    
    def _calculate_macd(self, prices: List[float]) -> Dict:
        """Calculate MACD (Moving Average Convergence Divergence)."""
        if len(prices) < 26:
            return {
                "macd": 0.0,
                "signal": 0.0,
                "histogram": 0.0,
                "signal_type": "neutral"
            }
        
        # Calculate EMAs
        ema_12 = self._calculate_ema(prices, 12)
        ema_26 = self._calculate_ema(prices, 26)
        
        # MACD line
        macd = ema_12 - ema_26
        
        # Signal line (9-period EMA of MACD)
        # Simplified: use average for demo
        signal = macd * 0.9
        
        # Histogram
        histogram = macd - signal
        
        # Determine signal
        if histogram > 0 and macd > signal:
            signal_type = "bullish"
        elif histogram < 0 and macd < signal:
            signal_type = "bearish"
        else:
            signal_type = "neutral"
        
        return {
            "macd": macd,
            "signal": signal,
            "histogram": histogram,
            "signal_type": signal_type
        }
    
    def _get_macd_interpretation(self, signal_type: str) -> str:
        """Get MACD interpretation text."""
        interpretations = {
            "bullish": "MACD above signal line indicates positive momentum and potential uptrend",
            "bearish": "MACD below signal line indicates negative momentum and potential downtrend",
            "neutral": "MACD near signal line suggests consolidation or trend reversal"
        }
        return interpretations.get(signal_type, "")
    
    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """Calculate Exponential Moving Average."""
        if len(prices) < period:
            return sum(prices) / len(prices)
        
        multiplier = 2 / (period + 1)
        ema = sum(prices[:period]) / period
        
        for price in prices[period:]:
            ema = (price - ema) * multiplier + ema
        
        return ema
    
    def _calculate_moving_averages(self, prices: List[float]) -> Dict:
        """Calculate multiple moving averages."""
        current_price = prices[-1]
        
        sma_20 = sum(prices[-20:]) / min(20, len(prices))
        sma_50 = sum(prices[-50:]) / min(50, len(prices))
        sma_200 = sum(prices[-200:]) / min(200, len(prices)) if len(prices) >= 200 else current_price
        
        ema_12 = self._calculate_ema(prices, 12)
        ema_26 = self._calculate_ema(prices, 26)
        
        # Golden cross: 50 SMA crosses above 200 SMA
        golden_cross = sma_50 > sma_200 and len(prices) >= 200
        
        # Death cross: 50 SMA crosses below 200 SMA
        death_cross = sma_50 < sma_200 and len(prices) >= 200
        
        return {
            "sma_20": sma_20,
            "sma_50": sma_50,
            "sma_200": sma_200,
            "ema_12": ema_12,
            "ema_26": ema_26,
            "golden_cross": golden_cross,
            "death_cross": death_cross
        }
    
    def _analyze_trend(self, prices: List[float], moving_averages: Dict) -> Dict:
        """Analyze price trend."""
        current_price = prices[-1]
        
        # Short-term trend (vs 20-day SMA)
        short_term = "bullish" if current_price > moving_averages["sma_20"] else "bearish"
        
        # Medium-term trend (vs 50-day SMA)
        medium_term = "bullish" if current_price > moving_averages["sma_50"] else "bearish"
        
        # Long-term trend (vs 200-day SMA)
        long_term = "bullish" if current_price > moving_averages["sma_200"] else "bearish"
        
        # Overall trend
        bullish_count = sum([
            short_term == "bullish",
            medium_term == "bullish",
            long_term == "bullish"
        ])
        
        if bullish_count >= 2:
            overall = "bullish"
            strength = "strong" if bullish_count == 3 else "moderate"
        elif bullish_count == 1:
            overall = "neutral"
            strength = "weak"
        else:
            overall = "bearish"
            strength = "strong"
        
        return {
            "short_term": short_term,
            "medium_term": medium_term,
            "long_term": long_term,
            "overall": overall,
            "strength": strength
        }
    
    def _calculate_momentum_score(
        self,
        rsi: float,
        macd: Dict,
        moving_averages: Dict,
        trend: Dict
    ) -> float:
        """Calculate composite momentum score (0-100)."""
        # RSI component (0-40 points)
        if 40 <= rsi <= 60:
            rsi_score = 40  # Neutral is best
        elif rsi > 60:
            rsi_score = 40 - (rsi - 60)  # Penalize overbought
        else:
            rsi_score = 40 - (40 - rsi)  # Penalize oversold
        
        # MACD component (0-30 points)
        macd_score = 30 if macd["signal_type"] == "bullish" else (15 if macd["signal_type"] == "neutral" else 0)
        
        # Trend component (0-30 points)
        trend_scores = {"bullish": 30, "neutral": 15, "bearish": 0}
        trend_score = trend_scores.get(trend["overall"], 15)
        
        total_score = max(0, min(100, rsi_score + macd_score + trend_score))
        
        return total_score
    
    def _get_momentum_rating(self, score: float) -> str:
        """Get momentum rating from score."""
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Fair"
        else:
            return "Poor"
    
    def _get_momentum_interpretation(self, score: float) -> str:
        """Get momentum interpretation."""
        if score >= 80:
            return "Strong positive momentum with bullish indicators across multiple timeframes"
        elif score >= 60:
            return "Positive momentum with favorable technical indicators"
        elif score >= 40:
            return "Neutral momentum with mixed signals"
        else:
            return "Weak momentum with bearish indicators"
    
    def _generate_trading_signals(
        self,
        rsi: float,
        macd: Dict,
        moving_averages: Dict,
        trend: Dict
    ) -> List[str]:
        """Generate trading signals based on indicators."""
        signals = []
        
        if rsi <= 30:
            signals.append("RSI oversold - potential buying opportunity")
        elif rsi >= 70:
            signals.append("RSI overbought - consider taking profits")
        
        if macd["signal_type"] == "bullish":
            signals.append("MACD bullish crossover - positive momentum")
        elif macd["signal_type"] == "bearish":
            signals.append("MACD bearish crossover - negative momentum")
        
        if moving_averages["golden_cross"]:
            signals.append("Golden cross detected - bullish long-term signal")
        elif moving_averages["death_cross"]:
            signals.append("Death cross detected - bearish long-term signal")
        
        if trend["overall"] == "bullish" and trend["strength"] == "strong":
            signals.append("Strong uptrend across all timeframes")
        elif trend["overall"] == "bearish" and trend["strength"] == "strong":
            signals.append("Strong downtrend - exercise caution")
        
        if not signals:
            signals.append("No strong signals - market in consolidation phase")
        
        return signals
    
    
    # ========================================================================
    # HELPER METHODS: Liquidity Analysis
    # ========================================================================
    
    def _get_sample_liquidity_data(self, ticker: str, period: str) -> Dict:
        """Generate sample liquidity data."""
        # In production, fetch from IntradayPrice and ETFProfile collections
        
        period_days = {
            "1m": 30,
            "3m": 90,
            "6m": 180,
            "1y": 365
        }
        
        days = period_days.get(period, 90)
        
        # Sample volume data
        base_volume = 5000000  # 5M shares/day
        volumes = []
        for i in range(days):
            noise = (hash(f"{ticker}vol{i}") % 40 - 20) / 100
            volume = base_volume * (1 + noise)
            volumes.append(int(volume))
        
        # Sample spread data (in basis points)
        spreads = []
        for i in range(days):
            noise = (hash(f"{ticker}spread{i}") % 10) / 100
            spread = 5 + noise  # ~5 bps average
            spreads.append(spread)
        
        # Sample AUM data (in millions)
        base_aum = 10000  # $10B
        aum_values = []
        for i in range(days):
            growth = (i / days) * 0.05  # 5% growth over period
            aum = base_aum * (1 + growth)
            aum_values.append(aum)
        
        return {
            "volume": volumes,
            "spreads": spreads,
            "aum": aum_values
        }
    
    def _analyze_volume(self, volumes: List[int]) -> Dict:
        """Analyze volume metrics."""
        avg_volume = sum(volumes) / len(volumes)
        current_volume = volumes[-1]
        
        # Volume trend
        first_half = sum(volumes[:len(volumes)//2]) / (len(volumes)//2)
        second_half = sum(volumes[len(volumes)//2:]) / (len(volumes) - len(volumes)//2)
        trend = "increasing" if second_half > first_half else "decreasing"
        
        # Volatility
        volatility = statistics.stdev(volumes) / avg_volume if len(volumes) > 1 else 0
        
        # High volume days
        high_threshold = avg_volume * 1.5
        high_volume_days = sum(1 for v in volumes if v > high_threshold)
        high_volume_pct = (high_volume_days / len(volumes)) * 100
        
        # Volume score (0-100)
        if avg_volume > 10000000:  # >10M
            base_score = 100
        elif avg_volume > 5000000:  # 5-10M
            base_score = 80
        elif avg_volume > 1000000:  # 1-5M
            base_score = 60
        else:
            base_score = 40
        
        # Adjust for consistency
        consistency_penalty = volatility * 20
        score = max(0, base_score - consistency_penalty)
        
        return {
            "avg_volume": int(avg_volume),
            "current_volume": current_volume,
            "trend": trend,
            "volatility": volatility,
            "high_volume_pct": high_volume_pct,
            "score": score
        }
    
    def _analyze_spreads(self, spreads: List[float]) -> Dict:
        """Analyze bid-ask spread metrics."""
        avg_spread = sum(spreads) / len(spreads)
        current_spread = spreads[-1]
        
        # Spread volatility
        volatility = statistics.stdev(spreads) / avg_spread if len(spreads) > 1 else 0
        
        # Tight spread days (< 5 bps)
        tight_threshold = 5.0
        tight_days = sum(1 for s in spreads if s < tight_threshold)
        tight_spread_pct = (tight_days / len(spreads)) * 100
        
        # Spread score (0-100)
        if avg_spread < 3:  # Very tight
            base_score = 100
        elif avg_spread < 5:  # Tight
            base_score = 80
        elif avg_spread < 10:  # Moderate
            base_score = 60
        else:  # Wide
            base_score = 40
        
        # Adjust for consistency
        consistency_penalty = volatility * 20
        score = max(0, base_score - consistency_penalty)
        
        return {
            "avg_spread": avg_spread,
            "current_spread": current_spread,
            "volatility": volatility,
            "tight_spread_pct": tight_spread_pct,
            "score": score
        }
    
    def _interpret_spread(self, spread_bps: float) -> str:
        """Interpret spread value."""
        if spread_bps < 3:
            return "Very tight spread - excellent liquidity"
        elif spread_bps < 5:
            return "Tight spread - good liquidity"
        elif spread_bps < 10:
            return "Moderate spread - adequate liquidity"
        else:
            return "Wide spread - lower liquidity"
    
    def _analyze_aum_trends(self, aum_values: List[float]) -> Dict:
        """Analyze AUM trends."""
        current_aum = aum_values[-1]
        start_aum = aum_values[0]
        
        # Period flow
        period_flow = current_aum - start_aum
        flow_pct = (period_flow / start_aum) * 100
        
        # Trend
        if flow_pct > 5:
            trend = "strong_inflow"
        elif flow_pct > 0:
            trend = "inflow"
        elif flow_pct > -5:
            trend = "outflow"
        else:
            trend = "strong_outflow"
        
        # Consistency (less volatility is better)
        changes = [aum_values[i] - aum_values[i-1] for i in range(1, len(aum_values))]
        consistency = 100 - (statistics.stdev(changes) / start_aum * 100) if len(changes) > 1 else 50
        consistency = max(0, min(100, consistency))
        
        # AUM score
        if trend in ["strong_inflow", "inflow"]:
            base_score = 80
        elif trend == "outflow":
            base_score = 50
        else:
            base_score = 30
        
        # Adjust for consistency
        score = (base_score + consistency) / 2
        
        return {
            "current_aum": int(current_aum),
            "period_flow": int(period_flow),
            "flow_pct": flow_pct,
            "trend": trend,
            "consistency": round(consistency, 1),
            "score": score
        }
    
    def _calculate_liquidity_score(
        self,
        volume_metrics: Dict,
        spread_metrics: Dict,
        aum_analysis: Dict
    ) -> float:
        """Calculate composite liquidity score (0-100)."""
        # Weighted average
        volume_weight = 0.4
        spread_weight = 0.4
        aum_weight = 0.2
        
        score = (
            volume_metrics["score"] * volume_weight +
            spread_metrics["score"] * spread_weight +
            aum_analysis["score"] * aum_weight
        )
        
        return score
    
    def _get_liquidity_rating(self, score: float) -> str:
        """Get liquidity rating from score."""
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Fair"
        else:
            return "Poor"
    
    def _get_liquidity_interpretation(self, score: float) -> str:
        """Get liquidity interpretation."""
        if score >= 80:
            return "Highly liquid with tight spreads and strong volume - ideal for large trades"
        elif score >= 60:
            return "Good liquidity suitable for most investors"
        elif score >= 40:
            return "Adequate liquidity but may have higher trading costs"
        else:
            return "Lower liquidity - best suited for buy-and-hold strategies"
    
    def _generate_liquidity_recommendations(
        self,
        volume_metrics: Dict,
        spread_metrics: Dict,
        aum_analysis: Dict,
        liquidity_score: float
    ) -> List[str]:
        """Generate liquidity-based recommendations."""
        recommendations = []
        
        if volume_metrics["score"] < 50:
            recommendations.append("Consider limit orders due to lower trading volume")
        
        if spread_metrics["avg_spread"] > 10:
            recommendations.append("Wide spreads may increase trading costs - avoid market orders")
        
        if aum_analysis["trend"] == "strong_outflow":
            recommendations.append("Significant outflows detected - monitor for potential closure")
        elif aum_analysis["trend"] == "strong_inflow":
            recommendations.append("Strong inflows indicate growing investor interest")
        
        if liquidity_score >= 80:
            recommendations.append("Excellent liquidity suitable for all trading strategies")
        elif liquidity_score < 40:
            recommendations.append("Lower liquidity - best for long-term buy-and-hold")
        
        if not recommendations:
            recommendations.append("Standard liquidity - suitable for most investors")
        
        return recommendations
    
    
    # ========================================================================
    # HELPER METHODS: Smart Beta Factor Analysis
    # ========================================================================
    
    def _get_sample_factor_data(self, ticker: str) -> Dict:
        """Generate sample factor data for ETF."""
        # In production, calculate from StockQuote holdings
        
        # Determine ETF type based on ticker
        etf_types = {
            "VOO": "broad_market",
            "VTV": "value",
            "VUG": "growth",
            "MTUM": "momentum",
            "QUAL": "quality",
            "USMV": "low_volatility"
        }
        
        etf_type = etf_types.get(ticker, "broad_market")
        
        # Base metrics vary by type
        base_metrics = {
            "broad_market": {
                "pe_ratio": 20.5,
                "pb_ratio": 3.2,
                "div_yield": 1.5,
                "returns_12m": 12.0,
                "returns_6m": 7.5,
                "roe": 18.0,
                "debt_equity": 1.5,
                "volatility": 15.0,
                "beta": 1.0,
                "large_cap": 75.0,
                "mid_cap": 20.0,
                "small_cap": 5.0
            },
            "value": {
                "pe_ratio": 15.0,
                "pb_ratio": 1.8,
                "div_yield": 2.8,
                "returns_12m": 8.5,
                "returns_6m": 5.0,
                "roe": 16.0,
                "debt_equity": 1.8,
                "volatility": 14.0,
                "beta": 0.95,
                "large_cap": 80.0,
                "mid_cap": 15.0,
                "small_cap": 5.0
            },
            "growth": {
                "pe_ratio": 28.0,
                "pb_ratio": 5.5,
                "div_yield": 0.8,
                "returns_12m": 18.0,
                "returns_6m": 12.0,
                "roe": 22.0,
                "debt_equity": 1.2,
                "volatility": 18.0,
                "beta": 1.1,
                "large_cap": 70.0,
                "mid_cap": 25.0,
                "small_cap": 5.0
            },
            "momentum": {
                "pe_ratio": 22.0,
                "pb_ratio": 3.8,
                "div_yield": 1.2,
                "returns_12m": 20.0,
                "returns_6m": 15.0,
                "roe": 19.0,
                "debt_equity": 1.4,
                "volatility": 17.0,
                "beta": 1.05,
                "large_cap": 65.0,
                "mid_cap": 30.0,
                "small_cap": 5.0
            },
            "quality": {
                "pe_ratio": 24.0,
                "pb_ratio": 4.2,
                "div_yield": 2.0,
                "returns_12m": 14.0,
                "returns_6m": 8.5,
                "roe": 25.0,
                "debt_equity": 0.8,
                "volatility": 13.0,
                "beta": 0.92,
                "large_cap": 85.0,
                "mid_cap": 12.0,
                "small_cap": 3.0
            },
            "low_volatility": {
                "pe_ratio": 18.0,
                "pb_ratio": 2.5,
                "div_yield": 2.5,
                "returns_12m": 10.0,
                "returns_6m": 6.0,
                "roe": 17.0,
                "debt_equity": 1.3,
                "volatility": 10.0,
                "beta": 0.75,
                "large_cap": 90.0,
                "mid_cap": 8.0,
                "small_cap": 2.0
            }
        }
        
        metrics = base_metrics.get(etf_type, base_metrics["broad_market"])
        metrics["etf_type"] = etf_type
        
        return metrics
    
    def _analyze_value_factor(self, factor_data: Dict) -> Dict:
        """Analyze value factor exposure."""
        pe_ratio = factor_data["pe_ratio"]
        pb_ratio = factor_data["pb_ratio"]
        div_yield = factor_data["div_yield"]
        
        # Value score (0-100, lower valuations = higher score)
        pe_score = max(0, 100 - (pe_ratio - 10) * 3)
        pb_score = max(0, 100 - (pb_ratio - 1) * 20)
        div_score = min(100, div_yield * 20)
        
        value_score = (pe_score + pb_score + div_score) / 3
        
        # Rating
        if value_score >= 70:
            rating = "Strong Value"
        elif value_score >= 50:
            rating = "Moderate Value"
        else:
            rating = "Growth/Neutral"
        
        # Interpretation
        if value_score >= 70:
            interpretation = "Strong value characteristics with attractive valuations"
        elif value_score >= 50:
            interpretation = "Moderate value tilt with reasonable valuations"
        else:
            interpretation = "Limited value exposure, higher growth orientation"
        
        return {
            "score": value_score,
            "rating": rating,
            "pe_ratio": pe_ratio,
            "pb_ratio": pb_ratio,
            "div_yield": div_yield,
            "interpretation": interpretation
        }
    
    def _analyze_momentum_factor(self, factor_data: Dict) -> Dict:
        """Analyze momentum factor exposure."""
        returns_12m = factor_data["returns_12m"]
        returns_6m = factor_data["returns_6m"]
        
        # Momentum score (0-100)
        momentum_12m = min(100, returns_12m * 5)
        momentum_6m = min(100, returns_6m * 8)
        price_momentum = (momentum_12m + momentum_6m) / 2
        
        momentum_score = price_momentum
        
        # Rating
        if momentum_score >= 70:
            rating = "Strong Momentum"
        elif momentum_score >= 50:
            rating = "Moderate Momentum"
        else:
            rating = "Low Momentum"
        
        # Interpretation
        if momentum_score >= 70:
            interpretation = "Strong price momentum with consistent positive returns"
        elif momentum_score >= 50:
            interpretation = "Moderate momentum with positive trend"
        else:
            interpretation = "Limited momentum, underperforming recent trends"
        
        return {
            "score": momentum_score,
            "rating": rating,
            "returns_12m": returns_12m,
            "returns_6m": returns_6m,
            "price_momentum": price_momentum,
            "interpretation": interpretation
        }
    
    def _analyze_quality_factor(self, factor_data: Dict) -> Dict:
        """Analyze quality factor exposure."""
        roe = factor_data["roe"]
        debt_equity = factor_data["debt_equity"]
        
        # Quality score (0-100)
        roe_score = min(100, roe * 4)
        debt_score = max(0, 100 - debt_equity * 40)
        earnings_stability = (roe_score + debt_score) / 2
        
        quality_score = earnings_stability
        
        # Rating
        if quality_score >= 70:
            rating = "High Quality"
        elif quality_score >= 50:
            rating = "Moderate Quality"
        else:
            rating = "Lower Quality"
        
        # Interpretation
        if quality_score >= 70:
            interpretation = "High-quality companies with strong profitability and low debt"
        elif quality_score >= 50:
            interpretation = "Moderate quality with reasonable financial metrics"
        else:
            interpretation = "Lower quality characteristics with higher leverage"
        
        return {
            "score": quality_score,
            "rating": rating,
            "roe": roe,
            "debt_equity": debt_equity,
            "earnings_stability": earnings_stability,
            "interpretation": interpretation
        }
    
    def _analyze_low_volatility_factor(self, factor_data: Dict) -> Dict:
        """Analyze low-volatility factor exposure."""
        volatility = factor_data["volatility"]
        beta = factor_data["beta"]
        
        # Low-vol score (0-100, lower volatility = higher score)
        vol_score = max(0, 100 - volatility * 4)
        beta_score = max(0, 100 - abs(beta - 0.8) * 80)
        max_drawdown = -volatility * 1.5  # Estimate
        
        low_vol_score = (vol_score + beta_score) / 2
        
        # Rating
        if low_vol_score >= 70:
            rating = "Low Volatility"
        elif low_vol_score >= 50:
            rating = "Moderate Volatility"
        else:
            rating = "High Volatility"
        
        # Interpretation
        if low_vol_score >= 70:
            interpretation = "Low volatility with defensive characteristics"
        elif low_vol_score >= 50:
            interpretation = "Moderate volatility in line with market"
        else:
            interpretation = "Higher volatility with greater risk"
        
        return {
            "score": low_vol_score,
            "rating": rating,
            "volatility": volatility,
            "beta": beta,
            "max_drawdown": max_drawdown,
            "interpretation": interpretation
        }
    
    def _analyze_size_factor(self, factor_data: Dict) -> Dict:
        """Analyze size factor exposure."""
        large_cap = factor_data["large_cap"]
        mid_cap = factor_data["mid_cap"]
        small_cap = factor_data["small_cap"]
        
        if large_cap >= 70:
            primary = "Large Cap"
            avg_market_cap = 250000
        elif mid_cap >= 40:
            primary = "Mid Cap"
            avg_market_cap = 50000
        else:
            primary = "Small Cap"
            avg_market_cap = 5000
        
        return {
            "primary": primary,
            "large_cap": large_cap,
            "mid_cap": mid_cap,
            "small_cap": small_cap,
            "avg_market_cap": avg_market_cap
        }
    
    def _calculate_composite_factor_score(
        self,
        value_factor: Dict,
        momentum_factor: Dict,
        quality_factor: Dict,
        low_vol_factor: Dict
    ) -> float:
        """Calculate composite factor score."""
        # Equal weighted average
        composite = (
            value_factor["score"] +
            momentum_factor["score"] +
            quality_factor["score"] +
            low_vol_factor["score"]
        ) / 4
        
        return composite
    
    def _determine_primary_tilt(
        self,
        value_factor: Dict,
        momentum_factor: Dict,
        quality_factor: Dict,
        low_vol_factor: Dict
    ) -> Dict:
        """Determine primary factor tilt."""
        factors = {
            "Value": value_factor["score"],
            "Momentum": momentum_factor["score"],
            "Quality": quality_factor["score"],
            "Low Volatility": low_vol_factor["score"]
        }
        
        primary_factor = max(factors, key=factors.get)
        primary_score = factors[primary_factor]
        
        # Determine strength
        other_scores = [s for f, s in factors.items() if f != primary_factor]
        avg_other = sum(other_scores) / len(other_scores)
        
        diff = primary_score - avg_other
        
        if diff > 20:
            strength = "Strong"
        elif diff > 10:
            strength = "Moderate"
        else:
            strength = "Weak"
        
        return {
            "factor": primary_factor,
            "strength": strength,
            "score": primary_score
        }
    
    def _calculate_factor_diversification(
        self,
        value_factor: Dict,
        momentum_factor: Dict,
        quality_factor: Dict,
        low_vol_factor: Dict
    ) -> str:
        """Calculate factor diversification."""
        scores = [
            value_factor["score"],
            momentum_factor["score"],
            quality_factor["score"],
            low_vol_factor["score"]
        ]
        
        # Calculate standard deviation
        stdev = statistics.stdev(scores)
        
        if stdev < 15:
            return "Highly diversified across factors"
        elif stdev < 25:
            return "Moderately diversified"
        else:
            return "Concentrated in specific factors"
    
    def _describe_investment_characteristics(
        self,
        primary_tilt: Dict,
        value_factor: Dict,
        momentum_factor: Dict,
        quality_factor: Dict,
        low_vol_factor: Dict
    ) -> List[str]:
        """Describe investment characteristics."""
        characteristics = []
        
        factor = primary_tilt["factor"]
        
        if factor == "Value":
            characteristics.append("Focus on undervalued companies with attractive valuations")
            characteristics.append(f"Average P/E ratio: {value_factor['pe_ratio']}")
        elif factor == "Momentum":
            characteristics.append("Emphasis on strong recent performance and price trends")
            characteristics.append(f"12-month returns: {momentum_factor['returns_12m']}%")
        elif factor == "Quality":
            characteristics.append("Investment in high-quality, profitable companies")
            characteristics.append(f"Average ROE: {quality_factor['roe']}%")
        elif factor == "Low Volatility":
            characteristics.append("Defensive approach with lower risk stocks")
            characteristics.append(f"Volatility: {low_vol_factor['volatility']}%")
        
        characteristics.append(f"Primary factor tilt: {primary_tilt['strength']} {factor}")
        
        return characteristics
    
    def _compare_to_market_factors(
        self,
        value_factor: Dict,
        momentum_factor: Dict,
        quality_factor: Dict,
        low_vol_factor: Dict
    ) -> Dict:
        """Compare to market average factors."""
        # Market benchmarks (S&P 500 proxy)
        market = {
            "pe_ratio": 20.5,
            "returns_12m": 12.0,
            "roe": 18.0,
            "volatility": 15.0
        }
        
        return {
            "valuation_vs_market": "Lower" if value_factor["pe_ratio"] < market["pe_ratio"] else "Higher",
            "momentum_vs_market": "Higher" if momentum_factor["returns_12m"] > market["returns_12m"] else "Lower",
            "quality_vs_market": "Higher" if quality_factor["roe"] > market["roe"] else "Lower",
            "volatility_vs_market": "Lower" if low_vol_factor["volatility"] < market["volatility"] else "Higher"
        }
    
    def _get_factor_rating(self, score: float) -> str:
        """Get factor rating from composite score."""
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Fair"
        else:
            return "Poor"


# Singleton instance
etf_analytics_service = ETFAdvancedAnalyticsService()
