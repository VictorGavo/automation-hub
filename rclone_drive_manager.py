import os
import subprocess
from datetime import datetime
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class RcloneDriveManager:
    def __init__(self, remote_name: str, remote_path: str = ""):
        """
        Initialize rclone drive manager.
        Args:
            remote_name: rclone remote name (e.g., "usvdrive")
            remote_path: path within remote (e.g., "My Calendar/My Daily Notes" or "")
        """
        self.remote_name = remote_name
        self.remote_path = remote_path.strip("/")
        self.full_remote = f"{self.remote_name}:{self.remote_path}" if self.remote_path else f"{self.remote_name}:"

    def upload_daily_note(self, file_path: str, date: datetime) -> Dict[str, Any]:
        """
        Upload daily note to Google Drive using rclone copy.
        Args:
            file_path: Path to the local markdown file
            date: Date of the daily note
        Returns:
            Dictionary with upload results
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Source file not found: {file_path}")

            filename = os.path.basename(file_path)
            dest_remote = self.full_remote
            cmd = ["rclone", "copyto", file_path, f"{dest_remote}/{filename}"]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                logger.error(f"rclone copyto failed: {result.stderr}")
                return {
                    'success': False,
                    'error': result.stderr,
                    'file_path': file_path,
                    'remote': dest_remote
                }

            action = 'created'  # rclone does not distinguish between create/update
            logger.info(f"Successfully {action} file in remote: {filename}")
            return {
                'success': True,
                'file_name': filename,
                'remote': dest_remote,
                'action': action,
                'sync_status': 'pending_sync',
                'rclone_stdout': result.stdout
            }
        except Exception as e:
            logger.error(f"Error uploading daily note via rclone: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_path': file_path,
                'remote': self.full_remote
            }

    def list_daily_notes(self, limit: int = 50) -> list:
        pass

    def delete_daily_note(self, filename: str) -> bool:
        pass

    def get_file_info(self, filename: str) -> Optional[Dict[str, Any]]:
        pass

    def test_sync_folder_access(self) -> Dict[str, Any]:
        pass

    def get_sync_status(self) -> Dict[str, Any]:
        pass

    def check_rclone_accessible(self) -> bool:
        """
        Check if rclone is accessible in the environment.
        Returns:
            True if rclone is found and executable, False otherwise
        Side effects:
            Prints error details if rclone is not found or fails
        """
        rclone_cmd = "rclone"
        # On Windows, check for rclone.exe if rclone fails
        if os.name == "nt":
            rclone_cmds = ["rclone", "rclone.exe"]
        else:
            rclone_cmds = ["rclone"]
        for cmd in rclone_cmds:
            try:
                result = subprocess.run([cmd, "version"], capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"rclone accessible: {cmd}")
                    return True
                else:
                    print(f"rclone command '{cmd}' failed: {result.stderr}")
            except Exception as e:
                print(f"Error running '{cmd} version': {e}")
        print("rclone is not accessible. Please ensure it is installed and in your PATH.")
        return False
