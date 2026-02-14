# Kuberan Documentation

**Last Updated:** December 16, 2025  
**Organization Standard:** See [DOCUMENTATION_STRUCTURE.md](./DOCUMENTATION_STRUCTURE.md) for complete guidelines

---

## 🎯 Quick Start

| I want to... | Start here |
|--------------|------------|
| Understand the project vision | [KUBERAN_OVERVIEW.md](./KUBERAN_OVERVIEW.md) ⭐ |
| Learn how the data pipeline works | [DATA_PIPELINE_ARCHITECTURE.md](./DATA_PIPELINE_ARCHITECTURE.md) ⭐ |
| Understand documentation organization | [DOCUMENTATION_STRUCTURE.md](./DOCUMENTATION_STRUCTURE.md) |
| Find a specific document | See "Quick Reference" section below |

---

## 📚 Core Documentation

### Foundation & Architecture

#### [KUBERAN_OVERVIEW.md](./KUBERAN_OVERVIEW.md) ⭐
**Project vision, goals, and development philosophy**
- Intended users and use cases
- Key features (completed, in-progress, planned)
- Technology stack
- Development standards and best practices
- Current status and roadmap

#### [DATA_PIPELINE_ARCHITECTURE.md](./DATA_PIPELINE_ARCHITECTURE.md) ⭐
**Complete data pipeline architecture** covering all four stages:
1. **Ingestion** - Fetching raw data from providers
2. **Standardization** - Matrix-driven data consolidation  
3. **API Exposure** - REST endpoints for frontend
4. **Frontend Consumption** - UI display patterns

Includes philosophy, strategies, examples, special cases (news, timeseries, corporate actions), and documentation status tracking.

#### [DOCUMENTATION_STRUCTURE.md](./DOCUMENTATION_STRUCTURE.md)
**Organization guidelines for all project documentation**
- Directory structure and conventions
- File naming standards
- Documentation types (foundational, domain-specific, planning, archive)
- Maintenance procedures
- Quick reference for finding and creating docs

### Main Development Docs (`.github/docs/`)

For comprehensive development documentation, see **[.github/docs/](../.github/docs/)**:

- **[ARCHITECTURE.md](../.github/docs/ARCHITECTURE.md)** - System design, layers, design patterns
- **[DOMAINS.md](../.github/docs/DOMAINS.md)** - Stock Tracker, Financier, and ETF Analysis domains
- **[SECURITY.md](../.github/docs/SECURITY.md)** - **CRITICAL** for financial data handling
- **[LOGGING.md](../.github/docs/LOGGING.md)** - Structured logging standards
- **[STYLE_GUIDE.md](../.github/docs/STYLE_GUIDE.md)** - Code style and conventions
- **[TECH_STACK.md](../.github/docs/TECH_STACK.md)** - Technologies, dependencies, versions
- **[WORKFLOWS.md](../.github/docs/WORKFLOWS.md)** - Development commands and workflows
- **[WEB_SCRAPING.md](../.github/docs/WEB_SCRAPING.md)** - MCP servers and data extraction

---

## 📁 Documentation by Domain

### Data Ingestion ([Ingest/](./Ingest/))

Provider-specific specifications for data extraction:

- **[YFINANCE_INGEST_SPEC.md](./Ingest/YFINANCE_INGEST_SPEC.md)** - YFinance API specification
- **[YFINANCE_API_GUIDE.md](./Ingest/YFINANCE_API_GUIDE.md)** - YFinance implementation guide
- **[MASSIVE_INGEST_SPEC.md](./Ingest/MASSIVE_INGEST_SPEC.md)** - MASSIVE/Polygon.io specification
- **[MASSIVE_PROVIDER_GUIDE.md](./Ingest/MASSIVE_PROVIDER_GUIDE.md)** - MASSIVE implementation guide
- **[MASSIVE_REFERENCE_ENDPOINTS_GUIDE.md](./Ingest/MASSIVE_REFERENCE_ENDPOINTS_GUIDE.md)** - Complete free tier endpoint guide
- **[FINVIZ_QUOTE_PAGE_STRUCTURE.md](./Ingest/FINVIZ_QUOTE_PAGE_STRUCTURE.md)** - Finviz HTML structure
- **[STOCKANALYSIS_QUOTE_PAGE_STRUCTURE.md](./Ingest/STOCKANALYSIS_QUOTE_PAGE_STRUCTURE.md)** - StockAnalysis HTML structure

### Data Standardization ([Standardization/](./Standardization/))

Rules and strategies for normalizing multi-provider data:

- **[DATA_STANDARDIZATION_RULES.md](./DATA_STANDARDIZATION_RULES.md)** - Master rules document (398 lines)
- **[DATA_PRIORITY_MATRIX.md](./Standardization/DATA_PRIORITY_MATRIX.md)** - Provider priority matrix design
- **[standardized_ticker_view.md](./Standardization/standardized_ticker_view.md)** - Output schema specification

