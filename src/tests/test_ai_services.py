"""
Focused tests for AI service components
"""

import pytest
import json
from unittest.mock import Mock, patch
from src.ai.interfaces import IAIService, IPromptLoader
from src.ai.azure_service import AzureAIService
from src.ai.prompt_loader import FilePromptLoader
from src.models.email_models import EmailMessage, SpamAnalysisResult, ConnectionConfig


class TestPromptLoader:
    """Test cases for prompt loader"""
    
    @pytest.fixture
    def loader(self):
        return FilePromptLoader()
    
    @patch('builtins.open', create=True)
    @patch('pathlib.Path.exists')
    def test_load_prompt_success(self, mock_exists, mock_open, loader):
        """Test successful prompt loading"""
        mock_exists.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = "Test prompt template with {placeholder}"
        
        result = loader.load_prompt('test_prompt')
        
        assert result == "Test prompt template with {placeholder}"
        mock_exists.assert_called_once()
        mock_open.assert_called_once()
    
    @patch('pathlib.Path.exists')
    def test_load_prompt_not_found(self, mock_exists, loader):
        """Test loading non-existent prompt"""
        mock_exists.return_value = False
        
        with pytest.raises(FileNotFoundError):
            loader.load_prompt('non_existent_prompt')
    
    @patch('builtins.open', create=True)
    @patch('pathlib.Path.exists')
    def test_load_prompt_with_parameters(self, mock_exists, mock_open, loader):
        """Test loading prompt with parameter substitution"""
        mock_exists.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = "Analyze this email from {sender} with subject {subject}"
        
        result = loader.load_prompt('email_analysis')
        
        assert result == "Analyze this email from {sender} with subject {subject}"


