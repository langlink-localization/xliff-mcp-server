"""Pytest coverage for core tool behavior."""

from __future__ import annotations

import csv
import io
import json

from xliff_mcp.server import (
    export_tmx_file,
    export_xliff_file,
    get_server_info,
    process_tmx,
    process_xliff,
    process_xliff_with_tags,
    replace_xliff_targets,
    validate_tmx,
    validate_xliff,
)
from xliff_mcp.xliff_processor import XliffProcessorService
from tests.samples import SAMPLE_TMX, SAMPLE_XLIFF, SDL_XLIFF


def test_process_xliff_extracts_units_and_languages() -> None:
    result = json.loads(process_xliff("sample.xliff", SAMPLE_XLIFF))

    assert result["success"] is True
    assert result["message"] == "Successfully processed 2 translation units"
    assert [unit["unitId"] for unit in result["data"]] == ["1", "2"]
    assert result["data"][0]["srcLang"] == "en"
    assert result["data"][0]["tgtLang"] == "zh"


def test_process_xliff_with_tags_preserves_inline_markup() -> None:
    result = json.loads(process_xliff_with_tags("sample.xliff", SAMPLE_XLIFF))

    assert result["success"] is True
    assert result["data"][1]["source"] == 'This is a <g id="1">test</g> message.'


def test_validate_xliff_reports_invalid_payloads() -> None:
    result = json.loads(validate_xliff("<not-xliff>"))

    assert result["valid"] is False
    assert result["unit_count"] == 0


def test_replace_xliff_targets_updates_matching_unit() -> None:
    translations = json.dumps([
        {"unitId": "2", "aiResult": "这是一条更新后的消息。"},
    ])

    result = json.loads(replace_xliff_targets(SAMPLE_XLIFF, translations))

    assert result["success"] is True
    assert result["replacements_count"] == 1
    assert "这是一条更新后的消息。" in result["content"]


def test_export_xliff_file_generates_csv_content() -> None:
    result = json.loads(export_xliff_file("sample.xliff", SAMPLE_XLIFF, output_format="csv"))

    assert result["success"] is True
    assert result["file_name"] == "sample.csv"
    assert result["format"] == "csv"
    assert result["mime_type"] == "text/csv"
    assert result["unit_count"] == 2

    rows = list(csv.DictReader(io.StringIO(result["content"])))

    assert [row["unitId"] for row in rows] == ["1", "2"]
    assert rows[0]["srcLang"] == "en"
    assert rows[0]["tgtLang"] == "zh"


def test_export_xliff_file_generates_json_content_with_tags() -> None:
    result = json.loads(
        export_xliff_file(
            "sample.xliff",
            SAMPLE_XLIFF,
            output_format="json",
            preserve_tags=True,
        )
    )

    assert result["success"] is True
    assert result["file_name"] == "sample.json"
    assert result["format"] == "json"
    assert result["mime_type"] == "application/json"

    payload = json.loads(result["content"])

    assert len(payload) == 2
    assert payload[1]["source"] == 'This is a <g id="1">test</g> message.'


def test_process_tmx_extracts_language_metadata() -> None:
    result = json.loads(process_tmx("memory.tmx", SAMPLE_TMX))

    assert result["success"] is True
    assert len(result["data"]) == 1
    assert result["data"][0]["srcLang"] == "en"
    assert result["data"][0]["tgtLang"] == "zh"


def test_validate_tmx_returns_unit_count() -> None:
    result = json.loads(validate_tmx(SAMPLE_TMX))

    assert result["valid"] is True
    assert result["unit_count"] == 1


def test_export_tmx_file_generates_json_content() -> None:
    result = json.loads(export_tmx_file("memory.tmx", SAMPLE_TMX, output_format="json"))

    assert result["success"] is True
    assert result["file_name"] == "memory.json"
    assert result["format"] == "json"
    assert result["mime_type"] == "application/json"
    assert result["unit_count"] == 1

    payload = json.loads(result["content"])

    assert payload[0]["fileName"] == "memory.tmx"
    assert payload[0]["srcLang"] == "en"
    assert payload[0]["tgtLang"] == "zh"


def test_export_xliff_file_rejects_unsupported_formats() -> None:
    result = json.loads(export_xliff_file("sample.xliff", SAMPLE_XLIFF, output_format="xml"))

    assert result["success"] is False
    assert "Unsupported export format" in result["message"]


def test_sdl_xliff_uses_file_level_language_metadata() -> None:
    result = XliffProcessorService.process_xliff("sample.sdlxliff", SDL_XLIFF)

    assert len(result) == 2
    assert result[0].srcLang == "en-us"
    assert result[0].tgtLang == "zh-hk"


def test_stdio_server_info_uses_current_version() -> None:
    info = json.loads(get_server_info())

    assert info["transport"] == "stdio"
    assert info["version"]
    assert "get_server_info" in info["available_tools"]
    assert "export_xliff_file" in info["available_tools"]
    assert "export_tmx_file" in info["available_tools"]
    assert "prepare_xliff_for_translation" in info["available_prompts"]
    assert "skills://catalog" in info["available_resources"]
    assert "skills://{skill_name}" in info["available_resource_templates"]
    assert any(
        skill["name"] == "translate_xliff_with_tags"
        for skill in info["available_skills"]
    )
