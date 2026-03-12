"""XLIFF MCP Server - Main server implementation."""

import logging
from mcp.server.fastmcp import FastMCP
from . import __version__
from .skills import (
    get_skill_descriptors,
    list_skill_names,
    list_skill_resource_templates,
    list_skill_resources,
    register_skills,
)
from .tool_registry import register_tools
from .xliff_processor import XliffProcessorService
from .tmx_processor import TmxProcessorService

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
registered_skills = register_skills(mcp)
registered_tools = register_tools(
    mcp,
    logger=logger,
    xliff_service=xliff_service,
    tmx_service=tmx_service,
    version=__version__,
    transport="stdio",
    prompt_names=list_skill_names(),
    resource_uris=list_skill_resources(),
    resource_templates=list_skill_resource_templates(),
    skill_descriptors=get_skill_descriptors(),
)

process_xliff = registered_tools.process_xliff
process_xliff_with_tags = registered_tools.process_xliff_with_tags
validate_xliff = registered_tools.validate_xliff
replace_xliff_targets = registered_tools.replace_xliff_targets
process_tmx = registered_tools.process_tmx
validate_tmx = registered_tools.validate_tmx
get_server_info = registered_tools.get_server_info
prepare_xliff_for_translation = registered_skills.prepare_xliff_for_translation
translate_xliff_with_tags = registered_skills.translate_xliff_with_tags
replace_xliff_targets_from_translations = (
    registered_skills.replace_xliff_targets_from_translations
)
inspect_tmx_translation_memory = registered_skills.inspect_tmx_translation_memory
skill_catalog = registered_skills.skill_catalog
describe_skill = registered_skills.describe_skill


def main():
    """Run the MCP server"""
    # Run with stdio transport by default
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()
