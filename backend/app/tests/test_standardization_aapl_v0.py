"""Golden fixture-based test for the standardization pipeline.

This test uses the AAPL fixtures in
`backend/app/tests/standardization_fixtures/aapl/` to validate the
matrix-driven standardization engine.

The test validates that the engine correctly applies strategies from
`config/data_priority_matrix.yaml` to produce expected standardized
data points.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from app.services.standardization_engine import (
    StandardizationEngine,
    load_json_file,
)


FIXTURES_DIR = (
    Path(__file__).parent
    / "standardization_fixtures"
    / "aapl"
)


def _load_snapshots() -> Dict[str, Dict[str, Any]]:
    """Load provider snapshots for AAPL from fixture JSON files."""

    return {
        "massive": load_json_file(FIXTURES_DIR / "aapl_massive_snapshot_v1.json"),
        "stockanalysis": load_json_file(FIXTURES_DIR / "aapl_stockanalysis_snapshot_v1.json"),
        "finviz": load_json_file(FIXTURES_DIR / "aapl_finviz_snapshot_v1.json"),
        "yfinance": load_json_file(FIXTURES_DIR / "aapl_yfinance_snapshot_v1.json"),
    }


def _load_expected_view() -> Dict[str, Any]:
    """Load expected standardized ticker view for AAPL."""

    return load_json_file(FIXTURES_DIR / "aapl_expected_standardized_ticker_view_v1.json")


def test_standardize_ticker_aapl_v0_core_fields() -> None:
    """Standardization produces expected core fields for AAPL.

    This test focuses on validating that the matrix-driven engine
    correctly standardizes all data points present in the fixture's
    expected output.
    """

    snapshots = _load_snapshots()
    expected = _load_expected_view()

    engine = StandardizationEngine()
    result = engine.standardize_ticker("AAPL", snapshots)

    # Validate all data points in the expected fixture
    expected_points = expected["data_points"]
    result_points = result["data_points"]

    for key, expected_dp in expected_points.items():
        assert key in result_points, f"Missing data point in result: {key}"
        
        result_dp = result_points[key]
        
        # Validate value (with floating point tolerance for numeric values)
        expected_value = expected_dp["value"]
        result_value = result_dp["value"]
        
        if isinstance(expected_value, (int, float)) and isinstance(result_value, (int, float)):
            # Round to 5 decimal places for comparison
            assert round(result_value, 5) == round(expected_value, 5), \
                f"{key}: value mismatch (got {result_value}, expected {expected_value})"
        else:
            # Exact match for non-numeric values
            assert result_value == expected_value, \
                f"{key}: value mismatch (got {result_value}, expected {expected_value})"
        
        # Validate source
        assert result_dp["source"] == expected_dp["source"], \
            f"{key}: source mismatch (got {result_dp['source']}, expected {expected_dp['source']})"
        
        # Validate inputs if present in expected
        if "inputs" in expected_dp:
            assert "inputs" in result_dp, f"{key}: missing inputs"
            assert result_dp["inputs"] == expected_dp["inputs"], \
                f"{key}: inputs mismatch"
