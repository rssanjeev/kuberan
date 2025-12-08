"""
Financial Analytics Service

Provides deep analysis of credit card transactions including:
- Cash flow analysis
- Spending trends and patterns
- Anomaly detection
- Financial health indicators
- Data visualizations (base64-encoded images for frontend display)

IMPORTANT: Visualizations are for FRONTEND CONSUMPTION ONLY.
Images are returned as base64-encoded PNG/SVG in JSON format, intended
for React components. Do NOT implement file downloads, PDF exports, or
email features for these visualizations.

Architecture: Hybrid functional/OOP pattern
- Pure functions for computations (testable, reusable)
- Service class for orchestration and API interface
"""

import io
import base64
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, date
from collections import defaultdict
import statistics

# Data analysis libraries
import numpy as np
import pandas as pd
from scipy import stats

# Visualization libraries
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server
import matplotlib.pyplot as plt
import seaborn as sns

from app.repositories.financial_repository import financial_repository
from app.models import CreditCardTransaction
from app.services.manual_entries_service import manual_entries_service


# ============================================================================
# PURE FUNCTIONS - Cash Flow Analysis
# ============================================================================

def calculate_cash_flow(transactions: List[CreditCardTransaction]) -> Dict[str, float]:
    """
    Calculate income, expenses, and net cash flow.
    
    Income is calculated from transactions with category='Income' and positive amounts.
    Expenses are all positive transaction amounts (charges, withdrawals).
    
    Args:
        transactions: List of transactions
        
    Returns:
        Dict with income, expenses, and net_cash_flow
    """
    # Calculate actual income from Income category deposits
    income_txns = [txn for txn in transactions if txn.category == 'Income' and txn.amount > 0]
    income = sum(abs(txn.amount) for txn in income_txns)
    
    # Only expenses - exclude Income category
    expenses = sum(txn.amount for txn in transactions if txn.amount > 0 and txn.category != 'Income')
    
    return {
        "total_income": income,
        "total_expenses": expenses,
        "net_cash_flow": income - expenses
    }


def calculate_monthly_cash_flow(
    transactions: List[CreditCardTransaction]
) -> List[Dict[str, Any]]:
    """
    Calculate cash flow breakdown by month.
    
    Income is calculated from transactions with category='Income' and positive amounts.
    Expenses are all positive transaction amounts (charges, withdrawals).
    
    Args:
        transactions: List of transactions
        
    Returns:
        List of monthly cash flow summaries
    """
    monthly_data: Dict[str, Dict[str, float]] = defaultdict(lambda: {"income": 0, "expenses": 0})
    
    for txn in transactions:
        month_key = f"{txn.statement_year}-{txn.statement_month:02d}"
        
        # Track income from Income category
        if txn.category == 'Income' and txn.amount > 0:
            monthly_data[month_key]["income"] += abs(txn.amount)
        
        # Track expenses from all positive amounts
        if txn.amount > 0:
            monthly_data[month_key]["expenses"] += txn.amount
    
    # Sort by month and format
    result = []
    for month_key in sorted(monthly_data.keys()):
        year, month = month_key.split('-')
        month_name = date(int(year), int(month), 1).strftime("%b %Y")
        data = monthly_data[month_key]
        
        result.append({
            "month": month_name,
            "income": round(data["income"], 2),
            "expenses": round(data["expenses"], 2),
            "net_cash_flow": round(data["income"] - data["expenses"], 2)
        })
    
    return result


# ============================================================================
# PURE FUNCTIONS - Spending Breakdown
# ============================================================================

def calculate_category_breakdown(
    transactions: List[CreditCardTransaction]
) -> List[Dict[str, Any]]:
    """
    Calculate spending breakdown by category.
    
    Args:
        transactions: List of transactions
        
    Returns:
        List of category summaries sorted by amount
    """
    category_totals = defaultdict(float)
    category_counts = defaultdict(int)
    
    for txn in transactions:
        # Only expenses - exclude Income category and negative amounts
        if txn.amount > 0 and txn.category != 'Income':
            category = txn.category or "Uncategorized"
            category_totals[category] += txn.amount
            category_counts[category] += 1
    
    total_spending = sum(category_totals.values())
    
    result = [
        {
            "category": cat,
            "amount": round(amt, 2),
            "percentage": round((amt / total_spending * 100) if total_spending > 0 else 0, 1),
            "transaction_count": category_counts[cat],
            "average_transaction": round(amt / category_counts[cat], 2)
        }
        for cat, amt in category_totals.items()
    ]
    
    return sorted(result, key=lambda x: x["amount"], reverse=True)


