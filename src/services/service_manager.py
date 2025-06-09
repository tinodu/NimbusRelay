"""
Service Manager - Coordinates email and AI services
Follows the Facade Pattern to provide simplified interface
"""

from typing import List, Dict, Any, Optional
from src.email_service.interfaces import IEmailService
from src.ai.interfaces import IAIService
from src.email_service.imap_service import IMAPEmailService
from src.ai.azure_service import AzureAIService
from src.models.email_models import EmailFolder, EmailMessage, SpamAnalysisResult, ConnectionConfig


class ServiceManager:
    """
    Facade for coordinating email and AI services
    Provides a simplified interface following the Facade Pattern
    """
    
    def __init__(self, 
                 email_service: IEmailService = None,
                 ai_service: IAIService = None):
        """
        Initialize service manager with dependency injection
        
        Args:
            email_service: Email service implementation
            ai_service: AI service implementation
        """
        # Dependency injection allows for easy testing and service swapping
        self.email_service = email_service or IMAPEmailService()
        self.ai_service = ai_service or AzureAIService()
        
        self._connection_config: Optional[ConnectionConfig] = None
    
    def connect_services(self, config_dict: Dict[str, str]) -> Dict[str, Any]:
        """
        Connect both email and AI services
        
        Args:
            config_dict: Configuration dictionary
            
        Returns:
            Dict: Connection status and messages
        """
        try:
            config = ConnectionConfig.from_dict(config_dict)
            self._connection_config = config
            
            # Connect to email service
            email_connected = self.email_service.connect(config)
            if not email_connected:
                return {
                    'success': False,
                    'error': 'Failed to connect to email service'
                }
            
            # Connect to AI service
            ai_connected = self.ai_service.connect(config)
            if not ai_connected:
                return {
                    'success': False,
                    'error': 'Failed to connect to AI service'
                }
            
            return {
                'success': True,
                'message': 'Connected to all services successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def disconnect_services(self) -> None:
        """Disconnect all services"""
        if hasattr(self.email_service, 'disconnect'):
            self.email_service.disconnect()
    
    def get_folders(self, include_hidden: bool = False) -> Dict[str, Any]:
        """
        Get email folders
        
        Args:
            include_hidden: Whether to include hidden folders
            
        Returns:
            Dict: Folders data or error
        """
        try:
            if not self.email_service.is_connected():
                return {
                    'error': 'Email service not connected. Please connect first.'
                }
            
            folders = self.email_service.list_folders(include_hidden)
            return {
                'folders': [folder.to_dict() for folder in folders]
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_emails(self, folder: str, limit: int = 50) -> Dict[str, Any]:
        """
        Get emails from folder
        
        Args:
            folder: Folder name
            limit: Maximum number of emails
            
        Returns:
            Dict: Emails data or error
        """
        try:
            if not self.email_service.is_connected():
                return {
                    'error': 'Email service not connected. Please connect first.'
                }
            
            emails = self.email_service.get_emails(folder, limit)
            return {
                'emails': [email.to_dict() for email in emails]
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_spam(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze email for spam
        
        Args:
            email_data: Email data dictionary
            
        Returns:
            Dict: Spam analysis results
        """
        try:
            if not self.ai_service.is_connected():
                return {
                    'error': 'AI service not connected. Please connect first.'
                }
            
            # Convert dict to EmailMessage
            email_obj = EmailMessage(
                id=email_data.get('id', ''),
                from_address=email_data.get('from', ''),
                to_address=email_data.get('to', ''),
                subject=email_data.get('subject', ''),
                date=email_data.get('date', ''),
                content_type=email_data.get('content_type', ''),
                body=email_data.get('body', ''),
                preview=email_data.get('preview', '')
            )
            
            result = self.ai_service.analyze_spam(email_obj)
            return result.to_dict()
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive email analysis
        
        Args:
            email_data: Email data dictionary
            
        Returns:
            Dict: Analysis results
        """
        try:
            if not self.ai_service.is_connected():
                return {
                    'error': 'AI service not connected. Please connect first.'
                }
            
            # Convert dict to EmailMessage
            email_obj = EmailMessage(
                id=email_data.get('id', ''),
                from_address=email_data.get('from', ''),
                to_address=email_data.get('to', ''),
                subject=email_data.get('subject', ''),
                date=email_data.get('date', ''),
                content_type=email_data.get('content_type', ''),
                body=email_data.get('body', ''),
                preview=email_data.get('preview', '')
            )
            
            analysis = self.ai_service.analyze_email(email_obj)
            return {'analysis': analysis}
            
        except Exception as e:
            return {'error': str(e)}
    
    def generate_draft(self, analysis_result: str) -> Dict[str, Any]:
        """
        Generate draft response
        
        Args:
            analysis_result: Email analysis results
            
        Returns:
            Dict: Draft response
        """
        try:
            if not self.ai_service.is_connected():
                return {
                    'error': 'AI service not connected. Please connect first.'
                }
            
            draft = self.ai_service.generate_draft(analysis_result)
            return {'draft': draft}
            
        except Exception as e:
            return {'error': str(e)}
    
    def is_connected(self) -> bool:
        """Check if both services are connected"""
        return (self.email_service.is_connected() and 
                self.ai_service.is_connected())
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get detailed connection status for both services"""
        return {
            'email_connected': self.email_service.is_connected(),
            'ai_connected': self.ai_service.is_connected(),
            'both_connected': self.is_connected()
        }
