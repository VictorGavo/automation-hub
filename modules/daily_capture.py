"""Daily Capture Module - Notion integration and markdown generation"""

from .core import CoreUtils, ValidationResult, handle_exceptions, logger
from config import Config
from markdown_generator import MarkdownGenerator

class NotionIntegrationManager:
    """Handles Notion API integration and template management"""
    
    def __init__(self, db_manager=None):
        self.config = Config()
        self.db_manager = db_manager
        self.notion_manager = None
        self.goal_manager = None
        # Initialize managers if enabled
        if self.config.NOTION_ENABLED:
            try:
                from notion_manager import NotionManager
                self.notion_manager = NotionManager()
                logger.info("Notion integration initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Notion manager: {e}")
                self.notion_manager = None
        if self.config.OBSIDIAN_GOALS_ENABLED:
            try:
                from obsidian_goal_manager import ObsidianGoalManager
                self.goal_manager = ObsidianGoalManager()
                logger.info("Obsidian goals integration initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Obsidian goal manager: {e}")
                self.goal_manager = None
    
    def update_daily_template_with_sod(self, sod_data, current_date):
        """Update Notion daily template with SOD data and goals"""
        if not self.config.NOTION_ENABLED or not self.notion_manager:
            return ValidationResult(True, "Notion integration disabled", {'notion_updated': False})
        
        try:
            # Get current goals if enabled
            goals_blocks = []
            goals_status = "disabled"
            
            if self.goal_manager:
                goals_result = self.goal_manager.get_current_goals(current_date)
                
                if goals_result['goals']:
                    goals_blocks = self.goal_manager.format_goals_for_notion(goals_result['goals'])
                    cache_status = "cached" if goals_result['cache_used'] else "fresh"
                    goals_found = sum(1 for goal in goals_result['goals'].values() if goal.get('found', False))
                    goals_status = f"loaded {goals_found}/4 goals ({cache_status})"
                    logger.info(f"Loaded {goals_found}/4 goals from Obsidian ({cache_status})")
            
            # Update Notion template with SOD data
            notion_result = self.notion_manager.update_daily_capture_template(sod_data)
            
            if notion_result['success']:
                updated_sections = notion_result.get('updated_sections', [])
                logger.info(f"Updated Notion Daily Capture: {', '.join(updated_sections)}")
                
                return ValidationResult(True, "Notion template updated successfully", {
                    'notion_updated': True,
                    'updated_sections': updated_sections,
                    'goals_status': goals_status
                })
            else:
                error_msg = f"Failed to update Notion Daily Capture: {notion_result['error']}"
                logger.error(error_msg)
                return ValidationResult(False, error_msg)
                
        except Exception as e:
            error_msg = f"Notion template update exception: {e}"
            logger.error(error_msg, exc_info=True)
            return ValidationResult(False, error_msg)
    
    def process_daily_captures(self, daily_entry):
        """Process daily captures from Notion during EOD"""
        if not self.config.NOTION_ENABLED or not self.notion_manager:
            logger.warning("Notion integration is disabled or NotionManager not initialized. Skipping capture processing.")
            return ValidationResult(True, "Notion integration disabled", {
                'captures_processed': False,
                'sections_imported': 0,
                'blocks_cleared': 0
            })

        try:
            date_str = daily_entry['date'].strftime('%Y-%m-%d')
            logger.info(f"Processing Notion captures for {date_str}")

            # Get captures from Notion
            capture_result = self.notion_manager.get_daily_capture_content()
            logger.info(f"Capture result: success={capture_result.get('success')}, block_count={capture_result.get('block_count', 0)}")

            result_data = {
                'captures_processed': False,
                'sections_imported': 0,
                'blocks_cleared': 0,
                'content': None
            }

            if capture_result['success'] and capture_result['content']:
                sections_found = len(capture_result['content'])
                logger.info(f"Found {sections_found} content sections in Notion")

                # Log each section for debugging
                for header, items in capture_result['content'].items():
                    logger.debug(f"Section '{header}': {len(items)} items")

                # Format for markdown
                notion_markdown = self.notion_manager.format_content_for_markdown(
                    capture_result['content']
                )
                logger.info(f"Generated markdown for Notion capture: {len(notion_markdown)} characters")
                logger.debug(f"Markdown preview: {notion_markdown[:200]}")

                if notion_markdown.strip():
                    result_data.update({
                        'captures_processed': True,
                        'sections_imported': len(capture_result['content']),
                        'content': notion_markdown
                    })
                    logger.info(f"Storing Notion markdown content in database for {date_str}")
                    logger.debug(f"Stored content: {notion_markdown[:500]}")

                # Clear the Notion page for next day
                clear_result = self.notion_manager.clear_daily_capture_page()
                if clear_result['success']:
                    result_data['blocks_cleared'] = clear_result['deleted_blocks']
                    logger.info(f"Cleared {clear_result['deleted_blocks']} blocks from Daily Capture")
                else:
                    logger.error(f"Failed to clear Daily Capture: {clear_result['error']}")

                # Rebuild template for next day
                if daily_entry['sod_data']:
                    rebuild_result = self.notion_manager.update_daily_capture_template(daily_entry['sod_data'])
                    if rebuild_result['success']:
                        logger.info("Rebuilt Daily Capture template for tomorrow")
                    else:
                        logger.error(f"Template rebuild failed: {rebuild_result['error']}")
                else:
                    logger.warning("No SOD data available for template rebuild")
                    # DEBUG: Check what's actually in daily_entry
                    print(f"🔍 DEBUG - daily_entry keys: {list(daily_entry.keys())}")
                    print(f"🔍 DEBUG - sod_data type: {type(daily_entry.get('sod_data'))}")
                    print(f"🔍 DEBUG - sod_data value: {daily_entry.get('sod_data')}")

            else:
                if capture_result['success']:
                    logger.info("No captures found in Notion Daily Capture page")
                else:
                    error_msg = f"Failed to retrieve captures: {capture_result.get('error', 'Unknown error')}"
                    logger.error(error_msg)
                    return ValidationResult(False, error_msg)

            logger.info(f"Final Notion capture result for {date_str}: {result_data}")
            return ValidationResult(True, "Notion captures processed", result_data)

        except Exception as e:
            error_msg = f"Notion capture processing exception: {e}"
            logger.error(error_msg, exc_info=True)
            return ValidationResult(False, error_msg)

