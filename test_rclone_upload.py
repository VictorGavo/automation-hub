import logging
import os
from datetime import datetime
from rclone_drive_manager import RcloneDriveManager

logging.basicConfig(level=logging.INFO)

daily_notes_dir = "daily_notes"
test_file = "2025-09-02.md"
test_file_path = os.path.join(daily_notes_dir, test_file)

if __name__ == "__main__":
    # Debug: Check if test file exists
    print(f"Checking if test file exists: {test_file_path}")
    file_exists = os.path.exists(test_file_path)
    print(f"File exists: {file_exists}")

    # Debug: List all files in daily_notes directory
    print(f"Listing all files in {daily_notes_dir}:")
    if os.path.exists(daily_notes_dir):
        for fname in os.listdir(daily_notes_dir):
            print(f" - {fname}")
    else:
        print(f"Directory {daily_notes_dir} does not exist.")

    # Debug: Print absolute path for upload
    abs_path = os.path.abspath(test_file_path)
    print(f"Absolute path for upload: {abs_path}")

    remote_name = "usvdrive"  # Should match your rclone remote name
    remote_path = ""  # Use subfolder if needed, e.g., "My Calendar/My Daily Notes"

    mgr = RcloneDriveManager(remote_name=remote_name, remote_path=remote_path)
    result = mgr.upload_daily_note(abs_path, datetime.now())
    print("Upload result:", result)
