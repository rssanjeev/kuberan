"""
Chase Checking Account Statement Parser

Extracts transaction data from Chase checking account PDF statements.

Security Features:
- Extracts ONLY transactions (no account numbers stored)
- Focuses on transaction date, description, amount, balance
- Account info parsing is for validation only, NOT stored
"""

import re
import pdfplumber
from datetime import datetime
from typing import Dict, List, Any, Optional


def parse_checking_statement(pdf_path: str) -> Dict[str, Any]:
    """
    Parse Chase checking account statement and extract structured data.
    
    Args:
        pdf_path: Path to Chase checking account statement PDF
        
    Returns:
        Structured data with transactions and summary
        
    Security Note:
        Account numbers and personal info are NOT stored.
        Only transaction-level data is extracted.
    """
    print(f"Parsing Chase Checking Account Statement: {pdf_path}")
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Extract text from all pages
            full_text = ""
            for page in pdf.pages:
                full_text += page.extract_text() + "\n"
            
            # Extract key information
            statement_period = extract_statement_period(full_text)
            account_type = extract_account_type(full_text)
            summary = extract_summary(full_text)
            transactions = extract_transactions(full_text)
            
            # Calculate additional metrics
            total_deposits = sum(t['amount'] for t in transactions if t['amount'] > 0)
            total_withdrawals = abs(sum(t['amount'] for t in transactions if t['amount'] < 0))
            
            return {
                "file_name": pdf_path.split('/')[-1],
                "bank": "Chase",
                "account_type": account_type,
                "statement_period": statement_period,
                "extraction_date": datetime.now().isoformat(),
                "summary": {
                    **summary,
                    "total_deposits": round(total_deposits, 2),
                    "total_withdrawals": round(total_withdrawals, 2),
                    "transaction_count": len(transactions)
                },
                "transactions": transactions
            }
    
    except Exception as e:
        print(f"Error parsing checking account statement: {str(e)}")
        raise


def extract_statement_period(text: str) -> Dict[str, str]:
    """
    Extract statement period dates.
    
    Pattern: "January 07, 2025throughFebruary 05, 2025"
    or: "December 06, 2024throughJanuary 06, 2025"
    """
    # Try to find the date range pattern
    pattern = r'([A-Z][a-z]+\s+\d{2},\s+\d{4})through([A-Z][a-z]+\s+\d{2},\s+\d{4})'
    match = re.search(pattern, text)
    
    if match:
        start_date_str = match.group(1).strip()
        end_date_str = match.group(2).strip()
        
        try:
            start_date = datetime.strptime(start_date_str, "%B %d, %Y")
            end_date = datetime.strptime(end_date_str, "%B %d, %Y")
            
            return {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "statement_year": end_date.year,
                "statement_month": end_date.month
            }
        except ValueError:
            pass
    
    # Fallback: try to extract from transaction dates
    return {
        "start_date": None,
        "end_date": None,
        "statement_year": None,
        "statement_month": None
    }


