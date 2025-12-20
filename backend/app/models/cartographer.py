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


class RegionDefinition(BaseModel):
    """A logical region on the page (e.g., 'snapshot_table')."""
    region_id: str = Field(..., description="Unique region identifier")
    description: str = Field(..., description="Human-readable description")
    container_selector: str = Field(..., description="CSS selector for container")
    parsing_rules: List[ParsingRule] = Field(
        default_factory=list,
        description="Rules for fields in this region"
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

class FinvizSnapshot(Document):
    """FinViz scraped data stored in MongoDB."""
    
    provider: str = Field(default="finviz")
    ticker: str = Field(..., description="Stock/ETF ticker")
    entity_type: str = Field(..., description="stock or etf")
    as_of: datetime = Field(default_factory=datetime.now)
    
    # Header & Classification
    display_name: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    exchange: Optional[str] = None
    
    # Snapshot Table Fields (store as Dict for flexibility)
    fields: Dict[str, Union[str, int, float, bool, None]] = Field(
        default_factory=dict,
        description="All extracted fields from snapshot table"
    )
    
    # Related Entities
    peers: List[str] = Field(default_factory=list)
    held_by_etfs: List[str] = Field(default_factory=list)
    
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
            [("entity_type", 1)],
            [("sector", 1)],
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
