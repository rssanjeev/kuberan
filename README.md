# Kuberan

Financial management system with Stock Tracker, Financier, and ETF Analysis domains.

**Project Status:**
- ✅ Phase 0 (Codebase Cleanup) - COMPLETED December 2, 2025
- 🔄 Phase 1-16 (MASSIVE API Integration) - Starting Soon

**Primary Data Provider:** MASSIVE API (formerly Polygon.io)

---

## Structure

- `frontend/` — Flutter app (Web, iOS, Android)
- `backend/` — FastAPI (Python 3.14) backend with MongoDB
- `docs/` — Comprehensive project documentation
- `scripts/` — Utility and deployment scripts

## Documentation

### Quick Start
- **Architecture:** [.github/docs/ARCHITECTURE.md](.github/docs/ARCHITECTURE.md)
- **Security:** [.github/docs/SECURITY.md](.github/docs/SECURITY.md) (**CRITICAL** for financial data)
- **API Reference:** [docs/API.md](docs/API.md)
- **Development Workflows:** [.github/docs/WORKFLOWS.md](.github/docs/WORKFLOWS.md)

### MASSIVE API Integration
- **Implementation Plan:** [docs/KUBERAN_MASSIVE_IMPLEMENTATION_PLAN.md](docs/KUBERAN_MASSIVE_IMPLEMENTATION_PLAN.md)
- **Reference Endpoints Guide:** [docs/MASSIVE_REFERENCE_ENDPOINTS_GUIDE.md](docs/MASSIVE_REFERENCE_ENDPOINTS_GUIDE.md)
- **Phase 0 Audit Report:** [docs/PHASE_0_AUDIT_REPORT.md](docs/PHASE_0_AUDIT_REPORT.md)

See [docs/README.md](docs/README.md) for complete documentation index.

## Getting Started

```bash
# Start all services
docker-compose up -d

# View logs
docker logs -f kuberan-backend-1

# Access API
curl http://localhost:8000
```

For detailed setup instructions, see [.github/docs/WORKFLOWS.md](.github/docs/WORKFLOWS.md).

---

**Last Updated:** December 2, 2025
