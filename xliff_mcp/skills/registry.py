"""Skill registration for MCP prompt and resource discovery."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from mcp.server.fastmcp import FastMCP

from .definitions import (
    SKILL_CATALOG_URI,
    SKILL_DETAIL_TEMPLATE,
    format_optional_hint,
    format_skill_catalog,
    format_skill_detail,
    get_skill,
    list_skill_names,
)


@dataclass(frozen=True)
class RegisteredSkills:
    """Exported prompt and resource callables for tests and direct imports."""

    prepare_xliff_for_translation: Callable[..., str]
    translate_xliff_with_tags: Callable[..., str]
    replace_xliff_targets_from_translations: Callable[..., str]
    inspect_tmx_translation_memory: Callable[..., str]
    skill_catalog: Callable[[], str]
    describe_skill: Callable[[str], str]


def register_skills(mcp: FastMCP) -> RegisteredSkills:
    """Register shared prompts and resources on a FastMCP instance."""

    @mcp.resource(
        SKILL_CATALOG_URI,
        name="skill_catalog",
        title="XLIFF Skill Catalog",
        description="List the reusable translation workflow skills exposed by this server.",
        mime_type="text/markdown",
    )
    def skill_catalog() -> str:
        return format_skill_catalog()

    @mcp.resource(
        SKILL_DETAIL_TEMPLATE,
        name="describe_skill",
        title="XLIFF Skill Detail",
        description="Read the details for one translation workflow skill.",
        mime_type="text/markdown",
    )
    def describe_skill(skill_name: str) -> str:
        skill = get_skill(skill_name)
        if skill is None:
            raise ValueError(
                f"Unknown skill '{skill_name}'. Available skills: {', '.join(list_skill_names())}"
            )
        return format_skill_detail(skill)

    @mcp.prompt(
        name="prepare_xliff_for_translation",
        title="Prepare XLIFF For Translation",
        description="Validate XLIFF content and extract translation-ready units.",
    )
    def prepare_xliff_for_translation(
        file_name: str = "document.xliff",
        workflow_goal: str = "translation preparation",
    ) -> str:
        return "\n".join(
            [
                "Use the XLIFF MCP Server to prepare an XLIFF file for downstream work.",
                f"File name: {file_name}",
                f"Goal: {workflow_goal}",
                "",
                "Required workflow:",
                "1. Ask for the raw XLIFF content if it has not been supplied yet.",
                "2. Call `validate_xliff` with the raw content. If validation fails, stop and explain the failure.",
                f"3. Call `process_xliff` with `file_name={file_name}` and the same raw content.",
                "4. Summarize source language, target language, segment count, and any units with empty targets.",
                "5. Return a translation-ready list keyed by `unitId` and `segNumber`.",
                "6. Do not rewrite XML or invent translations in this skill.",
            ]
        )

    @mcp.prompt(
        name="translate_xliff_with_tags",
        title="Translate XLIFF While Preserving Tags",
        description="Extract tag-preserving XLIFF segments and translate them safely.",
    )
    def translate_xliff_with_tags(
        file_name: str = "document.xliff",
        target_language: str = "target language",
        translation_instructions: str = "",
    ) -> str:
        return "\n".join(
            [
                "Use the XLIFF MCP Server to translate XLIFF content while preserving inline tags.",
                f"File name: {file_name}",
                f"Target language: {target_language}",
                format_optional_hint("Extra instructions", translation_instructions),
                "",
                "Required workflow:",
                "1. Ask for the raw XLIFF content if it has not been supplied yet.",
                f"2. Call `process_xliff_with_tags` with `file_name={file_name}` and the raw content.",
                "3. Translate each unit without changing inline tags, placeholders, or unit identifiers.",
                "4. Preserve the original segmentation and keep untranslated markup exactly as returned by the tool.",
                "5. If the user wants reimport-ready output, return a JSON array with `unitId` and `aiResult` for each translated unit.",
                "6. Flag any segments that are ambiguous or unsafe to translate automatically.",
            ]
        )

    @mcp.prompt(
        name="replace_xliff_targets_from_translations",
        title="Rebuild XLIFF Targets From Translation Results",
        description="Apply translation JSON back into an original XLIFF payload.",
    )
    def replace_xliff_targets_from_translations(
        file_name: str = "document.xliff",
        translation_source: str = "approved translation results",
    ) -> str:
        return "\n".join(
            [
                "Use the XLIFF MCP Server to merge translated segments back into the original XLIFF.",
                f"File name: {file_name}",
                f"Translation source: {translation_source}",
                "",
                "Required workflow:",
                "1. Confirm that the original XLIFF content and the translation JSON are both available.",
                "2. Ensure each translation entry includes either `unitId` or `segNumber` plus `aiResult` or `mtResult`.",
                "3. Call `replace_xliff_targets` with the original content and the translation JSON string.",
                "4. Report the `replacements_count` and call out any untranslated or unmatched units.",
                "5. Return the updated XLIFF content exactly as produced by the tool.",
            ]
        )

    @mcp.prompt(
        name="inspect_tmx_translation_memory",
        title="Inspect TMX Translation Memory",
        description="Validate TMX content and extract reusable translation memory entries.",
    )
    def inspect_tmx_translation_memory(
        file_name: str = "memory.tmx",
        review_focus: str = "translation memory review",
    ) -> str:
        return "\n".join(
            [
                "Use the XLIFF MCP Server to inspect a TMX translation memory file.",
                f"File name: {file_name}",
                f"Review focus: {review_focus}",
                "",
                "Required workflow:",
                "1. Ask for the raw TMX content if it has not been supplied yet.",
                "2. Call `validate_tmx` with the raw content. If validation fails, stop and explain the failure.",
                f"3. Call `process_tmx` with `file_name={file_name}` and the same TMX content.",
                "4. Summarize language pairs, unit count, representative entries, and any empty segments.",
                "5. Explain how the TMX content can support reuse, QA, or glossary extraction.",
            ]
        )

    return RegisteredSkills(
        prepare_xliff_for_translation=prepare_xliff_for_translation,
        translate_xliff_with_tags=translate_xliff_with_tags,
        replace_xliff_targets_from_translations=replace_xliff_targets_from_translations,
        inspect_tmx_translation_memory=inspect_tmx_translation_memory,
        skill_catalog=skill_catalog,
        describe_skill=describe_skill,
    )
