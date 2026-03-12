"""Utilities for generating CSV and JSON file content."""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Any, Iterable


SUPPORTED_EXPORT_FORMATS = ("csv", "json")


def export_records(
    file_name: str,
    records: Iterable[Any],
    *,
    output_format: str,
) -> dict[str, object]:
    """Generate file metadata and content for a record collection."""
    normalized_format = output_format.lower()
    if normalized_format not in SUPPORTED_EXPORT_FORMATS:
        supported_formats = ", ".join(SUPPORTED_EXPORT_FORMATS)
        raise ValueError(
            f"Unsupported export format: {output_format}. Use one of: {supported_formats}"
        )

    payload = [_normalize_record(record) for record in records]
    export_file_name = _build_export_file_name(file_name, normalized_format)

    return {
        "file_name": export_file_name,
        "format": normalized_format,
        "mime_type": _get_mime_type(normalized_format),
        "encoding": "utf-8",
        "content": _render_content(payload, normalized_format),
        "unit_count": len(payload),
    }


def _normalize_record(record: Any) -> dict[str, object]:
    if hasattr(record, "model_dump"):
        raw_record = record.model_dump()
    elif isinstance(record, dict):
        raw_record = record
    else:
        raise TypeError(f"Unsupported record type for export: {type(record)!r}")

    return {
        key: ("" if value is None else value)
        for key, value in raw_record.items()
    }


def _build_export_file_name(file_name: str, output_format: str) -> str:
    path = Path(file_name)
    stem = path.stem or path.name or "export"
    return f"{stem}.{output_format}"


def _get_mime_type(output_format: str) -> str:
    if output_format == "csv":
        return "text/csv"
    return "application/json"


def _render_content(payload: list[dict[str, object]], output_format: str) -> str:
    if output_format == "json":
        return json.dumps(payload, ensure_ascii=False, indent=2)
    return _render_csv(payload)


def _render_csv(payload: list[dict[str, object]]) -> str:
    if not payload:
        return ""

    buffer = io.StringIO()
    fieldnames = list(payload[0].keys())
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(payload)
    return buffer.getvalue()
