# GitHub Copilot Instructions for Kuberan Project

## Project Context

Kuberan is a financial management system with multiple services:
- **Stock Tracker**: Real-time stock price monitoring and notifications
- **Financier**: Credit card statement processing and transaction analytics
- **Backend**: FastAPI (Python 3.14) with MongoDB
- **Frontend**: React (future implementation)
- **Architecture**: Hybrid functional/OOP approach
- **Deployment**: Docker Compose

### Service Overview

#### Stock Tracker Service
- Real-time price collection during market hours
- Historical price storage and analysis
- Ticker configuration and watchlists

#### Financier Service
- **Document Processing**: PDF credit card statement parsing
- **Transaction Management**: Category-based transaction organization
- **Analytics Engine**: Deep financial analysis with insights
- **Visualizations**: Chart generation for frontend consumption (NOT for export/download)

**Important**: Visualization endpoints (`/financier/analytics/visualizations`) generate base64-encoded images intended for React frontend display. Do NOT implement file download or export features unless explicitly requested.

## Python Environment Requirements

**CRITICAL**: Always use Python 3.14 for this project.

- **Docker**: Uses Python 3.14 in containers
- **Local Development**: Use `backend/venv` (Python 3.14)
- **Command Syntax**: Always use `python3` (never `python`)
- **Virtual Environment**: `backend/venv/bin/python3`

**Examples:**
```bash
# ✅ Correct
python3 script.py
python3 -m pip install package
./venv/bin/python3 script.py

# ❌ Wrong
python script.py
python -m pip install package
```

---

## Core Development Principles

### 1. Security & Privacy (Financial Documents)

**CRITICAL SECURITY REQUIREMENTS:**

#### PDF Processing Rules
- **NEVER store PDF files** in the repository or database
- **NEVER commit PDFs** to git (enforced via .gitignore)
- Process PDFs in-memory only, extract data, then discard file
- Use SHA256 file hash for deduplication (NOT filename)

#### Account Information Protection
- **NEVER store account numbers** (full or partial)
- **NEVER store account holder names** or addresses
- **NEVER expose SSNs, card numbers, or PINs**
- Account info parsing is for **validation only**, NOT storage
- Focus exclusively on transaction-level data

#### Transaction Data Handling
- Store ONLY: date, merchant, amount, category, location
- **Obscure all personally identifiable information**
- Transaction data is discrete - no linking to specific accounts
- Use generic fields: statement_year, statement_month (not account-specific dates)

#### Database Storage Policy
- `CreditCardTransaction`: merchant, amount, category only
- `FinancialDocumentMetadata`: SHA256 hash, counts, aggregates only
- `MerchantCategory`: merchant-to-category mappings only
- NO `AccountInfo` or `UserAccount` models allowed

#### File Handling
- PDFs processed via upload endpoint → extract → save to DB → delete file
- No temporary file storage (use in-memory processing)
- All PDFs excluded in .gitignore
- Extracted JSON files (for testing) excluded in .gitignore

### 2. Architectural Guidelines

#### Separation of Concerns
- **Services** (`backend/app/services/`): Business logic and external API integrations
- **Jobs** (`backend/app/services/jobs/`): Scheduled background tasks
- **Repositories** (`backend/app/repositories/`): Database access layer
- **Core** (`backend/app/core/`): Shared utilities and helpers
- **Routers** (`backend/app/routers/`): API endpoint definitions

#### Scalability First
- Design for future features (data analyzer, portfolio updater, notifiers, etc.)
- Use centralized patterns (e.g., job scheduler) instead of per-service instances
- Keep components loosely coupled and independently testable
- Consider how changes affect future extensibility

### 2. Programming Paradigm: Hybrid Functional/OOP

**Use Functional Programming for:**
- Core business logic and data transformations
- Stateless operations
- Easily testable functions
- Reusable utilities

