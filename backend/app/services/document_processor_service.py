"""
Document Processor Service - Credit Card Statement PDF Processing

Security: PDFs are processed in-memory only, never stored.
Only transaction data is persisted to database.
"""

import os
import tempfile
from typing import Dict, Any
from fastapi import UploadFile
from datetime import datetime

from app.core.chase_parser import parse_chase_statement, calculate_file_hash
from app.repositories.financial_repository import (
    financial_repository,
    merchant_category_repository
)


class DocumentProcessorService:
    """Service for processing financial document PDFs."""
    
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


# Singleton instance
document_processor = DocumentProcessorService()
