# backend-dataset-validation

A Flask + Celery + Redis + PostgreSQL service for **asynchronous dataset preprocessing and rule-based validation**. Built to run entirely via Docker Compose — no local Python environment or manual runtime commands required.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Getting Started](#getting-started)
3. [Environment Variables](#environment-variables)
4. [Project Structure](#project-structure)
5. [Data Flow](#data-flow)
6. [Database Models](#database-models)
7. [Validation Rules Reference](#validation-rules-reference)
8. [API Reference](#api-reference)
9. [Adding New Validation Rules](#adding-new-validation-rules)
10. [Redis / In-Memory DataFrame Store](#redis--in-memory-dataframe-store)
11. [Celery Tasks](#celery-tasks)
12. [Running Tests](#running-tests)
13. [Known Limitations & Notes](#known-limitations--notes)

---

## Architecture Overview

```
Client
  │
  ▼
Flask API (port 5000)
  │
  ├─ Writes jobs to ──────► Redis (port 6379)  ◄─── Celery Worker reads jobs
  │                                                        │
  ├─ Reads/writes ───────► PostgreSQL (port 5432) ◄────────┤
  │                         (PreprocessingReport,          │
  │                          ValidationReport)             │
  │                                                        │
  └─ DataFrames cached ──► Redis (serialised Parquet) ◄────┘
```

The service has **five Docker containers**:

| Container | Role |
|---|---|
| `postgres` | Persistent storage for preprocessing and validation reports |
| `redis` | Celery broker + result backend + in-memory DataFrame store |
| `db-migrate` | One-shot container that runs `flask db upgrade` on startup |
| `flask` | HTTP API server (with debugpy on port 5678) |
| `celery_worker` | Background task processor (with debugpy on port 5679) |

---

## Getting Started

```bash
# Clone and start everything
git clone <repo-url>
cd backend-dataset-validation

# Copy the env file and adjust if needed
cp .env.example .env   # or edit the existing .env

docker compose up --build
```

The API will be available at `http://localhost:5000/api`.

No manual database migration or seed steps are needed — the `db-migrate` container handles that automatically.

---

## Environment Variables

All variables live in `.env`. The Docker Compose file injects service-specific overrides (e.g. `DATABASE_URL`, `REDIS_URL`) directly, so containers always connect to each other correctly regardless of what's in `.env`.

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | `dev-secret-key` | Flask secret key |
| `DATABASE_URL` | set by compose | PostgreSQL connection string |
| `REDIS_URL` | set by compose | Redis connection string |
| `UPLOAD_FOLDER` | `uploads` | Temp directory for uploaded files |
| `MAX_CONTENT_LENGTH` | `524288000` (500 MB) | Max upload size in bytes |
| `DATAFRAME_STORE_REMOVAL_TIMEOUT` | `1800` (30 min) | Seconds before an unused DataFrame is evicted from Redis |

---

## Project Structure

```
backend-dataset-validation/
├── app/
│   ├── __init__.py              # App factory: create_app(), Celery setup
│   ├── config.py                # All configuration via environment variables
│   ├── models/
│   │   ├── preprocessing_report.py   # DB model for preprocessing jobs
│   │   ├── validation_report.py      # DB model for validation jobs
│   │   └── task_status.py            # Enum: QUEUED | STARTED | SUCCESS | FAILURE
│   ├── routes/
│   │   └── validation.py        # All HTTP endpoints (Blueprint: /api)
│   ├── tasks/
│   │   ├── preprocessing_tasks.py    # Celery task: load & preprocess a file
│   │   └── validation_task.py        # Celery task: run validation rules
│   ├── utils/
│   │   ├── dataframe_processing.py   # Load/get/remove DataFrames; column introspection
│   │   ├── redis_store.py            # Low-level Redis serialisation (Parquet via pyarrow)
│   │   └── file_handler.py           # Upload save/delete helpers
│   └── validators/
│       ├── engine.py            # run_rules(): dispatches rules to functions
│       ├── rules.py             # All rule implementations
│       └── descriptions.py      # Machine-readable rule metadata (used by /available_rules)
├── migrations/                  # Alembic migration files
├── tests/
│   └── test_engine.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── run.py                       # Entrypoint; exposes `celery` for the worker command
```

---

## Data Flow

### Preprocessing (uploading a dataset)

```
POST /api/preprocess
  │
  ├── Save file to disk (uploads/)
  ├── Generate dataframe_id (UUID)
  ├── Create PreprocessingReport (status=QUEUED) in PostgreSQL
  └── Dispatch Celery task: preprocess_dataset(file_path, dataframe_id)
         │
         ├── Load file into pandas DataFrame
         ├── Serialise DataFrame → Redis (key: dataframe_<id>)
         ├── Delete temp file from disk
         ├── Extract column names + presumed types
         ├── Update PreprocessingReport (status=SUCCESS, results)
         └── Schedule remove_dataframe_if_still_stored (after DATAFRAME_STORE_REMOVAL_TIMEOUT)

Client polls: GET /api/preprocessing_results/<job_id>
```

### Validation (running rules against datasets)

```
POST /api/validate?datasets=...&rules=...
  │
  ├── Validate all dataframe_ids exist in Redis
  ├── Validate all preprocessing_report_ids exist in PostgreSQL
  ├── Create ValidationReport (status=QUEUED) in PostgreSQL
  └── Dispatch Celery task: run_validation(dataframe_ids, rules)
         │
         ├── Load all DataFrames from Redis into a local dict
         ├── For each rule: look up validator fn in RULE_REGISTRY
         ├── Call validator fn with the relevant DataFrames and rule params
         ├── Compile results dict
         └── Update ValidationReport (status=SUCCESS, report_result, passed)

Client polls: GET /api/validation_results/<job_id>
```

---

## Database Models

### `PreprocessingReport`

| Column | Type | Description |
|---|---|---|
| `id` | Integer PK | |
| `dadosgov_dataset_id` | String(64) | Dados.gov dataset identifier provided by the client |
| `dataframe_id` | String(64) | UUID assigned to the in-memory DataFrame |
| `job_id` | String(64) | Celery task ID |
| `status` | Enum | `queued` / `started` / `success` / `failure` |
| `original_filename` | String(255) | Original uploaded filename |
| `column_names` | JSON | List of column names detected after loading |
| `presumed_column_types` | JSON | Dict mapping column → `{dtype_raw, display_name}` |
| `error_message` | Text | Set only on failure |
| `created_at` | DateTime | |
| `completed_at` | DateTime | |

### `ValidationReport`

| Column | Type | Description |
|---|---|---|
| `id` | Integer PK | |
| `job_id` | String(64) | Celery task ID |
| `preprocessing_report_ids` | JSON | List of PreprocessingReport IDs included in this run |
| `status` | Enum | `queued` / `started` / `success` / `failure` |
| `rules_applied` | JSON | The rules array sent by the client |
| `report_result` | JSON | Full output from `run_rules()` |
| `passed` | Boolean | Top-level pass/fail (True only if every rule passed) |
| `error_message` | Text | Set only on failure |
| `created_at` | DateTime | |
| `completed_at` | DateTime | |

---

## Validation Rules Reference

All rules are passed as a JSON array to `POST /api/validate`. Each rule object **must** include a `type` field and a `dataframe_ids` array. Additional fields depend on the rule type.

The list of available rules with their parameter schemas can be fetched at runtime from `GET /api/available_rules`.

### Common structure

```json
{
  "type": "<rule_type>",
  "dataframe_ids": ["<dataframe_id_1>"],
  "column": "ColumnName",
  ... other rule-specific params
}
```

### Rules that operate on a single dataset

| Rule type | Required params | Optional params | Description |
|---|---|---|---|
| `test_not_null` | `column` | — | Fails rows where the column is null/NaN |
| `test_unique_generic` | `columns` (array) | — | Fails rows where the combination of columns is duplicated |
| `test_length_max` | `column`, `max_length` | — | Fails rows where string length exceeds `max_length` (numerics have `.` stripped before counting) |
| `test_length_min` | `column`, `min_length` | — | Fails rows where string length is below `min_length` |
| `test_length_exact` | `column`, `exact_length` | — | Fails rows where string length differs from `exact_length` |
| `test_possible_values` | `column`, `possible_values` (array) | — | Fails non-null rows whose value is not in the allowed set (comparison is string-based) |
| `test_percentage_max_decimal_places` | `column`, `max_decimal_places` | — | Fails rows with more decimal places than allowed |
| `test_domains_numeric` | `column` | `min_value`, `max_value` | Fails rows outside the `[min_value, max_value]` range. At least one bound must be provided |
| `test_one_to_one_columns` | `column1`, `column2` | — | Fails if the two columns do not have a strict 1-to-1 relationship |

### Rules that operate on multiple datasets

| Rule type | Datasets | Required params | Description |
|---|---|---|---|
| `test_boundaries_extended_table_coherence` | 2 (base, extended) | `base_column`, `extended_column` | Checks that every value in `base_column` (dataset 1) exists in `extended_column` (dataset 2) |
| `test_domains_only_one_value_across_datasets` | ≥ 2 | `base_column`, `extended_columns` | The first dataset's column must contain exactly one unique non-null value; all other datasets must contain only that value in their respective columns |

---

## API Reference

Base path: `/api`

All endpoints that accept parameters do so via query string (GET) or multipart form data / query string (POST).

---

### `GET /api/available_rules`

Returns the machine-readable metadata for all registered validation rules.

**Response `200`**
```json
{
  "rules": [
    {
      "id": "test_not_null",
      "display_name": "Columna não nula",
      "description": "...",
      "parameters": {
        "dataset_parameters": {
          "amount_of_datasets": "1",
          "dataset_descriptions": { "dataset1": "..." }
        },
        "validation_parameters": {
          "column": { "type": "string", "required": true, "description": "..." }
        }
      }
    },
    ...
  ]
}
```

---

### `POST /api/preprocess`

Uploads a dataset file and starts asynchronous preprocessing.

**Request** — `multipart/form-data`

| Field | Type | Required | Description |
|---|---|---|---|
| `file` | File | Yes | `.xlsx`, `.xls`, or `.csv` |
| `dadosgov_dataset_id` | String | Yes | The Dados.gov identifier for this dataset |

**Response `200`**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "dataframe_id": "ed0f871e-122d-45ad-bd16-f89d2e10545d",
  "preprocessing_report_id": 42,
  "status": "queued",
  "poll_url": "/api/results/550e8400-..."
}
```

**Errors**

| Status | Condition |
|---|---|
| `400` | No file, empty filename, unsupported file type, or missing `dadosgov_dataset_id` |

---

### `GET /api/preprocessing_results/<job_id>`

Polls the status of a preprocessing job.

**Response `202`** (still processing)
```json
{ "job_id": "...", "status": "queued" }
```
or
```json
{ "job_id": "...", "status": "started" }
```

**Response `200`** (complete)
```json
{
  "job_id": "...",
  "status": "success",
  "result": {
    "column_names": ["Age", "Name", "Score"],
    "presumed_column_types": {
      "Age":   { "dtype_raw": "int64",   "display_name": "Número inteiro" },
      "Name":  { "dtype_raw": "object",  "display_name": "Não identificado" },
      "Score": { "dtype_raw": "float64", "display_name": "Número real" }
    }
  }
}
```

**Response `500`** (failed)
```json
{ "job_id": "...", "status": "failure", "error": "Something went wrong" }
```

**Errors**

| Status | Condition |
|---|---|
| `400` | `job_id` not found |

---

### `POST /api/validate`

Starts an asynchronous validation run over one or more preprocessed datasets.

**Request** — query string parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `datasets` | JSON string | Yes | Object mapping `dataframe_id` → `preprocessing_report_id` |
| `rules` | JSON string | Yes | Array of rule objects (see Validation Rules Reference) |

**Example**
```
POST /api/validate
  ?datasets={"ed0f871e-...":"42","b3c1f902-...":"43"}
  &rules=[{"type":"test_not_null","dataframe_ids":["ed0f871e-..."],"column":"Age"}]
```

**Response `202`**
```json
{
  "job_id": "77a4c579-...",
  "status": "queued",
  "poll_url": "/api/results/77a4c579-..."
}
```

**Errors**

| Status | Condition |
|---|---|
| `400` | Missing or malformed `datasets` or `rules`; any dataframe not found in store; any preprocessing report not found |

---

### `GET /api/validation_results/<job_id>`

Polls the status of a validation job.

**Response `202`** (still processing)
```json
{ "job_id": "...", "status": "queued" }
```

**Response `200`** (complete)
```json
{
  "job_id": "...",
  "status": "success",
  "result": {
    "total_rules": 3,
    "passed": 2,
    "failed": 1,
    "execution_time_seconds": 0.42,
    "results": [
      {
        "rule": { "type": "test_not_null", "dataframe_ids": ["ed0f871e-..."], "column": "Age" },
        "passed": true,
        "failures": []
      },
      {
        "rule": { "type": "test_domains_numeric", "dataframe_ids": ["ed0f871e-..."], "column": "Score", "min_value": 0 },
        "passed": false,
        "failures": [
          { "row": 4,  "column": "Score", "value": -1, "message": "O valor está fora do intervalo permitido" },
          { "row": 17, "column": "Score", "value": -4, "message": "O valor está fora do intervalo permitido" }
        ]
      }
    ]
  }
}
```

**Response `500`** (failed)
```json
{ "job_id": "...", "status": "failure", "error": "..." }
```

---

### `GET /api/tmp_get_current_dataframe_store`

> ⚠️ **Temporary / debug endpoint.** Returns the list of dataframe IDs currently held in Redis. Not intended for production use.

---

## Adding New Validation Rules

1. **Implement the function** in `app/validators/rules.py`:

```python
def test_my_rule(df_list: list, rule: dict) -> list:
    """Short description."""
    assert len(df_list) == 1, "test_my_rule expects exactly one dataset"
    df = df_list[0]

    column = _require_column(df, rule)
    failures = []

    for idx, value in df[column].items():
        if <your_condition>:
            failures.append({
                "row": int(idx),
                "column": column,
                "value": value,
                "message": "Human-readable failure reason"
            })

    return failures
```

2. **Register it** in `app/validators/engine.py`:

```python
from app.validators.rules import test_my_rule

RULE_REGISTRY: dict = {
    ...
    'test_my_rule': test_my_rule,
}
```

3. **Add metadata** to `app/validators/descriptions.py` so it appears in `GET /api/available_rules`.

---

## Redis / In-Memory DataFrame Store

DataFrames are serialised to Parquet (via `pyarrow`) and stored in Redis under the key `dataframe_<id>`.

They are **automatically evicted** after `DATAFRAME_STORE_REMOVAL_TIMEOUT` seconds (default: 30 minutes), via a scheduled Celery task. Eviction also happens immediately after a validation run completes for the datasets that were used.

If a validation request is made and the dataframe is no longer in Redis (evicted or not yet ready), the `/validate` endpoint returns a `400` error — the client should re-upload and preprocess the file.

---

## Celery Tasks

| Task name | Defined in | Triggered by |
|---|---|---|
| `dataset_store_tasks.preprocess_dataset` | `preprocessing_tasks.py` | `POST /api/preprocess` |
| `dataframe_store_tasks.remove_dataframe_if_still_stored` | `preprocessing_tasks.py` | Scheduled after preprocessing completes |
| `validation_task.run_validation` | `validation_task.py` | `POST /api/validate` |

All tasks update the corresponding DB report row (`status`, `completed_at`, `error_message`) on both success and failure. On failure they re-raise the exception so Celery can handle retries (max 3 retries, 5-second delay).

---

## Running Tests

```bash
docker compose run --rm flask pytest
```

Tests live in `tests/`. `conftest.py` at the root sets up the Flask test client and an in-memory SQLite database.

---

## Known Limitations & Notes

- **DataFrames are ephemeral.** They live in Redis only for `DATAFRAME_STORE_REMOVAL_TIMEOUT`. If that window passes before the client calls `/validate`, the file must be re-uploaded.
- **`/validate` uses query-string parameters**, not form body, for `datasets` and `rules`. This is unconventional for a POST endpoint but is the current design.
- **No authentication.** All endpoints are publicly accessible. Add auth middleware before exposing to production.