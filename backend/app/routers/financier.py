"""
Financial Documents API Router

Security: All endpoints designed to handle financial data discreetly.
No account information is exposed or stored.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Body
from fastapi.responses import JSONResponse
from typing import Optional, List

from app.core.logging_config import get_logger
from app.services.financier.document_processor_service import document_processor
from app.services.financier.transaction_service import transaction_service
from app.services.financier.merchant_service import merchant_service
from app.services.financier.investment_analysis_service import investment_analysis_service
from app.services.analytics_service import analytics_service
from app.repositories.financial_repository import financial_repository

logger = get_logger(__name__)
router = APIRouter(prefix="/financier", tags=["Financier"])


@router.post("/upload")
async def upload_financial_document(
    file: UploadFile = File(...),
    bank: str = Query(default="Chase", description="Bank name (Chase, Amex, etc.)"),
    statement_type: str = Query(default="credit_card", description="Statement type (credit_card or checking_account)")
):
    """
    Upload and process a single bank statement PDF.
    
    Security Features:
    - PDF is processed in-memory only, never stored
    - Only transaction data (merchant, amount, category) is saved
    - Account numbers and personal info are NOT stored
    - File hash used for deduplication
    
    Args:
        file: PDF file upload
        bank: Bank name (default: Chase)
        statement_type: Type of statement - credit_card or checking_account (default: credit_card)
        
    Returns:
        Processing summary with transaction counts
    """
    # DEBUG: Log upload attempt
    logger.info(
        "📄 Upload request received",
        extra={
            "file_name": file.filename,  # Note: 'filename' is reserved in LogRecord
            "bank": bank,
            "statement_type": statement_type
        }
    )
    
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        result = await document_processor.process_credit_card_statement(
            file=file,
            bank=bank,
            statement_type=statement_type
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
    bank: str = Query(default="Chase", description="Bank name (Chase, Amex, etc.)"),
    statement_type: str = Query(default="credit_card", description="Statement type (credit_card or checking_account)")
):
    """
    Upload and process multiple bank statement PDFs in a single request.
    
    Security Features:
    - All PDFs are processed in-memory only, never stored
    - Only transaction data (merchant, amount, category) is saved
    - Account numbers and personal info are NOT stored
    - File hash used for deduplication
    
    Args:
        files: List of PDF file uploads
        bank: Bank name (default: Chase)
        statement_type: Type of statement - applies to all files (default: credit_card)
        
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
            result = await document_processor.process_credit_card_statement(
                file=file,
                bank=bank,
                statement_type=statement_type
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
        result = await transaction_service.get_transactions(
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
        result = await transaction_service.get_spending_summary(
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
        result = await analytics_service.analyze_transactions(
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
        result = await merchant_service.get_all_merchants()
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
        result = await merchant_service.get_merchants_by_category(category)
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
        result = await merchant_service.update_merchant_category(
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
        result = await merchant_service.add_custom_category(category_name)
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error adding category: {str(e)}"
        )


# ============================================================================
# ANALYTICS ENDPOINTS - Deep Financial Analysis
# ============================================================================

@router.get("/analytics/comprehensive")
async def get_comprehensive_analysis(
    year: Optional[int] = Query(None, description="Filter by year"),
    month: Optional[int] = Query(None, description="Filter by month (1-12)"),
    category: Optional[str] = Query(None, description="Filter by category")
):
    """
    Get comprehensive financial analysis including:
    - Cash flow analysis (income, expenses, net flow)
    - Monthly cash flow trends
    - Category spending breakdown
    - Outlier detection (unusual transactions)
    - Spending spike detection
    - Trend analysis (increasing/decreasing expenses)
    - Recurring payment detection
    - Financial health indicators
    
    Args:
        year: Filter by year
        month: Filter by month (1-12)
        category: Filter by category
        
    Returns:
        Complete financial analysis with all metrics
    """
    try:
        result = await analytics_service.get_comprehensive_analysis(
            year=year,
            month=month,
            category=category
        )
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error performing analysis: {str(e)}"
        )


@router.get("/analytics/monthly-trends")
async def get_monthly_trends(
    period: str = Query("6m", description="Time period: 2m (2 months), 6m (6 months), ytd (year to date)"),
    year: Optional[int] = Query(None, description="Year for YTD calculation (default: current year)")
):
    """
    Get monthly expense and cash flow trends for charting.
    
    Returns aggregated data by month for the specified time period.
    Used by frontend to render line/bar charts showing spending trends.
    
    Args:
        period: Time period selector
            - '2m': Last 2 months
            - '6m': Last 6 months (default)
            - 'ytd': Year to date (Jan to current month)
        year: Year for YTD calculation (default: current year)
        
    Returns:
        {
            "months": ["2025-07", "2025-08", ...],
            "labels": ["Jul", "Aug", ...],
            "expenses": [2100.50, 2450.75, ...],
            "income": [6827.24, 10240.86, ...],
            "cashflow": [4726.74, 7790.11, ...]
        }
    """
    try:
        result = await analytics_service.get_monthly_trends(
            period=period,
            year=year
        )
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching monthly trends: {str(e)}"
        )


@router.put("/transactions/{transaction_id}/category")
async def update_transaction_category(
    transaction_id: str,
    new_category: str = Body(..., embed=True),
    update_all_from_merchant: bool = Body(False, embed=True)
):
    """
    Update the category of a specific transaction.
    
    Args:
        transaction_id: MongoDB ObjectId string of the transaction
        new_category: New category name to assign
        update_all_from_merchant: If True, update all past and future transactions from same merchant
    
    Returns:
        Updated transaction object with count of updated transactions
    
    Example:
        PUT /transactions/507f1f77bcf86cd799439011/category
        Body: {"new_category": "Food", "update_all_from_merchant": true}
    
    Use cases:
        - Correct miscategorized transactions
        - Reclassify purchases for better analysis
        - Fix automatic categorization errors
        - Update all transactions from same merchant in one action
    """
    try:
        result = await financial_repository.update_transaction_category(
            transaction_id=transaction_id,
            new_category=new_category,
            update_all_from_merchant=update_all_from_merchant
        )
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Transaction with id '{transaction_id}' not found"
            )
        
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error updating transaction category: {str(e)}"
        )


