"""
SMTP Email Service

Handles sending emails via SMTP protocol
"""

import smtplib
import email.mime.text
import email.mime.multipart
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from src.models.email_models import ConnectionConfig, DraftEmail


class SMTPEmailService:
    """Service for sending emails via SMTP"""
    
    def __init__(self, config: Optional[ConnectionConfig] = None):
        """
        Initialize SMTP service
        
        Args:
            config: Connection configuration containing SMTP settings
        """
        self.config = config
        self._connection: Optional[smtplib.SMTP] = None
    
    def connect(self, config: ConnectionConfig) -> bool:
        """
        Connect to SMTP server
        
        Args:
            config: Connection configuration
            
        Returns:
            bool: True if connection successful
        """
        try:
            self.config = config
            
            if not config.smtp_server:
                raise ValueError("SMTP server not configured")
            
            print(f"Connecting to SMTP server: {config.smtp_server}:{config.smtp_port}")
            
            # Create SMTP connection
            self._connection = smtplib.SMTP(config.smtp_server, config.smtp_port)
            
            # Enable TLS if configured
            if config.smtp_use_tls:
                self._connection.starttls()
                print("TLS enabled for SMTP connection")
            
            # Login with credentials - use SMTP credentials if available, otherwise fallback to IMAP
            smtp_username = config.smtp_username or config.imap_username
            smtp_password = config.smtp_password or config.imap_password
            self._connection.login(smtp_username, smtp_password)
            print("SMTP authentication successful")
            
            return True
            
        except Exception as e:
            print(f"Failed to connect to SMTP server: {e}")
            self._connection = None
            return False
    
    def disconnect(self) -> None:
        """Disconnect from SMTP server"""
        if self._connection:
            try:
                self._connection.quit()
            except Exception as e:
                print(f"Error disconnecting from SMTP: {e}")
            finally:
                self._connection = None
    
    def is_connected(self) -> bool:
        """Check if connected to SMTP server"""
        if not self._connection:
            return False
        
        try:
            # Test connection by sending NOOP command
            status = self._connection.noop()[0]
            return status == 250
        except Exception:
            return False
    
    def send_email(self, draft: DraftEmail) -> Dict[str, Any]:
        """
        Send an email
        
        Args:
            draft: Draft email to send
            
        Returns:
            Dict: Result of send operation
        """
        try:
            if not self.is_connected():
                return {'error': 'SMTP service not connected'}
            
            if not self.config:
                return {'error': 'SMTP configuration not available'}
            
            # Validate required fields
            if not draft.to:
                return {'error': 'Recipient email address is required'}
            
            # Create message
            msg = MIMEMultipart('alternative')
            # Use dedicated sender email if configured, otherwise fallback to IMAP username
            sender_email = self.config.smtp_sender_email or self.config.imap_username
            msg['From'] = sender_email
            msg['To'] = draft.to
            msg['Subject'] = draft.subject or '(no subject)'
            
            # Add CC and BCC if provided
            all_recipients = [draft.to]
            if draft.cc:
                msg['Cc'] = draft.cc
                all_recipients.extend([addr.strip() for addr in draft.cc.split(',')])
            if draft.bcc:
                # BCC is not added to headers, just to recipient list
                all_recipients.extend([addr.strip() for addr in draft.bcc.split(',')])
            
            # Add message body
            if draft.body:
                # For now, treat all content as plain text
                # In the future, could detect HTML content and handle accordingly
                text_part = MIMEText(draft.body, 'plain', 'utf-8')
                msg.attach(text_part)
            
            # Send the email
            self._connection.send_message(msg, to_addrs=all_recipients)
            
            print(f"Email sent successfully to: {', '.join(all_recipients)}")
            
            return {
                'success': True,
                'message': f'Email sent to {len(all_recipients)} recipient(s)',
                'recipients': all_recipients
            }
            
        except Exception as e:
            error_msg = f"Failed to send email: {str(e)}"
            print(error_msg)
            return {'error': error_msg}
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure connection is closed"""
        self.disconnect()
