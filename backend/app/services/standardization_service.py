"""Standardization service for per-ticker unified views.

This module currently implements a very small v0 slice of the
standardization pipeline, focused on a handful of core identity
and size data points for a single ticker (used in golden fixtures).

Future versions should expand this to be fully driven by
`config/data_priority_matrix.yaml` and support all configured
providers and data points.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Mapping

import json

from app.core.logging_config import get_logger


logger = get_logger(__name__)


SnapshotMapping = Mapping[str, Mapping[str, Any]]


def _parse_finviz_market_cap(raw: str) -> float | None:
    """Parse Finviz market cap strings like '2.68T', '150.5B', '3.2M'.

    Args:
        raw: Market cap string from Finviz (e.g., "2.68T").

    Returns:
        Numeric market cap value, or None if unparseable.
    """

    if not isinstance(raw, str):
        return None

    raw = raw.strip().upper()
    if not raw:
        return None

    # Extract numeric part and suffix
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
        base = float(raw)
        return base * multiplier
    except (ValueError, TypeError):
        return None


def standardize_ticker_from_snapshots(ticker: str, snapshots: SnapshotMapping) -> Dict[str, Any]:
    """Build a minimal `standardized_ticker_view_v1` from provider snapshots.

    This v0 implementation is intentionally narrow: it only standardizes
    a small set of data points used by the initial golden fixture test
    for AAPL:

    - ticker
    - name
    - exchange
    - sector
    - market_cap

    The logic is explicitly hard-coded for now and does not yet consult
    `config/data_priority_matrix.yaml`. It is designed to be replaced by
    a matrix-driven implementation once the broader pipeline is ready.

    Args:
        ticker: The ticker symbol being standardized.
        snapshots: Mapping of provider name to its parsed snapshot
            dictionary. Expected keys for the v0 path are
            "massive", "stockanalysis", "finviz", and "yfinance".

    Returns:
        A dictionary representing `standardized_ticker_view_v1` for the
        subset of data points covered by the initial golden fixtures.
    """

    logger.info("Standardizing ticker from snapshots", extra={"ticker": ticker, "providers": list(snapshots.keys())})

    massive = snapshots.get("massive", {})
    stockanalysis = snapshots.get("stockanalysis", {})
    finviz = snapshots.get("finviz", {})
    yfinance = snapshots.get("yfinance", {})

    # Core identity fields
    name = (
        massive.get("identity", {}).get("company_name")
        or stockanalysis.get("identity", {}).get("company_name")
        or finviz.get("identity", {}).get("company_name")
        or yfinance.get("identity", {}).get("company_name")
    )

    exchange = (
        massive.get("identity", {}).get("exchange")
        or stockanalysis.get("identity", {}).get("exchange")
        or finviz.get("identity", {}).get("exchange")
        or yfinance.get("identity", {}).get("exchange")
    )

    sector = (
        stockanalysis.get("identity", {}).get("sector")
        or massive.get("identity", {}).get("sector")
        or finviz.get("identity", {}).get("sector")
        or yfinance.get("identity", {}).get("sector")
    )

    # Market cap consensus (very simple for v0: prefer yfinance, but
    # record all available inputs under `inputs`).
    market_cap_inputs: Dict[str, Any] = {}

    sa_mc = stockanalysis.get("overview_metrics", {}).get("market_cap")
    if sa_mc is not None:
        market_cap_inputs["stockanalysis"] = sa_mc

    fv_mc_raw = finviz.get("snapshot_table", {}).get("Market Cap")
    if fv_mc_raw is not None:
        # Parse Finviz market cap strings like "2.68T", "150.5B", etc.
        fv_mc_numeric = _parse_finviz_market_cap(fv_mc_raw)
        if fv_mc_numeric is not None:
            market_cap_inputs["finviz"] = fv_mc_numeric

    yf_mc = yfinance.get("fundamentals", {}).get("market_cap")
    if yf_mc is not None:
        market_cap_inputs["yfinance"] = yf_mc

    market_cap_value = yf_mc or sa_mc

    # Build minimal standardized view; timestamps and version are left
    # to callers/fixtures for now since this function focuses solely on
    # data point values.
    data_points: Dict[str, Any] = {
        "ticker": {
            "value": ticker,
            "source": "massive" if massive else "unknown",
        },
        "name": {
            "value": name,
            "source": "massive" if massive else "unknown",
        },
        "exchange": {
            "value": exchange,
            "source": "massive" if massive else "unknown",
        },
        "sector": {
            "value": sector,
            "source": "stockanalysis" if stockanalysis else "unknown",
        },
    }

    if market_cap_value is not None:
        data_points["market_cap"] = {
            "value": market_cap_value,
            "source": "yfinance" if yf_mc is not None else "stockanalysis",
            "inputs": market_cap_inputs,
        }

    standardized: Dict[str, Any] = {
        "ticker": ticker,
        # `as_of`, `computed_at`, and `standardization_version` are
        # filled in by higher layers or provided by tests/fixtures.
        "data_points": data_points,
    }

    logger.info("Standardized ticker view built", extra={"ticker": ticker, "data_points": list(data_points.keys())})

    return standardized


def load_json_file(path: Path) -> Dict[str, Any]:
    """Load a JSON file into a dictionary.

    This small helper exists primarily for tests and scripts that want
    to work with golden fixtures on disk.

    Args:
        path: Path to the JSON file.

    Returns:
        Parsed JSON content as a dictionary.
    """

    logger.debug("Loading JSON file", extra={"path": str(path)})
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
