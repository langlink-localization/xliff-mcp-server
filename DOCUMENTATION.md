# XLIFF MCP Server - Documentation

## Overview

The XLIFF MCP Server provides Model Context Protocol (MCP) tools for processing XLIFF (XML Localization Interchange File Format) and TMX (Translation Memory eXchange) files. These are industry-standard formats used in translation and localization workflows.

## Architecture

The server is built using:
- **FastMCP**: Simplified MCP server framework  
- **translate-toolkit**: Industry-standard library for handling translation files
- **lxml**: XML processing with full XPath support
- **pydantic**: Data validation and serialization

## Tools Reference

### 1. process_xliff

Extracts translation units from XLIFF files for review or processing.

**Input:**
```json
{
  "file_name": "document.xliff",
  "content": "<?xml version=\"1.0\"?>..."
}
```

**Output:**
```json
{
  "success": true,
  "message": "Successfully processed 10 translation units",
  "data": [
    {
      "fileName": "document.xliff",
      "segNumber": 1,
      "unitId": "unit-001",
      "percent": 75.0,
      "source": "Hello World",
      "target": "Hola Mundo",
      "srcLang": "en",
      "tgtLang": "es"
    }
  ]
}
```

### 2. process_xliff_with_tags

Preserves inline formatting tags, essential for maintaining text formatting in translations.

**Use Cases:**
- AI-assisted translation where formatting must be preserved
- Processing files with complex inline markup
- Maintaining brand-specific styling in translations

**Example with tags:**
```xml
<source>Click <g id="1">here</g> to continue</source>
```

### 3. validate_xliff

Checks if XLIFF content is well-formed and valid.

**Input:**
```json
{
  "content": "<?xml version=\"1.0\"?>..."
}
```

**Output:**
```json
{
  "valid": true,
  "message": "XLIFF format is valid",
  "unit_count": 25
}
```

### 4. replace_xliff_targets

Updates target translations in XLIFF files, useful for batch translation updates.

**Input:**
```json
{
  "content": "<?xml version=\"1.0\"?>...",
  "translations": "[{\"unitId\": \"1\", \"aiResult\": \"Nueva traducción\"}]"
}
```

**Output:**
```json
{
  "success": true,
  "message": "Successfully replaced 1 translations",
  "content": "<?xml version=\"1.0\"?>...",
  "replacements_count": 1
}
```

### 5. process_tmx

Processes TMX (Translation Memory) files.

**Features:**
- Extracts translation pairs
- Preserves metadata (creator, modifier, context)
- Handles multi-language TMX files

### 6. validate_tmx

Validates TMX file format and structure.

## XLIFF Format Support

### Supported Versions
- XLIFF 1.2 (most common)
- XLIFF 2.0 (basic support)
- XLIFF 2.1 (basic support)

### Supported Elements
- `trans-unit` / `unit` - Translation units
- `source` - Source text
- `target` - Target translation
- `g` - Generic inline element
- `x` - Generic placeholder
- `bx` / `ex` - Begin/end paired elements
- `bpt` / `ept` - Begin/end paired tags
- `ph` - Placeholder
- `it` - Isolated tag

### Metadata Extraction
- Language codes (source-language, target-language)
- Translation percentage/score
- Unit IDs
- File references

## TMX Format Support

### Features
- Multi-language support
- Translation unit variants (tuv)
- Property extraction
- Creation/modification tracking

## Integration Examples

### With Claude Desktop

1. **Simple Translation Review:**
```
"I have an XLIFF file with 100 segments. Can you process it and show me all segments that are less than 50% translated?"
```

2. **Batch Translation Update:**
```
"Here's my XLIFF file and a list of new translations. Please update the file with these translations."
```

3. **Format Validation:**
```
"Please validate this XLIFF file and tell me if there are any formatting issues."
```

### Programmatic Usage

```python
import json
from xliff_mcp.server import process_xliff

# Process XLIFF content
result = await process_xliff("myfile.xliff", xliff_content)
data = json.loads(result)

# Extract untranslated segments
untranslated = [
    unit for unit in data['data'] 
    if not unit['target']
]
```

## Best Practices

### 1. File Size Considerations
- Optimal: < 10MB XLIFF files
- Maximum tested: 50MB
- For larger files, consider splitting

### 2. Character Encoding
- Always use UTF-8 encoding
- Server automatically handles BOM
- Preserves special characters

### 3. Tag Preservation
- Use `process_xliff_with_tags` for AI translation
- Regular `process_xliff` for analysis
- Tags are preserved during replacement

### 4. Error Handling
- All tools return success status
- Detailed error messages included
- Original content preserved on error

## Troubleshooting

### Common Issues

**1. "Invalid XLIFF format" error**
- Check XML is well-formed
- Verify namespace declarations
- Ensure proper XLIFF structure

**2. Missing translations after replacement**
- Verify unit IDs match
- Check translations JSON format
- Ensure proper escaping of special characters

**3. Language codes not detected**
- Check file-level language attributes
- Verify language code format (use ISO codes)

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance Metrics

- **Processing Speed**: ~1000 units/second
- **Memory Usage**: ~50MB for 10,000 units
- **Validation Speed**: ~5000 units/second

## Limitations

1. **Binary content**: Cannot process binary XLIFF formats
2. **Custom namespaces**: Limited support for proprietary extensions
3. **Large files**: Performance degrades >100MB
4. **Streaming**: No streaming support (full file load required)

## Future Enhancements

- [ ] XLIFF 2.1 full support
- [ ] Streaming processing for large files
- [ ] Translation memory integration
- [ ] Quality check tools
- [ ] Diff/merge capabilities
- [ ] Format conversion (XLIFF ↔ TMX)

## Support

For issues or feature requests, please open an issue on GitHub or contact the maintainers.