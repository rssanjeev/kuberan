"""
Financial Documents API Router

Security: All endpoints designed to handle financial data discreetly.
No account information is exposed or stored.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from typing import Optional, List

from app.services.financial_service import financier

router = APIRouter(prefix="/financier", tags=["Financier"])


@router.post("/upload")
async def upload_financial_document(
    file: UploadFile = File(...),
    bank: str = Query(default="Chase", description="Bank name (Chase, Amex, etc.)")
):
    """
    Upload and process a single credit card statement PDF.
    
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


@router.post("/upload/batch")
async def upload_multiple_financial_documents(
    files: List[UploadFile] = File(...),
    bank: str = Query(default="Chase", description="Bank name (Chase, Amex, etc.)")
):
    """
    Upload and process multiple credit card statement PDFs in a single request.
    
    Security Features:
    - All PDFs are processed in-memory only, never stored
    - Only transaction data (merchant, amount, category) is saved
    - Account numbers and personal info are NOT stored
    - File hash used for deduplication
    
    Args:
        files: List of PDF file uploads
        bank: Bank name (default: Chase)
        
    Returns:
        Processing summary for each file with transaction counts
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    results = []
    errors = []
    
    for file in files:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            errors.append({
                "filename": file.filename,
                "error": "Only PDF files are supported"
            })
            continue
        
        try:
            result = await financier.process_credit_card_statement(
                file=file,
                bank=bank
            )
            results.append({
                "filename": file.filename,
                "status": "success",
                "data": result
            })
        
        except ValueError as e:
            errors.append({
                "filename": file.filename,
                "error": str(e)
            })
        
        except Exception as e:
            errors.append({
                "filename": file.filename,
                "error": f"Error processing document: {str(e)}"
            })
    
    return {
        "total_files": len(files),
        "successful": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors if errors else None
    }


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


@router.get("/spending/analysis")
async def analyze_transactions(
    year: Optional[int] = Query(None, description="Filter by year"),
    month: Optional[int] = Query(None, description="Filter by month (1-12)"),
    category: Optional[str] = Query(None, description="Filter by category")
):
    """
    Detailed transaction analysis by month, year, and category.
    
    Provides:
    - Transaction count and total spending
    - Average transaction amount
    - Top merchants
    - Day-by-day breakdown
    - Category-specific insights
    
    Args:
        year: Filter by year
        month: Filter by month (1-12)
        category: Filter by specific category
        
    Returns:
        Detailed analysis with statistics, top merchants, and trends
    """
    try:
        result = await financier.analyze_transactions(
            year=year,
            month=month,
            category=category
        )
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing transactions: {str(e)}"
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


@router.get("/merchants")
async def get_all_merchants():
    """
    Get all merchants with their category mappings.
    
    Returns:
        List of merchants with categories, source, confidence, and last update time
    """
    try:
        result = await financier.get_all_merchants()
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving merchants: {str(e)}"
        )


@router.get("/merchants/category/{category}")
async def get_merchants_by_category(category: str):
    """
    Get all merchants in a specific category.
    
    Args:
        category: Category name
        
    Returns:
        List of merchants in that category
    """
    try:
        result = await financier.get_merchants_by_category(category)
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving merchants: {str(e)}"
        )


@router.put("/merchants/{merchant_name}/category")
async def update_merchant_category(
    merchant_name: str,
    new_category: str = Query(..., description="New category to assign")
):
    """
    Reassign a merchant to a different category.
    This will update both the merchant mapping and all related transactions.
    
    Args:
        merchant_name: Merchant name (URL encoded)
        new_category: New category to assign
        
    Returns:
        Update result with old and new category
    """
    try:
        result = await financier.update_merchant_category(
            merchant_name=merchant_name,
            new_category=new_category
        )
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error updating merchant category: {str(e)}"
        )


@router.post("/categories/add")
async def add_custom_category(
    category_name: str = Query(..., description="Name of the new category")
):
    """
    Add a new custom category.
    The category will be available for assignment to merchants.
    
    Args:
        category_name: Name of the new category
        
    Returns:
        Status of category creation
    """
    try:
        result = await financier.add_custom_category(category_name)
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error adding category: {str(e)}"
        )

