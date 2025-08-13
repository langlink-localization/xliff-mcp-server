"""XLIFF processing service"""

from translate.storage import xliff
from typing import List, Dict, Any, Tuple
import logging
import re
from .models import XliffData

logger = logging.getLogger(__name__)


class XliffProcessorService:
    """XLIFF file processing service"""
    
    @staticmethod
    def process_xliff(file_name: str, content: str) -> List[XliffData]:
        """
        Parse XLIFF content and extract translation units
        
        Args:
            file_name: File name
            content: XLIFF file content
            
        Returns:
            List of XliffData objects
        """
        try:
            store = xliff.xlifffile()
            store.parse(content.encode('utf-8'))
            
            data = []
            
            # Get file-level language attributes
            file_src_lang = ""
            file_tgt_lang = ""
            if hasattr(store, 'document') and store.document is not None:
                root = store.document.getroot()
                if root is not None:
                    file_node = root.find('.//{urn:oasis:names:tc:xliff:document:1.2}file')
                    if file_node is None:
                        file_node = root.find('.//file')
                    
                    if file_node is not None:
                        file_src_lang = (file_node.get('source-language') or "").lower()
                        file_tgt_lang = (file_node.get('target-language') or "").lower()
            
            for index, unit in enumerate(store.units):
                if unit.isheader():
                    continue
                
                unit_full_id = unit.getid()
                if not unit_full_id:
                    continue
                
                # Extract real unit ID
                if '\x04' in unit_full_id:
                    unit_id = unit_full_id.split('\x04')[-1]
                else:
                    unit_id = unit_full_id
                
                # Get translation percentage
                percent = -1
                if hasattr(unit, 'xmlelement'):
                    element = unit.xmlelement
                    percent_value = (
                        element.get('percent') or 
                        element.get('mq:percent') or 
                        element.get('{urn:oasis:names:tc:xliff:document:2.0}percent') or
                        element.get('{urn:oasis:names:tc:xliff:document:1.2}percent')
                    )
                    if percent_value:
                        try:
                            percent = float(percent_value)
                        except ValueError:
                            percent = -1
                
                # Get languages
                src_lang = ""
                tgt_lang = ""
                if hasattr(unit, 'xmlelement'):
                    element = unit.xmlelement
                    src_lang = (element.get('source-language') or "").lower()
                    tgt_lang = (element.get('target-language') or "").lower()
                
                if not src_lang:
                    src_lang = file_src_lang
                if not tgt_lang:
                    tgt_lang = file_tgt_lang
                
                xliff_data = XliffData(
                    fileName=file_name,
                    segNumber=index + 1,
                    unitId=unit_id,
                    percent=percent,
                    source=unit.source or "",
                    target=unit.target or "",
                    srcLang=src_lang,
                    tgtLang=tgt_lang
                )
                
                data.append(xliff_data)
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to process XLIFF file: {str(e)}")
            raise
    
    @staticmethod
    def validate_xliff(content: str) -> Tuple[bool, str, int]:
        """
        Validate XLIFF content format
        
        Args:
            content: XLIFF file content
            
        Returns:
            (is_valid, message, unit_count)
        """
        try:
            store = xliff.xlifffile()
            store.parse(content.encode('utf-8'))
            
            unit_count = sum(1 for unit in store.units if not unit.isheader())
            
            return True, "XLIFF format is valid", unit_count
        except Exception as e:
            return False, f"Invalid XLIFF format: {str(e)}", 0
    
    @staticmethod
    def process_xliff_with_tags(file_name: str, content: str) -> List[XliffData]:
        """
        Process XLIFF preserving internal tags for AI translation
        
        Args:
            file_name: File name
            content: XLIFF file content
            
        Returns:
            List of XliffData objects with preserved tags
        """
        try:
            store = xliff.xlifffile()
            store.parse(content.encode('utf-8'))
            
            data = []
            unit_index = 0
            
            for unit in store.units:
                if unit.isheader():
                    continue
                
                unit_full_id = unit.getid()
                if not unit_full_id:
                    continue
                
                if '\x04' in unit_full_id:
                    unit_id = unit_full_id.split('\x04')[-1]
                else:
                    unit_id = unit_full_id
                
                unit_index += 1
                
                percent = -1
                if hasattr(unit, 'xmlelement'):
                    element = unit.xmlelement
                    percent_value = (
                        element.get('percent') or 
                        element.get('mq:percent') or 
                        element.get('{urn:oasis:names:tc:xliff:document:2.0}percent') or
                        element.get('{urn:oasis:names:tc:xliff:document:1.2}percent')
                    )
                    if percent_value:
                        try:
                            percent = float(percent_value)
                        except ValueError:
                            percent = -1
                
                # Extract content using regex to preserve tags
                source = XliffProcessorService._extract_element_content(content, 'source', unit_id)
                target = XliffProcessorService._extract_element_content(content, 'target', unit_id)
                
                if not source:
                    source = unit.source or ""
                if not target:
                    target = unit.target or ""
                
                src_lang = ""
                tgt_lang = ""
                if hasattr(unit, 'xmlelement'):
                    element = unit.xmlelement
                    src_lang = (element.get('source-language') or "").lower()
                    tgt_lang = (element.get('target-language') or "").lower()
                
                if not src_lang or not tgt_lang:
                    file_src_lang, file_tgt_lang = XliffProcessorService._get_file_languages(content)
                    if not src_lang:
                        src_lang = file_src_lang
                    if not tgt_lang:
                        tgt_lang = file_tgt_lang
                
                xliff_data = XliffData(
                    fileName=file_name,
                    segNumber=unit_index,
                    unitId=unit_id,
                    percent=percent,
                    source=source,
                    target=target,
                    srcLang=src_lang,
                    tgtLang=tgt_lang
                )
                
                data.append(xliff_data)
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to process XLIFF with tags: {str(e)}")
            raise
    
    @staticmethod
    def _extract_element_content(xml_content: str, element_name: str, unit_id: str) -> str:
        """Extract element content from raw XML preserving format"""
        try:
            unit_pattern = rf'<(?:trans-unit|unit)[^>]*id=["\']{re.escape(unit_id)}["\'][^>]*>([\s\S]*?)</(?:trans-unit|unit)>'
            
            unit_match = re.search(unit_pattern, xml_content, re.IGNORECASE)
            if not unit_match:
                return ""
            
            unit_content = unit_match.group(1)
            
            element_pattern = rf'<{element_name}[^>]*>([\s\S]*?)</{element_name}>'
            
            element_match = re.search(element_pattern, unit_content, re.IGNORECASE)
            if not element_match:
                return ""
            
            content = element_match.group(1).strip()
            
            content = XliffProcessorService._decode_html_entities(content)
            
            return content
        except Exception as e:
            logger.error(f"Failed to extract {element_name} content: {str(e)}")
            return ""
    
    @staticmethod
    def _get_file_languages(xml_content: str) -> Tuple[str, str]:
        """Get language info from file level"""
        try:
            file_pattern = r'<file[^>]*source-language=["\'"]([^"\']*)["\'][^>]*target-language=["\'"]([^"\']*)["\'][^>]*>'
            match = re.search(file_pattern, xml_content, re.IGNORECASE)
            if match:
                return match.group(1).lower(), match.group(2).lower()
            
            file_pattern2 = r'<file[^>]*target-language=["\'"]([^"\']*)["\'][^>]*source-language=["\'"]([^"\']*)["\'][^>]*>'
            match2 = re.search(file_pattern2, xml_content, re.IGNORECASE)
            if match2:
                return match2.group(2).lower(), match2.group(1).lower()
            
            return "", ""
        except Exception:
            return "", ""
    
    @staticmethod
    def _decode_html_entities(text: str) -> str:
        """Decode HTML entities"""
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        text = text.replace('&#39;', "'")
        text = text.replace('&nbsp;', ' ')
        
        return text
    
    @staticmethod
    def replace_xliff_targets(content: str, translations: List[dict]) -> Tuple[str, int]:
        """
        Replace target content in XLIFF file using string replacement
        
        Args:
            content: Original XLIFF file content
            translations: List of translation data with segNumber, aiResult, mtResult
            
        Returns:
            (updated_content, replacement_count)
        """
        updated_content = content
        replacements_count = 0
        
        for translation in translations:
            if not translation.get('aiResult') and not translation.get('mtResult'):
                continue
            
            new_target_content = translation.get('aiResult') or translation.get('mtResult') or ''
            unit_id = translation.get('unitId') or str(translation['segNumber'])
            
            unit_pattern = rf'(<(?:trans-unit|unit)[^>]*id=["\']{re.escape(unit_id)}["\'][^>]*>)([\s\S]*?)(</(?:trans-unit|unit)>)'
            unit_match = re.search(unit_pattern, updated_content, re.IGNORECASE)
            
            if not unit_match:
                continue
            
            unit_start = unit_match.group(1)
            unit_content = unit_match.group(2)
            unit_end = unit_match.group(3)
            
            target_pattern = r'<target[^>]*>[\s\S]*?</target>'
            target_match = re.search(target_pattern, unit_content, re.IGNORECASE)
            
            if target_match:
                existing_target = target_match.group(0)
                
                target_attr_pattern = r'<target([^>]*?)>'
                target_attr_match = re.search(target_attr_pattern, existing_target, re.IGNORECASE)
                target_attributes = target_attr_match.group(1) if target_attr_match else ''
                
                new_target = f'<target{target_attributes}>{new_target_content}</target>'
                new_unit_content = unit_content.replace(existing_target, new_target)
                
                updated_content = updated_content.replace(
                    unit_match.group(0),
                    unit_start + new_unit_content + unit_end
                )
                
                replacements_count += 1
            else:
                source_pattern = r'(<source[^>]*>[\s\S]*?</source>)'
                source_match = re.search(source_pattern, unit_content, re.IGNORECASE)
                
                if source_match:
                    new_target = f'\n        <target>{new_target_content}</target>'
                    new_unit_content = unit_content.replace(
                        source_match.group(0),
                        source_match.group(0) + new_target
                    )
                    
                    updated_content = updated_content.replace(
                        unit_match.group(0),
                        unit_start + new_unit_content + unit_end
                    )
                    
                    replacements_count += 1
        
        return updated_content, replacements_count