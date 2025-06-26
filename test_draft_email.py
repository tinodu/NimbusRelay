#!/usr/bin/env python3
"""
Test script for draft and email sending functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.models.email_models import DraftEmail, ConnectionConfig
from src.email_service.smtp_service import SMTPEmailService

def test_draft_email_model():
    """Test DraftEmail model creation and serialization"""
    print("Testing DraftEmail model...")
    
    # Test creating from dict
    draft_data = {
        'to': 'test@example.com',
        'cc': 'cc@example.com',
        'bcc': 'bcc@example.com',
        'subject': 'Test Subject',
        'body': 'Test email body content',
        'reply_to_id': '12345'
    }
    
    draft = DraftEmail.from_dict(draft_data)
    print(f"Created draft: {draft}")
    
    # Test serialization
    serialized = draft.to_dict()
    print(f"Serialized draft: {serialized}")
    
    # Verify data integrity
    assert draft.to == 'test@example.com'
    assert draft.subject == 'Test Subject'
    assert draft.reply_to_id == '12345'
    
    print("✅ DraftEmail model test passed!")

def test_connection_config():
    """Test ConnectionConfig with SMTP settings"""
    print("\nTesting ConnectionConfig with SMTP...")
    
    config_data = {
        'IMAP_SERVER': 'imap.gmail.com',
        'IMAP_PORT': '993',
        'IMAP_USERNAME': 'test@gmail.com',
        'IMAP_PASSWORD': 'test_password',
        'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com/',
        'AZURE_OPENAI_API_KEY': 'test_key',
        'AZURE_OPENAI_DEPLOYMENT': 'gpt-4',
        'AZURE_OPENAI_API_VERSION': '2024-12-01-preview'
    }
    
    config = ConnectionConfig.from_dict(config_data)
    print(f"Auto-configured SMTP server: {config.smtp_server}")
    print(f"SMTP port: {config.smtp_port}")
    print(f"SMTP TLS: {config.smtp_use_tls}")
    
    # Verify Gmail SMTP auto-configuration
    assert config.smtp_server == 'smtp.gmail.com'
    assert config.smtp_port == 587
    assert config.smtp_use_tls == True
    
    print("✅ ConnectionConfig SMTP test passed!")

def test_smtp_service_initialization():
    """Test SMTP service can be initialized"""
    print("\nTesting SMTPEmailService initialization...")
    
    config_data = {
        'IMAP_SERVER': 'imap.gmail.com',
        'IMAP_USERNAME': 'test@gmail.com',
        'IMAP_PASSWORD': 'test_password',
    }
    
    config = ConnectionConfig.from_dict(config_data)
    smtp_service = SMTPEmailService(config)
    
    print(f"SMTP service created with config: {config.smtp_server}")
    print("✅ SMTPEmailService initialization test passed!")

def test_smtp_sender_email_config():
    """Test SMTP sender email configuration"""
    print("\nTesting SMTP sender email configuration...")
    
    # Test with explicit sender email
    config_data_with_sender = {
        'IMAP_SERVER': 'imap.gmail.com',
        'IMAP_PORT': '993',
        'IMAP_USERNAME': 'test@gmail.com',
        'IMAP_PASSWORD': 'test_password',
        'SMTP_SENDER_EMAIL': 'sender@gmail.com',
        'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com/',
        'AZURE_OPENAI_API_KEY': 'test_key',
        'AZURE_OPENAI_DEPLOYMENT': 'gpt-4',
        'AZURE_OPENAI_API_VERSION': '2024-12-01-preview'
    }
    
    config_with_sender = ConnectionConfig.from_dict(config_data_with_sender)
    print(f"SMTP sender email (explicit): {config_with_sender.smtp_sender_email}")
    assert config_with_sender.smtp_sender_email == 'sender@gmail.com'
    
    # Test without explicit sender email (should default to empty)
    config_data_no_sender = {
        'IMAP_SERVER': 'imap.gmail.com',
        'IMAP_PORT': '993',
        'IMAP_USERNAME': 'test@gmail.com',
        'IMAP_PASSWORD': 'test_password',
        'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com/',
        'AZURE_OPENAI_API_KEY': 'test_key',
        'AZURE_OPENAI_DEPLOYMENT': 'gpt-4',
        'AZURE_OPENAI_API_VERSION': '2024-12-01-preview'
    }
    
    config_no_sender = ConnectionConfig.from_dict(config_data_no_sender)
    print(f"SMTP sender email (default): '{config_no_sender.smtp_sender_email}'")
    assert config_no_sender.smtp_sender_email == ''
    
    # Test serialization includes sender email
    config_dict = config_with_sender.to_dict()
    assert 'SMTP_SENDER_EMAIL' in config_dict
    assert config_dict['SMTP_SENDER_EMAIL'] == 'sender@gmail.com'
    
    print("✅ SMTP sender email configuration test passed!")

if __name__ == '__main__':
    print("🧪 Running draft and email functionality tests...\n")
    
    try:
        test_draft_email_model()
        test_connection_config()
        test_smtp_service_initialization()
        test_smtp_sender_email_config()
        
        print("\n🎉 All tests passed! Draft and email sending functionality is ready.")
        print("\nNext steps:")
        print("1. Configure your email settings in the web interface")
        print("2. Try generating a draft response to an email")
        print("3. Use 'Save Draft' to save to INBOX.Drafts folder")
        print("4. Use 'Send Reply' to send the email immediately")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