class MarkdownManager:
    """Handles markdown template generation and file management"""
    
    def __init__(self, db_manager=None):
        self.config = Config()
        self.db_manager = db_manager
        self.markdown_generator = MarkdownGenerator()
        self.notion_integration = NotionIntegrationManager(db_manager=db_manager) if db_manager else NotionIntegrationManager()
    
    def generate_final_template(self, daily_entry):
        """Generate final markdown template for daily entry"""
        try:
            generator = MarkdownGenerator()
            date_str = daily_entry['date'].strftime('%Y-%m-%d')
            logger.info(f"[SOD-TEMPLATE] generate_final_template: date={daily_entry['date']} (type={type(daily_entry['date'])}), date_str={date_str}")
            content_exists = daily_entry['sod_data'] is not None
            logger.info(f"[SOD-TEMPLATE] generate_final_template: sod_data_exists={content_exists}")
            if content_exists:
                logger.info(f"[SOD-TEMPLATE] generate_final_template: sod_data_keys={list(daily_entry['sod_data'].keys())}")
            else:
                logger.warning("[SOD-TEMPLATE] generate_final_template: No SOD data available for template generation")
            return generator.generate_daily_template(daily_entry)
        except Exception as e:
            error_msg = f"[SOD-TEMPLATE] generate_final_template: Template generation failed: {e}"
            logger.error(error_msg, exc_info=True)
            return None
            markdown_path = self.markdown_generator.generate_daily_template(daily_entry)
            
            if markdown_path:
                logger.info(f"Generated initial daily template: {markdown_path}")
                return ValidationResult(True, "Initial template generated", {
                    'template_generated': True,
                    'path': markdown_path
                })
            else:
                return ValidationResult(False, "Failed to generate template")
                
        except Exception as e:
            error_msg = f"Template generation failed: {e}"
            logger.error(error_msg, exc_info=True)
            return ValidationResult(False, error_msg)
    
    def generate_final_template(self, daily_entry):
        """Generate final template with captures (EOD processing)"""
        try:
            print(f"🔍 Starting final template generation for {daily_entry['date']}")
            
            # Process Notion captures first
            capture_result = self.notion_integration.process_daily_captures(daily_entry)
            
            print(f"📝 Notion capture result: {getattr(capture_result, 'is_valid', False)}")
            content = ''
            if capture_result and getattr(capture_result, 'data', None):
                print(f"   Captures processed: {capture_result.data.get('captures_processed', False)}")
                content = capture_result.data.get('content', '')
            content_length = len(content) if content is not None else 0
            print(f"   Content length: {content_length}")
            
            # Generate the base markdown template
            markdown_path = self.markdown_generator.generate_daily_template(daily_entry)
            
            # If we have capture content, we need to manually insert it
            if capture_result.is_valid and capture_result.data and capture_result.data.get('content'):
                notion_content = capture_result.data['content']
                print(f"🔄 Inserting {len(notion_content)} characters of Notion content...")
                
                try:
                    # Read the generated file
                    with open(markdown_path, 'r', encoding='utf-8') as f:
                        content_lines = f.read().split('\n')
                    
                    print(f"📄 Read {len(content_lines)} lines from generated file")
                    
                    # Insert the notion content
                    updated_lines = self.markdown_generator._insert_notion_captures(content_lines, notion_content)
                    
                    print(f"✏️ Updated to {len(updated_lines)} lines (+{len(updated_lines) - len(content_lines)})")
                    
                    # Write the updated content back
                    with open(markdown_path, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(updated_lines))
                    
                    print(f"✅ Successfully inserted Notion content into {markdown_path}")
                    
                except Exception as e:
                    print(f"❌ Failed to insert Notion content: {e}")
                    import traceback
                    traceback.print_exc()
            
            result_data = {
                'template_generated': markdown_path is not None,
                'path': markdown_path,
                'notion_captures': capture_result.data if capture_result.is_valid else None,
                'notion_error': capture_result.message if not capture_result.is_valid else None,
                'content_inserted': capture_result.is_valid and capture_result.data and capture_result.data.get('content')
            }
            
            if markdown_path:
                print(f"✅ Generated final daily template: {markdown_path}")
                return ValidationResult(True, "Final template generated", result_data)
            else:
                return ValidationResult(False, "Failed to generate final template", result_data)
                
        except Exception as e:
            error_msg = f"Final template generation failed: {e}"
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
            return ValidationResult(False, error_msg)
    
    def regenerate_template(self, daily_entry):
        """Regenerate template for a specific date"""
        try:
            markdown_path = self.markdown_generator.generate_daily_template(daily_entry)
            
            if markdown_path:
                logger.info(f"Regenerated template: {markdown_path}")
                return ValidationResult(True, "Template regenerated", {
                    'template_generated': True,
                    'path': markdown_path
                })
            else:
                return ValidationResult(False, "Failed to regenerate template")
                
        except Exception as e:
            error_msg = f"Template regeneration failed: {e}"
            logger.error(error_msg, exc_info=True)
            return ValidationResult(False, error_msg)

