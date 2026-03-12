"""Skill metadata and shared formatting helpers."""

from __future__ import annotations

from dataclasses import dataclass


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


def get_skill(skill_name: str) -> SkillDefinition | None:
    """Return the skill definition for a prompt name."""
    return SKILL_BY_NAME.get(skill_name)


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


def format_skill_catalog() -> str:
    """Render the skills catalog as markdown."""
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


def format_skill_detail(skill: SkillDefinition) -> str:
    """Render one skill description as markdown."""
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


def format_optional_hint(label: str, value: str) -> str:
    """Render an optional prompt hint without dropping empty values silently."""
    if value.strip():
        return f"{label}: {value}"
    return f"{label}: none provided, use the repository defaults and state assumptions."
