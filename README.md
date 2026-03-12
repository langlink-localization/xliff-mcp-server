# XLIFF MCP Server

An MCP (Model Context Protocol) server for processing XLIFF and TMX translation files. This server provides tools for parsing, validating, and manipulating translation files commonly used in localization workflows.

## Features

- **XLIFF Processing**: Parse and extract translation units from XLIFF files
- **TMX Processing**: Parse and extract translation units from TMX files  
- **Tag Preservation**: Special processing mode that preserves inline tags for AI translation
- **Validation**: Validate XLIFF and TMX file formats
- **Translation Replacement**: Replace target translations in XLIFF files
- **CSV / JSON Export**: Generate CSV or JSON file content from XLIFF and TMX inputs
- **MCP Skills**: Expose reusable localization workflows as MCP prompts and skill resources

## Installation

### Automatic Setup (Recommended)

```bash
python setup.py
```

### Manual Installation

#### Using pip

```bash
pip install -e .
```

#### Using the install script

```bash
./install.sh  # Unix/Linux/macOS
install.bat   # Windows
```

## Configuration

### For Claude Desktop

Add the server to your Claude Desktop configuration file:

**macOS/Linux**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%AppData%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "xliff-processor": {
      "command": "python",
      "args": ["-m", "xliff_mcp.server"],
      "cwd": "/absolute/path/to/xliff-mcp-server"
    }
  }
}
```

Or if using uv:

```json
{
  "mcpServers": {
    "xliff-processor": {
      "command": "uv",
      "args": ["run", "python", "-m", "xliff_mcp.server"],
      "cwd": "/absolute/path/to/xliff-mcp-server"
    }
  }
}
```

## Available Tools

### process_xliff
Process XLIFF content and extract translation units.

**Parameters:**
- `file_name` (string): Name of the XLIFF file
- `content` (string): XLIFF file content

**Returns:** JSON with translation units including:
- fileName, segNumber, unitId, percent, source, target, srcLang, tgtLang

### process_xliff_with_tags
Process XLIFF preserving inline tags for AI translation.

**Parameters:**
- `file_name` (string): Name of the XLIFF file
- `content` (string): XLIFF file content

**Returns:** JSON with translation units preserving original formatting tags

### validate_xliff
Validate XLIFF content format.

**Parameters:**
- `content` (string): XLIFF file content to validate

**Returns:** JSON with validation status, message, and unit count

### replace_xliff_targets
Replace target translations in XLIFF file.

**Parameters:**
- `content` (string): Original XLIFF file content
- `translations` (string): JSON array of translations with segNumber/unitId and aiResult/mtResult

**Returns:** JSON with updated XLIFF content and replacement count

### process_tmx
Process TMX content and extract translation units.

**Parameters:**
- `file_name` (string): Name of the TMX file
- `content` (string): TMX file content

**Returns:** JSON with translation units including metadata

### validate_tmx
Validate TMX content format.

**Parameters:**
- `content` (string): TMX file content to validate

**Returns:** JSON with validation status and unit count

### export_xliff_file
Generate CSV or JSON file content from an XLIFF file.

**Parameters:**
- `file_name` (string): Name of the source XLIFF file
- `content` (string): XLIFF file content
- `output_format` (string): `csv` or `json`
- `preserve_tags` (boolean): Whether to preserve inline tags before export

**Returns:** JSON with generated `file_name`, `mime_type`, `content`, and `unit_count`

### export_tmx_file
Generate CSV or JSON file content from a TMX file.

**Parameters:**
- `file_name` (string): Name of the source TMX file
- `content` (string): TMX file content
- `output_format` (string): `csv` or `json`

**Returns:** JSON with generated `file_name`, `mime_type`, `content`, and `unit_count`

## Available Skills

The server now exposes MCP-native skills through:

- **Prompts**: Reusable workflow prompts that guide an MCP client through the right tool sequence
- **Resources**: A discoverable skill catalog at `skills://catalog` and per-skill detail resources at `skills://{skill_name}`

The implementation now lives under `xliff_mcp/skills/`, so the MCP skills are easy to find and extend in the repository.

### prepare_xliff_for_translation
Validate XLIFF content, extract translation units, and summarize translation readiness.

### translate_xliff_with_tags
Extract tag-preserving XLIFF segments and guide AI translation without breaking inline markup.

### replace_xliff_targets_from_translations
Merge translated segment JSON back into the original XLIFF and verify the replacement count.

### inspect_tmx_translation_memory
Validate TMX content, inspect language pairs, and summarize translation memory entries for reuse.

## Usage Examples

Once configured in Claude Desktop, you can use the tools like this:

1. **Process an XLIFF file:**
   "Please process this XLIFF file and show me the translation units"

2. **Validate XLIFF format:**
   "Can you validate if this XLIFF content is properly formatted?"

3. **Replace translations:**
   "Replace the target translations in this XLIFF file with these new translations"

4. **Process TMX file:**
   "Extract all translation units from this TMX file"

5. **Generate a CSV export:**
   "Export this XLIFF file as CSV and give me the file content"

6. **Generate a JSON export:**
   "Export this TMX file as JSON so I can save it locally"

7. **Use a built-in skill prompt:**
   "Use the `translate_xliff_with_tags` prompt to help me translate this XLIFF safely"

## Development

### Running lint

```bash
ruff check .
```

### Running tests

```bash
python -m pytest
```

### Running the smoke test script

```bash
python test_server.py
```

### Running the server directly

```bash
python -m xliff_mcp.server
```

## Requirements

- Python 3.10+
- mcp >= 1.2.0
- translate-toolkit >= 3.0.0
- lxml >= 4.9.0
- pydantic >= 2.0.0

## License

MIT

## Support

For issues and questions, please open an issue on the GitHub repository.
