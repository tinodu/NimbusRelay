"""
Focused tests for email service components
"""

import pytest
from unittest.mock import Mock, patch
from src.email_service.interfaces import IEmailService, IFolderParser, IEmailParser
from src.email_service.imap_service import IMAPEmailService
from src.email_service.folder_parser import IMAPFolderParser
from src.email_service.message_parser import EmailMessageParser
from src.email_service.utils import EmailFolderUtils
from src.models.email_models import EmailFolder, EmailMessage, ConnectionConfig


class TestIMAPFolderParserDetailed:
    """Detailed tests for IMAP folder parser"""
    
    @pytest.fixture
    def parser(self):
        return IMAPFolderParser()
    
    def test_parse_outlook_folders(self, parser):
        """Test parsing Outlook-style folders"""
        test_cases = [
            (b'(\\HasNoChildren) "/" "INBOX"', "INBOX", "inbox"),
            (b'(\\HasNoChildren) "/" "Sent Items"', "Sent Items", "sent"),
            (b'(\\HasNoChildren) "/" "Deleted Items"', "Deleted Items", "trash"),
            (b'(\\HasNoChildren) "/" "Junk Email"', "Junk Email", "spam"),
        ]
        
        for folder_info, expected_name, expected_type in test_cases:
            result = parser.parse_folder_info(folder_info.decode('utf-8'))
            assert result['name'] == expected_name
            assert EmailFolderUtils.get_folder_type(expected_name) == expected_type
    
    def test_parse_gmail_folders(self, parser):
        """Test parsing Gmail-style folders"""
        test_cases = [
            (b'(\\HasNoChildren) "/" "INBOX"', "INBOX", "inbox"),
            (b'(\\HasNoChildren \\Sent) "/" "[Gmail]/Sent Mail"', "[Gmail]/Sent Mail", "sent"),
            (b'(\\HasNoChildren \\Drafts) "/" "[Gmail]/Drafts"', "[Gmail]/Drafts", "drafts"),
            (b'(\\HasNoChildren \\Trash) "/" "[Gmail]/Trash"', "[Gmail]/Trash", "trash"),
            (b'(\\HasNoChildren \\All) "/" "[Gmail]/All Mail"', "[Gmail]/All Mail", "archive"),
        ]
        
        for folder_info, expected_name, expected_type in test_cases:
            result = parser.parse_folder_info(folder_info.decode('utf-8'))
            assert result['name'] == expected_name
            assert EmailFolderUtils.get_folder_type(expected_name) == expected_type
    
    def test_parse_complex_folder_names(self, parser):
        """Test parsing folders with complex names"""
        test_cases = [
            b'(\\HasNoChildren) "/" "Projects/2024/Q1"',
            b'(\\HasNoChildren) "." "INBOX.Work.Important"',
            b'(\\HasNoChildren) "/" "Newsletters & Updates"',
        ]
        
        for folder_info in test_cases:
            result = parser.parse_folder(folder_info)
            assert result is not None
            assert result.name is not None
            assert result.display_name is not None
    
    def test_parse_folder_attributes(self, parser):
        """Test parsing folder attributes correctly"""
        folder_info = b'(\\HasChildren \\Noselect \\Subscribed) "/" "Gmail"'
        result = parser.parse_folder(folder_info)
        
        assert "HasChildren" in result.attributes
        assert "Noselect" in result.attributes
        assert "Subscribed" in result.attributes
        assert result.is_selectable is False


