"""
Repository for financial document and transaction data access.

Security Principles:
- No account numbers or sensitive info stored in database
- PDF files are NEVER stored, only processed data
- Focus on transaction-level analysis only
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from beanie.operators import In

from app.models import (
    CreditCardTransaction,
    MerchantCategory,
    FinancialDocumentMetadata
)
from app.core.logging_config import get_logger

logger = get_logger(__name__)

class FinancialRepository:
    """Repository for financial document operations."""
    
    async def save_transactions(
        self,
        transactions: List[Dict[str, Any]],
        statement_year: int,
        statement_month: int,
        bank: str
    ) -> int:
        """
        Save credit card transactions to database.
        
        Args:
            transactions: List of transaction dictionaries
            statement_year: Year of statement
            statement_month: Month of statement
            bank: Bank name
            
        Returns:
            Number of transactions saved
        """
        transaction_docs = []
        
        for txn in transactions:
            # Parse transaction date to determine actual year/month
            # Transaction date format: MM/DD
            date_parts = txn['date'].split('/')
            if len(date_parts) == 2:
                txn_month = int(date_parts[0])
                
                # Infer transaction year based on statement period
                # If transaction month > statement month, it's from previous year
                # (e.g., Nov statement with Oct transactions when due date is 23rd)
                if txn_month > statement_month:
                    txn_year = statement_year - 1
                else:
                    txn_year = statement_year
            else:
                # Fallback: use statement month/year
                txn_month = statement_month
                txn_year = statement_year
            
            # Create transaction document (no account info)
            doc = CreditCardTransaction(
                transaction_date=txn['date'],
                transaction_year=txn_year,
                transaction_month=txn_month,
                statement_year=statement_year,
                statement_month=statement_month,
                merchant_name=txn['description'],
                merchant_location=txn.get('location', ''),
                amount=float(txn['amount']),
                transaction_type=txn['type'],
                category=txn.get('category'),
                bank=bank,
                raw_description=txn.get('raw_line', txn['description']),
                imported_at=datetime.utcnow(),
                source_file_hash=txn.get('file_hash')
            )
            transaction_docs.append(doc)
        
        # Bulk insert
        if transaction_docs:
            await CreditCardTransaction.insert_many(transaction_docs)
        
        return len(transaction_docs)
    
    async def get_transactions(
        self,
        year: Optional[int] = None,
        month: Optional[int] = None,
        category: Optional[str] = None,
        bank: Optional[str] = None,
        limit: int = 100
    ) -> List[CreditCardTransaction]:
        """
        Query credit card transactions with filters.
        
        Args:
            year: Filter by statement year
            month: Filter by statement month
            category: Filter by category
            bank: Filter by bank
            limit: Maximum results
            
        Returns:
            List of transactions
        """
        query = {}
        
        if year:
            query['statement_year'] = year
        if month:
            query['statement_month'] = month
        if category:
            query['category'] = category
        if bank:
            query['bank'] = bank
        
        transactions = await CreditCardTransaction.find(
            query
        ).sort('-statement_year', '-statement_month').limit(limit).to_list()
        
        return transactions
    
    async def get_spending_by_category(
        self,
        year: Optional[int] = None,
        month: Optional[int] = None
    ) -> Dict[str, float]:
        """
        Get total spending grouped by category.
        
        Args:
            year: Filter by year
            month: Filter by month
            
        Returns:
            Dictionary of category -> total amount
        """
        query = {}
        if year:
            query['statement_year'] = year
        if month:
            query['statement_month'] = month
        
        transactions = await CreditCardTransaction.find(query).to_list()
        
        # Group by category (only charges/expenses, not credits/income)
        # For credit cards: transaction_type == 'charge' (positive amounts)
        # For checking accounts: amount < 0 (expenses/withdrawals, stored as negative)
        # EXCLUDE: Income, Zelle Received, Investments (not spending categories)
        category_totals: Dict[str, float] = {}
        for txn in transactions:
            if not txn.category:
                continue
            
            # Exclude non-spending categories
            excluded_categories = {'Income', 'Zelle Received', 'Investments'}
            if txn.category in excluded_categories:
                continue
            
            # Include if:
            # 1. Credit card charge (positive amount)
            # 2. Checking account expense (negative amount)
            is_charge = txn.transaction_type == 'charge'
            is_checking_expense = (txn.amount < 0)
            
            if is_charge or is_checking_expense:
                # Use absolute value for spending totals
                category_totals[txn.category] = category_totals.get(txn.category, 0) + abs(txn.amount)
        
        return category_totals
    
    async def save_document_metadata(
        self,
        file_hash: str,
        statement_period: Optional[str],  # Add statement period (PRIMARY duplicate detection)
        document_type: str,
        bank: Optional[str],
        statement_year: int,
        statement_month: int,
        statement_period_start: Optional[str],
        statement_period_end: Optional[str],
        transaction_count: int,
        total_charges: float,
        total_credits: float
    ) -> FinancialDocumentMetadata:
        """
        Save financial document metadata (no actual PDF stored).
        
        Args:
            file_hash: SHA256 hash of PDF (FALLBACK for duplicate detection)
            statement_period: Statement period string (PRIMARY for duplicate detection, e.g., "10/27/25 - 11/26/25")
            document_type: Type of document
            bank: Bank name
            statement_year: Year
            statement_month: Month
            statement_period_start: Period start date
            statement_period_end: Period end date
            transaction_count: Number of transactions
            total_charges: Total charge amount
            total_credits: Total credit amount
            
        Returns:
            Created metadata document
        """
        # Check if already processed (by period first, then hash)
        existing = None
        if statement_period:
            existing = await FinancialDocumentMetadata.find_one(
                FinancialDocumentMetadata.statement_period == statement_period
            )
        
        if not existing:
            existing = await FinancialDocumentMetadata.find_one(
                FinancialDocumentMetadata.file_hash == file_hash
            )
        
        if existing:
            return existing
        
        metadata = FinancialDocumentMetadata(
            file_hash=file_hash,
            statement_period=statement_period,  # Store statement period
            document_type=document_type,
            bank=bank,
            statement_year=statement_year,
            statement_month=statement_month,
            statement_period_start=statement_period_start,
            statement_period_end=statement_period_end,
            processed_at=datetime.utcnow(),
            transaction_count=transaction_count,
            total_charges=total_charges,
            total_credits=total_credits
        )
        
        await metadata.insert()
        return metadata
    
    async def get_income_from_payroll(
        self,
        year: Optional[int] = None,
        month: Optional[int] = None
    ) -> float:
        """
        Calculate total income from payroll deposits.
        
        Args:
            year: Filter by year
            month: Filter by month
            
        Returns:
            Total income from payroll deposits
        """
        query = {'category': 'Income'}
        if year:
            query['statement_year'] = year
        if month:
            query['statement_month'] = month
        
        transactions = await CreditCardTransaction.find(query).to_list()
        total_income = sum(abs(txn.amount) for txn in transactions if txn.amount > 0)
        
        return total_income
    
    async def get_investment_transactions(
        self,
        year: Optional[int] = None,
        month: Optional[int] = None,
        months_back: int = 12
    ) -> List[CreditCardTransaction]:
        """
        Get investment transactions for rolling analysis.
        
        Args:
            year: Filter by year
            month: Filter by month
            months_back: Number of months to look back (default 12)
            
        Returns:
            List of investment transactions
        """
        query = {'category': 'Investments'}
        if year:
            query['statement_year'] = year
        if month:
            query['statement_month'] = month
        
        transactions = await CreditCardTransaction.find(
            query
        ).sort('-statement_year', '-statement_month').limit(months_back * 50).to_list()
        
        return transactions
    
    async def is_document_processed(self, file_hash: str) -> bool:
        """
        Check if document has already been processed.
        
        Args:
            file_hash: SHA256 hash of PDF
            
        Returns:
            True if already processed
        """
        existing = await FinancialDocumentMetadata.find_one(
            FinancialDocumentMetadata.file_hash == file_hash
        )
        return existing is not None
    
    async def get_document_by_hash(self, file_hash: str) -> Optional[FinancialDocumentMetadata]:
        """
        Get document metadata by file hash.
        
        Args:
            file_hash: SHA256 hash of PDF
            
        Returns:
            Document metadata or None
        """
        return await FinancialDocumentMetadata.find_one(
            FinancialDocumentMetadata.file_hash == file_hash
        )
    
    async def get_document_by_period(self, statement_period: str) -> Optional[FinancialDocumentMetadata]:
        """
        Get document metadata by statement period (PRIMARY duplicate detection method).
        
        Args:
            statement_period: Statement period string (e.g., "10/27/25 - 11/26/25")
            
        Returns:
            Document metadata or None
        """
        return await FinancialDocumentMetadata.find_one(
            FinancialDocumentMetadata.statement_period == statement_period
        )
    
    async def count_transactions_by_statement(self, year: int, month: int) -> int:
        """
        Count transactions for a specific statement period.
        
        Args:
            year: Statement year
            month: Statement month
            
        Returns:
            Number of transactions
        """
        return await CreditCardTransaction.find(
            CreditCardTransaction.statement_year == year,
            CreditCardTransaction.statement_month == month
        ).count()
    
    async def delete_document_metadata(self, file_hash: str) -> bool:
        """
        Delete document metadata by file hash.
        
        Args:
            file_hash: SHA256 hash of PDF
            
        Returns:
            True if deleted, False if not found
        """
        doc = await FinancialDocumentMetadata.find_one(
            FinancialDocumentMetadata.file_hash == file_hash
        )
        if doc:
            await doc.delete()
            return True
        return False
    
    async def update_transaction_category(
        self,
        transaction_id: str,
        new_category: str,
        update_all_from_merchant: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Update the category of a specific transaction.
        Optionally update all transactions from the same merchant.
        
        Args:
            transaction_id: MongoDB ObjectId string of transaction
            new_category: New category name to assign
            update_all_from_merchant: If True, update all transactions from same merchant
            
        Returns:
            Dictionary with updated transaction and count of updates
            
        Raises:
            ValueError: If transaction_id is invalid or category is empty
        """
        from bson import ObjectId
        from bson.errors import InvalidId
        
        # Validate inputs
        if not new_category or not new_category.strip():
            raise ValueError("Category cannot be empty")
        
        try:
            obj_id = ObjectId(transaction_id)
        except InvalidId:
            raise ValueError(f"Invalid transaction ID format: {transaction_id}")
        
        # Find and update transaction
        transaction = await CreditCardTransaction.find_one(
            CreditCardTransaction.id == obj_id
        )
        
        if not transaction:
            return None
        
        # Update category
        transaction.category = new_category.strip()
        await transaction.save()
        
        updated_count = 1
        
        # If requested, update all transactions from same merchant
        if update_all_from_merchant:
            merchant_name = transaction.merchant_name
            
            # Update all other transactions from this merchant
            other_transactions = await CreditCardTransaction.find(
                CreditCardTransaction.merchant_name == merchant_name,
                CreditCardTransaction.id != obj_id
            ).to_list()
            
            for txn in other_transactions:
                txn.category = new_category.strip()
                await txn.save()
                updated_count += 1
            
            logger.info(
                "Bulk updated transactions from merchant",
                extra={
                    "merchant": merchant_name,
                    "category": new_category,
                    "count": updated_count
                }
            )
            
            # Also update the merchant mapping for future transactions
            # Import at runtime to avoid circular reference issue
            try:
                logger.info(
                    "Saving merchant mapping",
                    extra={"merchant": merchant_name, "category": new_category.strip()}
                )
                
                # Create or update merchant mapping directly
                existing_mapping = await MerchantCategory.find_one(
                    MerchantCategory.merchant_name == merchant_name
                )
                
                if existing_mapping:
                    existing_mapping.category = new_category.strip()
                    existing_mapping.confidence = 1.0
                    existing_mapping.source = "manual"
                    existing_mapping.updated_at = datetime.utcnow()
                    await existing_mapping.save()
                    logger.info(
                        "Updated existing merchant mapping",
                        extra={"merchant": merchant_name, "mapping_id": str(existing_mapping.id)}
                    )
                else:
                    new_mapping = MerchantCategory(
                        merchant_name=merchant_name,
                        category=new_category.strip(),
                        confidence=1.0,
                        source="manual"
                    )
                    await new_mapping.insert()
                    logger.info(
                        "Created new merchant mapping",
                        extra={"merchant": merchant_name, "mapping_id": str(new_mapping.id)}
                    )
                    
            except Exception as e:
                logger.error(
                    "Failed to save merchant mapping",
                    extra={
                        "merchant": merchant_name,
                        "category": new_category.strip(),
                        "error": str(e)
                    },
                    exc_info=True
                )
                # Don't fail the whole operation - transactions already updated successfully
        
        return {
            "transaction": transaction,
            "updated_count": updated_count,
            "merchant": transaction.merchant_name,
            "updated_all_from_merchant": update_all_from_merchant
        }


