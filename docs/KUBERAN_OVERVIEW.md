# Kuberan - Financial Intelligence Platform

**Last Updated:** December 16, 2025  
**Status:** 🟢 Active - Authoritative Reference  
**Purpose:** Project vision, goals, user personas, and development philosophy  
**Related Docs:**
- [DATA_PIPELINE_ARCHITECTURE.md](DATA_PIPELINE_ARCHITECTURE.md) - Technical architecture
- [DOCUMENTATION_STRUCTURE.md](DOCUMENTATION_STRUCTURE.md) - Documentation organization

---

## Vision

**Kuberan** is a comprehensive financial intelligence platform designed to gather, standardize, and present all relevant information required to enable users to make informed trading decisions.

### Core Mission

Empower individual traders with institutional-grade data aggregation and analysis capabilities, democratizing access to financial intelligence that was previously available only to professional traders and large institutions.

---

## Functional Philosophy

### Data-Centric Approach

1. **Build Knowledgebase:** Continuously update and expand understanding of trading terminologies and user references
2. **Data Aggregation:** Collect data from multiple reliable financial data providers to ensure accuracy and comprehensiveness
3. **No Synthetic Data:** NEVER calculate or derive new financial values - only select from existing provider data
4. **Source Transparency:** Every data point includes its source provider for verification
5. **Standardization:** Normalize data from multiple sources to create a single source of truth

### User-Centric Design

1. **Clear & Concise:** Present information in an easily understandable format
2. **Real-Time Updates:** Provide up-to-date information for timely market responses
3. **Analytical Tools:** Include technical analysis, trend identification, and risk assessment
4. **Customization:** Allow users to tailor information and alerts to their strategies

---

## Intended Users

### Primary: Individual Retail Traders

**Skill Range:** Novice to experienced investors

**Characteristics:**
- Self-directed investors managing personal portfolios
- Seek comprehensive tools to assist trading decisions
- Range from beginners learning the basics to experienced traders
- Value transparency and want to understand "why" behind recommendations

**User Needs:**
1. **Beginners:**
   - Clear explanations of trading concepts
   - Guided decision-making support
   - Educational resources integrated into workflow
   - Low barrier to entry

2. **Intermediate Traders:**
   - Multi-source data comparison
   - Technical analysis tools
   - Portfolio tracking and performance metrics
   - Alert system for price movements

3. **Advanced Traders:**
   - Raw data access with full source transparency
   - Custom analysis capabilities
   - API access for algorithmic trading
   - Advanced charting and backtesting

### Design Goal

Make the tool **user-friendly for all levels**, especially beginners, while providing depth for advanced users. Empower users to:
- Make informed decisions independently
- Understand the market better
- See the bigger picture of market dynamics
- Build confidence in their trading strategy

---

## Key Features

### Priority Features (Implemented or In Progress)

#### 1. Trader Knowledgebase
**Status:** 🟡 Planned  
**Purpose:** Comprehensive knowledge foundation for trading concepts

**Components:**
- Trading terminologies and definitions
- Strategy explanations
- Market analysis frameworks
- Risk management best practices

**Documentation:** [Knowledge/TRADER_KNOWLEDGEBASE_OVERVIEW.md](Knowledge/TRADER_KNOWLEDGEBASE_OVERVIEW.md) (to be created)

#### 2. Multi-Source Data Extraction
**Status:** 🟢 Active  
**Purpose:** Aggregate data from APIs and web scraping

**Data Sources:**
- YFinance (price data, company info)
- MASSIVE/Polygon.io (comprehensive stock data)
- Finviz (market overview, sentiment)
- StockAnalysis (detailed financials)

**Documentation:** [Ingest/](Ingest/) directory

#### 3. Data Standardization
**Status:** 🟢 Active  
**Purpose:** Create single source of truth from multiple providers

**Strategies:**
- `single_value`: Select highest-priority provider value (stock metrics)
- `aggregate_union`: Consolidate from all sources with deduplication (news articles)
- `timeseries_primary_with_checks`: Primary source with outlier detection (price data)

**Documentation:** [Standardization/](Standardization/) directory

#### 4. Stock Tracker
**Status:** 🟢 Active  
**Purpose:** Real-time price monitoring and historical analysis

**Features:**
- Real-time price updates during market hours
- Historical price tracking
- Ticker watchlists
- Metadata enrichment (12,140 tickers)

**Documentation:** `.github/docs/DOMAINS.md` (Stock Tracker section)

#### 5. Financier
**Status:** 🟢 Active  
**Purpose:** Credit card statement processing and spending analysis

**Features:**
- PDF statement upload and parsing
- Transaction categorization
- Spending analytics
- Budget tracking

**Documentation:** `.github/docs/DOMAINS.md` (Financier section)

