"""
Abstract base class for email services
Defines the interface for email operations following Interface Segregation Principle
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from src.models.email_models import EmailFolder, EmailMessage, ConnectionConfig


class IEmailService(ABC):
    """Abstract interface for email services"""
    
    @abstractmethod
    def connect(self, config: ConnectionConfig) -> bool:
        """Connect to email service"""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from email service"""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if service is connected"""
        pass
    
    @abstractmethod
    def list_folders(self, include_hidden: bool = False) -> List[EmailFolder]:
        """List email folders"""
        pass
    
    @abstractmethod
    def get_emails(self, folder: str, limit: int = 50) -> List[EmailMessage]:
        """Get emails from folder"""
        pass


class IFolderParser(ABC):
    """Abstract interface for folder parsing"""
    
    @abstractmethod
    def parse_folder_info(self, folder_info: str) -> Dict[str, Any]:
        """Parse IMAP folder information"""
        pass
    
    @abstractmethod
    def is_folder_hidden(self, folder_name: str, attributes: List[str]) -> bool:
        """Determine if folder is hidden"""
        pass


class IEmailParser(ABC):
    """Abstract interface for email parsing"""
    
    @abstractmethod
    def parse_email(self, raw_email_bytes: bytes) -> EmailMessage:
        """Parse raw email into EmailMessage"""
        pass
