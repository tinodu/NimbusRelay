"""
Static file routes for NimbusRelay application
Handles serving of static files and templates
"""

from flask import Flask, render_template, send_from_directory


def register_static_routes(app: Flask) -> None:
    """
    Register static file routes with the Flask application
    
    Args:
        app: Flask application instance
    """
    
    @app.route('/')
    def index():
        """Serve the main application page"""
        return render_template('index.html')
    
    @app.route('/debug')
    def debug():
        """Serve the debug page"""
        return render_template('debug.html')
    
    @app.route('/static/<path:filename>')
    def serve_static(filename):
        """Serve static files"""
        return send_from_directory('static', filename)
