# Data Engineer Dev Assignment — Azure Medallion Data Product

Thin medallion pipeline that ingests university chapter data from a public ArcGIS FeatureServer API, applies data quality rules, and publishes a consumer-facing Gold data product.

## What this solution covers

- Azure-style Bronze / Silver / Gold lake layout
- Python ingestion from public ArcGIS REST API
- PySpark transforms for Silver and Gold
- CA / OR / WA filtering only
- Required published attributes:
  - `chapter_id`
  - `chapter_name`
  - `city`
  - `state`
  - `longitude`
  - `latitude`
- Required DQ behaviors:
  - `DQ-Q1` hard-fail quarantine for invalid coordinates
  - `DQ-W1` warn-and-pass for missing / blank / UNKNOWN city
- Quarantine output separated from Gold output
- Run-level metrics logging
- Tests proving quarantined rows do not appear in Gold and warned rows do

## Tech choices

- **Ingest**: Python `requests`
- **Transform / publish**: PySpark
- **Storage**: local filesystem with ADLS-style paths
- **Format**: JSON in Bronze, Parquet in Silver/Gold/Quarantine

This is intentionally local-first so a reviewer can clone and run it without needing Azure credentials or cloud provisioning.

## Repository structure

```text
.
├── src/
│   ├── pipeline.py
│   ├── ingest.py
│   ├── transform_silver.py
│   ├── publish_gold.py
│   ├── dq.py
│   └── utils.py
├── tests/
│   └── test_dq_rules.py
├── docs/
│   ├── architecture.md
│   └── data_product_contract.md
├── fixtures/
│   └── synthetic_bad_rows.json
├── data/
│   ├── bronze/
│   ├── silver/
│   ├── gold/
│   └── quarantine/
└── requirements.txt
```

## Run instructions

### 1. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the pipeline

```bash
python -m src.pipeline
```

This will:
- call the public ArcGIS API
- filter to CA / OR / WA
- append synthetic fixture rows so both DQ paths are visible
- write Bronze raw payload by run id
- create Silver cleaned records
- write Quarantine rows for `DQ-Q1`
- publish Gold `v1`
- log `rows_in`, `rows_quarantined`, `rows_warned`, `rows_ok`

### 3. Run tests

```bash
pytest -q
```

## Output layout

Suggested medallion layout from the assignment is preserved:

```text
data/bronze/university_chapters/<run_id>/
data/silver/university_chapters/
data/gold/university_chapters/v1/
data/quarantine/university_chapters/<run_id>/
```

## DQ behavior

### DQ-Q1 — Quarantine (hard fail)

Fail when longitude or latitude is missing, null, non-numeric, or outside valid ranges:
- longitude must be in `[-180, 180]`
- latitude must be in `[-90, 90]`

Behavior:
- excluded from Silver and Gold
- written to quarantine with:
  - `dq_reason_code = INVALID_COORDINATES`
  - `ingest_run_id`
  - raw payload for debugging

### DQ-W1 — Warning (soft)

Warn when city is:
- null
- blank
- literal `UNKNOWN` (case-insensitive)

Behavior:
- row still enters Silver and Gold
- set `dq_status = 'WARNING'`
- append `MISSING_OR_UNKNOWN_CITY` to `dq_warnings`
- clean rows use `dq_status = 'OK'`

## Idempotency choice

Gold is overwritten on each run for this exercise. In production I would use Delta Lake plus `MERGE` keyed by `chapter_id` and effective load timestamp.

## Failure policy

- API errors fail the run loudly
- whole-batch empty fails the run loudly
- OR / WA empty is allowed
- CA dropping to zero is treated as an alert condition because the assignment notes CA is expected to be historically non-zero

## Trade-offs and production next steps

This solution favors reproducibility and reviewability over production completeness.

In production I would add:
- Delta Lake tables instead of plain Parquet
- schema enforcement / expectations framework
- orchestrator scheduling
- observability sinks and alerting
- historical CA baseline validation from prior successful batches
- cloud storage + managed Spark runtime
