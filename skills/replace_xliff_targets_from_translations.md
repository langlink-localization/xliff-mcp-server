# Rebuild XLIFF Targets From Translation Results

## Use When

- approved translations need to be merged back into XLIFF
- you need updated XLIFF content for downstream CAT or QA workflows

## Inputs

- source file name
- original XLIFF content
- translation JSON containing `unitId` or `segNumber`

## Recommended MCP Tools

- `replace_xliff_targets`

## Workflow

1. Confirm the original XLIFF content is available.
2. Confirm the translation payload includes `aiResult` or `mtResult`.
3. Merge the translations back into the original XLIFF.
4. Report the replacement count.
5. Call out any unmatched or untranslated units.

## Expected Output

- updated XLIFF content
- replacement count
- unmatched unit summary if any