class MerchantCategoryRepository:
    """Repository for merchant category mappings."""
    
    async def get_category(self, merchant_name: str) -> Optional[str]:
        """
        Get category for a merchant.
        
        Args:
            merchant_name: Merchant name
            
        Returns:
            Category name or None
        """
        mapping = await MerchantCategory.find_one(
            MerchantCategory.merchant_name == merchant_name
        )
        
        return mapping.category if mapping else None
    
    async def save_mapping(
        self,
        merchant_name: str,
        category: str,
        confidence: float = 1.0,
        source: str = "manual"
    ) -> MerchantCategory:
        """
        Save or update merchant category mapping.
        
        Args:
            merchant_name: Merchant name
            category: Category name
            confidence: Confidence score
            source: Source of mapping
            
        Returns:
            Created/updated mapping
        """
        existing = await MerchantCategory.find_one(
            MerchantCategory.merchant_name == merchant_name
        )
        
        if existing:
            existing.category = category
            existing.confidence = confidence
            existing.source = source
            existing.updated_at = datetime.utcnow()
            await existing.save()
            return existing
        
        mapping = MerchantCategory(
            merchant_name=merchant_name,
            category=category,
            confidence=confidence,
            source=source,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        await mapping.insert()
        return mapping
    
    async def bulk_save_mappings(
        self,
        mappings: Dict[str, str],
        source: str = "auto"
    ) -> int:
        """
        Bulk save merchant category mappings.
        
        Args:
            mappings: Dictionary of merchant_name -> category
            source: Source of mappings
            
        Returns:
            Number of mappings saved
        """
        count = 0
        for merchant_name, category in mappings.items():
            await self.save_mapping(merchant_name, category, 1.0, source)
            count += 1
        
        return count
    
    async def get_all_categories(self) -> List[str]:
        """
        Get list of all unique categories.
        
        Returns:
            List of category names
        """
        mappings = await MerchantCategory.find_all().to_list()
        categories = sorted(set(m.category for m in mappings))
        return categories
    
    async def get_all_merchants(self) -> List[MerchantCategory]:
        """
        Get all merchant category mappings.
        
        Returns:
            List of all merchant mappings
        """
        mappings = await MerchantCategory.find_all().sort('merchant_name').to_list()
        return mappings
    
    async def get_merchants_by_category(self, category: str) -> List[MerchantCategory]:
        """
        Get all merchants in a specific category.
        
        Args:
            category: Category name
            
        Returns:
            List of merchant mappings in that category
        """
        mappings = await MerchantCategory.find(
            MerchantCategory.category == category
        ).sort('merchant_name').to_list()
        return mappings
    
    async def update_merchant_category(
        self,
        merchant_name: str,
        new_category: str,
        source: str = "manual"
    ) -> Optional[MerchantCategory]:
        """
        Update the category for a merchant and update all related transactions.
        
        Args:
            merchant_name: Merchant name
            new_category: New category name
            source: Source of update (default: manual)
            
        Returns:
            Updated merchant mapping or None if not found
        """
        # Update merchant mapping
        mapping = await self.save_mapping(merchant_name, new_category, 1.0, source)
        
        # Update all transactions with this merchant
        from app.models import CreditCardTransaction
        transactions = await CreditCardTransaction.find(
            CreditCardTransaction.merchant_name == merchant_name
        ).to_list()
        
        for txn in transactions:
            txn.category = new_category
            await txn.save()
        
        return mapping
    
    async def add_custom_category(self, category_name: str) -> Dict[str, Any]:
        """
        Add a new custom category (validated by checking if it exists).
        
        Args:
            category_name: Name of the new category
            
        Returns:
            Status dictionary
        """
        # Check if category already exists
        existing_categories = await self.get_all_categories()
        
        if category_name in existing_categories:
            return {
                "status": "exists",
                "message": f"Category '{category_name}' already exists"
            }
        
        # Category will be created when first merchant is assigned to it
        # For now, just return success
        return {
            "status": "success",
            "message": f"Category '{category_name}' is ready to use",
            "category": category_name
        }


# Singleton instances
financial_repository = FinancialRepository()
merchant_category_repository = MerchantCategoryRepository()
