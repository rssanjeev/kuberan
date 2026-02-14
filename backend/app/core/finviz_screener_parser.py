"""
FinViz Screener Parser

Parses HTML files extracted from FinViz screener pages to extract
ticker data including sector, industry, country, market cap, P/E, price, etc.

This parser works with the "Overview" view (v=111) of the FinViz screener.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from bs4 import BeautifulSoup

from app.core.logging_config import get_logger

logger = get_logger(__name__)


def parse_screener_html(html_content: str) -> List[Dict[str, Any]]:
    """
    Parse FinViz screener HTML content and extract ticker data.
    
    Args:
        html_content: Raw HTML content from FinViz screener page
        
    Returns:
        List of ticker dictionaries with parsed data
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    tickers = []
    
    # Find the screener table - it has class "screener_table"
    screener_table = soup.find('table', class_='screener_table')
    
    if not screener_table:
        logger.warning("Could not find screener_table in HTML")
        return []
    
    # Find all data rows (skip header row)
    rows = screener_table.find('tbody').find_all('tr', class_='styled-row')
    
    logger.info(f"Found {len(rows)} ticker rows in screener table")
    
    for row in rows:
        cells = row.find_all('td')
        
        if len(cells) < 11:
            continue
            
        try:
            ticker_data = _parse_row(cells)
            if ticker_data:
                tickers.append(ticker_data)
        except Exception as e:
            logger.warning(f"Failed to parse row: {e}")
            continue
    
    logger.info(f"Successfully parsed {len(tickers)} tickers from screener")
    return tickers


def _parse_row(cells: List) -> Optional[Dict[str, Any]]:
    """
    Parse a single row from the screener table.
    
    Column order (Overview v=111):
    0: No. (row number)
    1: Ticker
    2: Company
    3: Sector
    4: Industry
    5: Country
    6: Market Cap
    7: P/E
    8: Price
    9: Change
    10: Volume
    """
    # Extract text from each cell
    row_num = _get_cell_text(cells[0])
    ticker = _get_cell_text(cells[1])
    company = _get_cell_text(cells[2])
    sector = _get_cell_text(cells[3])
    industry = _get_cell_text(cells[4])
    country = _get_cell_text(cells[5])
    market_cap_raw = _get_cell_text(cells[6])
    pe_raw = _get_cell_text(cells[7])
    price_raw = _get_cell_text(cells[8])
    change_raw = _get_cell_text(cells[9])
    volume_raw = _get_cell_text(cells[10])
    
    if not ticker:
        return None
    
    return {
        "ticker": ticker,
        "company_name": company,
        "sector": sector,
        "industry": industry,
        "country": country,
        "market_cap_raw": market_cap_raw,
        "market_cap": _parse_market_cap(market_cap_raw),
        "pe_ratio_raw": pe_raw,
        "pe_ratio": _parse_number(pe_raw),
        "price_raw": price_raw,
        "price": _parse_number(price_raw),
        "change_raw": change_raw,
        "change_percent": _parse_percent(change_raw),
        "volume_raw": volume_raw,
        "volume": _parse_volume(volume_raw),
        "is_etf": industry == "Exchange Traded Fund",
        "source": "finviz_screener",
        "parsed_at": datetime.now(timezone.utc).isoformat()
    }


def _get_cell_text(cell) -> str:
    """Extract clean text from a table cell."""
    # Try to find anchor tag first
    link = cell.find('a')
    if link:
        # Handle span inside anchor (for colored price/change)
        span = link.find('span')
        if span:
            return span.get_text(strip=True)
        return link.get_text(strip=True)
    return cell.get_text(strip=True)


def _parse_market_cap(value: str) -> Optional[float]:
    """
    Parse market cap string to numeric value in dollars.
    
    Examples:
        "38.85B" -> 38850000000.0
        "285.05M" -> 285050000.0
        "1.23T" -> 1230000000000.0
        "-" -> None
    """
    if not value or value == "-":
        return None
    
    value = value.strip().upper()
    
    multipliers = {
        'K': 1_000,
        'M': 1_000_000,
        'B': 1_000_000_000,
        'T': 1_000_000_000_000
    }
    
    for suffix, multiplier in multipliers.items():
        if value.endswith(suffix):
            try:
                number = float(value[:-1])
                return number * multiplier
            except ValueError:
                return None
    
    try:
        return float(value)
    except ValueError:
        return None


def _parse_number(value: str) -> Optional[float]:
    """Parse a numeric string, handling dashes and commas."""
    if not value or value == "-":
        return None
    
    # Remove commas and clean up
    value = value.replace(',', '').strip()
    
    try:
        return float(value)
    except ValueError:
        return None


