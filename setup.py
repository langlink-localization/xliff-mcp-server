#!/usr/bin/env python3
"""
Simple setup script to install and configure XLIFF MCP Server for Claude Desktop
"""

import json
import os
import platform
import subprocess
import sys
from pathlib import Path


def get_claude_config_path():
    """Get the path to Claude Desktop config file"""
    system = platform.system()
    if system == "Darwin":  # macOS
        return Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
    elif system == "Windows":
        return Path(os.environ.get("APPDATA", "")) / "Claude" / "claude_desktop_config.json"
    else:  # Linux and others
        # Claude Desktop might not be available on Linux, but we'll provide the path anyway
        return Path.home() / ".config/claude/claude_desktop_config.json"


def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def test_installation():
    """Test that the MCP server works"""
    print("🧪 Testing MCP server...")
    try:
        result = subprocess.run(
            [sys.executable, "test_server.py"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print("✅ MCP server test passed!")
            return True
        else:
            print(f"❌ MCP server test failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ MCP server test timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing MCP server: {e}")
        return False


def configure_claude_desktop():
    """Configure Claude Desktop to use the MCP server"""
    config_path = get_claude_config_path()
    current_dir = Path.cwd().absolute()
    
    print(f"🔧 Configuring Claude Desktop...")
    print(f"   Config file: {config_path}")
    
    # Create config directory if it doesn't exist
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Load existing config or create new one
    config = {}
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except json.JSONDecodeError:
            print("⚠️  Existing config file is invalid JSON, creating new one")
            config = {}
    
    # Add our MCP server
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    
    config["mcpServers"]["xliff-processor"] = {
        "command": "python",
        "args": ["-m", "xliff_mcp.server"],
        "cwd": str(current_dir)
    }
    
    # Write config
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print("✅ Claude Desktop configured successfully!")
        print(f"   Server 'xliff-processor' added to config")
        return True
    except Exception as e:
        print(f"❌ Failed to write config: {e}")
        return False


def main():
    """Main setup function"""
    print("🚀 XLIFF MCP Server Setup")
    print("=" * 50)
    
    # Check we're in the right directory
    if not Path("xliff_mcp").exists() or not Path("requirements.txt").exists():
        print("❌ Please run this script from the xliff-mcp-server directory")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed during dependency installation")
        sys.exit(1)
    
    # Test installation
    if not test_installation():
        print("\n❌ Setup failed during testing")
        sys.exit(1)
    
    # Configure Claude Desktop
    if not configure_claude_desktop():
        print("\n⚠️  MCP server works but Claude Desktop configuration failed")
        print("   You can manually add the server to your Claude config")
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Restart Claude Desktop")
    print("2. Look for the MCP tools icon in Claude Desktop")
    print("3. You should see 6 XLIFF/TMX processing tools available")
    print("\nAvailable tools:")
    print("- process_xliff: Extract translation units from XLIFF files")
    print("- process_xliff_with_tags: Process XLIFF preserving tags for AI translation")
    print("- validate_xliff: Validate XLIFF format")
    print("- replace_xliff_targets: Replace translations in XLIFF files")
    print("- process_tmx: Process TMX translation memory files")
    print("- validate_tmx: Validate TMX format")


if __name__ == "__main__":
    main()