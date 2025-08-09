# test_markdown.py
from markdown_generator import MarkdownGenerator
from database import DatabaseManager
from config import DATABASE_CONFIG
from datetime import date

def test_markdown_generation():
    # Get today's SOD data from database
    db = DatabaseManager(DATABASE_CONFIG)
    db.connect()
    
    today = date.today()
    sod_data = db.get_sod_response(today)
    
    db.disconnect()
    
    # Generate markdown
    generator = MarkdownGenerator()
    markdown_content = generator.generate_daily_note(today, sod_data)
    
    # Save to file for testing
    filename = f"{today.strftime('%Y-%m-%d')}.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"✅ Markdown file generated: {filename}")
    print(f"Preview of first few lines:")
    print("=" * 50)
    print(markdown_content[:500] + "...")

if __name__ == "__main__":
    test_markdown_generation()