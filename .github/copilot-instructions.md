# GitHub Copilot Instructions for Kuberan

## Quick Navigation

📚 **Comprehensive Documentation:**
- [**DOCUMENTATION STRUCTURE**](../docs/DOCUMENTATION_STRUCTURE.md) - **START HERE** for finding any documentation
- [**Project Overview**](../docs/KUBERAN_OVERVIEW.md) - Vision, goals, users, development philosophy
- [**Data Pipeline Architecture**](../docs/DATA_PIPELINE_ARCHITECTURE.md) - Complete pipeline (4 stages)
- [Tech Stack & Dependencies](docs/TECH_STACK.md) - Technologies, versions, libraries
- [Architecture & Design Patterns](docs/ARCHITECTURE.md) - System design, layers, patterns
- [Coding Style Guide](docs/STYLE_GUIDE.md) - Naming, formatting, conventions
- [Domain Overviews](docs/DOMAINS.md) - Stock Tracker, Financier, ETF domains
- [Security Policies](docs/SECURITY.md) - **CRITICAL** for financial data handling
- [Logging Standards](docs/LOGGING.md) - Structured logging, best practices
- [Development Workflows](docs/WORKFLOWS.md) - Commands, testing, deployment
- [Web Scraping Guide](docs/WEB_SCRAPING.md) - MCP servers, data extraction, best practices

📁 **Documentation by Domain:**
- [Data Ingestion](../docs/Ingest/) - Provider-specific specs (YFinance, MASSIVE, Finviz, StockAnalysis)
- [Data Standardization](../docs/Standardization/) - Rules, priority matrix, schemas
- [API Layer](../docs/API/) - Endpoint specifications and contracts
- [Frontend](../docs/Frontend/) - UI patterns and implementation plans
- [Trader Knowledge](../docs/Knowledge/) - Trading concepts and terminology
- [Background Jobs](../docs/Jobs/) - Job specifications and scheduling
- [Planning](../docs/planning/) - ⏳ Current work items and decisions

## Project Overview

**Kuberan** is a financial management system with two primary domains:

### Stock Tracker
- Real-time stock price monitoring during NYSE market hours
- Historical price storage and analysis
- Ticker configuration and watchlists
- Background jobs for automated data collection

### Financier  
- Credit card statement PDF processing
- Transaction categorization and analytics
- Spending analysis and visualizations
- **Security First**: No account info stored, PDFs never saved

## Core Technologies

- **Backend**: FastAPI (Python 3.14) + MongoDB (Beanie ODM)
- **Deployment**: Docker Compose
- **Frontend**: React (future)
- **Architecture**: Hybrid functional/OOP, layered design

## Critical Principles

### 1. Security First (Financial Data)

**ALWAYS follow [SECURITY.md](docs/SECURITY.md) when handling financial data.**

Key rules:
- ❌ **NEVER** store PDF files, account numbers, or personal info
- ✅ **ONLY** store transaction data (merchant, amount, category)
- ✅ Process PDFs in-memory only, delete immediately
- ✅ Use SHA256 hashes for file deduplication

### 2. File Size Limit (300 Lines Maximum)

**CRITICAL RULE**: All new files MUST be kept within 300 lines of code.

**Why 300 Lines?**
- ✅ Easier to scan and understand entire file
- ✅ Efficient AI/Copilot context loading
- ✅ Reduces complexity and coupling
- ✅ Prevents accidental breaking changes during updates
- ✅ Clear file purpose and responsibility

**Implementation Rules**:
- ❌ **NEVER** create files exceeding 300 lines
- ✅ Break large files into logical modules (e.g., split services into multiple files)
- ✅ Use meaningful file names that indicate specific purpose
- ✅ Extract shared utilities into separate helper files
- ✅ When updating existing files: if additions push beyond 300 lines, refactor first

**Examples**:
```python
# ❌ BAD: financier_service.py (800 lines)
# One giant file with all financier logic

# ✅ GOOD: Split into focused files
# financier/document_processor_service.py (250 lines)
# financier/transaction_service.py (180 lines)
# financier/merchant_service.py (220 lines)
```

