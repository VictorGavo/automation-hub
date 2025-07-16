def regenerate_real_data_markdown(self):
    """Regenerate markdown using your actual Google Form data"""
    self.print_header("REGENERATE MARKDOWN FROM REAL DATA")
    
    today_str = date.today().strftime('%Y-%m-%d')
    
    print(f"🔄 Regenerating markdown for {today_str} using real Google Form data...")
    
    try:
        # Get current data
        response = requests.get(f"{self.base_url}/api/daily/{today_str}")
        if response.status_code == 200:
            data = response.json()
            has_sod = data['sod_data'] is not None
            has_eod = data['eod_data'] is not None
            
            print(f"📊 Current data status:")
            print(f"   SOD Data: {'✅ Yes' if has_sod else '❌ No'}")
            print(f"   EOD Data: {'✅ Yes' if has_eod else '❌ No'}")
            
            if has_sod:
                print(f"\n📝 Your real SOD data:")
                sod_highlight = data['sod_data'].get("What am I looking forward to the most today?", "Not found")
                sod_big3 = data['sod_data'].get("Today's Big 3", "Not found")
                print(f"   Highlight: {sod_highlight}")
                print(f"   Big 3: {sod_big3}")
            
            if has_eod:
                print(f"\n📝 Your real EOD data:")
                eod_rating = data['eod_data'].get("Rating", "Not found")
                eod_summary = data['eod_data'].get("Summary", "Not found")
                print(f"   Rating: {eod_rating}")
                print(f"   Summary: {eod_summary}")
            
            # Regenerate markdown
            regen_response = requests.post(f"{self.base_url}/api/regenerate/{today_str}")
            if regen_response.status_code == 200:
                print(f"\n✅ Markdown regenerated successfully!")
                print(f"📁 Check: daily_notes/{today_str}.md")
                
                # Show file preview
                markdown_file = f"daily_notes/{today_str}.md"
                if os.path.exists(markdown_file):
                    with open(markdown_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Show Big 3 section specifically
                    big3_start = content.find("**Today's Big 3**")
                    if big3_start != -1:
                        section_end = content.find("\n\n", big3_start + 20)
                        if section_end == -1:
                            section_end = big3_start + 200
                        big3_section = content[big3_start:section_end]
                        print(f"\n📋 Big 3 section in regenerated markdown:")
                        print(f"   {big3_section}")
                
                return True
            else:
                print(f"❌ Failed to regenerate: {regen_response.status_code}")
                return False
        else:
            print(f"❌ Could not get data: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False    

def _check_markdown_generation_for_date(self, test_date):
    """Check markdown generation for specific date"""
    markdown_file = f"daily_notes/{test_date}.md"
    
    if os.path.exists(markdown_file):
        print(f"   ✅ Markdown file created: {markdown_file}")
        
        # Check file contents
        try:
            with open(markdown_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # More detailed content checking
            required_sections = [
                "## Reminders",
                "**Today's Big 3**", 
                "### Gratitude",
                "### Morning Mindset",
                "## Reflection",
                "### Rating",
                "### Summary"
            ]
            
            missing_sections = []
            found_sections = []
            
            for section in required_sections:
                if section in content:
                    found_sections.append(section)
                else:
                    missing_sections.append(section)
            
            print(f"   📄 Found {len(found_sections)}/{len(required_sections)} required sections")
            
            if missing_sections:
                print("   ❌ Missing sections:")
                for section in missing_sections:
                    print(f"      - {section}")
                return False
            
            return len(missing_sections) == 0
            
        except Exception as e:
            print(f"   ❌ Error reading markdown: {e}")
            return False
    else:
        print(f"   ❌ Markdown file not found: {markdown_file}")
        return False

def _test_api_endpoints_for_date(self, test_date):
    """Test API endpoints for specific date"""
    try:
        # Test daily entry endpoint
        response = requests.get(f"{self.base_url}/api/daily/{test_date}")
        if response.status_code == 200:
            data = response.json()
            has_sod = data['sod_data'] is not None
            has_eod = data['eod_data'] is not None
            print(f"   ✅ Daily API: SOD={has_sod}, EOD={has_eod}")
            return has_sod and has_eod
        else:
            print(f"   ❌ Daily API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ API error: {e}")
        return False

def _test_database_retrieval_for_date(self, test_date):
    """Test database retrieval for specific date"""
    try:
        response = requests.get(f"{self.base_url}/api/daily/{test_date}")
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Database retrieval successful")
            
            # Check SOD data
            if data['sod_data']:
                print(f"   📝 SOD Data Fields: {len(data['sod_data'])} fields")
                # Check for key fields
                key_sod_fields = ["What am I looking forward to the most today?", "Today's Big 3", "3 things I'm grateful for in my life:"]
                for field in key_sod_fields:
                    if field in data['sod_data']:
                        value = data['sod_data'][field]
                        preview = value[:50] + "..." if len(str(value)) > 50 else str(value)
                        print(f"      ✅ {field}: {preview}")
                    else:
                        print(f"      ❌ Missing: {field}")
            else:
                print("   ❌ No SOD data in database")
            
            # Check EOD data  
            if data['eod_data']:
                print(f"   📝 EOD Data Fields: {len(data['eod_data'])} fields")
                # Check for key fields
                key_eod_fields = ["Rating", "Summary", "Story", "Accomplishments"]
                for field in key_eod_fields:
                    if field in data['eod_data']:
                        value = data['eod_data'][field]
                        preview = value[:50] + "..." if len(str(value)) > 50 else str(value)
                        print(f"      ✅ {field}: {preview}")
                    else:
                        print(f"      ❌ Missing: {field}")
            else:
                print("   ❌ No EOD data in database")
            
            return True
        else:
            print(f"   ❌ Database retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return False    
    
def test_with_real_data(self):
    """Test using actual data from database instead of fake test data"""
    self.print_header("TEST WITH REAL DATABASE DATA")
    
    today_str = date.today().strftime('%Y-%m-%d')
    
    # Try to get existing data from database
    try:
        response = requests.get(f"{self.base_url}/api/daily/{today_str}")
        if response.status_code == 200:
            data = response.json()
            has_sod = data['sod_data'] is not None
            has_eod = data['eod_data'] is not None
            
            print(f"📅 Found data for {today_str}:")
            print(f"   SOD Data: {'✅ Yes' if has_sod else '❌ No'}")
            print(f"   EOD Data: {'✅ Yes' if has_eod else '❌ No'}")
            
            if has_sod or has_eod:
                print("\n🔄 Regenerating markdown from real data...")
                regen_response = requests.post(f"{self.base_url}/api/regenerate/{today_str}")
                if regen_response.status_code == 200:
                    print("   ✅ Markdown regenerated successfully")
                    
                    # Check the regenerated file
                    markdown_file = f"daily_notes/{today_str}.md"
                    if os.path.exists(markdown_file):
                        with open(markdown_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        print("\n📄 Real data preview:")
                        if has_sod and data['sod_data']:
                            sod_highlight = data['sod_data'].get("What am I looking forward to the most today?", "Not found")
                            print(f"   Today's Highlight: {sod_highlight[:100]}{'...' if len(sod_highlight) > 100 else ''}")
                        
                        if has_eod and data['eod_data']:
                            eod_rating = data['eod_data'].get("Rating", "Not found")
                            print(f"   Rating: {eod_rating}")
                    
                    return True
                else:
                    print(f"   ❌ Failed to regenerate: {regen_response.status_code}")
                    return False
            else:
                print("\n⚠️  No real data found. Submit your Google Forms first!")
                print("   Then run this test to see real data in action.")
                return False
        else:
            print(f"❌ Could not retrieve data: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing real data: {e}")
        return False#!/usr/bin/env python3
"""
Improved testing utility for Automation Hub
"""
import os
import sys
import requests
import json
from datetime import datetime, date, timedelta
from config import Config

class TestingUtility:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        
    def print_header(self, title):
        print("\n" + "=" * 60)
        print(f" {title}")
        print("=" * 60)
    
    def print_status(self):
        """Print current configuration status"""
        self.print_header("CURRENT CONFIGURATION")
        print(f"🗃️  Database: {Config.DB_NAME}")
        print(f"🧪 Testing Mode: {Config.TESTING}")
        print(f"🏠 Host: {Config.DB_HOST}:{Config.DB_PORT}")
        print(f"📍 Timezone: {Config.TIMEZONE}")
        
        # Test server connection
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                print(f"🟢 Flask Server: Running")
            else:
                print(f"🔴 Flask Server: Error ({response.status_code})")
        except:
            print(f"🔴 Flask Server: Not running or unreachable")
    
    def switch_to_testing(self):
        """Instructions to switch to testing mode"""
        self.print_header("SWITCH TO TESTING MODE")
        print("To use the test database, follow these steps:")
        print()
        print("💻 Windows PowerShell:")
        print("   $env:TESTING = 'true'")
        print()
        print("💻 Windows Command Prompt:")
        print("   set TESTING=true")
        print()
        print("🍎 Mac/Linux:")
        print("   export TESTING=true")
        print()
        print("⚙️  Then restart your Flask app:")
        print("   python app.py")
        print()
        print("✅ This will use 'automation_hub_test' database")
        print("✅ Keeps your production data safe")
    
    def test_complete_workflow(self):
        """Test the complete SOD → EOD → Markdown workflow using YESTERDAY'S date to avoid overwriting real data"""
        self.print_header("COMPLETE WORKFLOW TEST")
        
        # Use yesterday's date for testing to avoid overwriting today's real data
        test_date = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        print(f"🗓️  Using test date: {test_date} (to avoid overwriting real data)")
        
        # Check if server is running
        try:
            health = requests.get(f"{self.base_url}/health", timeout=5)
            print(f"✅ Server Status: {health.json()['status']}")
            print(f"🗃️  Using Database: {health.json()['database']}")
        except:
            print("❌ Flask server not running. Start with: python app.py")
            return False
        
        print("\n📝 Step 1: Testing SOD Form Submission...")
        sod_success = self._test_sod_submission()
        
        print("\n📝 Step 2: Testing EOD Form Submission...")
        eod_success = self._test_eod_submission()
        
        print("\n📄 Step 3: Checking Generated Markdown...")
        markdown_success = self._check_markdown_generation_for_date(test_date)
        
        print("\n📊 Step 4: Testing API Endpoints...")
        api_success = self._test_api_endpoints_for_date(test_date)
        
        print("\n🗃️  Step 5: Testing Database Retrieval...")
        db_success = self._test_database_retrieval_for_date(test_date)
        
        # Summary
        self.print_header("WORKFLOW TEST SUMMARY")
        print(f"SOD Submission:      {'✅ PASS' if sod_success else '❌ FAIL'}")
        print(f"EOD Submission:      {'✅ PASS' if eod_success else '❌ FAIL'}")
        print(f"Markdown Generation: {'✅ PASS' if markdown_success else '❌ FAIL'}")
        print(f"API Endpoints:       {'✅ PASS' if api_success else '❌ FAIL'}")
        print(f"Database Retrieval:  {'✅ PASS' if db_success else '❌ FAIL'}")
        
        if all([sod_success, eod_success, markdown_success, api_success, db_success]):
            test_file = f"daily_notes/{test_date}.md"
            print(f"\n🎉 COMPLETE SUCCESS! Check your test markdown file:")
            print(f"   📁 {test_file}")
            print(f"\n💡 Your real data for today is preserved!")
            return True
        else:
            print(f"\n⚠️  Some tests failed. See details above.")
            return False
    
    def _test_database_retrieval(self):
        """Test retrieving actual data from database"""
        today_str = date.today().strftime('%Y-%m-%d')
        
        try:
            response = requests.get(f"{self.base_url}/api/daily/{today_str}")
            if response.status_code == 200:
                data = response.json()
                print("   ✅ Database retrieval successful")
                
                # Check SOD data
                if data['sod_data']:
                    print(f"   📝 SOD Data Fields: {len(data['sod_data'])} fields")
                    # Check for key fields
                    key_sod_fields = ["What am I looking forward to the most today?", "Today's Big 3", "3 things I'm grateful for in my life:"]
                    for field in key_sod_fields:
                        if field in data['sod_data']:
                            value = data['sod_data'][field]
                            preview = value[:50] + "..." if len(str(value)) > 50 else str(value)
                            print(f"      ✅ {field}: {preview}")
                        else:
                            print(f"      ❌ Missing: {field}")
                else:
                    print("   ❌ No SOD data in database")
                
                # Check EOD data  
                if data['eod_data']:
                    print(f"   📝 EOD Data Fields: {len(data['eod_data'])} fields")
                    # Check for key fields
                    key_eod_fields = ["Rating", "Summary", "Story", "Accomplishments"]
                    for field in key_eod_fields:
                        if field in data['eod_data']:
                            value = data['eod_data'][field]
                            preview = value[:50] + "..." if len(str(value)) > 50 else str(value)
                            print(f"      ✅ {field}: {preview}")
                        else:
                            print(f"      ❌ Missing: {field}")
                else:
                    print("   ❌ No EOD data in database")
                
                return True
            else:
                print(f"   ❌ Database retrieval failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Database error: {e}")
            return False
    
    def _test_sod_submission(self):
        """Test SOD form submission"""
        test_date = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        sample_sod = {
            "What am I looking forward to the most today?": "Testing the complete workflow and seeing perfect markdown generation!",
            "Today's Big 3": "1. Complete EOD integration testing\n2. Generate perfect markdown template\n3. Document the final workflow",
            "3 things I'm grateful for in my life:": "My family and their support\nThe opportunity to build useful tools\nHaving time to learn and create",
            "3 things I'm grateful about myself:": "My persistence in solving problems\nMy willingness to learn new things\nMy attention to detail",
            "I'm excited today for:": "Seeing the automation hub come together perfectly",
            "One word to describe the person I want to be today would be __ because:": "Focused - because completing this project requires sustained attention and effort",
            "Someone who needs me on my a-game today is:": "Future me who will benefit from this automated workflow",
            "What's a potential obstacle/stressful situation for today and how would my best self deal with it?": "Technical bugs might arise - I'll debug systematically and take breaks when needed",
            "Someone I could surprise with a note, gift, or sign of appreciation is:": "My family, for being patient while I work on this project",
            "One action I could take today to demonstrate excellence or real value is:": "Create clear documentation for this automation system",
            "One bold action I could take today is:": "Share this project publicly to help others",
            "An overseeing high performance coach would tell me today that:": "Stay focused on the outcome and celebrate small wins along the way",
            "The big projects I should keep in mind, even if I don't work on them today, are:": "Google Drive integration, mobile notes capture, and eventual deployment",
            "I know today would be successful if I did or felt this by the end:": "The complete SOD to EOD to markdown workflow is working perfectly"
        }
        
        try:
            response = requests.post(f"{self.base_url}/webhook/sod?test_date={test_date}", json=sample_sod)
            if response.status_code == 200:
                print("   ✅ SOD form processed successfully")
                return True
            else:
                print(f"   ❌ SOD failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ SOD error: {e}")
            return False
    
    def _test_eod_submission(self):
        """Test EOD form submission"""
        test_date = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        sample_eod = {
            "Rating": "9",
            "Summary": "Excellent day working on the automation hub!\n\nSuccessfully integrated SOD and EOD workflows and got the markdown generation working perfectly.",
            "Story": "The moment when I saw the first perfectly formatted markdown file generated from the form data was incredibly satisfying.\n\nIt felt like all the pieces finally clicked together.",
            "Accomplishments": "Fixed database JSON serialization issues\nCreated proper Obsidian-style markdown templates\nTested complete workflow end-to-end\nUpdated all documentation",
            "Obstacles": "Had some initial confusion with the form field names and template structure.\n\nSolved it by carefully examining the actual form payload data and matching it exactly to the template format.",
            "What did you do to re-energize? How did it go?": "Took short breaks between debugging sessions and went for a quick walk. Really helped me think through the problems more clearly.",
            "Physical": "8",
            "Mental": "9",
            "Emotional": "9", 
            "Spiritual": "7",
            "What can I do tomorrow to be 1% better?": "Start with a clearer plan and break down complex tasks into smaller, testable pieces from the beginning."
        }
        
        try:
            response = requests.post(f"{self.base_url}/webhook/eod?test_date={test_date}", json=sample_eod)
            if response.status_code == 200:
                print("   ✅ EOD form processed successfully")
                return True
            else:
                print(f"   ❌ EOD failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ EOD error: {e}")
            return False
    
    def _check_markdown_generation(self):
        """Check if markdown file was generated and contains proper content"""
        today_str = date.today().strftime('%Y-%m-%d')
        markdown_file = f"daily_notes/{today_str}.md"
        
        if os.path.exists(markdown_file):
            print(f"   ✅ Markdown file created: {markdown_file}")
            
            # Check file contents
            try:
                with open(markdown_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # More detailed content checking
                required_sections = [
                    "## Reminders",
                    "**Today's Big 3**", 
                    "### Gratitude",
                    "### Morning Mindset",
                    "## Reflection",
                    "### Rating",
                    "### Summary"
                ]
                
                missing_sections = []
                found_sections = []
                
                for section in required_sections:
                    if section in content:
                        found_sections.append(section)
                    else:
                        missing_sections.append(section)
                
                print(f"   📄 Found {len(found_sections)}/{len(required_sections)} required sections")
                
                if missing_sections:
                    print("   ❌ Missing sections:")
                    for section in missing_sections:
                        print(f"      - {section}")
                    return False
                
                # Check for actual data vs placeholders
                data_indicators = [
                    "What am I looking forward to the most today?",
                    "Today's Big 3",
                    "Rating",
                    "Summary"
                ]
                
                placeholder_indicators = [
                    "(SOD form not completed)",
                    "(EOD form not completed)",
                    "(Empty response",
                    "(No Big 3 data"
                ]
                
                has_real_data = any(indicator in content for indicator in data_indicators)
                has_placeholders = any(indicator in content for indicator in placeholder_indicators)
                
                if has_real_data and not has_placeholders:
                    print("   ✅ Markdown contains real form data")
                elif has_real_data and has_placeholders:
                    print("   ⚠️  Markdown contains mix of real data and placeholders")
                else:
                    print("   ❌ Markdown contains only placeholders")
                
                # Show a preview of the Big 3 section to debug numbering
                big3_start = content.find("**Today's Big 3**")
                if big3_start != -1:
                    big3_section = content[big3_start:big3_start+200]
                    print("   📋 Big 3 Preview:")
                    for line in big3_section.split('\n')[:6]:  # Show first few lines
                        if line.strip():
                            print(f"      {line}")
                
                return len(missing_sections) == 0
                
            except Exception as e:
                print(f"   ❌ Error reading markdown: {e}")
                return False
        else:
            print(f"   ❌ Markdown file not found: {markdown_file}")
            return False
    
    def _check_markdown_generation_for_date(self, test_date):
        """Check markdown generation for specific date"""
        markdown_file = f"daily_notes/{test_date}.md"
        
        if os.path.exists(markdown_file):
            print(f"   ✅ Markdown file created: {markdown_file}")
            
            try:
                with open(markdown_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                required_sections = [
                    "## Reminders",
                    "**Today's Big 3**", 
                    "### Gratitude",
                    "### Morning Mindset",
                    "## Reflection",
                    "### Rating",
                    "### Summary"
                ]
                
                missing_sections = [section for section in required_sections if section not in content]
                found_sections = [section for section in required_sections if section in content]
                
                print(f"   📄 Found {len(found_sections)}/{len(required_sections)} required sections")
                
                if missing_sections:
                    print("   ❌ Missing sections:")
                    for section in missing_sections:
                        print(f"      - {section}")
                    return False
                
                # Show Big 3 preview
                big3_start = content.find("**Today's Big 3**")
                if big3_start != -1:
                    big3_section = content[big3_start:big3_start+200]
                    print("   📋 Big 3 Preview:")
                    for line in big3_section.split('\n')[:6]:
                        if line.strip():
                            print(f"      {line}")
                
                return len(missing_sections) == 0
                
            except Exception as e:
                print(f"   ❌ Error reading markdown: {e}")
                return False
        else:
            print(f"   ❌ Markdown file not found: {markdown_file}")
            return False

    def _test_api_endpoints_for_date(self, test_date):
        """Test API endpoints for specific date"""
        try:
            response = requests.get(f"{self.base_url}/api/daily/{test_date}")
            if response.status_code == 200:
                data = response.json()
                has_sod = data['sod_data'] is not None
                has_eod = data['eod_data'] is not None
                print(f"   ✅ Daily API: SOD={has_sod}, EOD={has_eod}")
                return has_sod and has_eod
            else:
                print(f"   ❌ Daily API failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ API error: {e}")
            return False

    def _test_database_retrieval_for_date(self, test_date):
        """Test database retrieval for specific date"""
        try:
            response = requests.get(f"{self.base_url}/api/daily/{test_date}")
            if response.status_code == 200:
                data = response.json()
                print("   ✅ Database retrieval successful")
                
                if data['sod_data']:
                    print(f"   📝 SOD Data Fields: {len(data['sod_data'])} fields")
                    key_field = "Today's Big 3"
                    if key_field in data['sod_data']:
                        value = data['sod_data'][key_field]
                        print(f"      ✅ {key_field}: {value}")
                        
                if data['eod_data']:
                    print(f"   📝 EOD Data Fields: {len(data['eod_data'])} fields")
                    key_field = "Rating"
                    if key_field in data['eod_data']:
                        value = data['eod_data'][key_field]
                        print(f"      ✅ {key_field}: {value}")
                
                return True
            else:
                print(f"   ❌ Database retrieval failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Database error: {e}")
            return False
    
    def _test_api_endpoints(self):
        """Test API endpoints"""
        today_str = date.today().strftime('%Y-%m-%d')
        
        try:
            # Test daily entry endpoint
            response = requests.get(f"{self.base_url}/api/daily/{today_str}")
            if response.status_code == 200:
                data = response.json()
                has_sod = data['sod_data'] is not None
                has_eod = data['eod_data'] is not None
                print(f"   ✅ Daily API: SOD={has_sod}, EOD={has_eod}")
                return has_sod and has_eod
            else:
                print(f"   ❌ Daily API failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ API error: {e}")
            return False
    
    def show_ngrok_help(self):
        """Show ngrok setup instructions"""
        self.print_header("NGROK SETUP FOR GOOGLE FORMS")
        print("Ngrok URLs change every time you restart ngrok.")
        print("Here's how to set it up:")
        print()
        print("1️⃣  Start ngrok (in new terminal):")
        print("   ngrok http 5000")
        print()
        print("2️⃣  Copy the HTTPS URL (example):")
        print("   https://abc123def.ngrok.io")
        print()
        print("3️⃣  Update your Google Apps Script:")
        print("   SOD Form: https://YOUR-URL.ngrok.io/webhook/sod")
        print("   EOD Form: https://YOUR-URL.ngrok.io/webhook/eod")
        print()
        print("4️⃣  Test with your actual Google Forms!")
        print()
        print("💡 Pro tip: For production, consider a stable URL service")
    
    def clean_test_database(self):
        """Clean test database"""
        if not Config.TESTING:
            print("❌ Only works in testing mode!")
            print("Set TESTING=true and restart Flask app first.")
            return
        
        confirm = input(f"🗑️  Clear all data from {Config.DB_NAME}? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Operation cancelled")
            return
        
        try:
            from database import DatabaseManager
            db = DatabaseManager()
            cursor = db.connection.cursor()
            cursor.execute("DELETE FROM daily_entries")
            db.connection.commit()
            cursor.close()
            db.close()
            print("✅ Test database cleared")
        except Exception as e:
            print(f"❌ Error clearing database: {e}")
    
    def test_with_real_data(self):
        """Test using actual data from database instead of fake test data"""
        self.print_header("TEST WITH REAL DATABASE DATA")
        
        today_str = date.today().strftime('%Y-%m-%d')
        
        # Try to get existing data from database
        try:
            response = requests.get(f"{self.base_url}/api/daily/{today_str}")
            if response.status_code == 200:
                data = response.json()
                has_sod = data['sod_data'] is not None
                has_eod = data['eod_data'] is not None
                
                print(f"📅 Found data for {today_str}:")
                print(f"   SOD Data: {'✅ Yes' if has_sod else '❌ No'}")
                print(f"   EOD Data: {'✅ Yes' if has_eod else '❌ No'}")
                
                if has_sod or has_eod:
                    print("\n🔄 Regenerating markdown from real data...")
                    regen_response = requests.post(f"{self.base_url}/api/regenerate/{today_str}")
                    if regen_response.status_code == 200:
                        print("   ✅ Markdown regenerated successfully")
                        
                        # Check the regenerated file
                        markdown_file = f"daily_notes/{today_str}.md"
                        if os.path.exists(markdown_file):
                            with open(markdown_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            print("\n📄 Real data preview:")
                            if has_sod and data['sod_data']:
                                sod_highlight = data['sod_data'].get("What am I looking forward to the most today?", "Not found")
                                print(f"   Today's Highlight: {sod_highlight[:100]}{'...' if len(sod_highlight) > 100 else ''}")
                            
                            if has_eod and data['eod_data']:
                                eod_rating = data['eod_data'].get("Rating", "Not found")
                                print(f"   Rating: {eod_rating}")
                        
                        return True
                    else:
                        print(f"   ❌ Failed to regenerate: {regen_response.status_code}")
                        return False
                else:
                    print("\n⚠️  No real data found. Submit your Google Forms first!")
                    print("   Then run this test to see real data in action.")
                    return False
            else:
                print(f"❌ Could not retrieve data: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error testing real data: {e}")
            return False
    
    def debug_big3_formatting(self):
        """Debug the Big 3 formatting issue specifically"""
        self.print_header("DEBUG BIG 3 FORMATTING")
        
        today_str = date.today().strftime('%Y-%m-%d')
        
        try:
            # Get the raw data from database
            response = requests.get(f"{self.base_url}/api/daily/{today_str}")
            if response.status_code == 200:
                data = response.json()
                
                if data['sod_data'] and "Today's Big 3" in data['sod_data']:
                    big3_raw = data['sod_data']["Today's Big 3"]
                    print(f"📝 Raw Big 3 data from database:")
                    print(f"   Type: {type(big3_raw)}")
                    print(f"   Content: {repr(big3_raw)}")
                    print(f"   Length: {len(big3_raw) if big3_raw else 0}")
                    print()
                    
                    if big3_raw:
                        print("📋 Split analysis:")
                        items = big3_raw.split('\n')
                        for i, item in enumerate(items):
                            print(f"   [{i}] '{item}' (len: {len(item)})")
                        print()
                        
                        print("🔧 Processed items:")
                        clean_items = [item.strip() for item in items if item.strip()]
                        for i, item in enumerate(clean_items, 1):
                            print(f"   {i}. {item}")
                        print()
                    
                    # Check the generated markdown
                    markdown_file = f"daily_notes/{today_str}.md"
                    if os.path.exists(markdown_file):
                        with open(markdown_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        print("📄 Big 3 section in markdown:")
                        big3_start = content.find("**Today's Big 3**")
                        if big3_start != -1:
                            # Find the end of the Big 3 section (next ## or empty line)
                            section_end = content.find("\n\n", big3_start)
                            if section_end == -1:
                                section_end = big3_start + 300
                            
                            big3_section = content[big3_start:section_end]
                            print(f"   {big3_section}")
                        else:
                            print("   ❌ Big 3 section not found in markdown")
                else:
                    print("❌ No Big 3 data found in database")
            else:
                print(f"❌ Could not get data: {response.status_code}")
        except Exception as e:
            print(f"❌ Error debugging: {e}")

    def regenerate_real_data_markdown(self):
        """Regenerate markdown using your actual Google Form data"""
        self.print_header("REGENERATE MARKDOWN FROM REAL DATA")
        
        today_str = date.today().strftime('%Y-%m-%d')
        
        print(f"🔄 Regenerating markdown for {today_str} using real Google Form data...")
        
        try:
            # Get current data
            response = requests.get(f"{self.base_url}/api/daily/{today_str}")
            if response.status_code == 200:
                data = response.json()
                has_sod = data['sod_data'] is not None
                has_eod = data['eod_data'] is not None
                
                print(f"📊 Current data status:")
                print(f"   SOD Data: {'✅ Yes' if has_sod else '❌ No'}")
                print(f"   EOD Data: {'✅ Yes' if has_eod else '❌ No'}")
                
                if has_sod:
                    print(f"\n📝 Your real SOD data:")
                    sod_highlight = data['sod_data'].get("What am I looking forward to the most today?", "Not found")
                    sod_big3 = data['sod_data'].get("Today's Big 3", "Not found")
                    print(f"   Highlight: {sod_highlight}")
                    print(f"   Big 3: {sod_big3}")
                
                if has_eod:
                    print(f"\n📝 Your real EOD data:")
                    eod_rating = data['eod_data'].get("Rating", "Not found")
                    eod_summary = data['eod_data'].get("Summary", "Not found")
                    print(f"   Rating: {eod_rating}")
                    print(f"   Summary: {eod_summary}")
                
                # Regenerate markdown
                regen_response = requests.post(f"{self.base_url}/api/regenerate/{today_str}")
                if regen_response.status_code == 200:
                    print(f"\n✅ Markdown regenerated successfully!")
                    print(f"📁 Check: daily_notes/{today_str}.md")
                    
                    # Show file preview
                    markdown_file = f"daily_notes/{today_str}.md"
                    if os.path.exists(markdown_file):
                        with open(markdown_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Show Big 3 section specifically
                        big3_start = content.find("**Today's Big 3**")
                        if big3_start != -1:
                            section_end = content.find("\n\n", big3_start + 20)
                            if section_end == -1:
                                section_end = big3_start + 200
                            big3_section = content[big3_start:section_end]
                            print(f"\n📋 Big 3 section in regenerated markdown:")
                            print(f"   {big3_section}")
                    
                    return True
                else:
                    print(f"❌ Failed to regenerate: {regen_response.status_code}")
                    return False
            else:
                print(f"❌ Could not get data: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def main_menu(self):
        """Show main menu"""
        while True:
            self.print_header("AUTOMATION HUB - TESTING UTILITY")
            print("1. 📊 Show current status")
            print("2. 🧪 Switch to testing mode (instructions)")
            print("3. 🔄 Test complete workflow (uses yesterday to preserve real data)")
            print("4. 📄 Test with real database data")
            print("5. 🔄 Regenerate markdown from real Google Form data")
            print("6. 🐛 Debug Big 3 formatting issue")
            print("7. 🌐 Show ngrok setup instructions")
            print("8. 🗑️  Clean test database")
            print("9. ❌ Exit")
            print()
            
            choice = input("Select option (1-9): ").strip()
            
            if choice == "1":
                self.print_status()
            elif choice == "2":
                self.switch_to_testing()
            elif choice == "3":
                self.test_complete_workflow()
            elif choice == "4":
                self.test_with_real_data()
            elif choice == "5":
                self.regenerate_real_data_markdown()
            elif choice == "6":
                self.debug_big3_formatting()
            elif choice == "7":
                self.show_ngrok_help()
            elif choice == "8":
                self.clean_test_database()
            elif choice == "9":
                print("Goodbye! 👋")
                break
            else:
                print("Invalid option. Please try again.")
            
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    tester = TestingUtility()
    
    # If command line argument provided, run specific test
    if len(sys.argv) > 1:
        if sys.argv[1] == "workflow":
            tester.test_complete_workflow()
        elif sys.argv[1] == "status":
            tester.print_status()
        else:
            print("Available commands: workflow, status")
    else:
        tester.main_menu()