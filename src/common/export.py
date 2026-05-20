"""Report export utilities for CSV and JSON formats.

CSV exports apply spreadsheet-safe escaping to neutralize formula injection.
JSON exports preserve original values with proper encoding.
"""

import csv
import io
import json
from typing import Any, Dict, List, Sequence

# Characters that trigger formula interpretation in spreadsheet applications
# (Excel, LibreOffice Calc, Google Sheets).
FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def escape_formula(value: Any) -> str:
    """Escape a value for safe inclusion in spreadsheet-oriented CSV exports.

    Prefixes the cell with a single quote when the string representation
    starts with a character that spreadsheet tools interpret as a formula.
    Non-string values are converted to their string representation first.

    Returns the escaped string suitable for CSV writing.
    """
    text = str(value) if not isinstance(value, str) else value
    if text and text[0] in FORMULA_PREFIXES:
        return f"'{text}"
    return text


def export_csv(rows: Sequence[Dict[str, Any]], fields: List[str]) -> str:
    """Export rows as CSV with formula-safe escaping.

    Args:
        rows: Sequence of dictionaries representing data rows.
        fields: Ordered list of field names to include as columns.

    Returns:
        CSV-formatted string with escaped formula characters.
    """
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

    # Header row (field names are trusted, but escape defensively)
    writer.writerow([escape_formula(f) for f in fields])

    # Data rows
    for row in rows:
        writer.writerow([escape_formula(row.get(f, "")) for f in fields])

    return output.getvalue()


def export_json(rows: Sequence[Dict[str, Any]], fields: List[str]) -> str:
    """Export rows as JSON preserving original values.

    Args:
        rows: Sequence of dictionaries representing data rows.
        fields: Ordered list of field names to include.

    Returns:
        JSON-formatted string with original (unescaped) values.
    """
    filtered = [{f: row.get(f) for f in fields} for row in rows]
    return json.dumps(filtered, ensure_ascii=False, indent=2)
