"""
IMAP Email Service Implementation
Concrete implementation of email service using IMAP protocol
"""

import imaplib
from typing import List, Optional
from src.email_service.interfaces import IEmailService, IFolderParser, IEmailParser
from src.email_service.folder_parser import IMAPFolderParser
from src.email_service.message_parser import EmailMessageParser
from src.email_service.utils import EmailFolderUtils
from src.models.email_models import EmailFolder, EmailMessage, ConnectionConfig


class IMAPEmailService(IEmailService):
    """IMAP implementation of email service following Dependency Inversion Principle"""
    
    def __init__(self, 
                 folder_parser: IFolderParser = None,
                 message_parser: IEmailParser = None):
        """
        Initialize IMAP email service with dependency injection
        
        Args:
            folder_parser: Parser for folder information
            message_parser: Parser for email messages
        """
        self.connection: Optional[imaplib.IMAP4_SSL] = None
        self.config: Optional[ConnectionConfig] = None
        
        # Dependency injection - allows for easy testing and swapping implementations
        self.folder_parser = folder_parser or IMAPFolderParser()
        self.message_parser = message_parser or EmailMessageParser()
    
    def connect(self, config: ConnectionConfig) -> bool:
        """
        Connect to IMAP server with provided configuration
        
        Args:
            config: Connection configuration
            
        Returns:
            bool: Success status
        """
        try:
            self.config = config
            self.connection = imaplib.IMAP4_SSL(
                config.imap_server, 
                config.imap_port
            )
            self.connection.login(config.imap_username, config.imap_password)
            return True
        except Exception as e:
            print(f"Email connection failed: {e}")
            return False
    
    def disconnect(self) -> None:
        """Safely disconnect from IMAP server"""
        if self.connection:
            try:
                self.connection.close()
                self.connection.logout()
            except:
                pass
            self.connection = None
    
    def is_connected(self) -> bool:
        """Check if service is connected"""
        return self.connection is not None
    
    def list_folders(self, include_hidden: bool = False) -> List[EmailFolder]:
        """
        List only allowed email folders (limited to specific set)
        
        Args:
            include_hidden: Whether to include hidden folders (unused, for compatibility)
            
        Returns:
            List[EmailFolder]: List of allowed email folders only
        """
        if not self.connection:
            return []

        try:
            # Define the allowed folders list
            allowed_folders = [
                'INBOX',
                'INBOX.Drafts', 
                'INBOX.Sent',
                'INBOX.spam',
                'INBOX.Trash',
                'INBOX.Archive'
            ]
            
            print(f"Limiting folder list to allowed folders: {allowed_folders}")
            
            folder_list = []
            
            # Check each allowed folder to see if it exists on the server
            for folder_name in allowed_folders:
                try:
                    # Try to select the folder to verify it exists
                    test_status, _ = self.connection.select(folder_name, readonly=True)
                    if test_status == 'OK':
                        print(f"Found allowed folder on server: {folder_name}")
                        
                        # Create display name and folder type
                        display_name = EmailFolderUtils.create_display_name(folder_name)
                        folder_type = EmailFolderUtils.get_folder_type(folder_name)
                        
                        # Create EmailFolder object
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
                        print(f"Added allowed folder: {email_folder}")
                    else:
                        print(f"Allowed folder not found on server: {folder_name}")
                        
                except Exception as e:
                    print(f"Failed to check allowed folder {folder_name}: {e}")
                    continue
            
            # If no allowed folders found, add at least INBOX
            if not folder_list:
                print("No allowed folders found, adding default INBOX")
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
            
            # Sort folders using utility function
            folder_list = EmailFolderUtils.sort_folders(folder_list)
            
            print(f"Final allowed folder list ({len(folder_list)} folders): {[f.name for f in folder_list]}")
            return folder_list
            
        except Exception as e:
            print(f"Failed to list folders: {e}")
            return []
    
    def get_emails(self, folder: str, limit: int = 50) -> List[EmailMessage]:
        """
        Retrieve emails from specified folder
        
        Args:
            folder: Folder name
            limit: Maximum number of emails to retrieve
            
        Returns:
            List[EmailMessage]: List of email messages
        """
        if not self.connection:
            return []
        
        try:
            self.connection.select(folder)
            status, messages = self.connection.search(None, 'ALL')
            
            if status != 'OK':
                return []
            
            email_ids = messages[0].split()
            emails = []
            
            # Get latest emails (limited by limit parameter)
            for email_id in reversed(email_ids[-limit:]):
                try:
                    status, msg_data = self.connection.fetch(email_id, '(RFC822)')
                    if status == 'OK':
                        raw_email = msg_data[0][1]
                        # Use injected parser
                        email_obj = self.message_parser.parse_email(raw_email)
                        email_obj.id = email_id.decode('utf-8')
                        emails.append(email_obj)
                except Exception as e:
                    print(f"Failed to fetch email {email_id}: {e}")
                    continue
            
            # Sort emails by date descending
            from email.utils import parsedate_to_datetime
            def parse_date_safe(email):
                try:
                    return parsedate_to_datetime(email.date)
                except Exception:
                    return None
            emails_sorted = sorted(
                emails,
                key=lambda e: parse_date_safe(e) or "",
                reverse=True
            )
            return emails_sorted
        except Exception as e:
            print(f"Failed to get emails: {e}")
            return []
    
    def _create_standard_folders(self) -> List[EmailFolder]:
        """Create only allowed standard folders when none are found"""
        print("No allowed folders found, creating standard allowed folders...")
        
        # Define allowed folders with variations to try
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
                    # Test if folder exists by trying to select it
                    test_status, _ = self.connection.select(folder_variant, readonly=True)
                    if test_status == 'OK':
                        # Use the primary name for consistency
                        display_name = EmailFolderUtils.create_display_name(primary_name)
                        folder_type = EmailFolderUtils.get_folder_type(primary_name)
                        
                        email_folder = EmailFolder(
                            name=primary_name,  # Use primary name for consistency
                            display_name=display_name,
                            type=folder_type,
                            attributes=[],
                            is_hidden=False,
                            is_selectable=True,
                            delimiter='.' if '.' in primary_name else '/'
                        )
                        folder_list.append(email_folder)
                        print(f"Added standard folder: {folder_variant} (as {primary_name})")
                        folder_added = True
                        break
                except Exception as e:
                    print(f"Standard folder {folder_variant} not available: {e}")
                    continue
            
            if not folder_added:
                print(f"No variant of {primary_name} folder found on server")
        
        return folder_list
    
    def move_email(self, email_id: str, from_folder: str, to_folder: str) -> bool:
        """
        Move an email from one folder to another
        
        Args:
            email_id: ID of the email to move
            from_folder: Source folder name
            to_folder: Destination folder name
            
        Returns:
            bool: Success status
        """
        if not self.connection:
            print(f"[MOVE EMAIL] No IMAP connection available")
            return False
        
        try:
            print(f"[MOVE EMAIL] Moving email {email_id} from {from_folder} to {to_folder}")
            
            # Select source folder
            status, _ = self.connection.select(from_folder)
            if status != 'OK':
                print(f"[MOVE EMAIL] Failed to select source folder {from_folder}")
                return False
            
            # Copy email to destination folder
            print(f"[MOVE EMAIL] Copying email to {to_folder}")
            copy_status, copy_response = self.connection.copy(email_id, to_folder)
            if copy_status != 'OK':
                print(f"[MOVE EMAIL] Failed to copy email to {to_folder}: {copy_response}")
                return False
            
            # Mark original email as deleted
            print(f"[MOVE EMAIL] Marking original email as deleted")
            store_status, store_response = self.connection.store(email_id, '+FLAGS', '\\Deleted')
            if store_status != 'OK':
                print(f"[MOVE EMAIL] Failed to mark email as deleted: {store_response}")
                return False
            
            # Expunge to permanently remove from source folder
            print(f"[MOVE EMAIL] Expunging deleted emails from {from_folder}")
            expunge_status, expunge_response = self.connection.expunge()
            if expunge_status != 'OK':
                print(f"[MOVE EMAIL] Warning: Failed to expunge: {expunge_response}")
                # Don't return False here as the move was technically successful
            
            print(f"[MOVE EMAIL] Successfully moved email {email_id} from {from_folder} to {to_folder}")
            return True
            
        except Exception as e:
            print(f"[MOVE EMAIL] Exception during move operation: {e}")
            return False
    
    def move_emails_by_criteria(self, from_folder: str, to_folder: str, criteria: str = 'ALL') -> dict:
        """
        Move multiple emails based on search criteria
        
        Args:
            from_folder: Source folder name
            to_folder: Destination folder name  
            criteria: IMAP search criteria (default: 'ALL')
            
        Returns:
            dict: Results with counts of moved emails and errors
        """
        if not self.connection:
            print(f"[MOVE EMAILS] No IMAP connection available")
            return {'moved': 0, 'errors': 0, 'error': 'No connection'}
        
        try:
            print(f"[MOVE EMAILS] Moving emails from {from_folder} to {to_folder} with criteria: {criteria}")
            
            # Select source folder
            status, _ = self.connection.select(from_folder)
            if status != 'OK':
                print(f"[MOVE EMAILS] Failed to select source folder {from_folder}")
                return {'moved': 0, 'errors': 0, 'error': f'Failed to select {from_folder}'}
            
            # Search for emails matching criteria
            search_status, messages = self.connection.search(None, criteria)
            if search_status != 'OK':
                print(f"[MOVE EMAILS] Search failed with criteria: {criteria}")
                return {'moved': 0, 'errors': 0, 'error': 'Search failed'}
            
            email_ids = messages[0].split()
            if not email_ids:
                print(f"[MOVE EMAILS] No emails found matching criteria: {criteria}")
                return {'moved': 0, 'errors': 0, 'message': 'No emails found'}
            
            moved_count = 0
            error_count = 0
            
            print(f"[MOVE EMAILS] Found {len(email_ids)} emails to move")
            
            for email_id in email_ids:
                try:
                    email_id_str = email_id.decode('utf-8')
                    if self.move_email(email_id_str, from_folder, to_folder):
                        moved_count += 1
                    else:
                        error_count += 1
                except Exception as e:
                    print(f"[MOVE EMAILS] Error moving email {email_id}: {e}")
                    error_count += 1
            
            result = {
                'moved': moved_count,
                'errors': error_count,
                'total_found': len(email_ids)
            }
            
            print(f"[MOVE EMAILS] Completed: {moved_count} moved, {error_count} errors")
            return result
            
        except Exception as e:
            print(f"[MOVE EMAILS] Exception during bulk move operation: {e}")
            return {'moved': 0, 'errors': 1, 'error': str(e)}
    
    def folder_exists(self, folder_name: str) -> bool:
        """
        Check if a specific folder exists on the server
        
        Args:
            folder_name: Name of the folder to check
            
        Returns:
            bool: True if folder exists, False otherwise
        """
        if not self.connection:
            return False
        
        try:
            # Try to select the folder to see if it exists
            test_status, _ = self.connection.select(folder_name, readonly=True)
            exists = test_status == 'OK'
            print(f"Folder '{folder_name}' exists: {exists}")
            return exists
        except Exception as e:
            print(f"Error checking folder '{folder_name}': {e}")
            return False
    
    def get_folder_count(self, folder_name: str) -> int:
        """
        Get the number of emails in a specific folder
        
        Args:
            folder_name: Name of the folder
            
        Returns:
            int: Number of emails in the folder
        """
        if not self.connection:
            return 0
        
        try:
            # Select the folder in readonly mode
            status, data = self.connection.select(folder_name, readonly=True)
            if status != 'OK':
                print(f"Failed to select folder {folder_name} for counting")
                return 0
            
            # Search for all messages
            status, messages = self.connection.search(None, 'ALL')
            if status != 'OK':
                return 0
            
            # Count the messages
            if messages[0]:
                email_ids = messages[0].split()
                count = len(email_ids)
                print(f"Folder {folder_name} contains {count} emails")
                return count
            else:
                return 0
                
        except Exception as e:
            print(f"Error counting emails in folder {folder_name}: {e}")
            return 0
    
    def debug_all_folders(self) -> dict:
        """
        Debug method to get detailed information about all folders
        
        Returns:
            dict: Detailed folder information for debugging
        """
        if not self.connection:
            return {'error': 'No connection'}
        
        try:
            # Get raw folder list
            status, folders = self.connection.list()
            
            debug_info = {
                'status': status,
                'raw_folder_count': len(folders) if folders else 0,
                'raw_folders': [],
                'spam_folders_found': [],
                'folder_existence_check': {}
            }
            
            # Process raw folders
            if folders:
                for folder in folders:
                    folder_str = folder.decode('utf-8') if isinstance(folder, bytes) else str(folder)
                    debug_info['raw_folders'].append(folder_str)
                    
                    # Check for spam-related folders
                    if any(keyword in folder_str.lower() for keyword in ['spam', 'junk']):
                        debug_info['spam_folders_found'].append(folder_str)
            
            # Test specific folder names
            test_folders = ['INBOX.spam', 'INBOX.Spam', 'INBOX.SPAM', 'spam', 'Spam', 'SPAM', 'Junk', 'INBOX.Junk']
            for test_folder in test_folders:
                debug_info['folder_existence_check'][test_folder] = self.folder_exists(test_folder)
            
            return debug_info
            
        except Exception as e:
            return {'error': str(e)}
