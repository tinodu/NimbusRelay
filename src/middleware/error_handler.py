"""
Error handling middleware for NimbusRelay application
Provides centralized error handling following Single Responsibility Principle
"""

from flask import Flask, jsonify, request
import logging
import traceback


class ErrorHandler:
    """Centralized error handling for the application"""
    
    @staticmethod
    def register_handlers(app: Flask) -> None:
        """
        Register error handlers with the Flask application
        
        Args:
            app: Flask application instance
        """
        
        @app.errorhandler(400)
        def bad_request(error):
            """Handle 400 Bad Request errors"""
            return jsonify({
                'error': 'Bad Request',
                'message': 'The request could not be understood by the server',
                'status_code': 400
            }), 400
        
        @app.errorhandler(401)
        def unauthorized(error):
            """Handle 401 Unauthorized errors"""
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Authentication is required',
                'status_code': 401
            }), 401
        
        @app.errorhandler(403)
        def forbidden(error):
            """Handle 403 Forbidden errors"""
            return jsonify({
                'error': 'Forbidden',
                'message': 'Access to this resource is forbidden',
                'status_code': 403
            }), 403
        
        @app.errorhandler(404)
        def not_found(error):
            """Handle 404 Not Found errors"""
            return jsonify({
                'error': 'Not Found',
                'message': 'The requested resource was not found',
                'status_code': 404
            }), 404
        
        @app.errorhandler(405)
        def method_not_allowed(error):
            """Handle 405 Method Not Allowed errors"""
            return jsonify({
                'error': 'Method Not Allowed',
                'message': 'The method is not allowed for this resource',
                'status_code': 405
            }), 405
        
        @app.errorhandler(500)
        def internal_server_error(error):
            """Handle 500 Internal Server Error"""
            # Log the error for debugging
            app.logger.error(f'Internal Server Error: {error}')
            app.logger.error(traceback.format_exc())
            
            return jsonify({
                'error': 'Internal Server Error',
                'message': 'An internal server error occurred',
                'status_code': 500
            }), 500
        
        @app.errorhandler(Exception)
        def handle_unexpected_error(error):
            """Handle unexpected exceptions"""
            # Log the error
            app.logger.error(f'Unexpected error: {error}')
            app.logger.error(traceback.format_exc())
            
            # Return generic error response
            return jsonify({
                'error': 'Unexpected Error',
                'message': 'An unexpected error occurred',
                'status_code': 500
            }), 500
        
        # Set up logging
        if not app.debug:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s %(levelname)s %(name)s %(message)s'
            )
