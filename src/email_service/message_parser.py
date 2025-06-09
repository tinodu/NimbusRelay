"""
Email message parser implementation
Handles parsing of raw email messages following Single Responsibility Principle
"""

import email
from email.header import decode_header, make_header
from typing import Optional
from src.email_service.interfaces import IEmailParser
from src.models.email_models import EmailMessage


class EmailMessageParser(IEmailParser):
    """Concrete implementation for parsing email messages"""
    
    def parse_email(self, raw_email_bytes: bytes) -> EmailMessage:
        """
        Parse raw email bytes into structured EmailMessage
        
        Args:
            raw_email_bytes: Raw email data
            
        Returns:
            EmailMessage: Parsed email message
        """
        msg = email.message_from_bytes(raw_email_bytes)
        
        from_address = self._decode_mime_header(msg.get("From"))
        to_address = self._decode_mime_header(msg.get("To"))
        subject = self._decode_mime_header(msg.get("Subject"))
        date = self._decode_mime_header(msg.get("Date"))
        content_type = self._decode_mime_header(msg.get("Content-Type"))
        
        # Handle empty subject
        if not subject or subject.strip() == "":
            subject = "(no subject)"
        
        # Extract email body
        body = self._extract_body(msg)
        
        # Create preview text (first 150 characters)
        preview = ""
        if body:
            preview_text = body.replace('\n', ' ').replace('\r', ' ').strip()
            preview = preview_text[:150] + "..." if len(preview_text) > 150 else preview_text
        
        return EmailMessage(
            id="",  # Will be set by caller
            from_address=from_address or "",
            to_address=to_address or "",
            subject=subject,
            date=date or "",
            content_type=content_type or "",
            body=body,
            preview=preview
        )
    
    def _extract_body(self, msg) -> Optional[str]:
        """Extract email body from message"""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    charset = part.get_content_charset() or "utf-8"
                    return part.get_payload(decode=True).decode(charset, errors="replace")
                elif part.get_content_type() == "text/html":
                    charset = part.get_content_charset() or "utf-8"
                    return part.get_payload(decode=True).decode(charset, errors="replace")
        else:
            charset = msg.get_content_charset() or "utf-8"
            return msg.get_payload(decode=True).decode(charset, errors="replace")
        
        return None
    
    def _decode_mime_header(self, header_value) -> Optional[str]:
        """Decode MIME encoded headers"""
        if header_value is None:
            return None
        try:
            return str(make_header(decode_header(header_value)))
        except Exception:
            return header_value