**Use Object-Oriented Programming for:**
- State management (job statistics, run counts, etc.)
- Lifecycle management (start/stop, setup/teardown)
- Encapsulation of related functionality
- When inheritance or polymorphism provides clear benefits

**Example Pattern:**
```python
# Pure functions for business logic
async def fetch_and_save_price(ticker: str) -> bool:
    """Testable, stateless core logic"""
    pass

# OOP wrapper for state and lifecycle
class PriceCollectorJob:
    """Manages state, statistics, and job lifecycle"""
    async def run(self):
        # Calls pure functions
        await fetch_and_save_price(ticker)
```

### 3. Code Organization Rules

#### Import Management
- All imports at the top of file (no local imports unless avoiding circular dependencies)
- Group imports: stdlib → third-party → local
- Use absolute imports (`from app.services.x import y`)

#### Naming Conventions
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions/variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Singletons: `lowercase_singleton` (e.g., `stock_repository`, `job_scheduler`)

#### Type Hints
- Always use type hints for function parameters and return types
- Use `Optional[T]` for nullable values
- Use `List[T]`, `Dict[K, V]` for collections

---

## Documentation Requirements

### API Documentation (`docs/API.md`)
**CRITICAL**: When modifying any endpoint in `backend/app/routers/*.py`:

1. Update the corresponding section in `docs/API.md`
2. Include:
   - Endpoint path and HTTP method
   - Request parameters (path, query, body)
   - Response format with example JSON
   - Error codes and messages
   - Any notes about behavior
3. Update the "Last Updated" date at the top
4. Commit router changes and documentation together

### Postman Collections (`docs/*.json`)
**CRITICAL**: When adding, modifying, or deleting any endpoint in `backend/app/routers/*.py`:

1. **Always update BOTH Postman collection files**:
   - `docs/Financier_Postman_Collection.json` - Service-specific collection
   - `docs/Kuberan_Complete_API_Postman_Collection.json` - Complete API collection

2. **For new endpoints**, add a new request object with:
   - `name`: Descriptive name (e.g., "Get Spending Analysis - By Month")
   - `request.method`: HTTP method (GET, POST, PUT, DELETE)
   - `request.url`: Full URL structure with path segments and query parameters
   - `request.query`: Array of query parameter objects with `key`, `value`, and `description`
   - `description`: What the endpoint does and what filters/options are available

3. **Placement in Financier Collection**:
   - Add new endpoints in logical sections (e.g., after related endpoints)
   - Maintain alphabetical or functional grouping

4. **Placement in Complete Collection**:
   - Maintain hierarchical structure: `Service → HTTP Method → Specific Operation`
   - Use `{{baseUrl}}` variable instead of hardcoded URL
   - Add to appropriate section (e.g., "GET - Spending Analysis")

5. **For modified endpoints**: Update URL paths, query parameters, or descriptions
6. **For deleted endpoints**: Remove from both collections
7. **Test endpoints** after adding to collections to ensure correctness
8. **Commit router changes and both collection files together**

**Example new endpoint structure:**
```json
{
  "name": "Get Spending Analysis - By Month",
  "request": {
    "method": "GET",
    "header": [],
    "url": {
      "raw": "{{baseUrl}}/financier/spending/analysis?year=2025&month=7",
      "host": ["{{baseUrl}}"],
      "path": ["financier", "spending", "analysis"],
      "query": [
        {"key": "year", "value": "2025", "description": "Filter by year"},
        {"key": "month", "value": "7", "description": "Filter by month (1-12)"}
      ]
    },
    "description": "Analyze spending for a specific month with daily breakdown"
  }
}
```

### Code Documentation
- Use docstrings for all classes and functions
- Document parameters with `Args:` section
- Document return values with `Returns:` section
- Document exceptions with `Raises:` section
- Add inline comments for complex logic only

---

## Database Guidelines

