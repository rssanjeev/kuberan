"""
Finviz Financial Data Parser

Extracts and parses:
1. Snapshot Table (snapshot-table2): 66 fundamental metrics
2. Income Statement: Revenue, expenses, profit metrics
3. Balance Sheet: Assets, liabilities, equity metrics  
4. Cash Flow: Operating, investing, financing activities

Handles Finviz free tier (3 periods: TTM, FY 2024, FY 2023) with paywall detection.
"""

import re
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
from .logging_config import get_logger

logger = get_logger(__name__)


class FinvizParser:
    """
    Parse Finviz HTML into structured JSON.
    
    Supports two architectures:
    - NEW (Option 1): 3 self-contained HTML files (each with snapshot + statement)
    - OLD: 4 separate files (1 fullpage + 3 statement-only files)
    """
    
    def __init__(
        self, 
        fullpage_html: str, 
        income_statement_html: str,
        balance_sheet_html: Optional[str] = None,
        cash_flow_html: Optional[str] = None,
        ticker: str = ""
    ):
        """
        Initialize parser with HTML content.
        
        Args:
            fullpage_html: 
                - NEW architecture: Full page HTML with snapshot + income statement
                - OLD architecture: Separate fullpage HTML with snapshot only
            income_statement_html: 
                - NEW architecture: Same as fullpage_html (self-contained)
                - OLD architecture: Statement-only HTML
            balance_sheet_html: 
                - NEW architecture: Full page HTML with snapshot + balance sheet
                - OLD architecture: Statement-only HTML (optional, uses income as fallback)
            cash_flow_html: 
                - NEW architecture: Full page HTML with snapshot + cash flow
                - OLD architecture: Statement-only HTML (optional, uses income as fallback)
            ticker: Stock ticker symbol (e.g., 'NVDA', 'AAPL')
            
        Note:
            Maintains backwards compatibility with old 4-file architecture.
            New 3-file architecture: All files are self-contained (snapshot + statement).
        """
        self.fullpage_html = fullpage_html
        self.income_statement_html = income_statement_html
        self.balance_sheet_html = balance_sheet_html or income_statement_html  # Fallback for backwards compat
        self.cash_flow_html = cash_flow_html or income_statement_html  # Fallback for backwards compat
        self.ticker = ticker.upper() if ticker else "UNKNOWN"
        
        # Create BeautifulSoup objects
        # For NEW architecture: fullpage_soup parses income file (which contains snapshot)
        # For OLD architecture: fullpage_soup parses separate fullpage file
        self.fullpage_soup = BeautifulSoup(fullpage_html, 'html.parser')
        self.income_statement_soup = BeautifulSoup(income_statement_html, 'html.parser')
        self.balance_sheet_soup = BeautifulSoup(self.balance_sheet_html, 'html.parser')
        self.cash_flow_soup = BeautifulSoup(self.cash_flow_html, 'html.parser')
        
        logger.info(
            "Initialized Finviz parser",
            extra={
                "ticker": self.ticker, 
                "fullpage_size": len(fullpage_html), 
                "income_statement_size": len(income_statement_html),
                "balance_sheet_size": len(self.balance_sheet_html),
                "cash_flow_size": len(self.cash_flow_html)
            }
        )
    
    def parse_all(self) -> Dict[str, Any]:
        """
        Parse all data sources into unified JSON structure.
        
        Returns:
            {
                "ticker": "NVDA",
                "snapshot": { "metric_name": "value", ... },  # 66 metrics
                "income_statement": {
                    "TTM": {...}, 
                    "FY_2024": {...}, 
                    "FY_2023": {...}
                },
                "balance_sheet": {...},
                "cash_flow": {...},
                "metadata": {
                    "paywall_detected": bool,
                    "periods_available": int,
                    "parsed_at": str
                }
            }
        """
        from datetime import datetime
        
        logger.info("Starting comprehensive parse", extra={"ticker": self.ticker})
        
        result = {
            "ticker": self.ticker,
            "snapshot": {},
            "income_statement": {},
            "balance_sheet": {},
            "cash_flow": {},
            "metadata": {
                "paywall_detected": False,
                "periods_available": 0,
                "parsed_at": datetime.utcnow().isoformat() + "Z"
            }
        }
        
        try:
            # Parse snapshot-table2 (66 fundamental metrics)
            result["snapshot"] = self.parse_snapshot_table()
            logger.info(
                "Parsed snapshot table",
                extra={"ticker": self.ticker, "metric_count": len(result["snapshot"])}
            )
            
            # Parse financial statements
            result["income_statement"] = self.parse_income_statement()
            result["balance_sheet"] = self.parse_balance_sheet()
            result["cash_flow"] = self.parse_cash_flow()
            
            # Detect paywall and count periods
            periods = result["income_statement"].keys()
            result["metadata"]["periods_available"] = len(periods)
            result["metadata"]["paywall_detected"] = self._detect_paywall()
            
            logger.info(
                "Parse completed successfully",
                extra={
                    "ticker": self.ticker,
                    "snapshot_metrics": len(result["snapshot"]),
                    "income_statement_periods": len(result["income_statement"]),
                    "paywall_detected": result["metadata"]["paywall_detected"]
                }
            )
            
        except Exception as e:
            logger.error(
                "Parse failed",
                extra={"ticker": self.ticker, "error": str(e)},
                exc_info=True
            )
            raise
        
        return result
    
    def parse_snapshot_table(self) -> Dict[str, str]:
        """
        Parse snapshot-table2 (66 fundamental metrics).
        
        Structure: 12 rows × 6 metric pairs per row = 72 cells (66 unique metrics)
        Pattern: <td class="snapshot-td2">Label</td><td class="snapshot-td2"><b>Value</b></td>
        
        Returns:
            {"Index": "DJIA, NDX, S&P 500", "P/E": "42.34", "EPS (ttm)": "4.04", ...}
        """
        logger.debug("Parsing snapshot-table2", extra={"ticker": self.ticker})
        
        snapshot_table = self.fullpage_soup.find('table', class_='snapshot-table2')
        if not snapshot_table:
            logger.warning("snapshot-table2 not found", extra={"ticker": self.ticker})
            return {}
        
        metrics = {}
        td_elements = snapshot_table.find_all('td', class_='snapshot-td2')
        
        # Process pairs: label at even index, value at odd index
        for i in range(0, len(td_elements) - 1, 2):
            label_td = td_elements[i]
            value_td = td_elements[i + 1]
            
            # Extract label (strip whitespace)
            label = label_td.get_text(strip=True)
            
            # Extract value (look for <b> tag first, fallback to text)
            value_tag = value_td.find('b')
            value = value_tag.get_text(strip=True) if value_tag else value_td.get_text(strip=True)
            
            # Skip empty labels (merged cells at row ends)
            if label:
                metrics[label] = value
        
        logger.debug(
            "Snapshot table parsed",
            extra={"ticker": self.ticker, "metric_count": len(metrics)}
        )
        
        return metrics
    
    def parse_income_statement(self) -> Dict[str, Dict[str, str]]:
        """
        Parse Income Statement table.
        
        Structure:
        - Header: Period | [chart] | TTM | FY 2024 | FY 2023 | [PAYWALL]
        - Rows: ~30 line items (Total Revenue, COGS, Gross Profit, etc.)
        - Paywall blocks FY 2022 and older
        
        Returns:
            {
                "TTM": {"Total Revenue": "187,142.00", "COGS": "56,049.00", ...},
                "FY_2024": {"Total Revenue": "130,497.00", ...},
                "FY_2023": {"Total Revenue": "60,922.00", ...}
            }
        """
        logger.debug("Parsing income statement", extra={"ticker": self.ticker})
        
        # Find the financial statements table (use income_statement_soup)
        table = self.income_statement_soup.find('table', class_='quote_statements-table')
        if not table:
            logger.warning("Income statement table not found", extra={"ticker": self.ticker})
            return {}
        
        # Extract periods from header row
        periods = self._extract_periods(table)
        logger.debug("Periods extracted", extra={"ticker": self.ticker, "periods": periods})
        
        # Parse metric rows
        result = {period: {} for period in periods}
        
        rows = table.find_all('tr', class_='styled-row')
        for row in rows:
            # Skip paywall rows
            if 'elite-row' in row.get('class', []):
                continue
            
            # Extract metric name from first column
            metric_name_td = row.find('td', class_='align-top')
            if not metric_name_td:
                continue
            
            metric_name = metric_name_td.get_text(strip=True)
            
            # Extract values for each period (skip chart column)
            value_tds = row.find_all('td', align='right', class_='align-top')
            
            # Match values to periods (skip paywall columns)
            for i, value_td in enumerate(value_tds):
                if i >= len(periods):
                    break
                
                # Skip paywall cells
                if 'quote-statements-elite-subscribe' in value_td.get('class', []):
                    break
                
                # Extract value from <span> tag
                value_span = value_td.find('span')
                value = value_span.get_text(strip=True) if value_span else value_td.get_text(strip=True)
                
                result[periods[i]][metric_name] = value
        
        logger.debug(
            "Income statement parsed",
            extra={
                "ticker": self.ticker,
                "periods": len(result),
                "metrics_per_period": len(result.get(periods[0], {})) if periods else 0
            }
        )
        
        return result
    
    def parse_balance_sheet(self) -> Dict[str, Dict[str, str]]:
        """
        Parse Balance Sheet table.
        
        Structure: Same as Income Statement but with Balance Sheet metrics
        - Header: Period | [chart] | TTM | FY 2024 | FY 2023 | [PAYWALL]
        - Rows: ~20-30 line items (Cash, Total Assets, Total Liabilities, Equity, etc.)
        - Paywall blocks FY 2022 and older
        
        Returns:
            {
                "TTM": {"Cash & Equivalents": "...", "Total Assets": "...", "Total Liabilities": "...", ...},
                "FY_2024": {...},
                "FY_2023": {...}
            }
        """
        logger.debug("Parsing balance sheet", extra={"ticker": self.ticker})
        
        # Find the financial statements table (use balance_sheet_soup)
        table = self.balance_sheet_soup.find('table', class_='quote_statements-table')
        if not table:
            logger.warning("Balance sheet table not found", extra={"ticker": self.ticker})
            return {}
        
        # Extract periods from header row
        periods = self._extract_periods(table)
        logger.debug("Balance sheet periods extracted", extra={"ticker": self.ticker, "periods": periods})
        
        # Parse metric rows (same structure as income statement)
        result = {period: {} for period in periods}
        
        rows = table.find_all('tr', class_='styled-row')
        for row in rows:
            # Skip paywall rows
            if 'elite-row' in row.get('class', []):
                continue
            
            # Extract metric name from first column
            metric_name_td = row.find('td', class_='align-top')
            if not metric_name_td:
                continue
            
            metric_name = metric_name_td.get_text(strip=True)
            
            # Extract values for each period (skip chart column)
            value_tds = row.find_all('td', align='right', class_='align-top')
            
            # Match values to periods (skip paywall columns)
            for i, value_td in enumerate(value_tds):
                if i >= len(periods):
                    break
                
                # Skip paywall cells
                if 'quote-statements-elite-subscribe' in value_td.get('class', []):
                    break
                
                # Extract value from <span> tag
                value_span = value_td.find('span')
                value = value_span.get_text(strip=True) if value_span else value_td.get_text(strip=True)
                
                result[periods[i]][metric_name] = value
        
        logger.debug(
            "Balance sheet parsed",
            extra={
                "ticker": self.ticker,
                "periods": len(result),
                "metrics_per_period": len(result.get(periods[0], {})) if periods else 0
            }
        )
        
        return result
    
    def parse_cash_flow(self) -> Dict[str, Dict[str, str]]:
        """
        Parse Cash Flow table.
        
        Structure: Same as Income Statement but with Cash Flow metrics
        - Header: Period | [chart] | TTM | FY 2024 | FY 2023 | [PAYWALL]
        - Rows: ~15-20 line items (Operating CF, Investing CF, Financing CF, Free CF, etc.)
        - Paywall blocks FY 2022 and older
        
        Returns:
            {
                "TTM": {"Operating Cash Flow": "...", "Investing Cash Flow": "...", "Free Cash Flow": "...", ...},
                "FY_2024": {...},
                "FY_2023": {...}
            }
        """
        logger.debug("Parsing cash flow", extra={"ticker": self.ticker})
        
        # Find the financial statements table (use cash_flow_soup)
        table = self.cash_flow_soup.find('table', class_='quote_statements-table')
        if not table:
            logger.warning("Cash flow table not found", extra={"ticker": self.ticker})
            return {}
        
        # Extract periods from header row
        periods = self._extract_periods(table)
        logger.debug("Cash flow periods extracted", extra={"ticker": self.ticker, "periods": periods})
        
        # Parse metric rows (same structure as income statement)
        result = {period: {} for period in periods}
        
        rows = table.find_all('tr', class_='styled-row')
        for row in rows:
            # Skip paywall rows
            if 'elite-row' in row.get('class', []):
                continue
            
            # Extract metric name from first column
            metric_name_td = row.find('td', class_='align-top')
            if not metric_name_td:
                continue
            
            metric_name = metric_name_td.get_text(strip=True)
            
            # Extract values for each period (skip chart column)
            value_tds = row.find_all('td', align='right', class_='align-top')
            
            # Match values to periods (skip paywall columns)
            for i, value_td in enumerate(value_tds):
                if i >= len(periods):
                    break
                
                # Skip paywall cells
                if 'quote-statements-elite-subscribe' in value_td.get('class', []):
                    break
                
                # Extract value from <span> tag
                value_span = value_td.find('span')
                value = value_span.get_text(strip=True) if value_span else value_td.get_text(strip=True)
                
                result[periods[i]][metric_name] = value
        
        logger.debug(
            "Cash flow parsed",
            extra={
                "ticker": self.ticker,
                "periods": len(result),
                "metrics_per_period": len(result.get(periods[0], {})) if periods else 0
            }
        )
        
        return result
        return {}
    
    def _extract_periods(self, table) -> List[str]:
        """
        Extract period labels from table header.
        
        Returns: ['TTM', 'FY_2024', 'FY_2023'] (up to 3 periods for free tier)
        """
        # Find the first row with class "first-row" which contains periods
        header_row = table.find('tr', class_='first-row')
        if not header_row:
            return []
        
        period_headers = []
        
        # Find all header cells with align="right" (period columns)
        for td in header_row.find_all('td', align='right', class_='align-top'):
            span = td.find('span')
            if not span:
                continue
            
            period_text = span.get_text(strip=True)
            
            # Skip empty cells
            if not period_text or period_text == 'Period':
                continue
            
            # Normalize period labels
            if period_text == 'TTM':
                period_headers.append('TTM')
            elif 'FY' in period_text:
                # Extract year: "FY 2024" -> "FY_2024"
                year_match = re.search(r'(\d{4})', period_text)
                if year_match:
                    period_headers.append(f'FY_{year_match.group(1)}')
        
        return period_headers
    
    def _detect_paywall(self) -> bool:
        """
        Detect if paywall is present (Elite subscription required).
        
        Paywall indicators:
        - Class "elite-row" in table rows
        - Large merged cell with "quote-statements-elite-subscribe" class
        - Less than 8 periods available (free tier shows 3, Elite shows 8)
        
        Returns: True if paywall detected
        """
        # Check for elite-row class (check income statement as representative)
        elite_rows = self.income_statement_soup.find_all(class_='elite-row')
        if elite_rows:
            return True
        
        # Check for subscription promotion cell
        elite_subscribe = self.income_statement_soup.find(class_='quote-statements-elite-subscribe')
        if elite_subscribe:
            return True
        
        return False


