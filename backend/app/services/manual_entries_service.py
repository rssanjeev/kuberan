"""
Manual Entries Service

Handles recurring income, recurring expenses, and adhoc expenses
from manual_entries.json file.

Security: No sensitive data stored, all entries are user-controlled.
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path

from app.core.logging_config import get_logger

logger = get_logger(__name__)


class ManualEntriesService:
    """Service for loading and processing manual financial entries."""
    
    def __init__(self):
        """Initialize the service with path to manual entries file."""
        # Path: backend/data/manual_entries.json
        self.data_file = Path(__file__).parent.parent.parent / "data" / "manual_entries.json"
        logger.info("Manual entries service initialized", extra={"file": str(self.data_file)})
    
    def load_manual_entries(self) -> Dict[str, Any]:
        """
        Load manual entries from JSON file.
        
        Returns:
            Dictionary with recurring_income, recurring_expenses, adhoc_expenses
            
        Raises:
            FileNotFoundError: If manual_entries.json doesn't exist
            ValueError: If JSON is invalid
        """
        try:
            if not self.data_file.exists():
                logger.warning("Manual entries file not found", extra={"path": str(self.data_file)})
                return {
                    "recurring_income": {},
                    "recurring_expenses": [],
                    "adhoc_expenses": []
                }
            
            with open(self.data_file, 'r') as f:
                data = json.load(f)
            
            logger.info(
                "Loaded manual entries",
                extra={
                    "recurring_income_enabled": data.get("recurring_income", {}).get("enabled", False),
                    "recurring_expenses_count": len(data.get("recurring_expenses", [])),
                    "adhoc_expenses_count": len(data.get("adhoc_expenses", []))
                }
            )
            
            return data
        
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON in manual entries file", extra={"error": str(e)}, exc_info=True)
            raise ValueError(f"Invalid JSON in manual_entries.json: {e}")
        except Exception as e:
            logger.error("Failed to load manual entries", extra={"error": str(e)}, exc_info=True)
            raise
    
    def generate_recurring_income(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Generate recurring income transactions for date range.
        
        Args:
            start_date: Start of period
            end_date: End of period
            
        Returns:
            List of transaction dictionaries
        """
        data = self.load_manual_entries()
        recurring_income = data.get("recurring_income", {})
        
        if not recurring_income.get("enabled", False):
            logger.debug("Recurring income disabled")
            return []
        
        transactions = []
        amount = recurring_income.get("amount", 0)
        frequency = recurring_income.get("frequency", "biweekly")
        description = recurring_income.get("description", "Income")
        category = recurring_income.get("category", "Income")
        
        # Parse start date from config
        income_start_str = recurring_income.get("start_date", "2025-01-01")
        income_start = datetime.strptime(income_start_str, "%Y-%m-%d")
        
        # Generate transactions based on frequency
        current_date = income_start
        
        if frequency == "biweekly":
            interval_days = 14
        elif frequency == "monthly":
            interval_days = 30  # Approximate
        elif frequency == "weekly":
            interval_days = 7
        else:
            interval_days = 14  # Default to biweekly
        
        # Generate all occurrences in date range
        while current_date <= end_date:
            if current_date >= start_date:
                transactions.append({
                    "merchant_name": description,
                    "merchant_location": "Manual Entry",
                    "amount": amount,  # Positive amount for income (credit card credits)
                    "transaction_type": "income",
                    "category": category,
                    "transaction_date": current_date.strftime("%d"),
                    "statement_year": current_date.year,
                    "statement_month": current_date.month,
                    "bank": "Manual Entry",
                    "file_hash": f"manual_income_{current_date.strftime('%Y%m%d')}",
                    "source": "manual_entries"
                })
            
            current_date += timedelta(days=interval_days)
        
        logger.info(
            "Generated recurring income transactions",
            extra={
                "count": len(transactions),
                "amount": amount,
                "frequency": frequency,
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d")
            }
        )
        
        return transactions
    
    def generate_recurring_expenses(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Generate recurring expense transactions for date range.
        
        Args:
            start_date: Start of period
            end_date: End of period
            
        Returns:
            List of transaction dictionaries
        """
        data = self.load_manual_entries()
        recurring_expenses = data.get("recurring_expenses", [])
        
        transactions = []
        
        for expense in recurring_expenses:
            if not expense.get("enabled", False):
                continue
            
            amount = expense.get("amount", 0)
            frequency = expense.get("frequency", "monthly")
            description = expense.get("description", "Expense")
            category = expense.get("category", "Other")
            
            # Parse due date
            due_date_str = expense.get("due_date", "2025-01-01")
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
            
            # Generate transactions based on frequency
            current_date = due_date
            
            if frequency == "monthly":
                # Generate for each month in range
                while current_date <= end_date:
                    if current_date >= start_date:
                        transactions.append({
                            "merchant_name": description,
                            "merchant_location": "Manual Entry",
                            "amount": amount,  # Positive = expense/debit
                            "transaction_type": "charge",
                            "category": category,
                            "transaction_date": current_date.strftime("%d"),
                            "statement_year": current_date.year,
                            "statement_month": current_date.month,
                            "bank": "Manual Entry",
                            "file_hash": f"manual_expense_{description.replace(' ', '_')}_{current_date.strftime('%Y%m%d')}",
                            "source": "manual_entries"
                        })
                    
                    # Move to next month (same day)
                    if current_date.month == 12:
                        current_date = current_date.replace(year=current_date.year + 1, month=1)
                    else:
                        try:
                            current_date = current_date.replace(month=current_date.month + 1)
                        except ValueError:
                            # Handle day overflow (e.g., Jan 31 -> Feb 31 doesn't exist)
                            if current_date.month == 12:
                                current_date = current_date.replace(year=current_date.year + 1, month=1, day=1)
                            else:
                                current_date = current_date.replace(month=current_date.month + 1, day=1)
            
            elif frequency == "biweekly":
                interval_days = 14
                while current_date <= end_date:
                    if current_date >= start_date:
                        transactions.append({
                            "merchant_name": description,
                            "merchant_location": "Manual Entry",
                            "amount": amount,
                            "transaction_type": "charge",
                            "category": category,
                            "transaction_date": current_date.strftime("%d"),
                            "statement_year": current_date.year,
                            "statement_month": current_date.month,
                            "bank": "Manual Entry",
                            "file_hash": f"manual_expense_{description.replace(' ', '_')}_{current_date.strftime('%Y%m%d')}",
                            "source": "manual_entries"
                        })
                    current_date += timedelta(days=interval_days)
            
            elif frequency == "weekly":
                interval_days = 7
                while current_date <= end_date:
                    if current_date >= start_date:
                        transactions.append({
                            "merchant_name": description,
                            "merchant_location": "Manual Entry",
                            "amount": amount,
                            "transaction_type": "charge",
                            "category": category,
                            "transaction_date": current_date.strftime("%d"),
                            "statement_year": current_date.year,
                            "statement_month": current_date.month,
                            "bank": "Manual Entry",
                            "file_hash": f"manual_expense_{description.replace(' ', '_')}_{current_date.strftime('%Y%m%d')}",
                            "source": "manual_entries"
                        })
                    current_date += timedelta(days=interval_days)
        
        logger.info(
            "Generated recurring expense transactions",
            extra={
                "count": len(transactions),
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d")
            }
        )
        
        return transactions
    
    def get_adhoc_expenses(
        self, 
        year: Optional[int] = None, 
        month: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get adhoc expenses, optionally filtered by year/month.
        
        Args:
            year: Filter by year (optional)
            month: Filter by month (optional)
            
        Returns:
            List of transaction dictionaries
        """
        data = self.load_manual_entries()
        adhoc_expenses = data.get("adhoc_expenses", [])
        
        transactions = []
        
        for expense in adhoc_expenses:
            # Parse date
            date_str = expense.get("date", "")
            if not date_str:
                continue
            
            try:
                exp_date = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                logger.warning("Invalid date format in adhoc expense", extra={"date": date_str})
                continue
            
            # Filter by year/month if specified
            if year and exp_date.year != year:
                continue
            if month and exp_date.month != month:
                continue
            
            transactions.append({
                "merchant_name": expense.get("description", "Adhoc Expense"),
                "merchant_location": expense.get("merchant", "Manual Entry"),
                "amount": expense.get("amount", 0),
                "transaction_type": "charge",
                "category": expense.get("category", "Other"),
                "transaction_date": exp_date.strftime("%d"),
                "statement_year": exp_date.year,
                "statement_month": exp_date.month,
                "bank": "Manual Entry",
                "file_hash": f"manual_adhoc_{exp_date.strftime('%Y%m%d')}_{expense.get('description', 'expense').replace(' ', '_')}",
                "source": "manual_entries"
            })
        
        logger.info(
            "Retrieved adhoc expenses",
            extra={
                "count": len(transactions),
                "year": year,
                "month": month
            }
        )
        
        return transactions
    
    def get_all_manual_transactions(
        self, 
        year: Optional[int] = None, 
        month: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all manual transactions (income + recurring + adhoc) for period.
        
        Args:
            year: Filter by year (optional)
            month: Filter by month (optional)
            
        Returns:
            Combined list of all manual transactions
        """
        # Determine date range
        if year and month:
            start_date = datetime(year, month, 1)
            # Last day of month
            if month == 12:
                end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = datetime(year, month + 1, 1) - timedelta(days=1)
        elif year:
            start_date = datetime(year, 1, 1)
            end_date = datetime(year, 12, 31)
        else:
            # Default: last 12 months
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
        
        # Generate all transaction types
        income_txns = self.generate_recurring_income(start_date, end_date)
        recurring_expense_txns = self.generate_recurring_expenses(start_date, end_date)
        adhoc_txns = self.get_adhoc_expenses(year, month)
        
        all_transactions = income_txns + recurring_expense_txns + adhoc_txns
        
        logger.info(
            "Retrieved all manual transactions",
            extra={
                "total": len(all_transactions),
                "income": len(income_txns),
                "recurring_expenses": len(recurring_expense_txns),
                "adhoc": len(adhoc_txns),
                "year": year,
                "month": month
            }
        )
        
        return all_transactions


# Singleton instance
manual_entries_service = ManualEntriesService()