**Existing Code Audit**:
- Files exceeding 300 lines will be audited and refactored in future
- When modifying existing large files: if update pushes beyond 300 lines, extract logic to new file
- Gradual migration approach - no rush, but enforce for all new code

**Counting Lines**:
- Exclude: blank lines, comments, docstrings, imports
- Include: actual code logic (functions, classes, statements)
- Use `cloc` or similar tools for accurate counts

### 3. Structured Logging

**ALWAYS follow [LOGGING.md](docs/LOGGING.md) for consistent logging.**

```python
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# Use structured context
logger.info(
    "Saved price for ticker",
    extra={"ticker": ticker, "price": price}
)

# Include tracebacks for errors
logger.error("Operation failed", extra={"error": str(e)}, exc_info=True)
```

### 4. Clean Architecture

**Follow [ARCHITECTURE.md](docs/ARCHITECTURE.md) for system design.**

- **Routers**: Thin API layer, delegate to services
- **Services**: Business logic, orchestration
- **Repositories**: Data access only, no business logic
- **Core**: Shared utilities and helpers

### 5. Coding Standards

**Follow [STYLE_GUIDE.md](docs/STYLE_GUIDE.md) for consistent code.**

- **Maximum 300 lines per file** (exclude blanks/comments/imports)
- Type hints required for all functions
- snake_case for files/functions, PascalCase for classes
- Docstrings required for all classes and functions
- Always use `python3` command (never `python`)
- **CRITICAL**: Never calculate or derive new financial values (no weighted averages, no consensus calculations). Only select existing values from providers based on priority rules.

## Common Workflows

### Endpoint Design Philosophy (Nov 30, 2025)

**CRITICAL RULE: Always challenge endpoint creation. Default to refining services.**

When asked to add functionality:
1. **FIRST**: Check if existing endpoints can handle it (query params, request body options)
2. **SECOND**: Implement in services layer and expose through existing endpoints
3. **LAST RESORT**: Create new endpoint only if absolutely necessary

**Core Principles**:

**1. Endpoints Are Query-Focused, Not Management-Focused**
- ✅ GOOD: `GET /stocks/price/{ticker}` - Queries data
- ❌ BAD: `POST /stocks/tickers/add` - Manages configuration
- **Rule**: Management operations belong in `/system/*` namespace

**2. One Domain = One Clear Purpose**
- **Stock endpoints** (`/stocks/*`): Price queries and market info ONLY
  - `GET /stocks/{ticker}` - Current stock information
  - `GET /stocks/history/{ticker}` - Historical data
  - `GET /stocks/price/{ticker}` - Lightweight price query
  - `GET /stocks/market/status` - Market hours check
  - `GET /stocks/config/routing` - Provider routing config
  
- **Metadata management** (`/system/metadata/*`): Ticker discovery and enrichment
  - Managing 12,140 tickers in database
  - Enrichment pipeline (base → foundation → enriched)
  - Discovery, stats, failed tickers
  
- **System operations** (`/system/*`): Provider status, jobs, health checks

**3. Share Data Through Services, Not Duplicate Endpoints**
- ETF domain needs stock data? → Import stock service
- Metadata needs stock prices? → Import stock service
- ❌ Don't create: `/etf/stocks/{ticker}` or `/metadata/stocks/{ticker}`
- ✅ Do this: Call stock_service methods from your domain service

**4. Examples of Removed Redundancy** (Nov 30, 2025):
- ❌ `/stocks/price/stats` - Used outdated collection (wrong data source)
- ❌ `/stocks/price/collected/{ticker}` - Duplicate of history endpoint
- ❌ `/stocks/configured` - Redundant with metadata system
- ❌ `/stocks/custom` - Unnecessary frontend override (use request body)
- ❌ `/stocks/poll/trigger` - Job management via scheduler, not REST
- ❌ `/stocks/tickers/*` (6 endpoints) - All ticker CRUD (use `/system/metadata/*`)