class TestEmailMessageParserDetailed:
    """Detailed tests for email message parser"""
    
    @pytest.fixture
    def parser(self):
        return EmailMessageParser()
    
    def test_parse_multipart_email(self, parser):
        """Test parsing multipart email with both text and HTML"""
        raw_email = b"""From: sender@test.com
To: recipient@test.com
Subject: Multipart Test
Date: Mon, 01 Jan 2024 12:00:00 +0000
Content-Type: multipart/alternative; boundary="boundary123"

--boundary123
Content-Type: text/plain; charset=utf-8

This is the plain text version.

--boundary123
Content-Type: text/html; charset=utf-8

<html><body><p>This is the <b>HTML</b> version.</p></body></html>

--boundary123--
"""
        
        result = parser.parse_email(raw_email)
        
        assert result.from_address == 'sender@test.com'
        assert result.subject == 'Multipart Test'
        # Should prefer HTML content and convert to text
        assert 'HTML' in result.body
        assert 'plain text' in result.body or 'HTML' in result.body
    
    def test_parse_email_with_attachments(self, parser):
        """Test parsing email with attachments"""
        raw_email = b"""From: sender@test.com
To: recipient@test.com
Subject: Email with attachment
Date: Mon, 01 Jan 2024 12:00:00 +0000
Content-Type: multipart/mixed; boundary="boundary456"

--boundary456
Content-Type: text/plain; charset=utf-8

Please find the attachment.

--boundary456
Content-Type: application/pdf; name="document.pdf"
Content-Disposition: attachment; filename="document.pdf"

[Binary PDF content would be here]

--boundary456--
"""
        
        result = parser.parse_email(raw_email)
        
        assert result.from_address == 'sender@test.com'
        assert result.subject == 'Email with attachment'
        assert 'Please find the attachment' in result.body
    
    def test_parse_email_encoding(self, parser):
        """Test parsing email with different encodings"""
        raw_email = b"""From: =?UTF-8?B?VGVzdCBTZW5kZXI=?= <test@example.com>
To: recipient@test.com
Subject: =?UTF-8?Q?Test_Subject_with_=C3=A9?=
Date: Mon, 01 Jan 2024 12:00:00 +0000
Content-Type: text/plain; charset=utf-8

Test content with special characters
"""
        
        result = parser.parse_email(raw_email)
        
        assert 'Test Sender' in result.from_address
        assert 'Test Subject with é' in result.subject
        assert 'special characters' in result.body
    
    def test_parse_email_missing_fields(self, parser):
        """Test parsing email with missing fields"""
        raw_email = b"""Subject: Only Subject
Date: Mon, 01 Jan 2024 12:00:00 +0000

Minimal email content.
"""
        
        result = parser.parse_email(raw_email)
        
        assert result.subject == 'Only Subject'
        assert result.from_address == ''
        assert result.to_address == ''
        assert 'Minimal email content' in result.body


class TestEmailFolderUtilsDetailed:
    """Detailed tests for email folder utilities"""
    
    def test_folder_type_edge_cases(self):
        """Test folder type classification edge cases"""
        test_cases = [
            ('INBOX.Sent Messages', 'sent'),
            ('INBOX.Sent Items', 'sent'),
            ('Outbox', 'sent'),
            ('Draft', 'drafts'),
            ('Draft Messages', 'drafts'),
            ('Deleted Messages', 'trash'),
            ('Recycle Bin', 'trash'),
            ('Junk', 'spam'),
            ('Junk E-mail', 'spam'),
            ('Bulk Mail', 'spam'),
        ]
        
        for folder_name, expected_type in test_cases:
            result = EmailFolderUtils.get_folder_type(folder_name)
            assert result == expected_type, f"Failed for {folder_name}, expected {expected_type}, got {result}"
    
    def test_display_name_normalization(self):
        """Test display name normalization"""
        test_cases = [
            ('INBOX', 'Inbox'),
            ('INBOX.Sent', 'Sent'),
            ('[Gmail]/All Mail', 'All Mail'),
            ('Work/Projects/2024', '2024'),
            ('Newsletters & Updates', 'Newsletters & Updates'),
            ('INBOX.Important', 'Important'),
        ]
        
        for folder_name, expected_display in test_cases:
            result = EmailFolderUtils.get_display_name(folder_name)
            assert result == expected_display
    
    def test_folder_sorting(self):
        """Test folder sorting logic"""
        folders = [
            EmailFolder('INBOX', 'Inbox', 'inbox', [], False, True, '/'),
            EmailFolder('Custom', 'Custom', 'custom', [], False, True, '/'),
            EmailFolder('Sent', 'Sent', 'sent', [], False, True, '/'),
            EmailFolder('Drafts', 'Drafts', 'drafts', [], False, True, '/'),
            EmailFolder('Trash', 'Trash', 'trash', [], False, True, '/'),
        ]
        
        sorted_folders = EmailFolderUtils.sort_folders(folders)
        
        # Check that inbox comes first, then standard folders, then custom
        folder_types = [f.type for f in sorted_folders]
        assert folder_types[0] == 'inbox'
        assert 'sent' in folder_types[:4]  # Standard folders should come early
        assert folder_types[-1] == 'custom'  # Custom folders should come last


