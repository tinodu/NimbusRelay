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
            print("=== Service Manager Connection Debug ===")
            print(f"Config received: {list(config_dict.keys())}")
            for key, value in config_dict.items():
                if 'password' in key.lower() or 'key' in key.lower():
                    print(f"{key}: {'*' * len(value) if value else 'EMPTY'}")
                else:
                    print(f"{key}: {value}")
            print("=" * 40)
            
            config = ConnectionConfig.from_dict(config_dict)
            self._connection_config = config
            
            # Connect to email service
            print("Attempting to connect to email service...")
            email_connected = self.email_service.connect(config)
            if not email_connected:
                print("Email service connection failed")
                return {
                    'success': False,
                    'error': 'Failed to connect to email service'
                }
            print("Email service connected successfully")
            
            # Connect to AI service
            print("Attempting to connect to AI service...")
            ai_connected = self.ai_service.connect(config)
            if not ai_connected:
                print("AI service connection failed")
                return {
                    'success': False,
                    'error': 'Failed to connect to AI service'
                }
            print("AI service connected successfully")
            
            return {
                'success': True,
                'message': 'Connected to all services successfully'
            }
            
        except Exception as e:
            print(f"Service manager connection error: {e}")
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
    
    def get_folder_counts(self) -> Dict[str, Any]:
        """
        Get email counts for all folders
        
        Returns:
            Dict: Folder counts or error
        """
        try:
            if not self.email_service.is_connected():
                return {
                    'error': 'Email service not connected. Please connect first.'
                }
            
            # Get all folders
            folders = self.email_service.list_folders(include_hidden=False)
            folder_counts = {}
            
            # Get count for each folder
            for folder in folders:
                try:
                    # Use the get_folder_count method to get accurate counts
                    count = self.email_service.get_folder_count(folder.name)
                    folder_counts[folder.name] = count
                except Exception as e:
                    print(f"Error getting count for folder {folder.name}: {e}")
                    folder_counts[folder.name] = 0
            
            return {
                'counts': folder_counts
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
            print(f"[SPAM ANALYSIS] Starting analysis for email: Subject='{email_data.get('subject', 'N/A')}', From='{email_data.get('from', 'N/A')}'")
            
            if not self.ai_service.is_connected():
                print("[SPAM ANALYSIS] AI service not connected, using mock analysis")
                # Return a mock analysis for demo purposes when AI service is not connected
                subject = email_data.get('subject', '').lower()
                from_addr = email_data.get('from', '').lower()
                
                print(f"[SPAM ANALYSIS] Mock analysis inputs: subject='{subject}', from='{from_addr}'")
                
                # Simple rule-based spam detection for demo
                is_spam = False
                reason = "Mock analysis - AI service not connected"
                
                # Basic spam indicators
                spam_keywords = ['free', 'urgent', 'limited time', 'act now', 'click here', 'guaranteed', 'prize']
                suspicious_domains = ['spam.com', 'fake.org', 'scam.net']
                
                if any(keyword in subject for keyword in spam_keywords):
                    is_spam = True
                    reason = "Contains spam keywords in subject"
                    print(f"[SPAM ANALYSIS] Mock: Detected spam keywords in subject")
                elif any(domain in from_addr for domain in suspicious_domains):
                    is_spam = True
                    reason = "Suspicious sender domain"
                    print(f"[SPAM ANALYSIS] Mock: Detected suspicious domain")
                elif subject == '(no subject)' or subject == '':
                    is_spam = True
                    reason = "No subject line"
                    print(f"[SPAM ANALYSIS] Mock: No subject line detected")
                else:
                    reason = "Appears to be legitimate email"
                    print(f"[SPAM ANALYSIS] Mock: Email appears legitimate")
                
                result = {
                    'classification': 'Spam/Junk' if is_spam else 'Valid',
                    'confidence': 0.7 if is_spam else 0.8,
                    'reason': reason + ' (Demo mode - configure Azure OpenAI for real analysis)'
                }
                
                print(f"[SPAM ANALYSIS] Mock result: {result}")
                return result

            print("[SPAM ANALYSIS] Using AI service for analysis")
            # Convert dict to EmailMessage with default values for missing fields
            email_obj = EmailMessage(
                id=email_data.get('id', ''),
                from_address=email_data.get('from', ''),
                to_address=email_data.get('to', ''),
                subject=email_data.get('subject', ''),
                date=email_data.get('date', ''),
                content_type=email_data.get('content_type', 'text/plain'),
                body=email_data.get('body', email_data.get('preview', '')),
                preview=email_data.get('preview', '')
            )
            
            result = self.ai_service.analyze_spam(email_obj)
            result_dict = result.to_dict()
            print(f"[SPAM ANALYSIS] AI service result: {result_dict}")
            return result_dict
            
        except Exception as e:
            error_msg = str(e)
            print(f"[SPAM ANALYSIS] Exception occurred: {error_msg}")
            return {'error': error_msg}
    
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
    
    def move_email(self, email_id: str, source_folder: str, target_folder: str) -> Dict[str, Any]:
        """
        Move email from source folder to target folder
        
        Args:
            email_id: ID of email to move
            source_folder: Source folder name
            target_folder: Target folder name
            
        Returns:
            Dict: Move operation result
        """
        try:
            print(f"[SERVICE MANAGER] Moving email {email_id} from {source_folder} to {target_folder}")
            
            if not self.email_service.is_connected():
                print("[SERVICE MANAGER] Email service not connected")
                return {'error': 'Email service not connected. Please connect first.'}
            
            # Use the email service to move the email
            success = self.email_service.move_email(email_id, source_folder, target_folder)
            
            if success:
                print(f"[SERVICE MANAGER] Successfully moved email {email_id}")
                return {
                    'success': True,
                    'message': f'Email moved from {source_folder} to {target_folder}',
                    'email_id': email_id,
                    'source_folder': source_folder,
                    'target_folder': target_folder
                }
            else:
                print(f"[SERVICE MANAGER] Failed to move email {email_id}")
                return {'error': 'Failed to move email'}
                
        except Exception as e:
            error_msg = str(e)
            print(f"[SERVICE MANAGER] Exception in move_email: {error_msg}")
            return {'error': error_msg}

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
