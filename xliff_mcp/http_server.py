"""XLIFF MCP HTTP Server - For public deployment."""

import json
import logging
import os
from typing import Optional
from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse
from . import __version__
from .auth import APIKeyAuth, RateLimiter
from .xliff_processor import XliffProcessorService
from .tmx_processor import TmxProcessorService

# Configure logging to avoid stdout interference with HTTP
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

HTTP_HOST = os.getenv("HOST", "0.0.0.0")
HTTP_PORT = int(os.getenv("PORT", "8000"))
HTTP_ENDPOINT = "/mcp"

# Initialize FastMCP server for HTTP deployment.
mcp = FastMCP(
    "xliff-processor",
    stateless_http=True,
    host=HTTP_HOST,
    port=HTTP_PORT,
    streamable_http_path=HTTP_ENDPOINT,
)

# Initialize processors
xliff_service = XliffProcessorService()
tmx_service = TmxProcessorService()
api_auth = APIKeyAuth()
rate_limiter = RateLimiter()

def _authorize_request(api_key: Optional[str]) -> dict | None:
    """Validate authentication and rate limit state for a tool request."""
    auth_result = api_auth.verify_key(api_key)
    if not auth_result["valid"]:
        return auth_result

    if api_auth.enabled and not rate_limiter.is_allowed(api_key or "", auth_result["rate_limit"]):
        return {
            "valid": False,
            "reason": "Rate limit exceeded. Please try again later.",
            "error_code": "RATE_LIMIT_EXCEEDED",
        }

    return None


@mcp.custom_route("/health", methods=["GET"], include_in_schema=False)
async def health_check(_: Request) -> JSONResponse:
    """Provide a simple health endpoint for containers and reverse proxies."""
    return JSONResponse({
        "status": "ok",
        "server_name": "XLIFF MCP Server",
        "version": __version__,
        "endpoint": HTTP_ENDPOINT,
        "authentication_required": api_auth.enabled,
    })


@mcp.tool()
def process_xliff(file_name: str, content: str, api_key: Optional[str] = None) -> str:
    """
    Process XLIFF content and extract translation units.
    
    Args:
        file_name: Name of the XLIFF file
        content: XLIFF file content as string
        api_key: Optional API key for authentication
        
    Returns:
        JSON string containing list of translation units with their metadata
    """
    auth_error = _authorize_request(api_key)
    if auth_error is not None:
        return json.dumps({
            "success": False,
            "message": f"Authentication failed: {auth_error['reason']}",
            "data": []
        })
    
    try:
        data = xliff_service.process_xliff(file_name, content)
        result = {
            "success": True,
            "message": f"Successfully processed {len(data)} translation units",
            "data": [item.model_dump() for item in data]
        }
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Failed to process XLIFF: {str(e)}")
        return json.dumps({
            "success": False,
            "message": f"Error processing XLIFF: {str(e)}",
            "data": []
        })


@mcp.tool()
def process_xliff_with_tags(file_name: str, content: str, api_key: Optional[str] = None) -> str:
    """
    Process XLIFF content preserving internal tags for AI translation.
    
    Args:
        file_name: Name of the XLIFF file
        content: XLIFF file content as string
        api_key: Optional API key for authentication
        
    Returns:
        JSON string containing translation units with preserved tags
    """
    auth_error = _authorize_request(api_key)
    if auth_error is not None:
        return json.dumps({
            "success": False,
            "message": f"Authentication failed: {auth_error['reason']}",
            "data": []
        })
    
    try:
        data = xliff_service.process_xliff_with_tags(file_name, content)
        result = {
            "success": True,
            "message": f"Successfully processed {len(data)} translation units with tags",
            "data": [item.model_dump() for item in data]
        }
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Failed to process XLIFF with tags: {str(e)}")
        return json.dumps({
            "success": False,
            "message": f"Error processing XLIFF with tags: {str(e)}",
            "data": []
        })


@mcp.tool()
def validate_xliff(content: str, api_key: Optional[str] = None) -> str:
    """
    Validate XLIFF content format.
    
    Args:
        content: XLIFF file content to validate
        api_key: Optional API key for authentication
        
    Returns:
        JSON string with validation result
    """
    auth_error = _authorize_request(api_key)
    if auth_error is not None:
        return json.dumps({
            "valid": False,
            "message": f"Authentication failed: {auth_error['reason']}",
            "unit_count": 0
        })
    
    try:
        valid, message, unit_count = xliff_service.validate_xliff(content)
        return json.dumps({
            "valid": valid,
            "message": message,
            "unit_count": unit_count
        })
    except Exception as e:
        logger.error(f"Failed to validate XLIFF: {str(e)}")
        return json.dumps({
            "valid": False,
            "message": f"Validation error: {str(e)}",
            "unit_count": 0
        })