def _parse_percent(value: str) -> Optional[float]:
    """
    Parse percentage string to decimal.
    
    Examples:
        "0.25%" -> 0.0025
        "-3.27%" -> -0.0327
        "0.00%" -> 0.0
    """
    if not value or value == "-":
        return None
    
    value = value.strip().replace('%', '')
    
    try:
        return float(value) / 100
    except ValueError:
        return None


def _parse_volume(value: str) -> Optional[int]:
    """Parse volume string to integer."""
    if not value or value == "-":
        return None
    
    # Remove commas
    value = value.replace(',', '').strip()
    
    try:
        return int(float(value))
    except ValueError:
        return None


def parse_screener_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Parse a FinViz screener HTML file.
    
    Args:
        file_path: Path to the HTML file
        
    Returns:
        List of parsed ticker dictionaries
    """
    path = Path(file_path)
    
    if not path.exists():
        logger.error(f"File not found: {file_path}")
        return []
    
    logger.info(f"Parsing screener file: {file_path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    return parse_screener_html(html_content)


def parse_all_screener_pages(directory: str) -> Dict[str, Any]:
    """
    Parse all FinViz screener HTML files in a directory.
    
    Assumes files are named: finviz_screener_overview_page{N}.html
    
    Args:
        directory: Path to directory containing HTML files
        
    Returns:
        Dictionary with parsed data and metadata
    """
    dir_path = Path(directory)
    
    if not dir_path.exists():
        logger.error(f"Directory not found: {directory}")
        return {"tickers": [], "metadata": {"error": "Directory not found"}}
    
    # Find all screener HTML files
    html_files = sorted(dir_path.glob("finviz_screener_overview*.html"))
    
    if not html_files:
        logger.warning(f"No screener HTML files found in {directory}")
        return {"tickers": [], "metadata": {"error": "No HTML files found"}}
    
    logger.info(f"Found {len(html_files)} screener HTML files")
    
    all_tickers = []
    pages_parsed = 0
    
    for html_file in html_files:
        tickers = parse_screener_file(str(html_file))
        all_tickers.extend(tickers)
        pages_parsed += 1
        logger.info(f"Parsed {html_file.name}: {len(tickers)} tickers")
    
    # Deduplicate by ticker (keep first occurrence)
    seen_tickers = set()
    unique_tickers = []
    
    for ticker_data in all_tickers:
        ticker = ticker_data["ticker"]
        if ticker not in seen_tickers:
            seen_tickers.add(ticker)
            unique_tickers.append(ticker_data)
    
    # Compute statistics
    etf_count = sum(1 for t in unique_tickers if t.get("is_etf"))
    stock_count = len(unique_tickers) - etf_count
    
    sectors = {}
    countries = {}
    
    for t in unique_tickers:
        sector = t.get("sector")
        country = t.get("country")
        
        if sector:
            sectors[sector] = sectors.get(sector, 0) + 1
        if country:
            countries[country] = countries.get(country, 0) + 1
    
    metadata = {
        "total_tickers": len(unique_tickers),
        "pages_parsed": pages_parsed,
        "etf_count": etf_count,
        "stock_count": stock_count,
        "sector_breakdown": sectors,
        "country_breakdown": countries,
        "parsed_at": datetime.now(timezone.utc).isoformat()
    }
    
    logger.info(
        f"Screener parsing complete",
        extra={
            "total_tickers": len(unique_tickers),
            "etf_count": etf_count,
            "stock_count": stock_count
        }
    )
    
    return {
        "tickers": unique_tickers,
        "metadata": metadata
    }


if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) < 2:
        print("Usage: python finviz_screener_parser.py <html_file_or_directory>")
        sys.exit(1)
    
    path = Path(sys.argv[1])
    
    if path.is_dir():
        result = parse_all_screener_pages(str(path))
        print(f"\n📊 Parsed {result['metadata']['total_tickers']} tickers from {result['metadata']['pages_parsed']} pages")
        print(f"   - Stocks: {result['metadata']['stock_count']}")
        print(f"   - ETFs: {result['metadata']['etf_count']}")
        
        # Save to JSON
        output_file = path / "finviz_screener_parsed.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n💾 Saved to: {output_file}")
    else:
        tickers = parse_screener_file(str(path))
        print(f"\n📊 Parsed {len(tickers)} tickers from {path.name}")
        
        # Show first 5 tickers
        print("\nFirst 5 tickers:")
        for t in tickers[:5]:
            print(f"  {t['ticker']}: {t['company_name']} ({t['sector']})")
