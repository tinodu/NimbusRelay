"""
Test suite for NimbusRelay Email Management Application
Tests for modular architecture with SOLID principles
"""

import pytest
import json
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from dataclasses import asdict

# Import the modular components
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import new modular components
from core.app_factory import create_app
from config.settings import Config, DevelopmentConfig
from config.environment import EnvironmentManager
from models.email_models import EmailFolder, EmailMessage, SpamAnalysisResult, ConnectionConfig
from src.email_service.interfaces import IEmailService, IFolderParser, IEmailParser
from src.email_service.imap_service import IMAPEmailService
from src.email_service.folder_parser import IMAPFolderParser
from src.email_service.message_parser import EmailMessageParser
from ai.interfaces import IAIService, IPromptLoader
from ai.azure_service import AzureAIService
from services.service_manager import ServiceManager

class TestEmailService:
    """Test cases for EmailService class"""
    
    def test_init(self):
        """Test EmailService initialization"""
        service = EmailService()
        assert service.connection is None
        assert service.config == {}
    
    @patch('imaplib.IMAP4_SSL')
    def test_connect_success(self, mock_imap):
        """Test successful email service connection"""
        # Setup
        mock_connection = Mock()
        mock_imap.return_value = mock_connection
        mock_connection.login.return_value = ('OK', ['Login successful'])
        
        service = EmailService()
        config = {
            'IMAP_SERVER': 'imap.test.com',
            'IMAP_PORT': '993',
            'IMAP_USERNAME': 'test@test.com',
            'IMAP_PASSWORD': 'password123'
        }
        
        # Execute
        result = service.connect(config)
        
        # Assert
        assert result is True
        assert service.config == config
        assert service.connection == mock_connection
        mock_imap.assert_called_once_with('imap.test.com', 993)
        mock_connection.login.assert_called_once_with('test@test.com', 'password123')
    
    @patch('imaplib.IMAP4_SSL')
    def test_connect_failure(self, mock_imap):
        """Test failed email service connection"""
        # Setup
        mock_imap.side_effect = Exception("Connection failed")
        
        service = EmailService()
        config = {
            'IMAP_SERVER': 'imap.test.com',
            'IMAP_PORT': '993',
            'IMAP_USERNAME': 'test@test.com',
            'IMAP_PASSWORD': 'wrong_password'
        }
        
        # Execute
        result = service.connect(config)
        
        # Assert
        assert result is False
        assert service.connection is None
    
    def test_get_folder_type(self):
        """Test folder type classification"""
        service = EmailService()
        
        assert service._get_folder_type('INBOX') == 'inbox'
        assert service._get_folder_type('Sent') == 'sent'
        assert service._get_folder_type('Drafts') == 'drafts'
        assert service._get_folder_type('Trash') == 'trash'
        assert service._get_folder_type('INBOX.spam') == 'spam'
        assert service._get_folder_type('CustomFolder') == 'custom'
    
    @patch('imaplib.IMAP4_SSL')
    def test_list_folders(self, mock_imap):
        """Test folder listing functionality"""
        # Setup
        mock_connection = Mock()
        mock_imap.return_value = mock_connection
        
        service = EmailService()
        service.connection = mock_connection
        
        mock_connection.list.return_value = ('OK', [
            b'(\\HasNoChildren) "." "INBOX"',
            b'(\\HasNoChildren) "." "INBOX.Sent"',
            b'(\\HasNoChildren) "." "INBOX.Drafts"',
        ])
        
        # Execute
        folders = service.list_folders()
        
        # Assert
        assert len(folders) == 3
        assert folders[0]['name'] == 'INBOX'
        assert folders[0]['display_name'] == 'Inbox'
        assert folders[0]['type'] == 'inbox'
    
    def test_parse_email(self):
        """Test email parsing functionality"""
        service = EmailService()
        
        # Create a simple test email
        raw_email = b"""From: sender@test.com
To: recipient@test.com
Subject: Test Subject
Date: Mon, 01 Jan 2024 12:00:00 +0000
Content-Type: text/plain; charset=utf-8

This is a test email body.
"""
        
        # Execute
        email_obj = service._parse_email(raw_email)
        
        # Assert
        assert email_obj['from'] == 'sender@test.com'
        assert email_obj['to'] == 'recipient@test.com'
        assert email_obj['subject'] == 'Test Subject'
        assert 'This is a test email body.' in email_obj['body']
        assert email_obj['preview'] == 'This is a test email body.'