**To Be Created:**
- `NEWS_AGGREGATION_STRATEGY.md` - News deduplication and consolidation
- `TIMESERIES_STANDARDIZATION.md` - Price timeseries with outlier detection
- `CORPORATE_ACTIONS_AGGREGATION.md` - Splits and dividends consolidation

### API Layer ([API/](./API/)) ⏳

REST endpoint specifications and contracts:

- **[API.md](./API.md)** - General API documentation (to be moved to `API/API_OVERVIEW.md`)

**To Be Created:**
- `API_OVERVIEW.md` - API conventions, error handling, authentication
- `STANDARDIZATION_ENDPOINTS.md` - `/standardized/{ticker}` endpoint contract
- `REAL_TIME_ENDPOINTS.md` - Real-time quote endpoints
- `HISTORICAL_ENDPOINTS.md` - Historical price endpoints

### Frontend ([Frontend/](./Frontend/)) ⏳

UI component specifications and patterns:

- **[FRONTEND_IMPLEMENTATION_PLAN.md](./FRONTEND_IMPLEMENTATION_PLAN.md)** 🟢 - Flutter implementation guide (6 phases)

**To Be Created:**
- `DATA_DISPLAY_PATTERNS.md` - Source badges, tooltips, data freshness
- `STATE_MANAGEMENT.md` - Provider patterns, caching strategies
- `COMPONENT_LIBRARY.md` - Reusable UI components

### Trader Knowledge ([Knowledge/](./Knowledge/)) ⏳

Educational content for traders:

**To Be Created:**
- `TRADING_TERMINOLOGIES.md` - Glossary of trading terms
- `TRADING_STRATEGIES.md` - Common strategies and patterns
- `RISK_MANAGEMENT.md` - Risk assessment and mitigation
- `MARKET_ANALYSIS.md` - Technical and fundamental analysis

### Background Jobs ([Jobs/](./Jobs/)) ⏳

Scheduled task specifications:

**To Be Created:**
- `STANDARDIZATION_JOBS.md` - Data standardization scheduling
- `PRICE_COLLECTION_JOBS.md` - Real-time price polling
- `METADATA_ENRICHMENT_JOBS.md` - Ticker metadata updates
- `JOB_MONITORING.md` - Job health and alerting

---

## 🛠️ Planning & Work-in-Progress ([planning/](./planning/))

Temporary documents for active development:

- **[PLANNING_CHECKLIST.md](./planning/PLANNING_CHECKLIST.md)** ⏳ - Current work items and status
- **[REFACTORING_PLAN.md](./planning/REFACTORING_PLAN.md)** ⏳ - Code refactoring roadmap

**Note:** These documents are temporary and will be archived when work completes.

---

## 📦 Archive ([archive/](./archive/))

Historical documentation from previous versions:

### [2025-12-13_pre-refactor/](./archive/2025-12-13_pre-refactor/Kuberan/)

Original vision documents before standardization engine refactor:
- **[Kuberan.md](./archive/2025-12-13_pre-refactor/Kuberan/Kuberan.md)** - Original project vision and philosophy
- **[Data_Extraction.md](./archive/2025-12-13_pre-refactor/Kuberan/Data_Extraction.md)** - Data extraction philosophy and approach
- **[Data_Standardization.md](./archive/2025-12-13_pre-refactor/Kuberan/Data_Standardization.md)** - Original standardization concepts
- **[Trader_Knowledgebase.md](./archive/2025-12-13_pre-refactor/Kuberan/Trader_Knowledgebase.md)** - Knowledge base vision

**Superseded By:** [KUBERAN_OVERVIEW.md](./KUBERAN_OVERVIEW.md), [DATA_PIPELINE_ARCHITECTURE.md](./DATA_PIPELINE_ARCHITECTURE.md)

---

## 🔍 Quick Reference

### Finding Documentation

| I want to... | Look at... | Status |
|--------------|------------|--------|
| Understand the overall vision | [KUBERAN_OVERVIEW.md](./KUBERAN_OVERVIEW.md) | 🟢 |
| Understand the data pipeline | [DATA_PIPELINE_ARCHITECTURE.md](./DATA_PIPELINE_ARCHITECTURE.md) | 🟢 |
| Learn documentation organization | [DOCUMENTATION_STRUCTURE.md](./DOCUMENTATION_STRUCTURE.md) | 🟢 |
| Learn how we ingest from YFinance | [Ingest/YFINANCE_INGEST_SPEC.md](./Ingest/YFINANCE_INGEST_SPEC.md) | 🟢 |
| Learn how we ingest from MASSIVE | [Ingest/MASSIVE_INGEST_SPEC.md](./Ingest/MASSIVE_INGEST_SPEC.md) | 🟢 |
| Learn data standardization rules | [DATA_STANDARDIZATION_RULES.md](./DATA_STANDARDIZATION_RULES.md) | 🟢 |
| Learn provider priority rules | [Standardization/DATA_PRIORITY_MATRIX.md](./Standardization/DATA_PRIORITY_MATRIX.md) | 🟢 |
| Learn standardized output schema | [Standardization/standardized_ticker_view.md](./Standardization/standardized_ticker_view.md) | 🟢 |
| Learn API conventions | [API.md](./API.md) | 🟢 |
| Build the frontend | [FRONTEND_IMPLEMENTATION_PLAN.md](./FRONTEND_IMPLEMENTATION_PLAN.md) | 🟢 |
| See current work plan | [planning/PLANNING_CHECKLIST.md](./planning/PLANNING_CHECKLIST.md) | ⏳ |

