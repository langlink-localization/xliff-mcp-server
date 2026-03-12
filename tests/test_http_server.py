"""Pytest coverage for HTTP server configuration and auth behavior."""

from __future__ import annotations

import importlib
import json

import httpx
from xliff_mcp import __version__
from tests.samples import SAMPLE_XLIFF


def load_http_server(monkeypatch, api_keys: str | None = None):
    """Reload the HTTP server module with the desired auth environment."""
    if api_keys is None:
        monkeypatch.delenv("XLIFF_MCP_API_KEYS", raising=False)
        monkeypatch.delenv("XLIFF_MCP_API_KEY", raising=False)
    else:
        monkeypatch.setenv("XLIFF_MCP_API_KEYS", api_keys)
        monkeypatch.delenv("XLIFF_MCP_API_KEY", raising=False)

    import xliff_mcp.http_server as http_server

    return importlib.reload(http_server)


async def test_health_endpoint_reports_current_runtime(monkeypatch) -> None:
    http_server = load_http_server(monkeypatch)

    transport = httpx.ASGITransport(app=http_server.mcp.streamable_http_app())
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "server_name": "XLIFF MCP Server",
        "version": __version__,
        "endpoint": "/mcp",
        "authentication_required": False,
    }


def test_http_server_info_uses_current_version(monkeypatch) -> None:
    http_server = load_http_server(monkeypatch)
    info = json.loads(http_server.get_server_info())

    assert info["version"] == __version__
    assert info["endpoint"] == "/mcp"
    assert info["authentication_required"] is False
    assert "prepare_xliff_for_translation" in info["available_prompts"]
    assert "skills://catalog" in info["available_resources"]
    assert "skills://{skill_name}" in info["available_resource_templates"]
    assert any(
        skill["name"] == "inspect_tmx_translation_memory"
        for skill in info["available_skills"]
    )


def test_http_server_requires_api_key_when_configured(monkeypatch) -> None:
    http_server = load_http_server(monkeypatch, api_keys="secret-key")

    unauthorized = json.loads(http_server.validate_xliff(SAMPLE_XLIFF))
    authorized = json.loads(http_server.validate_xliff(SAMPLE_XLIFF, api_key="secret-key"))

    assert unauthorized["valid"] is False
    assert unauthorized["message"] == "Authentication failed: No API key provided"
    assert authorized["valid"] is True


def test_http_server_accepts_legacy_single_key_env(monkeypatch) -> None:
    monkeypatch.delenv("XLIFF_MCP_API_KEYS", raising=False)
    monkeypatch.setenv("XLIFF_MCP_API_KEY", "legacy-key")

    import xliff_mcp.http_server as http_server

    http_server = importlib.reload(http_server)
    result = json.loads(http_server.validate_xliff(SAMPLE_XLIFF, api_key="legacy-key"))

    assert result["valid"] is True
