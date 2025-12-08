"""
Document Processor Service - Bank Statement PDF Processing

Security: PDFs are processed in-memory only, never stored.
Only transaction data is persisted to database.
"""

import os
import tempfile
from typing import Dict, Any
from fastapi import UploadFile
from datetime import datetime

from app.core.chase_parser import parse_chase_statement, calculate_file_hash
from app.core.checking_account_parser import parse_checking_statement
from app.core.logging_config import get_logger
from app.repositories.financial_repository import (
    financial_repository,
    merchant_category_repository
)

logger = get_logger(__name__)


class DocumentProcessorService:
    """Service for processing financial document PDFs."""
    
    async def process_credit_card_statement(
        self,
        file: UploadFile,
        bank: str = "Chase",
        statement_type: str = "credit_card"
    ) -> Dict[str, Any]:
        """
        Process bank statement PDF (credit card or checking account).
        
        Security:
        - PDF is written to temp file, processed, then deleted
        - No account information is stored
        - Only transaction data persists to database
        
        Args:
            file: Uploaded PDF file
            bank: Bank name (default: Chase)
            statement_type: Type of statement - credit_card or checking_account (default: credit_card)
            
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
            # Calculate file hash for deduplication (fallback method)
            file_hash = calculate_file_hash(tmp_path)
            
            logger.info(
                "📊 File hash calculated",
                extra={"hash": file_hash[:16], "full_hash": file_hash}
            )
            
            # Parse statement first to extract statement period
            # Parse statement based on type and bank
            if statement_type == "credit_card":
                if bank.lower() == "chase":
                    extracted_data = parse_chase_statement(tmp_path, include_account_info=False)
                else:
                    raise ValueError(f"Unsupported bank for credit cards: {bank}")
            elif statement_type == "checking_account":
                raise ValueError(
                    "Checking account statement uploads are disabled. "
                    "Use credit card statements for expense tracking, or add manual entries "
                    "to the manual_entries.json file for checking account income/expenses."
                )
            else:
                raise ValueError(f"Unsupported statement type: {statement_type}")
            
            # Extract statement period for duplicate detection (PRIMARY METHOD)
            account_info = extracted_data.get('account_info', {})
            statement_period = account_info.get('statement_period')  # e.g., "10/27/25 - 11/26/25"
            
            logger.info(
                "📅 Statement period extracted",
                extra={"statement_period": statement_period}
            )
            
            # Check for duplicate by statement period (PRIMARY) or file hash (FALLBACK)
            existing_metadata = None
            
            if statement_period:
                # Primary: Check by statement period (more reliable)
                existing_metadata = await financial_repository.get_document_by_period(statement_period)
                if existing_metadata:
                    logger.info(
                        "🔍 Duplicate check: Found existing statement by period",
                        extra={"statement_period": statement_period}
                    )
            
            if not existing_metadata:
                # Fallback: Check by file hash
                existing_metadata = await financial_repository.get_document_by_hash(file_hash)
                if existing_metadata:
                    logger.info(
                        "🔍 Duplicate check: Found existing statement by file hash",
                        extra={"file_hash": file_hash[:16]}
                    )
            
            if existing_metadata:
                # Check if orphaned (has metadata but no transactions)
                txn_count = await financial_repository.count_transactions_by_statement(
                    existing_metadata.statement_year,
                    existing_metadata.statement_month
                )
                
                if txn_count == 0:
                    # Orphaned metadata - delete and allow re-upload
                    logger.info(
                        "🗑️ Orphaned metadata found (0 transactions), deleting and allowing re-upload",
                        extra={
                            "file_hash": file_hash[:16],
                            "statement_period": statement_period,
                            "year": existing_metadata.statement_year,
                            "month": existing_metadata.statement_month
                        }
                    )
                    await financial_repository.delete_document_metadata(file_hash)
                else:
                    # Has transactions - reject as duplicate
                    period_display = existing_metadata.statement_period or f"{existing_metadata.statement_year}-{existing_metadata.statement_month:02d}"
                    logger.warning(
                        f"❌ DUPLICATE REJECTED: Statement period '{period_display}' already processed ({txn_count} transactions)",
                        extra={
                            "uploaded_file": file.filename,
                            "statement_period": period_display,
                            "matches_year": existing_metadata.statement_year,
                            "matches_month": existing_metadata.statement_month,
                            "transaction_count": txn_count,
                            "file_hash": file_hash[:16]
                        }
                    )
                    return {
                        "status": "duplicate",
                        "message": f"Statement period '{period_display}' is already processed ({txn_count} transactions found)",
                        "existing_year": existing_metadata.statement_year,
                        "existing_month": existing_metadata.statement_month,
                        "statement_period": period_display,
                        "transaction_count": txn_count
                    }
            
            # Extract statement period dates based on statement type
            if statement_type == "credit_card":
                account_info = extracted_data.get('account_info', {})
                statement_period_start = account_info.get('statement_period_start', '')
                statement_period_end = account_info.get('statement_period_end', '')
                
                # Parse year/month from period (format: MM/DD/YY)
                if statement_period_end:
                    parts = statement_period_end.split('/')
                    if len(parts) == 3:
                        statement_month = int(parts[0])
                        statement_year = 2000 + int(parts[2])  # Convert YY to YYYY
                    else:
                        now = datetime.utcnow()
                        statement_month = now.month
                        statement_year = now.year
                else:
                    now = datetime.utcnow()
                    statement_month = now.month
                    statement_year = now.year
                    
            else:  # checking_account
                period = extracted_data.get('statement_period', {})
                statement_period_start = period.get('start_date', '')  # YYYY-MM-DD format
                statement_period_end = period.get('end_date', '')
                statement_month = int(period.get('statement_month', datetime.utcnow().month))
                statement_year = int(period.get('statement_year', datetime.utcnow().year))
            
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
            
            # Calculate totals based on statement type
            summary = extracted_data.get('summary', {})
            if statement_type == "credit_card":
                total_charges = abs(float(summary.get('total_charges', 0)))
                total_credits = abs(float(summary.get('total_credits', 0)))
            else:  # checking_account
                total_charges = abs(float(summary.get('total_withdrawals', 0)))
                total_credits = abs(float(summary.get('total_deposits', 0)))
            
            # Save document metadata (no account info)
            document_type = "credit_card_statement" if statement_type == "credit_card" else "checking_account_statement"
            
            await financial_repository.save_document_metadata(
                file_hash=file_hash,
                statement_period=statement_period,  # Add statement period for duplicate detection
                document_type=document_type,
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


# Singleton instance
document_processor = DocumentProcessorService()
