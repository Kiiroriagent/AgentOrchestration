"""Tests for CSV and JSON report export with formula escaping."""

import csv
import io
import json

import pytest

from src.common.export import escape_formula, export_csv, export_json, FORMULA_PREFIXES


class TestEscapeFormula:
    """Tests for the escape_formula helper."""

    @pytest.mark.parametrize("char", list("=+-@\t\r"))
    def test_escapes_formula_prefix_characters(self, char):
        value = f"{char}SUM(A1:A10)"
        result = escape_formula(value)
        assert result == f"'{char}SUM(A1:A10)"
        assert not result.startswith(char)

    def test_preserves_normal_text(self):
        assert escape_formula("hello world") == "hello world"

    def test_preserves_empty_string(self):
        assert escape_formula("") == ""

    def test_preserves_numeric_string(self):
        assert escape_formula("12345") == "12345"

    def test_escapes_equals_sign(self):
        assert escape_formula("=CMD('calc')") == "'=CMD('calc')"

    def test_escapes_plus_sign(self):
        assert escape_formula("+1234") == "'+1234"

    def test_escapes_minus_sign(self):
        assert escape_formula("-1234") == "'-1234"

    def test_escapes_at_sign(self):
        assert escape_formula("@SUM(A1)") == "'@SUM(A1)"

    def test_escapes_tab_character(self):
        assert escape_formula("\t=payload") == "'\t=payload"

    def test_escapes_carriage_return(self):
        assert escape_formula("\r=payload") == "'\r=payload"

    def test_converts_non_string_to_string(self):
        assert escape_formula(42) == "42"
        assert escape_formula(None) == "None"

    def test_escapes_negative_number_as_string(self):
        # When a numeric value is passed as string, it gets escaped
        assert escape_formula("-500") == "'-500"

    def test_preserves_negative_number_as_int(self):
        # int -500 converts to "-500" which starts with "-"
        result = escape_formula(-500)
        assert result == "'-500"


class TestExportCsv:
    """Tests for CSV export with formula escaping."""

    def test_basic_export(self):
        rows = [
            {"name": "Alice", "email": "alice@example.com"},
            {"name": "Bob", "email": "bob@example.com"},
        ]
        result = export_csv(rows, ["name", "email"])
        reader = csv.reader(io.StringIO(result))
        lines = list(reader)
        assert lines[0] == ["name", "email"]
        assert lines[1] == ["Alice", "alice@example.com"]
        assert lines[2] == ["Bob", "bob@example.com"]

    def test_escapes_formula_in_data(self):
        rows = [{"name": "=HYPERLINK(\"http://evil.com\")", "value": "safe"}]
        result = export_csv(rows, ["name", "value"])
        reader = csv.reader(io.StringIO(result))
        lines = list(reader)
        assert lines[1][0] == "'=HYPERLINK(\"http://evil.com\")"
        assert lines[1][1] == "safe"

    def test_escapes_multiple_formula_characters(self):
        rows = [
            {"a": "=cmd", "b": "+cmd", "c": "-cmd", "d": "@cmd"},
        ]
        result = export_csv(rows, ["a", "b", "c", "d"])
        reader = csv.reader(io.StringIO(result))
        lines = list(reader)
        assert lines[1] == ["'=cmd", "'+cmd", "'-cmd", "'@cmd"]

    def test_handles_missing_fields(self):
        rows = [{"name": "Alice"}]
        result = export_csv(rows, ["name", "missing_field"])
        reader = csv.reader(io.StringIO(result))
        lines = list(reader)
        assert lines[1] == ["Alice", ""]

    def test_empty_rows(self):
        result = export_csv([], ["name", "email"])
        reader = csv.reader(io.StringIO(result))
        lines = list(reader)
        assert len(lines) == 1  # header only
        assert lines[0] == ["name", "email"]


class TestExportJson:
    """Tests for JSON export preserving original values."""

    def test_preserves_formula_characters(self):
        rows = [{"name": "=SUM(A1)", "value": "+100"}]
        result = export_json(rows, ["name", "value"])
        data = json.loads(result)
        assert data[0]["name"] == "=SUM(A1)"
        assert data[0]["value"] == "+100"

    def test_filters_to_specified_fields(self):
        rows = [{"name": "Alice", "secret": "password", "email": "a@b.com"}]
        result = export_json(rows, ["name", "email"])
        data = json.loads(result)
        assert "secret" not in data[0]
        assert data[0]["name"] == "Alice"
        assert data[0]["email"] == "a@b.com"

    def test_handles_none_values(self):
        rows = [{"name": "Alice", "email": None}]
        result = export_json(rows, ["name", "email"])
        data = json.loads(result)
        assert data[0]["email"] is None

    def test_empty_rows(self):
        result = export_json([], ["name"])
        data = json.loads(result)
        assert data == []
