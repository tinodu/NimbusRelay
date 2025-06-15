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
        List all available email folders with visibility filtering
        
        Args:
            include_hidden: Whether to include hidden folders
            
        Returns:
            List[EmailFolder]: List of email folders
        """
        if not self.connection:
            return []

        try:
            status, folders = self.connection.list()
            folder_list = []
            
            print(f"IMAP LIST status: {status}")
            print(f"Raw folder data count: {len(folders) if folders else 0}")
            
            if status != 'OK':
                print(f"IMAP LIST failed with status: {status}")
                return []
            
            # Debug: Print all raw folders to see what the server returns
            print("=== ALL RAW FOLDERS FROM SERVER ===")
            for i, folder in enumerate(folders):
                folder_str = folder.decode('utf-8') if isinstance(folder, bytes) else str(folder)
                print(f"{i+1}: {repr(folder_str)}")
                # Check specifically for spam folder
                if 'spam' in folder_str.lower():
                    print(f"   ^ FOUND SPAM FOLDER: {folder_str}")
            print("=== END RAW FOLDERS ===")

            for folder in folders:
                try:
                    folder_info = folder.decode('utf-8') if isinstance(folder, bytes) else str(folder)
                    print(f"Processing folder info: {repr(folder_info)}")
                    
                    # Parse folder with attributes using injected parser
                    parsed_folder = self.folder_parser.parse_folder_info(folder_info)
                    
                    # Special debug for spam folder
                    if 'spam' in folder_info.lower():
                        print(f"SPAM FOLDER DEBUG:")
                        print(f"  Raw info: {repr(folder_info)}")
                        print(f"  Parsed result: {parsed_folder}")
                        if parsed_folder:
                            print(f"  Name: {parsed_folder.name}")
                            print(f"  Hidden: {parsed_folder.is_hidden}")
                            print(f"  Selectable: {parsed_folder.is_selectable}")
                    
                    if not parsed_folder:
                        print(f"Failed to parse folder: {folder_info}")
                        continue
                    
                    # Skip hidden folders unless explicitly requested
                    if parsed_folder.is_hidden and not include_hidden:
                        print(f"Skipping hidden folder: {parsed_folder.name}")
                        continue
                    
                    # Skip non-selectable folders
                    if not parsed_folder.is_selectable:
                        print(f"Skipping non-selectable folder: {parsed_folder.name}")
                        continue
                    
                    # Use parsed folder directly since it's already an EmailFolder object
                    folder_list.append(parsed_folder)
                    print(f"Added folder: {parsed_folder}")
                    
                except Exception as e:
                    print(f"Failed to parse folder: {folder_info}, error: {e}")
                    continue
            
            # If no folders found, add standard ones
            if not folder_list:
                folder_list = self._create_standard_folders()
            
            # Special check: ensure INBOX.spam is included if it exists on server
            spam_folder_names = ['INBOX.spam', 'INBOX.Spam', 'INBOX.SPAM', 'spam', 'Spam', 'SPAM', 'Junk']
            spam_found = any('spam' in f.name.lower() or 'junk' in f.name.lower() for f in folder_list)
            
            if not spam_found:
                print("INBOX.spam not found in folder list, checking server directly...")
                for spam_name in spam_folder_names:
                    try:
                        # Try to select the folder to see if it exists
                        test_status, _ = self.connection.select(spam_name, readonly=True)
                        if test_status == 'OK':
                            print(f"Found spam folder on server: {spam_name}")
                            # Create EmailFolder object for the spam folder
                            spam_folder = EmailFolder(
                                name=spam_name,
                                display_name='Spam',
                                type='spam',
                                attributes=[],
                                is_hidden=False,
                                is_selectable=True,
                                delimiter='.'
                            )
                            folder_list.append(spam_folder)
                            print(f"Added spam folder: {spam_folder}")
                            break
                    except Exception as e:
                        print(f"Failed to check spam folder {spam_name}: {e}")
                        continue
            
            # Sort folders using utility function
            folder_list = EmailFolderUtils.sort_folders(folder_list)
            
            print(f"Final folder list ({len(folder_list)} folders): {[f.name for f in folder_list]}")
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
            
            return emails
        except Exception as e:
            print(f"Failed to get emails: {e}")
            return []
    
    def _create_standard_folders(self) -> List[EmailFolder]:
        """Create standard folders when none are found"""
        print("No folders found, adding standard folders...")
        
        # Try multiple variations of standard folder names
        standard_folder_variations = [
            ('INBOX', 'Inbox', 'inbox'),
            ('SENT', 'Sent', 'INBOX.Sent', 'INBOX.SENT'),
            ('DRAFTS', 'Drafts', 'INBOX.Drafts', 'INBOX.DRAFTS'),
            ('SPAM', 'Spam', 'INBOX.spam', 'INBOX.Spam', 'INBOX.SPAM', 'Junk', 'INBOX.Junk'),
            ('TRASH', 'Trash', 'INBOX.Trash', 'INBOX.TRASH', 'Deleted Items')
        ]
        
        folder_list = []
        
        for folder_group in standard_folder_variations:
            folder_added = False
            primary_name = folder_group[0]
            
            for folder_variant in folder_group:
                try:
                    # Test if folder exists by trying to select it
                    test_status, _ = self.connection.select(folder_variant, readonly=True)
                    if test_status == 'OK':
                        email_folder = EmailFolder(
                            name=folder_variant,
                            display_name=primary_name.title(),
                            type=EmailFolderUtils.get_folder_type(primary_name),
                            attributes=[],
                            is_hidden=False,
                            is_selectable=True,
                            delimiter='.' if '.' in folder_variant else '/'
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
