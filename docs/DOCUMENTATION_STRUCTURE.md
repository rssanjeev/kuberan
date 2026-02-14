# Documentation Structure & Guidelines

**Last Updated:** December 16, 2025  
**Purpose:** Define the standard organization and structure for all Kuberan project documentation  
**Status:** 🟢 Active - Authoritative Reference

---

## Documentation Philosophy

### Core Principles

1. **Single Source of Truth:** Each concept should have ONE authoritative document
2. **Clear Hierarchy:** Organized by domain → feature → implementation detail
3. **Permanence Levels:** Separate foundational docs from temporary planning docs
4. **Maximum 300 Lines:** Break large documents into focused sub-documents
5. **Living Documentation:** Update docs alongside code changes
6. **Copilot-Friendly:** Structure enables efficient AI-assisted development

### Documentation Types

| Type | Purpose | Location | Lifespan |
|------|---------|----------|----------|
| **Foundational** | Core concepts, architecture, philosophy | `/docs/` root | Permanent |
| **Domain-Specific** | Feature area documentation | `/docs/{Domain}/` | Permanent |
| **Implementation** | Technical specs, contracts, schemas | `/docs/{Domain}/` or `/docs/Ingest/` | Permanent |
| **Planning** | Roadmaps, checklists, decisions | `/docs/planning/` | Temporary |
| **Archive** | Superseded or outdated docs | `/docs/archive/{date}/` | Historical |

---

## Directory Structure

```
docs/
├── README.md                              # Master index with navigation
├── DOCUMENTATION_STRUCTURE.md             # THIS FILE - Structure guidelines
│
├── [FOUNDATIONAL] - Core Architecture
│   ├── KUBERAN_OVERVIEW.md                # Project vision, goals, users
│   ├── DATA_PIPELINE_ARCHITECTURE.md      # ⭐ Pipeline architecture (4 stages)
│   └── DATA_STANDARDIZATION_RULES.md      # Standardization rules & philosophy
│
├── [CONFIGURATION]
├── /config/
│   └── data_priority_matrix.yaml          # Data source priority config
│
├── [DOMAIN: DATA INGESTION]
├── /Ingest/                               # Provider-specific ingestion specs
│   ├── YFINANCE_INGEST_SPEC.md
│   ├── YFINANCE_API_GUIDE.md
│   ├── MASSIVE_INGEST_SPEC.md
│   ├── MASSIVE_PROVIDER_GUIDE.md
│   ├── MASSIVE_REFERENCE_ENDPOINTS_GUIDE.md
│   ├── FINVIZ_QUOTE_PAGE_STRUCTURE.md
│   ├── STOCKANALYSIS_QUOTE_PAGE_STRUCTURE.md
│   └── finviz_pagesource*.md              # HTML structure references
│
├── [DOMAIN: DATA STANDARDIZATION]
├── /Standardization/                      # Standardization strategies & specs
│   ├── DATA_STANDARDIZATION_RULES.md      # Master rules document
│   ├── DATA_PRIORITY_MATRIX.md            # Matrix design documentation
│   ├── standardized_ticker_view.md        # Output schema specification
│   ├── NEWS_AGGREGATION_STRATEGY.md       # (To be created) News deduplication
│   ├── TIMESERIES_STANDARDIZATION.md      # (To be created) Price timeseries
│   └── CORPORATE_ACTIONS_AGGREGATION.md   # (To be created) Splits/dividends
│
├── [DOMAIN: API LAYER]
├── /API/                                  # API endpoint specifications
│   ├── API_OVERVIEW.md                    # API architecture & conventions
│   ├── STANDARDIZATION_ENDPOINTS.md       # (To be created) /standardized/{ticker}
│   ├── STOCKS_ENDPOINTS.md                # Stock domain endpoints
│   ├── FINANCIER_ENDPOINTS.md             # Financier domain endpoints
│   └── Kuberan_API_Collection.json        # Postman collection
│
├── [DOMAIN: FRONTEND]
├── /Frontend/                             # Frontend integration docs
│   ├── FRONTEND_IMPLEMENTATION_PLAN.md    # Flutter implementation plan
│   ├── DATA_DISPLAY_PATTERNS.md           # (To be created) UI components
│   └── STATE_MANAGEMENT.md                # (To be created) State architecture
│
├── [DOMAIN: TRADER KNOWLEDGE]
├── /Knowledge/                            # Trading concepts & terminology
│   ├── TRADER_KNOWLEDGEBASE_OVERVIEW.md   # (To be created) Knowledge structure
│   ├── TRADING_TERMINOLOGIES.md           # (To be created) Terms & definitions
│   ├── TRADING_STRATEGIES.md              # (To be created) Strategy guides
│   └── MARKET_ANALYSIS.md                 # (To be created) Analysis frameworks
│
├── [BACKGROUND JOBS & AUTOMATION]
├── /Jobs/                                 # Background job specifications
│   ├── JOB_ARCHITECTURE.md                # (To be created) Job framework
│   ├── STANDARDIZATION_JOBS.md            # (To be created) Data processing jobs
│   └── MONITORING_ALERTING.md             # (To be created) Observability
│
├── [PLANNING & TEMPORARY]
├── /planning/                             # ⏳ Temporary planning documents
│   ├── PLANNING_CHECKLIST.md              # Current work planning checklist
│   ├── REFACTORING_PLAN.md                # Refactoring roadmap
│   └── decisions/                         # Architectural decision records
│       └── ADR-{YYYYMMDD}-{title}.md
│
├── [ARCHIVE]
└── /archive/                              # Historical/superseded documentation
    └── {YYYY-MM-DD}_pre-refactor/
        └── Kuberan/
            ├── Kuberan.md
            ├── Data_Extraction.md
            ├── Data_Standardization.md
            └── Trader_Knowledgebase.md
```

