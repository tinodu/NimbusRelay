"""
Simple test to validate modular architecture imports and basic functionality
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_import_models():
    """Test that we can import email models"""
    from models.email_models import EmailFolder, EmailMessage, SpamAnalysisResult, ConnectionConfig
    
    # Test EmailFolder creation
    folder = EmailFolder(
        name="INBOX",
        display_name="Inbox", 
        type="inbox",
        attributes=["HasNoChildren"],
        is_hidden=False,
        is_selectable=True,
        delimiter="/"
    )
    
    assert folder.name == "INBOX"
    assert folder.type == "inbox"

def test_import_email_services():
    """Test that we can import email service components"""
    from email_service.interfaces import IEmailService, IFolderParser, IEmailParser
    from email_service.folder_parser import IMAPFolderParser
    from email_service.message_parser import EmailMessageParser
    from email_service.utils import EmailFolderUtils
    
    # Test folder parser
    parser = IMAPFolderParser()
    assert parser is not None
    
    # Test folder utils
    folder_type = EmailFolderUtils.get_folder_type('INBOX')
    assert folder_type == 'inbox'

def test_import_ai_services():
    """Test that we can import AI service components"""
    from ai.interfaces import IAIService, IPromptLoader
    from ai.prompt_loader import FilePromptLoader
    
    # Test prompt loader
    loader = FilePromptLoader()
    assert loader is not None

def test_import_config():
    """Test that we can import configuration components"""
    from config.settings import Config, DevelopmentConfig
    from config.environment import EnvironmentManager
    
    # Test config creation
    config = DevelopmentConfig()
    assert config.DEBUG is True

def test_import_service_manager():
    """Test that we can import service manager"""
    from services.service_manager import ServiceManager
    from unittest.mock import Mock
    from email_service.interfaces import IEmailService
    from ai.interfaces import IAIService
    
    # Test service manager creation
    email_service = Mock(spec=IEmailService)
    ai_service = Mock(spec=IAIService)
    manager = ServiceManager(email_service, ai_service)
    assert manager is not None

def test_import_app_factory():
    """Test that we can import app factory"""
    from core.app_factory import create_app
    
    # Test app creation (but don't fully initialize to avoid dependencies)
    assert create_app is not None

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
