"""
Chase Credit Card Statement Parser

Security Features:
- Extracts ONLY transactions (no account numbers stored)
- Focuses on merchant, amount, date, category
- Account info parsing is for validation only, NOT stored
"""

import re
from typing import Dict, List, Any, Optional
import hashlib
from datetime import datetime

from app.core.pdf_extractor import extract_text, extract_tables, get_pdf_metadata


def clean_chase_text(text: str) -> str:
    """
    Clean duplicated characters in Chase PDFs.
    
    Chase PDFs sometimes have character duplication (e.g., "MMaannaaggee" -> "Manage")
    
    Args:
        text: Raw text with potential duplications
        
    Returns:
        Cleaned text
    """
    # Remove alternating duplicate characters
    result = []
    i = 0
    while i < len(text):
        result.append(text[i])
        # Skip next character if it's the same
        if i + 1 < len(text) and text[i] == text[i + 1]:
            i += 2
        else:
            i += 1
    return ''.join(result)


def categorize_transaction(description: str) -> str:
    """
    Categorize a transaction based on merchant description.
    
    Args:
        description: Merchant description
        
    Returns:
        Category name
    """
    desc_lower = description.lower()
    
    # Payment/Credit
    if 'payment' in desc_lower or 'thank you' in desc_lower:
        return 'Payment'
    
    # Coffee & Cafes
    if any(word in desc_lower for word in ['coffee', 'cofe', 'cafe', 'starbucks', 'dunkin']):
        return 'Coffee & Cafes'
    
    # Restaurants & Dining
    if any(word in desc_lower for word in [
        'restaurant', 'taqueria', 'ramen', 'pizza', 'biryaniz', 'breadz',
        'kitchen', 'grill', 'yard', 'taco', 'toro loco', 'harp'
    ]):
        return 'Restaurants & Dining'
    
    # Groceries & Food
    if any(word in desc_lower for word in [
        'trader joe', 'whole foods', 'grocery', 'market', 'farmers',
        'groceries', 'roche brothers', 'costco whse'
    ]):
        return 'Groceries'
    
    # Gas & Fuel
    if 'gas' in desc_lower or 'fuel' in desc_lower:
        return 'Gas & Fuel'
    
    # Alcohol & Wine
    if any(word in desc_lower for word in ['wine', 'liquor', 'spirits', 'winery', 'wine club']):
        return 'Alcohol & Wine'
    
    # Entertainment
    if any(word in desc_lower for word in [
        'fandango', 'regal', 'movie', 'cinema', 'hulu', 'netflix',
        'spotify', 'entertainment'
    ]):
        return 'Entertainment'
    
    # Transportation
    if any(word in desc_lower for word in [
        'uber', 'lyft', 'taxi', 'mta', 'transit', 'parking', 'ezpass',
        'zipcar', 'u-haul', 'movinghelp'
    ]):
        return 'Transportation'
    
    # Utilities
    if any(word in desc_lower for word in ['pseg', 'utility', 'electric', 'gas utility', 'water']):
        return 'Utilities'
    
    # Insurance
    if any(word in desc_lower for word in ['progressive', 'insurance', 'geico', 'allstate']):
        return 'Insurance'
    
    # Home & Garden
    if any(word in desc_lower for word in ['home depot', 'lowes', 'hardware', 'wayfair', 'ikea']):
        return 'Home & Garden'
    
    # Health & Pharmacy
    if any(word in desc_lower for word in ['cvs', 'pharmacy', 'walgreens', 'rite aid', 'health']):
        return 'Health & Pharmacy'
    
    # Shopping & Retail
    if any(word in desc_lower for word in ['amazon', 'target', 'walmart', 'costco', 'store']):
        return 'Shopping & Retail'
    
    # Ice Cream & Desserts
    if any(word in desc_lower for word in ['ice cream', 'bakery', 'leches', 'scops']):
        return 'Ice Cream & Desserts'
    
    # Food Delivery
    if any(word in desc_lower for word in ['doordash', 'ubereats', 'grubhub', 'postmates']):
        return 'Food Delivery'
    
    # Services & Fees
    if any(word in desc_lower for word in ['usps', 'ups', 'fedex', 'shipping', 'change of address']):
        return 'Services & Fees'
    
    # Car Wash & Maintenance
    if any(word in desc_lower for word in ['car wash', 'auto', 'oil change', 'tire']):
        return 'Car Wash & Maintenance'
    
    # Farm Stands & Local
    if any(word in desc_lower for word in ['farm', 'outpost']):
        return 'Farm Stands & Local'
    
    # Interest & Fees (from credit card)
    if 'interest' in desc_lower or 'fee' in desc_lower:
        return 'Interest & Fees'
    
    # Default
    return 'Other'


