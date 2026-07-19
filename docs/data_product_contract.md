# Data Product Contract — university_chapters_gold_v1

## 1. Name and owner

- **Product name**: `university_chapters_gold_v1`
- **Technical owner**: Data Engineering
- **Consumer use cases**:
  - chapter coverage reporting
  - west coast chapter analytics
  - mapping and geographic reporting

## 2. Interface

- **Published layer**: Gold
- **Path**: `data/gold/university_chapters/v1/`
- **Grain**: one row per university chapter (`chapter_id`)
- **Format**: Parquet

### Schema

| Column | Type | Description |
|---|---|---|
| chapter_id | string | Stable business key |
| chapter_name | string | University chapter display name |
| city | string | City from source |
| state | string | USPS state code, limited to CA/OR/WA |
| longitude | double | WGS84 longitude |
| latitude | double | WGS84 latitude |
| dq_status | string | `OK` or `WARNING` |
| dq_warnings | array<string> | Warning reason list |
| ingest_run_id | string | Batch ingestion identifier |

## 3. Freshness

- Intended SLA: refreshed daily by 06:00 UTC
- This exercise runs manually from local execution

## 4. Quality

### Row-level rules

- **DQ-Q1** quarantine when longitude / latitude is missing, null, non-numeric, or out of valid range
  - longitude must be in `[-180, 180]`
  - latitude must be in `[-90, 90]`
  - quarantined rows are written to `data/quarantine/university_chapters/<run_id>/`
  - quarantined rows never appear in Gold
- **DQ-W1** warning when `city` is null, blank, or `UNKNOWN` (case-insensitive)
  - row remains publishable
  - `dq_status = WARNING`
  - `dq_warnings` includes `MISSING_OR_UNKNOWN_CITY`

### Batch rules

- Do **not** require OR/WA row counts to be greater than zero
- Fail the run if the whole batch is empty
- Fail or alert if CA drops to zero unexpectedly

## 5. Versioning

- Published contract version is `v1`
- Breaking schema changes will publish to a new versioned path such as `v2`
- Non-breaking additions may be appended with backward-compatible documentation updates

## 6. Classification

- Source classification: public source data
- PII expectation: no PII expected
- Handling label: public
