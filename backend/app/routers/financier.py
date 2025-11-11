"""
Financial Documents API Router

Security: All endpoints designed to handle financial data discreetly.
No account information is exposed or stored.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from typing import Optional

from app.services.financial_service import financier

router = APIRouter(prefix="/documents", tags=["Financier"])


@router.post("/upload")
async def upload_financial_document(
    file: UploadFile = File(...),
    bank: str = Query(default="Chase", description="Bank name (Chase, Amex, etc.)")
):
    """
    Upload and process a credit card statement PDF.
    
    Security Features:
    - PDF is processed in-memory only, never stored
    - Only transaction data (merchant, amount, category) is saved
    - Account numbers and personal info are NOT stored
    - File hash used for deduplication
    
    Args:
        file: PDF file upload
        bank: Bank name (default: Chase)
        
    Returns:
        Processing summary with transaction counts
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        result = await financier.process_credit_card_statement(
            file=file,
            bank=bank
        )
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        )


@router.get("/transactions")
async def get_transactions(
    year: Optional[int] = Query(None, description="Filter by year"),
    month: Optional[int] = Query(None, description="Filter by month (1-12)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(100, description="Maximum number of results")
):
    """
    Get credit card transactions with optional filters.
    
    Returns only transaction-level data (no account info).
    
    Args:
        year: Filter by statement year
        month: Filter by statement month
        category: Filter by category
        limit: Maximum results (default: 100)
        
    Returns:
        List of transactions
    """
    try:
        result = await financier.get_transactions(
            year=year,
            month=month,
            category=category,
            limit=limit
        )
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving transactions: {str(e)}"
        )


@router.get("/spending/summary")
async def get_spending_summary(
    year: Optional[int] = Query(None, description="Filter by year"),
    month: Optional[int] = Query(None, description="Filter by month (1-12)")
):
    """
    Get spending summary grouped by category.
    
    Args:
        year: Filter by year
        month: Filter by month
        
    Returns:
        Spending breakdown by category with percentages
    """
    try:
        result = await financier.get_spending_summary(
            year=year,
            month=month
        )
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating spending summary: {str(e)}"
        )


@router.get("/categories")
async def get_categories():
    """
    Get list of all transaction categories.
    
    Returns:
        List of category names
    """
    from app.repositories.financial_repository import merchant_category_repository
    
    try:
        categories = await merchant_category_repository.get_all_categories()
        return {
            "count": len(categories),
            "categories": categories
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving categories: {str(e)}"
        )
