#!/usr/bin/env python3
from config import Config

print("Testing Google Drive Config...")
print(f"GOOGLE_DRIVE_ENABLED: {Config.GOOGLE_DRIVE_ENABLED}")
print(f"GOOGLE_DRIVE_METHOD: {Config.GOOGLE_DRIVE_METHOD}")
print(f"GOOGLE_DRIVE_SYNC_PATH: {Config.GOOGLE_DRIVE_SYNC_PATH}")

# Test with environment variable
import os
os.environ['GOOGLE_DRIVE_ENABLED'] = 'true'
os.environ['GOOGLE_DRIVE_SYNC_PATH'] = '/test/path'

# Reload config (in a real scenario you'd restart the app)
from importlib import reload
import config
reload(config)
from config import Config

print("\nAfter setting environment variables:")
print(f"GOOGLE_DRIVE_ENABLED: {Config.GOOGLE_DRIVE_ENABLED}")
print(f"GOOGLE_DRIVE_SYNC_PATH: {Config.GOOGLE_DRIVE_SYNC_PATH}")