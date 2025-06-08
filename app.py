"""
NimbusRelay - Minimalistic Email Management Application
A beautiful, responsive email client with AI-powered spam detection and draft generation.
"""

import os
import json
import imaplib
import email
import time
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
from openai import AzureOpenAI
from email.header import decode_header, make_header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables
load_dotenv()

# Initialize Flask app with imperial purple theme
app = Flask(__name__, 
           static_folder='static',
           template_folder='templates')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'nimbus-relay-imperial-secret')

# Enable CORS for frontend communication
CORS(app, origins=["*"])
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global variables for email and AI services
mailbox_connection = None
azure_client = None

class EmailService:
    """Service class for email operations with IMAP"""
    
    def __init__(self):
        self.connection = None
        self.config = {}
    
    def connect(self, config: Dict[str, str]) -> bool:
        """Connect to IMAP server with provided configuration"""
        try:
            self.config = config
            self.connection = imaplib.IMAP4_SSL(
                config['IMAP_SERVER'], 
                int(config.get('IMAP_PORT', 993))
            )
            self.connection.login(config['IMAP_USERNAME'], config['IMAP_PASSWORD'])
            return True
        except Exception as e:
            print(f"Email connection failed: {e}")
            return False
    
    def disconnect(self):
        """Safely disconnect from IMAP server"""
        if self.connection:
            try:
                self.connection.close()
                self.connection.logout()
            except:
                pass
            self.connection = None
    
    def list_folders(self) -> List[Dict[str, Any]]:
        """List all available email folders"""
        if not self.connection:
            return []
        
        try:
            status, folders = self.connection.list()
            folder_list = []
            
            for folder in folders:
                folder_info = folder.decode('utf-8')
                # Parse folder information
                parts = folder_info.split('"')
                if len(parts) >= 3:
                    folder_name = parts[-2]
                    folder_list.append({
                        'name': folder_name,
                        'display_name': folder_name.split('.')[-1].title(),
                        'type': self._get_folder_type(folder_name)
                    })
            
            return folder_list
        except Exception as e:
            print(f"Failed to list folders: {e}")
            return []
    
    def _get_folder_type(self, folder_name: str) -> str:
        """Determine folder type based on name"""
        folder_lower = folder_name.lower()
        if 'spam' in folder_lower or 'junk' in folder_lower:
            return 'spam'
        elif 'inbox' in folder_lower:
            return 'inbox'
        elif 'sent' in folder_lower:
            return 'sent'
        elif 'draft' in folder_lower:
            return 'drafts'
        elif 'trash' in folder_lower or 'deleted' in folder_lower:
            return 'trash'
        else:
            return 'custom'
    
    def get_emails(self, folder: str = 'INBOX', limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve emails from specified folder"""
        if not self.connection:
            return []
        
        try:
            self.connection.select(folder)
            status, messages = self.connection.search(None, 'ALL')
            
            if status != 'OK':
                return []
            
            email_ids = messages[0].split()
            emails = []
            
            # Get latest emails (limited by limit parameter)
            for email_id in reversed(email_ids[-limit:]):
                try:
                    status, msg_data = self.connection.fetch(email_id, '(RFC822)')
                    if status == 'OK':
                        raw_email = msg_data[0][1]
                        email_obj = self._parse_email(raw_email)
                        email_obj['id'] = email_id.decode('utf-8')
                        emails.append(email_obj)
                except Exception as e:
                    print(f"Failed to fetch email {email_id}: {e}")
                    continue
            
            return emails
        except Exception as e:
            print(f"Failed to get emails: {e}")
            return []
    
    def _parse_email(self, raw_email_bytes: bytes) -> Dict[str, Any]:
        """Parse raw email bytes into structured data"""
        msg = email.message_from_bytes(raw_email_bytes)
        
        email_details = {
            "from": self._decode_mime_header(msg.get("From")),
            "to": self._decode_mime_header(msg.get("To")),
            "subject": self._decode_mime_header(msg.get("Subject")),
            "date": self._decode_mime_header(msg.get("Date")),
            "content_type": self._decode_mime_header(msg.get("Content-Type")),
            "body": None,
            "preview": ""
        }
        
        if not email_details["subject"] or email_details["subject"].strip() == "":
            email_details["subject"] = "(no subject)"
        
        # Extract email body
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    charset = part.get_content_charset() or "utf-8"
                    email_details["body"] = part.get_payload(decode=True).decode(charset, errors="replace")
                    break
                elif part.get_content_type() == "text/html" and not email_details["body"]:
                    charset = part.get_content_charset() or "utf-8"
                    email_details["body"] = part.get_payload(decode=True).decode(charset, errors="replace")
        else:
            charset = msg.get_content_charset() or "utf-8"
            email_details["body"] = msg.get_payload(decode=True).decode(charset, errors="replace")
        
        # Create preview text (first 150 characters)
        if email_details["body"]:
            preview_text = email_details["body"].replace('\n', ' ').replace('\r', ' ').strip()
            email_details["preview"] = preview_text[:150] + "..." if len(preview_text) > 150 else preview_text
        
        return email_details
    
    def _decode_mime_header(self, header_value):
        """Decode MIME encoded headers"""
        if header_value is None:
            return None
        try:
            return str(make_header(decode_header(header_value)))
        except Exception:
            return header_value

class AIService:
    """Service class for AI operations using Azure OpenAI"""
    
    def __init__(self):
        self.client = None
        self.config = {}
    
    def connect(self, config: Dict[str, str]) -> bool:
        """Initialize Azure OpenAI client with provided configuration"""
        try:
            self.config = config
            self.client = AzureOpenAI(
                api_version=config['AZURE_OPENAI_API_VERSION'],
                azure_endpoint=config['AZURE_OPENAI_ENDPOINT'],
                api_key=config['AZURE_OPENAI_API_KEY'],
            )
            return True
        except Exception as e:
            print(f"AI service connection failed: {e}")
            return False
    
    def analyze_spam(self, email_obj: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze email for spam detection using AI"""
        if not self.client:
            return {"error": "AI service not connected"}
        
        try:
            # Load spam detection prompt
            with open('prompts/email-spam.md', 'r', encoding='utf-8') as file:
                spam_prompt = file.read()
            
            # Truncate email body for analysis
            email_copy = dict(email_obj)
            if email_copy.get("body"):
                email_copy["body"] = email_copy["body"][:25000]
            
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": spam_prompt},
                    {"role": "user", "content": json.dumps(email_copy)}
                ],
                max_tokens=1000,
                temperature=0.3,
                model=self.config['AZURE_OPENAI_DEPLOYMENT']
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                return json.loads(result_text)
            except json.JSONDecodeError:
                # Fallback parsing
                is_spam = "spam" in result_text.lower() or "junk" in result_text.lower()
                return {
                    "classification": "Spam/Junk" if is_spam else "Not Spam",
                    "confidence": 0.7,
                    "reason": result_text
                }
                
        except Exception as e:
            print(f"Spam analysis failed: {e}")
            return {"error": f"Analysis failed: {str(e)}"}
    
    def analyze_email(self, email_obj: Dict[str, Any]) -> str:
        """Perform comprehensive email analysis"""
        if not self.client:
            return "AI service not connected"
        
        try:
            # Load email analysis prompt
            with open('prompts/email-analyze.md', 'r', encoding='utf-8') as file:
                analyze_prompt = file.read()
            
            # Truncate email body for analysis
            email_copy = dict(email_obj)
            if email_copy.get("body"):
                email_copy["body"] = email_copy["body"][:25000]
            
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": analyze_prompt},
                    {"role": "user", "content": json.dumps(email_copy)}
                ],
                max_tokens=2000,
                temperature=0.5,
                model=self.config['AZURE_OPENAI_DEPLOYMENT']
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Email analysis failed: {e}")
            return f"Analysis failed: {str(e)}"
    
    def generate_draft(self, analysis_result: str) -> str:
        """Generate draft response based on email analysis"""
        if not self.client:
            return "AI service not connected"
        
        try:
            # Load draft generation prompt
            with open('prompts/email-draft.md', 'r', encoding='utf-8') as file:
                draft_prompt = file.read()
            
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": draft_prompt},
                    {"role": "user", "content": analysis_result}
                ],
                max_tokens=1500,
                temperature=0.7,
                model=self.config['AZURE_OPENAI_DEPLOYMENT']
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Draft generation failed: {e}")
            return f"Draft generation failed: {str(e)}"