class TestEmailServiceFolderParsing:
    """Test cases for EmailService folder parsing functionality"""
    
    def test_parse_folder_name_and_attributes(self):
        """Test IMAP folder parsing with various formats"""
        service = EmailService()
        
        # Test standard Gmail format
        folder_info = '* LIST (\\HasNoChildren) "/" "INBOX"'
        result = service._parse_folder_name_and_attributes(folder_info)
        assert result['name'] == 'INBOX'
        assert result['attributes'] == ['HasNoChildren']
        assert result['is_selectable'] == True
        
        # Test with hidden folder
        folder_info = '* LIST (\\HasNoChildren \\All) "/" "[Gmail]/All Mail"'
        result = service._parse_folder_name_and_attributes(folder_info)
        assert result['name'] == '[Gmail]/All Mail'
        assert result['is_hidden'] == True
        
        # Test with Noselect attribute
        folder_info = '* LIST (\\Noselect \\HasChildren) "/" "Gmail"'
        result = service._parse_folder_name_and_attributes(folder_info)
        assert result['name'] == 'Gmail'
        assert result['is_selectable'] == False
    
    def test_is_folder_hidden(self):
        """Test folder hidden detection logic"""
        service = EmailService()
        
        # Test Gmail hidden patterns
        assert service._is_folder_hidden('[Gmail]/All Mail', ['All']) == True
        assert service._is_folder_hidden('Gmail/Spam', []) == True
        assert service._is_folder_hidden('INBOX', []) == False
        
        # Test Outlook patterns
        assert service._is_folder_hidden('Calendar', []) == True
        assert service._is_folder_hidden('Contacts', []) == True
        assert service._is_folder_hidden('Sync Issues', []) == True
        
        # Test attribute-based hiding
        assert service._is_folder_hidden('SomeFolder', ['Hidden']) == True
        assert service._is_folder_hidden('SomeFolder', ['Noselect']) == True
        assert service._is_folder_hidden('SomeFolder', ['Archive']) == True

