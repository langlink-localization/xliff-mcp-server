#!/usr/bin/env python3
"""Test with real SDL XLIFF content from user"""

import json
from xliff_mcp.server import process_xliff

# The actual content provided by user
sdl_xliff_content = """<?xml version="1.0" encoding="utf-8"?>
<xliff xmlns:sdl="http://sdl.com/FileTypes/SdlXliff/1.0" xmlns="urn:oasis:names:tc:xliff:document:1.2" version="1.2" sdl:version="1.0">
  <file original="C:\\Users\\mayz\\AppData\\Local\\Temp\\181fa28c-c8b2-489c-8258-7eec9e0924c0\\JH_HL_Phase2_html_245keys_07_zh_HK_20250807_182444\\zh-HK\\iloc_1754590946310.strings_18615759.xlf" datatype="x-sdlfilterframework2" source-language="en-US" target-language="zh-HK">
    <header>
      <sdl:seg-defs>
        <sdl:seg id="1" conf="Draft" origin="source"/>
        <sdl:seg id="2" conf="Draft" origin="source"/>
      </sdl:seg-defs>
    </header>
    <body>
      <trans-unit id="1">
        <source>Welcome to our service</source>
        <seg-source>
          <mrk mid="0" mtype="seg">Welcome to our service</mrk>
        </seg-source>
        <target>
          <mrk mid="0" mtype="seg">歡迎使用我們的服務</mrk>
        </target>
      </trans-unit>
      <trans-unit id="2">
        <source>Please select an option</source>
        <seg-source>
          <mrk mid="0" mtype="seg">Please select an option</mrk>
        </seg-source>
        <target>
          <mrk mid="0" mtype="seg">請選擇一個選項</mrk>
        </target>
      </trans-unit>
    </body>
  </file>
</xliff>"""

def test_real_sdl():
    print("Testing real SDL XLIFF content...")
    
    # Test using the MCP tool directly
    result = process_xliff(
        file_name="AI_iloc_1754590946310.strings_18615759.xlf (1).sdlxliff",
        content=sdl_xliff_content
    )
    
    print("\nResult:")
    print(result)
    
    # Parse the result
    result_data = json.loads(result)
    print(f"\nSuccess: {result_data['success']}")
    print(f"Message: {result_data['message']}")
    print(f"Number of units: {len(result_data['data'])}")
    
    if result_data['data']:
        print("\nTranslation units:")
        for unit in result_data['data']:
            print(f"\n  Unit {unit['unitId']}:")
            print(f"    Source: {unit['source']}")
            print(f"    Target: {unit['target']}")
            print(f"    Languages: {unit['srcLang']} -> {unit['tgtLang']}")

if __name__ == "__main__":
    test_real_sdl()