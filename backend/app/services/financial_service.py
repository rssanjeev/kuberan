"""
Financier - Financial Document Processing Service

Security: PDFs are processed in-memory only, never stored.
Only transaction data is persisted to database.
"""

import os
import tempfile
from typing import Dict, Any, BinaryIO
from fastapi import UploadFile
from datetime import datetime

from app.core.chase_parser import parse_chase_statement, calculate_file_hash
from app.repositories.financial_repository import (
    financial_repository,
    merchant_category_repository
)


class FinancierService:
    """Service for processing financial documents."""
    
    async def process_credit_card_statement(
        self,
        file: UploadFile,
        bank: str = "Chase"
    ) -> Dict[str, Any]:
        """
        Process credit card statement PDF.
        
        Security:
        - PDF is written to temp file, processed, then deleted
        - No account information is stored
        - Only transaction data persists to database
        
        Args:
            file: Uploaded PDF file
            bank: Bank name (default: Chase)
            
        Returns:
            Processing results summary
        """
        # Create temporary file for processing
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False) as tmp_file:
            # Write uploaded content to temp file
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        try:
            # Calculate file hash for deduplication
            file_hash = calculate_file_hash(tmp_path)
            
            # Check if already processed
            if await financial_repository.is_document_processed(file_hash):
                return {
                    "status": "duplicate",
                    "message": "This document has already been processed",
                    "file_hash": file_hash
                }
            
            # Parse statement based on bank
            if bank.lower() == "chase":
                extracted_data = parse_chase_statement(tmp_path, include_account_info=False)
            else:
                raise ValueError(f"Unsupported bank: {bank}")
            
            # Extract statement period
            account_info = extracted_data.get('account_info', {})
            statement_period_start = account_info.get('statement_period_start', '')
            statement_period_end = account_info.get('statement_period_end', '')
            
            # Parse year/month from period
            if statement_period_end:
                # Format: MM/DD/YY
                parts = statement_period_end.split('/')
                if len(parts) == 3:
                    statement_month = int(parts[0])
                    statement_year = 2000 + int(parts[2])  # Convert YY to YYYY
                else:
                    # Fallback to current date
                    now = datetime.utcnow()
                    statement_month = now.month
                    statement_year = now.year
            else:
                # Fallback to current date
                now = datetime.utcnow()
                statement_month = now.month
                statement_year = now.year
            
            # Add file hash to transactions
            transactions = extracted_data.get('transactions', [])
            for txn in transactions:
                txn['file_hash'] = file_hash
            
            # Save transactions to database
            transaction_count = await financial_repository.save_transactions(
                transactions=transactions,
                statement_year=statement_year,
                statement_month=statement_month,
                bank=bank
            )
            
            # Calculate totals
            summary = extracted_data.get('summary', {})
            total_charges = abs(float(summary.get('total_charges', 0)))
            total_credits = abs(float(summary.get('total_credits', 0)))
            
            # Save document metadata (no account info)
            await financial_repository.save_document_metadata(
                file_hash=file_hash,
                document_type="credit_card_statement",
                bank=bank,
                statement_year=statement_year,
                statement_month=statement_month,
                statement_period_start=statement_period_start,
                statement_period_end=statement_period_end,
                transaction_count=transaction_count,
                total_charges=total_charges,
                total_credits=total_credits
            )
            
            # Save merchant category mappings
            unique_merchants = {}
            for txn in transactions:
                merchant = txn['description']
                category = txn.get('category', 'Other')
                if merchant not in unique_merchants:
                    unique_merchants[merchant] = category
            
            await merchant_category_repository.bulk_save_mappings(
                mappings=unique_merchants,
                source="auto"
            )
            
            return {
                "status": "success",
                "file_hash": file_hash,
                "bank": bank,
                "statement_period": f"{statement_period_start} to {statement_period_end}",
                "statement_year": statement_year,
                "statement_month": statement_month,
                "transaction_count": transaction_count,
                "total_charges": total_charges,
                "total_credits": total_credits,
                "categories_found": len(set(txn.get('category') for txn in transactions if txn.get('category')))
            }
        
        finally:
            # CRITICAL: Delete temporary PDF file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
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
    
    async def get_all_merchants(self) -> Dict[str, Any]:
        """
        Get all merchants with their category mappings.
        
        Returns:
            List of merchants with categories
        """
        mappings = await merchant_category_repository.get_all_merchants()
        
        return {
            "count": len(mappings),
            "merchants": [
                {
                    "merchant": m.merchant_name,
                    "category": m.category,
                    "source": m.source,
                    "confidence": m.confidence,
                    "last_updated": m.updated_at.isoformat()
                }
                for m in mappings
            ]
        }
    
    async def get_merchants_by_category(self, category: str) -> Dict[str, Any]:
        """
        Get all merchants in a specific category.
        
        Args:
            category: Category name
            
        Returns:
            List of merchants in that category
        """
        mappings = await merchant_category_repository.get_merchants_by_category(category)
        
        return {
            "category": category,
            "count": len(mappings),
            "merchants": [
                {
                    "merchant": m.merchant_name,
                    "source": m.source,
                    "confidence": m.confidence,
                    "last_updated": m.updated_at.isoformat()
                }
                for m in mappings
            ]
        }
    
    async def update_merchant_category(
        self,
        merchant_name: str,
        new_category: str
    ) -> Dict[str, Any]:
        """
        Reassign a merchant to a different category.
        Updates both the merchant mapping and all related transactions.
        
        Args:
            merchant_name: Merchant name
            new_category: New category to assign
            
        Returns:
            Update result
        """
        mapping = await merchant_category_repository.update_merchant_category(
            merchant_name=merchant_name,
            new_category=new_category,
            source="manual"
        )
        
        if not mapping:
            raise ValueError(f"Merchant '{merchant_name}' not found")
        
        return {
            "status": "success",
            "message": f"Merchant '{merchant_name}' reassigned to '{new_category}'",
            "merchant": merchant_name,
            "old_category": mapping.category if mapping else None,
            "new_category": new_category
        }
    
    async def add_custom_category(self, category_name: str) -> Dict[str, Any]:
        """
        Add a new custom category.
        
        Args:
            category_name: Name of the new category
            
        Returns:
            Status result
        """
        return await merchant_category_repository.add_custom_category(category_name)
    
    async def analyze_transactions(
        self,
        year: int = None,
        month: int = None,
        category: str = None
    ) -> Dict[str, Any]:
        """
        Detailed transaction analysis by month, year, and category.
        
        Args:
            year: Filter by year
            month: Filter by month
            category: Filter by category
            
        Returns:
            Detailed analysis with statistics, top merchants, and trends
        """
        # Get filtered transactions
        transactions = await financial_repository.get_transactions(
            year=year,
            month=month,
            category=category,
            limit=10000  # Get all matching transactions for analysis
        )
        
        if not transactions:
            return {
                "filters": {"year": year, "month": month, "category": category},
                "transaction_count": 0,
                "message": "No transactions found for the specified filters"
            }
        
        # Calculate statistics
        amounts = [txn.amount for txn in transactions]
        total_spending = sum(amounts)
        avg_transaction = total_spending / len(transactions)
        max_transaction = max(amounts)
        min_transaction = min(amounts)
        
        # Top merchants by spending
        merchant_totals = {}
        merchant_counts = {}
        for txn in transactions:
            merchant = txn.merchant_name
            merchant_totals[merchant] = merchant_totals.get(merchant, 0) + txn.amount
            merchant_counts[merchant] = merchant_counts.get(merchant, 0) + 1
        
        top_merchants = sorted(
            merchant_totals.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Category breakdown (if not filtering by category)
        category_breakdown = {}
        if not category:
            for txn in transactions:
                cat = txn.category
                category_breakdown[cat] = category_breakdown.get(cat, 0) + txn.amount
            
            category_breakdown = sorted(
                category_breakdown.items(),
                key=lambda x: x[1],
                reverse=True
            )
        
        # Day-of-month breakdown (if month and year specified)
        daily_breakdown = {}
        if year and month:
            for txn in transactions:
                day = txn.transaction_date
                daily_breakdown[day] = daily_breakdown.get(day, 0) + txn.amount
            
            daily_breakdown = dict(sorted(daily_breakdown.items()))
        
        # Month breakdown (if only year specified)
        monthly_breakdown = {}
        if year and not month:
            from datetime import date
            for txn in transactions:
                txn_month = txn.statement_month
                txn_year = txn.statement_year
                # Create month label like "Sep 25" or "Nov 25"
                month_name = date(txn_year, txn_month, 1).strftime("%b %y")
                monthly_breakdown[month_name] = monthly_breakdown.get(month_name, 0) + txn.amount
            
            # Sort by actual month number for chronological order
            monthly_breakdown = dict(sorted(
                monthly_breakdown.items(),
                key=lambda x: datetime.strptime(x[0], "%b %y")
            ))
        
        # Build response
        result = {
            "filters": {
                "year": year,
                "month": month,
                "category": category
            },
            "summary": {
                "transaction_count": len(transactions),
                "total_spending": round(total_spending, 2),
                "average_transaction": round(avg_transaction, 2),
                "max_transaction": round(max_transaction, 2),
                "min_transaction": round(min_transaction, 2)
            },
            "top_merchants": [
                {
                    "merchant": merchant,
                    "total_spent": round(amount, 2),
                    "transaction_count": merchant_counts[merchant],
                    "average_per_transaction": round(amount / merchant_counts[merchant], 2)
                }
                for merchant, amount in top_merchants
            ]
        }
        
        # Add category breakdown if available
        if category_breakdown:
            result["category_breakdown"] = [
                {
                    "category": cat,
                    "amount": round(amt, 2),
                    "percentage": round((amt / total_spending) * 100, 1)
                }
                for cat, amt in category_breakdown
            ]
        
        # Add daily breakdown if available
        if daily_breakdown:
            result["daily_spending"] = [
                {"day": day, "amount": round(amt, 2)}
                for day, amt in daily_breakdown.items()
            ]
        
        # Add monthly breakdown if available
        if monthly_breakdown:
            result["monthly_spending"] = [
                {"month": month_label, "amount": round(amt, 2)}
                for month_label, amt in monthly_breakdown.items()
            ]
        
        return result


# Singleton instance
financier = FinancierService()
