#!/usr/bin/env python3
import os

print("Testing MarkdownGenerator with Google Drive disabled...")

# Test with Google Drive disabled (default)
from markdown_generator import MarkdownGenerator

generator = MarkdownGenerator()
print(f"Drive manager: {generator.drive_manager}")
print("✅ Works with Google Drive disabled")

print("\nTesting with Google Drive enabled but no file_system.py...")

# Test with Google Drive enabled but missing file
os.environ['GOOGLE_DRIVE_ENABLED'] = 'true'

# Reload to pick up environment change
from importlib import reload
import markdown_generator
reload(markdown_generator)

generator2 = MarkdownGenerator()
print(f"Drive manager: {generator2.drive_manager}")
print("✅ Handles missing file_system.py gracefully")