class TestIMAPEmailServiceDetailed:
    """Detailed tests for IMAP email service"""
    
    @pytest.fixture
    def service(self):
        folder_parser = Mock(spec=IFolderParser)
        message_parser = Mock(spec=IEmailParser)
        return IMAPEmailService(folder_parser, message_parser)
    
    @patch('imaplib.IMAP4_SSL')
    def test_search_emails(self, mock_imap, service):
        """Test email search functionality"""
        # Setup
        mock_connection = Mock()
        mock_imap.return_value = mock_connection
        service._connection = mock_connection
        
        mock_connection.select.return_value = ('OK', [b'10'])
        mock_connection.search.return_value = ('OK', [b'1 2 3'])
        mock_connection.fetch.return_value = ('OK', [
            (b'1 (RFC822 {500}', b'email content 1'),
            (b'2 (RFC822 {500}', b'email content 2'),
            (b'3 (RFC822 {500}', b'email content 3'),
        ])
        
        # Mock message parser
        mock_emails = [
            EmailMessage('1', 'test1@test.com', 'user@test.com', 'Subject 1', 'Body 1', 'Body 1', '2024-01-01', []),
            EmailMessage('2', 'test2@test.com', 'user@test.com', 'Subject 2', 'Body 2', 'Body 2', '2024-01-02', []),
            EmailMessage('3', 'test3@test.com', 'user@test.com', 'Subject 3', 'Body 3', 'Body 3', '2024-01-03', []),
        ]
        service._message_parser.parse_email.side_effect = mock_emails
        
        # Execute
        emails = service.get_emails('INBOX', limit=10)
        
        # Assert
        assert len(emails) == 3
        assert emails[0].id == '1'
        mock_connection.select.assert_called_once_with('INBOX')
        mock_connection.search.assert_called_once()
    
    def test_disconnect(self, service):
        """Test disconnection functionality"""
        # Setup
        mock_connection = Mock()
        service._connection = mock_connection
        
        # Execute
        service.disconnect()
        
        # Assert
        mock_connection.close.assert_called_once()
        mock_connection.logout.assert_called_once()
        assert service._connection is None
    
    def test_get_emails_no_connection(self, service):
        """Test get_emails when not connected"""
        # Execute & Assert
        with pytest.raises(Exception):
            service.get_emails('INBOX')
    
    def test_list_folders_with_hidden(self, service):
        """Test listing folders with hidden folder filtering"""
        # Setup mock connection
        mock_connection = Mock()
        service._connection = mock_connection
        
        mock_connection.list.return_value = ('OK', [
            b'(\\HasNoChildren) "." "INBOX"',
            b'(\\HasNoChildren \\All) "." "[Gmail]/All Mail"',
        ])
        
        # Setup mock folder parser
        mock_folders = [
            EmailFolder('INBOX', 'Inbox', 'inbox', ['HasNoChildren'], False, True, '.'),
            EmailFolder('[Gmail]/All Mail', 'All Mail', 'archive', ['HasNoChildren', 'All'], True, True, '.'),
        ]
        service._folder_parser.parse_folder.side_effect = mock_folders
        
        # Execute - without hidden folders
        folders = service.list_folders(include_hidden=False)
        assert len(folders) == 1
        assert folders[0].name == 'INBOX'
        
        # Execute - with hidden folders
        folders = service.list_folders(include_hidden=True)
        assert len(folders) == 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
