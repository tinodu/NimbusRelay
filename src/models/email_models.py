"""
Data models for NimbusRelay email management
Defines the structure for email-related data
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class EmailFolder:
    """Model representing an email folder"""
    name: str
    display_name: str
    type: str
    attributes: List[str]
    is_hidden: bool
    is_selectable: bool
    delimiter: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'name': self.name,
            'display_name': self.display_name,
            'type': self.type,
            'attributes': self.attributes,
            'is_hidden': self.is_hidden,
            'is_selectable': self.is_selectable,
            'delimiter': self.delimiter
        }


@dataclass
class EmailMessage:
    """Model representing an email message"""
    id: str
    from_address: str
    to_address: str
    subject: str
    date: str
    content_type: str
    body: Optional[str]  # legacy, for backward compatibility
    preview: str
    text_body: Optional[str] = None
    html_body: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'from': self.from_address,
            'to': self.to_address,
            'subject': self.subject,
            'date': self.date,
            'content_type': self.content_type,
            'body': self.body,
            'preview': self.preview,
            'text_body': self.text_body,
            'html_body': self.html_body
        }


@dataclass
class DraftEmail:
    """Model representing a draft email to be sent or saved"""
    to: str
    cc: Optional[str] = None
    bcc: Optional[str] = None
    subject: str = ""
    body: str = ""
    reply_to_id: Optional[str] = None  # ID of email being replied to
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'to': self.to,
            'cc': self.cc,
            'bcc': self.bcc,
            'subject': self.subject,
            'body': self.body,
            'reply_to_id': self.reply_to_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DraftEmail':
        """Create instance from dictionary"""
        return cls(
            to=data.get('to', ''),
            cc=data.get('cc'),
            bcc=data.get('bcc'),
            subject=data.get('subject', ''),
            body=data.get('body', ''),
            reply_to_id=data.get('reply_to_id')
        )


@dataclass
class SpamAnalysisResult:
    """Model representing spam analysis results"""
    classification: str
    confidence: float
    reason: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'classification': self.classification,
            'confidence': self.confidence,
            'reason': self.reason
        }


@dataclass
class ConnectionConfig:
    """Model representing connection configuration"""
    imap_server: str
    imap_port: int
    imap_username: str
    imap_password: str
    azure_endpoint: str
    azure_api_key: str
    azure_deployment: str
    azure_api_version: str
    smtp_server: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_sender_email: Optional[str] = None
    smtp_use_tls: bool = True
    
    @classmethod
    def from_dict(cls, config: Dict[str, str]) -> 'ConnectionConfig':
        """Create instance from dictionary"""
        # Auto-configure SMTP server based on IMAP server if not provided
        smtp_server = config.get('SMTP_SERVER')
        if not smtp_server and config.get('IMAP_SERVER'):
            imap_server = config.get('IMAP_SERVER', '')
            if 'gmail' in imap_server.lower():
                smtp_server = 'smtp.gmail.com'
            elif 'outlook' in imap_server.lower() or 'hotmail' in imap_server.lower():
                smtp_server = 'smtp-mail.outlook.com'
            elif 'yahoo' in imap_server.lower():
                smtp_server = 'smtp.mail.yahoo.com'
            else:
                # Generic fallback - replace imap with smtp
                smtp_server = imap_server.replace('imap', 'smtp')
        
        return cls(
            imap_server=config.get('IMAP_SERVER', ''),
            imap_port=int(config.get('IMAP_PORT', 993)),
            imap_username=config.get('IMAP_USERNAME', ''),
            imap_password=config.get('IMAP_PASSWORD', ''),
            azure_endpoint=config.get('AZURE_OPENAI_ENDPOINT', ''),
            azure_api_key=config.get('AZURE_OPENAI_API_KEY', ''),
            azure_deployment=config.get('AZURE_OPENAI_DEPLOYMENT', ''),
            azure_api_version=config.get('AZURE_OPENAI_API_VERSION', '2024-12-01-preview'),
            smtp_server=smtp_server,
            smtp_port=int(config.get('SMTP_PORT', 587)),
            smtp_username=config.get('SMTP_USERNAME', ''),
            smtp_password=config.get('SMTP_PASSWORD', ''),
            smtp_sender_email=config.get('SMTP_SENDER_EMAIL', ''),
            smtp_use_tls=config.get('SMTP_USE_TLS', 'true').lower() == 'true'
        )
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary"""
        return {
            'IMAP_SERVER': self.imap_server,
            'IMAP_PORT': str(self.imap_port),
            'IMAP_USERNAME': self.imap_username,
            'IMAP_PASSWORD': self.imap_password,
            'AZURE_OPENAI_ENDPOINT': self.azure_endpoint,
            'AZURE_OPENAI_API_KEY': self.azure_api_key,
            'AZURE_OPENAI_DEPLOYMENT': self.azure_deployment,
            'AZURE_OPENAI_API_VERSION': self.azure_api_version,
            'SMTP_SERVER': self.smtp_server or '',
            'SMTP_PORT': str(self.smtp_port),
            'SMTP_USERNAME': self.smtp_username or '',
            'SMTP_PASSWORD': self.smtp_password or '',
            'SMTP_SENDER_EMAIL': self.smtp_sender_email or '',
            'SMTP_USE_TLS': str(self.smtp_use_tls).lower()
        }
