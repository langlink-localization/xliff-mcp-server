# Export Translation Data As CSV Or JSON

## Use When

- a user needs translation data in a file-oriented format
- parsed XLIFF or TMX content must be saved outside the chat
- the next step expects CSV or JSON instead of conversational output

## Inputs

- source file name
- raw XLIFF or TMX content
- desired format: `csv` or `json`
- for XLIFF, whether inline tags should be preserved

## Recommended MCP Tools

- `export_xliff_file`
- `export_tmx_file`

## Workflow

1. Identify whether the source content is XLIFF or TMX.
2. Choose the export format the user asked for.
3. For XLIFF, decide whether tag-preserving export is required.
4. Generate the export content with the matching tool.
5. Return the generated `file_name`, `mime_type`, `encoding`, and `content`.

## Expected Output

- generated file name
- file content in CSV or JSON
- MIME type and encoding
- unit count for verification
