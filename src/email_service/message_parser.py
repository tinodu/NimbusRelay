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
        
        # Extract email bodies
        text_body, html_body = self._extract_bodies(msg)
        # For backward compatibility, set body to text if available, else html
        body = text_body if text_body else html_body

        # Create preview text (first 150 characters)
        preview = ""
        if text_body:
            preview_text = text_body.replace('\n', ' ').replace('\r', ' ').strip()
            preview = preview_text[:150] + "..." if len(preview_text) > 150 else preview_text
        elif html_body:
            # Strip HTML tags for preview
            import re
            preview_text = re.sub('<[^<]+?>', '', html_body).replace('\n', ' ').replace('\r', ' ').strip()
            preview = preview_text[:150] + "..." if len(preview_text) > 150 else preview_text

        return EmailMessage(
            id="",  # Will be set by caller
            from_address=from_address or "",
            to_address=to_address or "",
            subject=subject,
            date=date or "",
            content_type=content_type or "",
            body=body,
            preview=preview,
            text_body=text_body,
            html_body=html_body
        )

    def _extract_bodies(self, msg) -> (Optional[str], Optional[str]):
        """Extract both text and HTML bodies from message"""
        text_body = None
        html_body = None

        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                charset = part.get_content_charset() or "utf-8"
                try:
                    payload = part.get_payload(decode=True)
                    if payload is None:
                        continue
                    decoded = payload.decode(charset, errors="replace")
                except Exception:
                    continue
                if ctype == "text/plain" and text_body is None:
                    text_body = decoded
                elif ctype == "text/html" and html_body is None:
                    html_body = decoded
        else:
            ctype = msg.get_content_type()
            charset = msg.get_content_charset() or "utf-8"
            try:
                payload = msg.get_payload(decode=True)
                decoded = payload.decode(charset, errors="replace") if payload else None
            except Exception:
                decoded = None
            if ctype == "text/plain":
                text_body = decoded
            elif ctype == "text/html":
                html_body = decoded

        return text_body, html_body
    
    def _decode_mime_header(self, header_value) -> Optional[str]:
        """Decode MIME encoded headers"""
        if header_value is None:
            return None
        try:
            return str(make_header(decode_header(header_value)))
        except Exception:
            return header_value