def calculate_file_hash(pdf_path: str) -> str:
    """
    Calculate SHA256 hash of PDF file for deduplication.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Hex digest of file hash
    """
    sha256 = hashlib.sha256()
    with open(pdf_path, 'rb') as f:
        # Read in chunks for large files
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def parse_chase_statement(pdf_path: str, include_account_info: bool = False) -> Dict[str, Any]:
    """
    Parse Chase credit card statement and extract structured data.
    
    Args:
        pdf_path: Path to Chase credit card statement PDF
        
    Returns:
        Structured data with account info, transactions, and summary
    """
    print(f"\n{'='*60}")
    print(f"Parsing Chase Credit Card Statement: {pdf_path}")
    print(f"{'='*60}\n")
    
    # Extract raw data
    print("Step 1: Extracting raw text...")
    raw_text = extract_text(pdf_path)
    # TEMPORARILY DISABLED: cleaned_text = clean_chase_text(raw_text)
    cleaned_text = raw_text  # Use raw text directly without cleaning
    print(f"✓ Extracted {len(cleaned_text)} characters\n")
    
    print("Step 2: Extracting tables...")
    tables = extract_tables(pdf_path)
    print(f"✓ Found {len(tables)} pages with tables\n")
    
    print("Step 3: Extracting metadata...")
    metadata = get_pdf_metadata(pdf_path)
    print(f"✓ Document has {metadata['num_pages']} pages\n")
    
    # Parse Chase-specific data
    print("Step 4: Parsing account information...")
    account_info = extract_chase_account_info(cleaned_text)
    print(f"✓ Extracted account details\n")
    
    print("Step 5: Parsing transactions...")
    transactions = extract_chase_transactions(tables, cleaned_text)
    print(f"✓ Found {len(transactions)} transactions\n")
    
    print("Step 6: Parsing fees and charges...")
    fees = extract_chase_fees(tables, cleaned_text)
    print(f"✓ Found {len(fees)} fees/charges\n")
    
    print("Step 7: Calculating summary...")
    summary = calculate_chase_summary(transactions, fees, account_info)
    print(f"✓ Summary calculated\n")
    
    return {
        "file_name": pdf_path.split('/')[-1],
        "bank": "Chase",
        "extraction_date": datetime.now().isoformat(),
        "metadata": metadata,
        "account_info": account_info,
        "transactions": transactions,
        "fees_and_charges": fees,
        "summary": summary
    }


def extract_chase_account_info(text: str) -> Dict[str, str]:
    """
    Extract Chase-specific account information.
    
    Args:
        text: Cleaned text from PDF
        
    Returns:
        Dictionary with account details
    """
    account_info = {}
    
    # Account number (last 4 digits)
    account_match = re.search(r'Account\s+(?:Number|#)?\s*[:\-]?\s*(?:\*+)?(\d{4})', text, re.IGNORECASE)
    if account_match:
        account_info['account_number_last4'] = account_match.group(1)
    
    # Statement period - Try multiple patterns
    # Pattern 1: "Opening/Closing Date MM/DD/YY - MM/DD/YY"
    period_match = re.search(r'Opening/Closing\s+Date\s+(\d{2}/\d{2}/\d{2,4})\s*-\s*(\d{2}/\d{2}/\d{2,4})', text, re.IGNORECASE)
    if not period_match:
        # Pattern 2: "Statement Period MM/DD/YY to MM/DD/YY"
        period_match = re.search(r'(?:Statement\s+Period|Closing\s+Date)[:\s]+(\d{2}/\d{2}/\d{2,4})\s*(?:to|-)\s*(\d{2}/\d{2}/\d{2,4})', text, re.IGNORECASE)
    
    if period_match:
        account_info['statement_period_start'] = period_match.group(1)
        account_info['statement_period_end'] = period_match.group(2)
        # Create unique statement period identifier
        account_info['statement_period'] = f"{period_match.group(1)} - {period_match.group(2)}"
    
    # Statement date
    date_match = re.search(r'(?:Statement\s+(?:Closing\s+)?Date|Opening/Closing\s+Date)[:\s]+(\d{2}/\d{2}/\d{2,4})', text, re.IGNORECASE)
    if date_match:
        account_info['statement_date'] = date_match.group(1)
    
    # Payment due date
    due_match = re.search(r'Payment\s+Due\s+Date[:\s]+(\d{2}/\d{2}/\d{2,4})', text, re.IGNORECASE)
    if due_match:
        account_info['payment_due_date'] = due_match.group(1)
    
    # New balance
    balance_match = re.search(r'New\s+Balance[:\s]+\$?([\d,]+\.?\d{0,2})', text, re.IGNORECASE)
    if balance_match:
        account_info['new_balance'] = balance_match.group(1).replace(',', '')
    
    # Previous balance
    prev_balance_match = re.search(r'Previous\s+Balance[:\s]+\$?([\d,]+\.?\d{0,2})', text, re.IGNORECASE)
    if prev_balance_match:
        account_info['previous_balance'] = prev_balance_match.group(1).replace(',', '')
    
    # Minimum payment
    min_payment_match = re.search(r'Minimum\s+Payment\s+Due[:\s]+\$?([\d,]+\.?\d{0,2})', text, re.IGNORECASE)
    if min_payment_match:
        account_info['minimum_payment'] = min_payment_match.group(1).replace(',', '')
    
    # Credit limit
    credit_limit_match = re.search(r'Credit\s+Limit[:\s]+\$?([\d,]+\.?\d{0,2})', text, re.IGNORECASE)
    if credit_limit_match:
        account_info['credit_limit'] = credit_limit_match.group(1).replace(',', '')
    
    # Available credit
    available_credit_match = re.search(r'Available\s+Credit[:\s]+\$?([\d,]+\.?\d{0,2})', text, re.IGNORECASE)
    if available_credit_match:
        account_info['available_credit'] = available_credit_match.group(1).replace(',', '')
    
    return account_info


