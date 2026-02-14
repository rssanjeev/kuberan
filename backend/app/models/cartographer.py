"""
Cartographer Data Models

Defines the schema for config-driven web scraping architecture.

Last Updated: 2025-12-20
Status: Active
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field
from beanie import Document


class DataType(str, Enum):
    """Supported data types for Smart Parser."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    PERCENTAGE = "percentage"
    CURRENCY = "currency"
    DATE = "date"
    BOOLEAN = "boolean"
    LIST = "list"


class ExtractionMode(str, Enum):
    """How to extract data from a region."""
    SELECTOR = "selector"      # Use individual CSS selectors for each field
    LABEL_BASED = "label_based"  # Find labels in table, extract adjacent values


class SelectorType(str, Enum):
    """CSS selector types."""
    CSS = "css"
    XPATH = "xpath"
    TEXT = "text"


class InterceptorAction(str, Enum):
    """Actions to take when interceptor triggers."""
    CLICK = "click"
    CLOSE = "close"
    WAIT = "wait"
    DISMISS = "dismiss"


class PageSignature(BaseModel):
    """Unique identifier for a page type."""
    name: str = Field(..., description="Human-readable page type name")
    url_pattern: str = Field(..., description="Regex pattern to match URL")
    required_elements: List[str] = Field(
        default_factory=list,
        description="CSS selectors that MUST exist"
    )
    forbidden_elements: List[str] = Field(
        default_factory=list,
        description="CSS selectors that MUST NOT exist"
    )


class GlobalInterceptor(BaseModel):
    """Rules for handling pop-ups and interruptions."""
    name: str = Field(..., description="Interceptor identifier")
    trigger_selector: str = Field(..., description="CSS selector for detection")
    action: InterceptorAction = Field(..., description="Action to take")
    target_selector: Optional[str] = Field(
        None,
        description="Target for action (e.g., close button)"
    )
    timeout_ms: int = Field(default=2000, description="Wait timeout")
    priority: int = Field(default=100, description="Execution priority (lower=first)")


class SelectorStrategy(BaseModel):
    """Fallback selector chain."""
    primary: str = Field(..., description="Primary CSS selector")
    fallbacks: List[str] = Field(
        default_factory=list,
        description="Fallback selectors in order"
    )
    selector_type: SelectorType = Field(default=SelectorType.CSS)


class ParsingRule(BaseModel):
    """Defines how to extract and cast a data point."""
    field_name: str = Field(..., description="Normalized field name")
    label_text: Optional[str] = Field(
        None,
        description="Label to search for (e.g., 'P/E')"
    )
    selector: SelectorStrategy = Field(..., description="Selector strategy")
    data_type: DataType = Field(..., description="Target data type")
    transformation: Optional[str] = Field(
        None,
        description="Optional transformation function"
    )
    required: bool = Field(default=False, description="Is field required?")
    paywalled: bool = Field(default=False, description="Is behind paywall?")


class LabelFieldMapping(BaseModel):
    """Maps a label text to a normalized field name for label-based extraction."""
    label: str = Field(..., description="Exact label text to search for (e.g., 'P/E')")
    field_name: str = Field(..., description="Normalized field name (e.g., 'pe_ratio')")
    data_type: DataType = Field(default=DataType.STRING)
    required: bool = Field(default=False)
    paywalled: bool = Field(default=False)


class LabelBasedConfig(BaseModel):
    """Configuration for label-based extraction mode."""
    label_selector: str = Field(
        ...,
        description="Selector for label cells (e.g., 'td.snapshot-td2:nth-child(odd)')"
    )
    value_selector: str = Field(
        default="following-sibling",
        description="How to find value relative to label: 'following-sibling', 'next-td', 'same-row'"
    )
    field_mappings: List[LabelFieldMapping] = Field(
        default_factory=list,
        description="List of label→field mappings to extract"
    )
    extract_all: bool = Field(
        default=False,
        description="If True, extract ALL label/value pairs (not just mapped ones)"
    )


