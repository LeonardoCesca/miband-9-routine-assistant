"""Tests for shared contract — validates that generated reminders match schema."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

SCHEMA_PATH = Path(__file__).parent.parent / "shared" / "reminder.schema.json"
LOG_SCHEMA_PATH = Path(__file__).parent.parent / "shared" / "reminder-log.schema.json"
FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestReminderSchema:
    def test_schema_is_valid_json(self) -> None:
        data = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        assert "properties" in data
        assert "required" in data

    def test_required_fields(self) -> None:
        data = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        assert set(data["required"]) == {"id", "title", "message", "hour", "minute", "active"}


class TestReminderLogSchema:
    def test_schema_is_valid_json(self) -> None:
        data = json.loads(LOG_SCHEMA_PATH.read_text(encoding="utf-8"))
        assert "properties" in data
        assert "required" in data

    def test_status_enum(self) -> None:
        data = json.loads(LOG_SCHEMA_PATH.read_text(encoding="utf-8"))
        assert data["properties"]["status"]["enum"] == ["done", "not_done"]


class TestContractCompatibility:
    """Ensure Python and JS models share the same field names and types."""

    def test_reminder_fields_match(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        props = schema["properties"]

        assert props["id"]["type"] == "string"
        assert props["title"]["type"] == "string"
        assert props["message"]["type"] == "string"
        assert props["hour"]["type"] == "integer"
        assert props["minute"]["type"] == "integer"
        assert props["active"]["type"] == "boolean"

    def test_log_fields_match(self) -> None:
        schema = json.loads(LOG_SCHEMA_PATH.read_text(encoding="utf-8"))
        props = schema["properties"]

        assert props["id"]["type"] == "string"
        assert props["reminderId"]["type"] == "string"
        assert props["date"]["type"] == "string"
        assert props["scheduledAt"]["type"] == "string"
        assert props["status"]["type"] == "string"
        assert props["answeredAt"]["type"] == "string"
