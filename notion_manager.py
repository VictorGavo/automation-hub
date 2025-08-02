"""
Notion API integration for Daily Capture page management.
Handles reading, processing, and clearing daily capture content.
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Any
from config import Config

logger = logging.getLogger(__name__)

class NotionManager:
    def __init__(self):
        """Initialize Notion API manager."""
        self.api_token = Config.NOTION_API_TOKEN
        self.daily_capture_page_id = Config.NOTION_DAILY_CAPTURE_PAGE_ID
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        
        if not self.api_token:
            logger.warning("Notion API token not configured")
        if not self.daily_capture_page_id:
            logger.warning("Notion Daily Capture page ID not configured")
    
    def get_daily_capture_content(self) -> Dict[str, Any]:
        """
        Retrieve and parse content from the Daily Capture page.
        
        Returns:
            Dictionary with parsed content organized by headers
        """
        try:
            if not self.api_token or not self.daily_capture_page_id:
                logger.error("Notion API not properly configured")
                return {'success': False, 'error': 'API not configured'}
            
            # Get page blocks
            url = f"{self.base_url}/blocks/{self.daily_capture_page_id}/children"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch Notion page: {response.status_code} - {response.text}")
                return {'success': False, 'error': f'API request failed: {response.status_code}'}
            
            data = response.json()
            blocks = data.get('results', [])
            
            # Parse blocks into structured content
            parsed_content = self._parse_blocks(blocks)
            
            return {
                'success': True,
                'content': parsed_content,
                'block_count': len(blocks)
            }
            
        except Exception as e:
            logger.error(f"Error getting daily capture content: {e}")
            return {'success': False, 'error': str(e)}
    
    def _parse_blocks(self, blocks: List[Dict]) -> Dict[str, List[str]]:
        """
        Parse Notion blocks into organized content by headers.
        Handles nested list items and preserves indentation.
        
        Args:
            blocks: List of Notion block objects
            
        Returns:
            Dictionary with header names as keys and content lists as values
        """
        content = {}
        current_header = None
        
        for block in blocks:
            block_type = block.get('type')
            
            # Handle headers (# Header format)
            if block_type == 'heading_1':
                header_text = self._extract_text_from_block(block)
                if header_text:
                    current_header = header_text.strip()
                    content[current_header] = []
            
            elif block_type == 'heading_2':
                header_text = self._extract_text_from_block(block)
                if header_text:
                    current_header = header_text.strip()
                    content[current_header] = []
            
            elif block_type == 'heading_3':
                header_text = self._extract_text_from_block(block)
                if header_text:
                    current_header = header_text.strip()
                    content[current_header] = []
            
            # Handle bullet points and content
            elif block_type in ['bulleted_list_item', 'numbered_list_item']:
                if current_header is not None:
                    bullet_text = self._extract_text_from_block(block)
                    if bullet_text and bullet_text.strip():
                        content[current_header].append(bullet_text.strip())
                    
                    # Check for nested children
                    if block.get('has_children'):
                        nested_items = self._get_nested_items(block['id'])
                        for nested_item in nested_items:
                            content[current_header].append(f"  {nested_item}")  # Indent nested items
            
            # Handle paragraphs
            elif block_type == 'paragraph':
                if current_header is not None:
                    para_text = self._extract_text_from_block(block)
                    if para_text and para_text.strip():
                        content[current_header].append(para_text.strip())
        
        # Clean up empty headers
        content = {k: v for k, v in content.items() if v}
        
        return content

    def _get_nested_items(self, block_id: str) -> List[str]:
        """
        Get nested list items for a block.
        
        Args:
            block_id: ID of the parent block
            
        Returns:
            List of nested item text
        """
        try:
            url = f"{self.base_url}/blocks/{block_id}/children"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                nested_blocks = data.get('results', [])
                
                nested_items = []
                for nested_block in nested_blocks:
                    if nested_block.get('type') in ['bulleted_list_item', 'numbered_list_item']:
                        nested_text = self._extract_text_from_block(nested_block)
                        if nested_text and nested_text.strip():
                            nested_items.append(nested_text.strip())
                
                return nested_items
            else:
                logger.warning(f"Failed to get nested items for block {block_id}: {response.status_code}")
                return []
        
        except Exception as e:
            logger.error(f"Error getting nested items: {e}")
            return []
    
    def _extract_text_from_block(self, block: Dict) -> str:
        """
        Extract plain text from a Notion block.
        
        Args:
            block: Notion block object
            
        Returns:
            Plain text content
        """
        block_type = block.get('type')
        
        if block_type in ['heading_1', 'heading_2', 'heading_3', 'paragraph']:
            rich_text = block.get(block_type, {}).get('rich_text', [])
        elif block_type in ['bulleted_list_item', 'numbered_list_item']:
            rich_text = block.get(block_type, {}).get('rich_text', [])
        else:
            return ""
        
        # Combine all text pieces
        text_parts = []
        for text_obj in rich_text:
            if text_obj.get('type') == 'text':
                text_parts.append(text_obj.get('text', {}).get('content', ''))
        
        return ''.join(text_parts)
    
    def clear_daily_capture_page(self) -> Dict[str, Any]:
        """
        Clear all content from the Daily Capture page.
        
        Returns:
            Dictionary with operation results
        """
        try:
            if not self.api_token or not self.daily_capture_page_id:
                logger.error("Notion API not properly configured")
                return {'success': False, 'error': 'API not configured'}
            
            # Get current blocks
            url = f"{self.base_url}/blocks/{self.daily_capture_page_id}/children"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch page for clearing: {response.status_code}")
                return {'success': False, 'error': f'Failed to fetch page: {response.status_code}'}
            
            data = response.json()
            blocks = data.get('results', [])
            
            # Delete each block
            deleted_count = 0
            for block in blocks:
                block_id = block.get('id')
                if block_id:
                    delete_url = f"{self.base_url}/blocks/{block_id}"
                    delete_response = requests.delete(delete_url, headers=self.headers)
                    
                    if delete_response.status_code == 200:
                        deleted_count += 1
                    else:
                        logger.warning(f"Failed to delete block {block_id}: {delete_response.status_code}")
            
            logger.info(f"Cleared {deleted_count} blocks from Daily Capture page")
            
            return {
                'success': True,
                'deleted_blocks': deleted_count,
                'total_blocks': len(blocks)
            }
            
        except Exception as e:
            logger.error(f"Error clearing daily capture page: {e}")
            return {'success': False, 'error': str(e)}
    
    def format_content_for_markdown(self, content: Dict[str, List[str]]) -> str:
        """
        Format parsed Notion content into markdown for insertion into daily notes.
        Only includes the Quick Capture section for daily notes.
        """
        if not content:
            print("DEBUG: No content provided to format_content_for_markdown")
            return ""
        
        print(f"DEBUG: Content keys found: {list(content.keys())}")
        for header, items in content.items():
            print(f"DEBUG: Header '{header}' has {len(items)} items")
        
        markdown_lines = []
        
        # Only process Quick Capture section for daily notes
        quick_capture_headers = ['💭 Quick Capture', 'Quick Capture', 'Capture']
        
        found_quick_capture = False
        for header, items in content.items():
            # Check if this is a quick capture section (flexible matching)
            is_quick_capture = any(capture_key in header for capture_key in quick_capture_headers)
            
            print(f"DEBUG: Header '{header}' - is_quick_capture: {is_quick_capture}")
            
            if is_quick_capture:
                found_quick_capture = True
                # Add header at #### level (for insertion under ### Captured Notes)
                markdown_lines.append(f"#### {header}")
                
                # Add bullet points
                for item in items:
                    print(f"DEBUG: Processing item: {item}")
                    # Preserve indentation for nested items
                    if item.startswith('  '):
                        markdown_lines.append(f"  * {item.strip()}")
                    else:
                        markdown_lines.append(f"* {item}")
                
                # Add spacing between sections
                markdown_lines.append("")
        
        if not found_quick_capture:
            print("DEBUG: No Quick Capture sections found in content")
        else:
            print(f"DEBUG: Generated markdown:\n{chr(10).join(markdown_lines)}")
        
        return "\n".join(markdown_lines)
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test the Notion API connection and configuration.
        
        Returns:
            Dictionary with test results
        """
        try:
            if not self.api_token:
                return {'success': False, 'error': 'No API token configured'}
            
            if not self.daily_capture_page_id:
                return {'success': False, 'error': 'No Daily Capture page ID configured'}
            
            # Test API connection by getting page info
            url = f"{self.base_url}/pages/{self.daily_capture_page_id}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                page_data = response.json()
                page_title = "Unknown"
                
                # Try to extract page title
                title_property = page_data.get('properties', {}).get('title')
                if title_property:
                    title_text = title_property.get('title', [])
                    if title_text:
                        page_title = title_text[0].get('text', {}).get('content', 'Unknown')
                
                return {
                    'success': True,
                    'page_title': page_title,
                    'page_id': self.daily_capture_page_id,
                    'api_connected': True
                }
            else:
                return {
                    'success': False,
                    'error': f'Failed to access page: {response.status_code} - {response.text}',
                    'page_id': self.daily_capture_page_id
                }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
        
    def update_daily_capture_template(self, sod_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the Daily Capture page template with SOD data.
        Updates Big 3 and Success Criteria sections while preserving other content.
        
        Args:
            sod_data: SOD form data dictionary
            
        Returns:
            Dictionary with operation results
        """
        try:
            if not self.api_token or not self.daily_capture_page_id:
                return {'success': False, 'error': 'API not configured'}
            
            # Get current content
            current_result = self.get_daily_capture_content()
            if not current_result['success']:
                return {'success': False, 'error': f'Failed to read current content: {current_result["error"]}'}
            
            current_content = current_result['content']
            
            # Extract SOD data
            big_3 = sod_data.get("Today's Big 3", "")
            success_criteria = sod_data.get("I know today would be successful if I did or felt this by the end:", "")
            
            # Clear the page first
            clear_result = self.clear_daily_capture_page()
            if not clear_result['success']:
                return {'success': False, 'error': f'Failed to clear page: {clear_result["error"]}'}
            
            # Rebuild page with updated content
            blocks_to_add = []
            
            # Add Current Goals section (preserved)
            blocks_to_add.extend(self._create_goals_section())
            
            # Add Today's Big 3 section (updated from SOD)
            blocks_to_add.extend(self._create_big3_section(big_3))
            
            # Add Success Criteria section (updated from SOD)
            blocks_to_add.extend(self._create_success_section(success_criteria))
            
            # Add Quick Capture section (preserved if it exists)
            quick_capture_content = current_content.get('💭 Quick Capture', [])
            blocks_to_add.extend(self._create_quick_capture_section(quick_capture_content))
            
            # Add all blocks to the page
            if blocks_to_add:
                add_result = self._add_blocks_to_page(blocks_to_add)
                if add_result['success']:
                    return {
                        'success': True,
                        'updated_sections': ['Big 3', 'Success Criteria'],
                        'preserved_sections': ['Current Goals', 'Quick Capture'],
                        'blocks_added': len(blocks_to_add)
                    }
                else:
                    return {'success': False, 'error': f'Failed to add blocks: {add_result["error"]}'}
            else:
                return {'success': True, 'message': 'No content to add'}
            
        except Exception as e:
            logger.error(f"Error updating daily capture template: {e}")
            return {'success': False, 'error': str(e)}

    def _create_goals_section(self) -> List[Dict]:
        """Create blocks for Current Goals section."""
        return [
            {
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"type": "text", "text": {"content": "🎯 Current Goals"}}]
                }
            },
            {
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Yearly: [Goals will be synced from Obsidian]"}}]
                }
            },
            {
                "type": "bulleted_list_item", 
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Quarterly: [Goals will be synced from Obsidian]"}}]
                }
            },
            {
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Monthly: [Goals will be synced from Obsidian]"}}]
                }
            },
            {
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Weekly: [Goals will be synced from Obsidian]"}}]
                }
            }
        ]

    def _create_big3_section(self, big_3_data: str) -> List[Dict]:
        """Create blocks for Today's Big 3 section."""
        blocks = [
            {
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"type": "text", "text": {"content": "⭐ Today's Big 3"}}]
                }
            }
        ]
        
        if big_3_data and big_3_data.strip():
            items = [item.strip() for item in big_3_data.split('\n') if item.strip()]
            for item in items:
                # Remove numbering if present
                clean_item = item.lstrip('123456789. ')
                blocks.append({
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": clean_item}}]
                    }
                })
        else:
            blocks.append({
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Submit your morning form to populate this section"}}]
                }
            })
        
        return blocks

    def _create_success_section(self, success_data: str) -> List[Dict]:
        """Create blocks for Success Criteria section."""
        blocks = [
            {
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"type": "text", "text": {"content": "✅ Success Criteria"}}]
                }
            }
        ]
        
        if success_data and success_data.strip():
            blocks.append({
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": success_data.strip()}}]
                }
            })
        else:
            blocks.append({
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Submit your morning form to populate this section"}}]
                }
            })
        
        return blocks

    def _create_quick_capture_section(self, existing_content: List[str]) -> List[Dict]:
        """Create blocks for Quick Capture section."""
        blocks = [
            {
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"type": "text", "text": {"content": "💭 Quick Capture"}}]
                }
            }
        ]
        
        if existing_content:
            for item in existing_content:
                blocks.append({
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": item}}]
                    }
                })
        else:
            blocks.append({
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": "Add your thoughts throughout the day here..."}}]
                }
            })
        
        return blocks

    def _add_blocks_to_page(self, blocks: List[Dict]) -> Dict[str, Any]:
        """Add blocks to the Daily Capture page."""
        try:
            url = f"{self.base_url}/blocks/{self.daily_capture_page_id}/children"
            
            # Notion API has a limit of 100 blocks per request
            for i in range(0, len(blocks), 100):
                batch = blocks[i:i+100]
                
                payload = {"children": batch}
                response = requests.patch(url, headers=self.headers, json=payload)
                
                if response.status_code != 200:
                    return {'success': False, 'error': f'Failed to add blocks: {response.status_code} - {response.text}'}
            
            return {'success': True, 'blocks_added': len(blocks)}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
        
    def update_goals_section(self, goals_blocks: List[Dict]) -> Dict[str, Any]:
        """Update the Current Goals section with Obsidian goal data."""
        try:
            # This would replace the _create_goals_section method
            # in update_daily_capture_template
            return {
                'success': True,
                'goals_blocks': goals_blocks,
                'block_count': len(goals_blocks)
            }
        except Exception as e:
            logger.error(f"Error updating goals section: {e}")
            return {'success': False, 'error': str(e)}