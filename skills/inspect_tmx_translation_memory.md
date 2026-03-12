# Inspect TMX Translation Memory

## Use When

- you need to validate a TMX file
- you want to inspect language pairs or representative translation memory entries
- you need a quick audit before reuse or glossary work

## Inputs

- source file name
- raw TMX content

## Recommended MCP Tools

- `validate_tmx`
- `process_tmx`

## Workflow

1. Validate the TMX content first.
2. Stop and report the validation error if the file is invalid.
3. Process the TMX into translation memory units.
4. Summarize language pairs, unit count, representative entries, and empty segments.
5. Explain how the TMX can support reuse, QA, or glossary extraction.

## Expected Output

- validation status
- language pair summary
- unit overview
- sample entries for analysis
