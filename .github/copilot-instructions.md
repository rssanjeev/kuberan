# GitHub Copilot Instructions for Kuberan

## Quick Navigation

📚 **Comprehensive Documentation:**
- [Tech Stack & Dependencies](docs/TECH_STACK.md) - Technologies, versions, libraries
- [Architecture & Design Patterns](docs/ARCHITECTURE.md) - System design, layers, patterns
- [Coding Style Guide](docs/STYLE_GUIDE.md) - Naming, formatting, conventions
- [Domain Overviews](docs/DOMAINS.md) - Stock Tracker & Financier domains
- [Security Policies](docs/SECURITY.md) - **CRITICAL** for financial data handling
- [Logging Standards](docs/LOGGING.md) - Structured logging, best practices
- [Development Workflows](docs/WORKFLOWS.md) - Commands, testing, deployment
- [Web Scraping Guide](docs/WEB_SCRAPING.md) - MCP servers, data extraction, best practices

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

### 2. Structured Logging

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

### 3. Clean Architecture

**Follow [ARCHITECTURE.md](docs/ARCHITECTURE.md) for system design.**

- **Routers**: Thin API layer, delegate to services
- **Services**: Business logic, orchestration
- **Repositories**: Data access only, no business logic
- **Core**: Shared utilities and helpers

### 4. Coding Standards

**Follow [STYLE_GUIDE.md](docs/STYLE_GUIDE.md) for consistent code.**

- Type hints required for all functions
- snake_case for files/functions, PascalCase for classes
- Docstrings required for all classes and functions
- Always use `python3` command (never `python`)

## Common Workflows

### Adding New Endpoints
1. Add route to router file
2. Update `docs/API.md` with endpoint documentation
3. **Update Postman collection** (REQUIRED):
   - `docs/Kuberan_API_Collection.json` (single file for all endpoints)
4. Test endpoint thoroughly with curl or Postman
5. Verify collection imports correctly in Postman
6. Commit all changes together (code + docs + collection)

**Critical**: Never commit endpoint changes without updating the Postman collection!

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

## Project Philosophy

- **Security First**: Financial data protection is non-negotiable
- **Scalability**: Design for future features and growth
- **Clean Architecture**: Clear separation of concerns
- **Documentation as Code**: Keep docs in sync with code
- **Thoughtful Design**: Consider impact before implementing
- **MCP-First Approach**: Use MCP servers for all external data fetching

## Notes for Copilot

- This project prioritizes **scalability** and **clean architecture**
- Always ask "how does this affect future features?" before implementing
- Documentation is not optional - it's part of the implementation
- When in doubt, use functional programming first, add OOP when state/lifecycle needed
- The user values thoughtful architecture over quick hacks
- **Always use MCP servers** for web scraping and data extraction (never custom libraries)

---

**Last Updated:** November 30, 2025

**For comprehensive details, see the documentation files linked above.**
