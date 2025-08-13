/**
 * JavaScript/Node.js example for connecting to XLIFF MCP HTTP Server
 * 
 * Install dependencies:
 * npm install @modelcontextprotocol/sdk
 */

const { Client } = require('@modelcontextprotocol/sdk/client/index.js');
const { StreamableHttpTransport } = require('@modelcontextprotocol/sdk/client/streamablehttp.js');

async function connectToXliffMCP() {
    // Your server URL
    const serverUrl = 'http://localhost:8000/mcp';
    // const serverUrl = 'https://your-domain.com/mcp';
    
    console.log(`Connecting to XLIFF MCP Server at: ${serverUrl}`);
    
    try {
        // Create transport
        const transport = new StreamableHttpTransport(serverUrl);
        
        // Create client
        const client = new Client({
            name: "xliff-client",
            version: "1.0.0"
        }, {
            capabilities: {}
        });
        
        // Connect
        await client.connect(transport);
        console.log('✅ Connected successfully!');
        
        // List available tools
        const tools = await client.listTools();
        console.log(`\n📋 Available tools: ${tools.tools.length}`);
        tools.tools.forEach(tool => {
            console.log(`  - ${tool.name}: ${tool.description}`);
        });
        
        // Test XLIFF processing
        const sampleXliff = `<?xml version="1.0" encoding="UTF-8"?>
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
</xliff>`;
        
        console.log('\n🔄 Testing XLIFF processing...');
        const result = await client.callTool({
            name: 'process_xliff',
            arguments: {
                file_name: 'test.xliff',
                content: sampleXliff,
                // api_key: 'your-api-key-here'  // Include if authentication is enabled
            }
        });
        
        if (result.content && result.content[0]) {
            const data = JSON.parse(result.content[0].text);
            if (data.success) {
                console.log(`✅ Successfully processed ${data.data.length} translation units`);
                data.data.forEach(unit => {
                    console.log(`  - Unit ${unit.segNumber}: '${unit.source.substring(0, 50)}...'`);
                });
            } else {
                console.log(`❌ Error: ${data.message}`);
            }
        }
        
        // Test validation
        console.log('\n🔍 Testing XLIFF validation...');
        const validationResult = await client.callTool({
            name: 'validate_xliff',
            arguments: {
                content: sampleXliff,
                // api_key: 'your-api-key-here'
            }
        });
        
        if (validationResult.content && validationResult.content[0]) {
            const data = JSON.parse(validationResult.content[0].text);
            console.log(`✅ Validation result: ${data.message} (${data.unit_count} units)`);
        }
        
        console.log('\n🎉 All tests completed successfully!');
        
        // Close connection
        await client.close();
        
    } catch (error) {
        console.error(`❌ Connection failed: ${error.message}`);
        console.error('Make sure the MCP server is running and accessible');
    }
}

// Web browser example (if using in browser)
function browserExample() {
    const example = `
<!-- Include MCP SDK in your HTML -->
<script src="https://unpkg.com/@modelcontextprotocol/sdk"></script>

<script>
async function connectToXliffMCP() {
    const serverUrl = 'https://your-domain.com/mcp';
    
    try {
        const transport = new MCPClient.StreamableHttpTransport(serverUrl);
        const client = new MCPClient.Client({
            name: "xliff-web-client",
            version: "1.0.0"
        });
        
        await client.connect(transport);
        
        // Use the tools
        const result = await client.callTool({
            name: 'process_xliff',
            arguments: {
                file_name: 'uploaded.xliff',
                content: document.getElementById('xliffContent').value,
                api_key: document.getElementById('apiKey').value
            }
        });
        
        const data = JSON.parse(result.content[0].text);
        document.getElementById('result').textContent = JSON.stringify(data, null, 2);
        
    } catch (error) {
        console.error('Error:', error);
    }
}
</script>
`;
    
    console.log('\n🌐 Browser Example:');
    console.log(example);
}

// React component example
function reactExample() {
    const example = `
import React, { useState } from 'react';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StreamableHttpTransport } from '@modelcontextprotocol/sdk/client/streamablehttp.js';

function XliffProcessor() {
    const [xliffContent, setXliffContent] = useState('');
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    
    const processXliff = async () => {
        setLoading(true);
        try {
            const transport = new StreamableHttpTransport('https://your-domain.com/mcp');
            const client = new Client({ name: "xliff-react-client", version: "1.0.0" });
            
            await client.connect(transport);
            
            const mcpResult = await client.callTool({
                name: 'process_xliff',
                arguments: {
                    file_name: 'upload.xliff',
                    content: xliffContent,
                    api_key: process.env.REACT_APP_MCP_API_KEY
                }
            });
            
            const data = JSON.parse(mcpResult.content[0].text);
            setResult(data);
            
            await client.close();
        } catch (error) {
            console.error('Error:', error);
            setResult({ success: false, message: error.message });
        }
        setLoading(false);
    };
    
    return (
        <div>
            <textarea 
                value={xliffContent}
                onChange={(e) => setXliffContent(e.target.value)}
                placeholder="Paste your XLIFF content here..."
            />
            <button onClick={processXliff} disabled={loading}>
                {loading ? 'Processing...' : 'Process XLIFF'}
            </button>
            {result && (
                <pre>{JSON.stringify(result, null, 2)}</pre>
            )}
        </div>
    );
}

export default XliffProcessor;
`;
    
    console.log('\n⚛️ React Component Example:');
    console.log(example);
}

// Run the example
if (require.main === module) {
    connectToXliffMCP().then(() => {
        browserExample();
        reactExample();
    });
}

module.exports = { connectToXliffMCP };