#### 6. ETF Analysis
**Status:** 🟢 Active  
**Purpose:** Comprehensive ETF research and comparison

**Features:**
- ETF profile and holdings analysis
- Multi-ETF comparison
- Portfolio optimization
- Backtesting capabilities

**Documentation:** `.github/docs/DOMAINS.md` (ETF Analysis section)

### Future Features (Planned)

#### News Integration
**Status:** 🟡 Planned  
**Purpose:** Aggregate news from multiple sources with deduplication

**Strategy:** `aggregate_union` - Consolidate articles from all providers, remove duplicates, preserve sources

**Documentation:** [Standardization/NEWS_AGGREGATION_STRATEGY.md](Standardization/NEWS_AGGREGATION_STRATEGY.md) (to be created)

#### Alerts & Notifications
**Status:** 🟡 Planned  
**Purpose:** Customizable alerts for market movements

**Triggers:**
- Price threshold crossings
- Volume spikes
- News sentiment changes
- Technical indicator signals

#### Portfolio Management
**Status:** 🟡 Planned  
**Purpose:** Track and analyze investment portfolios

**Features:**
- Multi-portfolio support
- Performance tracking
- Risk assessment
- Rebalancing recommendations

#### Reporting
**Status:** 🟡 Planned  
**Purpose:** Generate comprehensive market and portfolio reports

**Report Types:**
- Daily market summaries
- Portfolio performance reports
- Tax documentation
- Custom analysis reports

---

## Development Philosophy

### Code Quality Standards

#### File Size
- **Maximum 300 lines** per Python script (excluding comments/docstrings)
- Split larger functionality into separate modules
- Keep functions focused and single-purpose

#### Logging
- **Comprehensive logging** in all scripts for debugging
- **Structured logging** with context (use `extra` parameter)
- **Timezone:** All timestamps in Eastern Standard Time (EST)
- Follow guidelines in `.github/docs/LOGGING.md`

#### Configuration
- **No hardcoded values** - use configuration files
- Store configs in `/backend/config/` directory
- Use YAML for structured configuration
- Use `.env` for secrets (never commit)

#### Error Handling
- **Graceful failures** - log error and continue with next item
- Don't crash on single item failures in batch operations
- Provide meaningful error messages
- Include context in error logs

#### Documentation
- **Comprehensive docstrings** for all functions and classes
- **Inline comments** for complex logic
- **Update documentation** with every code change
- Keep copilot instructions current

#### Code Style
- **Follow PEP 8** guidelines for Python
- **Use type hints** for all function parameters and returns
- **Async/await** wherever possible for I/O operations
- **Modular and reusable** code for easy maintenance

#### Testing
- **Unit tests** for all core functionality
- **Integration tests** for API endpoints
- **Golden fixtures** for data transformation validation
- Maintain >80% test coverage

### Architectural Principles

#### Asynchronous by Default
- Use `async/await` for all I/O operations
- Non-blocking database queries
- Concurrent API requests where appropriate
- Event-driven background jobs

#### Single Responsibility
- Each service handles one domain
- Each function does one thing well
- Clear separation of concerns
- Thin controllers, fat services

#### Layered Architecture
```
Routers (API Layer)
    ↓
Services (Business Logic)
    ↓
Repositories (Data Access)
    ↓
Database (MongoDB)
```

#### Copilot Integration
- **Keep copilot instructions updated** with every significant change
- Document file locations and purposes
- Provide context for architectural decisions
- Enable efficient AI-assisted development

---

## Technology Stack

### Backend
- **Language:** Python 3.14
- **Framework:** FastAPI (async web framework)
- **Database:** MongoDB with Beanie ODM
- **Container:** Docker + Docker Compose

### Frontend
- **Framework:** Flutter (Web, iOS, Android)
- **State Management:** Provider
- **Navigation:** go_router
- **HTTP Client:** http package

### Data Sources
- **YFinance:** Real-time and historical prices
- **MASSIVE (Polygon.io):** Comprehensive stock data
- **Finviz:** Market overview and sentiment
- **StockAnalysis:** Detailed financial statements
- **Alpha Vantage:** ETF data (30-day cache)

### Background Jobs
- **Scheduler:** APScheduler
- **Task Management:** asyncio
- **Job Types:** Price collection, metadata enrichment, standardization

---

## Current Status

### Completed Features ✅

1. **Data Ingestion Framework**
   - YFinance provider implementation
   - MASSIVE provider implementation
   - Finviz web scraping
   - StockAnalysis web scraping
   - Provider snapshot storage

2. **Data Standardization Engine**
   - single_value strategy (65 data points)
   - Priority matrix configuration
   - Standardized ticker view schema
   - End-to-end tests with golden fixtures

3. **Stock Tracker**
   - Real-time price collection
   - Market hours detection
   - 12,140 ticker metadata (41.7% enriched)
   - Historical price storage