# Initialize services
email_service = EmailService()
ai_service = AIService()

def get_required_env_vars() -> Dict[str, str]:
    """Get list of required environment variables and their current values"""
    required_vars = {
        'AZURE_OPENAI_ENDPOINT': os.getenv('AZURE_OPENAI_ENDPOINT', ''),
        'AZURE_OPENAI_API_KEY': os.getenv('AZURE_OPENAI_API_KEY', ''),
        'AZURE_OPENAI_DEPLOYMENT': os.getenv('AZURE_OPENAI_DEPLOYMENT', ''),
        'AZURE_OPENAI_API_VERSION': os.getenv('AZURE_OPENAI_API_VERSION', '2024-12-01-preview'),
        'IMAP_SERVER': os.getenv('IMAP_SERVER', ''),
        'IMAP_PORT': os.getenv('IMAP_PORT', '993'),
        'IMAP_USERNAME': os.getenv('IMAP_USERNAME', ''),
        'IMAP_PASSWORD': os.getenv('IMAP_PASSWORD', ''),
    }
    return required_vars

def save_env_var(key: str, value: str) -> bool:
    """Save environment variable to .env file"""
    try:
        env_file = Path('.env')
        
        # Read existing content
        existing_content = {}
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        k, v = line.split('=', 1)
                        existing_content[k] = v
        
        # Update with new value
        existing_content[key] = value
        
        # Write back to file
        with open(env_file, 'w', encoding='utf-8') as f:
            for k, v in existing_content.items():
                f.write(f"{k}={v}\n")
        
        # Update current environment
        os.environ[key] = value
        return True
        
    except Exception as e:
        print(f"Failed to save environment variable: {e}")
        return False

