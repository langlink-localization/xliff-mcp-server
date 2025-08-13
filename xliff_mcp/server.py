"""XLIFF MCP Server - Main server implementation"""

import json
import logging
from typing import Any, List, Dict
from mcp.server.fastmcp import FastMCP
from .xliff_processor import XliffProcessorService
from .tmx_processor import TmxProcessorService
from .models import TranslationReplacementData

# Configure logging to stderr to avoid stdout interference
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]  # This defaults to stderr
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("xliff-processor")

# Initialize processors
xliff_service = XliffProcessorService()
tmx_service = TmxProcessorService()


@mcp.tool()
def process_xliff(file_name: str, content: str) -> str:
    """
    Process XLIFF content and extract translation units.
    
    Args:
        file_name: Name of the XLIFF file
        content: XLIFF file content as string
        
    Returns:
        JSON string containing list of translation units with their metadata
    """
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
def process_xliff_with_tags(file_name: str, content: str) -> str:
    """
    Process XLIFF content preserving internal tags for AI translation.
    
    This tool preserves inline tags and markup, making it suitable for AI-assisted translation
    where maintaining formatting is crucial.
    
    Args:
        file_name: Name of the XLIFF file
        content: XLIFF file content as string
        
    Returns:
        JSON string containing translation units with preserved tags
    """
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
def validate_xliff(content: str) -> str:
    """
    Validate XLIFF content format.
    
    Args:
        content: XLIFF file content to validate
        
    Returns:
        JSON string with validation result including validity status and unit count
    """
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
def replace_xliff_targets(content: str, translations: str) -> str:
    """
    Replace target translations in XLIFF file.
    
    Args:
        content: Original XLIFF file content
        translations: JSON string containing list of translations with segNumber/unitId and aiResult/mtResult
        
    Returns:
        JSON string with updated XLIFF content and replacement count
    """
    try:
        # Parse translations JSON
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
def process_tmx(file_name: str, content: str) -> str:
    """
    Process TMX content and extract translation units.
    
    Args:
        file_name: Name of the TMX file
        content: TMX file content as string
        
    Returns:
        JSON string containing list of translation units with metadata
    """
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
def validate_tmx(content: str) -> str:
    """
    Validate TMX content format.
    
    Args:
        content: TMX file content to validate
        
    Returns:
        JSON string with validation result
    """
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


def main():
    """Run the MCP server"""
    # Run with stdio transport by default
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()