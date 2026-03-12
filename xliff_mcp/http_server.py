"""XLIFF MCP HTTP Server - For public deployment."""

import logging
import os
from typing import Optional
from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse
from . import __version__
from .auth import APIKeyAuth, RateLimiter
from .tool_registry import register_tools
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
registered_tools = register_tools(
    mcp,
    logger=logger,
    xliff_service=xliff_service,
    tmx_service=tmx_service,
    version=__version__,
    transport="streamable-http",
    endpoint_getter=lambda: HTTP_ENDPOINT,
    auth_validator=_authorize_request,
    auth_enabled_getter=lambda: api_auth.enabled,
)

process_xliff = registered_tools.process_xliff
process_xliff_with_tags = registered_tools.process_xliff_with_tags
validate_xliff = registered_tools.validate_xliff
replace_xliff_targets = registered_tools.replace_xliff_targets
process_tmx = registered_tools.process_tmx
validate_tmx = registered_tools.validate_tmx
get_server_info = registered_tools.get_server_info


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
