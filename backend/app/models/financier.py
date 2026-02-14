"""
Financier domain models.

Models:
- MerchantCategory: Merchant-to-category mappings
- CreditCardTransaction: Parsed credit card transactions
- FinancialDocumentMetadata: Metadata about processed statements

Security: No account numbers or sensitive information stored.
"""

from beanie import Document
from typing import Optional
from datetime import datetime


class MerchantCategory(Document):
    """
    Store merchant-to-category mappings for transaction categorization.
    Used to automatically categorize transactions based on merchant patterns.
    """
    merchant_name: str  # Exact merchant name from transaction
    category: str  # Category name (e.g., "Coffee & Cafes", "Groceries")
    confidence: float = 1.0  # Confidence score (0.0-1.0) for auto-categorization
    source: str = "manual"  # "manual", "auto", "ml"
    created_at: datetime
    updated_at: datetime
    
    class Settings:
        name = "merchant_categories"
        indexes = [
            "merchant_name",  # Unique index on merchant name
            "category",
        ]


class CreditCardTransaction(Document):
    """
    Store credit card transactions parsed from statements.
    Security: No account numbers or sensitive account info stored.
    Focus: Transaction-level data only for expense analysis.
    """
    # Transaction identification (no account info)
    transaction_date: str  # MM/DD format from statement (where MM=month, DD=day)
    transaction_year: int  # Actual year of transaction (inferred from statement period)
    transaction_month: int  # Actual month of transaction (from MM in MM/DD)
    statement_year: int  # Year of statement
    statement_month: int  # Month of statement (for grouping)
    
    # Merchant information
    merchant_name: str  # Merchant description
    merchant_location: Optional[str] = None  # Location/state if available
    
    # Transaction details
    amount: float  # Positive for charges, negative for credits/payments
    transaction_type: str  # "charge" or "credit"
    category: Optional[str] = None  # Auto-assigned category
    
    # Metadata (no sensitive data)
    bank: str  # "Chase", "Amex", etc.
    raw_description: str  # Original transaction line for reference
    
    # Processing info
    imported_at: datetime
    source_file_hash: Optional[str] = None  # SHA256 hash of PDF (for deduplication)
    
    class Settings:
        name = "credit_card_transactions"
        indexes = [
            "statement_year",
            "statement_month",
            "category",
            "merchant_name",
            "bank",
            [("statement_year", -1), ("statement_month", -1)],  # Recent first
            [("category", 1), ("statement_year", -1)],  # Category analysis
        ]


class FinancialDocumentMetadata(Document):
    """
    Store minimal metadata about processed financial documents.
    Security: PDF file itself is NEVER stored, only processing metadata.
    """
    file_hash: str  # SHA256 hash of PDF (for deduplication)
    statement_period: Optional[str] = None  # "MM/DD/YY - MM/DD/YY" (unique identifier for each statement)
    document_type: str  # "credit_card_statement", "payslip", etc.
    bank: Optional[str] = None  # Bank name if credit card
    
    # Statement period (no account info)
    statement_year: int
    statement_month: int
    statement_period_start: Optional[str] = None  # MM/DD/YY format
    statement_period_end: Optional[str] = None  # MM/DD/YY format
    
    # Processing info
    processed_at: datetime
    transaction_count: int  # Number of transactions extracted
    total_charges: float
    total_credits: float
    
    class Settings:
        name = "financial_document_metadata"
        indexes = [
            "file_hash",  # Unique index for deduplication
            "document_type",
            "bank",
            [("statement_year", -1), ("statement_month", -1)],
        ]
