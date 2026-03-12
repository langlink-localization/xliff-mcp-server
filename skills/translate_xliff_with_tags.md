# Translate XLIFF While Preserving Tags

## Use When

- the XLIFF contains inline tags or placeholders
- translations must preserve markup exactly
- you need output that can be merged back safely

## Inputs

- source file name
- raw XLIFF content
- target language
- optional translation instructions

## Recommended MCP Tools

- `process_xliff_with_tags`

## Workflow

1. Extract translation units with tags preserved.
2. Translate only the human-readable text.
3. Keep inline tags, placeholders, and identifiers unchanged.
4. Preserve segmentation exactly as returned by the tool.
5. If reimport is needed, produce a JSON array with `unitId` and `aiResult`.

## Expected Output

- translated segments with preserved markup
- clear notice for any ambiguous or unsafe segments
- optional reimport-ready JSON