---

## Documentation Conventions

### File Naming

| Type | Pattern | Example |
|------|---------|---------|
| **Overview** | `{DOMAIN}_OVERVIEW.md` | `KUBERAN_OVERVIEW.md` |
| **Architecture** | `{DOMAIN}_ARCHITECTURE.md` | `DATA_PIPELINE_ARCHITECTURE.md` |
| **Strategy** | `{FEATURE}_STRATEGY.md` | `NEWS_AGGREGATION_STRATEGY.md` |
| **Specification** | `{PROVIDER}_INGEST_SPEC.md` | `YFINANCE_INGEST_SPEC.md` |
| **Endpoints** | `{DOMAIN}_ENDPOINTS.md` | `STANDARDIZATION_ENDPOINTS.md` |
| **Guide** | `{TOOL}_GUIDE.md` | `YFINANCE_API_GUIDE.md` |
| **Planning** | `{PURPOSE}_PLAN.md` or `{PURPOSE}_CHECKLIST.md` | `PLANNING_CHECKLIST.md` |

### Document Header Template

Every document should start with:

```markdown
# {Document Title}

**Last Updated:** {Date}  
**Status:** {🟢 Active | 🟡 Draft | 🔴 Deprecated | ⏳ Temporary}  
**Purpose:** {One-line description}  
**Related Docs:** {Links to related documentation}

---
```

### Status Indicators

- 🟢 **Active:** Current, authoritative, regularly updated
- 🟡 **Draft:** Work in progress, not yet authoritative
- 🔴 **Deprecated:** Superseded by another document, kept for reference
- ⏳ **Temporary:** Planning document, will be archived when work completes
- ⭐ **Core:** Critical document, start here for onboarding

### Document Size Guidelines

- **Maximum 300 lines** per document (excluding code examples)
- **When to split:**
  - Document exceeds 300 lines
  - Multiple distinct topics covered
  - Clear sub-sections that could stand alone
- **How to split:**
  - Create subdirectory for related documents
  - Create index document linking to sub-documents
  - Use clear cross-references between documents

---

## Domain Organization

### Data Ingestion (`/Ingest/`)

**Purpose:** Document how we fetch raw data from providers

**Contents:**
- Provider API specifications
- Web scraping page structures
- Authentication & rate limiting
- Error handling patterns
- Snapshot schemas

**Naming:** `{PROVIDER}_{TYPE}.md`

**Examples:**
- `YFINANCE_INGEST_SPEC.md` - YFinance API specification
- `FINVIZ_QUOTE_PAGE_STRUCTURE.md` - Finviz HTML structure

### Data Standardization (`/Standardization/`)

**Purpose:** Document how we normalize data from multiple sources

**Contents:**
- Standardization strategies (single_value, aggregate_union, etc.)
- Priority matrix configuration
- Output schemas
- Data quality rules
- Edge case handling

**Naming:** `{FEATURE}_STRATEGY.md` or `{ASPECT}.md`

**Examples:**
- `DATA_STANDARDIZATION_RULES.md` - Master rules
- `NEWS_AGGREGATION_STRATEGY.md` - News deduplication strategy

