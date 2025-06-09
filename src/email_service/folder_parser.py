"""
IMAP folder parser implementation
Handles parsing of IMAP LIST responses following Single Responsibility Principle
"""

import re
from typing import Dict, List, Any
from src.email_service.interfaces import IFolderParser
from src.models.email_models import EmailFolder
from src.email_service.utils import EmailFolderUtils


class IMAPFolderParser(IFolderParser):
    """Concrete implementation for parsing IMAP folder responses"""
    
    def parse_folder_info(self, folder_info) -> EmailFolder:
        """
        Parse folder name and attributes from IMAP LIST response
        
        Args:
            folder_info: Raw IMAP LIST response string or bytes
            
        Returns:
            EmailFolder object containing parsed folder information
        """
        try:
            # Convert bytes to string if necessary
            if isinstance(folder_info, bytes):
                folder_info = folder_info.decode('utf-8')
            
            # Parse IMAP LIST response format:
            # (attributes) "delimiter" "folder_name" or (attributes) "delimiter" folder_name
            
            # Pattern 1: Standard format with quoted delimiter and folder name
            pattern1 = r'\(([^)]*)\) "([^"]*)" "([^"]*)"'
            match = re.match(pattern1, folder_info)
            
            if not match:
                # Pattern 2: Folder name without quotes
                pattern2 = r'\(([^)]*)\) "([^"]*)" (.+)'
                match = re.match(pattern2, folder_info)
            
            if not match:
                # Pattern 3: NIL delimiter
                pattern3 = r'\(([^)]*)\) NIL "([^"]*)"'
                match = re.match(pattern3, folder_info)
                if match:
                    attributes_str = match.group(1)
                    folder_name = match.group(2)
                    delimiter = '/'
                else:
                    # Fallback: extract quoted strings
                    quoted_parts = re.findall(r'"([^"]*)"', folder_info)
                    if quoted_parts:
                        folder_name = quoted_parts[-1]
                        display_name = EmailFolderUtils.create_display_name(folder_name)
                        folder_type = EmailFolderUtils.get_folder_type(folder_name)
                        return EmailFolder(
                            name=folder_name,
                            display_name=display_name,
                            type=folder_type,
                            attributes=[],
                            is_hidden=False,
                            is_selectable=True,
                            delimiter='/'
                        )
                    return None
            else:
                attributes_str = match.group(1)
                delimiter = match.group(2).strip('"') if match.group(2) else '/'
                folder_name = match.group(3).strip('"') if match.group(3) else ''
            
            # Parse attributes
            attributes = self._parse_attributes(attributes_str)
            
            # Determine folder properties
            is_hidden = self.is_folder_hidden(folder_name, attributes)
            is_selectable = 'Noselect' not in attributes
            
            # Create display name and determine folder type
            display_name = EmailFolderUtils.create_display_name(folder_name)
            folder_type = EmailFolderUtils.get_folder_type(folder_name)
            
            return EmailFolder(
                name=folder_name,
                display_name=display_name,
                type=folder_type,
                attributes=attributes,
                is_hidden=is_hidden,
                is_selectable=is_selectable,
                delimiter=delimiter if delimiter != 'NIL' else '/'
            )
            
        except Exception as e:
            print(f"Failed to parse folder info: {folder_info}, error: {e}")
            return None
    
    def _parse_attributes(self, attributes_str: str) -> List[str]:
        """Parse IMAP attributes from string"""
        attributes = []
        if attributes_str.strip():
            # Split by spaces but handle escaped backslashes
            attr_parts = attributes_str.split()
            for attr in attr_parts:
                # Remove leading backslash and any extra escaping
                clean_attr = attr.strip('\\').strip()
                if clean_attr:
                    attributes.append(clean_attr)
        return attributes
    
    def is_folder_hidden(self, folder_name: str, attributes: List[str]) -> bool:
        """
        Determine if a folder should be considered hidden
        
        Args:
            folder_name: Name of the folder
            attributes: List of IMAP attributes
            
        Returns:
            bool: True if folder should be hidden
        """
        # Check for explicit hidden attributes
        hidden_attributes = {'Hidden', 'Noselect', 'All', 'Archive', 'Important'}
        if any(attr in hidden_attributes for attr in attributes):
            return True
        
        # Check for server-specific hidden patterns
        folder_lower = folder_name.lower()
        
        # Gmail patterns
        gmail_hidden = [
            '[gmail]', 'gmail/', 'all mail', 'important', 'starred',
            'chats', 'spam', 'trash'
        ]
        if any(pattern in folder_lower for pattern in gmail_hidden):
            return True
        
        # Outlook/Exchange patterns  
        outlook_hidden = [
            'calendar', 'contacts', 'tasks', 'notes', 'journal',
            'sync issues', 'conversation history', 'quick step settings',
            'suggested contacts', 'recipient cache'
        ]
        if any(pattern in folder_lower for pattern in outlook_hidden):
            return True
        
        # Generic patterns
        generic_hidden = [
            'noselect', 'archive', 'all_mail', 'flagged'
        ]
        if any(pattern in folder_lower for pattern in generic_hidden):
            return True
            
        return False