class TestAIService:
    """Test cases for AIService class"""
    
    def test_init(self):
        """Test AIService initialization"""
        service = AIService()
        assert service.client is None
        assert service.config == {}
    
    @patch('app.AzureOpenAI')
    def test_connect_success(self, mock_azure_client):
        """Test successful AI service connection"""
        # Setup
        mock_client = Mock()
        mock_azure_client.return_value = mock_client
        
        service = AIService()
        config = {
            'AZURE_OPENAI_API_VERSION': '2024-02-01',
            'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com/',
            'AZURE_OPENAI_API_KEY': 'test-key',
            'AZURE_OPENAI_DEPLOYMENT': 'gpt-4'
        }
        
        # Execute
        result = service.connect(config)
        
        # Assert
        assert result is True
        assert service.config == config
        assert service.client == mock_client
    
    @patch('app.AzureOpenAI')
    def test_connect_failure(self, mock_azure_client):
        """Test failed AI service connection"""
        # Setup
        mock_azure_client.side_effect = Exception("API connection failed")
        
        service = AIService()
        config = {
            'AZURE_OPENAI_API_VERSION': '2024-02-01',
            'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com/',
            'AZURE_OPENAI_API_KEY': 'invalid-key',
            'AZURE_OPENAI_DEPLOYMENT': 'gpt-4'
        }
        
        # Execute
        result = service.connect(config)
        
        # Assert
        assert result is False
        assert service.client is None
    
    @patch('builtins.open', create=True)
    def test_analyze_spam(self, mock_open):
        """Test spam analysis functionality"""
        # Setup
        service = AIService()
        
        mock_client = Mock()
        service.client = mock_client
        service.config = {'AZURE_OPENAI_DEPLOYMENT': 'gpt-4'}
        
        # Mock file reading
        mock_open.return_value.__enter__.return_value.read.return_value = "Spam detection prompt"
        
        # Mock API response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"classification": "Not Spam", "confidence": 0.9, "reason": "Legitimate email"}'
        mock_client.chat.completions.create.return_value = mock_response
        
        email_obj = {
            'from': 'test@test.com',
            'subject': 'Test Email',
            'body': 'This is a test email'
        }
        
        # Execute
        result = service.analyze_spam(email_obj)
        
        # Assert
        assert result['classification'] == 'Not Spam'
        assert result['confidence'] == 0.9
        assert 'Legitimate email' in result['reason']
    
    @patch('builtins.open', create=True)
    def test_analyze_email(self, mock_open):
        """Test email analysis functionality"""
        # Setup
        service = AIService()
        
        mock_client = Mock()
        service.client = mock_client
        service.config = {'AZURE_OPENAI_DEPLOYMENT': 'gpt-4'}
        
        # Mock file reading
        mock_open.return_value.__enter__.return_value.read.return_value = "Email analysis prompt"
        
        # Mock API response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = 'Detailed email analysis result'
        mock_client.chat.completions.create.return_value = mock_response
        
        email_obj = {
            'from': 'test@test.com',
            'subject': 'Test Email',
            'body': 'This is a test email'
        }
        
        # Execute
        result = service.analyze_email(email_obj)
        
        # Assert
        assert result == 'Detailed email analysis result'
    
    @patch('builtins.open', create=True)
    def test_generate_draft(self, mock_open):
        """Test draft generation functionality"""
        # Setup
        service = AIService()
        
        mock_client = Mock()
        service.client = mock_client
        service.config = {'AZURE_OPENAI_DEPLOYMENT': 'gpt-4'}
        
        # Mock file reading
        mock_open.return_value.__enter__.return_value.read.return_value = "Draft generation prompt"
        
        # Mock API response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = 'Generated draft response'
        mock_client.chat.completions.create.return_value = mock_response
        
        analysis_result = "Email analysis indicating request for meeting"
        
        # Execute
        result = service.generate_draft(analysis_result)
        
        # Assert
        assert result == 'Generated draft response'

