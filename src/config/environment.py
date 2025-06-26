"""
Environment configuration utility
Handles saving and loading environment variables
"""

import os
from pathlib import Path
from typing import Dict


class EnvironmentManager:
    """Manages environment variables and .env file operations"""
    
    def __init__(self, env_file_path: str = '.env'):
        self.env_file_path = Path(env_file_path)
    
    def save_env_var(self, key: str, value: str) -> bool:
        """
        Save environment variable to .env file
        
        Args:
            key: Environment variable key
            value: Environment variable value
            
        Returns:
            bool: Success status
        """
        try:
            # Read existing content
            existing_content = {}
            if self.env_file_path.exists():
                with open(self.env_file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if '=' in line and not line.startswith('#'):
                            k, v = line.split('=', 1)
                            existing_content[k] = v
            
            # Update with new value
            existing_content[key] = value
            
            # Write back to file
            with open(self.env_file_path, 'w', encoding='utf-8') as f:
                for k, v in existing_content.items():
                    f.write(f"{k}={v}\n")
            
            # Update current environment
            os.environ[key] = value
            return True
            
        except Exception as e:
            print(f"Failed to save environment variable: {e}")
            return False
    
    def get_env_var(self, key: str, default: str = '') -> str:
        """
        Get environment variable value
        
        Args:
            key: Environment variable key
            default: Default value if not found
            
        Returns:
            str: Environment variable value
        """
        return os.getenv(key, default)
    
    def validate_required_vars(self, required_vars: Dict[str, str]) -> Dict[str, bool]:
        """
        Validate that required environment variables are set
        
        Args:
            required_vars: Dictionary of required variables
            
        Returns:
            Dict[str, bool]: Validation status for each variable
        """
        return {key: bool(value) for key, value in required_vars.items()}
