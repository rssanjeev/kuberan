# Documentation

This directory contains project documentation for Kuberan.

## 📚 Main Documentation (`.github/docs/`)

For comprehensive project documentation, see **[.github/docs/](../.github/docs/)**:

- **[ARCHITECTURE.md](../.github/docs/ARCHITECTURE.md)** - System design, layers, design patterns
- **[DOMAINS.md](../.github/docs/DOMAINS.md)** - Stock Tracker, Financier, and ETF Analysis domains
- **[SECURITY.md](../.github/docs/SECURITY.md)** - **CRITICAL** for financial data handling
- **[LOGGING.md](../.github/docs/LOGGING.md)** - Structured logging standards
- **[STYLE_GUIDE.md](../.github/docs/STYLE_GUIDE.md)** - Code style and conventions
- **[TECH_STACK.md](../.github/docs/TECH_STACK.md)** - Technologies, dependencies, versions
- **[WORKFLOWS.md](../.github/docs/WORKFLOWS.md)** - Development commands and workflows
- **[WEB_SCRAPING.md](../.github/docs/WEB_SCRAPING.md)** - MCP servers and data extraction

## 📄 Files in This Directory

### [API.md](./API.md)
REST API endpoint documentation including request/response formats, parameters, and examples for all domains:
- Stock Tracker endpoints
- Financier endpoints
- ETF Analysis endpoints (67 endpoints)
- System management and monitoring endpoints
- Authentication endpoints

**Last Updated:** November 30, 2025

### [Kuberan_API_Collection.json](./Kuberan_API_Collection.json)
Complete Postman API collection with all endpoints organized by domain and HTTP method. Import into Postman for testing.

**Last Updated:** November 28, 2025

### Technical Architecture Documents

- **[MULTI_PROVIDER_ARCHITECTURE.md](./MULTI_PROVIDER_ARCHITECTURE.md)** - Multi-provider data layer design
- **[MASSIVE_PROVIDER_IMPACT.md](./MASSIVE_PROVIDER_IMPACT.md)** - Polygon.io integration and foundation metadata
- **[PROVIDER_METADATA_COMPARISON.md](./PROVIDER_METADATA_COMPARISON.md)** - Provider capability comparison
- **[ALPHA_VANTAGE_PREMIUM_STRATEGY.md](./ALPHA_VANTAGE_PREMIUM_STRATEGY.md)** - Alpha Vantage usage strategy

### ETF Domain Documentation

- **[ETF_IMPLEMENTATION_PLAN.md](./ETF_IMPLEMENTATION_PLAN.md)** - Comprehensive ETF feature roadmap

### Monitoring & Metrics

- **[API_METRICS_TRACKING.md](./API_METRICS_TRACKING.md)** - API call tracking and monitoring
- **[METRICS_INTEGRATION_GUIDE.md](./METRICS_INTEGRATION_GUIDE.md)** - Metrics integration patterns
- **[QUERYING_API_METRICS.md](./QUERYING_API_METRICS.md)** - Query examples for metrics data
- **[ADAPTIVE_RATE_LIMITING.md](./ADAPTIVE_RATE_LIMITING.md)** - Rate limiting strategies

### Domain-Specific

- **[FINANCIAL_DOCUMENTS.md](./FINANCIAL_DOCUMENTS.md)** - Financier domain credit card processing
- **[ALPHA_VANTAGE_COMPLETE_PLAN.md](./ALPHA_VANTAGE_COMPLETE_PLAN.md)** - Alpha Vantage integration plan

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

**Documentation Structure Last Updated:** November 30, 2025
