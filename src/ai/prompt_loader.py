"""
Prompt loader implementation
Handles loading of AI prompts from files
"""

import os
from pathlib import Path
from src.ai.interfaces import IPromptLoader


class FilePromptLoader(IPromptLoader):
    """File-based prompt loader implementation"""
    
    def __init__(self, prompts_directory: str = 'prompts'):
        """
        Initialize prompt loader
        
        Args:
            prompts_directory: Directory containing prompt files
        """
        self.prompts_dir = Path(prompts_directory)
    
    def load_prompt(self, prompt_name: str) -> str:
        """
        Load prompt from file
        
        Args:
            prompt_name: Name of the prompt file (without extension)
            
        Returns:
            str: Prompt content
            
        Raises:
            FileNotFoundError: If prompt file doesn't exist
        """
        prompt_file = self.prompts_dir / f"{prompt_name}.md"
        
        if not prompt_file.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
        
        try:
            with open(prompt_file, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            raise Exception(f"Failed to load prompt {prompt_name}: {e}")
