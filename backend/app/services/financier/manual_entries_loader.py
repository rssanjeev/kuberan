"""
Manual Entries Loader Service

Loads hardcoded income and expenses from manual_entries.json file.
This allows users to add recurring income and adhoc checking account expenses
without uploading full bank statements.

File Format:
{
  "recurring_income": {
    "enabled": true,
    "amount": 3140.62,
    "frequency": "biweekly",  // "biweekly", "monthly", "weekly"
    "start_date": "2025-01-03",
    "description": "Payroll",
    "category": "Income"
  },
  "adhoc_expenses": [
    {
      "date": "2025-02-15",
      "description": "Gym Membership",
      "category": "Health & Pharmacy",
      "amount": 50.00
    }
  ]
}
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

from app.core.logging_config import get_logger

logger = get_logger(__name__)


class ManualEntriesLoader:
    """Service for loading and processing manual income/expense entries."""
    
    def __init__(self, file_path: Optional[str] = None):
        """
        Initialize loader with path to manual entries JSON file.
        
        Args:
            file_path: Path to JSON file (default: backend/data/manual_entries.json)
        """
        if file_path is None:
            # Default to backend/data/manual_entries.json
            base_dir = Path(__file__).parent.parent.parent  # Get backend/ directory
            self.file_path = base_dir / "data" / "manual_entries.json"
        else:
            self.file_path = Path(file_path)
    
    def load_entries(self) -> Dict[str, Any]:
        """
        Load manual entries from JSON file.
        
        Returns:
            Dictionary with recurring_income and adhoc_expenses
            Returns empty structure if file not found
        """
        if not self.file_path.exists():
            logger.warning(
                "Manual entries file not found",
                extra={"file_path": str(self.file_path)}
            )
            return {
                "recurring_income": {"enabled": False},
                "adhoc_expenses": []
            }
        
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
            
            logger.info(
                "Loaded manual entries",
                extra={
                    "file_path": str(self.file_path),
                    "has_recurring_income": "recurring_income" in data,
                    "adhoc_count": len(data.get("adhoc_expenses", []))
                }
            )
            return data
        
        except json.JSONDecodeError as e:
            logger.error(
                "Invalid JSON in manual entries file",
                extra={"file_path": str(self.file_path), "error": str(e)},
                exc_info=True
            )
            return {
                "recurring_income": {"enabled": False},
                "adhoc_expenses": []
            }
        
        except Exception as e:
            logger.error(
                "Error loading manual entries",
                extra={"file_path": str(self.file_path), "error": str(e)},
                exc_info=True
            )
            return {
                "recurring_income": {"enabled": False},
                "adhoc_expenses": []
            }
    
    def calculate_recurring_income(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Calculate recurring income entries for date range.
        
        Generates income entries based on frequency (biweekly, monthly, weekly).
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            List of income transaction dictionaries
        """
        entries = self.load_entries()
        recurring = entries.get("recurring_income", {})
        
        # Check if recurring income is enabled
        if not recurring.get("enabled", False):
            return []
        
        # Extract settings
        amount = recurring.get("amount", 0)
        frequency = recurring.get("frequency", "biweekly")
        income_start = datetime.strptime(recurring.get("start_date"), "%Y-%m-%d")
        description = recurring.get("description", "Payroll")
        category = recurring.get("category", "Income")
        
        # Generate income entries
        income_entries = []
        current_date = income_start
        
        # Determine interval
        if frequency == "biweekly":
            delta = timedelta(days=14)
        elif frequency == "weekly":
            delta = timedelta(days=7)
        elif frequency == "monthly":
            delta = timedelta(days=30)  # Approximate
        else:
            logger.warning(f"Unknown frequency: {frequency}, defaulting to biweekly")
            delta = timedelta(days=14)
        
        # Generate entries within date range
        while current_date <= end_date:
            if current_date >= start_date:
                income_entries.append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "description": description,
                    "category": category,
                    "amount": amount,
                    "source": "manual_recurring"
                })
            
            current_date += delta
        
        logger.info(
            "Generated recurring income entries",
            extra={
                "count": len(income_entries),
                "frequency": frequency,
                "amount": amount,
                "date_range": f"{start_date.date()} to {end_date.date()}"
            }
        )
        
        return income_entries
    
    def get_adhoc_expenses(
        self,
        year: Optional[int] = None,
        month: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get adhoc expenses, optionally filtered by year/month.
        
        Args:
            year: Filter by year (optional)
            month: Filter by month (optional, requires year)
            
        Returns:
            List of expense transaction dictionaries
        """
        entries = self.load_entries()
        adhoc = entries.get("adhoc_expenses", [])
        
        # Filter by date if specified
        if year is not None:
            filtered = []
            for expense in adhoc:
                expense_date = datetime.strptime(expense["date"], "%Y-%m-%d")
                
                # Check year
                if expense_date.year != year:
                    continue
                
                # Check month if specified
                if month is not None and expense_date.month != month:
                    continue
                
                # Add source tag
                expense_with_source = expense.copy()
                expense_with_source["source"] = "manual_adhoc"
                filtered.append(expense_with_source)
            
            logger.info(
                "Filtered adhoc expenses",
                extra={
                    "total": len(adhoc),
                    "filtered": len(filtered),
                    "year": year,
                    "month": month
                }
            )
            
            return filtered
        
        # Return all with source tag
        return [
            {**expense, "source": "manual_adhoc"}
            for expense in adhoc
        ]
    
    def convert_to_transactions(
        self,
        entries: List[Dict[str, Any]],
        statement_year: int,
        statement_month: int
    ) -> List[Dict[str, Any]]:
        """
        Convert manual entries to transaction format compatible with database.
        
        Args:
            entries: List of manual entry dictionaries
            statement_year: Year for statement period
            statement_month: Month for statement period
            
        Returns:
            List of transaction dictionaries ready for database insertion
        """
        transactions = []
        
        for entry in entries:
            # Parse date
            entry_date = datetime.strptime(entry["date"], "%Y-%m-%d")
            
            # Create transaction object
            transaction = {
                "merchant_name": entry["description"],
                "merchant_location": "Manual Entry",
                "amount": abs(entry["amount"]),
                "transaction_type": "charge" if entry.get("category") != "Income" else "credit",
                "category": entry["category"],
                "transaction_date": str(entry_date.day),
                "statement_year": statement_year,
                "statement_month": statement_month,
                "bank": "Manual",
                "source": entry.get("source", "manual"),
                "file_hash": f"manual_{statement_year}_{statement_month}"
            }
            
            transactions.append(transaction)
        
        return transactions


# Singleton instance
manual_entries_loader = ManualEntriesLoader()
