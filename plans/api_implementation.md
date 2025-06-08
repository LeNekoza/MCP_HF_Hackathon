# 🚀 FastAPI API Implementation Plan (`src/api/`)

## 📁 Updated Directory Structure

```
/
├── app.py                        # Gradio + MCP app
└── src/
    ├── core/
    │   └── generate_sql.py       # Contains dynamic SQL helpers
    └── api/
        ├── main.py               # FastAPI app entry point
        ├── db.py                 # DB connection + query execution
        └── routes/
            └── {table}.py        # (Optional) Modular route files
```

---

## 🎯 Objective

Implement a **FastAPI-based API** under `src/api/` that provides secure, database-connected endpoints for all tables — **without modifying** the Gradio/MCP logic in `app.py`.

---

## ✅ Planned Features

### 1. `GET /api/{table}/all`

* Fetch all rows
* SQL: `SELECT * FROM {table}`

### 2. `GET /api/{table}/filter?column=...&value=...`

* Fetch rows using dynamic WHERE clause
* Validate columns via schema map
* SQL: `SELECT * FROM {table} WHERE {column} = {value}`

### 3. `GET /api/{table}/{id}`

* Fetch a single record by ID
* e.g., `GET /api/users/1`

### 4. `POST /api/{table}/`

* Insert a new record (validated JSON body)

### 5. `PUT /api/{table}/{id}`

* Update existing record by ID (partial or full)

### 6. `GET /api/{parent}/{id}/with/{child}`

* Use `JOIN` to fetch related rows
* Logic from `src/core/generate_sql.py`

---

## 🔧 Implementation Notes

* Use helpers from `src/core/generate_sql.py` to:

  * Construct SELECT / INSERT / UPDATE queries
  * Map relationships for JOINs

* Use `db.py` for:

  * Connecting to the database
  * Executing and returning query results

---
## 🔐 Security & Validation

* Sanitize all table/column inputs
* Use Pydantic models for POST/PUT validation
