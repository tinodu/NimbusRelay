#!/usr/bin/env python3

import re

def test_folder_parsing(folder_info: str):
    print(f"Testing: {repr(folder_info)}")
    
    # Try format: (attributes) "delimiter" "folder_name"
    pattern = r'\(([^)]*)\) "([^"]*)" "([^"]*)"'
    match = re.match(pattern, folder_info)
    print(f"Pattern 1: {pattern}")
    print(f"Match 1: {match}")
    
    if not match:
        # Try format: (attributes) "delimiter" folder_name (without quotes around folder)
        pattern = r'\(([^)]*)\) "([^"]*)" (.+)'
        match = re.match(pattern, folder_info)
        print(f"Pattern 2: {pattern}")
        print(f"Match 2: {match}")
        if match:
            print(f"Groups: {match.groups()}")
    
    if not match:
        # Try format: (attributes) delimiter folder_name (no quotes around delimiter)
        pattern = r'\(([^)]*)\) ([^ ]+) (.+)'
        match = re.match(pattern, folder_info)
        print(f"Pattern 3: {pattern}")
        print(f"Match 3: {match}")
        if match:
            print(f"Groups: {match.groups()}")
    
    if not match:
        # Try format with NIL delimiter: (attributes) NIL folder_name
        pattern = r'\(([^)]*)\) NIL (.+)'
        match = re.match(pattern, folder_info)
        print(f"Pattern 4: {pattern}")
        print(f"Match 4: {match}")
        if match:
            print(f"Groups: {match.groups()}")
    
    print("-" * 50)

# Test cases from the actual server output
test_cases = [
    '(\\HasChildren) "." INBOX',
    '(\\HasNoChildren \\Archive) "." INBOX.Archive',
    '(\\HasNoChildren \\Sent) "." INBOX.Sent',
    '(\\HasNoChildren \\Drafts) "." INBOX.Drafts'
]

for test_case in test_cases:
    test_folder_parsing(test_case)
