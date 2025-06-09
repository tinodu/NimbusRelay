"""
Azure OpenAI Service Implementation
Concrete implementation of AI service using Azure OpenAI
"""

import json
from typing import Dict, Any, Optional
from openai import AzureOpenAI
from src.ai.interfaces import IAIService, IPromptLoader
from src.ai.prompt_loader import FilePromptLoader
from src.models.email_models import EmailMessage, SpamAnalysisResult, ConnectionConfig


class AzureAIService(IAIService):
    """Azure OpenAI implementation of AI service following Dependency Inversion Principle"""
    
    def __init__(self, prompt_loader: IPromptLoader = None):
        """
        Initialize Azure AI service with dependency injection
        
        Args:
            prompt_loader: Loader for AI prompts
        """
        self.client: Optional[AzureOpenAI] = None
        self.config: Optional[ConnectionConfig] = None
        
        # Dependency injection for prompt loading
        self.prompt_loader = prompt_loader or FilePromptLoader()
    
    def connect(self, config: ConnectionConfig) -> bool:
        """
        Initialize Azure OpenAI client with provided configuration
        
        Args:
            config: Connection configuration
            
        Returns:
            bool: Success status
        """
        try:
            self.config = config
            self.client = AzureOpenAI(
                api_version=config.azure_api_version,
                azure_endpoint=config.azure_endpoint,
                api_key=config.azure_api_key,
            )
            return True
        except Exception as e:
            print(f"AI service connection failed: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Check if service is connected"""
        return self.client is not None and self.config is not None
    
    def analyze_spam(self, email_obj: EmailMessage) -> SpamAnalysisResult:
        """
        Analyze email for spam detection using AI
        
        Args:
            email_obj: Email message to analyze
            
        Returns:
            SpamAnalysisResult: Spam analysis results
        """
        if not self.is_connected():
            return SpamAnalysisResult(
                classification="Error",
                confidence=0.0,
                reason="AI service not connected"
            )
        
        try:
            # Load spam detection prompt
            spam_prompt = self.prompt_loader.load_prompt('email-spam')
            
            # Prepare email data for analysis
            email_data = self._prepare_email_for_analysis(email_obj)
            
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": spam_prompt},
                    {"role": "user", "content": json.dumps(email_data)}
                ],
                max_tokens=1000,
                temperature=0.3,
                model=self.config.azure_deployment
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                result_data = json.loads(result_text)
                return SpamAnalysisResult(
                    classification=result_data.get('classification', 'Unknown'),
                    confidence=float(result_data.get('confidence', 0.0)),
                    reason=result_data.get('reason', 'No reason provided')
                )
            except json.JSONDecodeError:
                # Fallback parsing
                is_spam = "spam" in result_text.lower() or "junk" in result_text.lower()
                return SpamAnalysisResult(
                    classification="Spam/Junk" if is_spam else "Not Spam",
                    confidence=0.7,
                    reason=result_text
                )
                
        except Exception as e:
            print(f"Spam analysis failed: {e}")
            return SpamAnalysisResult(
                classification="Error",
                confidence=0.0,
                reason=f"Analysis failed: {str(e)}"
            )
    
    def analyze_email(self, email_obj: EmailMessage) -> str:
        """
        Perform comprehensive email analysis
        
        Args:
            email_obj: Email message to analyze
            
        Returns:
            str: Analysis results
        """
        if not self.is_connected():
            return "AI service not connected"
        
        try:
            # Load email analysis prompt
            analyze_prompt = self.prompt_loader.load_prompt('email-analyze')
            
            # Prepare email data for analysis
            email_data = self._prepare_email_for_analysis(email_obj)
            
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": analyze_prompt},
                    {"role": "user", "content": json.dumps(email_data)}
                ],
                max_tokens=2000,
                temperature=0.5,
                model=self.config.azure_deployment
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Email analysis failed: {e}")
            return f"Analysis failed: {str(e)}"
    
    def generate_draft(self, analysis_result: str) -> str:
        """
        Generate draft response based on email analysis
        
        Args:
            analysis_result: Email analysis results
            
        Returns:
            str: Generated draft response
        """
        if not self.is_connected():
            return "AI service not connected"
        
        try:
            # Load draft generation prompt
            draft_prompt = self.prompt_loader.load_prompt('email-draft')
            
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": draft_prompt},
                    {"role": "user", "content": analysis_result}
                ],
                max_tokens=1500,
                temperature=0.7,
                model=self.config.azure_deployment
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Draft generation failed: {e}")
            return f"Draft generation failed: {str(e)}"
    
    def _prepare_email_for_analysis(self, email_obj: EmailMessage) -> Dict[str, Any]:
        """
        Prepare email data for AI analysis by truncating content if necessary
        
        Args:
            email_obj: Email message
            
        Returns:
            Dict: Prepared email data
        """
        email_data = email_obj.to_dict()
        
        # Truncate email body for analysis (max 25000 characters)
        if email_data.get("body") and len(email_data["body"]) > 25000:
            email_data["body"] = email_data["body"][:25000]
        
        return email_data