def parse_finviz_files(
    fullpage_path: str, 
    income_statement_path: str, 
    balance_sheet_path: Optional[str] = None,
    cash_flow_path: Optional[str] = None,
    ticker: str = ""
) -> Dict[str, Any]:
    """
    Convenience function to parse Finviz HTML files directly.
    
    Supports two architectures:
    - NEW (Option 1): 3 self-contained files (each with snapshot + statement)
    - OLD: 4 separate files (1 fullpage + 3 statement-only files)
    
    Args:
        fullpage_path: 
            - NEW architecture: Same as income_statement_path (self-contained)
            - OLD architecture: Separate fullpage HTML with snapshot only
        income_statement_path: 
            - NEW architecture: Full page HTML with snapshot + income statement
            - OLD architecture: Statement-only HTML
        balance_sheet_path: 
            - NEW architecture: Full page HTML with snapshot + balance sheet
            - OLD architecture: Statement-only HTML (optional, uses income as fallback)
        cash_flow_path: 
            - NEW architecture: Full page HTML with snapshot + cash flow
            - OLD architecture: Statement-only HTML (optional, uses income as fallback)
        ticker: Stock ticker symbol
    
    Returns:
        Parsed JSON structure with all financial data
    
    Example (NEW 3-file architecture - recommended):
        >>> result = parse_finviz_files(
        ...     fullpage_path='docs/Ingest/finviz_income_statement_nvda.html',
        ...     income_statement_path='docs/Ingest/finviz_income_statement_nvda.html',
        ...     balance_sheet_path='docs/Ingest/finviz_balance_sheet_nvda.html',
        ...     cash_flow_path='docs/Ingest/finviz_cash_flow_nvda.html',
        ...     ticker='NVDA'
        ... )
        >>> print(result['snapshot']['Market Cap'])
        '4153.84B'
        
    Example (OLD 4-file architecture - backwards compatible):
        >>> result = parse_finviz_files(
        ...     fullpage_path='docs/Ingest/finviz_fullpage_nvda.html',
        ...     income_statement_path='docs/Ingest/finviz_income_statement_nvda.html',
        ...     balance_sheet_path='docs/Ingest/finviz_balance_sheet_nvda.html',
        ...     cash_flow_path='docs/Ingest/finviz_cash_flow_nvda.html',
        ...     ticker='NVDA'
        ... )
    
    Note:
        For NEW architecture, fullpage_path and income_statement_path point to same file.
        Parser automatically detects which architecture based on file contents.
    """
    logger.info("Loading Finviz HTML files", extra={"ticker": ticker})
    
    try:
        with open(fullpage_path, 'r', encoding='utf-8') as f:
            fullpage_html = f.read()
        
        with open(income_statement_path, 'r', encoding='utf-8') as f:
            income_html = f.read()
        
        # Load balance sheet if provided
        balance_html = None
        if balance_sheet_path:
            with open(balance_sheet_path, 'r', encoding='utf-8') as f:
                balance_html = f.read()
        
        # Load cash flow if provided
        cashflow_html = None
        if cash_flow_path:
            with open(cash_flow_path, 'r', encoding='utf-8') as f:
                cashflow_html = f.read()
        
        parser = FinvizParser(fullpage_html, income_html, balance_html, cashflow_html, ticker)
        return parser.parse_all()
        
    except FileNotFoundError as e:
        logger.error(
            "HTML file not found",
            extra={"ticker": ticker, "error": str(e)},
            exc_info=True
        )
        raise
    except Exception as e:
        logger.error(
            "Parse failed",
            extra={"ticker": ticker, "error": str(e)},
            exc_info=True
        )
        raise
