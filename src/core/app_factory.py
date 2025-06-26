"""
Application Factory for NimbusRelay
Creates and configures the Flask application with proper dependency injection
"""

import os
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from dotenv import load_dotenv
from typing import Union

from src.config.settings import Config, config_map
from src.middleware.error_handler import ErrorHandler
from src.routes.api_routes import register_api_routes
from src.routes.static_routes import register_static_routes
from src.websocket.socket_handlers import register_socket_handlers


def create_app(config_name_or_class: Union[str, type] = Config) -> tuple[Flask, SocketIO]:
    """
    Application factory function following the Factory Pattern
    
    Args:
        config_name_or_class: Configuration name (string) or class to use
        
    Returns:
        Tuple of (Flask app, SocketIO instance)
    """
    # Load environment variables
    load_dotenv()
    
    # Initialize Flask app with imperial purple theme
    app = Flask(__name__, 
               static_folder='../../static',
               template_folder='../../templates')
    
    # Configure app - handle both string and class configurations
    if isinstance(config_name_or_class, str):
        config_class = config_map.get(config_name_or_class, Config)
    else:
        config_class = config_name_or_class
    
    app.config.from_object(config_class)
    
    # Enable CORS for frontend communication
    CORS(app, origins=["*"])
    
    # Initialize SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    
    # Register error handlers
    ErrorHandler.register_handlers(app)
    
    # Register routes
    register_api_routes(app)
    register_static_routes(app)
    
    # Register WebSocket handlers
    register_socket_handlers(socketio)
    
    return app, socketio


def run_app(app: Flask, socketio: SocketIO) -> None:
    """
    Run the application with proper configuration
    
    Args:
        app: Flask application instance
        socketio: SocketIO instance
    """
    print("🌩️  Starting NimbusRelay - Minimalistic Email Management")
    print("📧  Imperial Purple Theme - Grandeur & Nobility")
    print("🔗  http://localhost:5000")
    
    # Run the application
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
