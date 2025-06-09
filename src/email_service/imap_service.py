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
            print(f"Raw folder data: {folders}")
            
            if status != 'OK':
                print(f"IMAP LIST failed with status: {status}")
                return []
            
            for folder in folders:
                try:
                    folder_info = folder.decode('utf-8') if isinstance(folder, bytes) else str(folder)
                    print(f"Processing folder info: {repr(folder_info)}")
                    
                    # Parse folder with attributes using injected parser
                    parsed_folder = self.folder_parser.parse_folder_info(folder_info)
                    
                    if not parsed_folder:
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
        standard_folders = ['INBOX', 'SENT', 'DRAFTS', 'SPAM', 'TRASH']
        folder_list = []
        
        for std_folder in standard_folders:
            try:
                # Test if folder exists by trying to select it
                test_status, _ = self.connection.select(std_folder, readonly=True)
                if test_status == 'OK':
                    email_folder = EmailFolder(
                        name=std_folder,
                        display_name=std_folder.title(),
                        type=EmailFolderUtils.get_folder_type(std_folder),
                        attributes=[],
                        is_hidden=False,
                        is_selectable=True,
                        delimiter='/'
                    )
                    folder_list.append(email_folder)
                    print(f"Added standard folder: {std_folder}")
            except Exception as e:
                print(f"Standard folder {std_folder} not available: {e}")
                continue
        
        return folder_list
