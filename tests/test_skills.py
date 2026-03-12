"""Coverage for workflow registration and agent skill assets."""

from __future__ import annotations

import json
from pathlib import Path

import xliff_mcp.skill_registry as legacy_skill_registry
import xliff_mcp.server as server
from xliff_mcp.workflows import list_skill_names


REPO_ROOT = Path(__file__).resolve().parents[1]


async def test_fastmcp_lists_translation_skill_prompts() -> None:
    prompts = await server.mcp.list_prompts()
    prompt_names = {prompt.name for prompt in prompts}

    assert {
        "prepare_xliff_for_translation",
        "translate_xliff_with_tags",
        "replace_xliff_targets_from_translations",
        "inspect_tmx_translation_memory",
    }.issubset(prompt_names)


async def test_fastmcp_reads_skill_prompts_and_resources() -> None:
    prompt = await server.mcp.get_prompt(
        "translate_xliff_with_tags",
        {
            "file_name": "sample.xliff",
            "target_language": "zh-CN",
            "translation_instructions": "Keep placeholders unchanged.",
        },
    )
    resources = await server.mcp.list_resources()
    resource_templates = await server.mcp.list_resource_templates()
    catalog = await server.mcp.read_resource("skills://catalog")
    detail = await server.mcp.read_resource("skills://translate_xliff_with_tags")

    resource_uris = {str(resource.uri) for resource in resources}
    resource_template_uris = {
        str(resource_template.uriTemplate) for resource_template in resource_templates
    }

    assert "process_xliff_with_tags" in prompt.messages[0].content.text
    assert "Keep placeholders unchanged." in prompt.messages[0].content.text
    assert "skills://catalog" in resource_uris
    assert "skills://{skill_name}" in resource_template_uris
    assert "prepare_xliff_for_translation" in catalog[0].content
    assert "Prompt name: translate_xliff_with_tags" in detail[0].content


def test_legacy_skill_registry_import_still_works() -> None:
    assert legacy_skill_registry.list_skill_names() == list_skill_names()


def test_agent_skills_catalog_points_to_existing_files() -> None:
    catalog_path = REPO_ROOT / "skills" / "catalog.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))

    assert catalog["module"] == "agent-skills"
    assert len(catalog["skills"]) >= 5

    for skill in catalog["skills"]:
        assert (REPO_ROOT / skill["file"]).exists()
