# Documentation

This directory contains all project documentation for the Kuberan project.

## Files

### [API.md](./API.md)
Complete API endpoint documentation for the Kuberan backend. This file documents all REST API endpoints, including:
- Request/response formats
- Query parameters
- Error codes
- Example requests
- Background job schedules

**⚠️ IMPORTANT:** When modifying endpoints in `backend/app/routers/stocks.py`, update this file to keep documentation in sync.

**Last Updated:** November 11, 2025

### [refactoring-summary.md](./refactoring-summary.md)
Summary of the hybrid functional/OOP architecture refactoring that implemented:
- Centralized job scheduler
- Separation of concerns
- Core utilities extraction
- Job-based architecture for scalability

## Contributing

When adding new endpoints or modifying existing ones:

1. Update the router file: `backend/app/routers/stocks.py`
2. Update the API documentation: `docs/API.md`
3. Update the "Last Updated" date in both files
4. Test the endpoint with Postman or curl
5. Commit both changes together

This ensures the documentation always reflects the actual implementation.
