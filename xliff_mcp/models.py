"""Data models for XLIFF MCP Server"""

from pydantic import BaseModel
from typing import Optional, List, Union


class XliffData(BaseModel):
    """XLIFF translation unit data model"""
    fileName: str
    segNumber: int
    unitId: str  
    percent: float
    source: str
    target: str
    srcLang: str
    tgtLang: str


class TmxData(BaseModel):
    """TMX translation unit data model"""
    id: Union[int, str]
    fileName: str
    segNumber: int
    percent: float
    source: str
    target: str
    noTagSource: Optional[str] = None
    noTagTarget: Optional[str] = None
    contextId: Optional[str] = None
    creator: Optional[str] = None
    changer: Optional[str] = None
    srcLang: Optional[str] = None
    tgtLang: Optional[str] = None


class TranslationReplacementData(BaseModel):
    """Translation replacement data model"""
    segNumber: int
    unitId: Optional[str] = None
    aiResult: Optional[str] = None
    mtResult: Optional[str] = None