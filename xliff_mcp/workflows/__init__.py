"""Workflow registration used by the MCP runtime."""

from .definitions import (
    SKILL_CATALOG_URI,
    SKILL_DETAIL_TEMPLATE,
    SKILL_DEFINITIONS,
    SkillDefinition,
    get_skill,
    get_skill_descriptors,
    list_skill_names,
    list_skill_resource_templates,
    list_skill_resources,
)
from .registry import RegisteredSkills, register_skills

__all__ = [
    "RegisteredSkills",
    "SKILL_CATALOG_URI",
    "SKILL_DEFINITIONS",
    "SKILL_DETAIL_TEMPLATE",
    "SkillDefinition",
    "get_skill",
    "get_skill_descriptors",
    "list_skill_names",
    "list_skill_resource_templates",
    "list_skill_resources",
    "register_skills",
]
