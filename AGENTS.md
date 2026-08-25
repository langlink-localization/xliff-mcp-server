# XLIFF MCP Server

## Repository purpose
- Python MCP server for parsing, validating, exporting, and rewriting XLIFF/TMX content, with a separate agent-readable `skills/` module.

## Key entrypoints
- `xliff_mcp/` owns MCP tools, prompts, resources, and runtime workflows; `skills/` owns standalone guidance.
- `pyproject.toml`, `Dockerfile`, `docker-compose.yml`, and `.env.example` are the package and runtime contracts.

## Canonical commands
- Install development dependencies with `pip install -e '.[dev]'`.
- Run `ruff check .`, `python -m pytest -q`, and `python -m compileall -q xliff_mcp tests`.
- Run `ruff format` on Python files you change; do not whole-tree reformat unless asked.
- Validate container changes with `docker compose config`.

## Working rules
- Preserve inline tags, segment identity, language metadata, replacement counts, and declared CSV/JSON output contracts.
- Keep agent Skill guidance separate from MCP runtime registration; update both only when their shared behavior changes.
- Treat user-supplied localization files as potentially confidential; do not persist inputs, translated content, exports, or raw tool payloads.
- Do not add new MCP tools or change schemas without updating tests and README tool contracts.

## Validation
- Add focused parser and round-trip tests for XLIFF/TMX behavior changes, including malformed input and tag preservation.
- Run MCP registration tests when tools, prompts, resources, or workflow mappings change.
