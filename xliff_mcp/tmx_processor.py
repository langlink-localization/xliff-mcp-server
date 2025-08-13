"""TMX processing service"""

from translate.storage import tmx
from typing import List, Tuple
import logging
import re
from .models import TmxData

logger = logging.getLogger(__name__)


class TmxProcessorService:
    """TMX file processing service"""
    
    @staticmethod
    def process_tmx(file_name: str, content: str) -> List[TmxData]:
        """
        Parse TMX content and extract translation units
        
        Args:
            file_name: File name
            content: TMX file content
            
        Returns:
            List of TmxData objects
        """
        try:
            store = tmx.tmxfile()
            store.parse(content.encode('utf-8'))
            
            data = []
            
            for index, unit in enumerate(store.units):
                if unit.isheader():
                    continue
                
                unit_id = unit.getid()
                if not unit_id:
                    unit_id = str(index + 1)
                
                source = unit.source or ""
                target = unit.target or ""
                
                # Get TMX specific attributes
                creator = ""
                changer = ""
                context_id = ""
                
                if hasattr(unit, 'xmlelement') and unit.xmlelement is not None:
                    element = unit.xmlelement
                    creator = element.get('creationid', '')
                    changer = element.get('changeid', '')
                    
                    # Find context property
                    props = element.xpath('.//prop[@type="x-context"]')
                    if props:
                        context_id = props[0].text or ""
                
                # Clean tags
                no_tag_source = TmxProcessorService.clean_tmx_tags(source)
                no_tag_target = TmxProcessorService.clean_tmx_tags(target)
                
                # Get language info
                src_lang = ""
                tgt_lang = ""
                
                if hasattr(unit, 'xmlelement') and unit.xmlelement is not None:
                    tuvs = unit.xmlelement.xpath('.//tuv')
                    if len(tuvs) >= 2:
                        src_lang = tuvs[0].get('xml:lang') or tuvs[0].get('lang') or ""
                        tgt_lang = tuvs[1].get('xml:lang') or tuvs[1].get('lang') or ""
                        src_lang = src_lang.lower()
                        tgt_lang = tgt_lang.lower()
                
                tmx_data = TmxData(
                    id=unit_id,
                    fileName=file_name,
                    segNumber=index + 1,
                    percent=-1,  # TMX usually doesn't have percent
                    source=source,
                    target=target,
                    noTagSource=no_tag_source,
                    noTagTarget=no_tag_target,
                    contextId=context_id,
                    creator=creator,
                    changer=changer,
                    srcLang=src_lang,
                    tgtLang=tgt_lang
                )
                
                data.append(tmx_data)
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to process TMX file: {str(e)}")
            raise
    
    @staticmethod
    def validate_tmx(content: str) -> Tuple[bool, str, int]:
        """
        Validate TMX content format
        
        Args:
            content: TMX file content
            
        Returns:
            (is_valid, message, unit_count)
        """
        try:
            store = tmx.tmxfile()
            store.parse(content.encode('utf-8'))
            
            unit_count = sum(1 for unit in store.units if not unit.isheader())
            
            return True, "TMX format is valid", unit_count
        except Exception as e:
            return False, f"Invalid TMX format: {str(e)}", 0
    
    @staticmethod
    def clean_tmx_tags(text: str) -> str:
        """
        Remove TMX tags from text
        
        Args:
            text: Text with TMX tags
            
        Returns:
            Text without tags
        """
        if not text:
            return ""
        
        # Remove TMX inline tags like <bpt>, <ept>, <ph>, <it>, <hi>
        patterns = [
            r'<bpt[^>]*>.*?</bpt>',
            r'<ept[^>]*>.*?</ept>',
            r'<ph[^>]*/>',
            r'<ph[^>]*>.*?</ph>',
            r'<it[^>]*>.*?</it>',
            r'<hi[^>]*>.*?</hi>',
            r'<ut[^>]*>.*?</ut>',
        ]
        
        cleaned = text
        for pattern in patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Remove any remaining XML-like tags
        cleaned = re.sub(r'<[^>]+>', '', cleaned)
        
        # Clean up multiple spaces
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        return cleaned.strip()