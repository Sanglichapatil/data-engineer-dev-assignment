from __future__ import annotations

import requests

from .utils import BRONZE_DIR, ensure_dirs, read_fixture_rows, utc_run_id, write_json

API_URL = "https://services2.arcgis.com/5I7u4SJE1vUr79JC/arcgis/rest/services/UniversityChapters_Public/FeatureServer/0/query"


def fetch_api_rows() -> dict:
    params = {
        "where": "State IN ('CA','OR','WA')",
        "outFields": "*",
        "returnGeometry": "true",
        "f": "json",
    }
    response = requests.get(API_URL, params=params, timeout=60)
    response.raise_for_status()
    payload = response.json()
    if "features" not in payload:
        raise RuntimeError("API response missing features")
    if len(payload["features"]) == 0:
        raise RuntimeError("Whole batch is empty; refusing to publish empty Gold")
    return payload


def append_fixture_rows(payload: dict) -> dict:
    fixture_rows = read_fixture_rows()
    payload = dict(payload)
    payload["features"] = list(payload.get("features", [])) + fixture_rows
    return payload


def ingest_bronze() -> tuple[str, str]:
    ensure_dirs()
    run_id = utc_run_id()
    payload = fetch_api_rows()
    payload = append_fixture_rows(payload)
    run_dir = BRONZE_DIR / run_id
    raw_path = run_dir / "raw_payload.json"
    write_json(raw_path, payload)
    return run_id, str(raw_path)
