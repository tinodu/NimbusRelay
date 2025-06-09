"""
Email utility functions
Helper functions for email operations following Single Responsibility Principle
"""

from typing import Dict


class EmailFolderUtils:
    """Utility class for email folder operations"""
    
    @staticmethod
    def create_display_name(folder_name: str) -> str:
        """
        Create a human-readable display name from folder name
        
        Args:
            folder_name: Raw folder name
            
        Returns:
            str: Human-readable display name
        """
        try:
            # Handle hierarchical folder names (e.g., "INBOX.Sent" -> "Sent")
            if '.' in folder_name:
                display_name = folder_name.split('.')[-1]
            elif '/' in folder_name:
                display_name = folder_name.split('/')[-1]
            else:
                display_name = folder_name
            
            # Clean up and format
            display_name = display_name.replace('_', ' ').replace('-', ' ')
            
            # Special cases for common folder names
            display_name_lower = display_name.lower()
            if display_name_lower == 'inbox':
                return 'Inbox'
            elif display_name_lower in ['sent', 'sent items', 'sent messages']:
                return 'Sent'
            elif display_name_lower in ['drafts', 'draft']:
                return 'Drafts'
            elif display_name_lower in ['spam', 'junk', 'junk e-mail', 'junk email']:
                return 'Spam'
            elif display_name_lower in ['trash', 'deleted', 'deleted items', 'deleted messages']:
                return 'Trash'
            else:
                return display_name.title()
                
        except Exception as e:
            print(f"Error creating display name for '{folder_name}': {e}")
            return folder_name
    
    @staticmethod
    def get_folder_type(folder_name: str) -> str:
        """
        Determine folder type based on name
        
        Args:
            folder_name: Folder name to analyze
            
        Returns:
            str: Folder type
        """
        folder_lower = folder_name.lower()
        # Check more specific patterns first
        if 'spam' in folder_lower or 'junk' in folder_lower:
            return 'spam'
        elif 'sent' in folder_lower:
            return 'sent'
        elif 'draft' in folder_lower:
            return 'drafts'
        elif 'trash' in folder_lower or 'deleted' in folder_lower:
            return 'trash'
        elif folder_lower == 'inbox' or folder_lower.endswith('inbox'):
            return 'inbox'
        elif 'inbox' in folder_lower:
            # For subfolders of INBOX, return custom unless already matched above
            return 'custom'
        else:
            return 'custom'
    
    @staticmethod
    def sort_folders(folders: list) -> list:
        """
        Sort folders by importance and name
        
        Args:
            folders: List of EmailFolder objects
            
        Returns:
            list: Sorted list of folders
        """
        return sorted(folders, key=lambda x: (
            x.type != 'inbox',  # Inbox first
            x.type not in ['sent', 'drafts', 'trash'],  # Important folders next
            x.display_name.lower()  # Then alphabetical
        ))
