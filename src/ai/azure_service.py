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
            # Validate required configuration
            print(f"Attempting to connect to Azure OpenAI...")
            print(f"Endpoint: {config.azure_endpoint}")
            print(f"Deployment: {config.azure_deployment}")
            print(f"API Version: {config.azure_api_version}")
            print(f"API Key present: {'Yes' if config.azure_api_key else 'No'}")
            
            if not config.azure_endpoint:
                print("AI service connection failed: Missing Azure OpenAI endpoint")
                return False
            if not config.azure_api_key:
                print("AI service connection failed: Missing Azure OpenAI API key")
                return False
            if not config.azure_deployment:
                print("AI service connection failed: Missing Azure OpenAI deployment name")
                return False
            
            self.config = config
            
            # Initialize Azure OpenAI client with explicit parameters only
            print("Creating AzureOpenAI client...")
            
            try:
                # Method 1: Set environment variables and use default initialization
                print("Attempting method 1: Environment variable initialization...")
                import os
                
                # Set required environment variables
                os.environ['OPENAI_API_TYPE'] = 'azure'
                os.environ['OPENAI_API_VERSION'] = config.azure_api_version
                os.environ['AZURE_OPENAI_ENDPOINT'] = config.azure_endpoint
                os.environ['AZURE_OPENAI_API_KEY'] = config.azure_api_key
                
                # Clear any proxy environment variables that might interfere
                proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY', 'all_proxy']
                original_proxies = {}
                for var in proxy_vars:
                    if var in os.environ:
                        original_proxies[var] = os.environ[var]
                        print(f"Temporarily removing proxy variable: {var}")
                        del os.environ[var]
                
                try:
                    # Create client without any parameters to avoid the proxies issue
                    self.client = AzureOpenAI()
                    print("Method 1 successful - using environment variables")
                    
                except Exception as env_error:
                    print(f"Environment variable method failed: {env_error}")
                    
                    # Method 2: Try with positional arguments instead of keyword arguments
                    print("Attempting method 2: Positional arguments...")
                    try:
                        # Create a simple client configuration
                        from openai._client import AzureOpenAI as DirectAzureOpenAI
                        self.client = DirectAzureOpenAI(
                            azure_endpoint=config.azure_endpoint,
                            api_key=config.azure_api_key,
                            api_version=config.azure_api_version
                        )
                        print("Method 2 successful - direct client import")
                        
                    except Exception as direct_error:
                        print(f"Direct import method failed: {direct_error}")
                        
                        # Method 3: Try creating the client with a custom httpx client
                        print("Attempting method 3: Custom HTTP client...")
                        try:
                            import httpx
                            
                            # Create a custom HTTP client without proxy support
                            http_client = httpx.Client()
                            
                            self.client = AzureOpenAI(
                                azure_endpoint=config.azure_endpoint,
                                api_key=config.azure_api_key,
                                api_version=config.azure_api_version,
                                http_client=http_client
                            )
                            print("Method 3 successful - custom HTTP client")
                            
                        except Exception as custom_error:
                            print(f"Custom HTTP client method failed: {custom_error}")
                            raise env_error  # Raise the original error
                            
                finally:
                    # Restore proxy environment variables
                    for var, value in original_proxies.items():
                        os.environ[var] = value
                        print(f"Restored proxy variable: {var}")
                        
            except Exception as init_error:
                print(f"All initialization attempts failed: {init_error}")
                raise init_error
            
            print("AI service client created successfully")
            
            # Test the connection with a simple call
            print("Testing connection with a simple API call...")
            try:
                test_response = self.client.chat.completions.create(
                    model=config.azure_deployment,
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=5,
                    temperature=0
                )
                print("AI service connection test successful!")
                return True
            except Exception as test_error:
                print(f"AI service connection test failed: {test_error}")
                print(f"Test error type: {type(test_error).__name__}")
                return False
                
        except Exception as e:
            print(f"AI service connection failed during initialization: {e}")
            print(f"Error type: {type(e).__name__}")
            self.client = None
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
                print("Spam analysis raw result:", json.dumps(result_data, indent=2))
                return SpamAnalysisResult(
                    classification=result_data.get('classification', 'Unknown'),
                    confidence=float(result_data.get('confidence', 0.0)),
                    reason=result_data.get('reason', 'No reason provided')
                )
            except json.JSONDecodeError:
                # Fallback parsing
                is_spam = "spam" in result_text.lower() or "junk" in result_text.lower()
                return SpamAnalysisResult(
                    classification="Spam/Junk" if is_spam else "Valid",
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
