#!/usr/bin/env python3

import sys
sys.path.append('.')

from app import EmailService

def test_folder_parsing():
    service = EmailService()
    
    # Test cases from the actual server output
    test_cases = [
        '(\\HasChildren) "." INBOX',
        '(\\HasNoChildren \\Archive) "." INBOX.Archive',
        '(\\HasNoChildren \\Sent) "." INBOX.Sent',
        '(\\HasNoChildren \\Drafts) "." INBOX.Drafts'
    ]
    
    print("Testing EmailService._parse_folder_name_and_attributes:")
    print("=" * 60)
    
    for test_case in test_cases:
        print(f"\nInput: {test_case}")
        result = service._parse_folder_name_and_attributes(test_case)
        
        if result:
            print(f"✓ Name: {result['name']}")
            print(f"  Attributes: {result['attributes']}")
            print(f"  Delimiter: {result['delimiter']}")
            print(f"  Hidden: {result['is_hidden']}")
            print(f"  Selectable: {result['is_selectable']}")
        else:
            print("✗ Failed to parse")

if __name__ == "__main__":
    test_folder_parsing()