### API Layer (`/API/`)

**Purpose:** Document REST API endpoint contracts

**Contents:**
- Endpoint specifications
- Request/response schemas
- Error handling
- Rate limiting
- Authentication

**Naming:** `{DOMAIN}_ENDPOINTS.md`

**Examples:**
- `STANDARDIZATION_ENDPOINTS.md` - /standardized/* endpoints
- `STOCKS_ENDPOINTS.md` - Stock domain endpoints

### Frontend (`/Frontend/`)

**Purpose:** Document UI/UX patterns and frontend architecture

**Contents:**
- Component specifications
- State management patterns
- Data display guidelines
- User interaction flows

**Naming:** `{ASPECT}.md` or `{FEATURE}_IMPLEMENTATION_PLAN.md`

**Examples:**
- `FRONTEND_IMPLEMENTATION_PLAN.md` - Flutter implementation
- `DATA_DISPLAY_PATTERNS.md` - Source badge UI patterns

### Trader Knowledge (`/Knowledge/`)

**Purpose:** Document trading concepts that inform product features

**Contents:**
- Trading terminologies
- Strategy guides
- Market analysis frameworks
- Risk management concepts

**Naming:** `{TOPIC}.md`

**Examples:**
- `TRADING_TERMINOLOGIES.md` - Glossary
- `TRADING_STRATEGIES.md` - Strategy explanations

### Background Jobs (`/Jobs/`)

**Purpose:** Document automated data processing & monitoring

**Contents:**
- Job specifications
- Scheduling strategies
- Monitoring & alerting
- Performance optimization

**Naming:** `{ASPECT}_JOBS.md` or `{ASPECT}.md`

**Examples:**
- `STANDARDIZATION_JOBS.md` - Data processing jobs
- `MONITORING_ALERTING.md` - Observability setup

---

## Planning & Temporary Documents

### Planning Directory (`/planning/`)

**Purpose:** Temporary documents for active work planning

**Lifecycle:** Move to archive when work completes

**Contents:**
- Work checklists
- Decision records
- Refactoring plans
- Implementation roadmaps

**Status:** Always mark as ⏳ Temporary

**Archival Process:**
1. When work completes, move to `/archive/{YYYY-MM-DD}_completed/`
2. Update references in permanent docs
3. Create summary in permanent docs if needed

### Architectural Decision Records (ADRs)

**Location:** `/planning/decisions/ADR-{YYYYMMDD}-{title}.md`

**Template:**
```markdown
# ADR-{YYYYMMDD}: {Decision Title}

**Date:** {YYYY-MM-DD}  
**Status:** Proposed | Accepted | Superseded  
**Deciders:** {Names}

## Context
{What is the issue we're facing?}

## Decision
{What is the change we're proposing?}

## Consequences
{What becomes easier or harder?}

## Alternatives Considered
{What other options did we evaluate?}
```

---

## Archive Strategy

### When to Archive

- Document is superseded by newer version
- Planning document's work is complete
- Feature is deprecated or removed
- Major refactoring makes doc obsolete

### How to Archive

1. **Create dated directory:** `/archive/{YYYY-MM-DD}_pre-{event}/`
2. **Move document:** Keep full path structure
3. **Update references:** Fix links in active docs
4. **Add archive header:**
   ```markdown
   > ⚠️ **ARCHIVED:** {Date}  
   > **Reason:** {Why archived}  
   > **Replaced By:** {Link to new doc if applicable}
   ```

### Archive Organization

```
/archive/
├── 2025-12-13_pre-refactor/          # Before standardization refactor
│   └── Kuberan/
│       ├── Kuberan.md
│       ├── Data_Extraction.md
│       └── Data_Standardization.md
└── 2025-12-XX_pre-news-aggregation/  # (Example future archive)
    └── ...
```

---

## Cross-Referencing Guidelines

### Internal Links

Use relative paths from `/docs/` root:

```markdown
See [Data Pipeline Architecture](DATA_PIPELINE_ARCHITECTURE.md) for overview.
See [YFinance Ingest Spec](Ingest/YFINANCE_INGEST_SPEC.md) for details.
```

### Related Docs Section

Every document should list related documentation:

```markdown
**Related Docs:**
- [DATA_PIPELINE_ARCHITECTURE.md](DATA_PIPELINE_ARCHITECTURE.md) - Pipeline overview
- [Ingest/YFINANCE_INGEST_SPEC.md](Ingest/YFINANCE_INGEST_SPEC.md) - YFinance ingestion
- [config/data_priority_matrix.yaml](../config/data_priority_matrix.yaml) - Priority config
```

### Copilot Instructions

Update `.github/copilot-instructions.md` with documentation paths:

```markdown
## Documentation Structure

- **Architecture:** See docs/DATA_PIPELINE_ARCHITECTURE.md
- **Standardization:** See docs/Standardization/DATA_STANDARDIZATION_RULES.md
- **Ingestion:** See docs/Ingest/{PROVIDER}_INGEST_SPEC.md
- **API:** See docs/API/{DOMAIN}_ENDPOINTS.md
```

---

## Maintenance Procedures

### Regular Reviews

**Monthly:** Review all 🟢 Active documents for accuracy
**Quarterly:** Review document structure for needed splits/merges
**Per Feature:** Update related docs when implementing features

### Update Checklist

When updating documentation:

- [ ] Update "Last Updated" date in header
- [ ] Verify all internal links still work
- [ ] Update related docs if this doc changes
- [ ] Update copilot instructions if structure changes
- [ ] Check document size (split if >300 lines)
- [ ] Update README.md if new document added

### Documentation Review Process

**Before committing code:**
1. Identify affected documentation
2. Update affected docs
3. Add links to new docs in related docs
4. Update README.md if structure changed
5. Commit docs with code in same PR

---

## Quick Reference

### Finding the Right Document

**I want to know...** | **Look at...**
---|---
Overall project vision | `KUBERAN_OVERVIEW.md`
How the data pipeline works | `DATA_PIPELINE_ARCHITECTURE.md`
How we ingest from YFinance | `Ingest/YFINANCE_INGEST_SPEC.md`
How we standardize data | `Standardization/DATA_STANDARDIZATION_RULES.md`
What data sources we prioritize | `config/data_priority_matrix.yaml`
API endpoint contracts | `API/{DOMAIN}_ENDPOINTS.md`
Current work planning | `planning/PLANNING_CHECKLIST.md`
Trading terminology | `Knowledge/TRADING_TERMINOLOGIES.md`

### Creating New Documentation

**I'm documenting...** | **Create file at...**
---|---
New data provider | `Ingest/{PROVIDER}_INGEST_SPEC.md`
New standardization strategy | `Standardization/{FEATURE}_STRATEGY.md`
New API endpoints | `API/{DOMAIN}_ENDPOINTS.md`
New background job | `Jobs/{FEATURE}_JOBS.md`
Planning new feature | `planning/{FEATURE}_PLAN.md`
Architectural decision | `planning/decisions/ADR-{DATE}-{title}.md`

---

## Migration from Old Structure

### Completed Migrations

- ✅ Created `/Standardization/` subdirectory
- ✅ Created `/Ingest/` subdirectory
- ✅ Archived pre-refactor docs to `/archive/2025-12-13_pre-refactor/`
- ✅ Created `DATA_PIPELINE_ARCHITECTURE.md` (master architecture doc)

### Pending Migrations

1. **Create `/planning/` subdirectory**
   - Move `PLANNING_CHECKLIST.md` → `planning/PLANNING_CHECKLIST.md`
   - Move `REFACTORING_PLAN.md` → `planning/REFACTORING_PLAN.md`

2. **Create domain subdirectories**
   - Create `/API/` subdirectory
   - Create `/Frontend/` subdirectory  
   - Create `/Knowledge/` subdirectory
   - Create `/Jobs/` subdirectory

3. **Create foundational overview document**
   - Create `KUBERAN_OVERVIEW.md` (consolidate from archived Kuberan.md)
   - Extract high-level vision, goals, users, development philosophy

4. **Reorganize API documentation**
   - Move `API.md` → `API/API_OVERVIEW.md`
   - Extract domain-specific endpoints into separate files

5. **Update README.md**
   - Add navigation by domain
   - Add quick-find reference table
   - Link to this structure document

---

## Success Criteria

Documentation structure is working when:

- ✅ **Findability:** Anyone can locate the right doc in <2 minutes
- ✅ **No Duplication:** Each concept has ONE authoritative source
- ✅ **Maintainability:** Docs stay <300 lines each
- ✅ **Currency:** "Last Updated" dates are recent (<30 days)
- ✅ **Completeness:** No "TODO" or "Coming Soon" sections older than 1 sprint
- ✅ **Copilot Efficiency:** AI can find relevant context without repeated searches

---

**Document Owner:** Engineering Team  
**Review Frequency:** Monthly  
**Next Review:** January 16, 2026