**Pre-Flight Checklist Before Adding Endpoint**:
1. ❓ Can existing endpoint handle this with query/path parameters?
2. ❓ Can existing endpoint accept different request body structure?
3. ❓ Should this be a service method called by existing endpoint?
4. ❓ Does this duplicate functionality in another router?
5. ❓ Is this management (use `/system/*`) or query (domain-specific)?
6. ❓ Will this endpoint still be relevant in 6 months or is it a one-off?

**If you answer YES to any above, DON'T create the endpoint.**

### Adding New Endpoints
1. Add route to router file
2. Update `docs/API.md` with endpoint documentation
3. **Update Postman collection** (REQUIRED):
   - `docs/Kuberan_API_Collection.json` (single file for all endpoints)
4. Test endpoint thoroughly with curl or Postman
5. Verify collection imports correctly in Postman
6. Commit all changes together (code + docs + collection)

**Critical**: Never commit endpoint changes without updating the Postman collection!

### Adding New Tabs or Dashboards (Frontend)

When adding a new tabbed screen (like Stocks, Financier):

1. **Create the main screen** with TabController
2. **Add ExpansionTile dropdown** to navigation drawer (all locations):
   - home_screen.dart drawer
   - The new screen's own drawer (with `initiallyExpanded: true`)
   - All other screen drawers (financier_screen.dart, stocks_tabs_screen.dart, etc.)
3. **Dropdown pattern to follow**:
   ```dart
   ExpansionTile(
     leading: Icon(Icons.your_icon),
     title: Text('Your Screen'),
     initiallyExpanded: currentScreen, // true on this screen, false on others
     children: [
       ListTile(
         leading: Icon(Icons.tab_icon),
         title: Text('  Tab Name'),
         selected: _tabController.index == 0, // if on this screen
         onTap: () {
           Navigator.pop(context);
           if (currentScreen) {
             _tabController.animateTo(0); // Switch tab
           } else {
             context.go('/route?tab=0'); // Navigate with tab param
           }
         },
       ),
     ],
   ),
   ```
4. **Add tab navigation support** in initState:
   ```dart
   WidgetsBinding.instance.addPostFrameCallback((_) {
     final uri = Uri.base;
     final tabParam = uri.queryParameters['tab'];
     if (tabParam != null) {
       final tabIndex = int.tryParse(tabParam);
       if (tabIndex != null && tabIndex >= 0 && tabIndex < tabCount) {
         _tabController.animateTo(tabIndex);
       }
     }
   });
   ```
4. **Update submenu items** with appropriate icons and tab indices
5. **Test navigation** from all screens to all tabs

**Pattern to follow:**
```dart
ExpansionTile(
  leading: Icon(Icons.your_icon),
  title: Text('Your Screen'),
  initiallyExpanded: currentScreen, // true on this screen, false on others
  children: [
    ListTile(
      leading: Icon(Icons.tab_icon),
      title: Text('  Tab Name'),
      selected: _tabController.index == 0, // if on this screen
      onTap: () {
        Navigator.pop(context);
        if (currentScreen) {
          _tabController.animateTo(0); // Switch tab
        } else {
          context.go('/route?tab=0'); // Navigate with tab param
        }
      },
    ),
  ],
),
```

### Making Code Changes
```bash
# After changes
docker-compose restart backend

# Check logs
docker logs kuberan-backend-1 --tail 50

# Test endpoint
curl http://localhost:8000/endpoint
```

### Adding Background Jobs
1. Create job in `backend/app/services/jobs/`
2. Use hybrid functional/OOP pattern
3. Register in `backend/app/services/scheduler/registry.py`
4. Test execution

## Domain-Specific Guidance

