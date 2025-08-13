"""Authentication and security utilities for XLIFF MCP Server"""

import hashlib
import hmac
import json
import time
from typing import Optional, Dict, Any
import os


class APIKeyAuth:
    """Simple API key authentication"""
    
    def __init__(self):
        self.api_keys = self._load_api_keys()
    
    def _load_api_keys(self) -> Dict[str, Dict[str, Any]]:
        """Load API keys from environment or file"""
        keys = {}
        
        # Load from environment variable (comma-separated)
        env_keys = os.getenv("XLIFF_MCP_API_KEYS", "")
        if env_keys:
            for key in env_keys.split(","):
                key = key.strip()
                if key:
                    keys[key] = {
                        "name": "env_key",
                        "permissions": ["all"],
                        "rate_limit": 100  # requests per minute
                    }
        
        # Load from file if exists
        try:
            with open("api_keys.json", "r") as f:
                file_keys = json.load(f)
                keys.update(file_keys)
        except FileNotFoundError:
            pass
        
        return keys
    
    def verify_key(self, api_key: Optional[str]) -> Dict[str, Any]:
        """Verify API key and return permissions"""
        if not api_key:
            return {"valid": False, "reason": "No API key provided"}
        
        if api_key in self.api_keys:
            return {
                "valid": True,
                "permissions": self.api_keys[api_key].get("permissions", ["all"]),
                "rate_limit": self.api_keys[api_key].get("rate_limit", 100)
            }
        
        return {"valid": False, "reason": "Invalid API key"}


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
    def get_headers() -> Dict[str, str]:
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
        api_key = kwargs.get('api_key')
        
        # Verify API key
        auth_result = api_auth.verify_key(api_key)
        if not auth_result["valid"]:
            return json.dumps({
                "success": False,
                "message": f"Authentication failed: {auth_result.get('reason', 'Invalid key')}",
                "error_code": "AUTH_FAILED"
            })
        
        # Check rate limit
        if not rate_limiter.is_allowed(api_key, auth_result.get("rate_limit", 100)):
            return json.dumps({
                "success": False,
                "message": "Rate limit exceeded. Please try again later.",
                "error_code": "RATE_LIMIT_EXCEEDED"
            })
        
        # Call original function
        return func(*args, **kwargs)
    
    return wrapper