4. **Financier**
   - Chase statement PDF parsing
   - Transaction storage and categorization
   - Spending analytics
   - Visualization generation

5. **ETF Analysis**
   - 67 API endpoints
   - Profile and holdings analysis
   - Comparison and screening
   - Portfolio management
   - Backtesting capabilities

### In Progress 🔄

1. **API Standardization Endpoints**
   - Design `/standardized/{ticker}` endpoint
   - Expose source information for each data point
   - Query parameter options (field selection, format)

2. **News Aggregation Strategy**
   - Define aggregate_union strategy
   - Deduplication algorithm
   - Multi-source consolidation
   - News article schema

3. **Frontend Development**
   - Flutter web application
   - Stock tracker dashboard
   - Financier interface
   - ETF analysis screens

### Planned 🟡

1. **Background Standardization Jobs**
   - Scheduled data processing
   - Freshness monitoring
   - Error recovery

2. **Price Timeseries Standardization**
   - timeseries_primary_with_checks strategy
   - Outlier detection
   - Anomaly flagging

3. **Corporate Actions Aggregation**
   - Stock splits consolidation
   - Dividend history aggregation
   - Conflict resolution

4. **Monitoring & Observability**
   - Data quality metrics
   - Provider availability tracking
   - Performance dashboards
   - Alerting rules

---

## Documentation Reference

### Core Architecture
- [DATA_PIPELINE_ARCHITECTURE.md](DATA_PIPELINE_ARCHITECTURE.md) - ⭐ Start here for technical overview
- [DATA_STANDARDIZATION_RULES.md](DATA_STANDARDIZATION_RULES.md) - Standardization philosophy and rules
- [DOCUMENTATION_STRUCTURE.md](DOCUMENTATION_STRUCTURE.md) - Documentation organization

### Domain-Specific
- [Ingest/](Ingest/) - Data extraction specifications by provider
- [Standardization/](Standardization/) - Data standardization strategies
- [API/](API/) - API endpoint contracts (to be created)
- [Frontend/](Frontend/) - Frontend implementation plans
- [Knowledge/](Knowledge/) - Trading concepts and terminology (to be created)

### Planning
- [planning/PLANNING_CHECKLIST.md](planning/PLANNING_CHECKLIST.md) - Current work planning
- [planning/decisions/](planning/decisions/) - Architectural decision records

### Legacy
- [archive/2025-12-13_pre-refactor/](archive/2025-12-13_pre-refactor/) - Pre-refactor documentation

---

## Project Roadmap

### Phase 1: Foundation (Completed)
- ✅ Multi-provider data ingestion
- ✅ Data standardization engine
- ✅ Stock tracker with real-time prices
- ✅ Financier with statement processing
- ✅ ETF analysis with 67 endpoints

### Phase 2: API & Frontend (Current)
- 🔄 Standardization API endpoints
- 🔄 Flutter web application
- 🟡 News aggregation strategy
- 🟡 Background data processing jobs

### Phase 3: Intelligence (Future)
- 🟡 Trader knowledgebase
- 🟡 Portfolio management
- 🟡 Alerts & notifications
- 🟡 Custom analysis tools

### Phase 4: Scale & Polish (Future)
- 🟡 Mobile apps (iOS/Android)
- 🟡 Performance optimization
- 🟡 Advanced analytics
- 🟡 Machine learning predictions

---

## Success Metrics

### Data Quality
- 95%+ of standardized fields have values
- <1% discrepancies between providers
- <5 minute data freshness during market hours

### User Experience
- <2 second page load times
- <100ms API response times
- Mobile-responsive on all screen sizes

### Reliability
- 99.9% uptime
- <0.1% error rate
- All background jobs complete successfully

### Growth
- 100% of S&P 500 tickers enriched
- 10+ data providers integrated
- 1000+ daily active users (future goal)

---

## Contributing

### Development Workflow
1. Create feature branch from `develop`
2. Implement feature with tests
3. Update documentation
4. Submit pull request
5. Code review and merge

### Documentation Requirements
- Update relevant docs in `/docs/` with code changes
- Update copilot instructions in `.github/copilot-instructions.md`
- Add examples for new features
- Keep "Last Updated" dates current

### Code Review Checklist
- [ ] Code follows development philosophy
- [ ] Tests pass and coverage maintained
- [ ] Documentation updated
- [ ] Copilot instructions updated
- [ ] No hardcoded values
- [ ] Proper error handling
- [ ] Structured logging implemented

---

## Contact & Support

**Project Owner:** Engineering Team  
**Repository:** https://github.com/rssanjeev/kuberan  
**Documentation:** `/docs/` directory in repository

---

**Last Reviewed:** December 16, 2025  
**Next Review:** January 16, 2026
