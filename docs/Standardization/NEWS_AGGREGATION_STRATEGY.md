# News Aggregation Strategy

**Last Updated:** December 16, 2025  
**Status:** 🟡 Draft - Placeholder for future work  
**Purpose:** Document aggregate_union strategy for news article consolidation  
**Related Docs:**
- [DATA_PIPELINE_ARCHITECTURE.md](../DATA_PIPELINE_ARCHITECTURE.md) - Case 1: News Article Aggregation
- [DATA_STANDARDIZATION_RULES.md](DATA_STANDARDIZATION_RULES.md) - Strategy definitions

---

## Status

⏳ **Deferred**: This strategy will be implemented after completing stock price ingestion and standardization.

## Scope

This document will define:

1. **Strategy Implementation**: `aggregate_union` for news articles
2. **Deduplication Algorithm**: Title similarity + date proximity matching
3. **News Schema**: Article structure with multi-provider support
4. **Conflict Resolution**: Rules for merging duplicate articles
5. **Source Transparency**: Provider attribution for each article
6. **API Integration**: News endpoints and response formats

## Prerequisites

Before implementing news aggregation, complete:
- [ ] Stock price ingestion from all providers
- [ ] Stock metadata standardization (`single_value` strategy)
- [ ] Standardization API endpoints implementation
- [ ] Frontend display of standardized stock data

---

**Next Review:** After stock standardization implementation complete
