"""
File system-based Google Drive integration.
Writes files directly to Google Drive sync folder for automatic upload.
No authentication required - relies on Google Drive desktop app sync.
"""

import os
import shutil
from datetime import datetime
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class FileSystemDriveManager:
    def __init__(self, sync_folder_path: str):
        """
        Initialize file system drive manager.
        
        Args:
            sync_folder_path: Path to Google Drive sync folder on local system
                             e.g., "/home/pi/GoogleDrive/USV/My Calendar/My Daily Notes"
        """
        self.sync_folder_path = sync_folder_path
        self.ensure_folder_exists()
    
    def ensure_folder_exists(self):
        """Ensure the sync folder path exists, create if necessary."""
        try:
            if not os.path.exists(self.sync_folder_path):
                os.makedirs(self.sync_folder_path, exist_ok=True)
                logger.info(f"Created sync folder: {self.sync_folder_path}")
            else:
                logger.info(f"Using existing sync folder: {self.sync_folder_path}")
        except Exception as e:
            logger.error(f"Failed to create/access sync folder {self.sync_folder_path}: {e}")
            raise
    
    def upload_daily_note(self, file_path: str, date: datetime) -> Dict[str, Any]:
        """
        'Upload' daily note by copying to Google Drive sync folder.
        
        Args:
            file_path: Path to the local markdown file
            date: Date of the daily note
            
        Returns:
            Dictionary with upload results
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Source file not found: {file_path}")
            
            # Generate destination path
            filename = os.path.basename(file_path)
            destination_path = os.path.join(self.sync_folder_path, filename)
            
            # Check if file already exists
            file_existed = os.path.exists(destination_path)
            
            # Copy file to sync folder
            shutil.copy2(file_path, destination_path)
            
            # Verify the copy was successful
            if not os.path.exists(destination_path):
                raise Exception("File copy failed - destination file not found")
            
            # Get file info
            file_stats = os.stat(destination_path)
            
            action = 'updated' if file_existed else 'created'
            
            logger.info(f"Successfully {action} file in sync folder: {filename}")
            
            return {
                'success': True,
                'file_name': filename,
                'destination_path': destination_path,
                'sync_folder': self.sync_folder_path,
                'action': action,
                'file_size': file_stats.st_size,
                'modified_time': datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                'sync_status': 'pending_sync'  # Google Drive will handle actual sync
            }
            
        except Exception as e:
            logger.error(f"Error copying daily note to sync folder: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_path': file_path,
                'sync_folder': self.sync_folder_path
            }
    
    def list_daily_notes(self, limit: int = 50) -> list:
        """
        List daily notes in the sync folder.
        
        Args:
            limit: Maximum number of files to return
            
        Returns:
            List of file information
        """
        try:
            if not os.path.exists(self.sync_folder_path):
                logger.warning(f"Sync folder does not exist: {self.sync_folder_path}")
                return []
            
            files = []
            
            # Get all .md files in the sync folder
            for filename in os.listdir(self.sync_folder_path):
                if filename.endswith('.md'):
                    file_path = os.path.join(self.sync_folder_path, filename)
                    
                    if os.path.isfile(file_path):
                        file_stats = os.stat(file_path)
                        
                        files.append({
                            'name': filename,
                            'path': file_path,
                            'size': file_stats.st_size,
                            'modified_time': datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                            'created_time': datetime.fromtimestamp(file_stats.st_ctime).isoformat()
                        })
            
            # Sort by modification time (newest first)
            files.sort(key=lambda x: x['modified_time'], reverse=True)
            
            # Limit results
            return files[:limit]
            
        except Exception as e:
            logger.error(f"Error listing daily notes: {e}")
            return []
    
    def delete_daily_note(self, filename: str) -> bool:
        """
        Delete a daily note file from sync folder.
        
        Args:
            filename: Name of the file to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = os.path.join(self.sync_folder_path, filename)
            
            if not os.path.exists(file_path):
                logger.warning(f"File not found for deletion: {file_path}")
                return False
            
            os.remove(file_path)
            logger.info(f"Successfully deleted file: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file {filename}: {e}")
            return False
    
    def get_file_info(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific file.
        
        Args:
            filename: Name of the file
            
        Returns:
            File information or None if not found
        """
        try:
            file_path = os.path.join(self.sync_folder_path, filename)
            
            if not os.path.exists(file_path):
                return None
            
            file_stats = os.stat(file_path)
            
            return {
                'name': filename,
                'path': file_path,
                'size': file_stats.st_size,
                'modified_time': datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                'created_time': datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
                'is_file': os.path.isfile(file_path)
            }
            
        except Exception as e:
            logger.error(f"Error getting file info for {filename}: {e}")
            return None
    
    def test_sync_folder_access(self) -> Dict[str, Any]:
        """
        Test access to the sync folder and Google Drive connectivity.
        
        Returns:
            Dictionary with test results
        """
        try:
            # Test folder access
            if not os.path.exists(self.sync_folder_path):
                return {
                    'success': False,
                    'error': f"Sync folder does not exist: {self.sync_folder_path}",
                    'suggestion': "Ensure Google Drive desktop app is installed and synced"
                }
            
            # Test write permissions
            test_file_path = os.path.join(self.sync_folder_path, '.automation_test_file')
            
            try:
                with open(test_file_path, 'w') as f:
                    f.write(f"Test file created at {datetime.now().isoformat()}")
                
                # Clean up test file
                os.remove(test_file_path)
                
            except Exception as e:
                return {
                    'success': False,
                    'error': f"Cannot write to sync folder: {e}",
                    'suggestion': "Check folder permissions"
                }
            
            # Count existing files
            existing_files = self.list_daily_notes(limit=10)
            
            # Check if Google Drive process is running (Linux)
            drive_running = self._check_google_drive_process()
            
            return {
                'success': True,
                'sync_folder_path': self.sync_folder_path,
                'folder_exists': True,
                'write_permission': True,
                'existing_files_count': len(existing_files),
                'sample_files': [f['name'] for f in existing_files[:3]],
                'google_drive_process': drive_running,
                'warning': None if drive_running else "Google Drive desktop app may not be running"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _check_google_drive_process(self) -> bool:
        """
        Check if Google Drive desktop app process is running.
        
        Returns:
            True if process appears to be running, False otherwise
        """
        try:
            import subprocess
            
            # Common Google Drive process names
            process_names = ['google-drive-ocamlfuse', 'googledrive', 'gdrive', 'insync']
            
            for process_name in process_names:
                result = subprocess.run(['pgrep', '-f', process_name], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    logger.debug(f"Found Google Drive process: {process_name}")
                    return True
            
            # Also check for any process with 'drive' in the name
            result = subprocess.run(['pgrep', '-f', 'drive'], 
                                  capture_output=True, text=True)
            
            return result.returncode == 0
            
        except Exception as e:
            logger.debug(f"Could not check Google Drive process: {e}")
            return False  # Assume it's not running if we can't check
    
    def get_sync_status(self) -> Dict[str, Any]:
        """
        Get information about the sync folder and its contents.
        
        Returns:
            Dictionary with sync status information
        """
        try:
            status = {
                'sync_folder_path': self.sync_folder_path,
                'folder_exists': os.path.exists(self.sync_folder_path),
                'total_files': 0,
                'markdown_files': 0,
                'total_size_bytes': 0,
                'last_modified': None,
                'oldest_file': None,
                'newest_file': None
            }
            
            if not status['folder_exists']:
                return status
            
            markdown_files = []
            
            for filename in os.listdir(self.sync_folder_path):
                file_path = os.path.join(self.sync_folder_path, filename)
                
                if os.path.isfile(file_path):
                    status['total_files'] += 1
                    file_stats = os.stat(file_path)
                    status['total_size_bytes'] += file_stats.st_size
                    
                    if filename.endswith('.md'):
                        status['markdown_files'] += 1
                        markdown_files.append({
                            'name': filename,
                            'modified_time': file_stats.st_mtime
                        })
            
            if markdown_files:
                # Find oldest and newest markdown files
                markdown_files.sort(key=lambda x: x['modified_time'])
                status['oldest_file'] = markdown_files[0]['name']
                status['newest_file'] = markdown_files[-1]['name']
                status['last_modified'] = datetime.fromtimestamp(
                    markdown_files[-1]['modified_time']
                ).isoformat()
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting sync status: {e}")
            return {'error': str(e)}


def get_default_sync_path():
    """
    Get the default Google Drive sync path for the current OS.
    
    Returns:
        Default sync path string
    """
    import platform
    
    system = platform.system()
    user = os.getenv('USER') or os.getenv('USERNAME')
    
    if system == 'Linux':
        # Common paths for Google Drive on Linux
        possible_paths = [
            f"/home/{user}/GoogleDrive",
            f"/home/{user}/Google Drive",
            f"/home/{user}/gdrive",
            f"/mnt/GoogleDrive"
        ]
    elif system == 'Darwin':  # macOS
        possible_paths = [
            f"/Users/{user}/Google Drive",
            f"/Users/{user}/GoogleDrive"
        ]
    elif system == 'Windows':
        possible_paths = [
            f"C:\\Users\\{user}\\Google Drive",
            f"C:\\Users\\{user}\\GoogleDrive"
        ]
    else:
        possible_paths = []
    
    # Check which paths exist
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # Return the first option as default if none exist
    return possible_paths[0] if possible_paths else "/home/pi/GoogleDrive"