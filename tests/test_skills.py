"""Coverage for MCP-native skill registration on FastMCP."""

from __future__ import annotations

import xliff_mcp.server as server


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
