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
        self._last_selected_folder: Optional[str] = None
        
        # Dependency injection - allows for easy testing and swapping implementations
        self.folder_parser = folder_parser or IMAPFolderParser()
        self.message_parser = message_parser or EmailMessageParser()
    
    def connect(self, config: ConnectionConfig, ssl_context=None) -> bool:
        """
        Connect to IMAP server with provided configuration and optional SSL context.
        """
        try:
            import ssl
            self.config = config
            if ssl_context is None:
                ssl_context = ssl.create_default_context()
            self.connection = imaplib.IMAP4_SSL(
                config.imap_server,
                config.imap_port,
                ssl_context=ssl_context
            )
            self.connection.login(config.imap_username, config.imap_password)
            self._last_selected_folder = None
            return True
        except Exception as e:
            print(f"Email connection failed: {e}")
            self.connection = None
            return False
    
    def disconnect(self) -> None:
        """Safely disconnect from IMAP server"""
        if self.connection:
            try:
                # Only close if a mailbox is selected
                try:
                    self.connection.close()
                except Exception:
                    pass
                self.connection.logout()
            except Exception:
                pass
            self.connection = None
            self._last_selected_folder = None
    
    def is_connected(self) -> bool:
        """Check if service is connected"""
        return self.connection is not None
    
    def _ensure_connection(self) -> bool:
        """Ensure the IMAP connection is alive, reconnect if needed."""
        import imaplib
        if self.connection is None or self.config is None:
            return False
        try:
            # NOOP is a cheap way to check if the connection is alive
            self.connection.noop()
            return True
        except (imaplib.IMAP4.abort, imaplib.IMAP4.error, OSError):
            print("IMAP connection lost, attempting to reconnect...")
            self.disconnect()
            return self.connect(self.config)

    def list_folders(self, include_hidden: bool = False) -> List[EmailFolder]:
        """
        List only allowed email folders (limited to specific set)
        """
        if not self._ensure_connection():
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
                    try:
                        test_status, test_response = self.connection.select(folder_name, readonly=True)
                        # Check for suspicious non-IMAP responses
                        if isinstance(test_response, bytes):
                            test_response_str = test_response.decode(errors='ignore')
                        else:
                            test_response_str = str(test_response)
                        # Clean non-IMAP lines (e.g., spam filter headers) before status check
                        if isinstance(test_response, bytes):
                            cleaned_response = b"\n".join(
                                line for line in test_response.split(b"\n")
                                if b'HEADER_FROM_DIFFERENT_DOMAINS' not in line
                            )
                            test_response_str = cleaned_response.decode(errors='ignore')
                        else:
                            cleaned_response = "\n".join(
                                line for line in str(test_response).split("\n")
                                if 'HEADER_FROM_DIFFERENT_DOMAINS' not in line
                            )
                            test_response_str = cleaned_response
                        
                        if test_status != 'OK':
                            print(f"Suspicious or invalid IMAP response for {folder_name}: {test_status}, {test_response_str}")
                            raise Exception(f"Non-IMAP response: {test_response_str}")
                    except Exception as e:
                        print(f"EXAMINE failed for {folder_name} with error: {e}, resetting connection and retrying with SELECT (readonly=False)")
                        # Reset the connection to avoid protocol state issues
                        self.disconnect()
                        if not self.connect(self.config):
                            print(f"Reconnect failed after EXAMINE error for {folder_name}")
                            continue  # Skip this folder
                        try:
                            test_status, test_response = self.connection.select(folder_name, readonly=False)
                            if isinstance(test_response, bytes):
                                test_response_str = test_response.decode(errors='ignore')
                            else:
                                test_response_str = str(test_response)
                            if test_status != 'OK' or 'HEADER_FROM_DIFFERENT_DOMAINS' in test_response_str:
                                print(f"Suspicious or invalid IMAP response for {folder_name} (SELECT): {test_status}, {test_response_str}")
                                continue  # Skip this folder
                        except Exception as e2:
                            print(f"SELECT also failed for {folder_name} with error: {e2}")
                            continue  # Skip this folder
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
        if not self._ensure_connection():
            return []
        try:
            self.connection.select(folder)
            status, messages = self.connection.search(None, 'ALL')
            if status != 'OK':
                return []
            email_ids = messages[0].split()
            emails = []
            for email_id in reversed(email_ids[-limit:]):
                try:
                    if not email_id or email_id in [b'0', b'']:
                        print(f"Skipping invalid email_id: {email_id}")
                        continue
                    if isinstance(email_id, bytes):
                        email_id_str = email_id.decode('utf-8')
                    else:
                        email_id_str = str(email_id)
                    status, msg_data = self.connection.fetch(email_id_str, '(RFC822)')
                    if status == 'OK':
                        raw_email = msg_data[0][1]
                        email_obj = self.message_parser.parse_email(raw_email)
                        email_obj.id = email_id_str
                        emails.append(email_obj)
                except Exception as e:
                    print(f"Failed to fetch email {email_id}: {e}")
                    continue
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
        if not self._ensure_connection():
            print(f"[MOVE EMAIL] No IMAP connection available")
            return False
        try:
            print(f"[MOVE EMAIL] Moving email {email_id} from {from_folder} to {to_folder}")
            status, _ = self.connection.select(from_folder)
            if status != 'OK':
                print(f"[MOVE EMAIL] Failed to select source folder {from_folder}")
                return False
            print(f"[MOVE EMAIL] Copying email to {to_folder}")
            copy_status, copy_response = self.connection.copy(email_id, to_folder)
            if copy_status != 'OK':
                print(f"[MOVE EMAIL] Failed to copy email to {to_folder}: {copy_response}")
                return False
            print(f"[MOVE EMAIL] Marking original email as deleted")
            store_status, store_response = self.connection.store(email_id, '+FLAGS', '\\Deleted')
            if store_status != 'OK':
                print(f"[MOVE EMAIL] Failed to mark email as deleted: {store_response}")
                return False
            print(f"[MOVE EMAIL] Expunging deleted emails from {from_folder}")
            expunge_status, expunge_response = self.connection.expunge()
            if expunge_status != 'OK':
                print(f"[MOVE EMAIL] Warning: Failed to expunge: {expunge_response}")
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
        if not self._ensure_connection():
            print(f"[MOVE EMAILS] No IMAP connection available")
            return {'moved': 0, 'errors': 0, 'error': 'No connection'}
        try:
            print(f"[MOVE EMAILS] Moving emails from {from_folder} to {to_folder} with criteria: {criteria}")
            status, _ = self.connection.select(from_folder)
            if status != 'OK':
                print(f"[MOVE EMAILS] Failed to select source folder {from_folder}")
                return {'moved': 0, 'errors': 0, 'error': f'Failed to select {from_folder}'}
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
        if not self._ensure_connection():
            return False
        try:
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
        if not self._ensure_connection():
            return 0
        try:
            status, data = self.connection.select(folder_name, readonly=True)
            if status != 'OK':
                print(f"Failed to select folder {folder_name} for counting")
                return 0
            status, messages = self.connection.search(None, 'ALL')
            if status != 'OK':
                return 0
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
        if not self._ensure_connection():
            return {'error': 'No connection'}
        try:
            status, folders = self.connection.list()
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
            test_folders = ['INBOX.spam', 'INBOX.Spam', 'INBOX.SPAM', 'spam', 'Spam', 'SPAM', 'Junk', 'INBOX.Junk']
            for test_folder in test_folders:
                debug_info['folder_existence_check'][test_folder] = self.folder_exists(test_folder)
            return debug_info
        except Exception as e:
            return {'error': str(e)}

    def get_raw_email(self, email_id: str) -> Optional[str]:
        """
        Fetch the raw RFC822 source of an email by ID from allowed folders.
        """
        if not self._ensure_connection():
            return None
        allowed_folders = [
            'INBOX',
            'INBOX.Drafts',
            'INBOX.Sent',
            'INBOX.spam',
            'INBOX.Trash',
            'INBOX.Archive'
        ]
        for folder in allowed_folders:
            try:
                status, _ = self.connection.select(folder, readonly=True)
                if status != 'OK':
                    continue
                status, msg_data = self.connection.fetch(email_id, '(RFC822)')
                if status == 'OK' and msg_data and msg_data[0]:
                    raw_bytes = msg_data[0][1]
                    if isinstance(raw_bytes, bytes):
                        return raw_bytes.decode('utf-8', errors='replace')
                    return str(raw_bytes)
            except Exception:
                continue
        return None
    
    def get_html_source(self, email_id: str) -> Optional[str]:
        """
        Fetch the HTML source code of an email by ID from allowed folders.
        Returns the HTML part if present, otherwise None.
        """
        import email
        if not self._ensure_connection():
            return None
        allowed_folders = [
            'INBOX',
            'INBOX.Drafts',
            'INBOX.Sent',
            'INBOX.spam',
            'INBOX.Trash',
            'INBOX.Archive'
        ]
        for folder in allowed_folders:
            try:
                status, _ = self.connection.select(folder, readonly=True)
                if status != 'OK':
                    continue
                status, msg_data = self.connection.fetch(email_id, '(RFC822)')
                if status == 'OK' and msg_data and msg_data[0]:
                    raw_bytes = msg_data[0][1]
                    msg = email.message_from_bytes(raw_bytes) if isinstance(raw_bytes, bytes) else email.message_from_string(raw_bytes)
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            if content_type == "text/html":
                                html = part.get_payload(decode=True)
                                return html.decode(part.get_content_charset() or 'utf-8', errors='replace')
                    else:
                        if msg.get_content_type() == "text/html":
                            html = msg.get_payload(decode=True)
                            return html.decode(msg.get_content_charset() or 'utf-8', errors='replace')
            except Exception:
                continue
        return None