class RegionDefinition(BaseModel):
    """A logical region on the page (e.g., 'snapshot_table')."""
    region_id: str = Field(..., description="Unique region identifier")
    description: str = Field(..., description="Human-readable description")
    container_selector: str = Field(..., description="CSS selector for container")
    extraction_mode: ExtractionMode = Field(
        default=ExtractionMode.SELECTOR,
        description="How to extract data: 'selector' (individual selectors) or 'label_based' (find labels)"
    )
    parsing_rules: List[ParsingRule] = Field(
        default_factory=list,
        description="Rules for fields in this region (used in 'selector' mode)"
    )
    label_config: Optional[LabelBasedConfig] = Field(
        None,
        description="Configuration for label-based extraction (used in 'label_based' mode)"
    )


class PageTemplate(BaseModel):
    """Complete template for a page type."""
    signature: PageSignature
    regions: List[RegionDefinition]
    interceptors: List[str] = Field(
        default_factory=list,
        description="Global interceptor IDs to apply"
    )


class SiteDictionary(BaseModel):
    """Generated mapping of extractable data."""
    site_name: str = Field(..., description="Website name")
    base_url: str = Field(..., description="Base URL for the site")
    generated_at: datetime = Field(default_factory=datetime.now)
    templates: Dict[str, PageTemplate] = Field(
        default_factory=dict,
        description="Page type → template mapping"
    )
    interceptors: List[GlobalInterceptor] = Field(
        default_factory=list,
        description="Global interceptor definitions"
    )
    metadata: Dict[str, Union[str, int, float]] = Field(
        default_factory=dict,
        description="Additional metadata"
    )


class ScrapingResult(BaseModel):
    """Result from a single scraping operation."""
    ticker: str
    page_type: str
    extracted_data: Dict[str, Union[str, int, float, bool, None]]
    interceptors_triggered: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)
    selectors_used: Dict[str, str] = Field(
        default_factory=dict,
        description="Field → selector mapping (for debugging)"
    )


class CartographerConfig(BaseModel):
    """Root configuration object."""
    site_name: str
    base_url: str
    global_interceptors: List[GlobalInterceptor]
    page_templates: List[PageTemplate]
    settings: Dict[str, Union[str, int, bool]] = Field(
        default_factory=dict,
        description="Global settings (timeouts, retries, etc.)"
    )


# ============================================================================
# MongoDB Document Models
# ============================================================================

class FinvizIdentity(BaseModel):
    """Company identification and classification fields."""
    company_name: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    index: Optional[str] = None  # quote_page only
    employees: Optional[int] = None  # quote_page only
    ipo_date: Optional[str] = None  # quote_page only


class FinvizPrice(BaseModel):
    """Current price and trading data."""
    price: Optional[float] = None
    change: Optional[str] = None
    change_from_open: Optional[str] = None  # screener only
    gap: Optional[str] = None  # screener only
    prev_close: Optional[float] = None  # quote_page only
    volume: Optional[str] = None
    avg_volume: Optional[str] = None
    rel_volume: Optional[float] = None
    trades: Optional[str] = None  # quote_page only


class FinvizValuation(BaseModel):
    """Valuation ratios and metrics."""
    market_cap: Optional[str] = None
    enterprise_value: Optional[str] = None  # quote_page only
    pe_ratio: Optional[float] = None
    forward_pe: Optional[float] = None
    peg_ratio: Optional[float] = None
    price_to_sales: Optional[float] = None
    price_to_book: Optional[float] = None
    price_to_cash: Optional[float] = None
    price_to_fcf: Optional[float] = None
    ev_to_ebitda: Optional[float] = None  # quote_page only
    ev_to_sales: Optional[float] = None  # quote_page only


class FinvizFinancials(BaseModel):
    """Financial metrics (quote_page only)."""
    income: Optional[str] = None
    sales: Optional[str] = None
    book_value_per_share: Optional[float] = None
    cash_per_share: Optional[float] = None


