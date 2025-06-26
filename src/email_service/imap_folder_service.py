"""
IMAP Folder Service

Encapsulates all folder-related operations for IMAP, using an IMAPConnectionManager for connection handling.
"""

from typing import List, Optional
from src.models.email_models import EmailFolder, ConnectionConfig
from src.email_service.utils import EmailFolderUtils

class IMAPFolderService:
    """
    Service for IMAP folder operations, using an IMAPConnectionManager for connection management.
    """

    def __init__(self, connection_manager):
        """
        Initialize the IMAPFolderService.

        Args:
            connection_manager: An instance of IMAPConnectionManager responsible for IMAP connections.
        """
        self.connection_manager = connection_manager

    def list_folders(self, include_hidden: bool = False) -> List[EmailFolder]:
        """
        List only allowed email folders (limited to a specific set).

        Args:
            include_hidden: Whether to include hidden folders (currently unused).

        Returns:
            List[EmailFolder]: List of allowed folders found on the server.
        """
        connection = self.connection_manager.get_connection()
        if connection is None:
            print("[IMAPFolderService] No IMAP connection available in list_folders.")
            return []

        try:
            allowed_folders = [
                'INBOX',
                'INBOX.Drafts',
                'INBOX.Sent',
                'INBOX.spam',
                'INBOX.Trash',
                'INBOX.Archive'
            ]

            folder_list = []

            for folder_name in allowed_folders:
                try:
                    status, response = connection.select(folder_name, readonly=True)
                    print(f"[IMAPFolderService] select({folder_name}) status: {status}")
                    if status != 'OK':
                        continue
                except Exception as e:
                    print(f"[IMAPFolderService] Exception selecting folder {folder_name}: {e}")
                    continue

                display_name = EmailFolderUtils.create_display_name(folder_name)
                folder_type = EmailFolderUtils.get_folder_type(folder_name)
                email_folder = EmailFolder(
                    name=folder_name,
                    display_name=display_name,
                    type=folder_type,
                    attributes=[],
                    is_hidden=False,
                    is_selectable=True,
                    delimiter='.' if '.' in folder_name else '/'
                )
                folder_list.append(email_folder)

            if not folder_list:
                inbox_folder = EmailFolder(
                    name='INBOX',
                    display_name='Inbox',
                    type='inbox',
                    attributes=[],
                    is_hidden=False,
                    is_selectable=True,
                    delimiter='/'
                )
                folder_list.append(inbox_folder)

            folder_list = EmailFolderUtils.sort_folders(folder_list)
            return folder_list

        except Exception as e:
            print(f"[IMAPFolderService] Exception in list_folders: {e}")
            return []

    def _create_standard_folders(self) -> List[EmailFolder]:
        """
        Create only allowed standard folders when none are found.

        Returns:
            List[EmailFolder]: List of standard folders found on the server.
        """
        connection = self.connection_manager.get_connection()
        if connection is None:
            return []

        allowed_folder_variations = [
            ('INBOX', ['INBOX']),
            ('INBOX.Drafts', ['INBOX.Drafts', 'INBOX.Draft', 'Drafts', 'Draft']),
            ('INBOX.Sent', ['INBOX.Sent', 'INBOX.SENT', 'Sent', 'SENT']),
            ('INBOX.spam', ['INBOX.spam', 'INBOX.Spam', 'INBOX.SPAM', 'spam', 'Spam', 'SPAM', 'Junk', 'INBOX.Junk']),
            ('INBOX.Trash', ['INBOX.Trash', 'INBOX.TRASH', 'Trash', 'TRASH', 'Deleted Items', 'INBOX.Deleted']),
            ('INBOX.Archive', ['INBOX.Archive', 'INBOX.ARCHIVE', 'Archive', 'ARCHIVE'])
        ]

        folder_list = []

        for primary_name, folder_variations in allowed_folder_variations:
            folder_added = False
            for folder_variant in folder_variations:
                try:
                    status, _ = connection.select(folder_variant, readonly=True)
                    if status == 'OK':
                        display_name = EmailFolderUtils.create_display_name(primary_name)
                        folder_type = EmailFolderUtils.get_folder_type(primary_name)
                        email_folder = EmailFolder(
                            name=primary_name,
                            display_name=display_name,
                            type=folder_type,
                            attributes=[],
                            is_hidden=False,
                            is_selectable=True,
                            delimiter='.' if '.' in primary_name else '/'
                        )
                        folder_list.append(email_folder)
                        folder_added = True
                        break
                except Exception:
                    continue
            # Optionally log if no variant found
        return folder_list

    def folder_exists(self, folder_name: str) -> bool:
        """
        Check if a specific folder exists on the server.

        Args:
            folder_name: Name of the folder to check.

        Returns:
            bool: True if folder exists, False otherwise.
        """
        connection = self.connection_manager.get_connection()
        if connection is None:
            return False
        try:
            status, _ = connection.select(folder_name, readonly=True)
            return status == 'OK'
        except Exception:
            return False

    def get_folder_count(self, folder_name: str) -> int:
        """
        Get the number of emails in a specific folder.

        Args:
            folder_name: Name of the folder.

        Returns:
            int: Number of emails in the folder.
        """
        connection = self.connection_manager.get_connection()
        if connection is None:
            return 0
        try:
            status, _ = connection.select(folder_name, readonly=True)
            if status != 'OK':
                return 0
            status, messages = connection.search(None, 'ALL')
            if status != 'OK' or not messages or not messages[0]:
                return 0
            email_ids = messages[0].split()
            return len(email_ids)
        except Exception:
            return 0

    def is_connected(self) -> bool:
        """
        Check if the IMAP connection is active.

        Returns:
            bool: True if connected, False otherwise.
        """
        return self.connection_manager.is_connected()