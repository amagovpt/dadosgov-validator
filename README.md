# Excel Validator API

A Flask + Celery + Redis backend for validating tabular Excel datasets against a set of rules.

## Project Structure

```
excel_validator/
├── app/
│   ├── __init__.py          # App factory + Celery setup
│   ├── config.py            # Configuration (reads from .env)
│   ├── routes/
│   │   └── validation.py    # POST /validate, GET /results/<job_id>
│   ├── tasks/
│   │   └── validation_task.py  # Celery task
│   ├── validators/
│   │   ├── engine.py        # Orchestrates rule execution (plug your code in here)
│   │   └── rules.py         # Sample built-in rule implementations
│   └── utils/
│       └── file_handler.py  # File upload helpers
├── tests/
│   └── test_engine.py       # Pytest tests for the validation engine
├── uploads/                 # Temp storage for uploaded files (auto-created)
├── .env                     # Environment variables
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── run.py                   # Flask app entrypoint
```

---

## Quickstart

### With Docker (recommended)

```bash
docker-compose up --build
```

That's it. Flask runs on `http://localhost:5000`.

### Without Docker

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start Redis (must be running separately)
redis-server

# 3. Start Flask
flask run

# 4. Start Celery worker (in a separate terminal)
celery -A run.celery worker --loglevel=info
```

---

## API Usage

### POST /api/validate

Submit an Excel file and a list of rules.

```bash
curl -X POST http://localhost:5000/api/validate \
  -F "file=@your_dataset.xlsx" \
  -F 'rules=[
    {"type": "not_null",       "column": "Name"},
    {"type": "min_value",      "column": "Score",  "value": 0},
    {"type": "max_value",      "column": "Score",  "value": 100},
    {"type": "allowed_values", "column": "Status", "values": ["active", "inactive"]},
    {"type": "unique",         "column": "ID"}
  ]'
```

**Response:**
```json
{
  "job_id": "abc123",
  "status": "queued",
  "poll_url": "/api/results/abc123"
}
```

### GET /api/results/{job_id}

Poll for results using the `job_id` returned above.

```bash
curl http://localhost:5000/api/results/abc123
```

**Response (when complete):**
```json
{
  "job_id": "abc123",
  "status": "success",
  "result": {
    "total_rules": 3,
    "passed": 2,
    "failed": 1,
    "results": [
      {"rule": {"type": "not_null", "column": "Name"}, "passed": true,  "failures": []},
      {"rule": {"type": "min_value", ...},              "passed": false, "failures": [{"row": 4, "column": "Score", "value": -1, "message": "..."}]},
      {"rule": {"type": "unique", "column": "ID"},      "passed": true,  "failures": []}
    ]
  }
}
```

---

## Plugging in Your Existing Validators

Open `app/validators/engine.py`. At the top you will find the `RULE_REGISTRY` dict:

```python
RULE_REGISTRY = {
    "not_null":       validate_not_null,
    "min_value":      validate_min_value,
    ...
}
```

Replace or extend these with your own functions. Each function must follow this signature:

```python
def my_validator(df: pd.DataFrame, rule: dict) -> list:
    # Return a list of failure dicts (empty = all rows passed)
    ...
```

If your validators live in another package, install it in editable mode and import directly:

```bash
pip install -e ../your_validation_project
```

```python
# engine.py
from your_validation_package import validate_not_null, validate_my_custom_rule
```

---

## Running Tests

```bash
pytest tests/
```
