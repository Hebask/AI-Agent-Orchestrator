# Testing Strategy

This project includes automated test cases to validate the correctness and stability of the API endpoints.
Tests are written using `pytest` and FastAPI’s `TestClient`.

The goal of testing is to ensure:
- Core endpoints are reachable
- Request validation works as expected
- Responses follow the documented API contract
- The orchestrator pipeline runs without crashing

---

## Test Coverage

The following endpoints are covered:

| Test File         | Endpoint Tested         | Purpose                              |
|-------------------|--------------------------|--------------------------------------|
| test_health.py    | GET /health              | Service availability and config      |
| test_ask.py       | POST /ask                | AI orchestrator pipeline             |
| test_files.py     | POST /files/upload       | File upload and ingestion            |
| test_runs.py      | GET /runs, GET /runs/{id}| Workflow run tracking                |

---

## How to Run Tests

Activate your virtual environment first:

```bash
venv\Scripts\activate
```

Then run:

```bash
pytest -v
```

Example Output
==================== test session starts ====================
collected 6 items

tests/test_health.py ....        [100%]
tests/test_ask.py ....           [100%]
tests/test_files.py ...          [100%]
tests/test_runs.py ..            [100%]

==================== 13 passed in 4.21s =====================

# Test Design Principles

Each endpoint has at least one positive test case

Invalid input scenarios are tested when applicable

Tests do not depend on external services (LLMs and embeddings can be mocked if required)

Tests are deterministic and reproducible

# Continuous Validation

## Tests should be executed:

Before committing code

Before pushing to GitHub

Before final project submission

This ensures the backend behaves consistently and matches the documented API specification.