@mcp.tool()
def replace_xliff_targets(content: str, translations: str, api_key: Optional[str] = None) -> str:
    """
    Replace target translations in XLIFF file.
    
    Args:
        content: Original XLIFF file content
        translations: JSON string containing list of translations
        api_key: Optional API key for authentication
        
    Returns:
        JSON string with updated XLIFF content and replacement count
    """
    auth_error = _authorize_request(api_key)
    if auth_error is not None:
        return json.dumps({
            "success": False,
            "message": f"Authentication failed: {auth_error['reason']}",
            "content": content,
            "replacements_count": 0
        })
    
    try:
        translations_data = json.loads(translations)
        if not isinstance(translations_data, list):
            translations_data = [translations_data]
        
        updated_content, replacements_count = xliff_service.replace_xliff_targets(
            content, translations_data
        )
        
        return json.dumps({
            "success": True,
            "message": f"Successfully replaced {replacements_count} translations",
            "content": updated_content,
            "replacements_count": replacements_count
        })
    except json.JSONDecodeError as e:
        return json.dumps({
            "success": False,
            "message": f"Invalid translations JSON: {str(e)}",
            "content": content,
            "replacements_count": 0
        })
    except Exception as e:
        logger.error(f"Failed to replace XLIFF targets: {str(e)}")
        return json.dumps({
            "success": False,
            "message": f"Error replacing targets: {str(e)}",
            "content": content,
            "replacements_count": 0
        })


@mcp.tool()
def process_tmx(file_name: str, content: str, api_key: Optional[str] = None) -> str:
    """
    Process TMX content and extract translation units.
    
    Args:
        file_name: Name of the TMX file
        content: TMX file content as string
        api_key: Optional API key for authentication
        
    Returns:
        JSON string containing list of translation units with metadata
    """
    auth_error = _authorize_request(api_key)
    if auth_error is not None:
        return json.dumps({
            "success": False,
            "message": f"Authentication failed: {auth_error['reason']}",
            "data": []
        })
    
    try:
        data = tmx_service.process_tmx(file_name, content)
        result = {
            "success": True,
            "message": f"Successfully processed {len(data)} translation units",
            "data": [item.model_dump() for item in data]
        }
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Failed to process TMX: {str(e)}")
        return json.dumps({
            "success": False,
            "message": f"Error processing TMX: {str(e)}",
            "data": []
        })


@mcp.tool()
def validate_tmx(content: str, api_key: Optional[str] = None) -> str:
    """
    Validate TMX content format.
    
    Args:
        content: TMX file content to validate
        api_key: Optional API key for authentication
        
    Returns:
        JSON string with validation result
    """
    auth_error = _authorize_request(api_key)
    if auth_error is not None:
        return json.dumps({
            "valid": False,
            "message": f"Authentication failed: {auth_error['reason']}",
            "unit_count": 0
        })
    
    try:
        valid, message, unit_count = tmx_service.validate_tmx(content)
        return json.dumps({
            "valid": valid,
            "message": message,
            "unit_count": unit_count
        })
    except Exception as e:
        logger.error(f"Failed to validate TMX: {str(e)}")
        return json.dumps({
            "valid": False,
            "message": f"Validation error: {str(e)}",
            "unit_count": 0
        })


@mcp.tool()
def get_server_info(api_key: Optional[str] = None) -> str:
    """
    Get server information and available tools.
    
    Args:
        api_key: Optional API key for authentication
        
    Returns:
        JSON string with server information
    """
    return json.dumps({
        "server_name": "XLIFF MCP Server",
        "version": __version__,
        "description": "Process XLIFF and TMX translation files via MCP",
        "available_tools": [
            "process_xliff",
            "process_xliff_with_tags", 
            "validate_xliff",
            "replace_xliff_targets",
            "process_tmx",
            "validate_tmx",
            "get_server_info"
        ],
        "authentication_required": api_auth.enabled,
        "endpoint": HTTP_ENDPOINT,
    })


def main():
    """Run the HTTP MCP server"""

    logger.info("Starting XLIFF MCP HTTP server on %s:%s%s", HTTP_HOST, HTTP_PORT, HTTP_ENDPOINT)
    if api_auth.enabled:
        logger.info("API key authentication enabled")
    else:
        logger.warning("No API key set - server is publicly accessible")

    # Run with streamable HTTP transport for public access
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
