#!/usr/bin/env python3
"""
API Key Management Tool for XLIFF MCP Server

Usage:
    python manage_keys.py generate --name "Client Name" --rate-limit 100
    python manage_keys.py list
    python manage_keys.py revoke --key "api-key-here"
    python manage_keys.py export --format env
"""

import json
import secrets
import string
import argparse
import os
from datetime import datetime
from typing import Dict, Any


class APIKeyManager:
    def __init__(self, keys_file: str = "api_keys.json"):
        self.keys_file = keys_file
        self.keys = self.load_keys()
    
    def load_keys(self) -> Dict[str, Dict[str, Any]]:
        """Load API keys from file"""
        if os.path.exists(self.keys_file):
            try:
                with open(self.keys_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: {self.keys_file} is corrupted, starting fresh")
        return {}
    
    def save_keys(self):
        """Save API keys to file"""
        with open(self.keys_file, 'w') as f:
            json.dump(self.keys, f, indent=2)
        print(f"Keys saved to {self.keys_file}")
    
    def generate_key(self, name: str, rate_limit: int = 100, permissions: list = None) -> str:
        """Generate a new API key"""
        if permissions is None:
            permissions = ["all"]
        
        # Generate a secure random key
        alphabet = string.ascii_letters + string.digits
        api_key = ''.join(secrets.choice(alphabet) for _ in range(32))
        
        # Store key metadata
        self.keys[api_key] = {
            "name": name,
            "permissions": permissions,
            "rate_limit": rate_limit,
            "created_at": datetime.now().isoformat(),
            "last_used": None,
            "active": True
        }
        
        self.save_keys()
        return api_key
    
    def list_keys(self):
        """List all API keys"""
        if not self.keys:
            print("No API keys found")
            return
        
        print(f"{'Key (first 8 chars)':<20} {'Name':<20} {'Rate Limit':<12} {'Status':<8} {'Created'}")
        print("-" * 80)
        
        for key, metadata in self.keys.items():
            status = "Active" if metadata.get("active", True) else "Revoked"
            created = metadata.get("created_at", "Unknown")[:10]  # Just date part
            print(f"{key[:8]}...{' ' * 9} {metadata.get('name', 'Unknown'):<20} "
                  f"{metadata.get('rate_limit', 'N/A'):<12} {status:<8} {created}")
    
    def revoke_key(self, api_key: str):
        """Revoke an API key"""
        if api_key in self.keys:
            self.keys[api_key]["active"] = False
            self.keys[api_key]["revoked_at"] = datetime.now().isoformat()
            self.save_keys()
            print(f"API key {api_key[:8]}... has been revoked")
        else:
            print(f"API key {api_key[:8]}... not found")
    
    def export_keys(self, format_type: str = "env"):
        """Export keys in different formats"""
        active_keys = [key for key, meta in self.keys.items() if meta.get("active", True)]
        
        if format_type == "env":
            print("# Environment variable format")
            print(f"export XLIFF_MCP_API_KEYS=\"{','.join(active_keys)}\"")
        elif format_type == "docker":
            print("# Docker environment format")
            print(f"XLIFF_MCP_API_KEYS={','.join(active_keys)}")
        elif format_type == "json":
            print(json.dumps(active_keys, indent=2))
        elif format_type == "yaml":
            print("# YAML format")
            print("environment:")
            print(f"  XLIFF_MCP_API_KEYS: \"{','.join(active_keys)}\"")
    
    def cleanup_revoked(self):
        """Remove revoked keys from storage"""
        active_keys = {k: v for k, v in self.keys.items() if v.get("active", True)}
        removed_count = len(self.keys) - len(active_keys)
        self.keys = active_keys
        self.save_keys()
        print(f"Removed {removed_count} revoked keys")


def main():
    parser = argparse.ArgumentParser(description="Manage API keys for XLIFF MCP Server")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate a new API key')
    gen_parser.add_argument('--name', required=True, help='Name for the API key')
    gen_parser.add_argument('--rate-limit', type=int, default=100, help='Rate limit (requests per minute)')
    gen_parser.add_argument('--permissions', nargs='+', default=['all'], help='Permissions for the key')
    
    # List command
    subparsers.add_parser('list', help='List all API keys')
    
    # Revoke command
    revoke_parser = subparsers.add_parser('revoke', help='Revoke an API key')
    revoke_parser.add_argument('--key', required=True, help='API key to revoke')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export API keys')
    export_parser.add_argument('--format', choices=['env', 'docker', 'json', 'yaml'], 
                              default='env', help='Export format')
    
    # Cleanup command
    subparsers.add_parser('cleanup', help='Remove revoked keys')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = APIKeyManager()
    
    if args.command == 'generate':
        api_key = manager.generate_key(args.name, args.rate_limit, args.permissions)
        print(f"\n🔑 New API key generated:")
        print(f"Key: {api_key}")
        print(f"Name: {args.name}")
        print(f"Rate Limit: {args.rate_limit} requests/minute")
        print(f"Permissions: {', '.join(args.permissions)}")
        print(f"\n⚠️  Save this key securely - it won't be shown again!")
        
    elif args.command == 'list':
        manager.list_keys()
        
    elif args.command == 'revoke':
        manager.revoke_key(args.key)
        
    elif args.command == 'export':
        manager.export_keys(args.format)
        
    elif args.command == 'cleanup':
        manager.cleanup_revoked()


if __name__ == "__main__":
    main()