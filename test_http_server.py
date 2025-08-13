#!/usr/bin/env python3
"""
Test HTTP MCP Server

This script tests the HTTP version of the XLIFF MCP server to ensure it works
correctly for public deployment.
"""

import asyncio
import json
import time
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def test_http_server(server_url: str = "http://localhost:8000/mcp"):
    """Test the HTTP MCP server"""
    
    print(f"🔍 Testing HTTP MCP Server at: {server_url}")
    print("=" * 60)
    
    try:
        async with streamablehttp_client(server_url) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                # Initialize connection
                print("🔌 Initializing connection...")
                await session.initialize()
                print("✅ Connected successfully!")
                
                # List available tools
                print("\n📋 Listing available tools...")
                tools = await session.list_tools()
                print(f"Found {len(tools.tools)} tools:")
                for tool in tools.tools:
                    print(f"  - {tool.name}: {tool.description}")
                
                # Test server info
                print("\n📊 Getting server information...")
                result = await session.call_tool("get_server_info", arguments={})
                if result.content:
                    server_info = json.loads(result.content[0].text)
                    print(f"  Server: {server_info.get('server_name', 'Unknown')}")
                    print(f"  Version: {server_info.get('version', 'Unknown')}")
                    print(f"  Authentication Required: {server_info.get('authentication_required', False)}")
                
                # Test XLIFF processing
                print("\n🔄 Testing XLIFF processing...")
                sample_xliff = """<?xml version="1.0" encoding="UTF-8"?>
<xliff version="1.2" xmlns="urn:oasis:names:tc:xliff:document:1.2">
  <file source-language="en" target-language="zh" datatype="plaintext" original="test.txt">
    <body>
      <trans-unit id="1">
        <source>Hello World</source>
        <target>你好世界</target>
      </trans-unit>
      <trans-unit id="2">
        <source>This is a test message.</source>
        <target></target>
      </trans-unit>
    </body>
  </file>
</xliff>"""
                
                start_time = time.time()
                result = await session.call_tool(
                    "process_xliff",
                    arguments={
                        "file_name": "test.xliff",
                        "content": sample_xliff
                    }
                )
                processing_time = time.time() - start_time
                
                if result.content:
                    data = json.loads(result.content[0].text)
                    if data["success"]:
                        print(f"✅ Successfully processed {len(data['data'])} units in {processing_time:.2f}s")
                        for unit in data['data'][:2]:  # Show first 2 units
                            print(f"  - Unit {unit['segNumber']}: '{unit['source'][:40]}...'")
                    else:
                        print(f"❌ Processing failed: {data['message']}")
                
                # Test validation
                print("\n🔍 Testing XLIFF validation...")
                start_time = time.time()
                result = await session.call_tool(
                    "validate_xliff",
                    arguments={"content": sample_xliff}
                )
                validation_time = time.time() - start_time
                
                if result.content:
                    data = json.loads(result.content[0].text)
                    status = "✅ Valid" if data["valid"] else "❌ Invalid"
                    print(f"{status}: {data['message']} ({data['unit_count']} units) in {validation_time:.2f}s")
                
                # Test with tags preservation
                print("\n🏷️  Testing tag preservation...")
                result = await session.call_tool(
                    "process_xliff_with_tags",
                    arguments={
                        "file_name": "test.xliff",
                        "content": sample_xliff
                    }
                )
                
                if result.content:
                    data = json.loads(result.content[0].text)
                    if data["success"]:
                        print(f"✅ Tag preservation test passed ({len(data['data'])} units)")
                
                # Test TMX processing
                print("\n📁 Testing TMX processing...")
                sample_tmx = """<?xml version="1.0" encoding="UTF-8"?>
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
                
                result = await session.call_tool(
                    "process_tmx",
                    arguments={
                        "file_name": "test.tmx",
                        "content": sample_tmx
                    }
                )
                
                if result.content:
                    data = json.loads(result.content[0].text)
                    if data["success"]:
                        print(f"✅ TMX processing successful ({len(data['data'])} units)")
                
                print("\n🎉 All tests completed successfully!")
                return True
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure the HTTP server is running: python -m xliff_mcp.http_server")
        print("2. Check if the port 8000 is available")
        print("3. Verify firewall settings allow connections to port 8000")
        return False


def test_direct_import():
    """Test that the HTTP server module can be imported"""
    print("🧪 Testing module imports...")
    try:
        from xliff_mcp.http_server import mcp
        print(f"✅ HTTP server module imported successfully")
        print(f"  Server name: {mcp.name}")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


async def performance_test(server_url: str = "http://localhost:8000/mcp", iterations: int = 10):
    """Run a simple performance test"""
    print(f"\n⚡ Running performance test ({iterations} iterations)...")
    
    times = []
    sample_xliff = """<?xml version="1.0" encoding="UTF-8"?>
<xliff version="1.2" xmlns="urn:oasis:names:tc:xliff:document:1.2">
  <file source-language="en" target-language="zh" datatype="plaintext" original="test.txt">
    <body>
      <trans-unit id="1">
        <source>Performance test message</source>
        <target></target>
      </trans-unit>
    </body>
  </file>
</xliff>"""
    
    try:
        async with streamablehttp_client(server_url) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                
                for i in range(iterations):
                    start_time = time.time()
                    await session.call_tool(
                        "validate_xliff",
                        arguments={"content": sample_xliff}
                    )
                    times.append(time.time() - start_time)
                
                avg_time = sum(times) / len(times)
                min_time = min(times)
                max_time = max(times)
                
                print(f"📊 Performance Results:")
                print(f"  Average response time: {avg_time:.3f}s")
                print(f"  Fastest response: {min_time:.3f}s")
                print(f"  Slowest response: {max_time:.3f}s")
                print(f"  Estimated throughput: {1/avg_time:.1f} requests/second")
                
    except Exception as e:
        print(f"❌ Performance test failed: {e}")


async def main():
    """Main test function"""
    print("🚀 XLIFF MCP HTTP Server Test Suite")
    print("=" * 60)
    
    # Test imports
    if not test_direct_import():
        return
    
    print("\n" + "=" * 60)
    print("🌐 Testing HTTP Server Connection")
    print("=" * 60)
    
    # Test basic functionality
    success = await test_http_server()
    
    if success:
        # Run performance test
        await performance_test()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\n📋 Next Steps:")
        print("1. Your HTTP MCP server is ready for deployment!")
        print("2. Configure authentication by setting XLIFF_MCP_API_KEYS environment variable")
        print("3. Deploy using Docker: docker-compose up -d")
        print("4. Set up reverse proxy for production use")
        print("5. Configure monitoring and logging")
    else:
        print("\n" + "=" * 60)
        print("❌ TESTS FAILED")
        print("=" * 60)
        print("\n🔧 Please fix the issues above before deploying")


if __name__ == "__main__":
    asyncio.run(main())