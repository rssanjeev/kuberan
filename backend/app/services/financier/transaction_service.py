"""
Transaction Service - Transaction Query and Retrieval

Provides read-only access to transaction data with filtering capabilities.
"""

from typing import Dict, Any
from app.repositories.financial_repository import financial_repository


class TransactionService:
    """Service for querying and retrieving transaction data."""
    
    async def get_transactions(
        self,
        year: int = None,
        month: int = None,
        category: str = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Get transactions with filters.
        
        Args:
            year: Filter by year
            month: Filter by month
            category: Filter by category
            limit: Maximum results
            
        Returns:
            Transactions list
        """
        transactions = await financial_repository.get_transactions(
            year=year,
            month=month,
            category=category,
            limit=limit
        )
        
        return {
            "count": len(transactions),
            "transactions": [
                {
                    "_id": str(txn.id),  # Include MongoDB ObjectId for editing
                    "date": f"{txn.statement_year}/{txn.statement_month:02d}/{txn.transaction_date}",
                    "merchant": txn.merchant_name,
                    "location": txn.merchant_location,
                    "amount": txn.amount,
                    "type": txn.transaction_type,
                    "category": txn.category,
                    "bank": txn.bank
                }
                for txn in transactions
            ]
        }
    
    async def get_spending_summary(
        self,
        year: int = None,
        month: int = None
    ) -> Dict[str, Any]:
        """
        Get spending summary by category.
        
        Args:
            year: Filter by year
            month: Filter by month
            
        Returns:
            Spending breakdown by category
        """
        category_totals = await financial_repository.get_spending_by_category(
            year=year,
            month=month
        )
        
        # Sort by amount descending
        sorted_categories = sorted(
            category_totals.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        total_spending = sum(category_totals.values())
        
        return {
            "total_spending": round(total_spending, 2),
            "category_breakdown": [
                {
                    "category": cat,
                    "amount": round(amt, 2),
                    "percentage": round((amt / total_spending * 100) if total_spending > 0 else 0, 1)
                }
                for cat, amt in sorted_categories
            ]
        }


# Singleton instance
transaction_service = TransactionService()
