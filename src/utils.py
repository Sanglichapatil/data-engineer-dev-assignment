from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
BRONZE_DIR = DATA_DIR / "bronze" / "university_chapters"
SILVER_DIR = DATA_DIR / "silver" / "university_chapters"
GOLD_DIR = DATA_DIR / "gold" / "university_chapters" / "v1"
QUARANTINE_DIR = DATA_DIR / "quarantine" / "university_chapters"
FIXTURES_FILE = BASE_DIR / "fixtures" / "synthetic_bad_rows.json"


def utc_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def ensure_dirs() -> None:
    for path in [BRONZE_DIR, SILVER_DIR, GOLD_DIR, QUARANTINE_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def read_fixture_rows() -> list[dict]:
    with open(FIXTURES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
