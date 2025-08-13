#!/usr/bin/env python3
"""Test SDL XLIFF processing"""

import json
from xliff_mcp.xliff_processor import XliffProcessorService

# SDL XLIFF sample content
sdl_xliff_content = """<?xml version="1.0" encoding="utf-8"?>
<xliff xmlns:sdl="http://sdl.com/FileTypes/SdlXliff/1.0" xmlns="urn:oasis:names:tc:xliff:document:1.2" version="1.2" sdl:version="1.0">
  <file original="test.xlf" datatype="x-sdlfilterframework2" source-language="en-US" target-language="zh-HK">
    <header>
      <sdl:seg-defs>
        <sdl:seg id="1" conf="Draft" origin="source"/>
      </sdl:seg-defs>
    </header>
    <body>
      <trans-unit id="1">
        <source>Hello World</source>
        <seg-source>
          <mrk mid="0" mtype="seg">Hello World</mrk>
        </seg-source>
        <target>
          <mrk mid="0" mtype="seg">你好世界</mrk>
        </target>
        <sdl:seg-defs>
          <sdl:seg id="1" conf="Draft" origin="source"/>
        </sdl:seg-defs>
      </trans-unit>
      <trans-unit id="2">
        <source>Welcome to the application</source>
        <seg-source>
          <mrk mid="0" mtype="seg">Welcome to the application</mrk>
        </seg-source>
        <target>
          <mrk mid="0" mtype="seg">歡迎使用應用程式</mrk>
        </target>
      </trans-unit>
    </body>
  </file>
</xliff>"""

def test_sdl_xliff():
    print("Testing SDL XLIFF processing...")
    processor = XliffProcessorService()
    
    try:
        result = processor.process_xliff("test.sdlxliff", sdl_xliff_content)
        print(f"\nProcessed {len(result)} translation units")
        
        for unit in result:
            print(f"\nUnit ID: {unit.unitId}")
            print(f"Source: {unit.source}")
            print(f"Target: {unit.target}")
            print(f"Percent: {unit.percent}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sdl_xliff()