class FinvizProfitability(BaseModel):
    """Profitability ratios and margins."""
    roa: Optional[str] = None
    roe: Optional[str] = None
    roic: Optional[str] = None
    gross_margin: Optional[str] = None
    operating_margin: Optional[str] = None
    profit_margin: Optional[str] = None


class FinvizLiquidity(BaseModel):
    """Liquidity and solvency ratios."""
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    debt_to_equity: Optional[float] = None
    lt_debt_to_equity: Optional[float] = None  # quote_page only


class FinvizDividend(BaseModel):
    """Dividend information."""
    dividend: Optional[str] = None  # quote_page only
    dividend_yield: Optional[str] = None
    payout_ratio: Optional[str] = None  # quote_page only
    ex_dividend_date: Optional[str] = None  # quote_page only


class FinvizGrowth(BaseModel):
    """Growth metrics (mostly quote_page only)."""
    eps_ttm: Optional[float] = None
    eps_next_year: Optional[float] = None  # quote_page only
    eps_next_quarter: Optional[float] = None  # quote_page only
    eps_growth_this_year: Optional[str] = None
    eps_growth_next_year: Optional[str] = None
    eps_growth_next_5y: Optional[str] = None
    eps_growth_past_5y: Optional[str] = None
    sales_growth_past_5y: Optional[str] = None
    sales_growth_quarter: Optional[str] = None


class FinvizOwnership(BaseModel):
    """Ownership and shares data (quote_page only)."""
    insider_ownership: Optional[str] = None
    insider_transactions: Optional[str] = None
    institutional_ownership: Optional[str] = None
    institutional_transactions: Optional[str] = None
    shares_outstanding: Optional[str] = None
    shares_float: Optional[str] = None
    short_float: Optional[str] = None
    short_ratio: Optional[float] = None
    float_short: Optional[str] = None


class FinvizTechnical(BaseModel):
    """Technical indicators."""
    beta: Optional[float] = None
    atr: Optional[float] = None
    volatility_week: Optional[str] = None
    volatility_month: Optional[str] = None
    rsi_14: Optional[float] = None
    sma_20: Optional[str] = None
    sma_50: Optional[str] = None
    sma_200: Optional[str] = None
    high_52w: Optional[float] = None
    low_52w: Optional[float] = None
    from_high_52w: Optional[str] = None
    from_low_52w: Optional[str] = None
    recom: Optional[float] = None  # analyst recommendation
    target_price: Optional[float] = None


class FinvizPerformance(BaseModel):
    """Performance over various periods."""
    perf_week: Optional[str] = None
    perf_month: Optional[str] = None
    perf_quarter: Optional[str] = None
    perf_half_year: Optional[str] = None
    perf_year: Optional[str] = None
    perf_ytd: Optional[str] = None


class FinvizSourceInfo(BaseModel):
    """Tracks data source and completeness."""
    screener_collected_at: Optional[datetime] = None
    quote_page_collected_at: Optional[datetime] = None
    screener_tab: Optional[str] = None  # overview, valuation, financial, technical
    is_complete: bool = Field(
        default=False,
        description="True when both screener and quote_page data collected"
    )
    screener_fields_count: int = 0
    quote_page_fields_count: int = 0


