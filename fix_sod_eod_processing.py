#!/usr/bin/env python3
"""
Comprehensive fix for SOD/EOD data processing issues
Addresses field mapping, template generation, and error handling
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class SODEODDataProcessor:
    """Enhanced data processor with better field mapping and error handling"""
    
    def __init__(self):
        # Define field mappings to handle variations
        self.sod_field_mappings = {
            # Standard fields
            "What am I looking forward to the most today?": "highlight",
            "Today's Big 3": "big3",
            "I know today would be successful if I did or felt this by the end:": "success_criteria",
            "What would make today successful?": "success_criteria",  # Alternative form
            
            # Gratitude fields
            "3 things I'm grateful for in my life:": "gratitude_life",
            "3 things I'm grateful about myself:": "gratitude_self",
            
            # Morning mindset fields
            "I'm excited today for:": "excited_for",
            "One word to describe the person I want to be today would be __ because:": "one_word",
            "Someone who needs me on my a-game today is:": "a_game_for",
            "What's a potential obstacle/stressful situation for today and how would my best self deal with it?": "obstacle",
            "Someone I could surprise with a note, gift, or sign of appreciation is:": "surprise",
            "One action I could take today to demonstrate excellence or real value is:": "excellence_action",
            "One bold action I could take today is:": "bold_action",
            "An overseeing high performance coach would tell me today that:": "coach_advice",
            "The big projects I should keep in mind, even if I don't work on them today, are:": "big_projects"
        }
    
    def normalize_sod_data(self, raw_data: Dict) -> Dict:
        """Normalize SOD data to handle field variations"""
        normalized = {}
        
        for raw_key, value in raw_data.items():
            # Find matching normalized key
            if raw_key in self.sod_field_mappings:
                normalized_key = self.sod_field_mappings[raw_key]
                normalized[normalized_key] = self.clean_field_value(value)
            else:
                # Keep unknown fields but clean them
                normalized[raw_key] = self.clean_field_value(value)
        
        return normalized
    
    def clean_field_value(self, value) -> str:
        """Clean and validate field values"""
        if not value:
            return ""
        
        # Convert to string and strip whitespace
        cleaned = str(value).strip()
        
        # Remove excessive newlines
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        
        return cleaned
    
    def process_big3(self, big3_text: str) -> List[str]:
        """Process Big 3 text into structured list"""
        if not big3_text:
            return ["(No Big 3 data from SOD form)", "", ""]
        
        # Split by newlines and clean
        items = [item.strip() for item in big3_text.split('\n') if item.strip()]
        
        processed_items = []
        
        for i, item in enumerate(items[:3]):  # Only take first 3 items
            # Check if already numbered
            if re.match(r'^\d+\.\s+', item):
                processed_items.append(item)
            else:
                processed_items.append(f"{i+1}. {item}")
        
        # Fill in missing items
        while len(processed_items) < 3:
            processed_items.append(f"{len(processed_items)+1}. ")
        
        return processed_items
    
    def get_success_criteria(self, normalized_data: Dict) -> str:
        """Get success criteria with fallback handling"""
        success = normalized_data.get('success_criteria', '')
        
        if not success:
            # Check for alternative field names
            for key, value in normalized_data.items():
                if 'success' in key.lower() and value:
                    return value
        
        return success if success else "(Success criteria not provided in SOD form)"
    
    def validate_sod_data(self, normalized_data: Dict) -> Dict:
        """Validate SOD data and provide detailed feedback"""
        validation_result = {
            'valid': True,
            'warnings': [],
            'missing_fields': [],
            'data_quality': 'good'
        }
        
        # Required fields check
        required_fields = ['big3', 'highlight', 'success_criteria']
        
        for field in required_fields:
            if field not in normalized_data or not normalized_data[field]:
                validation_result['missing_fields'].append(field)
                validation_result['warnings'].append(f"Missing or empty: {field}")
        
        # Data quality assessment
        if len(validation_result['missing_fields']) > 1:
            validation_result['data_quality'] = 'poor'
            validation_result['valid'] = False
        elif len(validation_result['missing_fields']) == 1:
            validation_result['data_quality'] = 'fair'
        
        return validation_result


def create_enhanced_template_builder():
    """Create enhanced template building functions"""
    
    def build_reminders_section_enhanced(daily_entry):
        """Enhanced reminders section with better error handling"""
        content = []
        content.append("## Reminders")
        content.append("")
        
        # Today's Highlight with fallback
        content.append("```ad-tip")
        content.append("title:Today's Highlight")
        
        processor = SODEODDataProcessor()
        
        if daily_entry['sod_data']:
            normalized_data = processor.normalize_sod_data(daily_entry['sod_data'])
            highlight = normalized_data.get('highlight', '')
            
            if highlight:
                content.append(f"{highlight}")
            else:
                content.append("(No highlight provided in SOD form)")
        else:
            content.append("(SOD form not completed)")
        
        content.append("```")
        content.append("")
        
        # Today's Big 3 with enhanced processing
        content.append("**Today's Big 3**")
        content.append("")
        
        if daily_entry['sod_data']:
            normalized_data = processor.normalize_sod_data(daily_entry['sod_data'])
            big3_text = normalized_data.get('big3', '')
            big3_items = processor.process_big3(big3_text)
            
            for item in big3_items:
                content.append(item)
        else:
            content.append("1. (SOD form not completed)")
            content.append("2. ")
            content.append("3. ")
        
        # Remember previous day's improvements
        prev_date = (daily_entry['date'] - timedelta(days=1)).strftime('%Y-%m-%d')
        content.append("")
        content.append(f"Remember [[{prev_date}#Improvements]]")
        
        return content
    
    def build_morning_mindset_enhanced(daily_entry):
        """Enhanced morning mindset with better field mapping"""
        content = []
        content.append("### Morning Mindset")
        content.append("")
        
        processor = SODEODDataProcessor()
        
        if not daily_entry['sod_data']:
            content.append("(SOD form not completed)")
            return content
        
        normalized_data = processor.normalize_sod_data(daily_entry['sod_data'])
        
        # Define questions in order
        mindset_questions = [
            ("excited_for", "I'm excited today for:"),
            ("one_word", "One word to describe the person I want to be today would be __ because:"),
            ("a_game_for", "Someone who needs me on my a-game today is:"),
            ("obstacle", "What's a potential obstacle/stressful situation for today and how would my best self deal with it?"),
            ("surprise", "Someone I could surprise with a note, gift, or sign of appreciation is:"),
            ("excellence_action", "One action I could take today to demonstrate excellence or real value is:"),
            ("bold_action", "One bold action I could take today is:"),
            ("coach_advice", "An overseeing high performance coach would tell me today that:"),
            ("big_projects", "The big projects I should keep in mind, even if I don't work on them today, are:"),
            ("success_criteria", "I know today would be successful if I did or felt this by the end:")
        ]
        
        for field_key, question_text in mindset_questions:
            content.append(f"**{question_text}**")
            
            answer = normalized_data.get(field_key, '')
            if answer:
                content.append(f"{answer}")
            else:
                content.append("(Not provided in SOD form)")
            
            content.append("")
        
        return content
    
    return build_reminders_section_enhanced, build_morning_mindset_enhanced


def test_enhanced_processing():
    """Test the enhanced processing with sample data"""
    print("🧪 Testing Enhanced SOD/EOD Processing")
    print("=" * 50)
    
    # Test data with variations
    test_sod_data = {
        "What am I looking forward to the most today?": "Testing enhanced processing",
        "Today's Big 3": "1. Test enhanced processing\n2. Fix field mapping issues\n3. Improve error handling",
        "What would make today successful?": "All processing works smoothly",  # Alternative field
        "3 things I'm grateful for in my life:": "Technology\nTime to code\nCommunity support",
        "I'm excited today for:": "Better error handling"
    }
    
    processor = SODEODDataProcessor()
    
    # Test normalization
    normalized = processor.normalize_sod_data(test_sod_data)
    print("✅ NORMALIZED DATA:")
    for key, value in normalized.items():
        print(f"  {key}: {value[:50]}{'...' if len(str(value)) > 50 else ''}")
    print()
    
    # Test Big 3 processing
    big3_items = processor.process_big3(normalized.get('big3', ''))
    print("✅ BIG 3 PROCESSING:")
    for item in big3_items:
        print(f"  {item}")
    print()
    
    # Test success criteria
    success = processor.get_success_criteria(normalized)
    print(f"✅ SUCCESS CRITERIA: {success}")
    print()
    
    # Test validation
    validation = processor.validate_sod_data(normalized)
    print(f"✅ VALIDATION RESULT:")
    print(f"  Valid: {validation['valid']}")
    print(f"  Quality: {validation['data_quality']}")
    print(f"  Warnings: {validation['warnings']}")
    print(f"  Missing: {validation['missing_fields']}")


if __name__ == "__main__":
    test_enhanced_processing()
