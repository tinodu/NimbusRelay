"""IMAP Debug Service

Provides debugging utilities for IMAP folders.
"""

from typing import Dict, Any
from src.email_service.imap_connection import IMAPConnectionManager
from src.email_service.imap_folder_service import IMAPFolderService

class IMAPDebugService:
    """
    Service for debugging IMAP folders and connections.
    """

    def __init__(
        self,
        connection_manager: IMAPConnectionManager,
        folder_service: IMAPFolderService = None
    ):
        """
        Initialize the debug service.

        Args:
            connection_manager: Instance managing IMAP connections.
            folder_service: Optional folder service for folder operations.
        """
        self.connection_manager = connection_manager
        self.folder_service = folder_service

    def debug_all_folders(self) -> Dict[str, Any]:
        """
        Get detailed information about all folders for debugging.

        Returns:
            dict: Detailed folder information for debugging.
        """
        connection = self.connection_manager.connection
        if not connection or not self.connection_manager.is_connected():
            return {'error': 'No connection'}
        try:
            status, folders = connection.list()
            debug_info = {
                'status': status,
                'raw_folder_count': len(folders) if folders else 0,
                'raw_folders': [],
                'spam_folders_found': [],
                'folder_existence_check': {}
            }
            if folders:
                for folder in folders:
                    folder_str = folder.decode('utf-8') if isinstance(folder, bytes) else str(folder)
                    debug_info['raw_folders'].append(folder_str)
                    if any(keyword in folder_str.lower() for keyword in ['spam', 'junk']):
                        debug_info['spam_folders_found'].append(folder_str)
            test_folders = [
                'INBOX.spam', 'INBOX.Spam', 'INBOX.SPAM',
                'spam', 'Spam', 'SPAM', 'Junk', 'INBOX.Junk'
            ]
            for test_folder in test_folders:
                debug_info['folder_existence_check'][test_folder] = self.folder_exists(test_folder)
            return debug_info
        except Exception as e:
            return {'error': str(e)}

    def folder_exists(self, folder_name: str) -> bool:
        """
        Check if a specific folder exists on the server.

        Args:
            folder_name: Name of the folder to check.

        Returns:
            bool: True if folder exists, False otherwise.
        """
        connection = self.connection_manager.connection
        if not connection or not self.connection_manager.is_connected():
            return False
        try:
            test_status, _ = connection.select(folder_name, readonly=True)
            return test_status == 'OK'
        except Exception:
            return False