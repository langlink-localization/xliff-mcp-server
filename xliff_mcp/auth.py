"""Authentication and security utilities for XLIFF MCP Server."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

_KEYS_ENV_VARS = ("XLIFF_MCP_API_KEYS", "XLIFF_MCP_API_KEY")


class APIKeyAuth:
    """Simple API key authentication"""

    def __init__(self, keys_file: str = "api_keys.json"):
        self.keys_file = Path(keys_file)
        self.api_keys = self._load_api_keys()

    @property
    def enabled(self) -> bool:
        """Whether API key enforcement is enabled."""
        return bool(self.api_keys)

    def _load_api_keys(self) -> dict[str, dict[str, Any]]:
        """Load API keys from environment or file"""
        keys: dict[str, dict[str, Any]] = {}

        for env_name in _KEYS_ENV_VARS:
            env_keys = os.getenv(env_name, "")
            if not env_keys:
                continue
            for key in env_keys.split(","):
                key = key.strip()
                if key:
                    keys[key] = {
                        "name": "env_key",
                        "permissions": ["all"],
                        "rate_limit": 100,
                        "active": True,
                    }

        if self.keys_file.exists():
            try:
                file_keys = json.loads(self.keys_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Failed to parse API keys file {self.keys_file}") from exc

            for key, metadata in file_keys.items():
                keys[key] = {
                    "name": metadata.get("name", "file_key"),
                    "permissions": metadata.get("permissions", ["all"]),
                    "rate_limit": metadata.get("rate_limit", 100),
                    "active": metadata.get("active", True),
                }

        return keys

    def verify_key(self, api_key: str | None) -> dict[str, Any]:
        """Verify API key and return permissions"""
        if not self.enabled:
            return {"valid": True, "permissions": ["all"], "rate_limit": 100}

        if not api_key:
            return {"valid": False, "reason": "No API key provided"}

        metadata = self.api_keys.get(api_key)
        if metadata is None:
            return {"valid": False, "reason": "Invalid API key"}

        if not metadata.get("active", True):
            return {"valid": False, "reason": "API key is inactive"}

        return {
            "valid": True,
            "permissions": metadata.get("permissions", ["all"]),
            "rate_limit": metadata.get("rate_limit", 100),
        }

    def describe(self) -> dict[str, Any]:
        """Return summary information for diagnostics and health endpoints."""
        if not self.enabled:
            return {
                "enabled": False,
                "key_count": 0,
            }

        return {
            "enabled": True,
            "key_count": len(self.api_keys),
        }


class RateLimiter:
    """Simple in-memory rate limiter"""

    def __init__(self):
        self.requests = {}  # key: {timestamp: count}

    def is_allowed(self, api_key: str, limit: int = 100, window: int = 60) -> bool:
        """Check if request is within rate limit"""
        now = time.time()
        window_start = now - window

        # Clean old entries
        if api_key in self.requests:
            self.requests[api_key] = [
                req_time for req_time in self.requests[api_key]
                if req_time > window_start
            ]
        else:
            self.requests[api_key] = []

        # Check if under limit
        if len(self.requests[api_key]) >= limit:
            return False

        # Add current request
        self.requests[api_key].append(now)
        return True


class SecurityHeaders:
    """Security headers for HTTP responses"""

    @staticmethod
    def get_headers() -> dict[str, str]:
        """Get security headers for HTTP responses"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }


# Global instances
api_auth = APIKeyAuth()
rate_limiter = RateLimiter()


def require_auth(func):
    """Decorator to require authentication for tool functions"""
    def wrapper(*args, **kwargs):
        api_key = kwargs.get("api_key")

        # Verify API key
        auth_result = api_auth.verify_key(api_key)
        if not auth_result["valid"]:
            return json.dumps({
                "success": False,
                "message": f"Authentication failed: {auth_result.get('reason', 'Invalid key')}",
                "error_code": "AUTH_FAILED",
            })

        if not api_auth.enabled:
            return func(*args, **kwargs)

        # Check rate limit
        if not rate_limiter.is_allowed(api_key, auth_result.get("rate_limit", 100)):
            return json.dumps({
                "success": False,
                "message": "Rate limit exceeded. Please try again later.",
                "error_code": "RATE_LIMIT_EXCEEDED",
            })

        # Call original function
        return func(*args, **kwargs)

    return wrapper
