#!/bin/bash

echo "Installing XLIFF MCP Server..."
echo "=============================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.10 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "Error: Python $REQUIRED_VERSION or higher is required. Found Python $PYTHON_VERSION"
    exit 1
fi

echo "✓ Python $PYTHON_VERSION found"

# Check if uv is available, otherwise use pip
if command -v uv &> /dev/null; then
    echo "✓ Using uv for installation"
    uv pip install -e .
else
    echo "✓ Using pip for installation"
    python3 -m pip install -r requirements.txt
    python3 -m pip install -e .
fi

echo ""
echo "✓ Installation complete!"
echo ""
echo "Testing the installation..."
python3 test_server.py

echo ""
echo "=============================="
echo "Setup Instructions for Claude Desktop:"
echo ""
echo "Add the following to your Claude Desktop config file:"
echo ""
echo "macOS/Linux: ~/Library/Application Support/Claude/claude_desktop_config.json"
echo "Windows: %AppData%\\Claude\\claude_desktop_config.json"
echo ""
echo '{'
echo '  "mcpServers": {'
echo '    "xliff-processor": {'
echo '      "command": "python",'
echo '      "args": ["-m", "xliff_mcp.server"],'
echo "      \"cwd\": \"$(pwd)\""
echo '    }'
echo '  }'
echo '}'
echo ""
echo "Then restart Claude Desktop to use the XLIFF processor!"