"""Tests for scripts/export_reminders.py — shared contract exporter."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from scripts.export_reminders import (
    infer_type,
    normalize_reminder,
    validate_schema,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SCHEMA_PATH = Path(__file__).parent.parent / "shared" / "reminder.schema.json"


# --- infer_type ---

class TestInferType:
    def test_water_from_title(self) -> None:
        assert infer_type("💧 Água", "") == "water"

    def test_water_from_message(self) -> None:
        assert infer_type("", "Você tomou água?") == "water"

    def test_water_hidrat(self) -> None:
        assert infer_type("Hidratação", "") == "water"

    def test_generic_fallback(self) -> None:
        assert infer_type("Alongamento", "Faça agora") == "generic"


# --- normalize_reminder ---

class TestNormalizeReminder:
    def test_basic(self) -> None:
        row = {
            "id": "abc-123",
            "title": "💧 Água",
            "message": "Tomou água?",
            "hour": 10,
            "minute": 30,
            "active": True,
        }
        result = normalize_reminder(row)
        assert result["id"] == "abc-123"
        assert result["hour"] == 10
        assert result["minute"] == 30
        assert result["active"] is True
        assert result["type"] == "water"

    def test_default_minute(self) -> None:
        row = {"id": "x", "title": "Test", "message": "Msg", "hour": 9, "active": True}
        result = normalize_reminder(row)
        assert result["minute"] == 0

    def test_id_preserved(self) -> None:
        row = {"id": "9bb9d43f-aaaa", "title": "T", "message": "M", "hour": 8, "active": False}
        result = normalize_reminder(row)
        assert result["id"] == "9bb9d43f-aaaa"
        assert result["active"] is False


# --- validate_schema ---

class TestValidateSchema:
    def test_valid_reminders(self) -> None:
        reminders = [
            {"id": "a", "title": "T", "message": "M", "hour": 9, "minute": 0, "active": True, "type": "water"},
        ]
        validate_schema(reminders)

    def test_missing_field_raises(self) -> None:
        reminders = [{"id": "a", "title": "T", "message": "M", "hour": 9}]
        with pytest.raises(ValueError, match="missing 'minute'"):
            validate_schema(reminders)

    def test_bad_hour_raises(self) -> None:
        reminders = [{"id": "a", "title": "T", "message": "M", "hour": 27, "minute": 0, "active": True}]
        with pytest.raises(ValueError, match="hour=27 out of range"):
            validate_schema(reminders)

    def test_bad_minute_raises(self) -> None:
        reminders = [{"id": "a", "title": "T", "message": "M", "hour": 9, "minute": 99, "active": True}]
        with pytest.raises(ValueError, match="minute=99 out of range"):
            validate_schema(reminders)

    def test_extra_field_raises(self) -> None:
        reminders = [{"id": "a", "title": "T", "message": "M", "hour": 9, "minute": 0, "active": True, "hack": 1}]
        with pytest.raises(ValueError, match="unexpected field 'hack'"):
            validate_schema(reminders)

    def test_empty_list_ok(self) -> None:
        validate_schema([])


# --- fixture validation ---

class TestFixture:
    def test_fixture_matches_schema(self) -> None:
        fixture_path = FIXTURES_DIR / "reminders.json"
        if not fixture_path.exists():
            pytest.skip("fixture not found")
        data = json.loads(fixture_path.read_text(encoding="utf-8"))
        reminders = [normalize_reminder(row) for row in data]
        validate_schema(reminders)

    def test_fixture_sorted_by_time(self) -> None:
        fixture_path = FIXTURES_DIR / "reminders.json"
        if not fixture_path.exists():
            pytest.skip("fixture not found")
        data = json.loads(fixture_path.read_text(encoding="utf-8"))
        reminders = [normalize_reminder(row) for row in data]
        hours = [(r["hour"], r["minute"]) for r in reminders]
        assert hours == sorted(hours)


# --- integration: export with fixture source ---

class TestExportFixture:
    def test_export_writes_files(self, tmp_path: Path) -> None:
        from scripts.export_reminders import load_fixture, write_output

        with patch("scripts.export_reminders.GENERATED_DIR", tmp_path / "generated"), \
             patch("scripts.export_reminders.QUICKAPP_DATA", tmp_path / "reminders.json"):
            reminders = load_fixture()
            validate_schema(reminders)
            write_output(reminders)

            gen = tmp_path / "generated" / "reminders.json"
            assert gen.exists()
            output = json.loads(gen.read_text(encoding="utf-8"))
            assert output["schemaVersion"] == 1
            assert len(output["reminders"]) == 12

            app = tmp_path / "reminders.json"
            assert app.exists()