class TestAzureOpenAIServiceDetailed:
    """Detailed tests for Azure OpenAI service"""
    
    @pytest.fixture
    def service(self):
        prompt_loader = Mock(spec=IPromptLoader)
        return AzureAIService(prompt_loader)
    
    def test_analyze_spam_with_confidence_scores(self, service):
        """Test spam analysis with different confidence scores"""
        # Setup
        mock_client = Mock()
        service.client = mock_client
        service.config = ConnectionConfig(
            imap_server='', imap_port=993, imap_username='', imap_password='',
            azure_endpoint='', azure_api_key='', azure_deployment='gpt-4', azure_api_version=''
        )
        service.prompt_loader.load_prompt.return_value = "Spam analysis prompt"
        
        test_cases = [
            ('{"classification": "Spam", "confidence": 0.95, "reason": "Obvious spam"}', 'Spam', 0.95),
            ('{"classification": "Not Spam", "confidence": 0.85, "reason": "Legitimate"}', 'Not Spam', 0.85),
            ('{"classification": "Uncertain", "confidence": 0.5, "reason": "Unclear"}', 'Uncertain', 0.5),
        ]
        
        email = EmailMessage('1', 'test@test.com', 'user@test.com', 'Test', '2024-01-01', 'text/plain', 'Body', 'Body')
        
        for response_content, expected_class, expected_conf in test_cases:
            # Setup mock response
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = response_content
            mock_client.chat.completions.create.return_value = mock_response
            
            # Execute
            result = service.analyze_spam(email)
            
            # Assert
            assert result.classification == expected_class
            assert result.confidence == expected_conf
    
    def test_analyze_spam_invalid_json(self, service):
        """Test spam analysis with invalid JSON response"""
        # Setup
        mock_client = Mock()
        service.client = mock_client
        service.config = ConnectionConfig(
            imap_server='', imap_port=993, imap_username='', imap_password='',
            azure_endpoint='', azure_api_key='', azure_deployment='gpt-4', azure_api_version=''
        )
        service.prompt_loader.load_prompt.return_value = "Spam analysis prompt"
        
        # Mock invalid JSON response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = 'Invalid JSON response'
        mock_client.chat.completions.create.return_value = mock_response
        
        email = EmailMessage('1', 'test@test.com', 'user@test.com', 'Test', '2024-01-01', 'text/plain', 'Body', 'Body')
        
        # Execute
        result = service.analyze_spam(email)
        
        # Assert - Should return fallback parsing result, not raise exception
        assert result.classification in ["Spam/Junk", "Not Spam"]
        assert result.confidence == 0.7
        assert result.reason == 'Invalid JSON response'
    
    def test_analyze_email_detailed(self, service):
        """Test detailed email analysis"""
        # Setup
        mock_client = Mock()
        service.client = mock_client
        service.config = ConnectionConfig(
            imap_server='', imap_port=993, imap_username='', imap_password='',
            azure_endpoint='', azure_api_key='', azure_deployment='gpt-4', azure_api_version=''
        )
        service.prompt_loader.load_prompt.return_value = "Email analysis prompt"
        
        # Mock API response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = 'Detailed analysis of the email content'
        mock_client.chat.completions.create.return_value = mock_response
        
        email = EmailMessage(
            id='1',
            from_address='business@company.com',
            to_address='user@test.com',
            subject='Meeting Request',
            date='2024-01-01T12:00:00Z',
            content_type='text/plain',
            body='Would you like to schedule a meeting next week?',
            preview='Would you like to schedule a meeting next week?'
        )
        
        # Execute
        result = service.analyze_email(email)
        
        # Assert
        assert result == 'Detailed analysis of the email content'
        service.prompt_loader.load_prompt.assert_called_with('email-analyze')
    
    def test_generate_draft_response(self, service):
        """Test draft response generation"""
        # Setup
        mock_client = Mock()
        service.client = mock_client
        service.config = ConnectionConfig(
            imap_server='', imap_port=993, imap_username='', imap_password='',
            azure_endpoint='', azure_api_key='', azure_deployment='gpt-4', azure_api_version=''
        )
        service.prompt_loader.load_prompt.return_value = "Draft generation prompt"
        
        # Mock API response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = 'Thank you for your email. I will review and get back to you.'
        mock_client.chat.completions.create.return_value = mock_response
        
        analysis_result = "This email is requesting a meeting and appears to be from a legitimate business contact."
        
        # Execute
        result = service.generate_draft(analysis_result)
        
        # Assert
        assert result == 'Thank you for your email. I will review and get back to you.'
        service.prompt_loader.load_prompt.assert_called_with('email-draft')
    
    def test_api_error_handling(self, service):
        """Test API error handling"""
        # Setup
        mock_client = Mock()
        service.client = mock_client
        service.config = ConnectionConfig(
            imap_server='', imap_port=993, imap_username='', imap_password='',
            azure_endpoint='', azure_api_key='', azure_deployment='gpt-4', azure_api_version=''
        )
        service.prompt_loader.load_prompt.return_value = "Test prompt"
        
        # Mock API error
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        email = EmailMessage('1', 'test@test.com', 'user@test.com', 'Test', '2024-01-01', 'text/plain', 'Body', 'Body')
        
        # Execute
        result = service.analyze_spam(email)
        
        # Assert - Should return error result, not raise exception
        assert result.classification == "Error"
        assert result.confidence == 0.0
        assert "API Error" in result.reason
    
    def test_connect_with_different_configs(self, service):
        """Test connection with different configuration scenarios"""
        with patch('src.ai.azure_service.AzureOpenAI') as mock_azure:
            mock_client = Mock()
            mock_azure.return_value = mock_client
            
            # Test minimal config
            minimal_config = ConnectionConfig(
                imap_server='imap.test.com', imap_port=993, 
                imap_username='test@test.com', imap_password='password',
                azure_endpoint='https://test.openai.azure.com/',
                azure_api_key='test-key',
                azure_deployment='gpt-4',
                azure_api_version='2024-02-01'
            )
            
            result = service.connect(minimal_config)
            assert result is True
            
            # Test complete config
            complete_config = ConnectionConfig(
                imap_server='imap.test.com', imap_port=993,
                imap_username='test@test.com', imap_password='password',
                azure_endpoint='https://test.openai.azure.com/',
                azure_api_key='test-key',
                azure_deployment='gpt-4',
                azure_api_version='2024-02-01'
            )
            
            result = service.connect(complete_config)
            assert result is True
    
    def test_is_connected(self, service):
        """Test connection status checking"""
        # Initially not connected
        assert service.is_connected() is False
        
        # Mock connection
        service.client = Mock()
        service.config = ConnectionConfig(
            imap_server='', imap_port=993, imap_username='', imap_password='',
            azure_endpoint='', azure_api_key='', azure_deployment='gpt-4', azure_api_version=''
        )
        assert service.is_connected() is True
        
        # Disconnect
        service.client = None
        assert service.is_connected() is False


