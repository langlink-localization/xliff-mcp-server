#!/usr/bin/env python3
"""Test script for XLIFF MCP Server"""

import json
from xliff_mcp.server import (
    process_xliff,
    process_xliff_with_tags,
    validate_xliff,
    replace_xliff_targets,
    process_tmx,
    validate_tmx
)

# Sample XLIFF content for testing
SAMPLE_XLIFF = """<?xml version="1.0" encoding="UTF-8"?>
<xliff version="1.2" xmlns="urn:oasis:names:tc:xliff:document:1.2">
  <file source-language="en" target-language="zh" datatype="plaintext" original="test.txt">
    <body>
      <trans-unit id="1">
        <source>Hello World</source>
        <target>你好世界</target>
      </trans-unit>
      <trans-unit id="2">
        <source>This is a <g id="1">test</g> message.</source>
        <target></target>
      </trans-unit>
    </body>
  </file>
</xliff>"""

# Sample TMX content for testing
SAMPLE_TMX = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE tmx SYSTEM "tmx14.dtd">
<tmx version="1.4">
  <header creationtool="TestTool" creationtoolversion="1.0" 
          datatype="plaintext" segtype="sentence" 
          adminlang="en" srclang="en" o-tmf="test"/>
  <body>
    <tu>
      <tuv xml:lang="en">
        <seg>Hello World</seg>
      </tuv>
      <tuv xml:lang="zh">
        <seg>你好世界</seg>
      </tuv>
    </tu>
  </body>
</tmx>"""


def test_xliff_processing():
    """Test XLIFF processing functions"""
    print("Testing XLIFF Processing...")
    print("-" * 50)
    
    # Test basic processing
    result = process_xliff("test.xliff", SAMPLE_XLIFF)
    data = json.loads(result)
    print(f"✓ process_xliff: {data['message']}")
    print(f"  Units found: {len(data['data'])}")
    
    # Test processing with tags
    result = process_xliff_with_tags("test.xliff", SAMPLE_XLIFF)
    data = json.loads(result)
    print(f"✓ process_xliff_with_tags: {data['message']}")
    
    # Test validation
    result = validate_xliff(SAMPLE_XLIFF)
    data = json.loads(result)
    print(f"✓ validate_xliff: {data['message']}")
    print(f"  Valid: {data['valid']}, Units: {data['unit_count']}")
    
    # Test target replacement
    translations = json.dumps([
        {"unitId": "2", "aiResult": "This is a <g id=\"1\">test</g> message in Chinese."}
    ])
    result = replace_xliff_targets(SAMPLE_XLIFF, translations)
    data = json.loads(result)
    print(f"✓ replace_xliff_targets: {data['message']}")
    print(f"  Replacements: {data['replacements_count']}")
    
    print()


def test_tmx_processing():
    """Test TMX processing functions"""
    print("Testing TMX Processing...")
    print("-" * 50)
    
    # Test TMX processing
    result = process_tmx("test.tmx", SAMPLE_TMX)
    data = json.loads(result)
    print(f"✓ process_tmx: {data['message']}")
    print(f"  Units found: {len(data['data'])}")
    
    # Test TMX validation
    result = validate_tmx(SAMPLE_TMX)
    data = json.loads(result)
    print(f"✓ validate_tmx: {data['message']}")
    print(f"  Valid: {data['valid']}, Units: {data['unit_count']}")
    
    print()


def main():
    """Run all tests"""
    print("\n" + "=" * 50)
    print("XLIFF MCP Server Test Suite")
    print("=" * 50 + "\n")
    
    try:
        test_xliff_processing()
        test_tmx_processing()
        
        print("=" * 50)
        print("All tests completed successfully! ✓")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()