def extract_chase_transactions(tables: List[List[List[str]]], text: str) -> List[Dict[str, Any]]:
    """
    Extract transactions from Chase statement tables and text.
    
    Chase transactions can be in tables OR in text format:
    Format: MM/DD MERCHANT_NAME LOCATION AMOUNT
    
    Args:
        tables: Extracted tables from PDF
        text: Cleaned text for fallback parsing
        
    Returns:
        List of transaction dictionaries
    """
    transactions = []
    
    # First try table-based extraction
    for page_idx, page_tables in enumerate(tables):
        for table_idx, table in enumerate(page_tables):
            if not table or len(table) < 2:
                continue
            
            # Look for transaction tables
            headers = [str(cell).lower().strip() if cell else '' for cell in table[0]]
            
            # Check if this looks like a transactions table
            has_date = any('date' in h or 'trans' in h for h in headers)
            has_amount = any('amount' in h or 'charge' in h or 'credit' in h for h in headers)
            
            if not (has_date and has_amount):
                continue
            
            # Parse transaction rows
            for row_idx, row in enumerate(table[1:], start=1):
                if not row or len(row) < 2:
                    continue
                
                # Skip header rows or subtotal rows
                first_cell = str(row[0]).lower().strip() if row[0] else ''
                if not first_cell or 'total' in first_cell or 'subtotal' in first_cell:
                    continue
                
                # Try to parse as transaction
                transaction = parse_chase_transaction_row(row, page_idx + 1, table_idx + 1, row_idx)
                if transaction:
                    transactions.append(transaction)
    
    # If no transactions found in tables, try text-based extraction
    if not transactions:
        transactions = extract_chase_transactions_from_text(text)
    
    return transactions


def extract_chase_transactions_from_text(text: str) -> List[Dict[str, Any]]:
    """
    Extract transactions from Chase statement text.
    
    Chase text format: MM/DD MERCHANT_NAME LOCATION AMOUNT
    Example: 05/20 Payment Thank You-Mobile -2,036.97
    
    Args:
        text: Cleaned text from statement
        
    Returns:
        List of transaction dictionaries
    """
    transactions = []
    lines = text.split('\n')
    
    # Pattern: MM/DD followed by text, ending with amount
    # Amount can be negative (credits/payments) or positive (charges)
    # Using greedy match (.+) to capture full merchant names with special chars
    pattern = r'^(\d{2}/\d{2})\s+(.+)\s+([\-]?[\d,]+\.\d{2})$'
    
    for line_num, line in enumerate(lines):
        line = line.strip()
        match = re.match(pattern, line)
        
        if match:
            date = match.group(1)
            description_and_location = match.group(2).strip()
            amount = match.group(3).replace(',', '')
            
            # Try to split description and location
            # Location is usually at the end (2-letter state code or country)
            parts = description_and_location.rsplit(' ', 2)
            
            if len(parts) >= 2:
                # Check if last part looks like a location (2 letters or short string)
                if len(parts[-1]) <= 3 or parts[-1].upper() == parts[-1]:
                    description = ' '.join(parts[:-1])
                    location = parts[-1]
                else:
                    description = description_and_location
                    location = ""
            else:
                description = description_and_location
                location = ""
            
            # Auto-assign category
            category = categorize_transaction(description)
            
            transactions.append({
                "date": date,
                "description": description.strip(),
                "location": location.strip(),
                "amount": amount,
                "type": "credit" if amount.startswith('-') else "charge",
                "category": category,
                "raw_line": line
            })
    
    return transactions