class DailyCaptureManager:
    """Main manager class for daily capture processing"""
    
    def __init__(self, db_manager=None):
        self.db_manager = db_manager
        self.notion_integration = NotionIntegrationManager(db_manager=db_manager) if db_manager else NotionIntegrationManager()
        self.markdown_manager = MarkdownManager(db_manager=db_manager) if db_manager else MarkdownManager()
    
    def process_sod_workflow(self, sod_data, daily_entry):
        """Process SOD workflow: update Notion template and generate initial markdown"""
        current_date = daily_entry['date']

        # Update Notion template with SOD data
        notion_result = self.notion_integration.update_daily_template_with_sod(sod_data, current_date)

        # Generate initial markdown template
        markdown_result = self.markdown_manager.regenerate_template(daily_entry)

        return {
            'notion_result': notion_result,
            'markdown_result': markdown_result
        }
    
    def process_eod_workflow(self, daily_entry):
        """Process EOD workflow: process captures and generate final markdown"""
        return self.markdown_manager.generate_final_template(daily_entry)
    
    def manual_notion_update(self, sod_data, current_date):
        """Manually update Notion template (API endpoint)"""
        return self.notion_integration.update_daily_template_with_sod(sod_data, current_date)
    
    def test_notion_connection(self):
        """Test Notion API connection"""
        if not self.notion_integration.notion_manager:
            return ValidationResult(False, "Notion integration not enabled")
        
        try:
            result = self.notion_integration.notion_manager.test_connection()
            return ValidationResult(result['success'], result.get('message', 'Connection test completed'), result)
        except Exception as e:
            return ValidationResult(False, f"Connection test failed: {e}")

# Export the main class
__all__ = ['DailyCaptureManager', 'NotionIntegrationManager', 'MarkdownManager']