# Routes
@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html')

@app.route('/debug')
def debug():
    """Serve the debug page"""
    return render_template('debug.html')

@app.route('/api/config')
def get_config():
    """Get current configuration status"""
    env_vars = get_required_env_vars()
    missing_vars = [k for k, v in env_vars.items() if not v]
    
    return jsonify({
        'configured': len(missing_vars) == 0,
        'missing_vars': missing_vars,
        'current_config': {k: bool(v) for k, v in env_vars.items()}
    })

@app.route('/api/config', methods=['POST'])
def save_config():
    """Save configuration parameters"""
    try:
        data = request.get_json()
        
        for key, value in data.items():
            if not save_env_var(key, value):
                return jsonify({'success': False, 'error': f'Failed to save {key}'}), 500
        
        return jsonify({'success': True, 'message': 'Configuration saved successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/connect', methods=['POST'])
def connect_services():
    """Connect to email and AI services"""
    try:
        env_vars = get_required_env_vars()
        
        # Connect to email service
        email_connected = email_service.connect(env_vars)
        if not email_connected:
            return jsonify({'success': False, 'error': 'Failed to connect to email service'}), 500
        
        # Connect to AI service
        ai_connected = ai_service.connect(env_vars)
        if not ai_connected:
            return jsonify({'success': False, 'error': 'Failed to connect to AI service'}), 500
        
        return jsonify({'success': True, 'message': 'Connected to all services successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/folders')
def list_folders():
    """List email folders"""
    try:
        folders = email_service.list_folders()
        return jsonify({'folders': folders})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/emails')
def get_emails():
    """Get emails from specified folder"""
    try:
        folder = request.args.get('folder', 'INBOX')
        limit = int(request.args.get('limit', 50))
        
        emails = email_service.get_emails(folder, limit)
        return jsonify({'emails': emails})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-spam', methods=['POST'])
def analyze_spam():
    """Analyze email for spam detection"""
    try:
        email_data = request.get_json()
        result = ai_service.analyze_spam(email_data)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-email', methods=['POST'])
def analyze_email():
    """Perform comprehensive email analysis"""
    try:
        email_data = request.get_json()
        analysis = ai_service.analyze_email(email_data)
        return jsonify({'analysis': analysis})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-draft', methods=['POST'])
def generate_draft():
    """Generate draft response based on analysis"""
    try:
        data = request.get_json()
        analysis = data.get('analysis', '')
        
        draft = ai_service.generate_draft(analysis)
        return jsonify({'draft': draft})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Static file serving
@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

# WebSocket events for real-time updates
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('status', {'message': 'Connected to NimbusRelay'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

if __name__ == '__main__':
    print("🌩️  Starting NimbusRelay - Minimalistic Email Management")
    print("📧  Imperial Purple Theme - Grandeur & Nobility")
    print("🔗  http://localhost:5000")
    
    # Run the application
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
