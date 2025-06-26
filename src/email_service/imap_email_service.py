"""
IMAP Email Logic Service

Encapsulates email-related IMAP operations, using an IMAPConnectionManager for connection handling.
"""

from typing import List, Optional, Dict, Any
from src.models.email_models import EmailMessage
from src.email_service.interfaces import IEmailParser
from src.email_service.message_parser import EmailMessageParser

class IMAPEmailService:
    """
    Service for IMAP email operations, using an IMAPConnectionManager for connection management.
    """

    def connect(self):
        """
        Establish and store an IMAP connection using the connection manager's configuration.
        """
        if not hasattr(self.connection_manager, "connect"):
            raise AttributeError("connection_manager does not support connect()")
        if not hasattr(self.connection_manager, "config") or self.connection_manager.config is None:
            raise ValueError("No connection configuration set on connection_manager")
        success = self.connection_manager.connect(self.connection_manager.config)
        if not success:
            raise ConnectionError("Failed to establish IMAP connection")
        self.connection = self.connection_manager.connection

    def __init__(
        self,
        connection_manager,
        message_parser: Optional[IEmailParser] = None,
    ):
        """
        Initialize the IMAPEmailService.

        Args:
            connection_manager: Instance managing IMAP connections.
            message_parser: Parser for email messages.
        """
        self.connection_manager = connection_manager
        self.message_parser = message_parser or EmailMessageParser()

    def get_emails(self, folder: str, limit: int = 50) -> List[EmailMessage]:
        """
        Retrieve emails from the specified folder.

        Args:
            folder: Folder name.
            limit: Maximum number of emails to retrieve.

        Returns:
            List[EmailMessage]: List of email messages.
        """
        conn = self.connection_manager.connection
        if not conn:
            return []
        try:
            select_status, select_response = conn.select(folder)
            if select_status != 'OK':
                return []
            status, messages = conn.search(None, 'ALL')
            if status != 'OK':
                return []
            email_ids = messages[0].split()
            emails = []
            for email_id in reversed(email_ids[-limit:]):
                try:
                    if not email_id or email_id in [b'0', b'']:
                        continue
                    email_id_str = email_id.decode('utf-8') if isinstance(email_id, bytes) else str(email_id)
                    if not email_id_str.isdigit():
                        continue
                    try:
                        status, msg_data = conn.fetch(email_id_str, '(RFC822)')
                    except Exception:
                        status = None
                        msg_data = None
                    if status != 'OK':
                        try:
                            status, msg_data = conn.uid('fetch', email_id_str, '(RFC822)')
                        except Exception:
                            continue
                    if status == 'OK' and msg_data and isinstance(msg_data, list) and len(msg_data) > 0 and isinstance(msg_data[0], tuple) and len(msg_data[0]) > 1:
                        raw_email = msg_data[0][1]
                        email_obj = self.message_parser.parse_email(raw_email)
                        email_obj.id = email_id_str
                        emails.append(email_obj)
                except Exception:
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
        except Exception:
            return []

    def move_email(self, email_id: str, from_folder: str, to_folder: str) -> bool:
        """
        Move an email from one folder to another.

        Args:
            email_id: ID of the email to move.
            from_folder: Source folder name.
            to_folder: Destination folder name.

        Returns:
            bool: Success status.
        """
        conn = self.connection_manager.connection
        if not conn:
            return False
        try:
            status, _ = conn.select(from_folder)
            if status != 'OK':
                return False
            copy_status, _ = conn.copy(email_id, to_folder)
            if copy_status != 'OK':
                return False
            store_status, _ = conn.store(email_id, '+FLAGS', '\\Deleted')
            if store_status != 'OK':
                return False
            expunge_status, _ = conn.expunge()
            return expunge_status == 'OK'
        except Exception:
            return False

    def move_emails_by_criteria(self, from_folder: str, to_folder: str, criteria: str = 'ALL') -> Dict[str, int]:
        """
        Move multiple emails based on search criteria.

        Args:
            from_folder: Source folder name.
            to_folder: Destination folder name.
            criteria: IMAP search criteria (default: 'ALL').

        Returns:
            dict: Results with counts of moved emails and errors.
        """
        conn = self.connection_manager.connection
        if not conn:
            return {'moved': 0, 'errors': 0, 'error': 'No connection'}
        try:
            status, _ = conn.select(from_folder)
            if status != 'OK':
                return {'moved': 0, 'errors': 0, 'error': f'Failed to select {from_folder}'}
            search_status, messages = conn.search(None, criteria)
            if search_status != 'OK':
                return {'moved': 0, 'errors': 0, 'error': 'Search failed'}
            email_ids = messages[0].split()
            if not email_ids:
                return {'moved': 0, 'errors': 0, 'message': 'No emails found'}
            moved_count = 0
            error_count = 0
            for email_id in email_ids:
                try:
                    email_id_str = email_id.decode('utf-8') if isinstance(email_id, bytes) else str(email_id)
                    if self.move_email(email_id_str, from_folder, to_folder):
                        moved_count += 1
                    else:
                        error_count += 1
                except Exception:
                    error_count += 1
            return {
                'moved': moved_count,
                'errors': error_count,
                'total_found': len(email_ids)
            }
        except Exception as e:
            return {'moved': 0, 'errors': 1, 'error': str(e)}

    def get_raw_email(self, email_id: str) -> Optional[str]:
        """
        Fetch the raw RFC822 source of an email by ID from allowed folders.

        Args:
            email_id: ID of the email.

        Returns:
            Optional[str]: Raw email source if found, else None.
        """
        conn = self.connection_manager.connection
        if not conn:
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
                status, _ = conn.select(folder, readonly=True)
                if status != 'OK':
                    continue
                status, msg_data = conn.fetch(email_id, '(RFC822)')
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

        Args:
            email_id: ID of the email.

        Returns:
            Optional[str]: HTML part if present, otherwise None.
        """
        import email
        conn = self.connection_manager.connection
        if not conn:
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
                status, _ = conn.select(folder, readonly=True)
                if status != 'OK':
                    continue
                status, msg_data = conn.fetch(email_id, '(RFC822)')
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

    def is_connected(self) -> bool:
        """
        Check if the IMAP connection is currently established.
        """
        return self.connection_manager.is_connected()
    
    def save_draft(self, draft, folder: str = "INBOX.Drafts") -> Dict[str, Any]:
        """
        Save a draft email to the specified folder (typically Drafts)
        
        Args:
            draft: DraftEmail object or dict containing draft data
            folder: Folder to save draft to (default: INBOX.Drafts)
            
        Returns:
            Dict: Result of save operation
        """
        try:
            from src.models.email_models import DraftEmail
            import email.mime.text
            import email.mime.multipart
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            from datetime import datetime
            import email.utils
            import imaplib
            
            conn = self.connection_manager.connection
            if not conn:
                return {'error': 'IMAP connection not available'}
            
            # Convert dict to DraftEmail if needed
            if isinstance(draft, dict):
                draft = DraftEmail.from_dict(draft)
            
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.connection_manager.config.imap_username if self.connection_manager.config else ""
            msg['To'] = draft.to
            msg['Subject'] = draft.subject or '(no subject)'
            msg['Date'] = email.utils.formatdate(localtime=True)
            
            # Add CC and BCC if provided
            if draft.cc:
                msg['Cc'] = draft.cc
            if draft.bcc:
                msg['Bcc'] = draft.bcc
            
            # Add message body
            if draft.body:
                text_part = MIMEText(draft.body, 'plain', 'utf-8')
                msg.attach(text_part)
            
            # Convert message to string
            draft_content = msg.as_string()
            
            # Ensure the drafts folder exists
            try:
                conn.select(folder)
            except imaplib.IMAP4.error:
                # Try to create the folder if it doesn't exist
                try:
                    conn.create(folder)
                    print(f"Created drafts folder: {folder}")
                except Exception as create_error:
                    print(f"Failed to create drafts folder: {create_error}")
                    return {'error': f'Drafts folder "{folder}" does not exist and could not be created'}
            
            # Append draft to folder
            result = conn.append(folder, None, None, draft_content.encode('utf-8'))
            
            if result[0] == 'OK':
                print(f"Draft saved successfully to {folder}")
                return {
                    'success': True,
                    'message': f'Draft saved to {folder}',
                    'folder': folder
                }
            else:
                error_msg = f"Failed to save draft: {result[1] if len(result) > 1 else 'Unknown error'}"
                print(error_msg)
                return {'error': error_msg}
                
        except Exception as e:
            error_msg = f"Error saving draft: {str(e)}"
            print(error_msg)
            return {'error': error_msg}