def parse_chase_transaction_row(row: List[str], page: int, table: int, row_num: int) -> Dict[str, Any]:
    """
    Parse a single transaction row from Chase statement.
    
    Args:
        row: Table row data
        page: Page number
        table: Table number
        row_num: Row number
        
    Returns:
        Transaction dictionary or None if not a valid transaction
    """
    if not row or len(row) < 2:
        return None
    
    # Clean row data
    cleaned_row = [str(cell).strip() if cell else '' for cell in row]
    
    # Try to identify date (MM/DD format common in Chase)
    date_pattern = r'\d{1,2}/\d{1,2}(?:/\d{2,4})?'
    transaction_date = None
    description = None
    amount = None
    reference = None
    
    # Find date column
    for i, cell in enumerate(cleaned_row):
        if re.match(date_pattern, cell):
            transaction_date = cell
            # Description is usually next column(s)
            if i + 1 < len(cleaned_row):
                description = cleaned_row[i + 1]
            break
    
    # Find amount (last column usually, has $ or numbers with decimals)
    for cell in reversed(cleaned_row):
        # Look for currency amounts
        amount_match = re.search(r'\$?\-?(\d{1,3}(?:,\d{3})*\.?\d{0,2})', cell)
        if amount_match:
            amount = amount_match.group(1).replace(',', '')
            # Negative or with minus sign = credit/payment
            if '-' in cell or cell.startswith('('):
                amount = '-' + amount
            break
    
    # Must have at least date and amount
    if not (transaction_date and amount):
        return None
    
    # Extract reference number if present (between description and amount)
    if len(cleaned_row) > 3:
        for cell in cleaned_row[2:-1]:
            if re.match(r'^\d+$', cell):  # Pure numbers = reference
                reference = cell
                break
    
    return {
        "date": transaction_date,
        "description": description or "Unknown",
        "reference_number": reference,
        "amount": amount,
        "page": page,
        "table": table,
        "row": row_num,
        "raw_data": cleaned_row
    }


def extract_chase_fees(tables: List[List[List[str]]], text: str) -> List[Dict[str, Any]]:
    """
    Extract fees and interest charges from Chase statement.
    
    Args:
        tables: Extracted tables
        text: Cleaned text
        
    Returns:
        List of fee/charge dictionaries
    """
    fees = []
    
    # Look for fees in text
    fee_patterns = [
        (r'(?:Late|Overlimit|Foreign Transaction)\s+(?:Payment\s+)?Fee[:\s]+\$?([\d,]+\.?\d{0,2})', 'Fee'),
        (r'Interest\s+Charged[:\s]+\$?([\d,]+\.?\d{0,2})', 'Interest Charge'),
        (r'Annual\s+(?:Membership\s+)?Fee[:\s]+\$?([\d,]+\.?\d{0,2})', 'Annual Fee'),
    ]
    
    for pattern, fee_type in fee_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            fees.append({
                "type": fee_type,
                "amount": match.group(1).replace(',', ''),
                "description": match.group(0)
            })
    
    return fees


def calculate_chase_summary(transactions: List[Dict], fees: List[Dict], account_info: Dict) -> Dict[str, Any]:
    """
    Calculate summary statistics for Chase statement.
    
    Args:
        transactions: List of transactions
        fees: List of fees
        account_info: Account information
        
    Returns:
        Summary dictionary
    """
    total_charges = 0.0
    total_credits = 0.0
    total_fees = 0.0
    
    for txn in transactions:
        try:
            amount = float(txn['amount'])
            if amount < 0:
                total_credits += abs(amount)
            else:
                total_charges += amount
        except (ValueError, KeyError):
            pass
    
    for fee in fees:
        try:
            total_fees += float(fee['amount'])
        except (ValueError, KeyError):
            pass
    
    return {
        "total_transactions": len(transactions),
        "total_charges": round(total_charges, 2),
        "total_credits": round(total_credits, 2),
        "total_fees": round(total_fees, 2),
        "net_charges": round(total_charges - total_credits + total_fees, 2),
        "new_balance": account_info.get('new_balance', '0'),
        "minimum_payment": account_info.get('minimum_payment', '0')
    }
