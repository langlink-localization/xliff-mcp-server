# XLIFF MCP Server - Quick Start Guide

## What is this?

The XLIFF MCP Server transforms your xliff-process-api into a **Model Context Protocol (MCP) server** that works directly with Claude Desktop and other MCP clients. Instead of making HTTP API calls, you can now process XLIFF and TMX translation files directly through natural language conversations with AI.

## Features Converted from API to MCP Tools

- ✅ **process_xliff** - Extract translation units from XLIFF files
- ✅ **process_xliff_with_tags** - Process XLIFF preserving tags for AI translation  
- ✅ **validate_xliff** - Validate XLIFF format
- ✅ **replace_xliff_targets** - Replace translations in XLIFF files
- ✅ **process_tmx** - Process TMX translation memory files
- ✅ **validate_tmx** - Validate TMX format

## Super Quick Setup (2 minutes)

### 1. Install & Configure
```bash
cd /home/user/projects/xliff-mcp-server
python setup.py
```

### 2. Restart Claude Desktop
Close and reopen Claude Desktop to load the new MCP server.

### 3. Look for MCP Tools
In Claude Desktop, look for the tools/MCP icon (🔌) that appears when MCP servers are available.

## Usage Examples

Once configured, you can use natural language with Claude:

### Example 1: Process an XLIFF file
```
"I have an XLIFF file with translation units. Can you process it and show me the untranslated segments?"

[Paste your XLIFF content]
```

### Example 2: Validate file format
```
"Please validate this XLIFF file format and tell me how many translation units it contains."

[Paste XLIFF content]
```

### Example 3: Replace translations
```
"Here's my XLIFF file and some new translations. Please update the file with these translations."

[Provide XLIFF file and translation updates in JSON format]
```

### Example 4: Process with preserved tags
```
"Process this XLIFF file but preserve all the inline formatting tags for AI translation."
```

## What's Different from the Original API?

| Original API | MCP Server |
|-------------|------------|
| HTTP POST to `/api/xliff/process` | Natural language: "Process this XLIFF file" |
| JSON API responses | Conversational responses with data |
| Manual API key authentication | Integrated with Claude Desktop |
| Upload files via HTTP | Paste content directly in chat |
| Separate endpoints for each function | Single interface, multiple tools |

## File Structure

```
xliff-mcp-server/
├── xliff_mcp/
│   ├── __init__.py           # Package init
│   ├── __main__.py           # Module entry point
│   ├── server.py             # Main MCP server with tools
│   ├── models.py             # Data models (Pydantic)
│   ├── xliff_processor.py    # XLIFF processing logic
│   └── tmx_processor.py      # TMX processing logic
├── setup.py                  # Automated setup script
├── test_server.py           # Test suite
├── requirements.txt         # Dependencies
├── pyproject.toml          # Modern Python packaging
├── README.md               # Full documentation
└── QUICKSTART.md           # This guide
```

## Manual Configuration (if setup.py fails)

Add this to your Claude Desktop config:

**macOS/Linux**: `~/.config/claude/claude_desktop_config.json`
**Windows**: `%AppData%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "xliff-processor": {
      "command": "python",
      "args": ["-m", "xliff_mcp.server"],
      "cwd": "/home/user/projects/xliff-mcp-server"
    }
  }
}
```

## Testing Your Installation

```bash
# Test the server components
python test_server.py

# Test MCP server startup (should run and wait for input)
python -m xliff_mcp.server
```

## Troubleshooting

1. **"Module not found" error**: Run `pip install -r requirements.txt`
2. **MCP tools not showing in Claude**: Restart Claude Desktop completely
3. **Server not responding**: Check the Claude Desktop logs for error messages
4. **Permission errors**: Ensure the working directory path is correct and accessible

## Next Steps

- Check the full [README.md](README.md) for detailed documentation
- See [DOCUMENTATION.md](DOCUMENTATION.md) for advanced usage and API reference
- The server is ready to use with any MCP-compatible client, not just Claude Desktop

## Support

If you encounter issues:
1. Check that all dependencies are installed: `pip install -r requirements.txt`
2. Verify the server works: `python test_server.py`
3. Check Claude Desktop config file syntax
4. Restart Claude Desktop completely

Your XLIFF processing API is now available as an AI-integrated MCP service! 🎉