def calculate_monthly_category_spending(
    transactions: List[CreditCardTransaction]
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Calculate spending by category for each month.
    
    Args:
        transactions: List of transactions
        
    Returns:
        Dict mapping months to category breakdowns
    """
    monthly_categories = defaultdict(lambda: defaultdict(float))
    
    for txn in transactions:
        # Only expenses - exclude Income category and negative amounts
        if txn.amount > 0 and txn.category != 'Income':
            month_key = f"{txn.statement_year}-{txn.statement_month:02d}"
            category = txn.category or "Uncategorized"
            monthly_categories[month_key][category] += txn.amount
    
    result = {}
    for month_key in sorted(monthly_categories.keys()):
        year, month = month_key.split('-')
        month_name = date(int(year), int(month), 1).strftime("%b %Y")
        
        categories = [
            {"category": cat, "amount": round(amt, 2)}
            for cat, amt in monthly_categories[month_key].items()
        ]
        result[month_name] = sorted(categories, key=lambda x: x["amount"], reverse=True)
    
    return result


# ============================================================================
# PURE FUNCTIONS - Anomaly Detection
# ============================================================================

def detect_outliers_zscore(
    transactions: List[CreditCardTransaction],
    threshold: float = 3.0
) -> List[Dict[str, Any]]:
    """
    Detect unusual transactions using Z-score method.
    
    Args:
        transactions: List of transactions
        threshold: Z-score threshold (default 3.0 = 99.7% confidence)
        
    Returns:
        List of outlier transactions
    """
    if len(transactions) < 3:
        return []
    
    amounts = [txn.amount for txn in transactions if txn.amount > 0]
    
    if len(amounts) < 3:
        return []
    
    mean = statistics.mean(amounts)
    stdev = statistics.stdev(amounts)
    
    if stdev == 0:
        return []
    
    outliers = []
    for txn in transactions:
        if txn.amount > 0:
            z_score = abs((txn.amount - mean) / stdev)
            if z_score > threshold:
                outlier_data = {
                    "transaction_date": txn.transaction_date,
                    "merchant": txn.merchant_name,
                    "amount": round(txn.amount, 2),
                    "category": txn.category,
                    "z_score": round(z_score, 2),
                    "deviation_from_average": round(txn.amount - mean, 2)
                }
                # Only include _id for MongoDB documents (not manual entries)
                if hasattr(txn, 'id'):
                    outlier_data["_id"] = str(txn.id)
                outliers.append(outlier_data)
    
    return sorted(outliers, key=lambda x: x["z_score"], reverse=True)


def detect_spending_spikes(
    transactions: List[CreditCardTransaction],
    spike_threshold: float = 1.5
) -> List[Dict[str, Any]]:
    """
    Detect months with unusually high spending compared to rolling average.
    
    Args:
        transactions: List of transactions
        spike_threshold: Multiplier above rolling average to consider a spike
        
    Returns:
        List of months with spending spikes
    """
    # Group by month
    monthly_spending = defaultdict(float)
    for txn in transactions:
        if txn.amount > 0:
            month_key = f"{txn.statement_year}-{txn.statement_month:02d}"
            monthly_spending[month_key] += txn.amount
    
    if len(monthly_spending) < 3:
        return []
    
    # Sort by month
    sorted_months = sorted(monthly_spending.items())
    
    # Calculate rolling average (3-month window)
    spikes = []
    for i in range(2, len(sorted_months)):
        current_month, current_spending = sorted_months[i]
        
        # Calculate average of previous 3 months (including current)
        window = sorted_months[i-2:i+1]
        avg_spending = sum(amt for _, amt in window) / len(window)
        
        # Check if current month is a spike
        if current_spending > avg_spending * spike_threshold:
            year, month = current_month.split('-')
            month_name = date(int(year), int(month), 1).strftime("%b %Y")
            
            spikes.append({
                "month": month_name,
                "spending": round(current_spending, 2),
                "average": round(avg_spending, 2),
                "spike_ratio": round(current_spending / avg_spending, 2),
                "excess_spending": round(current_spending - avg_spending, 2)
            })
    
    return sorted(spikes, key=lambda x: x["spike_ratio"], reverse=True)


# ============================================================================
# PURE FUNCTIONS - Trend Analysis
# ============================================================================

def calculate_spending_trend(
    transactions: List[CreditCardTransaction]
) -> Dict[str, Any]:
    """
    Calculate spending trend using linear regression.
    
    Args:
        transactions: List of transactions
        
    Returns:
        Trend analysis with slope, direction, and prediction
    """
    # Group by month
    monthly_spending = defaultdict(float)
    for txn in transactions:
        if txn.amount > 0:
            month_key = f"{txn.statement_year}-{txn.statement_month:02d}"
            monthly_spending[month_key] += txn.amount
    
    if len(monthly_spending) < 2:
        return {"status": "insufficient_data"}
    
    # Prepare data for regression
    sorted_months = sorted(monthly_spending.items())
    x = np.arange(len(sorted_months))
    y = np.array([amt for _, amt in sorted_months])
    
    # Linear regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    
    # Determine trend direction
    if abs(slope) < 10:
        direction = "stable"
    elif slope > 0:
        direction = "increasing"
    else:
        direction = "decreasing"
    
    # Calculate average monthly change
    avg_monthly_change = slope
    
    # Predict next month
    next_month_prediction = slope * len(sorted_months) + intercept
    
    return {
        "trend_direction": direction,
        "average_monthly_change": round(avg_monthly_change, 2),
        "correlation_coefficient": round(r_value, 3),
        "statistical_significance": "significant" if p_value < 0.05 else "not_significant",
        "next_month_prediction": round(next_month_prediction, 2),
        "confidence": round(r_value ** 2, 3)  # R-squared
    }


def detect_recurring_payments(
    transactions: List[CreditCardTransaction],
    min_occurrences: int = 3
) -> List[Dict[str, Any]]:
    """
    Detect recurring payments based on merchant and amount patterns.
    
    Args:
        transactions: List of transactions
        min_occurrences: Minimum number of occurrences to consider recurring
        
    Returns:
        List of likely recurring payments
    """
    # Group by merchant and amount (with small tolerance)
    merchant_payments = defaultdict(list)
    
    for txn in transactions:
        if txn.amount > 0:
            # Round amount to nearest dollar for grouping
            amount_key = round(txn.amount)
            key = (txn.merchant_name, amount_key)
            merchant_payments[key].append({
                "date": f"{txn.statement_year}-{txn.statement_month:02d}",
                "amount": txn.amount
            })
    
    # Find recurring patterns
    recurring = []
    for (merchant, amount_key), payments in merchant_payments.items():
        if len(payments) >= min_occurrences:
            amounts = [p["amount"] for p in payments]
            avg_amount = statistics.mean(amounts)
            stdev = statistics.stdev(amounts) if len(amounts) > 1 else 0
            
            recurring.append({
                "merchant": merchant,
                "average_amount": round(avg_amount, 2),
                "amount_variation": round(stdev, 2),
                "occurrences": len(payments),
                "frequency": "monthly" if len(payments) >= 3 else "recurring",
                "is_stable": stdev < 1.0  # Less than $1 variation
            })
    
    return sorted(recurring, key=lambda x: x["average_amount"], reverse=True)


# ============================================================================
# PURE FUNCTIONS - Financial Health Indicators
# ============================================================================

def calculate_financial_health(
    transactions: List[CreditCardTransaction]
) -> Dict[str, Any]:
    """
    Calculate financial health indicators.
    
    Args:
        transactions: List of transactions
        
    Returns:
        Financial health metrics
    """
    # Separate income and expenses
    expense_txns = [txn for txn in transactions if txn.amount > 0 and txn.category != 'Income']
    
    # Calculate actual income from payroll deposits (Income category with positive amounts)
    income_txns = [txn for txn in transactions if txn.category == 'Income' and txn.amount > 0]
    total_income = sum(abs(txn.amount) for txn in income_txns)
    
    # If no income found in this period, return None for income-dependent metrics
    total_expenses = sum(txn.amount for txn in expense_txns)
    
    # Calculate savings rate (if income exists)
    savings_rate = None
    if total_income > 0:
        savings_rate = ((total_income - total_expenses) / total_income) * 100
    
    # Categorize spending as discretionary vs fixed
    # Fixed: Utilities, Insurance, Healthcare, Transportation
    # Discretionary: Everything else
    fixed_categories = {
        "Utilities", "Insurance", "Healthcare", "Gas & Fuel",
        "Transportation", "Bills & Utilities", "Medical"
    }
    
    fixed_spending = sum(
        txn.amount for txn in expense_txns
        if txn.category in fixed_categories
    )
    discretionary_spending = total_expenses - fixed_spending
    
    # Category concentration (Gini coefficient approximation)
    category_totals = defaultdict(float)
    for txn in expense_txns:
        category_totals[txn.category or "Other"] += txn.amount
    
    if category_totals:
        sorted_amounts = sorted(category_totals.values())
        n = len(sorted_amounts)
        cumsum = np.cumsum(sorted_amounts)
        gini = (2 * sum((i + 1) * amt for i, amt in enumerate(sorted_amounts))) / (n * sum(sorted_amounts)) - (n + 1) / n
    else:
        gini = 0
    
    return {
        "savings_rate": round(savings_rate, 1) if savings_rate is not None else None,
        "expense_to_income_ratio": round((total_expenses / total_income) * 100, 1) if total_income > 0 else None,
        "fixed_spending": round(fixed_spending, 2),
        "discretionary_spending": round(discretionary_spending, 2),
        "fixed_percentage": round((fixed_spending / total_expenses * 100) if total_expenses > 0 else 0, 1),
        "discretionary_percentage": round((discretionary_spending / total_expenses * 100) if total_expenses > 0 else 0, 1),
        "category_concentration": round(gini, 3),  # 0 = diverse, 1 = concentrated
        "diversification_score": round((1 - gini) * 100, 1)  # Higher is better
    }


# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================

def create_income_vs_expenses_chart(
    monthly_data: List[Dict[str, Any]],
    format: str = "png"
) -> str:
    """
    Create monthly income vs expenses bar chart.
    
    Args:
        monthly_data: List of monthly cash flow data
        format: Output format ('png' or 'svg')
        
    Returns:
        Base64 encoded image
    """
    if not monthly_data:
        return ""
    
    # Prepare data
    months = [d["month"] for d in monthly_data]
    income = [d["income"] for d in monthly_data]
    expenses = [d["expenses"] for d in monthly_data]
    
    # Create figure
    plt.figure(figsize=(12, 6))
    x = np.arange(len(months))
    width = 0.35
    
    plt.bar(x - width/2, income, width, label='Income', color='#28a745', alpha=0.8)
    plt.bar(x + width/2, expenses, width, label='Expenses', color='#dc3545', alpha=0.8)
    
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('Amount ($)', fontsize=12)
    plt.title('Monthly Income vs Expenses', fontsize=14, fontweight='bold')
    plt.xticks(x, months, rotation=45, ha='right')
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    
    # Convert to base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format=format, dpi=150, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    plt.close()
    
    return image_base64


def create_category_pie_chart(
    category_data: List[Dict[str, Any]],
    format: str = "png"
) -> str:
    """
    Create spending by category pie chart.
    
    Args:
        category_data: List of category spending data
        format: Output format ('png' or 'svg')
        
    Returns:
        Base64 encoded image
    """
    if not category_data:
        return ""
    
    # Prepare data (show top 8 categories, group rest as "Other")
    top_categories = category_data[:8]
    categories = [d["category"] for d in top_categories]
    amounts = [d["amount"] for d in top_categories]
    
    if len(category_data) > 8:
        other_amount = sum(d["amount"] for d in category_data[8:])
        categories.append("Other")
        amounts.append(other_amount)
    
    # Create figure
    plt.figure(figsize=(10, 8))
    colors = sns.color_palette('Set3', len(categories))
    
    plt.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90,
            colors=colors, textprops={'fontsize': 10})
    plt.title('Spending by Category', fontsize=14, fontweight='bold')
    plt.axis('equal')
    plt.tight_layout()
    
    # Convert to base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format=format, dpi=150, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    plt.close()
    
    return image_base64


def create_spending_trend_chart(
    monthly_data: List[Dict[str, Any]],
    format: str = "png"
) -> str:
    """
    Create spending trend time series chart with trend line.
    
    Args:
        monthly_data: List of monthly cash flow data
        format: Output format ('png' or 'svg')
        
    Returns:
        Base64 encoded image
    """
    if not monthly_data:
        return ""
    
    # Prepare data
    months = [d["month"] for d in monthly_data]
    expenses = [d["expenses"] for d in monthly_data]
    
    # Create figure
    plt.figure(figsize=(12, 6))
    
    # Plot actual spending
    plt.plot(months, expenses, marker='o', linewidth=2, markersize=6,
             label='Actual Spending', color='#dc3545')
    
    # Add trend line
    x = np.arange(len(months))
    z = np.polyfit(x, expenses, 1)
    p = np.poly1d(z)
    plt.plot(months, p(x), linestyle='--', linewidth=2,
             label=f'Trend (${z[0]:.2f}/month)', color='#6c757d', alpha=0.7)
    
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('Expenses ($)', fontsize=12)
    plt.title('Spending Trend Over Time', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Convert to base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format=format, dpi=150, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    plt.close()
    
    return image_base64


def create_outlier_chart(
    transactions: List[CreditCardTransaction],
    outliers: List[Dict[str, Any]],
    format: str = "png"
) -> str:
    """
    Create scatter plot showing transaction amounts with outliers highlighted.
    
    Args:
        transactions: All transactions
        outliers: Detected outlier transactions
        format: Output format ('png' or 'svg')
        
    Returns:
        Base64 encoded image
    """
    if not transactions:
        return ""
    
    # Prepare data
    amounts = [txn.amount for txn in transactions if txn.amount > 0]
    x_values = list(range(len(amounts)))
    
    outlier_amounts = {d["amount"] for d in outliers}
    
    # Create figure
    plt.figure(figsize=(12, 6))
    
    # Plot all transactions
    normal_x = [x for x, amt in zip(x_values, amounts) if amt not in outlier_amounts]
    normal_y = [amt for amt in amounts if amt not in outlier_amounts]
    outlier_x = [x for x, amt in zip(x_values, amounts) if amt in outlier_amounts]
    outlier_y = [amt for amt in amounts if amt in outlier_amounts]
    
    plt.scatter(normal_x, normal_y, alpha=0.5, s=30, color='#007bff', label='Normal')
    plt.scatter(outlier_x, outlier_y, alpha=0.8, s=100, color='#dc3545',
                marker='^', label='Outliers', edgecolors='black', linewidths=1)
    
    # Add mean line
    mean = statistics.mean(amounts)
    plt.axhline(y=mean, color='#28a745', linestyle='--', linewidth=2,
                label=f'Average: ${mean:.2f}')
    
    plt.xlabel('Transaction Index', fontsize=12)
    plt.ylabel('Amount ($)', fontsize=12)
    plt.title('Transaction Amounts - Outlier Detection', fontsize=14, fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Convert to base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format=format, dpi=150, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    plt.close()
    
    return image_base64


# ============================================================================
# SERVICE CLASS - Orchestration & API Interface
# ============================================================================

class AnalyticsService:
    """
    Financial analytics service for deep transaction analysis.
    
    Provides:
    - Cash flow analysis
    - Spending trends and patterns
    - Anomaly detection
    - Financial health indicators
    - Data visualizations
    """
    
    async def get_comprehensive_analysis(
        self,
        year: Optional[int] = None,
        month: Optional[int] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive financial analysis.
        
        Args:
            year: Filter by year
            month: Filter by month
            category: Filter by category
            
        Returns:
            Complete analysis with all metrics
        """
        # Fetch transactions from database
        transactions = await financial_repository.get_transactions(
            year=year,
            month=month,
            category=category,
            limit=100000  # Get all for analysis
        )
        
        # Add manual entries (recurring income + recurring expenses + adhoc expenses)
        if year and month:
            try:
                # Get all manual transactions (already in transaction format)
                manual_transactions = manual_entries_service.get_all_manual_transactions(
                    year=year,
                    month=month
                )
                
                # Create simple objects that work with analytics functions
                from types import SimpleNamespace
                for txn_data in manual_transactions:
                    # Create object with attributes (analytics functions expect object.attribute, not dict["key"])
                    manual_txn = SimpleNamespace(
                        merchant_name=txn_data["merchant_name"],
                        merchant_location=txn_data["merchant_location"],
                        amount=txn_data["amount"],
                        transaction_type=txn_data["transaction_type"],
                        category=txn_data["category"],
                        transaction_date=txn_data["transaction_date"],
                        statement_year=txn_data["statement_year"],
                        statement_month=txn_data["statement_month"],
                        bank=txn_data["bank"]
                    )
                    transactions.append(manual_txn)
                
                # Log integration
                if len(manual_transactions) > 0:
                    from app.core.logging_config import get_logger
                    logger = get_logger(__name__)
                    logger.info(
                        "Integrated manual entries into analysis",
                        extra={
                            "year": year,
                            "month": month,
                            "manual_count": len(manual_transactions),
                            "total_count": len(transactions)
                        }
                    )
            except Exception as e:
                # Don't fail analysis if manual entries fail to load
                from app.core.logging_config import get_logger
                logger = get_logger(__name__)
                logger.error(
                    "Failed to load manual entries, continuing with database transactions only",
                    extra={"error": str(e), "error_type": type(e).__name__},
                    exc_info=True
                )
        
        if not transactions:
            return {
                "status": "no_data",
                "message": "No transactions found for the specified filters"
            }
        
        # Run all analyses
        cash_flow = calculate_cash_flow(transactions)
        monthly_cash_flow = calculate_monthly_cash_flow(transactions)
        category_breakdown = calculate_category_breakdown(transactions)
        outliers = detect_outliers_zscore(transactions)
        spending_spikes = detect_spending_spikes(transactions)
        trend = calculate_spending_trend(transactions)
        recurring = detect_recurring_payments(transactions)
        health = calculate_financial_health(transactions)
        
        return {
            "filters": {"year": year, "month": month, "category": category},
            "transaction_count": len(transactions),
            "cash_flow": cash_flow,
            "monthly_cash_flow": monthly_cash_flow,
            "category_breakdown": category_breakdown,
            "outliers": {
                "count": len(outliers),
                "transactions": outliers[:10]  # Top 10
            },
            "spending_spikes": spending_spikes,
            "trend_analysis": trend,
            "recurring_payments": recurring,
            "financial_health": health
        }
    
    async def get_monthly_trends(
        self,
        period: str = "6m",
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get monthly expense and cash flow trends for the specified time period.
        
        This method aggregates transaction data by month and includes manual entries
        (recurring income, recurring expenses, adhoc expenses) to provide complete
        financial trends over time.
        
        Args:
            period: Time period selector
                - '2m': Last 2 months
                - '6m': Last 6 months (default)
                - 'ytd': Year to date (Jan to current month)
            year: Year for YTD calculation (default: current year)
            
        Returns:
            {
                "period": "6m",
                "months": ["2025-07", "2025-08", "2025-09", "2025-10", "2025-11", "2025-12"],
                "labels": ["Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
                "expenses": [2100.50, 2450.75, ...],
                "income": [6827.24, 10240.86, ...],  # Note: Aug has 3 paydays!
                "cashflow": [4726.74, 7790.11, ...]
            }
            
        Note:
            Income variations are normal! August 2025 shows higher income because
            there are 3 biweekly paydays in that month ($3,413.62 × 3 = $10,240.86)
            instead of the usual 2 paydays.
        """
        from datetime import datetime, timedelta
        from calendar import month_abbr
        
        # Determine date range based on period
        now = datetime.now()
        current_year = year if year else now.year
        
        if period == "ytd":
            # Year to date: Jan to current month
            start_year = current_year
            start_month = 1
            end_year = current_year
            end_month = now.month
        elif period == "2m":
            # Last 2 months
            end_date = datetime(now.year, now.month, 1)
            start_date = end_date - timedelta(days=60)  # Approximately 2 months
            start_year = start_date.year
            start_month = start_date.month
            end_year = end_date.year
            end_month = end_date.month
        else:  # Default: 6m
            # Last 6 months
            end_date = datetime(now.year, now.month, 1)
            start_date = end_date - timedelta(days=180)  # Approximately 6 months
            start_year = start_date.year
            start_month = start_date.month
            end_year = end_date.year
            end_month = end_date.month
        
        # Fetch all transactions in date range
        all_transactions = await financial_repository.get_transactions(
            limit=100000  # Get all for aggregation
        )
        
        # Filter by date range
        transactions = [
            txn for txn in all_transactions
            if (txn.statement_year > start_year or 
                (txn.statement_year == start_year and txn.statement_month >= start_month))
            and (txn.statement_year < end_year or 
                 (txn.statement_year == end_year and txn.statement_month <= end_month))
        ]
        
        # Aggregate by month with manual entries
        monthly_data = {}
        
        # Generate month keys in range
        current_date = datetime(start_year, start_month, 1)
        end_date = datetime(end_year, end_month, 1)
        
        while current_date <= end_date:
            month_key = f"{current_date.year}-{current_date.month:02d}"
            
            # Get transactions for this month
            month_txns = [
                txn for txn in transactions
                if txn.statement_year == current_date.year 
                and txn.statement_month == current_date.month
            ]
            
            # Add manual entries for this month
            try:
                from types import SimpleNamespace
                manual_transactions = manual_entries_service.get_all_manual_transactions(
                    year=current_date.year,
                    month=current_date.month
                )
                
                for txn_data in manual_transactions:
                    manual_txn = SimpleNamespace(
                        merchant_name=txn_data["merchant_name"],
                        amount=txn_data["amount"],
                        category=txn_data["category"],
                        statement_year=txn_data["statement_year"],
                        statement_month=txn_data["statement_month"]
                    )
                    month_txns.append(manual_txn)
            except Exception:
                # Continue without manual entries if they fail to load
                pass
            
            # Calculate metrics
            income = sum(abs(txn.amount) for txn in month_txns if txn.category == 'Income' and txn.amount > 0)
            expenses = sum(txn.amount for txn in month_txns if txn.amount > 0 and txn.category != 'Income')
            cashflow = income - expenses
            
            monthly_data[month_key] = {
                "income": round(income, 2),
                "expenses": round(expenses, 2),
                "cashflow": round(cashflow, 2)
            }
            
            # Move to next month
            if current_date.month == 12:
                current_date = datetime(current_date.year + 1, 1, 1)
            else:
                current_date = datetime(current_date.year, current_date.month + 1, 1)
        
        # Format for chart
        months = sorted(monthly_data.keys())
        labels = [month_abbr[int(m.split('-')[1])] for m in months]
        expenses = [monthly_data[m]["expenses"] for m in months]
        income = [monthly_data[m]["income"] for m in months]
        cashflow = [monthly_data[m]["cashflow"] for m in months]
        
        return {
            "period": period,
            "months": months,
            "labels": labels,
            "expenses": expenses,
            "income": income,
            "cashflow": cashflow
        }
    
    async def get_visualizations(
        self,
        year: Optional[int] = None,
        month: Optional[int] = None,
        format: str = "png"
    ) -> Dict[str, str]:
        """
        Generate visualizations as base64-encoded images for frontend display.
        
        IMPORTANT: Images are for frontend consumption only. Returned as base64
        strings in JSON format for React components. NOT for file downloads or exports.
        
        Args:
            year: Filter by year
            month: Filter by month
            format: Output format ('png' or 'svg')
            
        Returns:
            Dict of visualization names to base64 encoded images
            
        Note:
            Images are generated in-memory and NOT saved to disk or database.
        """
        # Fetch transactions
        transactions = await financial_repository.get_transactions(
            year=year,
            month=month,
            limit=100000
        )
        
        if not transactions:
            return {"status": "no_data"}
        
        # Calculate data for visualizations
        monthly_cash_flow = calculate_monthly_cash_flow(transactions)
        category_breakdown = calculate_category_breakdown(transactions)
        outliers = detect_outliers_zscore(transactions)
        
        # Generate visualizations
        visualizations = {}
        
        if monthly_cash_flow:
            visualizations["income_vs_expenses"] = create_income_vs_expenses_chart(
                monthly_cash_flow, format
            )
            visualizations["spending_trend"] = create_spending_trend_chart(
                monthly_cash_flow, format
            )
        
        if category_breakdown:
            visualizations["category_pie_chart"] = create_category_pie_chart(
                category_breakdown, format
            )
        
        if outliers:
            visualizations["outlier_detection"] = create_outlier_chart(
                transactions, outliers, format
            )
        
        return visualizations
    
    async def analyze_transactions(
        self,
        year: Optional[int] = None,
        month: Optional[int] = None,
        category: Optional[str] = None
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
analytics_service = AnalyticsService()
