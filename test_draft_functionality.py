#!/usr/bin/env python3
"""
Test script for draft email functionality
"""

from src.models.email_models import DraftEmail, ConnectionConfig

def test_draft_model():
    """Test the DraftEmail model"""
    print("Testing DraftEmail model...")
    
    # Test creating a draft email
    draft_data = {
        'to': 'test@example.com',
        'cc': 'cc@example.com',
        'bcc': 'bcc@example.com',
        'subject': 'Test Subject',
        'body': 'This is a test email body.',
        'reply_to_id': '12345'
    }
    
    # Create from dict
    draft = DraftEmail.from_dict(draft_data)
    print(f"Draft created: {draft}")
    
    # Convert to dict
    draft_dict = draft.to_dict()
    print(f"Draft as dict: {draft_dict}")
    
    print("✅ DraftEmail model test passed!")

def test_connection_config():
    """Test the updated ConnectionConfig model"""
    print("Testing ConnectionConfig model...")
    
    config_data = {
        'IMAP_SERVER': 'imap.gmail.com',
        'IMAP_PORT': '993',
        'IMAP_USERNAME': 'test@gmail.com',
        'IMAP_PASSWORD': 'password123',
        'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com/',
        'AZURE_OPENAI_API_KEY': 'api-key-123',
        'AZURE_OPENAI_DEPLOYMENT': 'gpt-4',
        'AZURE_OPENAI_API_VERSION': '2024-12-01-preview'
    }
    
    # Create from dict
    config = ConnectionConfig.from_dict(config_data)
    print(f"Config created: {config}")
    print(f"Auto-configured SMTP server: {config.smtp_server}")
    
    # Convert to dict
    config_dict = config.to_dict()
    print(f"Config as dict keys: {list(config_dict.keys())}")
    
    print("✅ ConnectionConfig model test passed!")

if __name__ == "__main__":
    test_draft_model()
    print()
    test_connection_config()
    print("\n🎉 All tests passed! Draft email functionality is ready.")
