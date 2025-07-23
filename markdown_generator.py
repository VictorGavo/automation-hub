from datetime import datetime, timedelta
import os
from typing import List
from config import Config
import logging

logger = logging.getLogger(__name__)

class MarkdownGenerator:
    def __init__(self):
        self.config = Config()
        self.template_dir = "templates"
        self.output_dir = "daily_notes"
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        self.drive_manager = None
        if Config.GOOGLE_DRIVE_ENABLED:
            try:
                if Config.GOOGLE_DRIVE_METHOD == 'filesystem':
                    from file_system import FileSystemDriveManager
                    self.drive_manager = FileSystemDriveManager(Config.GOOGLE_DRIVE_SYNC_PATH)
                    print("Google Drive file system integration enabled")
                else:
                    print(f"Unknown Google Drive Method: {Config.GOOGLE_DRIVE_METHOD}")
            except Exception as e:
                print(f"Failed to initialize Google Drive: {e}")
                self.drive_manager = None
    
    def generate_daily_template(self, daily_entry):
        """Generate markdown template with dynamic frontmatter and restructured sections"""

        if not daily_entry:
            return None
        
        date_str = daily_entry['date'].strftime('%Y-%m-%d')
        
        # Generate markdown content using updated structure
        content = self._build_template_content(daily_entry, date_str)

        # Process Notion captures if EOD data exists (indicating end of day processing)
        notion_processing_results = {
        'enabled': Config.NOTION_ENABLED,
        'captures_found': False,
        'sections_imported': 0,
        'blocks_cleared': 0,
        'error': None
        }

        # Process Notion captures if EOD data exists (indicating end of day processing)
        if daily_entry['eod_data'] and Config.NOTION_ENABLED:
            try:
                from notion_manager import NotionManager
                notion_manager = NotionManager()
                
                # Get captures from Notion
                capture_result = notion_manager.get_daily_capture_content()
                
                if capture_result['success'] and capture_result['content']:
                    # print(f"DEBUG: Found {len(capture_result['content'])} content sections")
                    # for header, items in capture_result['content'].items():
                    #     print(f"DEBUG: Section '{header}' has {len(items)} items")
                    
                    # Format for markdown
                    notion_markdown = notion_manager.format_content_for_markdown(
                        capture_result['content']
                    )
                    
                    # print(f"DEBUG: Generated markdown length: {len(notion_markdown)}")
                    # print(f"DEBUG: Generated markdown preview: {notion_markdown[:200]}...")
                    
                    if notion_markdown.strip():
                        # Insert into content
                        content_lines = content.split('\n')
                        updated_lines = self._insert_notion_captures(content_lines, notion_markdown)
                        content = '\n'.join(updated_lines)
                        print(f"✅ Imported captures from Notion Daily Capture")
                        # print(f"DEBUG: Content after insertion contains 'Quick Capture': {'Quick Capture' in content}")


                        notion_processing_results['captures_found'] = True
                        notion_processing_results['sections_imported'] = len([
                            header for header in capture_result['content'].keys()
                            if any(capture_key in header for capture_key in ['💭 Quick Capture', 'Quick Capture', 'Capture'])
                        ])
                    
                    # Clear the Notion page for next day
                    clear_result = notion_manager.clear_daily_capture_page()
                    if clear_result['success']:
                        notion_processing_results['blocks_cleared'] = clear_result['deleted_blocks']
                        print(f"✅ Cleared {clear_result['deleted_blocks']} items from Daily Capture")
                    else:
                        print(f"❌ Failed to clear Daily Capture: {clear_result['error']}")
                        notion_processing_results['error'] = f"Clear failed: {clear_result['error']}"

                    # Rebuild template sections for the next day
                    if daily_entry['sod_data']: # Use current SOD data to rebuild tempalte
                        rebuild_result = notion_manager.update_daily_capture_template(daily_entry['sod_data'])
                        if rebuild_result['success']:
                            print(f"✅ Rebuilt Daily Capture template for next day")
                        else:
                            print(f"❌ Failed to rebuild tempalte: {rebuild_result['error']}")

                    if notion_processing_results['sections_imported'] > 0:
                        print(f"✅ Imported {notion_processing_results['sections_imported']} capture sections from Notion")
                else:
                    print("ℹ️ No captures found in Notion Daily Capture page")
                    
            except Exception as e:
                error_msg = f"Error processing Notion captures: {e}"
                print(f"❌ {error_msg}")
                notion_processing_results['error'] = error_msg
        
        # Write to file
        filename = f"{date_str}.md"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"Generated daily template: {filepath}")
            # Upload to Google Drive if enabled (add after the existing print statement)
            if self.drive_manager:
                upload_result = self.drive_manager.upload_daily_note(filepath, daily_entry['date'])
                if upload_result['success']:
                    print(f"Successfully uploaded {os.path.basename(filepath)} to Google Drive")
                else:
                    print(f"Failed to upload {os.path.basename(filepath)} to Google Drive: {upload_result.get('error')}")
            return filepath
        except Exception as e:
            print(f"Error writing markdown file: {e}")
            return None
    
    def _build_template_content(self, daily_entry, date_str):
        """Build the complete template with dynamic frontmatter and restructured sections"""
        content = []
        
        # Add dynamic frontmatter
        content.extend(self._build_frontmatter(daily_entry, date_str))
        content.append("")
        
        # Navigation
        content.extend(self._build_navigation(daily_entry, date_str))
        content.append("")
        
        # Reminders section (with SOD data)
        content.extend(self._build_reminders_section(daily_entry))
        content.append("")
        
        # Tasks section (with code blocks)
        content.extend(self._build_tasks_section(date_str))
        content.append("")
        
        # Today section (simplified)
        content.extend(self._build_today_section())
        content.append("")
        
        # Journals section (with SOD data)
        content.extend(self._build_journals_section(daily_entry))
        content.append("")
        
        # Reflection section (with EOD data, no manual inputs)
        content.extend(self._build_reflection_section(daily_entry))
        content.append("")
        
        # Today's Notes section
        content.extend(self._build_notes_section(daily_entry))
        
        return "\n".join(content)
    
    def _build_frontmatter(self, daily_entry, date_str):
        """Build dynamic frontmatter based on available data"""
        date_obj = daily_entry['date']
        year = date_obj.year
        week_num = date_obj.isocalendar()[1]
        week_str = f"{year}-W{week_num:02d}"
        
        frontmatter = []
        frontmatter.append("---")
        
        # Base fields (created on SOD submission)
        frontmatter.append("tags: reviews/daily")
        frontmatter.append(f"Created: {datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}")
        frontmatter.append("Headings:")
        frontmatter.append(f'  - "[[{date_str}#Thoughts|💭]] [[{date_str}#Improvements|💪]] [[{date_str}#Obstacles|🚧]]"')
        frontmatter.append(f'  - "[[{date_str}#Accomplishments|✅]] [[{date_str}#Gratitude|🙏]] [[{date_str}#Content Log|📚]]"')
        frontmatter.append(f'Parent: "[[My Calendar/My Weekly Notes/{week_str}|{week_str}]]"')
        
        # Add EOD fields if EOD data exists
        if daily_entry['eod_data'] and daily_entry['eod_timestamp']:
            eod_data = daily_entry['eod_data']
            
            if 'Rating' in eod_data and eod_data['Rating']:
                frontmatter.append(f"Rating: {eod_data['Rating']}")
            
            if 'Summary' in eod_data and eod_data['Summary']:
                # Format for YAML multiline
                summary = eod_data['Summary'].replace('\n', '\n  ')
                frontmatter.append("Summary: |-")
                frontmatter.append(f"  {summary}")
            
            if 'Story' in eod_data and eod_data['Story']:
                story = eod_data['Story'].replace('\n', '\n  ')
                frontmatter.append("Story: |-")
                frontmatter.append(f"  {story}")
                
            for energy_type in ['Physical', 'Mental', 'Emotional', 'Spiritual']:
                if energy_type in eod_data and eod_data[energy_type]:
                    frontmatter.append(f"{energy_type}: {eod_data[energy_type]}")
        
        # Journal metadata
        frontmatter.append("journal: Day")
        frontmatter.append(f"journal-start-date: {date_str}")
        
        # Add journal-end-date only if EOD is completed
        if daily_entry['eod_data']:
            frontmatter.append(f"journal-end-date: {date_str}")
        
        frontmatter.append("journal-section: day")
        frontmatter.append("---")
        
        return frontmatter
    
    def _build_navigation(self, daily_entry, date_str):
        """Build navigation with proper week linking"""
        prev_date = (daily_entry['date'] - timedelta(days=1)).strftime('%Y-%m-%d')
        next_date = (daily_entry['date'] + timedelta(days=1)).strftime('%Y-%m-%d')
        week_str = f"{daily_entry['date'].year}-W{daily_entry['date'].isocalendar()[1]:02d}"
        
        return [f"<< [[My Calendar/My Daily Notes/{prev_date}|{prev_date}]] | [[My Calendar/My Weekly Notes/{week_str}|{week_str}]] | [[My Calendar/My Daily Notes/{next_date}|{next_date}]] >>"]
    
    def _build_reminders_section(self, daily_entry):
        """Build reminders section with SOD data"""
        content = []
        content.append("## Reminders")
        content.append("")
        
        # Today's Highlight
        content.append("```ad-tip")
        content.append("title:Today's Highlight")
        if daily_entry['sod_data'] and "What am I looking forward to the most today?" in daily_entry['sod_data']:
            highlight = daily_entry['sod_data']["What am I looking forward to the most today?"]
            content.append(f"{highlight}")
        else:
            content.append("What am I looking forward to the most today?")
        content.append("```")
        content.append("")
        
        # Today's Big 3
        content.append("**Today's Big 3**")
        content.append("")
        if daily_entry['sod_data'] and "Today's Big 3" in daily_entry['sod_data']:
            big3 = daily_entry['sod_data']["Today's Big 3"]
            if big3:
                items = [item.strip() for item in big3.split('\n') if item.strip()]
                for item in items:
                    # Check if item already starts with a number (like "1. Task")
                    if item and item[0].isdigit() and '. ' in item[:4]:
                        # Already numbered, use as-is
                        content.append(item)
                    else:
                        # Not numbered, add numbering
                        item_num = len([line for line in content if line and line[0].isdigit()]) + 1
                        content.append(f"{item_num}. {item}")
            else:
                content.append("1. (No Big 3 data from SOD form)")
                content.append("2. ")
                content.append("3. ")
        else:
            content.append("1. (SOD form not completed)")
            content.append("2. ")
            content.append("3. ")
        
        # Remember previous day's improvements
        prev_date = (daily_entry['date'] - timedelta(days=1)).strftime('%Y-%m-%d')
        content.append("")
        content.append(f"Remember [[{prev_date}#Improvements]]")
        
        return content
    
    def _build_tasks_section(self, date_str):
        """Build tasks section with code blocks"""
        content = []
        content.append("## Tasks")
        content.append("")
        
        # Tasks code block
        content.append("```tasks")
        content.append("not done")
        content.append(f"((due on {date_str}) OR (scheduled on {date_str})) OR (((scheduled before {date_str}) OR (due before {date_str})) AND (tags does not include habit))")
        content.append("sort by priority")
        content.append("```")
        content.append("")
        
        # Todoist under h3 for minimization
        content.append("### Today")
        content.append("```todoist")
        content.append('name: "Today and Overdue"')
        content.append('filter: "today | overdue"')
        content.append("```")
        
        return content
    
    def _build_today_section(self):
        """Build simplified today section"""
        content = []
        content.append("## Today")
        content.append("")
        
        # Captured Notes
        content.append("### Captured Notes")
        content.append("```dataview")
        content.append("list")
        content.append('where tags = "#note/🌱" and file.cday = this.file.cday')
        content.append("```")
        content.append("")
        
        # Created Notes
        content.append("### Created Notes")
        content.append("```dataview")
        content.append("list")
        content.append("where file.cday = this.file.cday")
        content.append("```")
        
        return content
    
    def _build_journals_section(self, daily_entry):
        """Build journals section with SOD data"""
        content = []
        content.append("## Journals")
        content.append("")
        
        # Gratitude section
        content.append("### Gratitude")
        content.append("")
        
        content.append("**3 things I'm grateful for in my life:**")
        if daily_entry['sod_data'] and "3 things I'm grateful for in my life:" in daily_entry['sod_data']:
            gratitude_life = daily_entry['sod_data']["3 things I'm grateful for in my life:"]
            if gratitude_life:
                items = [item.strip() for item in gratitude_life.split('\n') if item.strip()]
                for item in items:
                    content.append(f"- {item}")
            else:
                content.append("- (No gratitude data from SOD form)")
        else:
            content.append("- (SOD form not completed)")
        content.append("")
        
        content.append("**3 things I'm grateful for about myself:**")
        if daily_entry['sod_data'] and "3 things I'm grateful about myself:" in daily_entry['sod_data']:
            gratitude_self = daily_entry['sod_data']["3 things I'm grateful about myself:"]
            if gratitude_self:
                items = [item.strip() for item in gratitude_self.split('\n') if item.strip()]
                for item in items:
                    content.append(f"- {item}")
            else:
                content.append("- (No self-gratitude data from SOD form)")
        else:
            content.append("- (SOD form not completed)")
        content.append("")
        
        # Morning Mindset
        content.append("### Morning Mindset")
        content.append("")
        
        mindset_questions = [
            "I'm excited today for:",
            "One word to describe the person I want to be today would be __ because:",
            "Someone who needs me on my a-game today is:",
            "What's a potential obstacle/stressful situation for today and how would my best self deal with it?",
            "Someone I could surprise with a note, gift, or sign of appreciation is:",
            "One action I could take today to demonstrate excellence or real value is:",
            "One bold action I could take today is:",
            "An overseeing high performance coach would tell me today that:",
            "The big projects I should keep in mind, even if I don't work on them today, are:",
            "I know today would be successful if I did or felt this by the end:"
        ]
        
        for question in mindset_questions:
            content.append(f"**{question}**")
            if daily_entry['sod_data'] and question in daily_entry['sod_data']:
                answer = daily_entry['sod_data'][question]
                if answer and answer.strip():
                    content.append(f"{answer}")
                else:
                    content.append("(Empty response in SOD form)")
            else:
                content.append("(SOD form not completed)")
            content.append("")
        
        return content
    
    def _build_reflection_section(self, daily_entry):
        """Build reflection section with EOD data (no manual inputs)"""
        content = []
        content.append("## Reflection")
        content.append("")
        
        # Rating (data from frontmatter, but also display here)
        if daily_entry['eod_data']:
            content.append("### Rating")
            content.append("")
            rating = daily_entry['eod_data'].get("Rating", "Not Provided")
            content.append(f"**Rating:** {rating}/10")
            content.append("")
        
            # Summary (data from frontmatter, but also display here)
            content.append("### Summary")
            content.append("")
            summary = daily_entry['eod_data'].get("Summary","")
            if summary and summary.strip():
                content.append(summary)
            else:
                content.append("(Empty summary in EOD form)")
            content.append("")
            
            # Story
            content.append("### Story")
            content.append("")
            content.append("%% What was a moment today that provided immense emotion, insight, or meaning? %%")
            content.append("")
            story = daily_entry['eod_data'].get("Story", "")
            if story and story.strip():
                content.append(story)
            else:
                content.append("(Empty story in EOD form)")
            content.append("")
            
            # Accomplishments
            content.append("### Accomplishments")
            content.append("")
            content.append("%% What did I get done today? %%")
            content.append("")
            accomplishments = daily_entry['eod_data'].get("Accomplishments", "")
            if accomplishments and accomplishments.strip():
                content.append(accomplishments)
            else:
                content.append("(Empty accomplishments in EOD form)")
            content.append("")
            
            # Obstacles
            content.append("### Obstacles")
            content.append("")
            content.append("%% What was an obstacle I faced, how did I deal with it, and what can I learn from for the future? %%")
            content.append("")
            obstacles = daily_entry['eod_data'].get("Obstacles", "")
            if obstacles and obstacles.strip():
                content.append(obstacles)
            else:
                content.append("(Empty obstacles in EOD form)")
            content.append("")
            
            # Content Log
            content.append("### Content Log")
            content.append("")
            content.append("%% What were some insightful inputs and sources that I could process now? %%")
            content.append("")
            content.append("```dataview")
            content.append("table Status, Links, Source")
            content.append('FROM  #input AND !"Hidden"')
            content.append('WHERE contains(dateformat(Created, "yyyy-MM-dd"), this.file.name)')
            content.append("SORT Created desc")
            content.append("```")
            content.append("")
            
            # Thoughts
            content.append("### Thoughts")
            content.append("")
            content.append("%% What ideas was I pondering on or were lingering in my mind? %%")
            content.append("")
            
            # Conversations
            content.append("### Conversations")
            content.append("")
            content.append("%% Create sub-headers for any mini conversation you had or want to prepare for here %%")
            content.append("")
            content.append("#### Meetings")
            content.append("")
            content.append("```dataview")
            content.append("TABLE Attendees, Summary")
            content.append('FROM #meeting AND !"Hidden"')
            content.append("WHERE contains(file.frontmatter.meetingDate, this.file.name)")
            content.append("SORT Created asc")
            content.append("```")
            content.append("")
            
            # Trackers
            content.append("### Trackers")
            content.append("")
            content.append("#### Energies")
            content.append("")
            content.append("> Rate from 1-10")
            content.append("")
            
            # Re-energize question
            content.append("**What did I do to re-energize? How did it go?**")
            content.append("")
            reenergize = daily_entry['eod_data'].get("What did you do to re-energize? How did it go?", "")
            content.append(f"- {reenergize}")
            content.append("")
            
            # Energy levels (data from frontmatter, but also display here)
            energy_types = ["Physical", "Mental", "Emotional", "Spiritual"]
            for energy_type in energy_types:
                content.append(f"##### {energy_type}")
                content.append("")
                energy_level = daily_entry['eod_data'].get(f"{energy_type}", "")
                content.append(f"**{energy_type} Energy:** {energy_level}/10")
                content.append("")
            
            # Improvements
            content.append("### Improvements")
            content.append("")
            content.append("%% What can I do tomorrow to be 1% better? %%")
            content.append("")
            improvements = daily_entry['eod_data'].get("What can I do tomorrow to be 1% better?", "")
            content.append(improvements)
        else:
            # EOD not completed - show placeholder
            content.append("*Complete your evening form to see reflection data here.*")
            content.append("")        

        return content
    
    def _build_notes_section(self, daily_entry):
        """Build today's notes section"""
        content = []
        content.append("## Today's Notes")
        content.append("")
        
        # Dataview for notes created today
        content.append("```dataview")
        content.append('TABLE file.tags as "Note Type", Created')
        content.append('from ""')
        content.append('WHERE contains(dateformat(Created, "yyyy-MM-dd"), this.file.name)')
        content.append("SORT file.name")
        content.append("```")
        content.append("")
        
        # Form completion status
        if daily_entry['sod_timestamp'] or daily_entry['eod_timestamp']:
            content.append("### Form Completion Status")
            content.append("")
            if daily_entry['sod_timestamp']:
                sod_time = daily_entry['sod_timestamp'].strftime('%I:%M %p')
                content.append(f"✅ Morning form completed at {sod_time}")
            else:
                content.append("❌ Morning form not completed")
            
            if daily_entry['eod_timestamp']:
                eod_time = daily_entry['eod_timestamp'].strftime('%I:%M %p')
                content.append(f"✅ Evening form completed at {eod_time}")
            else:
                content.append("⏳ Evening form not completed")
        
        return content
    
    def generate_template_from_date(self, date):
        """Generate template for a specific date (utility method)"""
        from database import DatabaseManager
        
        db_manager = DatabaseManager()
        daily_entry = db_manager.get_daily_entry(date)
        
        if daily_entry:
            return self.generate_daily_template(daily_entry)
        else:
            # Create a basic template for date with no data
            basic_entry = {
                'date': date,
                'sod_data': None,
                'sod_timestamp': None,
                'eod_data': None,
                'eod_timestamp': None
            }
            return self.generate_daily_template(basic_entry)
        
    def _insert_notion_captures(self, content_lines: List[str], notion_content: str) -> List[str]:
        """
        Insert Notion capture content under the ### Captured Notes section.
        
        Args:
            content_lines: Existing markdown content as list of lines
            notion_content: Formatted notion content to insert
            
        Returns:
            Updated content lines with notion content inserted
        """
        if not notion_content.strip():
            # print("DEBUG: notion_content is empty, returning original lines")
            return content_lines
        
        # print(f"DEBUG: Inserting notion content ({len(notion_content)} chars)")
        # print(f"DEBUG: notion_content preview: {notion_content[:100]}...")
    

        # Find the ### Captured Notes section
        capture_notes_index = None
        for i, line in enumerate(content_lines):
            if line.strip() == "### Captured Notes":
                capture_notes_index = i
                # print(f"DEBUG: Found '### Captured Notes' at line {i}")
                break
        
        if capture_notes_index is None:
            # print("DEBUG: Could not find ### Captured Notes section")
            logger.warning("Could not find ### Captured Notes section")
            for i, line in enumerate(content_lines):
                    if line.startswith("###"):
                        # print(f"DEBUG: Found section at line {i}: {line}")
                        return content_lines
        
        # Find the end of the dataview block (look for next ### or ##)
        insert_index = None
        for i in range(capture_notes_index + 1, len(content_lines)):
            line = content_lines[i].strip()
            if line.startswith("```") and i > capture_notes_index + 1:
                # Found end of dataview block, insert after it
                insert_index = i + 1
                # print(f"DEBUG: Found end of dataview block at line {i}, will insert at {insert_index}")
                break
            elif line.startswith("###") or line.startswith("##"):
                # Found next section, insert before it
                insert_index = i
                # print(f"DEBUG: Found next section at line {i}, will insert before it")
                break
        
        # If no insertion point found, append to end
        if insert_index is None:
            insert_index = len(content_lines)
            # print(f"DEBUG: No insertion point found, appending at end (line {insert_index})")
        
        # Insert the notion content
        notion_lines = notion_content.split('\n')
        # print(f"DEBUG: Splitting notion content into {len(notion_lines)} lines")

        
        # Add a separator and the content
        updated_lines = (
            content_lines[:insert_index] + 
            ['', '#### From Daily Capture'] + 
            notion_lines + 
            [''] + 
            content_lines[insert_index:]
        )

        # print(f"DEBUG: Original content had {len(content_lines)} lines")
        # print(f"DEBUG: Updated content has {len(updated_lines)} lines")
        # print(f"DEBUG: Added {len(notion_lines) + 3} lines (content + separator + spacing)")
            
        return updated_lines