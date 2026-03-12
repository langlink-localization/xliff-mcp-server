# Agent Skills

This directory is the agent-facing skills module for the repository.

It is separate from the MCP runtime under `xliff_mcp/`.

- `skills/`: skill docs and catalog for AI agents
- `xliff_mcp/workflows/`: runtime prompt and resource registration used by the MCP server

Agents should start with `skills/catalog.json`, then open the referenced skill file they need.

Each skill file describes:

- when to use the skill
- required inputs
- recommended MCP tools
- expected outputs

The current skills in this module cover:

- preparing XLIFF for translation
- translating XLIFF with inline tags preserved
- merging translations back into XLIFF
- inspecting TMX translation memory
- exporting translation data as CSV or JSON
