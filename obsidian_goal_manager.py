"""
Obsidian Goal Manager - Sync goals from Obsidian vault to Notion Daily Capture.
Handles caching, timeframe detection, and content formatting.
"""

import os
import re
import json
import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import frontmatter
from config import Config

logger = logging.getLogger(__name__)

class ObsidianGoalManager:
    def __init__(self, vault_path: str = None):
        """
        Initialize Obsidian Goal Manager.
        
        Args:
            vault_path: Path to Obsidian vault root directory
        """
        self.vault_path = vault_path or Config.OBSIDIAN_VAULT_LOCAL_PATH
        self.goals_folder = os.path.join(self.vault_path, "USV", "My Goals")
        self.content_char_limit = 200  # Safe limit for Notion display
        
        # Setup cache directory and file
        self.cache_dir = "cache"
        os.makedirs(self.cache_dir, exist_ok=True)  # This creates the directory if it doesn't exist
        self.cache_file = os.path.join(self.cache_dir, "goal_cache.json")  # Cache file goes in cache/ folder
        
        # Ensure goals folder exists
        if not os.path.exists(self.goals_folder):
            logger.warning(f"Goals folder not found: {self.goals_folder}")
    
    def get_current_goals(self, target_date: date = None) -> Dict[str, Any]:
        """
        Get current goals for all timeframes with intelligent caching.
        
        Args:
            target_date: Date to get goals for (default: today)
            
        Returns:
            Dictionary with timeframe goals and metadata
        """
        if target_date is None:
            target_date = date.today()
        
        # Calculate timeframes for target date
        timeframes = self._calculate_timeframes(target_date)
        
        # Check cache validity
        cache_data = self._load_cache()
        needs_refresh = self._check_cache_validity(cache_data, timeframes, target_date)
        
        if needs_refresh:
            logger.info("Cache expired or invalid, refreshing goals from Obsidian")
            goals_data = self._fetch_goals_from_obsidian(timeframes)
            self._save_cache(goals_data, timeframes, target_date)
        else:
            logger.info("Using cached goals data")
            goals_data = cache_data.get('goals', {})
        
        return {
            'goals': goals_data,
            'timeframes': timeframes,
            'cache_used': not needs_refresh,
            'last_updated': cache_data.get('last_updated') if not needs_refresh else datetime.now().isoformat()
        }
    
    def _calculate_timeframes(self, target_date: date) -> Dict[str, str]:
        """Calculate timeframe strings for a given date."""
        year = target_date.year
        month = target_date.month
        quarter = (month - 1) // 3 + 1
        
        # Calculate week number (ISO week)
        iso_year, iso_week, _ = target_date.isocalendar()
        
        return {
            'yearly': str(year),
            'quarterly': f"{year}-Q{quarter}",
            'monthly': f"{year}-M{month}",
            'weekly': f"{iso_year}-W{iso_week:02d}"
        }
    
    def _check_cache_validity(self, cache_data: Dict, timeframes: Dict, target_date: date) -> bool:
        """Check if cache needs refresh based on timeframes and dates."""
        if not cache_data or 'last_updated' not in cache_data:
            return True
        
        cached_timeframes = cache_data.get('timeframes', {})
        
        # Check if any timeframe changed
        for timeframe_type, current_value in timeframes.items():
            if cached_timeframes.get(timeframe_type) != current_value:
                logger.info(f"Timeframe changed: {timeframe_type} {cached_timeframes.get(timeframe_type)} -> {current_value}")
                return True
        
        # Check cache expiration based on timeframe sensitivity
        last_updated = datetime.fromisoformat(cache_data['last_updated']).date()
        
        # Weekly cache expires on Monday
        if target_date.weekday() == 0 and last_updated < target_date:  # Monday = 0
            logger.info("Weekly cache expired (new week)")
            return True
        
        # Monthly cache expires on 1st
        if target_date.day == 1 and last_updated < target_date:
            logger.info("Monthly cache expired (new month)")
            return True
        
        # Quarterly cache expires on quarter start
        if target_date.month in [1, 4, 7, 10] and target_date.day == 1 and last_updated < target_date:
            logger.info("Quarterly cache expired (new quarter)")
            return True
        
        # Yearly cache expires on Jan 1
        if target_date.month == 1 and target_date.day == 1 and last_updated < target_date:
            logger.info("Yearly cache expired (new year)")
            return True
        
        return False
    
    def _fetch_goals_from_obsidian(self, timeframes: Dict[str, str]) -> Dict[str, Any]:
        """Fetch goals from Obsidian vault for specified timeframes."""
        goals_data = {}
        
        for timeframe_type, timeframe_value in timeframes.items():
            goal_info = self._find_goal_by_timeframe(timeframe_value)
            goals_data[timeframe_type] = goal_info
        
        return goals_data
    
    def _find_goal_by_timeframe(self, timeframe: str) -> Dict[str, Any]:
        """Find goal file matching the specified timeframe."""
        try:
            if not os.path.exists(self.goals_folder):
                return self._create_placeholder_goal(timeframe, "Goals folder not found")
            
            # Search for goal files with matching timeframe
            for filename in os.listdir(self.goals_folder):
                if not filename.endswith('.md') or filename.startswith('Goal Template'):
                    continue
                
                file_path = os.path.join(self.goals_folder, filename)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        post = frontmatter.load(f)
                    
                    # Extract timeframe from frontmatter
                    goal_timeframe = post.metadata.get('Timeframe', '')
                    
                    # Handle both formats: "[[2025]]" and "2025-M02"
                    if isinstance(goal_timeframe, str):
                        # Remove double brackets and quotes if present
                        clean_timeframe = goal_timeframe.strip('[]"').strip()
                        
                        if clean_timeframe == timeframe:
                            return self._parse_goal_content(post, filename)
                
                except Exception as e:
                    logger.warning(f"Error reading goal file {filename}: {e}")
                    continue
            
            # No matching goal found
            return self._create_placeholder_goal(timeframe, "No goal found for timeframe")
            
        except Exception as e:
            logger.error(f"Error searching for goals: {e}")
            return self._create_placeholder_goal(timeframe, f"Error: {str(e)}")
    
    def _parse_goal_content(self, post: frontmatter.Post, filename: str) -> Dict[str, Any]:
        """Parse goal content from frontmatter post."""
        metadata = post.metadata
        content = post.content
        
        # Extract key information
        title = filename.replace('.md', '')
        description = metadata.get('Description', '').strip()
        why = metadata.get('Why', '').strip()
        status = metadata.get('Status', '')
        
        # Truncate description if too long
        if description and len(description) > self.content_char_limit:
            description = description[:self.content_char_limit-3] + "..."
        
        # Create summary text for Notion
        summary_parts = []
        if description:
            summary_parts.append(description)
        if why:
            summary_parts.append(f"Why: {why}")
        
        summary = " | ".join(summary_parts)
        if len(summary) > self.content_char_limit:
            summary = summary[:self.content_char_limit-3] + "..."
        
        return {
            'title': title,
            'description': description,
            'why': why,
            'status': status,
            'summary': summary,
            'found': True,
            'filename': filename,
            'last_updated': datetime.now().isoformat()
        }
    
    def _create_placeholder_goal(self, timeframe: str, reason: str) -> Dict[str, Any]:
        """Create placeholder when no goal is found."""
        return {
            'title': f"[Create {timeframe} Goal]",
            'description': '',
            'why': '',
            'status': '',
            'summary': f"No goal found for {timeframe}. Create one in Obsidian.",
            'found': False,
            'error': reason,
            'last_updated': datetime.now().isoformat()
        }
    
    def _load_cache(self) -> Dict[str, Any]:
        """Load cached goals data."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading cache: {e}")
        
        return {}
    
    def _save_cache(self, goals_data: Dict, timeframes: Dict, target_date: date):
        """Save goals data to cache."""
        try:
            cache_data = {
                'goals': goals_data,
                'timeframes': timeframes,
                'last_updated': datetime.now().isoformat(),
                'target_date': target_date.isoformat()
            }
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
                
            logger.info("Goals cache updated successfully")
            
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
    
    def format_goals_for_notion(self, goals_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format goals data for Notion blocks."""
        blocks = [
            {
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"type": "text", "text": {"content": "🎯 Current Goals"}}]
                }
            }
        ]
        
        # Order: Yearly -> Quarterly -> Monthly -> Weekly
        timeframe_order = ['yearly', 'quarterly', 'monthly', 'weekly']
        timeframe_labels = {
            'yearly': 'Yearly',
            'quarterly': 'Quarterly', 
            'monthly': 'Monthly',
            'weekly': 'Weekly'
        }
        
        for timeframe_type in timeframe_order:
            goal_info = goals_data.get(timeframe_type, {})
            
            if goal_info.get('found', False):
                # Rich content block for found goals
                label = timeframe_labels[timeframe_type]
                title = goal_info.get('title', 'Unknown Goal')
                summary = goal_info.get('summary', 'No description available')
                
                # Add timeframe label
                blocks.append({
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {"type": "text", "text": {"content": f"**{label}: {title}**", "annotations": {"bold": True}}}
                        ]
                    }
                })
                
                # Add summary
                blocks.append({
                    "type": "paragraph", 
                    "paragraph": {
                        "rich_text": [
                            {"type": "text", "text": {"content": summary}}
                        ]
                    }
                })
                
                # Add spacing
                blocks.append({
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": ""}}]
                    }
                })
            else:
                # Placeholder for missing goals
                label = timeframe_labels[timeframe_type]
                placeholder_text = goal_info.get('summary', f'[Create {label} Goal in Obsidian]')
                
                blocks.append({
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [
                            {"type": "text", "text": {"content": f"{label}: {placeholder_text}", "annotations": {"italic": True}}}
                        ]
                    }
                })
        
        return blocks
    
    def clear_cache(self):
        """Clear the goals cache file."""
        try:
            if os.path.exists(self.cache_file):
                os.remove(self.cache_file)
                logger.info("Goals cache cleared")
                return True
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
        
        return False
    
    def test_obsidian_access(self) -> Dict[str, Any]:
        """Test access to Obsidian vault and goals folder."""
        try:
            results = {
                'vault_path': self.vault_path,
                'vault_exists': os.path.exists(self.vault_path),
                'goals_folder': self.goals_folder,
                'goals_folder_exists': os.path.exists(self.goals_folder),
                'goal_files': [],
                'errors': []
            }
            
            if results['goals_folder_exists']:
                try:
                    goal_files = [f for f in os.listdir(self.goals_folder) 
                                if f.endswith('.md') and not f.startswith('Goal Template')]
                    
                    for filename in goal_files[:5]:  # Test first 5 files
                        file_path = os.path.join(self.goals_folder, filename)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                post = frontmatter.load(f)
                            
                            timeframe = post.metadata.get('Timeframe', 'No timeframe')
                            description = post.metadata.get('Description', 'No description')
                            
                            results['goal_files'].append({
                                'filename': filename,
                                'timeframe': timeframe,
                                'description': description[:50] + "..." if len(description) > 50 else description,
                                'readable': True
                            })
                            
                        except Exception as e:
                            results['goal_files'].append({
                                'filename': filename,
                                'readable': False,
                                'error': str(e)
                            })
                            
                except Exception as e:
                    results['errors'].append(f"Error listing goal files: {e}")
            else:
                results['errors'].append("Goals folder does not exist")
            
            results['success'] = len(results['errors']) == 0
            return results
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'vault_path': self.vault_path
            }