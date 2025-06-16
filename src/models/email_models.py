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
    
    @classmethod
    def from_dict(cls, config: Dict[str, str]) -> 'ConnectionConfig':
        """Create instance from dictionary"""
        return cls(
            imap_server=config.get('IMAP_SERVER', ''),
            imap_port=int(config.get('IMAP_PORT', 993)),
            imap_username=config.get('IMAP_USERNAME', ''),
            imap_password=config.get('IMAP_PASSWORD', ''),
            azure_endpoint=config.get('AZURE_OPENAI_ENDPOINT', ''),
            azure_api_key=config.get('AZURE_OPENAI_API_KEY', ''),
            azure_deployment=config.get('AZURE_OPENAI_DEPLOYMENT', ''),
            azure_api_version=config.get('AZURE_OPENAI_API_VERSION', '2024-12-01-preview')
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
            'AZURE_OPENAI_API_VERSION': self.azure_api_version
        }