class TestSpamAnalysisScenarios:
    """Test various spam analysis scenarios"""
    
    @pytest.fixture
    def service(self):
        prompt_loader = Mock(spec=IPromptLoader)
        service = AzureAIService(prompt_loader)
        service.client = Mock()
        service.config = ConnectionConfig(
            imap_server='', imap_port=993, imap_username='', imap_password='',
            azure_endpoint='', azure_api_key='', azure_deployment='gpt-4', azure_api_version=''
        )
        service.prompt_loader.load_prompt.return_value = "Spam analysis prompt"
        return service
    
    def test_obvious_spam_detection(self, service):
        """Test detection of obvious spam emails"""
        # Setup obvious spam email
        spam_email = EmailMessage(
            id='1',
            from_address='noreply@suspicious.com',
            to_address='user@test.com',
            subject='FREE MONEY!!! CLICK NOW!!!',
            date='2024-01-01T12:00:00Z',
            content_type='text/plain',
            body='Congratulations! You have won $1,000,000!!! Click here immediately!',
            preview='Congratulations! You have won $1,000,000!!!'
        )
        
        # Mock high confidence spam response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "classification": "Spam",
            "confidence": 0.98,
            "reason": "Contains excessive capitalization, money promises, and urgency tactics typical of spam"
        })
        service.client.chat.completions.create.return_value = mock_response
        
        # Execute
        result = service.analyze_spam(spam_email)
        
        # Assert
        assert result.classification == "Spam"
        assert result.confidence >= 0.9
        assert "spam" in result.reason.lower()
    
    def test_legitimate_email_detection(self, service):
        """Test detection of legitimate emails"""
        # Setup legitimate email
        legit_email = EmailMessage(
            id='1',
            from_address='colleague@mycompany.com',
            to_address='user@test.com',
            subject='Quarterly Report Review',
            date='2024-01-01T12:00:00Z',
            content_type='text/plain',
            body='Hi, could you please review the quarterly report I sent earlier? Let me know if you have any questions.',
            preview='Hi, could you please review the quarterly report'
        )
        
        # Mock legitimate email response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "classification": "Not Spam",
            "confidence": 0.92,
            "reason": "Professional tone, legitimate business request from known domain"
        })
        service.client.chat.completions.create.return_value = mock_response
        
        # Execute
        result = service.analyze_spam(legit_email)
        
        # Assert
        assert result.classification == "Not Spam"
        assert result.confidence >= 0.8
        assert "legitimate" in result.reason.lower() or "professional" in result.reason.lower()
    
    def test_phishing_email_detection(self, service):
        """Test detection of phishing emails"""
        # Setup phishing email
        phishing_email = EmailMessage(
            id='1',
            from_address='security@bank-alert.com',
            to_address='user@test.com',
            subject='Urgent: Verify Your Account Immediately',
            date='2024-01-01T12:00:00Z',
            content_type='text/plain',
            body='Your account will be suspended unless you verify your credentials immediately. Click here: http://fake-bank.com/verify',
            preview='Your account will be suspended unless you verify'
        )
        
        # Mock phishing detection response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "classification": "Phishing",
            "confidence": 0.96,
            "reason": "Suspicious domain, urgent language, credential harvesting attempt"
        })
        service.client.chat.completions.create.return_value = mock_response
        
        # Execute
        result = service.analyze_spam(phishing_email)
        
        # Assert
        assert result.classification == "Phishing"
        assert result.confidence >= 0.9
        assert "phishing" in result.reason.lower() or "suspicious" in result.reason.lower()


class TestEmailAnalysisScenarios:
    """Test various email analysis scenarios"""
    
    @pytest.fixture
    def service(self):
        prompt_loader = Mock(spec=IPromptLoader)
        service = AzureAIService(prompt_loader)
        service.client = Mock()
        service.config = ConnectionConfig(
            imap_server='', imap_port=993, imap_username='', imap_password='',
            azure_endpoint='', azure_api_key='', azure_deployment='gpt-4', azure_api_version=''
        )
        return service
    
    def test_meeting_request_analysis(self, service):
        """Test analysis of meeting request emails"""
        # Setup meeting request email
        meeting_email = EmailMessage(
            id='1',
            from_address='manager@company.com',
            to_address='user@test.com',
            subject='Team Meeting Next Week',
            date='2024-01-01T12:00:00Z',
            content_type='text/plain',
            body='Hi, I would like to schedule a team meeting for next Tuesday at 2 PM. Please let me know if this works for you.',
            preview='Hi, I would like to schedule a team meeting'
        )
        
        service.prompt_loader.load_prompt.return_value = "Analyze this email"
        
        # Mock analysis response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = 'This email is a meeting request from a manager asking for availability for a team meeting next Tuesday at 2 PM. The tone is professional and requires a response regarding availability.'
        service.client.chat.completions.create.return_value = mock_response
        
        # Execute
        result = service.analyze_email(meeting_email)
        
        # Assert
        assert 'meeting request' in result.lower()
        assert 'Tuesday' in result
        assert '2 PM' in result
    
    def test_urgent_request_analysis(self, service):
        """Test analysis of urgent emails"""
        # Setup urgent email
        urgent_email = EmailMessage(
            id='1',
            from_address='client@urgent.com',
            to_address='user@test.com',
            subject='URGENT: Server Issue Needs Immediate Attention',
            date='2024-01-01T12:00:00Z',
            content_type='text/plain',
            body='Our production server is down and we need immediate assistance. This is affecting all our customers. Please respond ASAP.',
            preview='Our production server is down and we need immediate assistance'
        )
        
        service.prompt_loader.load_prompt.return_value = "Analyze this email"
        
        # Mock analysis response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = 'This email reports an urgent production server outage affecting customers. The sender requires immediate technical assistance and expects a rapid response.'
        service.client.chat.completions.create.return_value = mock_response
        
        # Execute
        result = service.analyze_email(urgent_email)
        
        # Assert
        assert 'urgent' in result.lower()
        assert 'server' in result.lower()
        assert 'immediate' in result.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
