"""Matrix-driven standardization engine for per-ticker unified views.

This module implements the complete standardization pipeline as specified
in `docs/DATA_STANDARDIZATION_RULES.md` and driven by the configuration
in `config/data_priority_matrix.yaml`.

It replaces the v0 hard-coded logic with a dynamic, strategy-based
approach that can handle all data points defined in the matrix.
"""

from __future__ import annotations

import statistics
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

import yaml

from app.core.logging_config import get_logger


logger = get_logger(__name__)


SnapshotMapping = Mapping[str, Mapping[str, Any]]


class StandardizationEngine:
    """Matrix-driven standardization engine.
    
    Loads `data_priority_matrix.yaml` and applies the appropriate strategy
    for each data point to build a `standardized_ticker_view_v1`.
    """

    def __init__(self, matrix_path: Optional[Path] = None):
        """Initialize the standardization engine.
        
        Args:
            matrix_path: Path to the data priority matrix YAML file.
                If None, defaults to `config/data_priority_matrix.yaml`
                relative to the backend root.
        """
        if matrix_path is None:
            # Default to <project_root>/config/data_priority_matrix.yaml
            # This file is at backend/app/services/standardization_engine.py
            # So go up 4 levels: services -> app -> backend -> project_root
            backend_root = Path(__file__).parent.parent.parent.parent
            matrix_path = backend_root / "config" / "data_priority_matrix.yaml"
        
        self.matrix_path = matrix_path
        self.matrix: Dict[str, Any] = {}
        self._load_matrix()
        
        logger.info(
            "StandardizationEngine initialized",
            extra={"matrix_path": str(self.matrix_path), "data_points": len(self.matrix)}
        )

    def _load_matrix(self) -> None:
        """Load the data priority matrix from YAML."""
        logger.debug("Loading data priority matrix", extra={"path": str(self.matrix_path)})
        
        with self.matrix_path.open("r", encoding="utf-8") as f:
            self.matrix = yaml.safe_load(f) or {}
        
        # Filter out comments and metadata
        self.matrix = {k: v for k, v in self.matrix.items() if isinstance(v, dict)}
        
        logger.info(
            "Data priority matrix loaded",
            extra={"data_points": len(self.matrix)}
        )

    def standardize_ticker(
        self,
        ticker: str,
        snapshots: SnapshotMapping,
    ) -> Dict[str, Any]:
        """Build a standardized ticker view from provider snapshots.
        
        Args:
            ticker: The ticker symbol being standardized.
            snapshots: Mapping of provider name to its parsed snapshot dictionary.
        
        Returns:
            A dictionary representing `standardized_ticker_view_v1` with all
            configured data points from the matrix.
        """
        logger.info(
            "Standardizing ticker",
            extra={"ticker": ticker, "providers": list(snapshots.keys())}
        )
        
        data_points: Dict[str, Any] = {}
        
        for data_point_name, config in self.matrix.items():
            try:
                result = self._standardize_data_point(
                    data_point_name,
                    config,
                    snapshots
                )
                if result is not None:
                    data_points[data_point_name] = result
            except Exception as e:
                logger.warning(
                    f"Failed to standardize data point: {data_point_name}",
                    extra={"ticker": ticker, "error": str(e)},
                    exc_info=True
                )
        
        standardized = {
            "ticker": ticker,
            "data_points": data_points,
        }
        
        logger.info(
            "Standardized ticker view built",
            extra={"ticker": ticker, "data_points_count": len(data_points)}
        )
        
        return standardized

    def _standardize_data_point(
        self,
        data_point_name: str,
        config: Dict[str, Any],
        snapshots: SnapshotMapping,
    ) -> Optional[Dict[str, Any]]:
        """Standardize a single data point using the configured strategy.
        
        Args:
            data_point_name: Name of the data point (e.g., "market_cap").
            config: Configuration from the matrix for this data point.
            snapshots: Provider snapshots.
        
        Returns:
            A dict with `value`, `source`, and optionally `inputs`, or None
            if the data point cannot be standardized.
        """
        strategy = config.get("strategy")
        
        if strategy == "single_value":
            return self._apply_single_value(data_point_name, config, snapshots)
        elif strategy == "numeric_consensus":
            # DEPRECATED: numeric_consensus violates "no synthetic data" principle
            # This strategy calculated weighted averages, creating financial values
            # that don't exist in any provider. Use single_value instead.
            logger.error(
                "DEPRECATED STRATEGY USED: numeric_consensus",
                extra={
                    "data_point": data_point_name,
                    "message": "This strategy creates synthetic financial data and must not be used. Use single_value instead."
                }
            )
            raise ValueError(
                f"numeric_consensus strategy is DEPRECATED for {data_point_name}. "
                "This violates the 'no synthetic data' principle. Use single_value strategy instead."
            )
        elif strategy == "timeseries_primary_with_checks":
            return self._apply_timeseries_primary(data_point_name, config, snapshots)
        elif strategy == "aggregate_union":
            return self._apply_aggregate_union(data_point_name, config, snapshots)
        elif strategy == "passthrough":
            return self._apply_passthrough(data_point_name, config, snapshots)
        else:
            logger.warning(
                f"Unknown strategy for data point: {data_point_name}",
                extra={"strategy": strategy}
            )
            return None

    def _apply_single_value(
        self,
        data_point_name: str,
        config: Dict[str, Any],
        snapshots: SnapshotMapping,
    ) -> Optional[Dict[str, Any]]:
        """Apply the single_value strategy: pick highest-weight non-null value."""
        candidates = config.get("candidates", [])
        
        for candidate in candidates:
            provider = candidate["provider"]
            if provider not in snapshots:
                continue
            
            value = self._extract_value(data_point_name, snapshots[provider])
            if value is not None:
                return {
                    "value": value,
                    "source": provider,
                }
        
        return None

    def _apply_numeric_consensus(
        self,
        data_point_name: str,
        config: Dict[str, Any],
        snapshots: SnapshotMapping,
    ) -> Optional[Dict[str, Any]]:
        """
        DEPRECATED: Apply numeric_consensus strategy.
        
        ⚠️ THIS METHOD IS DEPRECATED AND MUST NOT BE USED ⚠️
        
        This method violates the "no synthetic data" principle by calculating
        weighted averages of provider values, creating financial data that
        doesn't actually exist in any provider.
        
        Historical behavior:
        - Calculated weighted average or median with outlier detection
        - Used tolerance_pct to filter outliers
        - Created synthetic values by multiplying provider values by weights
        
        Why deprecated:
        - Weights are PRIORITY RANKINGS, not calculation coefficients
        - Financial decisions must be based on real provider data only
        - Never calculate or manipulate financial values
        
        Replacement: Use single_value strategy instead, which selects the
        highest-priority provider's value without calculation.
        
        This method is kept for historical reference only.
        """
        raise NotImplementedError(
            "numeric_consensus strategy is DEPRECATED. "
            "This method created synthetic financial data by calculating weighted averages. "
            "Use single_value strategy instead to select from real provider values."
        )

    def _apply_timeseries_primary(
        self,
        data_point_name: str,
        config: Dict[str, Any],
        snapshots: SnapshotMapping,
    ) -> Optional[Dict[str, Any]]:
        """Apply timeseries_primary_with_checks: use primary provider, sanity check others."""
        candidates = config.get("candidates", [])
        
        primary_provider = None
        for candidate in candidates:
            if candidate.get("role") == "primary":
                primary_provider = candidate["provider"]
                break
        
        if not primary_provider or primary_provider not in snapshots:
            return None
        
        value = self._extract_value(data_point_name, snapshots[primary_provider])
        if value is None:
            return None
        
        return {
            "value": value,
            "source": primary_provider,
        }

    def _apply_aggregate_union(
        self,
        data_point_name: str,
        config: Dict[str, Any],
        snapshots: SnapshotMapping,
    ) -> Optional[Dict[str, Any]]:
        """Apply aggregate_union: combine all provider values into a list."""
        candidates = config.get("candidates", [])
        
        all_values = []
        sources = []
        
        for candidate in candidates:
            provider = candidate["provider"]
            if provider not in snapshots:
                continue
            
            value = self._extract_value(data_point_name, snapshots[provider])
            if value is not None:
                if isinstance(value, list):
                    all_values.extend(value)
                else:
                    all_values.append(value)
                sources.append(provider)
        
        if not all_values:
            return None
        
        return {
            "value": all_values,
            "source": sources,
        }

    def _apply_passthrough(
        self,
        data_point_name: str,
        config: Dict[str, Any],
        snapshots: SnapshotMapping,
    ) -> Optional[Dict[str, Any]]:
        """Apply passthrough: return value from highest-weight provider as-is."""
        candidates = config.get("candidates", [])
        
        for candidate in candidates:
            provider = candidate["provider"]
            if provider not in snapshots:
                continue
            
            value = self._extract_value(data_point_name, snapshots[provider])
            if value is not None:
                return {
                    "value": value,
                    "source": provider,
                }
        
        return None

    def _extract_value(self, data_point_name: str, snapshot: Mapping[str, Any]) -> Any:
        """Extract a value from a provider snapshot for a given data point.
        
        This uses a heuristic mapping from data point names to snapshot paths.
        In a production system, this should be configurable in the matrix or
        a separate mapping file.
        
        Args:
            data_point_name: Name of the data point.
            snapshot: Provider snapshot dictionary.
        
        Returns:
            The extracted value, or None if not found.
        """
        provider = snapshot.get("provider", "unknown")
        
        # Get common sections
        identity = snapshot.get("identity", {})
        profile = snapshot.get("company_profile", {})
        fundamentals = snapshot.get("fundamentals", {})
        overview = snapshot.get("overview_metrics", {})
        profitability = snapshot.get("profitability_metrics", {})
        growth = snapshot.get("growth_metrics", {})
        earnings_div = snapshot.get("earnings_dividends", {})
        risk = snapshot.get("risk_metrics", {})
        shares = snapshot.get("shares", {})
        prices = snapshot.get("prices", {})
        finviz_table = snapshot.get("snapshot_table", {})
        corporate_actions = snapshot.get("corporate_actions", {})
        news = snapshot.get("news", {})
        etf = snapshot.get("etf_specific", {})
        
        # ===== Identity & Classification =====
        if data_point_name == "ticker":
            return snapshot.get("ticker")
        elif data_point_name == "name":
            return identity.get("company_name")
        elif data_point_name == "exchange":
            return identity.get("exchange")
        elif data_point_name == "exchange_mic":
            return identity.get("exchange_mic")
        elif data_point_name == "locale":
            return identity.get("locale")
        elif data_point_name == "country":
            return identity.get("country")
        elif data_point_name == "sector":
            return identity.get("sector")
        elif data_point_name == "industry":
            return identity.get("industry")
        elif data_point_name == "sic_code":
            return identity.get("sic_code")
        elif data_point_name == "sic_description":
            return identity.get("sic_description")
        elif data_point_name == "cik":
            return identity.get("cik")
        elif data_point_name == "composite_figi":
            return identity.get("composite_figi")
        elif data_point_name == "share_class_figi":
            return identity.get("share_class_figi")
        elif data_point_name == "isin":
            return identity.get("isin")
        elif data_point_name == "cusip":
            return identity.get("cusip")
        elif data_point_name == "primary_listing_date":
            return identity.get("primary_listing_date")
        elif data_point_name == "status_active":
            return identity.get("status_active")
        
        # ===== Company Profile =====
        elif data_point_name == "company_description":
            return profile.get("description")
        elif data_point_name == "website_url":
            return profile.get("website_url")
        elif data_point_name == "phone_number":
            return profile.get("phone_number")
        elif data_point_name == "address_city":
            return profile.get("address_city")
        elif data_point_name == "address_state":
            return profile.get("address_state")
        elif data_point_name == "address_postal_code":
            return profile.get("address_postal_code")
        elif data_point_name == "country_full":
            return profile.get("country_full")
        elif data_point_name == "employees":
            return profile.get("employees") or fundamentals.get("employees")
        
        # ===== Size, Shares & Liquidity =====
        elif data_point_name == "market_cap":
            return (
                fundamentals.get("market_cap")
                or overview.get("market_cap")
                or self._parse_finviz_market_cap(finviz_table.get("Market Cap"))
            )
        elif data_point_name == "enterprise_value":
            return (
                fundamentals.get("enterprise_value")
                or overview.get("enterprise_value")
                or self._parse_finviz_market_cap(finviz_table.get("Enterprise Value"))
            )
        elif data_point_name == "shares_outstanding":
            return (
                shares.get("shares_outstanding")
                or fundamentals.get("shares_outstanding")
                or overview.get("shares_outstanding")
            )
        elif data_point_name == "free_float_shares":
            return (
                overview.get("free_float_shares")
                or self._parse_finviz_market_cap(finviz_table.get("Float"))
            )
        elif data_point_name == "avg_volume_10d":
            return overview.get("avg_volume_10d")
        elif data_point_name == "avg_volume_3m":
            return (
                overview.get("avg_volume_3m")
                or self._parse_finviz_market_cap(finviz_table.get("Avg Volume"))
            )
        
        # ===== Valuation Multiples =====
        elif data_point_name == "pe_ttm":
            return overview.get("pe_ttm") or self._parse_numeric(finviz_table.get("P/E"))
        elif data_point_name == "pe_forward":
            return overview.get("pe_forward") or self._parse_numeric(finviz_table.get("Forward P/E"))
        elif data_point_name == "peg_ratio":
            return overview.get("peg_ratio") or self._parse_numeric(finviz_table.get("PEG"))
        elif data_point_name == "ps_ttm":
            return overview.get("ps_ttm") or self._parse_numeric(finviz_table.get("P/S"))
        elif data_point_name == "pb_ratio":
            return overview.get("pb_ratio") or self._parse_numeric(finviz_table.get("P/B"))
        elif data_point_name == "pfcf_ttm":
            return overview.get("pfcf_ttm") or self._parse_numeric(finviz_table.get("P/FCF"))
        elif data_point_name == "enterprise_value_ebitda":
            return overview.get("enterprise_value_ebitda") or self._parse_numeric(finviz_table.get("EV/EBITDA"))
        elif data_point_name == "enterprise_value_sales":
            return overview.get("enterprise_value_sales") or self._parse_numeric(finviz_table.get("EV/Sales"))
        
        # ===== Profitability & Margins =====
        elif data_point_name == "gross_margin_ttm":
            return profitability.get("gross_margin_ttm")
        elif data_point_name == "operating_margin_ttm":
            return profitability.get("operating_margin_ttm")
        elif data_point_name == "profit_margin_ttm":
            return profitability.get("profit_margin_ttm")
        elif data_point_name == "return_on_equity_ttm":
            return profitability.get("return_on_equity_ttm")
        elif data_point_name == "return_on_assets_ttm":
            return profitability.get("return_on_assets_ttm")
        elif data_point_name == "return_on_invested_capital_ttm":
            return profitability.get("return_on_invested_capital_ttm")
        
        # ===== Growth Metrics =====
        elif data_point_name == "revenue_ttm":
            return growth.get("revenue_ttm") or fundamentals.get("revenue_ttm")
        elif data_point_name == "revenue_5y_cagr":
            return growth.get("revenue_5y_cagr")
        elif data_point_name == "net_income_ttm":
            return growth.get("net_income_ttm") or fundamentals.get("net_income_ttm")
        elif data_point_name == "net_income_5y_cagr":
            return growth.get("net_income_5y_cagr")
        elif data_point_name == "free_cash_flow_ttm":
            return growth.get("free_cash_flow_ttm")
        elif data_point_name == "free_cash_flow_5y_cagr":
            return growth.get("free_cash_flow_5y_cagr")
        
        # ===== Earnings & Dividends =====
        elif data_point_name == "eps_ttm":
            return (
                earnings_div.get("eps_ttm")
                or overview.get("eps_ttm")
                or self._parse_numeric(finviz_table.get("EPS (ttm)"))
            )
        elif data_point_name == "EPS_forward":
            return (
                earnings_div.get("eps_forward")
                or overview.get("eps_forward")
                or self._parse_numeric(finviz_table.get("EPS next Y"))
            )
        elif data_point_name == "Dividend_yield_ttm":
            dividend_str = finviz_table.get("Dividend %")
            if dividend_str and isinstance(dividend_str, str):
                # Parse "0.47%" to 0.0047
                try:
                    return float(dividend_str.strip("%")) / 100.0
                except:
                    pass
            return earnings_div.get("dividend_yield_ttm") or overview.get("dividend_yield_ttm")
        elif data_point_name == "Dividend_payout_ratio_ttm":
            return earnings_div.get("dividend_payout_ratio_ttm")
        
        # ===== Risk & Volatility =====
        elif data_point_name == "beta_5y_monthly":
            return (
                risk.get("beta_5y_monthly")
                or fundamentals.get("beta_5y_monthly")
                or self._parse_numeric(finviz_table.get("Beta"))
            )
        elif data_point_name == "beta_1y_daily":
            return risk.get("beta_1y_daily")
        elif data_point_name == "price_52w_high":
            return (
                fundamentals.get("price_52w_high")
                or self._parse_numeric(finviz_table.get("52W High"))
            )
        elif data_point_name == "price_52w_low":
            return (
                fundamentals.get("price_52w_low")
                or self._parse_numeric(finviz_table.get("52W Low"))
            )
        
        # ===== Prices (OHLCV) =====
        elif data_point_name == "close_price":
            return prices.get("close_price") or self._parse_numeric(finviz_table.get("Price"))
        elif data_point_name == "open_price":
            return prices.get("open_price") or self._parse_numeric(finviz_table.get("Open"))
        elif data_point_name == "high_price":
            return prices.get("high_price") or self._parse_numeric(finviz_table.get("High"))
        elif data_point_name == "low_price":
            return prices.get("low_price") or self._parse_numeric(finviz_table.get("Low"))
        elif data_point_name == "adjusted_close_price":
            return prices.get("adjusted_close_price")
        elif data_point_name == "volume":
            return (
                prices.get("volume")
                or self._parse_finviz_market_cap(finviz_table.get("Volume"))
            )
        
        # ===== Corporate Actions =====
        elif data_point_name == "split_event":
            return corporate_actions.get("split_event")
        elif data_point_name == "dividend_event":
            return corporate_actions.get("dividend_event")
        
        # ===== News & Sentiment =====
        elif data_point_name == "news_article":
            articles = news.get("news_article") or snapshot.get("news_articles")
            return articles if articles else None
        elif data_point_name == "news_sentiment_score":
            return news.get("news_sentiment_score")
        
        # ===== ETF-Specific Fields =====
        elif data_point_name == "etf_aum":
            return etf.get("etf_aum")
        elif data_point_name == "etf_expense_ratio":
            return etf.get("etf_expense_ratio")
        elif data_point_name == "etf_holdings_count":
            return etf.get("etf_holdings_count")
        
        # Not found
        return None

    def _parse_finviz_market_cap(self, raw: Any) -> Optional[float]:
        """Parse Finviz market cap strings like '2.68T', '150.5B'."""
        if not isinstance(raw, str):
            return None
        
        raw = raw.strip().upper()
        if not raw:
            return None
        
        multiplier = 1.0
        if raw.endswith("T"):
            multiplier = 1_000_000_000_000
            raw = raw[:-1]
        elif raw.endswith("B"):
            multiplier = 1_000_000_000
            raw = raw[:-1]
        elif raw.endswith("M"):
            multiplier = 1_000_000
            raw = raw[:-1]
        elif raw.endswith("K"):
            multiplier = 1_000
            raw = raw[:-1]
        
        try:
            return float(raw) * multiplier
        except (ValueError, TypeError):
            return None

    def _parse_numeric(self, raw: Any) -> Optional[float]:
        """Parse a numeric value from various formats."""
        if isinstance(raw, (int, float)):
            return float(raw)
        elif isinstance(raw, str):
            try:
                return float(raw.strip())
            except (ValueError, TypeError):
                return None
        return None


def load_json_file(path: Path) -> Dict[str, Any]:
    """Load a JSON file into a dictionary."""
    import json
    
    logger.debug("Loading JSON file", extra={"path": str(path)})
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