class FinvizSnapshot(Document):
    """
    FinViz scraped data stored in MongoDB.
    
    Dual-Pipeline Architecture:
    - Pipeline 1 (Screener): Bulk collection, 20 tickers at a time, 4 tabs
    - Pipeline 2 (Quote Page): Deep dive, 1 ticker at a time, quote-only fields
    
    Data is merged from both sources into a single document per ticker.
    """
    
    provider: str = Field(default="finviz")
    ticker: str = Field(..., description="Stock/ETF ticker")
    entity_type: str = Field(default="stock", description="stock or etf")
    as_of: datetime = Field(default_factory=datetime.now)
    
    # Structured Data Sections (aligned with FINVIZ_SCHEMA.json)
    identity: FinvizIdentity = Field(default_factory=FinvizIdentity)
    price: FinvizPrice = Field(default_factory=FinvizPrice)
    valuation: FinvizValuation = Field(default_factory=FinvizValuation)
    financials: FinvizFinancials = Field(default_factory=FinvizFinancials)
    profitability: FinvizProfitability = Field(default_factory=FinvizProfitability)
    liquidity: FinvizLiquidity = Field(default_factory=FinvizLiquidity)
    dividend: FinvizDividend = Field(default_factory=FinvizDividend)
    growth: FinvizGrowth = Field(default_factory=FinvizGrowth)
    ownership: FinvizOwnership = Field(default_factory=FinvizOwnership)
    technical: FinvizTechnical = Field(default_factory=FinvizTechnical)
    performance: FinvizPerformance = Field(default_factory=FinvizPerformance)
    
    # Related Entities (quote_page only)
    peers: List[str] = Field(default_factory=list)
    held_by_etfs: List[str] = Field(default_factory=list)
    
    # Source Tracking (dual-pipeline support)
    source: FinvizSourceInfo = Field(default_factory=FinvizSourceInfo)
    
    # Flexible storage for any additional/unmapped fields
    extra_fields: Dict[str, Union[str, int, float, bool, None]] = Field(
        default_factory=dict,
        description="Any fields not in structured sections"
    )
    
    # Metadata
    page_url: Optional[str] = None
    interceptors_triggered: List[str] = Field(default_factory=list)
    selectors_used: Dict[str, str] = Field(default_factory=dict)
    paywalled_fields: List[str] = Field(
        default_factory=list,
        description="Fields behind Elite paywall"
    )
    errors: List[str] = Field(default_factory=list)
    
    class Settings:
        name = "finviz_snapshots"
        indexes = [
            [("ticker", 1), ("as_of", -1)],  # Latest snapshot per ticker
            [("ticker", 1)],  # Unique ticker lookup
            [("entity_type", 1)],
            [("identity.sector", 1)],
            [("source.is_complete", 1)],  # Find incomplete records
            [("as_of", -1)],
        ]


class StockAnalysisSnapshot(Document):
    """StockAnalysis.com scraped data stored in MongoDB."""
    
    provider: str = Field(default="stockanalysis")
    ticker: str = Field(..., description="Stock/ETF ticker")
    entity_type: str = Field(..., description="stock or etf")
    as_of: datetime = Field(default_factory=datetime.now)
    
    # Company Info
    display_name: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    
    # Extracted Fields
    fields: Dict[str, Union[str, int, float, bool, None]] = Field(
        default_factory=dict,
        description="All extracted fields"
    )
    
    # Metadata
    page_url: Optional[str] = None
    interceptors_triggered: List[str] = Field(default_factory=list)
    selectors_used: Dict[str, str] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)
    
    class Settings:
        name = "stockanalysis_snapshots"
        indexes = [
            [("ticker", 1), ("as_of", -1)],
            [("entity_type", 1)],
            [("as_of", -1)],
        ]


class AlphaVantageSnapshot(Document):
    """Alpha Vantage API data stored in MongoDB."""
    
    provider: str = Field(default="alphavantage")
    ticker: str = Field(..., description="Stock/ETF ticker")
    entity_type: str = Field(..., description="stock or etf")
    as_of: datetime = Field(default_factory=datetime.now)
    
    # Company Overview
    display_name: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    exchange: Optional[str] = None
    
    # Extracted Fields (Alpha Vantage provides rich fundamental data)
    fields: Dict[str, Union[str, int, float, bool, None]] = Field(
        default_factory=dict,
        description="All extracted fields from API response"
    )
    
    # Metadata
    api_endpoint: Optional[str] = None
    errors: List[str] = Field(default_factory=list)
    
    class Settings:
        name = "alphavantage_snapshots"
        indexes = [
            [("ticker", 1), ("as_of", -1)],
            [("entity_type", 1)],
            [("as_of", -1)],
        ]
