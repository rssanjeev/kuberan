# GitHub Copilot Instructions for Kuberan Project

## Project Context

Kuberan is a stock price tracking and notification system built with:
- **Backend**: FastAPI (Python) with MongoDB
- **Frontend**: React (future implementation)
- **Architecture**: Hybrid functional/OOP approach
- **Deployment**: Docker Compose

---

## Core Development Principles

### 1. Architectural Guidelines

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

## File Change Protocols

### Adding New Endpoints
1. Add route function to appropriate router file
2. Update `docs/API.md` with endpoint documentation
3. Test endpoint thoroughly
4. Update "Last Updated" dates
5. Commit router + documentation together

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

### ❌ DON'T
- Create multiple scheduler instances
- Put business logic in routers
- Use local imports (unless circular dependency)
- Forget to update documentation
- Hardcode configuration values
- Ignore error cases
- Use OOP when pure functions suffice

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

**Last Updated:** November 11, 2025
