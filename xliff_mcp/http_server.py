"""XLIFF MCP HTTP Server - For public deployment"""

import json
import logging
import os
from typing import Any, List, Dict, Optional
from mcp.server.fastmcp import FastMCP
from .xliff_processor import XliffProcessorService
from .tmx_processor import TmxProcessorService
from .models import TranslationReplacementData

# Configure logging to avoid stdout interference with HTTP
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server for HTTP deployment
# Use stateless HTTP for public deployment (no session persistence)
mcp = FastMCP("xliff-processor", stateless_http=True)

# Initialize processors
xliff_service = XliffProcessorService()
tmx_service = TmxProcessorService()

# Optional API key authentication
API_KEY = os.getenv("XLIFF_MCP_API_KEY", None)


def verify_api_key(api_key: Optional[str]) -> bool:
    """Verify API key if authentication is enabled"""
    if API_KEY is None:
        return True  # No authentication required
    return api_key == API_KEY


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
    if not verify_api_key(api_key):
        return json.dumps({
            "success": False,
            "message": "Invalid or missing API key",
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
    if not verify_api_key(api_key):
        return json.dumps({
            "success": False,
            "message": "Invalid or missing API key",
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
    if not verify_api_key(api_key):
        return json.dumps({
            "valid": False,
            "message": "Invalid or missing API key",
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
    if not verify_api_key(api_key):
        return json.dumps({
            "success": False,
            "message": "Invalid or missing API key",
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
    if not verify_api_key(api_key):
        return json.dumps({
            "success": False,
            "message": "Invalid or missing API key",
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
    if not verify_api_key(api_key):
        return json.dumps({
            "valid": False,
            "message": "Invalid or missing API key",
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
        "version": "0.1.0",
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
        "authentication_required": API_KEY is not None,
        "endpoint": "/mcp"
    })


def main():
    """Run the HTTP MCP server"""
    import os
    # Set port to avoid conflicts
    os.environ['MCP_HTTP_PORT'] = '8080'
    
    logger.info("Starting XLIFF MCP HTTP server on port 8080")
    if API_KEY:
        logger.info("API key authentication enabled")
    else:
        logger.warning("No API key set - server is publicly accessible")
    
    # Run with streamable HTTP transport for public access
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()