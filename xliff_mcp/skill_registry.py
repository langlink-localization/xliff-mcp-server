"""Backward-compatible re-export for runtime workflow registration."""

from .workflows import (
    RegisteredSkills,
    SKILL_CATALOG_URI,
    SKILL_DEFINITIONS,
    SKILL_DETAIL_TEMPLATE,
    SkillDefinition,
    get_skill,
    get_skill_descriptors,
    list_skill_names,
    list_skill_resource_templates,
    list_skill_resources,
    register_skills,
)

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
