"""Shared MCP prompt and resource registration for translation workflows."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from mcp.server.fastmcp import FastMCP


SKILL_CATALOG_URI = "skills://catalog"
SKILL_DETAIL_TEMPLATE = "skills://{skill_name}"


@dataclass(frozen=True)
class SkillDefinition:
    """Declarative metadata for an MCP-native workflow skill."""

    name: str
    title: str
    description: str
    required_tools: tuple[str, ...]
    use_cases: tuple[str, ...]

    @property
    def resource_uri(self) -> str:
        return f"skills://{self.name}"


@dataclass(frozen=True)
class RegisteredSkills:
    """Exported prompt and resource callables for tests and direct imports."""

    prepare_xliff_for_translation: Callable[..., str]
    translate_xliff_with_tags: Callable[..., str]
    replace_xliff_targets_from_translations: Callable[..., str]
    inspect_tmx_translation_memory: Callable[..., str]
    skill_catalog: Callable[[], str]
    describe_skill: Callable[[str], str]


SKILL_DEFINITIONS = (
    SkillDefinition(
        name="prepare_xliff_for_translation",
        title="Prepare XLIFF For Translation",
        description="Validate XLIFF and extract translation units before translation or QA.",
        required_tools=("validate_xliff", "process_xliff"),
        use_cases=(
            "Build a clean segment list before translation starts.",
            "Confirm languages, segment counts, and empty targets in an XLIFF file.",
        ),
    ),
    SkillDefinition(
        name="translate_xliff_with_tags",
        title="Translate XLIFF While Preserving Tags",
        description="Extract tag-preserving XLIFF content for AI translation without "
        "breaking inline markup.",
        required_tools=("process_xliff_with_tags",),
        use_cases=(
            "Translate XLIFF content that contains placeholders or inline formatting.",
            "Produce unit-aligned translations that can be reimported safely.",
        ),
    ),
    SkillDefinition(
        name="replace_xliff_targets_from_translations",
        title="Rebuild XLIFF Targets From Translation Results",
        description="Inject translated segments back into the original XLIFF and verify "
        "replacement counts.",
        required_tools=("replace_xliff_targets",),
        use_cases=(
            "Apply approved AI or MT output back into the source XLIFF.",
            "Generate an updated XLIFF payload for downstream CAT or QA workflows.",
        ),
    ),
    SkillDefinition(
        name="inspect_tmx_translation_memory",
        title="Inspect TMX Translation Memory",
        description="Validate TMX content and summarize language pairs and translation "
        "memory units.",
        required_tools=("validate_tmx", "process_tmx"),
        use_cases=(
            "Audit a TMX file before reuse in localization work.",
            "Extract representative translation memory entries for analysis or glossary work.",
        ),
    ),
)
SKILL_BY_NAME = {skill.name: skill for skill in SKILL_DEFINITIONS}


def list_skill_names() -> list[str]:
    """Return prompt names that act as skills for this server."""
    return [skill.name for skill in SKILL_DEFINITIONS]


def list_skill_resources() -> list[str]:
    """Return static resource URIs published by the server."""
    return [SKILL_CATALOG_URI]


def list_skill_resource_templates() -> list[str]:
    """Return resource URI templates published by the server."""
    return [SKILL_DETAIL_TEMPLATE]


def get_skill_descriptors() -> list[dict[str, object]]:
    """Return JSON-serializable skill metadata."""
    return [
        {
            "name": skill.name,
            "title": skill.title,
            "description": skill.description,
            "required_tools": list(skill.required_tools),
            "resource_uri": skill.resource_uri,
        }
        for skill in SKILL_DEFINITIONS
    ]


def _format_skill_catalog() -> str:
    lines = [
        "# XLIFF MCP Skills",
        "",
        "These skills are exposed as MCP prompts and backed by the server's existing tools.",
        "",
    ]
    for skill in SKILL_DEFINITIONS:
        lines.extend(
            [
                f"## {skill.name}",
                f"Title: {skill.title}",
                f"Description: {skill.description}",
                f"Required tools: {', '.join(skill.required_tools)}",
                f"Resource URI: {skill.resource_uri}",
                "Use when:",
                *[f"- {use_case}" for use_case in skill.use_cases],
                "",
            ]
        )
    return "\n".join(lines).strip()


def _format_skill_detail(skill: SkillDefinition) -> str:
    lines = [
        f"# {skill.title}",
        "",
        f"Prompt name: {skill.name}",
        f"Description: {skill.description}",
        f"Required tools: {', '.join(skill.required_tools)}",
        "",
        "Recommended use cases:",
        *[f"- {use_case}" for use_case in skill.use_cases],
    ]
    return "\n".join(lines)


def _format_optional_hint(label: str, value: str) -> str:
    if value.strip():
        return f"{label}: {value}"
    return f"{label}: none provided, use the repository defaults and state assumptions."


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
        return _format_skill_catalog()

    @mcp.resource(
        SKILL_DETAIL_TEMPLATE,
        name="describe_skill",
        title="XLIFF Skill Detail",
        description="Read the details for one translation workflow skill.",
        mime_type="text/markdown",
    )
    def describe_skill(skill_name: str) -> str:
        skill = SKILL_BY_NAME.get(skill_name)
        if skill is None:
            raise ValueError(
                f"Unknown skill '{skill_name}'. Available skills: {', '.join(list_skill_names())}"
            )
        return _format_skill_detail(skill)

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
                _format_optional_hint("Extra instructions", translation_instructions),
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
