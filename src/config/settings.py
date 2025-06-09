"""
Configuration settings for NimbusRelay application
Follows the Single Responsibility Principle for configuration management
"""

import os
from typing import Dict, Any


class Config:
    """Base configuration class with default settings"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'nimbus-relay-imperial-secret')
    DEBUG = False
    TESTING = False
    
    # CORS Configuration
    CORS_ORIGINS = ["*"]
    
    # SocketIO Configuration
    SOCKETIO_ASYNC_MODE = 'threading'
    
    @staticmethod
    def get_required_env_vars() -> Dict[str, str]:
        """Get list of required environment variables and their current values"""
        return {
            'AZURE_OPENAI_ENDPOINT': os.getenv('AZURE_OPENAI_ENDPOINT', ''),
            'AZURE_OPENAI_API_KEY': os.getenv('AZURE_OPENAI_API_KEY', ''),
            'AZURE_OPENAI_DEPLOYMENT': os.getenv('AZURE_OPENAI_DEPLOYMENT', ''),
            'AZURE_OPENAI_API_VERSION': os.getenv('AZURE_OPENAI_API_VERSION', '2024-12-01-preview'),
            'IMAP_SERVER': os.getenv('IMAP_SERVER', ''),
            'IMAP_PORT': os.getenv('IMAP_PORT', '993'),
            'IMAP_USERNAME': os.getenv('IMAP_USERNAME', ''),
            'IMAP_PASSWORD': os.getenv('IMAP_PASSWORD', ''),
        }


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False


# Configuration mapping
config_map = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