def extract_account_type(text: str) -> str:
    """Extract account type (e.g., Chase Total Checking)."""
    patterns = [
        r'(Chase Total Checking)',
        r'(Chase Premier Plus Checking)',
        r'(Chase Secure Checking)',
        r'(Chase Sapphire Checking)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    
    return "Chase Checking"


def extract_summary(text: str) -> Dict[str, float]:
    """
    Extract checking summary section.
    
    Pattern:
    CHECKING SUMMARY
    Beginning Balance $12,997.83
    Deposits and Additions 6,281.25
    Electronic Withdrawals -7,122.93
    Ending Balance $12,156.15
    """
    summary = {}
    
    # Find CHECKING SUMMARY section
    if 'CHECKING SUMMARY' in text:
        summary_section = text.split('CHECKING SUMMARY')[1].split('*end*summary')[0]
        
        # Extract beginning balance
        begin_match = re.search(r'Beginning Balance\s+\$?([\d,]+\.\d{2})', summary_section)
        if begin_match:
            summary['beginning_balance'] = float(begin_match.group(1).replace(',', ''))
        
        # Extract deposits
        deposit_match = re.search(r'Deposits and Additions\s+\$?([\d,]+\.\d{2})', summary_section)
        if deposit_match:
            summary['deposits'] = float(deposit_match.group(1).replace(',', ''))
        
        # Extract withdrawals (already negative in statement)
        withdrawal_match = re.search(r'Electronic Withdrawals\s+\-?\$?([\d,]+\.\d{2})', summary_section)
        if withdrawal_match:
            amount = withdrawal_match.group(1).replace(',', '')
            summary['withdrawals'] = -float(amount) if not withdrawal_match.group(0).startswith('-') else float(amount)
        
        # Extract ending balance
        end_match = re.search(r'Ending Balance\s+\$?([\d,]+\.\d{2})', summary_section)
        if end_match:
            summary['ending_balance'] = float(end_match.group(1).replace(',', ''))
    
    return summary


def extract_transactions(text: str) -> List[Dict[str, Any]]:
    """
    Extract all transactions from statement.
    
    Pattern: MM/DD DESCRIPTION AMOUNT BALANCE
    Example: 01/07 Webull Fyyg0Rk5H Payments Ad 85Ofgac9N4Lc CCD ID: 9992799206 -100.00 12,897.83
    """
    transactions = []
    
    # Find TRANSACTION DETAIL section(s)
    transaction_sections = []
    
    # Split by TRANSACTION DETAIL marker
    parts = text.split('TRANSACTION DETAIL')
    for i in range(1, len(parts)):
        # Get text until next section or end marker
        section = parts[i].split('*end*transaction detail')[0]
        transaction_sections.append(section)
    
    # Process all transaction sections
    for section in transaction_sections:
        lines = section.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and headers
            if not line or 'DATE' in line or 'DESCRIPTION' in line or 'Beginning Balance' in line or 'Ending Balance' in line:
                continue
            
            # Pattern: MM/DD at start, then description, then amount, then balance at end
            # Amount is negative for withdrawals, positive for deposits
            pattern = r'^(\d{2}/\d{2})\s+(.+?)\s+([\-]?[\d,]+\.\d{2})\s+([\d,]+\.\d{2})$'
            match = re.match(pattern, line)
            
            if match:
                date = match.group(1)
                description = match.group(2).strip()
                amount = float(match.group(3).replace(',', ''))
                balance = float(match.group(4).replace(',', ''))
                
                # Categorize and determine transaction type
                category = categorize_transaction(description, amount)
                trans_type = determine_transaction_type(description, amount)
                
                transactions.append({
                    "date": date,
                    "description": description,
                    "amount": amount,
                    "balance": balance,
                    "category": category,
                    "type": trans_type,  # Use "type" to match credit card parser
                    "raw_line": line
                })
    
    return transactions


def categorize_transaction(description: str, amount: float) -> str:
    """
    Auto-categorize checking account transactions based on description.
    
    Categories:
    - Income (Payroll, Direct Deposit)
    - Housing (Rent, Mortgage)
    - Utilities (Phone, Electric, Gas, Water, Internet)
    - Credit Card Payments
    - Investments (Brokerage transfers, Retirement)
    - Personal Transfers (Zelle, Venmo, P2P)
    - Loan Payments
    - Remittances
    - Bank Fees
    - Other
    """
    desc_upper = description.upper()
    
    # Income (deposits only)
    if amount > 0:
        if any(keyword in desc_upper for keyword in ['PAYROLL', 'SALARY', 'DIRECT DEPOSIT', 'DIRECT DEP']):
            return "Income"
    
    # Housing
    if any(keyword in desc_upper for keyword in ['RENT', 'MORTGAGE', 'OSPREY COVE', 'APARTMENT', 'LEASE', 'HOA']):
        return "Housing"
    
    # Utilities
    if any(keyword in desc_upper for keyword in ['VERIZON', 'AT&T', 'T-MOBILE', 'ELECTRIC', 'POWER', 'GAS', 'WATER', 'INTERNET', 'COMCAST', 'SPECTRUM', 'LAUNDRY']):
        return "Utilities"
    
    # Credit Card Payments
    if any(keyword in desc_upper for keyword in ['CHASE CARD', 'CREDIT CARD', 'CHASE CREDIT', 'APPLECARD', 'AUTOPAY']):
        return "Credit Card Payments"
    
    # Investments (all amounts - deposits and withdrawals)
    if any(keyword in desc_upper for keyword in ['SCHWAB', 'WEBULL', 'FIDELITY', 'VANGUARD', 'ROBINHOOD', 'BROKERAGE', 'MONEYLINK', 'INVESTMENT']):
        return "Investments"
    
    # Zelle Received (deposits only)
    if amount > 0 and 'ZELLE' in desc_upper:
        return "Zelle Received"
    
    # Personal Transfers (Zelle sent and other transfers)
    if any(keyword in desc_upper for keyword in ['ZELLE', 'VENMO', 'CASHAPP', 'PAYPAL', 'PAYMENT TO']):
        return "Personal Transfers"
    
    # Loan Payments
    if any(keyword in desc_upper for keyword in ['LOAN', 'MFSUSA', 'MORTGAGE PAYMENT', 'AUTO LOAN', 'STUDENT LOAN']):
        return "Loan Payments"
    
    # Remittances
    if any(keyword in desc_upper for keyword in ['REMITLY', 'WESTERN UNION', 'MONEYGRAM', 'REMITTANCE', 'XOOM']):
        return "Remittances"
    
    # Bank Fees
    if any(keyword in desc_upper for keyword in ['FEE', 'CHARGE', 'SERVICE CHARGE', 'OVERDRAFT', 'NSF']):
        return "Bank Fees"
    
    # Catch-all for deposits
    if amount > 0:
        return "Income"
    
    return "Other"


def determine_transaction_type(description: str, amount: float) -> str:
    """
    Determine the type of transaction for detailed tracking.
    
    Types:
    - Payroll Deposit
    - Bill Payment
    - ACH Transfer
    - Zelle Payment
    - Wire Transfer
    - ATM Withdrawal
    - Debit Card Purchase
    - Check Payment
    - Bank Fee
    - Other
    """
    desc_upper = description.upper()
    
    # Payroll
    if 'PAYROLL' in desc_upper or 'SALARY' in desc_upper:
        return "Payroll Deposit"
    
    # Bill Payment
    if 'BILL PAY' in desc_upper or 'PAYMENT' in desc_upper:
        return "Bill Payment"
    
    # ACH
    if 'ACH' in desc_upper or 'PPD ID:' in desc_upper or 'CCD ID:' in desc_upper:
        return "ACH Transfer"
    
    # Zelle
    if 'ZELLE' in desc_upper:
        return "Zelle Payment"
    
    # Wire
    if 'WIRE' in desc_upper:
        return "Wire Transfer"
    
    # ATM
    if 'ATM' in desc_upper or 'WITHDRAWAL' in desc_upper:
        return "ATM Withdrawal"
    
    # Check
    if 'CHECK' in desc_upper or re.search(r'CHECK\s*#?\d+', desc_upper):
        return "Check Payment"
    
    # Web payment
    if 'WEB' in desc_upper or 'WEB ID:' in desc_upper:
        return "Bill Payment"
    
    # Fee
    if 'FEE' in desc_upper or 'CHARGE' in desc_upper:
        return "Bank Fee"
    
    # Default based on amount
    if amount > 0:
        return "Deposit"
    else:
        return "Withdrawal"


def clean_text(text: str) -> str:
    """Clean extracted text by removing extra whitespace and special characters."""
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    # Remove special markers
    text = re.sub(r'\*start\*|\*end\*', '', text)
    return text.strip()


if __name__ == "__main__":
    # Test the parser with sample PDF
    import sys
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        result = parse_checking_statement(pdf_path)
        
        print("\n=== PARSING RESULTS ===\n")
        print(f"Account Type: {result['account_type']}")
        print(f"Statement Period: {result['statement_period']}")
        print(f"\nSummary:")
        for key, value in result['summary'].items():
            print(f"  {key}: {value}")
        
        print(f"\nTransactions: {len(result['transactions'])}")
        print("\nFirst 5 transactions:")
        for i, txn in enumerate(result['transactions'][:5], 1):
            print(f"  {i}. {txn['date']} - {txn['description'][:50]} - ${txn['amount']:.2f} - {txn['category']}")
    else:
        print("Usage: python checking_account_parser.py <path_to_pdf>")
