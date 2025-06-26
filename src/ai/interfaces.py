"""
Abstract interfaces for AI services
Defines contracts for AI operations following Interface Segregation Principle
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from src.models.email_models import EmailMessage, SpamAnalysisResult, ConnectionConfig


class IAIService(ABC):
    """Abstract interface for AI services"""
    
    @abstractmethod
    def connect(self, config: ConnectionConfig) -> bool:
        """Connect to AI service"""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if service is connected"""
        pass
    
    @abstractmethod
    def analyze_spam(self, email_obj: EmailMessage) -> SpamAnalysisResult:
        """Analyze email for spam detection"""
        pass
    
    @abstractmethod
    def analyze_email(self, email_obj: EmailMessage) -> str:
        """Perform comprehensive email analysis"""
        pass
    
    @abstractmethod
    def generate_draft(self, analysis_result: str) -> str:
        """Generate draft response based on analysis"""
        pass


class IPromptLoader(ABC):
    """Abstract interface for loading AI prompts"""
    
    @abstractmethod
    def load_prompt(self, prompt_name: str) -> str:
        """Load prompt from file"""
        pass