class TestUtilityFunctions:
    """Test cases for utility functions"""
    
    @patch.dict(os.environ, {
        'AZURE_OPENAI_ENDPOINT': 'https://test.com',
        'AZURE_OPENAI_API_KEY': 'test-key',
        'IMAP_SERVER': 'imap.test.com'
    })
    def test_get_required_env_vars(self):
        """Test environment variable retrieval"""
        env_vars = get_required_env_vars()
        
        assert env_vars['AZURE_OPENAI_ENDPOINT'] == 'https://test.com'
        assert env_vars['AZURE_OPENAI_API_KEY'] == 'test-key'
        assert env_vars['IMAP_SERVER'] == 'imap.test.com'
        assert env_vars['AZURE_OPENAI_API_VERSION'] == '2024-12-01-preview'  # Default value
    
    def test_save_env_var(self):
        """Test saving environment variables to .env file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Change to temporary directory
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Test saving a new variable
                result = save_env_var('TEST_VAR', 'test_value')
                assert result is True
                
                # Check if .env file was created and contains the variable
                env_file = Path('.env')
                assert env_file.exists()
                
                content = env_file.read_text()
                assert 'TEST_VAR=test_value' in content
                
                # Test updating existing variable
                result = save_env_var('TEST_VAR', 'updated_value')
                assert result is True
                
                content = env_file.read_text()
                assert 'TEST_VAR=updated_value' in content
                assert content.count('TEST_VAR=') == 1  # Should not duplicate
                
            finally:
                os.chdir(original_cwd)

class TestAPIEndpoints:
    """Test cases for Flask API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create a test client"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_index_route(self, client):
        """Test main index route"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'NimbusRelay' in response.data
    
    @patch('app.get_required_env_vars')
    def test_get_config(self, mock_get_env_vars, client):
        """Test configuration status endpoint"""
        mock_get_env_vars.return_value = {
            'AZURE_OPENAI_ENDPOINT': 'https://test.com',
            'AZURE_OPENAI_API_KEY': '',
            'IMAP_SERVER': 'imap.test.com',
            'IMAP_USERNAME': ''
        }
        
        response = client.get('/api/config')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['configured'] is False
        assert 'AZURE_OPENAI_API_KEY' in data['missing_vars']
        assert 'IMAP_USERNAME' in data['missing_vars']
    
    @patch('app.save_env_var')
    def test_save_config(self, mock_save_env_var, client):
        """Test configuration saving endpoint"""
        mock_save_env_var.return_value = True
        
        config_data = {
            'IMAP_SERVER': 'imap.test.com',
            'IMAP_USERNAME': 'test@test.com',
            'AZURE_OPENAI_ENDPOINT': 'https://test.com'
        }
        
        response = client.post('/api/config',
                             data=json.dumps(config_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    @patch('app.email_service')
    @patch('app.ai_service')
    def test_connect_services(self, mock_ai_service, mock_email_service, client):
        """Test service connection endpoint"""
        mock_email_service.connect.return_value = True
        mock_ai_service.connect.return_value = True
        
        response = client.post('/api/connect')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
    
    @patch('app.email_service')
    def test_list_folders(self, mock_email_service, client):
        """Test folder listing endpoint"""
        mock_folders = [
            {
                'name': 'INBOX', 
                'display_name': 'Inbox', 
                'type': 'inbox',
                'attributes': [],
                'is_hidden': False,
                'is_selectable': True,
                'delimiter': '/'
            },
            {
                'name': 'Sent', 
                'display_name': 'Sent', 
                'type': 'sent',
                'attributes': [],
                'is_hidden': False,
                'is_selectable': True,
                'delimiter': '/'
            }
        ]
        mock_email_service.list_folders.return_value = mock_folders
        
        response = client.get('/api/folders')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert len(data['folders']) == 2
        assert data['folders'][0]['name'] == 'INBOX'
        assert data['folders'][0]['is_selectable'] == True
    
    @patch('app.email_service')
    def test_list_folders_with_hidden(self, mock_email_service, client):
        """Test folder listing endpoint with hidden folders"""
        mock_folders_visible = [
            {
                'name': 'INBOX', 
                'display_name': 'Inbox', 
                'type': 'inbox',
                'attributes': [],
                'is_hidden': False,
                'is_selectable': True,
                'delimiter': '/'
            }
        ]
        mock_folders_all = mock_folders_visible + [
            {
                'name': '[Gmail]/All Mail', 
                'display_name': 'All Mail', 
                'type': 'archive',
                'attributes': ['All'],
                'is_hidden': True,
                'is_selectable': True,
                'delimiter': '/'
            }
        ]
        
        # Mock different responses based on include_hidden parameter
        def mock_list_folders(include_hidden=False):
            return mock_folders_all if include_hidden else mock_folders_visible
        
        mock_email_service.list_folders.side_effect = mock_list_folders
        
        # Test without hidden folders
        response = client.get('/api/folders')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['folders']) == 1
        
        # Test with hidden folders
        response = client.get('/api/folders?include_hidden=true')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['folders']) == 2
    
    @patch('app.email_service')
    def test_get_emails(self, mock_email_service, client):
        """Test email retrieval endpoint"""
        mock_emails = [
            {
                'id': '1',
                'from': 'test@test.com',
                'subject': 'Test Email',
                'date': '2024-01-01T12:00:00Z',
                'preview': 'Test email content'
            }
        ]
        mock_email_service.get_emails.return_value = mock_emails
        
        response = client.get('/api/emails?folder=INBOX&limit=10')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert len(data['emails']) == 1
        assert data['emails'][0]['from'] == 'test@test.com'
    
    @patch('app.ai_service')
    def test_analyze_spam(self, mock_ai_service, client):
        """Test spam analysis endpoint"""
        mock_ai_service.analyze_spam.return_value = {
            'classification': 'Not Spam',
            'confidence': 0.9,
            'reason': 'Legitimate email'
        }
        
        email_data = {
            'from': 'test@test.com',
            'subject': 'Test Email',
            'body': 'Test content'
        }
        
        response = client.post('/api/analyze-spam',
                             data=json.dumps(email_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['classification'] == 'Not Spam'
    
    @patch('app.ai_service')
    def test_analyze_email(self, mock_ai_service, client):
        """Test email analysis endpoint"""
        mock_ai_service.analyze_email.return_value = 'Detailed analysis result'
        
        email_data = {
            'from': 'test@test.com',
            'subject': 'Test Email',
            'body': 'Test content'
        }
        
        response = client.post('/api/analyze-email',
                             data=json.dumps(email_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['analysis'] == 'Detailed analysis result'
    
    @patch('app.ai_service')
    def test_generate_draft(self, mock_ai_service, client):
        """Test draft generation endpoint"""
        mock_ai_service.generate_draft.return_value = 'Generated draft response'
        
        request_data = {
            'analysis': 'Email analysis indicating meeting request'
        }
        
        response = client.post('/api/generate-draft',
                             data=json.dumps(request_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['draft'] == 'Generated draft response'

class TestIntegration:
    """Integration tests for the complete workflow"""
    
    @pytest.fixture
    def mock_services(self):
        """Setup mock services for integration tests"""
        with patch('app.email_service') as mock_email, \
             patch('app.ai_service') as mock_ai:
            
            # Setup email service mocks
            mock_email.connect.return_value = True
            mock_email.list_folders.return_value = [
                {'name': 'INBOX', 'display_name': 'Inbox', 'type': 'inbox'}
            ]
            mock_email.get_emails.return_value = [{
                'id': '1',
                'from': 'spam@spammer.com',
                'subject': 'FREE MONEY NOW!!!',
                'body': 'Click here to get free money!',
                'date': '2024-01-01T12:00:00Z',
                'preview': 'Click here to get free money!'
            }]
            
            # Setup AI service mocks
            mock_ai.connect.return_value = True
            mock_ai.analyze_spam.return_value = {
                'classification': 'Spam/Junk',
                'confidence': 0.95,
                'reason': 'Contains spam indicators: excessive caps, money promises'
            }
            mock_ai.analyze_email.return_value = 'This email appears to be spam with promotional language'
            mock_ai.generate_draft.return_value = 'This email has been identified as spam and moved to junk folder.'
            
            yield mock_email, mock_ai
    
    def test_full_workflow(self, mock_services):
        """Test complete email analysis workflow"""
        mock_email, mock_ai = mock_services
        
        app.config['TESTING'] = True
        with app.test_client() as client:
            # 1. Connect services
            response = client.post('/api/connect')
            assert response.status_code == 200
            
            # 2. Get folders
            response = client.get('/api/folders')
            assert response.status_code == 200
            
            # 3. Get emails
            response = client.get('/api/emails')
            assert response.status_code == 200
            emails = json.loads(response.data)['emails']
            
            # 4. Analyze first email for spam
            email_data = emails[0]
            response = client.post('/api/analyze-spam',
                                 data=json.dumps(email_data),
                                 content_type='application/json')
            assert response.status_code == 200
            spam_result = json.loads(response.data)
            assert spam_result['classification'] == 'Spam/Junk'
            
            # 5. Analyze email content
            response = client.post('/api/analyze-email',
                                 data=json.dumps(email_data),
                                 content_type='application/json')
            assert response.status_code == 200
            analysis = json.loads(response.data)['analysis']
            
            # 6. Generate draft response
            response = client.post('/api/generate-draft',
                                 data=json.dumps({'analysis': analysis}),
                                 content_type='application/json')
            assert response.status_code == 200
            draft = json.loads(response.data)['draft']
            assert 'spam' in draft.lower()

if __name__ == '__main__':
    # Run the tests
    pytest.main([__file__, '-v', '--tb=short'])