### Status Legend

- 🟢 **Active** - Current, authoritative, regularly updated
- 🟡 **Draft** - Work in progress, not yet authoritative
- 🔴 **Deprecated** - Superseded by another document
- ⏳ **Temporary** - Planning document, will be archived when work completes
- ⭐ **Core** - Critical document, start here for onboarding

---

## 🚀 Quick Start Guide

1. **New to the project?** Start with [KUBERAN_OVERVIEW.md](./KUBERAN_OVERVIEW.md) ⭐
2. **Want to understand the architecture?** Read [DATA_PIPELINE_ARCHITECTURE.md](./DATA_PIPELINE_ARCHITECTURE.md) ⭐
3. **Need to find a specific document?** See [DOCUMENTATION_STRUCTURE.md](./DOCUMENTATION_STRUCTURE.md) for organization guidelines
4. **Working on ingestion?** See [Ingest/](./Ingest/) directory for provider specifications
5. **Working on standardization?** See [Standardization/](./Standardization/) directory for rules and schemas
6. **Working on API?** See [API.md](./API.md) for endpoint documentation
7. **Working on frontend?** See [FRONTEND_IMPLEMENTATION_PLAN.md](./FRONTEND_IMPLEMENTATION_PLAN.md)

---

## 📝 Contributing to Documentation

When creating or updating documentation:

1. **Follow the structure** defined in [DOCUMENTATION_STRUCTURE.md](./DOCUMENTATION_STRUCTURE.md)
2. **Use the standard header template** (see DOCUMENTATION_STRUCTURE.md)
3. **Add status indicators** (🟢🟡🔴⏳⭐)
4. **Keep documents under 300 lines** (split if needed)
5. **Update README.md** when adding new documents
6. **Cross-reference related documents**
7. **Archive superseded documents** (don't delete)

### Document Size Guidelines

- **Maximum 300 lines per document** (excludes blanks, comments, docstrings)
- **Split large documents** into logical modules with clear naming
- **Use subdirectories** for related documents (e.g., Ingest/, Standardization/)

### Maintenance Schedule

- **Daily**: Update planning documents as work progresses
- **Weekly**: Review domain-specific docs for accuracy
- **Monthly**: Review foundational docs, archive completed planning docs
- **Quarterly**: Full documentation audit and reorganization

---

## 📊 Documentation Coverage

### Completed ✅

- Core Architecture (DATA_PIPELINE_ARCHITECTURE.md)
- Project Overview (KUBERAN_OVERVIEW.md)
- Documentation Structure (DOCUMENTATION_STRUCTURE.md)
- Ingestion Layer (9 provider specs)
- Standardization Layer (3 core documents)
- Frontend Plan (FRONTEND_IMPLEMENTATION_PLAN.md)

### In Progress 🔄

- API Layer (endpoints being documented)
- Background Jobs (job specs being created)
- Trader Knowledge (content gathering phase)

### Planned 🟡

- API subdirectory with endpoint contracts
- Frontend subdirectory with component patterns
- Knowledge subdirectory with educational content
- Jobs subdirectory with scheduling specifications

---

**For questions or improvements, see the Contributing section in [KUBERAN_OVERVIEW.md](./KUBERAN_OVERVIEW.md)**

### Archived Documentation

Obsolete documentation moved to **[archive/](./archive/)** during Phase 0 cleanup:
- AlphaVantage implementation plans (superseded by MASSIVE)
- Redundant MASSIVE API documentation (consolidated into reference guide)
- Legacy unstructured notes

## 🎯 Quick Start

1. **Architecture**: Start with [ARCHITECTURE.md](../.github/docs/ARCHITECTURE.md)
2. **Security**: Read [SECURITY.md](../.github/docs/SECURITY.md) before handling financial data
3. **Coding**: Follow [STYLE_GUIDE.md](../.github/docs/STYLE_GUIDE.md)
4. **API**: Reference [API.md](./API.md) or [Kuberan_API_Collection.json](./Kuberan_API_Collection.json)

## 🔄 Contributing

When adding new endpoints or modifying existing ones:

1. **Update router file**: `backend/app/routers/*.py`
2. **Update API documentation**: `docs/API.md`
3. **Update Postman collection**: `docs/Kuberan_API_Collection.json`
4. **Update "Last Updated" dates** in documentation
5. **Test endpoint** with Postman or curl
6. **Commit all changes together**: router + docs + collection

This ensures documentation always reflects the actual implementation.

---

**Documentation Structure Last Updated:** December 2, 2025  
**Phase 0 Cleanup Completed:** December 2, 2025