@router.get("/analytics/visualizations")
async def get_visualizations(
    year: Optional[int] = Query(None, description="Filter by year"),
    month: Optional[int] = Query(None, description="Filter by month (1-12)"),
    format: str = Query("png", description="Output format: png or svg")
):
    """
    Generate financial visualizations as base64-encoded images for frontend display.
    
    IMPORTANT: This endpoint is for FRONTEND CONSUMPTION ONLY. Images are returned
    as base64 strings in JSON format for React components to display. Do NOT use
    this for file downloads, PDF exports, or email attachments.
    
    Visualizations generated:
    - Monthly income vs expenses bar chart
    - Spending by category pie chart
    - Spending trend over time line chart
    - Outlier detection scatter plot
    
    Args:
        year: Filter by year
        month: Filter by month (1-12)
        format: Output format ('png' or 'svg')
        
    Returns:
        Dict of visualization names to base64 encoded images
        Frontend usage: <img src="data:image/png;base64,{encoded_data}" />
        
    Note:
        Images are generated server-side and NOT saved to disk or database.
    """
    if format not in ["png", "svg"]:
        raise HTTPException(status_code=400, detail="Format must be 'png' or 'svg'")
    
    try:
        result = await analytics_service.get_visualizations(
            year=year,
            month=month,
            format=format
        )
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating visualizations: {str(e)}"
        )


@router.get("/investments/rolling-analysis")
async def get_rolling_investment_analysis(
    year: Optional[int] = Query(None, description="Current year for analysis"),
    month: Optional[int] = Query(None, description="Current month for analysis (1-12)"),
    months_back: int = Query(12, description="Number of months to analyze (default 12)")
):
    """
    Get rolling investment analysis over specified period.
    
    Provides comprehensive analysis of investment contributions including:
    - Total contributions over period
    - Monthly average and median contributions
    - Contribution trends (increasing/decreasing)
    - Consistency metrics
    - Top investment destinations
    - Projected annual contributions
    - Actionable insights
    
    Args:
        year: Current year (optional, uses current if not provided)
        month: Current month (optional, uses current if not provided)
        months_back: Number of months to look back (default 12)
        
    Returns:
        Comprehensive investment analysis with metrics, trends, and insights
        
    Example Response:
        {
            "period": {
                "months_analyzed": 12,
                "date_range": {"start": "2024-03", "end": "2025-02"}
            },
            "summary": {
                "total_contributions": 15000.00,
                "transaction_count": 60,
                "average_monthly": 1250.00,
                "median_monthly": 1200.00,
                "projected_annual": 15000.00
            },
            "trends": {
                "direction": "increasing",
                "change_percentage": 15.5,
                "consistency_score": 85.0,
                "standard_deviation": 187.50
            },
            "monthly_breakdown": [
                {"month": "2025-02", "amount": 1526.00, "transaction_count": 5},
                ...
            ],
            "top_destinations": [
                {"destination": "Charles Schwab", "amount": 10000.00},
                {"destination": "Webull", "amount": 5000.00}
            ],
            "insights": [
                "✓ Excellent consistency! Your investments vary by less than 15%.",
                "📈 Great! Your investments are increasing by 15.5%.",
                "💰 At current rate, you'll invest $15,000.00 annually."
            ]
        }
    """
    try:
        result = await investment_analysis_service.get_rolling_investment_analysis(
            year=year,
            month=month,
            months_back=months_back
        )
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating rolling investment analysis: {str(e)}"
        )

