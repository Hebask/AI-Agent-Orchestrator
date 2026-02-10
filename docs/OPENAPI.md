
---

## ✅ `docs/OPENAPI.md`

```md
# OpenAPI (Specification) — Export & Use

FastAPI generates an OpenAPI schema automatically from route definitions and Pydantic models.
We export it to a static file (`openapi.json`) so it can be reviewed, shared, and imported into tools.

Reference: https://swagger.io/specification/

---

## 1) Export OpenAPI to a file

From the project root:

```bash
python scripts/export_openapi.py