### Stock Tracker
- **Timezone**: Always use US/Eastern (EST/EDT) for timestamps
- **Market Hours**: 9:00 AM - 5:00 PM EST, Monday-Friday
- **Services**: Located in `backend/app/services/stock/`
- **Metadata Enrichment**: MASSIVE provider (Polygon.io) collects foundation metadata
  - **Rate Limits**: 5 calls/min, 300/hour, 7,200/day
  - **Enrichment Status**: base → foundation → enriched → failed
  - **Progress**: 1,418/12,140 tickers processed (11.7%)
  - **404 Handling**: Gracefully mark as "failed" to prevent retries
  - **Monitoring**: `/system/metadata/stats`, `/system/metadata/failed`
- See [DOMAINS.md](docs/DOMAINS.md#stock-tracker-domain) for details

### Financier
- **Security**: Review [SECURITY.md](docs/SECURITY.md) for every feature
- **Services**: Three specialized services in `backend/app/services/financier/`
  - `document_processor_service.py` - PDF processing
  - `transaction_service.py` - Read-only queries
  - `merchant_service.py` - Merchant/category management
- See [DOMAINS.md](docs/DOMAINS.md#financier-domain) for details

### ETF Analysis
- **67 Endpoints**: Comprehensive ETF research and portfolio management
- **Services**: 16 specialized services in `backend/app/services/etf/`
- **Data Provider**: Alpha Vantage with 30-day caching
- **Features**: Profile, comparison, screening, portfolio, risk, tax, backtesting
- See [DOMAINS.md](docs/DOMAINS.md#etf-analysis-domain) for details

### Financial Statements Extraction (S&P 500)

**CRITICAL**: MASSIVE Financials API deprecated on **February 23, 2026** (73 days remaining).

**Overview:**
- **Target**: S&P 500 top 500 companies by market cap
- **Current Progress**: 5/500 tickers (1.0% complete)
- **Extracted**: 976 statements across 5 tickers (AAPL, GOOG, GOOGL, MSFT, NVDA)
- **Coverage**: 2013 to 2025 (12+ years of historical data)

**Four Statement Types Extracted:**

1. **income** - Income Statement (P&L)
   - Revenue, operating income, net income, EPS
   - Use: Profitability analysis, earnings quality

2. **balance_sheet** - Balance Sheet
   - Assets, liabilities, shareholders equity
   - Use: Financial position, liquidity ratios

3. **cash_flow** - Cash Flow Statement
   - Operating, investing, financing activities
   - Use: Cash generation, free cash flow analysis

4. **comprehensive_income** - Comprehensive Income Statement
   - Other comprehensive income/loss, currency translation
   - Use: Hidden gains/losses, full income picture

**Three Timeframes Collected:**
- **annual**: Full fiscal year (FY) statements
- **quarterly**: Q1, Q2, Q3, Q4 statements
- **ttm**: Trailing Twelve Months (most current annual view)

**Scheduled Extraction Job:**
- **Location**: `backend/app/services/jobs/financials_extraction_job.py`
- **Schedule**: Every 3 minutes via CronTrigger (optimal for 2-minute execution time)
- **Batch Size**: 10 tickers per run
- **Rate Limiting**: 12-second delays (5 calls/min MASSIVE limit)
- **Timeline**: ~2.5 hours for all 500 tickers (was 25 hours with 30-min schedule)
- **Self-Terminating**: Stops automatically when 500 tickers complete
- **Resume Capability**: Skips already processed tickers

**Key Features:**
- ✅ Single API call per ticker (50 statements limit)
- ✅ All timeframes in one request (annual + quarterly + TTM)
- ✅ ~200 statements per ticker (vs 12 before optimization)
- ✅ JSON backups saved to `backend/extracted_financials/{ticker}.json`
- ✅ Graceful error handling with retry logic
- ✅ Progress logging every 50 tickers

**API Endpoints:**

```bash
# Extraction statistics
GET /stocks/financials/stats

# All statements for ticker
GET /stocks/financials/{ticker}?limit=20

# Filter by statement type
GET /stocks/financials/{ticker}?statement_type=income
GET /stocks/financials/{ticker}?statement_type=balance_sheet
GET /stocks/financials/{ticker}?statement_type=cash_flow
GET /stocks/financials/{ticker}?statement_type=comprehensive_income

# Filter by timeframe
GET /stocks/financials/{ticker}?timeframe=annual
GET /stocks/financials/{ticker}?timeframe=quarterly
GET /stocks/financials/{ticker}?timeframe=ttm

# Filter by year
GET /stocks/financials/{ticker}?fiscal_year=2024
```

**Monitoring Job Progress:**

```bash
# Check job logs
docker logs kuberan-backend-1 | grep "Financials extraction"

# Check MongoDB collection
docker exec -it kuberan-mongodb mongosh kuberan --eval "
  db.financial_statements.countDocuments()
"

# Check stats endpoint
curl http://localhost:8000/stocks/financials/stats | python3 -m json.tool
```

**Database Schema:**
- **Collection**: `financial_statements`
- **Indexes**: `(ticker, fiscal_year, statement_type)`, `(ticker, timeframe)`
- **Fields**: ticker, statement_type, fiscal_year, fiscal_period, timeframe, data, key metrics

**Use Cases:**
- DCF modeling (using all 4 statements together)
- Earnings quality analysis (income vs cash flow comparison)
- Balance sheet health checks (liquidity/solvency ratios)
- Comprehensive income analysis (detecting hidden gains/losses)

**Complete Documentation:**
- See [FINANCIALS_EXTRACTION_COMPLETE_GUIDE.md](../docs/FINANCIALS_EXTRACTION_COMPLETE_GUIDE.md) for comprehensive details
- Postman collection: 10 endpoints fully documented in `docs/FINANCIALS_POSTMAN_UPDATE.json`

## When Working on This Project

### Before Implementing Features

1. **Read relevant documentation** - Check domain-specific docs
2. **Security check** - If handling financial data, review [SECURITY.md](docs/SECURITY.md)
3. **Follow patterns** - Maintain consistency with existing code
4. **Consider scalability** - How does this affect future features?

### During Implementation

1. **Use type hints** - Required for all functions
2. **Add structured logging** - Follow [LOGGING.md](docs/LOGGING.md)
3. **Keep layers separated** - Routers → Services → Repositories
4. **Handle errors gracefully** - Use appropriate HTTP status codes

### After Implementation

1. **Update documentation** - API.md, Postman collections
2. **Test thoroughly** - Manual and automated tests
3. **Review security** - No sensitive data exposed
4. **Verify logs** - Structured context, appropriate levels

## Common Patterns

### Error Handling Best Practices

**404 Handling** (Metadata Collection):
```python
# Check status code before raise_for_status()
if response.status_code == 404:
    logger.warning("Resource not found", extra={"ticker": ticker})
    return None  # Graceful handling

response.raise_for_status()  # Raise for other errors
```

**Failed Ticker Marking**:
```python
# Mark ticker as failed to prevent endless retries
await metadata_service._mark_ticker_as_failed(
    ticker=ticker,
    error_message="404 Not Found"
)
# Creates/updates CompanyOverview with enrichment_status="failed"
```

**Rate Limit Handling**:
```python
try:
    data = await provider.fetch_data(ticker)
except ProviderException as e:
    if "rate limit" in str(e).lower():
        logger.warning("Rate limit hit", extra={"ticker": ticker})
        await asyncio.sleep(60)  # Back off
    else:
        raise
```

### ✅ DO
- Use centralized job scheduler
- Keep routers thin, delegate to services
- Use pure functions for testable logic
- Add structured context to logs
- Follow Single Responsibility Principle
- Update documentation with code

### ❌ DON'T
- Store PDF files anywhere
- Store account numbers or personal info
- Put business logic in routers
- Use `print()` instead of logger
- Forget to update documentation
- Hardcode configuration values

## Quick Reference Commands

```bash
# Restart backend
docker-compose restart backend

# View logs
docker logs kuberan-backend-1 --tail 50 -f

# Test endpoint
curl http://localhost:8000/stocks/price/stats | python3 -m json.tool

# Access MongoDB
docker exec -it kuberan-mongodb mongosh kuberan

# Rebuild (if dependencies changed)
docker-compose build backend
```

See [WORKFLOWS.md](docs/WORKFLOWS.md) for comprehensive command reference.

## Documentation Structure

This project uses **modular documentation** for better Copilot efficiency:

- **Focused context**: Load only relevant docs for the task
- **Explicit references**: "Follow SECURITY.md" is clearer than "follow security section"
- **Better caching**: Smaller files cache better
- **Easier maintenance**: Update specific docs without affecting others

### When to Reference Docs

**Copilot automatically discovers and applies all documentation** in `.github/docs/`.

You only need to explicitly mention files when:
- Dealing with security/sensitive data: "Follow SECURITY.md"
- Resolving ambiguity: "Use patterns from ARCHITECTURE.md"
- Emphasizing critical requirements: "Logging per LOGGING.md"
- Learning/asking questions: "What does STYLE_GUIDE.md say about naming?"

**80% of requests** don't need file mentions - Copilot handles it automatically!

## MASSIVE API Integration

**Primary metadata provider** for Kuberan's Stock Tracker domain.

See [MASSIVE_REFERENCE_ENDPOINTS_GUIDE.md](../docs/MASSIVE_REFERENCE_ENDPOINTS_GUIDE.md) for complete documentation on all 11 free tier reference endpoints.

### Free Tier Access (Current)

**Available Endpoints** (11 total):
- ✅ All Tickers - Comprehensive ticker list with filtering
- ✅ Ticker Overview - Detailed company profiles (primary use for metadata enrichment)
- ✅ Ticker Types - Security type classifications
- ✅ Exchanges - Exchange directory with MIC codes
- ✅ Condition Codes - Trade/quote condition mappings
- ✅ Stock Splits - Historical split events
- ✅ Dividends - Dividend history with dates and amounts
- ✅ Financials (Deprecated) - SEC filings data (use with caution)
- ✅ News - Financial news with sentiment analysis
- ✅ All Option Contracts - Options contract listings
- ✅ Option Contract Overview - Specific contract details

**Rate Limits**: 5 calls/min, 300/hour, 7,200/day

**Authentication**: API key required (passed as query param or header)

### Migration from Polygon.io

**Current Status**: Migrating metadata enrichment from Polygon.io to MASSIVE
- Use **Ticker Overview** endpoint (`GET /v3/reference/tickers/{ticker}`) for foundation metadata
- Collects: CIK, FIGI, SIC codes, branding (logos/icons), company description, financials
- Background job: Enrich 5 tickers per minute (respects rate limits)
- Progress: Ongoing replacement of Polygon.io integration

**Key Differences**:
- MASSIVE: Free tier includes reference data (no pricing)
- Polygon.io: Free tier extremely limited (migrating away)
- Both have same rate limits (5/min, 300/hr, 7,200/day)

### When to Use MASSIVE API

**✅ Always use for**:
- Ticker metadata enrichment (CIK, FIGI, SIC, branding)
- Corporate actions tracking (splits, dividends)
- Company fundamentals (description, employees, market cap)
- Financial news with sentiment analysis
- Exchange and ticker type reference data

**❌ Not available on free tier**:
- Real-time or historical prices (use YFinance instead)
- Technical indicators (SMA, EMA, RSI, etc.)
- Market status and hours
- WebSocket streaming

**🔮 Future (paid tier upgrade)**:
- Access to 130+ additional endpoints
- Real-time pricing, trades, quotes
- Technical indicators
- Options pricing and Greeks

### Implementation Patterns

**Refer to MASSIVE_REFERENCE_ENDPOINTS_GUIDE.md** for:
- Complete endpoint documentation with parameters and responses
- Sample requests and responses
- Kuberan integration recommendations
- Rate limiting strategies
- Error handling patterns
- Caching guidelines

**Quick Example**:
```python
# Fetch ticker overview for metadata enrichment
async def fetch_ticker_metadata(ticker: str) -> Dict:
    url = f"{base_url}/v3/reference/tickers/{ticker}"
    response = await client.get(url, headers={"Authorization": f"Bearer {api_key}"})
    return response.json()["results"]
```

## Web Scraping & Data Extraction

**ALWAYS use MCP servers for web scraping and data extraction.** Never implement custom web scraping libraries.

See [WEB_SCRAPING.md](docs/WEB_SCRAPING.md) for comprehensive guidelines on:
- Available MCP servers (mcp_fetch, mcp_brave_search, mcp_puppeteer)
- 4-step strategy for consolidating website features
- Implementation patterns (API calls, HTML parsing, browser automation)
- Rules and best practices
- Error handling and performance optimization
- Examples and testing strategies

**Quick Rules**:
- ✅ Use `mcp_fetch` for HTML/content inspection
- ✅ Use `mcp_brave_search` for search-based extraction (current: precious metals)
- ✅ Use `mcp_puppeteer` for JavaScript-heavy sites
- ❌ Never install custom scraping libraries (requests, beautifulsoup, scrapy, selenium)
- ❌ Don't bypass rate limits or store scraped HTML

## Frontend Development (Flutter)

**Framework:** Flutter (Web, iOS, Android)  
**Design Reference:** Budget App (https://github.com/theReynald/Budget-App)  
**Implementation Plan:** [docs/FRONTEND_IMPLEMENTATION_PLAN.md](../docs/FRONTEND_IMPLEMENTATION_PLAN.md)

### Key Principles

**Beginner-Friendly Approach:**
- Explain every step in simple terms before implementing
- Show what user will see in their browser after each change
- Wait for approval at checkpoints before continuing
- Provide exact commands to test and verify functionality
- Never assume user knows Flutter/Dart terminology

**Design Philosophy:**
- Copy proven patterns from Budget App (card-based layout)
- Translate React patterns to Flutter equivalently
- Use Material Design components (familiar, well-documented)
- Responsive design (desktop → tablet → mobile)
- Clean visual hierarchy (stats cards, tables, forms)

**Development Workflow:**
1. **Phase-based implementation** (6 phases, each with clear goal)
2. **Hot reload testing** (save file → see changes instantly)
3. **Browser-first development** (test in Chrome before mobile)
4. **Checkpoint approvals** (user verifies before continuing)
5. **Troubleshooting support** (provide exact fix commands)

### When Working on Frontend

**Before implementing any feature:**
1. Explain in simple terms what will be built
2. Show mockup/layout of what user will see
3. List exact files that will be created/modified
4. Provide test commands user will run
5. Wait for explicit approval

**After implementing:**
1. Provide exact test commands
2. Describe what user should see in browser
3. List common issues and fixes
4. Wait for checkpoint approval before next phase
5. Never batch multiple phases - one at a time only

**Communication Style:**
- Use analogies to React/TypeScript (user's familiar territory)
- Avoid Flutter jargon unless explained first
- Provide screenshots or ASCII diagrams for layouts
- Give exact commands (copy-pasteable)
- Explain why each step is needed

### Frontend File Structure

See [FRONTEND_IMPLEMENTATION_PLAN.md](../docs/FRONTEND_IMPLEMENTATION_PLAN.md#project-structure) for complete directory tree and file purposes.

**Key Directories:**
- `lib/screens/` - Full page views (like React pages)
- `lib/widgets/` - Reusable components (like React components)
- `lib/services/` - Backend API calls (like fetch/axios)
- `lib/models/` - Data structures (like TypeScript interfaces)

## Project Philosophy

- **Security First**: Financial data protection is non-negotiable
- **Scalability**: Design for future features and growth
- **Clean Architecture**: Clear separation of concerns
- **Documentation as Code**: Keep docs in sync with code
- **Thoughtful Design**: Consider impact before implementing
- **MCP-First Approach**: Use MCP servers for all external data fetching
- **Beginner-Friendly**: Explain everything in simple terms, wait for approvals
- **No Synthetic Data**: NEVER calculate or manipulate financial values - only select from existing provider data. Decisions must be based on real data that actually exists, not computed averages or derived values.

## Notes for Copilot

- This project prioritizes **scalability** and **clean architecture**
- Always ask "how does this affect future features?" before implementing
- Documentation is not optional - it's part of the implementation
- When in doubt, use functional programming first, add OOP when state/lifecycle needed
- The user values thoughtful architecture over quick hacks
- **Always use MCP servers** for web scraping and data extraction (never custom libraries)
- **Frontend development**: Follow [FRONTEND_IMPLEMENTATION_PLAN.md](../docs/FRONTEND_IMPLEMENTATION_PLAN.md) phase-by-phase
- **User is new to Flutter**: Explain everything in beginner-friendly terms, provide exact commands

## Documentation Standards

### Organization

**CRITICAL**: Follow [DOCUMENTATION_STRUCTURE.md](../docs/DOCUMENTATION_STRUCTURE.md) for ALL documentation work.

**Key Principles:**
1. **Single Source of Truth**: Each concept has ONE authoritative document
2. **Domain-Based Organization**: Use subdirectories (Ingest/, Standardization/, API/, Frontend/, Knowledge/, Jobs/)
3. **Maximum 300 Lines**: Split documents exceeding 300 lines
4. **Status Indicators**: Always add status (🟢 Active, 🟡 Draft, 🔴 Deprecated, ⏳ Temporary, ⭐ Core)
5. **Living Documentation**: Update docs alongside code changes

### Finding Documentation

**Quick Reference:**
- **Overall vision?** → `docs/KUBERAN_OVERVIEW.md`
- **How to organize docs?** → `docs/DOCUMENTATION_STRUCTURE.md`
- **Data pipeline?** → `docs/DATA_PIPELINE_ARCHITECTURE.md`
- **Ingestion from provider?** → `docs/Ingest/{PROVIDER}_INGEST_SPEC.md`
- **Standardization rules?** → `docs/Standardization/DATA_STANDARDIZATION_RULES.md`
- **API endpoints?** → `docs/API/{DOMAIN}_ENDPOINTS.md`
- **Current work?** → `docs/planning/PLANNING_CHECKLIST.md`

### Creating Documentation

**File Naming:**
- Overview: `{DOMAIN}_OVERVIEW.md`
- Strategy: `{FEATURE}_STRATEGY.md`
- Specification: `{PROVIDER}_INGEST_SPEC.md`
- Endpoints: `{DOMAIN}_ENDPOINTS.md`
- Planning: `{PURPOSE}_PLAN.md` or `{PURPOSE}_CHECKLIST.md`

**Document Header Template:**
```markdown
# {Document Title}

**Last Updated:** {Date}  
**Status:** {🟢 Active | 🟡 Draft | 🔴 Deprecated | ⏳ Temporary}  
**Purpose:** {One-line description}  
**Related Docs:** {Links to related documentation}

---
```

**When Creating/Updating Docs:**
1. Check `docs/DOCUMENTATION_STRUCTURE.md` for correct location
2. Use standard header template
3. Keep under 300 lines (split if needed)
4. Add to `docs/README.md` if new document
5. Update related docs with cross-references
6. Update copilot instructions if structure changes

**Planning Documents:**
- Create in `docs/planning/` subdirectory
- Mark as ⏳ Temporary status
- Move to archive when work completes

**Architectural Decisions:**
- Create as `docs/planning/decisions/ADR-{YYYYMMDD}-{title}.md`
- Use ADR template from DOCUMENTATION_STRUCTURE.md
- **User is new to Flutter**: Explain everything in beginner-friendly terms, provide exact commands

---

**Last Updated:** December 10, 2025

**For comprehensive details, see the documentation files linked above.**
