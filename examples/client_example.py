#!/usr/bin/env python3
"""
Example client for connecting to XLIFF MCP HTTP Server

This shows how other applications can connect to your public MCP service.
"""

import asyncio
import json
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def test_public_mcp_server():
    """Test connection to public XLIFF MCP server"""
    
    # Your server URL (change this to your actual deployed server)
    server_url = "http://localhost:8000/mcp"
    # server_url = "https://your-domain.com/mcp"
    
    print(f"Connecting to XLIFF MCP Server at: {server_url}")
    
    try:
        async with streamablehttp_client(server_url) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                # Initialize the connection
                await session.initialize()
                print("✅ Connected successfully!")
                
                # List available tools
                tools = await session.list_tools()
                print(f"\n📋 Available tools: {len(tools.tools)}")
                for tool in tools.tools:
                    print(f"  - {tool.name}: {tool.description}")
                
                # Test XLIFF processing
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
                
                print("\n🔄 Testing XLIFF processing...")
                result = await session.call_tool(
                    "process_xliff",
                    arguments={
                        "file_name": "test.xliff",
                        "content": sample_xliff,
                        # "api_key": "your-api-key-here"  # Include if authentication is enabled
                    }
                )
                
                if result.content:
                    data = json.loads(result.content[0].text)
                    if data["success"]:
                        print(f"✅ Successfully processed {len(data['data'])} translation units")
                        for unit in data['data']:
                            print(f"  - Unit {unit['segNumber']}: '{unit['source'][:50]}...'")
                    else:
                        print(f"❌ Error: {data['message']}")
                
                # Test validation
                print("\n🔍 Testing XLIFF validation...")
                result = await session.call_tool(
                    "validate_xliff",
                    arguments={
                        "content": sample_xliff,
                        # "api_key": "your-api-key-here"
                    }
                )
                
                if result.content:
                    data = json.loads(result.content[0].text)
                    print(f"✅ Validation result: {data['message']} ({data['unit_count']} units)")
                
                print("\n🎉 All tests completed successfully!")
                
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("Make sure the MCP server is running and accessible")


async def example_claude_desktop_config():
    """Show how to configure Claude Desktop to use the public server"""
    
    config = {
        "mcpServers": {
            "xliff-processor-public": {
                "command": "python",
                "args": ["-c", """
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def main():
    async with streamablehttp_client('http://your-domain.com/mcp') as (r, w, _):
        async with ClientSession(r, w) as session:
            await session.initialize()
            # Your MCP client logic here

if __name__ == '__main__':
    asyncio.run(main())
"""]
            }
        }
    }
    
    print("\n📝 Claude Desktop Configuration for Public Server:")
    print("Add this to your claude_desktop_config.json:")
    print(json.dumps(config, indent=2))


def example_direct_http_usage():
    """Show how to use the server with direct HTTP requests"""
    
    example_code = """
# Example using requests library (Python)
import requests
import json

# Server endpoint
url = "http://your-domain.com/mcp"

# Prepare MCP request
mcp_request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "process_xliff",
        "arguments": {
            "file_name": "test.xliff",
            "content": "<?xml version='1.0'?>...",
            "api_key": "your-api-key"  # if authentication enabled
        }
    }
}

# Send request
response = requests.post(url, json=mcp_request)
result = response.json()

print(json.loads(result["result"]["content"][0]["text"]))
"""
    
    print("\n🌐 Direct HTTP Usage Example:")
    print(example_code)


async def main():
    """Main function to run all examples"""
    print("=" * 60)
    print("XLIFF MCP Public Server Client Examples")
    print("=" * 60)
    
    await test_public_mcp_server()
    await example_claude_desktop_config()
    example_direct_http_usage()
    
    print("\n" + "=" * 60)
    print("For more information, see the deployment documentation.")


if __name__ == "__main__":
    asyncio.run(main())