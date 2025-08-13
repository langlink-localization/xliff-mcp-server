# XLIFF MCP Server

An MCP (Model Context Protocol) server for processing XLIFF and TMX translation files. This server provides tools for parsing, validating, and manipulating translation files commonly used in localization workflows.

## Features

- **XLIFF Processing**: Parse and extract translation units from XLIFF files
- **TMX Processing**: Parse and extract translation units from TMX files  
- **Tag Preservation**: Special processing mode that preserves inline tags for AI translation
- **Validation**: Validate XLIFF and TMX file formats
- **Translation Replacement**: Replace target translations in XLIFF files

## Installation

### Automatic Setup (Recommended)

```bash
python setup.py
```

### Manual Installation

#### Using pip

```bash
pip install -r requirements.txt
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

## Development

### Running tests

```bash
python -m pytest tests/
```

### Running the server directly

```bash
python -m xliff_mcp.server
```

## Requirements

- Python 3.10+
- mcp[cli] >= 1.2.0
- translate-toolkit >= 3.0.0
- lxml >= 4.9.0
- pydantic >= 2.0.0

## License

MIT

## Support

For issues and questions, please open an issue on the GitHub repository.