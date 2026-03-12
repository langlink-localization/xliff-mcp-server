# Prepare XLIFF For Translation

## Use When

- you need to validate XLIFF before translation starts
- you need a clean list of translation units
- you need to identify empty targets or language metadata quickly

## Inputs

- source file name
- raw XLIFF content

## Recommended MCP Tools

- `validate_xliff`
- `process_xliff`

## Workflow

1. Validate the raw XLIFF content first.
2. Stop and report the validation error if the file is invalid.
3. Process the XLIFF into translation units.
4. Summarize source language, target language, segment count, and untranslated units.
5. Return a translation-ready unit list keyed by `unitId` and `segNumber`.

## Expected Output

- validation status
- language pair summary
- translation unit list
- untranslated or risky units called out explicitly
