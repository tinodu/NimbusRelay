"""
API routes for NimbusRelay application
Handles REST API endpoints following Single Responsibility Principle
"""

from flask import Flask, request, jsonify
from src.services.service_manager import ServiceManager
from src.config.environment import EnvironmentManager
from src.config.settings import Config


# Global service manager instance
service_manager = ServiceManager()
env_manager = EnvironmentManager()


def register_api_routes(app: Flask) -> None:
    """
    Register all API routes with the Flask application
    
    Args:
        app: Flask application instance
    """

    import re

    def strip_json_code_block(text):
        """
        Extracts and returns any text outside a JSON code block.
        If only a JSON code block exists, returns its content as plain text.
        """
        if not isinstance(text, str):
            return text
        # Find all code blocks
        code_blocks = re.findall(r"```json(.*?)```", text, flags=re.DOTALL)
        # Remove all code blocks from text
        text_outside = re.sub(r"```json.*?```", "", text, flags=re.DOTALL).strip()
        if text_outside:
            return text_outside
        elif code_blocks:
            # Return the first code block content, stripped of whitespace
            return code_blocks[0].strip()
        else:
            return text.strip()
    
    @app.route('/api/config')
    def get_config():
        """Get current configuration status"""
        try:
            env_vars = Config.get_required_env_vars()
            missing_vars = [k for k, v in env_vars.items() if not v]
            
            return jsonify({
                'configured': len(missing_vars) == 0,
                'missing_vars': missing_vars,
                'current_config': {k: bool(v) for k, v in env_vars.items()}
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/config', methods=['POST'])
    def save_config():
        """Save configuration parameters"""
        try:
            data = request.get_json()
            
            for key, value in data.items():
                if not env_manager.save_env_var(key, value):
                    return jsonify({
                        'success': False, 
                        'error': f'Failed to save {key}'
                    }), 500
            
            return jsonify({
                'success': True, 
                'message': 'Configuration saved successfully'
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/connect', methods=['POST'])
    def connect_services():
        """Connect to email and AI services"""
        try:
            env_vars = Config.get_required_env_vars()
            result = service_manager.connect_services(env_vars)
            
            if result['success']:
                return jsonify(result)
            else:
                return jsonify(result), 400
                
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/folders')
    def list_folders():
        """List email folders with optional hidden folder inclusion"""
        try:
            include_hidden = request.args.get('include_hidden', 'false').lower() == 'true'
            result = service_manager.get_folders(include_hidden)
            
            if 'error' in result:
                return jsonify(result), 400
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/folder-counts')
    def get_folder_counts():
        """Get email counts for all folders"""
        try:
            result = service_manager.get_folder_counts()
            
            if 'error' in result:
                return jsonify(result), 400
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/emails')
    def get_emails():
        """Get emails from specified folder"""
        try:
            folder = request.args.get('folder', 'INBOX')
            limit = int(request.args.get('limit', 50))
            
            result = service_manager.get_emails(folder, limit)
            
            if 'error' in result:
                return jsonify(result), 400
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/analyze-spam', methods=['POST'])
    def analyze_spam():
        """Analyze email for spam detection"""
        try:
            email_data = request.get_json()
            print(f"[SPAM API] Received request with email data keys: {list(email_data.keys()) if email_data else 'None'}")
            
            if not email_data:
                print("[SPAM API] No email data provided")
                return jsonify({'error': 'No email data provided'}), 400
            
            print(f"[SPAM API] Processing email: Subject='{email_data.get('subject', 'N/A')}', From='{email_data.get('from', 'N/A')}'")
            result = service_manager.analyze_spam(email_data)
            
            if 'error' in result:
                print(f"[SPAM API] Error in analysis: {result['error']}")
                return jsonify(result), 400

            # If the result contains an 'explanation' or 'analysis' field, strip JSON code block
            if 'explanation' in result and isinstance(result['explanation'], str):
                result['explanation'] = strip_json_code_block(result['explanation'])
            if 'analysis' in result and isinstance(result['analysis'], str):
                result['analysis'] = strip_json_code_block(result['analysis'])
            
            print(f"[SPAM API] Returning result: {result}")
            return jsonify(result)
            
        except Exception as e:
            error_msg = str(e)
            print(f"[SPAM API] Exception in analyze_spam: {error_msg}")
            return jsonify({'error': error_msg}), 500
    
    @app.route('/api/analyze-email', methods=['POST'])
    def analyze_email():
        """Perform comprehensive email analysis"""
        try:
            email_data = request.get_json()
            result = service_manager.analyze_email(email_data)
            
            if 'error' in result:
                return jsonify(result), 400

            # If the result contains an 'analysis' field, strip JSON code block
            if 'analysis' in result and isinstance(result['analysis'], str):
                result['analysis'] = strip_json_code_block(result['analysis'])
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/generate-draft', methods=['POST'])
    def generate_draft():
        """Generate draft response based on email analysis"""
        try:
            data = request.get_json()
            analysis_result = data.get('analysis', '')
            
            result = service_manager.generate_draft(analysis_result)
            
            if 'error' in result:
                return jsonify(result), 400
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/move-email', methods=['POST'])
    def move_email():
        """Move email from one folder to another"""
        try:
            data = request.get_json()
            print(f"[MOVE EMAIL API] Received request: {data}")
            
            if not data:
                print("[MOVE EMAIL API] No data provided")
                return jsonify({'error': 'No data provided'}), 400
            
            email_id = data.get('email_id')
            source_folder = data.get('source_folder', 'INBOX')
            target_folder = data.get('target_folder')
            
            if not email_id or not target_folder:
                print(f"[MOVE EMAIL API] Missing required fields: email_id={email_id}, target_folder={target_folder}")
                return jsonify({'error': 'Missing email_id or target_folder'}), 400
            
            print(f"[MOVE EMAIL API] Moving email {email_id} from {source_folder} to {target_folder}")
            result = service_manager.move_email(email_id, source_folder, target_folder)
            
            if 'error' in result:
                print(f"[MOVE EMAIL API] Error in move operation: {result['error']}")
                return jsonify(result), 400
            
            print(f"[MOVE EMAIL API] Successfully moved email: {result}")
            return jsonify(result)
            
        except Exception as e:
            error_msg = str(e)
            print(f"[MOVE EMAIL API] Exception in move_email: {error_msg}")
            return jsonify({'error': error_msg}), 500
    
    @app.route('/api/debug/folders')
    def debug_folders():
        """Debug endpoint to get detailed folder information"""
        try:
            print("[DEBUG FOLDERS] Getting detailed folder information...")
            
            # Get detailed folder debug info from email service
            if hasattr(service_manager.email_service, 'debug_all_folders'):
                debug_info = service_manager.email_service.debug_all_folders()
                print(f"[DEBUG FOLDERS] Debug info: {debug_info}")
                return jsonify(debug_info)
            else:
                return jsonify({'error': 'Debug method not available'}), 400
                
        except Exception as e:
            error_msg = str(e)
            print(f"[DEBUG FOLDERS] Exception: {error_msg}")
            return jsonify({'error': error_msg}), 500

    @app.route('/api/email-raw')
    def get_email_raw():
        """Get raw email source by ID"""
        try:
            email_id = request.args.get('id')
            if not email_id:
                return jsonify({'error': 'Missing email id'}), 400
            raw = service_manager.get_email_raw(email_id)
            if raw is None:
                return jsonify({'error': 'Raw email not found'}), 404
            return jsonify({'raw': raw})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
