"""
CSV report generation service.
"""
import csv
from typing import List, Dict, Any
from pathlib import Path


class ReportService:
    """Service for generating CSV reports."""

    def __init__(self, output_dir: str = "Reports/Projections"):
        """Initialize report service with output directory."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_csv_report(self, data: List[Dict[str, Any]], ticker: str) -> str:
        """
        Generate CSV report from projection data.

        Args:
            data: List of projection data dictionaries
            ticker: Stock ticker symbol for filename

        Returns:
            Path to the generated CSV file
        """
        filename = self.output_dir / f"{ticker}_projection.csv"

        fieldnames = [
            "Strategy",
            "Quarter",
            "Initial_Investment",
            "Quarterly_Investment",
            "Total Shares",
            "Total_Investment",
            "Projected_Balance"
        ]

        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(row)

        return str(filename)