### MongoDB Collections
- Use Beanie ODM for document modeling
- Collection names: plural snake_case (e.g., `stock_prices`, `ticker_config`)
- Always define indexes in model's `Settings` class
- Use compound indexes for common query patterns

### Repositories Pattern
- All database operations through repository classes
- Repository methods should be async
- Keep repositories focused on data access only (no business logic)
- Use singleton instances (e.g., `stock_repository`)

---

## Background Jobs & Scheduling

### Job Structure
Located in `backend/app/services/jobs/`:

```python
# Pure function (core logic)
async def process_data(input: str) -> Dict:
    """Testable business logic"""
    pass

# Job class (state + lifecycle)
class MyJob:
    """State tracking and job management"""
    last_run: datetime
    run_count: int
    
    async def run(self):
        """Scheduled execution"""
        result = await process_data(input)
        self._update_stats()
```

### Scheduler Registry
Register all jobs in `backend/app/services/scheduler/registry.py`:

```python
def register_all_jobs():
    job_scheduler.add_job(
        func=my_job.run,
        trigger=CronTrigger(...),
        job_id='unique_id',
        name='Human Readable Name'
    )
```

---

## Testing Principles

### When to Write Tests
- Always test pure functions (they're easy to test)
- Test critical business logic
- Test edge cases and error handling
- Integration tests for API endpoints

### Manual Testing Workflow
After endpoint changes:
1. Restart backend: `docker-compose restart backend`
2. Test with curl or Postman
3. Verify logs: `docker logs kuberan-backend-1 --tail 50`
4. Check database: `docker exec kuberan-mongodb mongosh`

**Python commands:** Always use `python3` syntax:
```bash
# ✅ Correct
python3 test_script.py
python3 -m pytest

# ❌ Wrong
python test_script.py
```

---

## Error Handling

### Logging
- Use structured logging with context
- Log format: `[timestamp] Message: details`
- Success: `✓ Action completed`
- Errors: `✗ Action failed: reason`
- Info: `ℹ Status update`

### HTTP Error Responses
- `400 Bad Request`: Invalid input
- `404 Not Found`: Resource doesn't exist
- `500 Internal Server Error`: Server-side errors
- Always include descriptive `detail` message

---

## Stock Market Specific

### Market Hours
- Use NYSE calendar (US/Eastern timezone)
- Trading hours: 9:00 AM - 5:00 PM EST (Monday-Friday)
- Account for holidays using `pandas_market_calendars`
- All market-related logic in `backend/app/core/market_calendar.py`

### Price Collection
- Poll every 60 seconds during market hours
- Capture closing price at market close (5:00 PM)
- Store all price points for historical analysis
- Handle Yahoo Finance API rate limits and errors gracefully

---

## Financial Analytics Specific

### Visualization Guidelines
**CRITICAL**: Visualizations are for **frontend consumption only**, NOT for export/download.

- **Purpose**: Charts generated by `/financier/analytics/visualizations` are base64-encoded images
- **Usage**: Intended for React frontend to display using `<img src="data:image/png;base64,{data}" />`
- **Format**: PNG or SVG returned as base64 strings in JSON response
- **Storage**: Images are NOT saved to disk or database
- **Export**: Do NOT implement file download, PDF export, or email features for visualizations
- **Frontend Integration**: Charts will be consumed by React components in future implementation

### Analytics Features
- **Cash Flow Analysis**: Income, expenses, net cash flow over time
- **Spending Breakdown**: Category-based analysis with percentages
- **Outlier Detection**: Z-score method (threshold: 3.0) for unusual transactions
- **Trend Analysis**: Linear regression for spending predictions
- **Recurring Payments**: Auto-detection of subscriptions and fixed expenses
- **Financial Health**: Savings rate, expense ratios, diversification metrics

### Analytics Service Architecture
- **Location**: `backend/app/services/analytics_service.py`
- **Pattern**: Hybrid functional/OOP (pure functions for logic, service class for orchestration)
- **Dependencies**: numpy, pandas, scipy, matplotlib, seaborn
- **Data Source**: Uses `financial_repository` for transaction access
- **Processing**: Can handle up to 100,000 transactions per query

---

## File Change Protocols

### Adding New Endpoints
1. Add route function to appropriate router file
2. Update `docs/API.md` with endpoint documentation
3. Update **BOTH Postman collections** (`docs/Financier_Postman_Collection.json` and `docs/Kuberan_Complete_API_Postman_Collection.json`)
4. Test endpoint thoroughly
5. Update "Last Updated" dates
6. Commit router + documentation + collections together

### Adding New Jobs
1. Create job file in `backend/app/services/jobs/`
2. Use hybrid pattern (pure functions + job class)
3. Register in `backend/app/services/scheduler/registry.py`
4. Update `docs/API.md` background jobs section if user-facing
5. Test job execution and error handling

### Refactoring Architecture
1. Consider impact on scalability and future features
2. Maintain backwards compatibility where possible
3. Update all affected imports
4. Update documentation (both code and `docs/`)
5. Test thoroughly before committing

### Modifying Database Models
1. Update model in `backend/app/models.py`
2. Update repository methods if needed
3. Consider migration impact (MongoDB is schemaless but plan for data changes)
4. Update affected endpoints and documentation

---

## Docker & Development

### Container Management
- Backend: `docker-compose restart backend` after code changes
- View logs: `docker logs kuberan-backend-1 --tail N`
- Rebuild: `docker-compose build backend` (if dependencies change)

### MongoDB Access
```bash
# Access MongoDB shell
docker exec -it kuberan-mongodb mongosh kuberan

# Check collections
db.getCollectionNames()

# Count documents
db.stock_prices.countDocuments({ticker: "AAPL"})
```

---

## Customer Requirements Template

When customer provides new requirements, consider:

1. **Scalability**: How does this affect future features?
2. **Architecture**: Which layer does this belong in?
3. **Documentation**: What needs updating?
4. **Testing**: How do we verify it works?
5. **Backwards Compatibility**: Will this break existing features?

---

## Common Patterns & Anti-Patterns

### ✅ DO
- Use centralized scheduler for all jobs
- Extract reusable logic to `core/`
- Keep routers thin (delegate to services)
- Use pure functions for testable logic
- Update documentation with code changes
- Use type hints everywhere
- Handle errors gracefully with proper logging
- **Process financial PDFs in-memory only**
- **Store ONLY transaction data (no account info)**
- **Use SHA256 hashes for file deduplication**
- **Return visualizations as base64 for frontend consumption**

### ❌ DON'T
- Create multiple scheduler instances
- Put business logic in routers
- Use local imports (unless circular dependency)
- Forget to update documentation (API.md + both Postman collections)
- Hardcode configuration values
- Ignore error cases
- Use OOP when pure functions suffice
- **Store PDF files anywhere**
- **Store account numbers or personal info**
- **Commit financial documents to git**
- **Expose sensitive financial data in logs or responses**
- **Implement file download/export for visualizations (frontend-only feature)**

---

## Quick Reference Commands

```bash
# Restart backend after code changes
docker-compose restart backend

# View backend logs
docker logs kuberan-backend-1 --tail 50 -f

# Test endpoint
curl http://localhost:8000/stocks/price/stats

# Check MongoDB
docker exec kuberan-mongodb mongosh kuberan --eval "db.stock_prices.countDocuments()"

# Rebuild if dependencies change
docker-compose build backend
```

---

## Notes for Future Copilot Sessions

- This project prioritizes **scalability** and **clean architecture**
- Always ask "how does this affect future features?" before implementing
- Documentation is not optional - it's part of the implementation
- When in doubt, use functional programming first, add OOP when state/lifecycle needed
- The user values thoughtful architecture over quick hacks

**Last Updated:** January 19, 2025
