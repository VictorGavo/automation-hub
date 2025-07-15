# markdown_generator.py
from datetime import datetime, timedelta
import re

class MarkdownGenerator:
    def __init__(self):
        pass
    
    def generate_daily_note(self, date, sod_data=None, eod_data=None):
        """Generate daily note markdown from template with SOD/EOD data"""
        
        # Format date strings
        date_str = date.strftime("%Y-%m-%d")
        prev_date = (date - timedelta(days=1)).strftime("%Y-%m-%d")
        next_date = (date + timedelta(days=1)).strftime("%Y-%m-%d")
        week_str = date.strftime("%Y-W%U")
        day_name = date.strftime("%a")
        
        # Base template structure
        template = f"""---
tags: reviews/daily
Created: {date.strftime("%Y-%m-%dT%H:%M:%S")}
Headings:
  - "[[{date_str}#Thoughts|💭]] [[{date_str}#Improvements|💪]] [[{date_str}#Obstacles|🚧]]"
  - "[[{date_str}#Accomplishments|✅]] [[{date_str}#Gratitude|🙏]] [[{date_str}#Content Log|📚]]"
Parent: "[[My Calendar/My Weekly Notes/{week_str}|{week_str}]]"
---

<< [[My Calendar/My Daily Notes/{prev_date}|{prev_date}]] | [[My Calendar/My Weekly Notes/{week_str}|{week_str}]] | [[My Calendar/My Daily Notes/{next_date}|{next_date}]] >>

## Reminders

```ad-tip
title:Today's Highlight
{self._get_field(sod_data, 'highlight', 'What am I looking forward to the most today?')}
```

**Today's Big 3**

{self._format_big_three(sod_data)}

Remember [[{prev_date}#Improvements]]

## Tasks

```tasks
not done
((due on {date_str}) OR (scheduled on {date_str})) OR (((scheduled before {date_str}) OR (due before {date_str})) AND (tags does not include habit))
sort by priority
```

## Today
```todoist
name: "Today and Overdue"
filter: "today | overdue"
```

Morning Routine
- [ ] Daily Fitness #habit 
- [ ] Opening Books #habit

### Captured Notes
```dataview
list
where tags = "#note/🌱" and file.cday = this.file.cday
```
### Created Notes
```dataview
list
where file.cday = this.file.cday
```

{self._add_work_section_if_weekday(date)}

Evening

Night Routine
- [ ] Closing Books #habit 
- Brush teeth and floss

## Journals

### Gratitude

**3 things I'm grateful for in my life:**
{self._format_grateful_life(sod_data)}

**3 things I'm grateful for about myself:**
{self._format_grateful_self(sod_data)}

### Morning Mindset

**I'm excited today for:**
{self._get_field(sod_data, 'excited_for', "I'm excited today for:")}

**One word to describe the person I want to be today would be \\_ because:**
{self._get_field(sod_data, 'word_description', "One word to describe the person I want to be today would be __ because:")}

**Someone who needs me on my a-game/needs my help today is:**
{self._get_field(sod_data, 'needs_me', "Someone who needs me on my a-game today is:")}

**What's a potential obstacle/stressful situation for today and how would my best self deal with it?**
{self._get_field(sod_data, 'obstacle_solution', "What's a potential obstacle/stressful situation for today and how would my best self deal with it?")}

**Someone I could surprise with a note, gift, or sign of appreciation is:**
{self._get_field(sod_data, 'surprise_appreciation', "Someone I could surprise with a note, gift, or sign of appreciation is:")}

**One action I could take today to demonstrate excellence or real value is:**
{self._get_field(sod_data, 'excellence_action', "One action I could take today to demonstrate excellence or real value is:")}

**One bold action I could take today is:**
{self._get_field(sod_data, 'bold_action', "One bold action I could take today is:")}

**An overseeing high performance coach would tell me today that:**
{self._get_field(sod_data, 'coach_advice', "An overseeing high performance coach would tell me today that:")}

**The big projects I should keep in mind, even if I don't work on them today, are:**
{self._get_field(sod_data, 'big_projects', "The big projects I should keep in mind, even if I don't work on them today, are:")}

**I know today would be successful if I did or felt this by the end:**
{self._get_field(sod_data, 'success_criteria', "I know today would be successful if I did or felt this by the end:")}

## Reflection

### Rating

```meta-bind
INPUT[progressBar(minValue(1), maxValue(10)):Rating]
```

### Summary

`INPUT[textArea():Summary]`
### Story

%% What was a moment today that provided immense emotion, insight, or meaning? %%

`INPUT[textArea():Story]`

### Accomplishments

%% What did I get done today? %%

```tasks
done on today
group by path
sort by priority
```

### Obstacles
%% What was an obstacle I faced, how did I deal with it, and what can I learn from for the future? %%

%% Any line with `obstacle:: x` will show up below %%
```dataview
table WITHOUT ID obstacle as "Obstacles"
from ""
where file.name = this.file.name
```
### Content Log
%% What were some insightful inputs and sources that I could process now? %%

```dataview
table Status, Links, Source
FROM  #input AND !"Hidden"
WHERE contains(dateformat(Created, "yyyy-MM-dd"), this.file.name)
SORT Created desc
```
### Thoughts
%% What ideas was I pondering on or were lingering in my mind? %%
### Conversations
%% Create sub-headers for any mini conversation you had or want to prepare for here, linking it to the respective `Conversations` header for the person %%
#### Meetings

```dataview
TABLE Attendees, Summary
FROM #meeting AND !"Hidden"
WHERE contains(file.frontmatter.meetingDate, this.file.name)
SORT Created asc
```

### Trackers

#### Energies

> Rate from 1-10

**What did I do to re-energize? How did it go?**

- 

##### Physical

```meta-bind
INPUT[progressBar(minValue(1), maxValue(10)):Physical]
```

##### Mental

```meta-bind
INPUT[progressBar(minValue(1), maxValue(10)):Mental]
```

##### Emotional

```meta-bind
INPUT[progressBar(minValue(1), maxValue(10)):Emotional]
```

##### Spiritual

```meta-bind
INPUT[progressBar(minValue(1), maxValue(10)):Spiritual]
```

### Improvements
%% What can I do tomorrow to be 1% better? %%

## Today's Notes

```dataview
TABLE file.tags as "Note Type", Created
from ""
WHERE contains(dateformat(Created, "yyyy-MM-dd"), this.file.name)
SORT file.name
```
"""
        return template
    
    def _get_field(self, data, field_name, question_text=""):
        """Get field from SOD data, fallback to raw_data with question text, or return empty"""
        if not data:
            return ""
            
        # Try the structured field first
        if data.get(field_name):
            return data[field_name]
            
        # Try the raw_data with question text
        if data.get('raw_data') and question_text:
            return data['raw_data'].get(question_text, "")
            
        return ""
    
    def _format_big_three(self, sod_data):
        """Format the Big 3 into numbered list"""
        big_three_text = self._get_field(sod_data, 'big_three', "Today's Big 3")
        if not big_three_text:
            return "1. \n2. \n3. "
            
        # Split by newline and create numbered list
        items = [item.strip() for item in big_three_text.split('\n') if item.strip()]
        formatted = []
        for i, item in enumerate(items[:3], 1):  # Only take first 3
            formatted.append(f"{i}. {item}")
        
        # Fill remaining slots if less than 3
        while len(formatted) < 3:
            formatted.append(f"{len(formatted) + 1}. ")
            
        return "\n".join(formatted)
    
    def _format_grateful_life(self, sod_data):
        """Format grateful for life into bullet points"""
        grateful_text = self._get_field(sod_data, 'grateful_life', "3 things I'm grateful for in my life:")
        if not grateful_text:
            return "- "
            
        items = [item.strip() for item in grateful_text.split('\n') if item.strip()]
        return "\n".join([f"- {item}" for item in items])
    
    def _format_grateful_self(self, sod_data):
        """Format grateful about self into bullet points"""
        grateful_text = self._get_field(sod_data, 'grateful_self', "3 things I'm grateful about myself:")
        if not grateful_text:
            return "- "
            
        items = [item.strip() for item in grateful_text.split('\n') if item.strip()]
        return "\n".join([f"- {item}" for item in items])
    
    def _add_work_section_if_weekday(self, date):
        """Add Work section if it's a weekday"""
        if date.strftime("%a") not in ["Sun", "Sat"]:
            return "Work"
        return ""