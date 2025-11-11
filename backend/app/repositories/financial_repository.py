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
            # Create transaction document (no account info)
            doc = CreditCardTransaction(
                transaction_date=txn['date'],
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
        
        # Group by category (only charges, not credits)
        category_totals: Dict[str, float] = {}
        for txn in transactions:
            if txn.transaction_type == 'charge' and txn.category:
                category_totals[txn.category] = category_totals.get(txn.category, 0) + txn.amount
        
        return category_totals
    
    async def save_document_metadata(
        self,
        file_hash: str,
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
            file_hash: SHA256 hash of PDF
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
        # Check if already processed
        existing = await FinancialDocumentMetadata.find_one(
            FinancialDocumentMetadata.file_hash == file_hash
        )
        
        if existing:
            return existing
        
        metadata = FinancialDocumentMetadata(
            file_hash=file_hash,
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


# Singleton instances
financial_repository = FinancialRepository()
merchant_category_repository = MerchantCategoryRepository()
