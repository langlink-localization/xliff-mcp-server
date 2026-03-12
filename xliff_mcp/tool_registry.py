"""Shared MCP tool registration for stdio and HTTP transports."""

import json
import logging
from dataclasses import dataclass
from typing import Callable, Optional, Sequence

from mcp.server.fastmcp import FastMCP


AuthValidator = Callable[[Optional[str]], dict | None]
AuthEnabledGetter = Callable[[], bool]
EndpointGetter = Callable[[], Optional[str]]


@dataclass(frozen=True)
class RegisteredTools:
    """Exported tool callables for direct imports and tests."""

    process_xliff: Callable[..., str]
    process_xliff_with_tags: Callable[..., str]
    validate_xliff: Callable[..., str]
    replace_xliff_targets: Callable[..., str]
    process_tmx: Callable[..., str]
    validate_tmx: Callable[..., str]
    get_server_info: Callable[..., str]


def _dump_json(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _tool_error_message(prefix: str, error: Exception) -> str:
    return f"{prefix}: {str(error)}"


def register_tools(
    mcp: FastMCP,
    *,
    logger: logging.Logger,
    xliff_service,
    tmx_service,
    version: str,
    transport: str,
    endpoint_getter: EndpointGetter = lambda: None,
    auth_validator: Optional[AuthValidator] = None,
    auth_enabled_getter: AuthEnabledGetter = lambda: False,
    prompt_names: Sequence[str] = (),
    resource_uris: Sequence[str] = (),
    resource_templates: Sequence[str] = (),
    skill_descriptors: Sequence[dict[str, object]] = (),
) -> RegisteredTools:
    """Register the shared MCP tools on a FastMCP instance."""

    def require_auth(api_key: Optional[str]) -> dict | None:
        if auth_validator is None:
            return None
        return auth_validator(api_key)

    def auth_failure_response(reason: str, *, success_key: str = "success", content: str = "", data=None) -> str:
        payload = {
            success_key: False,
            "message": f"Authentication failed: {reason}",
        }
        if data is not None:
            payload["data"] = data
        if content:
            payload["content"] = content
        if success_key == "success" and "replacements_count" not in payload and content:
            payload["replacements_count"] = 0
        if success_key == "valid":
            payload["unit_count"] = 0
        return _dump_json(payload)

    @mcp.tool()
    def process_xliff(file_name: str, content: str, api_key: Optional[str] = None) -> str:
        auth_error = require_auth(api_key)
        if auth_error is not None:
            return auth_failure_response(auth_error["reason"], data=[])

        try:
            data = xliff_service.process_xliff(file_name, content)
            return _dump_json({
                "success": True,
                "message": f"Successfully processed {len(data)} translation units",
                "data": [item.model_dump() for item in data],
            })
        except Exception as error:
            logger.error("Failed to process XLIFF: %s", error)
            return _dump_json({
                "success": False,
                "message": _tool_error_message("Error processing XLIFF", error),
                "data": [],
            })

    @mcp.tool()
    def process_xliff_with_tags(file_name: str, content: str, api_key: Optional[str] = None) -> str:
        auth_error = require_auth(api_key)
        if auth_error is not None:
            return auth_failure_response(auth_error["reason"], data=[])

        try:
            data = xliff_service.process_xliff_with_tags(file_name, content)
            return _dump_json({
                "success": True,
                "message": f"Successfully processed {len(data)} translation units with tags",
                "data": [item.model_dump() for item in data],
            })
        except Exception as error:
            logger.error("Failed to process XLIFF with tags: %s", error)
            return _dump_json({
                "success": False,
                "message": _tool_error_message("Error processing XLIFF with tags", error),
                "data": [],
            })

    @mcp.tool()
    def validate_xliff(content: str, api_key: Optional[str] = None) -> str:
        auth_error = require_auth(api_key)
        if auth_error is not None:
            return auth_failure_response(auth_error["reason"], success_key="valid")

        try:
            valid, message, unit_count = xliff_service.validate_xliff(content)
            return _dump_json({
                "valid": valid,
                "message": message,
                "unit_count": unit_count,
            })
        except Exception as error:
            logger.error("Failed to validate XLIFF: %s", error)
            return _dump_json({
                "valid": False,
                "message": _tool_error_message("Validation error", error),
                "unit_count": 0,
            })

    @mcp.tool()
    def replace_xliff_targets(content: str, translations: str, api_key: Optional[str] = None) -> str:
        auth_error = require_auth(api_key)
        if auth_error is not None:
            return auth_failure_response(auth_error["reason"], content=content)

        try:
            translations_data = json.loads(translations)
            if not isinstance(translations_data, list):
                translations_data = [translations_data]

            updated_content, replacements_count = xliff_service.replace_xliff_targets(content, translations_data)
            return _dump_json({
                "success": True,
                "message": f"Successfully replaced {replacements_count} translations",
                "content": updated_content,
                "replacements_count": replacements_count,
            })
        except json.JSONDecodeError as error:
            return _dump_json({
                "success": False,
                "message": f"Invalid translations JSON: {str(error)}",
                "content": content,
                "replacements_count": 0,
            })
        except Exception as error:
            logger.error("Failed to replace XLIFF targets: %s", error)
            return _dump_json({
                "success": False,
                "message": _tool_error_message("Error replacing targets", error),
                "content": content,
                "replacements_count": 0,
            })

    @mcp.tool()
    def process_tmx(file_name: str, content: str, api_key: Optional[str] = None) -> str:
        auth_error = require_auth(api_key)
        if auth_error is not None:
            return auth_failure_response(auth_error["reason"], data=[])

        try:
            data = tmx_service.process_tmx(file_name, content)
            return _dump_json({
                "success": True,
                "message": f"Successfully processed {len(data)} translation units",
                "data": [item.model_dump() for item in data],
            })
        except Exception as error:
            logger.error("Failed to process TMX: %s", error)
            return _dump_json({
                "success": False,
                "message": _tool_error_message("Error processing TMX", error),
                "data": [],
            })

    @mcp.tool()
    def validate_tmx(content: str, api_key: Optional[str] = None) -> str:
        auth_error = require_auth(api_key)
        if auth_error is not None:
            return auth_failure_response(auth_error["reason"], success_key="valid")

        try:
            valid, message, unit_count = tmx_service.validate_tmx(content)
            return _dump_json({
                "valid": valid,
                "message": message,
                "unit_count": unit_count,
            })
        except Exception as error:
            logger.error("Failed to validate TMX: %s", error)
            return _dump_json({
                "valid": False,
                "message": _tool_error_message("Validation error", error),
                "unit_count": 0,
            })

    @mcp.tool()
    def get_server_info(api_key: Optional[str] = None) -> str:
        del api_key
        payload = {
            "server_name": "XLIFF MCP Server",
            "version": version,
            "description": "Process XLIFF and TMX translation files via MCP",
            "available_tools": [
                "process_xliff",
                "process_xliff_with_tags",
                "validate_xliff",
                "replace_xliff_targets",
                "process_tmx",
                "validate_tmx",
                "get_server_info",
            ],
            "available_prompts": list(prompt_names),
            "available_resources": list(resource_uris),
            "available_resource_templates": list(resource_templates),
            "available_skills": list(skill_descriptors),
        }
        endpoint = endpoint_getter()
        if endpoint is not None:
            payload["endpoint"] = endpoint
            payload["authentication_required"] = auth_enabled_getter()
        else:
            payload["transport"] = transport
        return _dump_json(payload)

    return RegisteredTools(
        process_xliff=process_xliff,
        process_xliff_with_tags=process_xliff_with_tags,
        validate_xliff=validate_xliff,
        replace_xliff_targets=replace_xliff_targets,
        process_tmx=process_tmx,
        validate_tmx=validate_tmx,
        get_server_info=get_server_info,
    )
