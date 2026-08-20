#!/usr/bin/env python3
"""Export reminders from Supabase (or fixture) to shared JSON for Vela JS Quick App."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SHARED_DIR = PROJECT_ROOT / "shared"
GENERATED_DIR = SHARED_DIR / "generated"
SCHEMA_PATH = SHARED_DIR / "reminder.schema.json"
QUICKAPP_DATA = PROJECT_ROOT / "quickapp" / "src" / "data" / "reminders.json"
FIXTURE_PATH = PROJECT_ROOT / "tests" / "fixtures" / "reminders.json"

WATER_KEYWORDS = {"agua", "água", "water", "hidrat"}


def log(msg: str) -> None:
    print(f"[REMINDERS] {msg}", file=sys.stderr)


def infer_type(title: str, message: str) -> str:
    text = (title + " " + message).lower()
    for kw in WATER_KEYWORDS:
        if kw in text:
            return "water"
    return "generic"


def normalize_reminder(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(row["id"]),
        "title": str(row["title"]),
        "message": str(row["message"]),
        "hour": int(row["hour"]),
        "minute": int(row.get("minute", 0)),
        "active": bool(row.get("active", True)),
        "type": infer_type(str(row.get("title", "")), str(row.get("message", ""))),
    }


def validate_schema(reminders: list[dict[str, Any]]) -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    required = schema["required"]
    props = schema["properties"]

    for r in reminders:
        for field in required:
            if field not in r:
                raise ValueError(f"INVALID_REMINDER_SCHEMA: missing '{field}' in {r.get('id', '?')}")

        for key, val in r.items():
            if key not in props:
                raise ValueError(f"INVALID_REMINDER_SCHEMA: unexpected field '{key}' in {r.get('id', '?')}")
            expected_type = props[key].get("type")
            if expected_type == "integer" and not isinstance(val, int):
                raise ValueError(f"INVALID_REMINDER_SCHEMA: '{key}' must be int in {r.get('id', '?')}")
            if expected_type == "boolean" and not isinstance(val, bool):
                raise ValueError(f"INVALID_REMINDER_SCHEMA: '{key}' must be bool in {r.get('id', '?')}")
            if expected_type == "string" and not isinstance(val, str):
                raise ValueError(f"INVALID_REMINDER_SCHEMA: '{key}' must be str in {r.get('id', '?')}")

        hour = r.get("hour", 0)
        minute = r.get("minute", 0)
        if not (0 <= hour <= 23):
            raise ValueError(f"INVALID_REMINDER_SCHEMA: hour={hour} out of range in {r.get('id', '?')}")
        if not (0 <= minute <= 59):
            raise ValueError(f"INVALID_REMINDER_SCHEMA: minute={minute} out of range in {r.get('id', '?')}")


def fetch_from_supabase() -> list[dict[str, Any]]:
    from dotenv import load_dotenv

    load_dotenv(PROJECT_ROOT / ".env")

    from supabase import create_client

    import os

    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "") or os.environ.get("SUPABASE_KEY", "")
    user_id = os.environ.get("DEFAULT_USER_ID", "")

    if not url or not key:
        raise SystemExit("SUPABASE_CONFIG_MISSING")

    log("Connecting to Supabase")
    client = create_client(url, key)

    query = client.table("reminders").select("*").eq("active", True)
    if user_id:
        query = query.eq("user_id", user_id)

    response = query.execute()
    rows = list(response.data or [])

    if not rows:
        log("No active reminders found")
        return []

    log(f"Found {len(rows)} active reminders")
    reminders = [normalize_reminder(row) for row in rows]
    reminders.sort(key=lambda r: (r["hour"], r["minute"]))
    return reminders


def load_fixture() -> list[dict[str, Any]]:
    if not FIXTURE_PATH.exists():
        log("No fixture file found, returning empty list")
        return []
    data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    reminders = [normalize_reminder(row) for row in data]
    reminders.sort(key=lambda r: (r["hour"], r["minute"]))
    log(f"Loaded {len(reminders)} reminders from fixture")
    return reminders


def write_output(reminders: list[dict[str, Any]]) -> None:
    output = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "reminders": reminders,
    }

    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    path = GENERATED_DIR / "reminders.json"
    path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    log(f"Exported {path}")

    QUICKAPP_DATA.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, QUICKAPP_DATA)
    log(f"Copied to {QUICKAPP_DATA}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Export reminders to shared JSON")
    parser.add_argument(
        "--source",
        choices=["supabase", "fixture"],
        default="supabase",
        help="Data source (default: supabase)",
    )
    args = parser.parse_args()

    if args.source == "fixture":
        reminders = load_fixture()
    else:
        try:
            reminders = fetch_from_supabase()
        except SystemExit:
            raise
        except Exception as exc:
            raise SystemExit(f"SUPABASE_CONNECTION_ERROR: {exc}") from exc

    if not reminders:
        log("No reminders to export, writing empty list")
        write_output([])
        log("Done")
        return

    log("Validating contracts")
    validate_schema(reminders)

    write_output(reminders)
    log("Done")


if __name__ == "__main__":
    main()
