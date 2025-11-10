# API Documentation (OpenAPI)

This backend uses FastAPI, which automatically generates interactive API documentation.

## Interactive Docs

- **Swagger UI:**
  - Run the backend (`uvicorn app.main:app --reload`)
  - Visit: [http://localhost:8000/docs](http://localhost:8000/docs)

- **ReDoc:**
  - Visit: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## OpenAPI Spec

- The OpenAPI (Swagger) JSON is available at:
  - [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

## Example Endpoint

```
GET /
Response: { "Hello": "World" }
```

## How to Add More Endpoints

- Define new routes in `backend/app/main.py` or additional modules.
- Use FastAPI's type hints and docstrings for automatic docs.

See [FastAPI docs](https://fastapi.tiangolo.com/tutorial/first-steps/) for more info.
