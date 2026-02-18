"""
Basic Chatbot Flask Application with H.E.R.O.S. SSO Integration
"""

import os
import json
import uuid
import re
import mimetypes
import threading
import time
import tempfile
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, g, send_from_directory, send_file
from flask_socketio import SocketIO, emit, join_room, leave_room
from dotenv import load_dotenv
import logging
from openai import OpenAI
import inspect
from pathlib import Path
from typing import Optional, Dict, Any
from werkzeug.utils import secure_filename


# Import SSO utilities
from sso_client_utils import init_sso, sso_token_required, get_current_user, logout_user, get_sso_client

# Import web scraper utilities
from web_scraper import WebScraper

# Load environment variables
load_dotenv()

# Development mode flag (use 'dev' to bypass session enforcement)
DEV_MODE = os.getenv("DEV_MODE", "production")

# Import standardized logger
from utils.logger import logger, workflow_logger, agent_logger, browser_logger

# Diagnostic trace helper (module-level)
diag_logger = logging.getLogger("diag_logger")

def TRACE(label, data=None):
    if getattr(TRACE, "_in_trace", False):
        return
    TRACE._in_trace = True
    try:
        frame = inspect.currentframe().f_back
        line = getattr(frame, 'f_lineno', None) if frame is not None else None
        func = getattr(frame.f_code, 'co_name', None) if frame is not None and getattr(frame, 'f_code', None) is not None else None
        diag_logger.info(f"[TRACE] {func}:{line} — {label} — {data}")
    finally:
        TRACE._in_trace = False

# Set up logging - REPLACED WITH STANDARDIZED LOGGER
#logging.basicConfig(level=logging.INFO)  # Commented out - using standardized logger
#logger = logging.getLogger(__name__)  # Commented out - using standardized logger

class FlaskChatbotApp:
    def __init__(self):
        self.app = Flask(__name__, static_folder='static', template_folder='templates')
        self.app.secret_key = os.getenv('SECRET_KEY', 'dev-key-change-in-production')

        # Configure timeouts for large file processing
        self.app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size (supports 40MB+ requirement)
        self.app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
        self.app.config['PERMANENT_SESSION_LIFETIME'] = 600  # 10 minutes for long operations

        # Configure request timeout for Heroku (bypass 30-second limit)
        import signal

        def timeout_handler(signum, frame):
            raise TimeoutError("Request timeout")

        # Set request timeout to 10 minutes for OCR operations
        self.request_timeout = 600

        # Initialize SocketIO with extended timeouts for OCR processing
        self.socketio = SocketIO(
            self.app,
            cors_allowed_origins="*",
            ping_timeout=300,  # 5 minutes for long-running operations
            ping_interval=25   # Keep connection alive during processing
        )

        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        # Initialize user document storage (in-memory for session-based storage)
        self.user_documents = {}  # Format: {user_id: [{'filename': str, 'content': str, 'timestamp': datetime}]}

        # Initialize conversation storage
        self.conversations = {}  # Format: {session_id: [{'role': str, 'content': str, 'timestamp': str}]}

        # Initialize temporary downloads storage
        self.temp_downloads = {}  # Format: {download_id: {'filepath': str, 'filename': str, 'created_at': float}}

        # Global progress tracking for file processing
        self.progress_data = {}

        # Initialize SSO
        init_sso('BasicChatbot')

        self.setup_routes()
        self.setup_socket_handlers()

    def update_progress(self, task_id: str, progress: int, message: str):
        """Update progress for a task"""
        if task_id not in self.progress_data:
            self.progress_data[task_id] = {}

        self.progress_data[task_id].update({
            'progress': progress,
            'message': message,
            'timestamp': time.time()
        })
        logger.info(f"Task {task_id}: {progress}% - {message}")

    def _get_current_user_documents(self, username=None):
        """Get current user documents directly from authenticated user context (no caching)"""
        try:
            if not username:
                user = get_current_user()
                if not user:
                    return []
                username = user.get('username')

            if not username:
                return []

            # Return current documents for this user from the storage
            return self.user_documents.get(username, [])

        except Exception as e:
            logger.error(f"Error getting current user documents: {e}")
            return []

    def setup_routes(self):
        """Set up Flask routes with SSO authentication"""

        @self.app.route('/')
        def index():
            """Main page - handles SSO authentication flow"""
            # Developer shortcut: when DEV_MODE is true, inject a dev user and
            # render the index immediately (placed before any token checks).
            if os.getenv("DEV_MODE", "false").lower() == "true":
                g.current_user = {
                    "user_id": "dev-user",
                    "username": "Developer",
                    "email": "dev@example.com"
                }
                return render_template("index.html")

            client = get_sso_client()

            # Check for token in URL (from auth system redirect)
            token = request.args.get('sso_token')
            if token:
                # Validate token
                user_data = client.validate_token(token)
                if user_data:
                    session['sso_token'] = token
                    g.current_user = user_data
                    logger.info(f"User authenticated via URL token: {user_data.get('username')}")
                    # Redirect to app page to remove token from URL
                    return redirect('/app')

            # Check for token in session
            token = session.get('sso_token')
            if token:
                user_data = client.validate_token(token)
                if user_data:
                    g.current_user = user_data
                    logger.info(f"User authenticated via session: {user_data.get('username')}")
                    return redirect('/app')

            # No valid token, redirect to SSO login
            logger.info("No valid token found, redirecting to SSO login")
            # Redirect callers to the central platform root (do NOT include redirect_uri).
            # This prevents automatic round-trip redirects back to the app when
            # the caller is unauthenticated.
            platform_root = os.getenv('AUTH_SERVICE_URL', 'https://unlocking-ai-auth-system-0477b057b952.herokuapp.com/')
            return render_template("index.html")

        @self.app.route('/auth/callback')
        def auth_callback():
            """Handle SSO authentication callback"""
            try:
                # Debug: Log all query parameters
                logger.info(f"Auth callback received. Query args: {dict(request.args)}")

                # Get token from query parameters - auth system sends as 'sso_token'
                token = request.args.get('sso_token') or request.args.get('token')
                if not token:
                    logger.error(f"No token received in callback. Available args: {list(request.args.keys())}")
                    return redirect('/')

                logger.info(f"Token received: {token[:50]}..." if len(token) > 50 else f"Token received: {token}")

                # Validate the token
                client = get_sso_client()
                user_data = client.validate_token(token)
                if not user_data:
                    logger.error("Invalid token received in callback")
                    return redirect('/')

                # Store token in session
                session['sso_token'] = token
                session['user_data'] = user_data

                logger.info(f"User successfully authenticated: {user_data.get('username')}")
                return redirect('/app')

            except Exception as e:
                logger.error(f"Error in auth callback: {e}")
                return redirect('/')

        @self.app.route('/app')
        @sso_token_required
        def main_app():
            """Main chatbot application - SSO protected"""
            user = get_current_user()
            if user:
                logger.info(f"Serving main app for user: {user.get('username')}")
            return render_template('index.html')

        @self.app.route("/get_config")
        @sso_token_required
        def get_config():
            """Get configuration for the frontend"""
            # Production behavior: require authenticated user (token protection enforced by decorator)
            user = get_current_user()
            if not user:
                platform_root = os.getenv('AUTH_SERVICE_URL', 'https://unlocking-ai-auth-system-0477b057b952.herokuapp.com/')
                return redirect(platform_root)

            return jsonify({
                'user': {
                    'id': user.get('id'),
                    'username': user.get('username'),
                    'email': user.get('email')
                },
                'authSystemUrl': os.getenv('AUTH_SERVICE_URL')
            })

        @self.app.route('/api/progress/<task_id>')
        @sso_token_required
        def get_progress(task_id):
            """Get progress for a specific task"""
            if task_id in self.progress_data:
                return jsonify(self.progress_data[task_id])
            else:
                return jsonify({'progress': 0, 'message': 'Task not found'}), 404

        @self.app.route('/download/<download_id>')
        @sso_token_required
        def download_file(download_id):
            """Download processed files (PDF exports and OCR files)"""
            try:
                # First check for temporary PDF exports
                if download_id in self.temp_downloads:
                    download_info = self.temp_downloads[download_id]
                    file_path = download_info['filepath']
                    filename = download_info['filename']

                    if os.path.exists(file_path):
                        return send_file(file_path, as_attachment=True, download_name=filename)
                    else:
                        # Clean up expired entry
                        del self.temp_downloads[download_id]
                        return jsonify({'error': 'File not found or expired'}), 404

                # Fall back to OCR downloads directory
                download_dir = os.path.join(os.path.dirname(__file__), 'downloads')
                if not os.path.exists(download_dir):
                    return jsonify({'error': 'Downloads directory not found'}), 404

                # Find file with matching download_id
                for filename in os.listdir(download_dir):
                    if filename.startswith(download_id + '_'):
                        file_path = os.path.join(download_dir, filename)
                        if os.path.exists(file_path):
                            return send_file(file_path, as_attachment=True, download_name=filename.split('_', 1)[1])

                return jsonify({'error': 'File not found'}), 404
            except Exception as e:
                logger.error(f"Download error: {e}")
                return jsonify({'error': 'Download failed'}), 500

        @self.app.route('/api/files/upload', methods=['POST'])
        @sso_token_required
        def upload_file():
            """Handle file uploads with background processing support - based on working OCR app"""
            user = get_current_user()

            if 'file' not in request.files:
                return jsonify({'error': 'No file uploaded'}), 400

            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400

            try:
                # Generate unique task ID and filename
                task_id = str(uuid.uuid4())
                filename = secure_filename(file.filename or 'unknown_file')

                # Create uploads directory if it doesn't exist
                uploads_dir = os.path.join(os.getcwd(), 'uploads')
                os.makedirs(uploads_dir, exist_ok=True)

                # Save file with task ID prefix
                file_extension = os.path.splitext(filename)[1].lower()
                input_path = os.path.join(uploads_dir, f"{task_id}_{filename}")

                logger.info(f"Starting file upload task: {task_id} for file: {filename}")

                # Save uploaded file
                file.save(input_path)

                # Initialize progress
                self.update_progress(task_id, 0, "File uploaded, starting processing...")

                # Start background processing thread
                def process_file():
                    try:
                        # Initial message informing user that document will be added after processing
                        self.update_progress(task_id, 10, f"Processing {filename}... Document will be added to chatbot context once processing is complete.")

                        processed_content = self.process_uploaded_file_with_progress(input_path, filename, task_id)

                        if not processed_content or not processed_content.strip():
                            self.update_progress(task_id, -1, "No content could be extracted from the file")
                            return

                        # Wait until processing is complete before adding to context
                        self.update_progress(task_id, 98, f"Processing complete. Adding document to chatbot context...")

                        # Store document content in user's session
                        user_id = user.get('username') if user else 'anonymous'
                        if user_id not in self.user_documents:
                            self.user_documents[user_id] = []

                        # Add document to user's collection (keep only last 5 documents to manage memory)
                        self.user_documents[user_id].append({
                            'filename': filename,
                            'content': processed_content,
                            'timestamp': datetime.now()
                        })

                        # Keep only the 5 most recent documents
                        if len(self.user_documents[user_id]) > 5:
                            self.user_documents[user_id] = self.user_documents[user_id][-5:]

                        logger.info(f"Document stored for user {user_id}: {filename}")

                        # Update progress with completion info
                        self.progress_data[task_id].update({
                            'filename': filename,
                            'content_preview': processed_content[:500] + "..." if len(processed_content) > 500 else processed_content,
                            'full_content_length': len(processed_content),
                            'completed': True
                        })

                        # Final success message only after document is loaded into context
                        self.update_progress(task_id, 100, f'File "{filename}" uploaded and processed successfully. Document loaded into chatbot context and ready for use.')

                        # Clean up uploaded file
                        try:
                            os.unlink(input_path)
                        except:
                            pass

                    except Exception as processing_error:
                        # Clean up files on processing error
                        try:
                            if os.path.exists(input_path):
                                os.unlink(input_path)
                        except:
                            pass
                        self.update_progress(task_id, -1, f"File processing failed: {str(processing_error)}")
                        logger.error(f"File processing failed for {filename}: {processing_error}")

                # Start processing thread
                thread = threading.Thread(target=process_file)
                thread.daemon = True
                thread.start()

                # Return task ID immediately for progress tracking
                return jsonify({
                    'success': True,
                    'task_id': task_id,
                    'message': f'File "{filename}" uploaded. Processing in progress... Document will be added to chatbot context once processing is complete.',
                    'filename': filename
                })

            except Exception as e:
                logger.error(f"File upload error: {e}")
                return jsonify({'error': f'File upload failed: {str(e)}'}), 500

        @self.app.route('/api/audio/transcribe', methods=['POST'])
        @sso_token_required
        def transcribe_audio():
            """Transcribe audio using OpenAI Whisper API"""
            user = get_current_user()

            if 'audio' not in request.files:
                return jsonify({'error': 'No audio file provided'}), 400

            audio_file = request.files['audio']
            if audio_file.filename == '':
                return jsonify({'error': 'No audio file selected'}), 400

            try:
                # Use OpenAI Whisper API for transcription
                # Pass the file-like object with a filename
                transcription = self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=(audio_file.filename, audio_file.read(), audio_file.content_type)
                )

                return jsonify({
                    'success': True,
                    'text': transcription.text
                })

            except Exception as e:
                logger.error(f"Error transcribing audio: {e}")
                return jsonify({'error': 'Failed to transcribe audio'}), 500

        @self.app.route('/api/tts', methods=['POST'])
        @sso_token_required
        def tts():
            """Text-to-Speech using OpenAI TTS API"""
            text = request.form.get("text")
            voice = request.form.get("voice", "alloy")  # Default to 'alloy' voice

            if not text:
                return jsonify({'error': 'No text provided'}), 400

            try:
                # Remove markdown syntax from text
                text = re.sub(r'\[.*?\]\(.*?\)', '', text)  # Remove links
                text = re.sub(r'[*_~`]', '', text)  # Remove other markdown symbols
                text = re.sub(r'#{2,}', '', text)  # Remove 2 or more consecutive #

                # Create speech file path
                speech_file_path = Path(__file__).parent / "temp" / "speech.opus"

                # Ensure temp directory exists
                speech_file_path.parent.mkdir(exist_ok=True)

                # Generate speech using OpenAI TTS
                response = self.openai_client.audio.speech.create(
                    model="tts-1",
                    voice=voice,
                    input=text,
                )

                # Save to file
                response.stream_to_file(speech_file_path)

                # Return the audio file
                return send_file(speech_file_path, as_attachment=True, mimetype="audio/ogg")

            except Exception as e:
                logger.error(f"Error generating TTS: {e}")
                return jsonify({'error': 'Failed to generate speech'}), 500

        @self.app.route('/api/remove-document', methods=['POST'])
        @sso_token_required
        def remove_document():
            """Remove a document from user's document collection"""
            user = get_current_user()
            if not user:
                return jsonify({'error': 'User not authenticated'}), 401

            data = request.get_json()
            if not data or 'filename' not in data:
                return jsonify({'error': 'Filename is required'}), 400

            filename = data['filename']
            # Use the same identifier as used during document storage
            user_id = user.get('username') if user else 'anonymous'

            try:
                if user_id not in self.user_documents:
                    return jsonify({'error': 'No documents found for user'}), 404

                # Find and remove the document with matching filename
                user_docs = self.user_documents[user_id]
                original_count = len(user_docs)

                # Filter out the document with the specified filename
                self.user_documents[user_id] = [
                    doc for doc in user_docs
                    if doc['filename'] != filename
                ]

                new_count = len(self.user_documents[user_id])

                if new_count == original_count:
                    return jsonify({'error': 'Document not found'}), 404

                # If no documents left, remove the user entry
                if new_count == 0:
                    del self.user_documents[user_id]

                logger.info(f'Document "{filename}" removed for user: {user_id}')
                return jsonify({
                    'success': True,
                    'message': f'Document "{filename}" removed successfully',
                    'remaining_documents': new_count
                })

            except Exception as e:
                logger.error(f"Error removing document: {e}")
                return jsonify({'error': 'Failed to remove document'}), 500

        @self.app.route('/api/scrape', methods=['POST'])
        @sso_token_required
        def scrape_url():
            """Handle URL scraping, create PDF, and add to documents"""
            user = get_current_user()
            if not user:
                return jsonify({'error': 'User not authenticated'}), 401

            data = request.get_json()
            if not data or 'url' not in data:
                return jsonify({'error': 'URL is required'}), 400

            url = data['url'].strip()
            if not url:
                return jsonify({'error': 'URL cannot be empty'}), 400

            try:
                # Generate unique task ID
                task_id = str(uuid.uuid4())

                logger.info(f"Starting URL scraping task: {task_id} for URL: {url}")

                # Initialize progress
                self.update_progress(task_id, 0, "Starting URL scraping...")

                # Start background processing
                def process_url():
                    try:
                        # Create a simple chat service for the web scraper
                        class SimpleChatService:
                            def __init__(self, openai_client):
                                self.openai_client = openai_client

                            def chat_model(self, prompt):
                                response = self.openai_client.chat.completions.create(
                                    model=os.getenv('CHAT_MODEL', 'gpt-4'),
                                    messages=[{"role": "user", "content": prompt}],
                                    max_completion_tokens=2000
                                )
                                return response.choices[0].message

                        chat_service = SimpleChatService(self.openai_client)

                        # Initialize web scraper
                        self.update_progress(task_id, 10, "Initializing web scraper...")
                        web_scraper = WebScraper(chat_service)

                        # Fetch content from URL
                        self.update_progress(task_id, 30, "Fetching content from URL...")
                        import asyncio
                        scraped_data = asyncio.run(web_scraper.fetch_page_content(url))

                        # Handle case where fetch_page_content returns string instead of dict
                        if isinstance(scraped_data, str):
                            content = scraped_data
                            title = 'Scraped Content'
                        elif isinstance(scraped_data, dict):
                            if not scraped_data or not scraped_data.get('content', '').strip():
                                self.update_progress(task_id, -1, "No content could be extracted from the URL")
                                return
                            content = scraped_data.get('content', '')
                            title = scraped_data.get('title', 'Scraped Content')
                        else:
                            self.update_progress(task_id, -1, "No content could be extracted from the URL")
                            return

                        # Create PDF from scraped content
                        self.update_progress(task_id, 60, "Creating PDF from scraped content...")

                        # Generate safe filename from URL
                        from urllib.parse import urlparse
                        parsed_url = urlparse(url)
                        domain = parsed_url.netloc or 'unknown'
                        safe_domain = re.sub(r'[^a-zA-Z0-9\-_]', '_', domain)
                        timestamp = int(time.time())
                        pdf_filename = f"scraped_{safe_domain}_{timestamp}.pdf"

                        # Create PDF content
                        pdf_content = self._create_web_scrape_pdf(url, title, content)

                        # Save PDF to downloads directory
                        self.update_progress(task_id, 80, "Saving PDF to downloads...")
                        downloads_dir = os.path.join(os.getcwd(), 'public', 'downloads')
                        os.makedirs(downloads_dir, exist_ok=True)

                        pdf_path = os.path.join(downloads_dir, pdf_filename)
                        self._save_pdf_file(pdf_content, pdf_path)

                        # Register for download
                        download_id = f"{task_id}_{pdf_filename}"
                        self.temp_downloads[download_id] = {
                            'filepath': pdf_path,
                            'filename': pdf_filename,
                            'created_at': time.time()
                        }

                        # Add to user documents
                        self.update_progress(task_id, 90, "Adding document to chatbot context...")

                        user_id = user.get('username') if user else 'anonymous'
                        if user_id not in self.user_documents:
                            self.user_documents[user_id] = []

                        # Add document to user's collection
                        self.user_documents[user_id].append({
                            'filename': pdf_filename,
                            'content': content,
                            'timestamp': datetime.now()
                        })

                        # Keep only the 5 most recent documents
                        if len(self.user_documents[user_id]) > 5:
                            self.user_documents[user_id] = self.user_documents[user_id][-5:]

                        logger.info(f"Scraped document stored for user {user_id}: {pdf_filename}")

                        # DEBUG: Log PDF file details before updating progress
                        logger.info(f"DEBUG - PDF file created: {pdf_path}")
                        logger.info(f"DEBUG - PDF file exists: {os.path.exists(pdf_path)}")
                        logger.info(f"DEBUG - PDF file size: {os.path.getsize(pdf_path) if os.path.exists(pdf_path) else 'N/A'} bytes")
                        logger.info(f"DEBUG - Download ID: {download_id}")
                        logger.info(f"DEBUG - temp_downloads registered: {download_id in self.temp_downloads}")

                        # Update progress with completion info
                        self.progress_data[task_id].update({
                            'filename': pdf_filename,
                            'download_id': download_id,
                            'download_filename': pdf_filename,
                            'completed': True
                        })

                        # DEBUG: Log progress data that will be sent to frontend
                        logger.info(f"DEBUG - Progress data for download trigger: {self.progress_data[task_id]}")

                        self.update_progress(task_id, 100, f"URL scraped successfully! PDF saved as {pdf_filename} and added to chatbot context.")

                    except Exception as e:
                        error_msg = f"Error processing URL: {str(e)}"
                        logger.error(error_msg)
                        self.update_progress(task_id, -1, error_msg)

                # Start processing in background thread
                thread = threading.Thread(target=process_url)
                thread.daemon = True
                thread.start()

                return jsonify({
                    'success': True,
                    'task_id': task_id,
                    'message': 'URL scraping started'
                })

            except Exception as e:
                logger.error(f"Error starting URL scraping: {e}")
                return jsonify({'error': 'Failed to start URL scraping'}), 500

        @self.app.route('/api/user-documents', methods=['GET'])
        @sso_token_required
        def get_user_documents():
            """Get all documents for the current user"""
            # DEV_MODE short-circuit removed: return real user documents only

            user = get_current_user()
            if not user:
                return jsonify({'error': 'User not authenticated'}), 401

            username = user.get('username')
            try:
                user_docs = self.user_documents.get(username, [])
                document_list = [doc['filename'] for doc in user_docs]

                return jsonify({
                    'success': True,
                    'documents': document_list,
                    'count': len(document_list)
                })

            except Exception as e:
                logger.error(f"Error getting user documents: {e}")
                return jsonify({'error': 'Failed to get user documents'}), 500

        @self.app.route('/logout')
        def logout():
            """Logout the user"""
            # Get current user before logout to clear their documents
            user = get_current_user()
            if user:
                username = user.get('username')
                if username and username in self.user_documents:
                    del self.user_documents[username]
                    logger.info(f'Cleared document memory for logged out user: {username}')

            client = get_sso_client()
            logout_user()
            return redirect(client.get_sso_logout_url())

        @self.app.route('/health')
        def health_check():
            """Health check endpoint"""
            return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

        # Serve favicon from root directory
        @self.app.route('/favicon.ico')
        def favicon():
            import os
            favicon_path = os.path.join(self.app.root_path, 'favicon.ico')
            logger.info(f'Favicon request - looking for: {favicon_path}')
            logger.info(f'File exists: {os.path.exists(favicon_path)}')
            logger.info(f'Root path: {self.app.root_path}')
            logger.info(f'Files in root: {os.listdir(self.app.root_path)}')
            return send_from_directory(self.app.root_path, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

        # Serve static files
        @self.app.route('/<path:filename>')
        def serve_static(filename):
            return send_from_directory('public', filename)

    def setup_socket_handlers(self):
        """Set up Socket.IO event handlers"""

        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            try:
                sid = request.sid
            except Exception:
                sid = 'unknown'
            logger.info(f'Client connected: {sid}')
            emit('connected', {'status': 'Connected to chatbot server'})

        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            try:
                sid = request.sid
            except Exception:
                sid = 'unknown'
            logger.info(f'Client disconnected: {sid}')

        @self.socketio.on('create-session')
        def handle_create_session(data):
            """Create a new chat session"""
            user_id = data.get('userId')
            username = data.get('username', 'Unknown')

            # Clear documents when browser is refreshed (new session created)
            if username in self.user_documents:
                del self.user_documents[username]
                logger.info(f'Cleared document memory for user on browser refresh: {username}')

            session_id = str(uuid.uuid4())
            join_room(session_id)

            logger.info(f'Session created: {session_id} for user: {username}')

            emit('session-created', {
                'sessionId': session_id,
                'userId': user_id,
                'username': username,
                'timestamp': datetime.now().isoformat()
            }, to=session_id)

        @self.socketio.on("user-message")
        @sso_token_required
        def handle_message(data):
            """Handle incoming chat messages with Google Custom Search integration and LLM prompt injection"""
            message = data.get('message', '')
            session_id = data.get('sessionId')
            user_id = data.get('userId')
            username = data.get('username', 'Unknown')
            current_time = data.get('currentTime')
            time_zone = data.get('timeZone')
            time_zone_offset = data.get('timeZoneOffset')
            local_time_string = data.get('localTimeString')

            # DEV_MODE session enforcement bypass and normalization
            try:
                # Print raw incoming payload for debugging as requested
                print("BACKEND RECEIVED:", data)
                print("DEV_MODE:", DEV_MODE)
            except Exception:
                pass

            if DEV_MODE != "dev":
                # Strict mode: require either camelCase or snake_case session id
                if not session_id and not data.get('session_id'):
                    logger.info('Missing session_id in incoming payload; rejecting message')
                    return
            else:
                # Dev mode: ensure a session_id is present for downstream logic
                data['session_id'] = data.get('session_id') or session_id or 'dev-session'
                session_id = data['session_id']

            # TRACE: Entry point for send-message handler
            try:
                frm = inspect.currentframe()
                logger.info(f"TRACE_STEP Enter handle_message - {inspect.getframeinfo(frm).lineno} - file:{__file__}")
            except Exception:
                logger.info('TRACE_STEP Enter handle_message')

            logger.info(f'Message from {username}: {message}')
            logger.info(f'User timezone: {time_zone}, offset: {time_zone_offset} minutes')

            logger.info('Emitting simplified user-message to connected client(s)')

            emit(
                "user-message",
                {
                "message": message,
                "username": username,
                "timestamp": datetime.now().isoformat()
                }, to=session_id)
            logger.info('Emitted simplified user-message to connected client(s)')

            # Echo the full incoming payload back to clients so frontend listeners
            # that expect the original data structure will always receive it.
            try:
                logger.info(f"Echoing full payload back to clients. Payload keys: {list(data.keys()) if isinstance(data, dict) else 'non-dict'}")
                self.socketio.emit("user-message", data, to=session_id)
                logger.info('Echoed full user-message successfully')
            except Exception as e:
                logger.error(f"Failed to echo full user-message: {e}")

            # TRACE: after emitting user-message
            try:
                frm = inspect.currentframe()
                logger.info(f"TRACE_STEP after_emit_user_message - {inspect.getframeinfo(frm).lineno}")
            except Exception:
                logger.info('TRACE_STEP after_emit_user_message')

            # Record user message into server-side conversation buffer so history_messages is populated
            try:
                conversation = self.conversations.setdefault(session_id, [])
                # keep username for PDF/export and context
                conversation.append({'role': 'user', 'content': message, 'username': username, 'timestamp': datetime.now().isoformat()})
                # enforce max history length to limit memory
                max_history_turns = int(os.getenv('CHAT_HISTORY_TURNS', '6'))
                if len(conversation) > max_history_turns * 2:
                    # keep only the most recent turns (user+assistant pairs)
                    self.conversations[session_id] = conversation[-(max_history_turns * 2):]
            except Exception:
                # non-fatal - do not break message handling if conversation buffer fails
                pass

            # Prepare time context for normal prompts only
            local_time_string = data.get('localTimeString')
            time_zone = data.get('timeZone')
            time_zone_offset = data.get('timeZoneOffset')
            time_context = f"Current user local time: {local_time_string} (timezone: {time_zone}, offset: {time_zone_offset} min). If the user asks for the current time, date, or anything time-related, use this as the present moment."

            # Prepare time context for normal prompts (unchanged)
            local_time_string = data.get('localTimeString')
            time_zone = data.get('timeZone')
            time_zone_offset = data.get('timeZoneOffset')
            time_context = (
                f"Current user local time: {local_time_string} (timezone: {time_zone}, offset: {time_zone_offset} min). "
                "If the user asks for the current time, date, or anything time-related, use this as the present moment."
            )

            # Build brief conversation history (chat buffer) to inject into helper LLM call and main LLM messages
            # Do not include the current user message here - it will be added as the final user turn
            conversation = self.conversations.setdefault(session_id, [])
            max_history_turns = int(os.getenv('CHAT_HISTORY_TURNS', '6'))
            history_slice = conversation[-max_history_turns:]
            history_messages = []
            for entry in history_slice:
                if entry.get('role') == 'user':
                    # use the raw content only for the LLM
                    history_messages.append({"role": "user", "content": entry.get('content', '')})
                else:
                    history_messages.append({"role": "assistant", "content": entry.get('content', '')})

            # Step 1: Ask the LLM to suggest a concise web search query based on user query + recent history.
            # This produces a focused search phrase used for the external auto-search step.
            suggested_query = None
            try:
                frm = inspect.currentframe()
                logger.info(f"TRACE_STEP before_helper_call - {inspect.getframeinfo(frm).lineno}")
                # Build a small prompt asking the assistant to return a short search query or keywords only.
                search_system = "You are a concise assistant that, when given a user's request and recent conversation history, returns a single short search query (no commentary). Respond with only the search query suitable for use with a web search API."
                # Reuse history_messages prepared earlier (if any)
                search_messages = [{"role": "system", "content": search_system}] + history_messages + [{"role": "user", "content": f"Generate a one-line search query for this user request: {message}"}]

                # Use a small token budget for this helper call
                helper_max_tokens = 64
                helper_model = os.getenv('CHAT_MODEL', 'gpt-4')
                helper_temperature = float(os.getenv('CHAT_TEMPERATURE', '0.2')) if not helper_model.lower().startswith('gpt-5') else 1.0

                helper_resp = self.openai_client.chat.completions.create(
                    model=helper_model,
                    messages=search_messages,
                    max_completion_tokens=helper_max_tokens,
                    temperature=helper_temperature
                )

                # Extract suggested query
                try:
                    helper_json = helper_resp.to_dict()
                except Exception:
                    helper_json = str(helper_resp)

                helper_text = self._extract_llm_message(helper_resp)
                try:
                    frm = inspect.currentframe()
                    logger.info(f"TRACE_STEP after_helper_call - {inspect.getframeinfo(frm).lineno}")
                except Exception:
                    logger.info('TRACE_STEP after_helper_call')
                if helper_text and isinstance(helper_text, str):
                    # Keep only the first line and strip whitespace
                    suggested_query = helper_text.splitlines()[0].strip()
            except Exception:
                try:
                    frm = inspect.currentframe()
                    logger.info(f"TRACE_STEP helper_call_exception - {inspect.getframeinfo(frm).lineno}")
                except Exception:
                    logger.info('TRACE_STEP helper_call_exception')
                # Non-fatal: fall back to using the raw user message
                suggested_query = None

            # Auto-search: attempt to fetch top results for the suggested query (fallback to the raw message)
            query_for_search = suggested_query if suggested_query else message
            search_results = self._auto_search_results(query_for_search)

            # Build the final prompt with time context and optional search results
            prompt_parts = [time_context]

            summary = None
            if search_results:
                # Create a compact, readable summary of top results
                summary_lines = []
                for idx, item in enumerate(search_results[:3]):
                    title = item.get('title', '')
                    snippet = item.get('snippet', '')
                    link = item.get('link', '')
                    summary_lines.append(f"{idx + 1}. {title} - {snippet} (URL: {link})")
                summary = "\n".join(summary_lines)
                prompt_parts.append("Top search results:\n" + summary)

            prompt_parts.append(f"User Query: {message}")

            # Inject user-uploaded documents into the prompt (if any).
            # Limit to a small number of most-recent documents and truncate to avoid blowing token budgets.
            docs_summary = None
            try:
                user_docs = []
                if username and username in self.user_documents:
                    user_docs = self.user_documents.get(username, [])
                else:
                    # Fallback: try to get current user documents via helper
                    user_docs = self._get_current_user_documents(username)

                if user_docs:
                    doc_lines = []
                    # Allow injecting up to 5 full documents by default (no truncation)
                    max_docs = int(os.getenv('MAX_DOCS_TO_INJECT', '5'))
                    # Use most recent documents first
                    for d in user_docs[-max_docs:][::-1]:
                        fname = d.get('filename', 'uploaded_document')
                        content = d.get('content', '') or ''
                        # Do not truncate documents by default; rely on large context window or env override
                        doc_lines.append(f"Filename: {fname}\n{content}")

                    docs_summary = "\n\n---\n\n".join(doc_lines)
                    # Insert documents summary as an additional context block after the time context
                    prompt_parts.insert(1, "User uploaded documents (most recent first):\n" + docs_summary)
            except Exception:
                # Non-fatal - do not block normal prompt flow if documents extraction fails
                docs_summary = None

            final_prompt = "\n\n".join(prompt_parts)

            logger.info(f"Final LLM prompt (auto-search): {final_prompt}")

            # TRACE: after auto-search
            try:
                frm = inspect.currentframe()
                logger.info(f"TRACE_STEP after_auto_search - {inspect.getframeinfo(frm).lineno} - query: {query_for_search}")
            except Exception:
                logger.info('TRACE_STEP after_auto_search')

            # We removed the previous intermediate LLM call (auto-search flow). Instead,
            # prepare the search summary so it can be injected into the final LLM prompt below.
            prompt_char_len = len(final_prompt or "")
            est_prompt_tokens = max(1, int(prompt_char_len / 4))  # rough estimate
            logger.info("Prompt length (auto-search): %d chars, est tokens: %d", prompt_char_len, est_prompt_tokens)

            # Build frontend payload with verification links from search_results so the final LLM can consume them
            search_results_payload = [
                {'title': r.get('title', ''), 'snippet': r.get('snippet', ''), 'link': r.get('link', '')}
                for r in search_results[:3]
            ]

            try:
                # Build the single final prompt: include time context, conversation history, and search summary
                try:
                    frm = inspect.currentframe()
                    logger.info(f"TRACE_STEP before_final_llm_call - {inspect.getframeinfo(frm).lineno}")
                except Exception:
                    logger.info('TRACE_STEP before_final_llm_call')
                system_msg = os.getenv('CHAT_SYSTEM_PROMPT', "You are a concise, helpful assistant. Answer the user's question directly and do not reveal internal chain-of-thought.")
                # Compose messages: system prompt, conversation history, search results (as system context), then the user's query
                messages = [{"role": "system", "content": system_msg}]
                # Inject conversation history (if any)
                messages += history_messages
                # Inject search summary as a system-level context so the final assistant can use it
                if summary:
                    messages += [{"role": "system", "content": "Top search results:\n" + summary}]

                # Inject user-uploaded documents as system-level context if available
                try:
                    if docs_summary:
                        # Instruct the model to treat these documents as "pages in hand".
                        # Encourage the model to freely reference, quote, and discuss the uploaded
                        # documents when relevant to the user's query. Prefer using the uploaded
                        # documents' content over external sources when they are applicable.
                        doc_system_instructions = (
                            "You have the user's uploaded documents available as pages in hand. "
                            "When answering, you should freely reference, quote verbatim when useful, "
                            "and discuss the content of these documents. Prefer using these uploaded "
                            "documents as primary evidence for answers when they are relevant. "
                            "If quoting, indicate the filename and short excerpt. Do not reveal internal "
                            "reasoning. Be concise, factual, and cite the uploaded document where you "
                            "derive answers.\n\n" + docs_summary
                        )
                        messages += [{"role": "system", "content": doc_system_instructions}]
                except Exception:
                    # Non-fatal - continue without document injection
                    pass
                # Final user turn contains the user's query and time context
                user_prompt = f"{time_context}\n\nUser Query: {message}"
                messages += [{"role": "user", "content": user_prompt}]

                # Log a single, combined final prompt for debugging/traceability
                try:
                    debug_preview = user_prompt + ("\n\nTop search results:\n" + summary if summary else "")
                    logger.info(f"Final LLM prompt: {debug_preview}")
                except Exception:
                    pass

                max_tokens = int(os.getenv('MAX_COMPLETION_TOKENS', '2000'))
                model_name = os.getenv('CHAT_MODEL', 'gpt-4')
                # Force temperature=1.0 for gpt-5 family as required
                if model_name.lower().startswith('gpt-5'):
                    temperature = 1.0
                else:
                    temperature = float(os.getenv('CHAT_TEMPERATURE', '0.2'))

                # DEBUG: Dump final LLM call payload for troubleshooting
                try:
                    # Ensure variable `model` exists for the exact debug payload shape requested
                    model = model_name
                    print("FINAL_LLM_CALL_PAYLOAD_START")
                    print(json.dumps({
                        "model": model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    }, indent=2))
                    print("FINAL_LLM_CALL_PAYLOAD_END")
                except Exception as _e:
                    # Avoid crashing the handler if debug printing fails
                    logger.error(f"Failed to print final LLM payload: {_e}")

                max_tokens = int(os.getenv('MAX_COMPLETION_TOKENS', '2000'))
                model_name = os.getenv('CHAT_MODEL', 'gpt-4')
                if model_name.lower().startswith('gpt-5'):
                    temperature = 1.0
                else:
                    temperature = float(os.getenv('CHAT_TEMPERATURE', '0.2'))

                # DEBUG: dump final payload (optional)
                try:
                    model = model_name
                    logger.info("FINAL_LLM_CALL_PAYLOAD_START")
                    logger.info(json.dumps({
                        "model": model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    }, indent=2))
                    logger.info("FINAL_LLM_CALL_PAYLOAD_END")
                except Exception as _e:
                    logger.error(f"Failed to print final LLM payload: {_e}")

                # Robust LLM call with retries and correct param names
                attempts = 3
                last_err = None
                for i in range(attempts):
                    try:
                        response = self.openai_client.chat.completions.create(
                            model=model_name,
                            messages=messages,
                            max_tokens=max_tokens,
                            temperature=temperature,
                            timeout=30
                        )
                        last_err = None
                        break
                    except Exception as e:
                        last_err = e
                        logger.error(f"LLM call attempt {i+1}/{attempts} failed: {e}", exc_info=True)
                        time.sleep(2)

                if last_err is not None:
                    # Re-raise so outer handler will catch and emit an error to clients
                    raise last_err

                logger.info(f"LLM raw response: {response}")
                try:
                    frm = inspect.currentframe()
                    logger.info(f"TRACE_STEP after_final_llm_call - {inspect.getframeinfo(frm).lineno}")
                except Exception:
                    logger.info('TRACE_STEP after_final_llm_call')
                try:
                    raw_json = response.to_dict()
                except Exception:
                    raw_json = str(response)
                logger.debug("LLM full response JSON (normal prompt): %s", json.dumps(raw_json, default=str))

                llm_message = self._extract_llm_message(response)
                try:
                    fr = raw_json.get('choices', [])[0].get('finish_reason') if isinstance(raw_json, dict) else None
                    td = raw_json.get('usage', {}).get('completion_tokens_details') if isinstance(raw_json, dict) else None
                    logger.info("LLM finish_reason (normal): %s, completion_tokens_details: %s", fr, td)
                except Exception:
                    pass

                if not llm_message or not str(llm_message).strip():
                    logger.warning("LLM returned empty assistant content for normal prompt; using search-results fallback")
                    fallback_lines = []
                    for i, r in enumerate(search_results[:3]):
                        fallback_lines.append(f"{i+1}. {r.get('title','')} - {r.get('snippet','')} (URL: {r.get('link','')})")
                    fallback_text = "I couldn't generate a reply right now. Here are some useful search results I found:\n" + "\n".join(fallback_lines)
                    llm_message = fallback_text

                logger.info(f"LLM extracted message: {llm_message}")
                # Normalize bot-response payload to match user-message schema
                botPayload = {
                    'type': 'bot-response',
                    'sessionId': session_id,
                    'userId': None,
                    'messageId': str(uuid.uuid4()),
                    'username': 'assistant',
                    'text': llm_message,
                    'timestamp': datetime.now().isoformat(),
                    'searchResults': search_results if isinstance(search_results, list) else [],
                    'metadata': {
                        'llm_raw': raw_json
                    }
                }

                emit("bot-response", botPayload, to=session_id)

                # TRACE: after emitting bot-response
                try:
                    frm = inspect.currentframe()
                    logger.info(f"TRACE_STEP after_emit_bot_response - {inspect.getframeinfo(frm).lineno}")
                except Exception:
                    logger.info('TRACE_STEP after_emit_bot_response')
            except Exception as e:
                logger.error(f'LLM error: {e}', exc_info=True)
                emit('error', {
                    'message': 'Sorry, there was an error generating a response.',
                    'timestamp': datetime.now().isoformat()
                }, to=session_id)
            return

        @self.socketio.on('file-upload')
        def handle_file_upload(data):
            """Handle file upload via socket"""
            filename = data.get('filename')
            user_id = data.get('userId')
            session_id = data.get('sessionId')

            logger.info(f'File upload: {filename} from user: {user_id}')

            emit('file-processed', {
                'filename': filename,
                'message': f'File {filename} processed successfully',
                'timestamp': datetime.now().isoformat()
            }, to=session_id)


        @self.socketio.on('export-pdf')
        def handle_export_pdf(data):
            """Handle PDF export request"""
            session_id = data.get('sessionId')

            # Enforce session_id unless DEV_MODE is 'dev'
            if DEV_MODE != "dev":
                if not session_id and not data.get('session_id'):
                    emit('error', {
                        'message': 'No session ID provided for export',
                        'timestamp': datetime.now().isoformat()
                    }, to=session_id)
                    return
            else:
                data['session_id'] = data.get('session_id') or session_id or 'dev-session'
                session_id = data['session_id']

            try:
                user_id = 'anonymous'  # Default fallback
                try:
                    current_user = get_current_user()
                    if current_user:
                        user_id = current_user.get('sub', 'anonymous')
                except:
                    pass  # Use default fallback

                logger.info(f'PDF export request from user: {user_id}, session: {session_id}')

                # Get conversation history for this session
                if session_id in self.conversations and self.conversations[session_id]:
                    conversation = self.conversations[session_id]

                    # Generate PDF content from existing conversation history
                    pdf_content = self._generate_pdf_content(self.conversations[session_id])

                    # Create temporary PDF file
                    pdf_filename = f"chat_export_{session_id}_{int(time.time())}.pdf"
                    pdf_path = os.path.join(tempfile.gettempdir(), pdf_filename)

                    # Save PDF to temporary file
                    self._save_pdf_file(pdf_content, pdf_path)

                    # Create download URL
                    download_id = str(uuid.uuid4())
                    self.temp_downloads[download_id] = {
                        'filepath': pdf_path,
                        'filename': pdf_filename,
                        'created_at': time.time()
                    }

                    download_url = f'/download/{download_id}'

                    emit('pdf-ready', {
                        'url': download_url,
                        'filename': pdf_filename
                    }, to=session_id)

                else:
                    emit('error', {
                        'message': 'No conversation found for export',
                        'timestamp': datetime.now().isoformat()
                    }, to=session_id)

            except Exception as e:
                logger.error(f'Error exporting PDF: {e}')
                emit('error', {
                    'message': 'Failed to export chat to PDF',
                    'timestamp': datetime.now().isoformat()
                }, to=session_id)

    def process_uploaded_file(self, file_path: str, filename: str) -> str:
        """Process uploaded file and extract content"""
        try:
            file_extension = os.path.splitext(filename)[1].lower().lstrip('.')
            logger.info(f"Processing file: {filename} (type: {file_extension})")

            if file_extension == 'txt':
                return self._process_text_file(file_path)
            elif file_extension == 'pdf':
                return self._process_pdf_file(file_path)
            elif file_extension in ['doc', 'docx']:
                return self._process_docx_file(file_path)
            elif file_extension == 'rtf':
                return self._process_rtf_file(file_path)
            elif file_extension in ['jpg', 'jpeg', 'png', 'bmp']:
                return self._process_image_file(file_path)
            else:
                return f"File type '{file_extension}' is supported but processing not yet implemented."

        except Exception as e:
            logger.error(f"Error processing file {filename}: {e}")
            return f"Error processing file: {str(e)}"

    def process_uploaded_file_with_progress(self, file_path: str, filename: str, task_id: str) -> str:
        """Process uploaded file and extract content with progress updates"""
        try:
            file_extension = os.path.splitext(filename)[1].lower().lstrip('.')
            logger.info(f"Processing file: {filename} (type: {file_extension})")

            self.update_progress(task_id, 20, f"Processing {file_extension.upper()} file...")

            if file_extension == 'txt':
                content = self._process_text_file(file_path)
            elif file_extension == 'pdf':
                content = self._process_pdf_file_with_progress(file_path, task_id)
            elif file_extension in ['doc', 'docx']:
                content = self._process_docx_file(file_path)
            elif file_extension == 'rtf':
                content = self._process_rtf_file(file_path)
            elif file_extension in ['jpg', 'jpeg', 'png', 'bmp']:
                content = self._process_image_file(file_path)
            else:
                content = f"File type '{file_extension}' is supported but processing not yet implemented."

            self.update_progress(task_id, 95, f"File processing completed! Extracted {len(content)} characters")
            return content

        except Exception as e:
            logger.error(f"Error processing file {filename}: {e}")
            self.update_progress(task_id, -1, f"Error processing file: {str(e)}")
            return f"Error processing file: {str(e)}"

    def _process_text_file(self, file_path: str) -> str:
        """Process text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()

    def _process_pdf_file(self, file_path: str) -> str:
        """Process PDF file with OCR fallback using chunking strategy"""
        try:
            import PyPDF2
            import tempfile
            import os

            content = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    content += page.extract_text() + "\n"

            content = content.strip()

            # If very little content extracted, perform OCR using chunking strategy
            if len(content) < 50:
                logger.info(f"PDF appears to be image-based ({len(content)} characters extracted). Attempting OCR...")
                return self._perform_chunked_ocr_on_pdf(file_path)

            return content
        except ImportError:
            return "PDF processing requires PyPDF2 library. Please install it."
        except Exception as e:
            return f"Error processing PDF: {str(e)}"

    def _process_pdf_file_with_progress(self, file_path: str, task_id: str) -> str:
        """Process PDF file with OCR fallback using chunking strategy and progress updates"""
        try:
            import PyPDF2
            import tempfile
            import os

            self.update_progress(task_id, 30, "Reading PDF content...")

            content = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    content += page.extract_text() + "\n"

            content = content.strip()

            self.update_progress(task_id, 50, f"Extracted {len(content)} characters from PDF...")

            # If very little content extracted, perform OCR using chunking strategy
            if len(content) < 50:
                self.update_progress(task_id, 60, "PDF appears to be image-based. Starting OCR processing...")
                logger.info(f"PDF appears to be image-based ({len(content)} characters extracted). Attempting OCR...")
                return self._perform_chunked_ocr_on_pdf_with_progress(file_path, task_id)

            return content
        except ImportError:
            return "PDF processing requires PyPDF2 library. Please install it."

    def _perform_chunked_ocr_on_pdf(self, input_path: str) -> str:
        """Perform OCR on PDF using chunking strategy for large documents"""
        try:
            import PyPDF2
            import tempfile
            import os
            import ocrmypdf

            logger.info(f"Starting chunked OCR processing: {input_path}")

            # Read the input PDF to get page count
            with open(input_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                total_pages = len(pdf_reader.pages)

            logger.info(f"PDF has {total_pages} pages - processing in chunks")

            # Determine chunk size based on document size
            if total_pages > 50:
                chunk_size = 1  # Single page chunks for large documents
            elif total_pages > 20:
                chunk_size = 2  # 2 pages per chunk for medium documents
            else:
                chunk_size = min(5, total_pages)  # Up to 5 pages for small documents

            # Calculate number of chunks
            num_chunks = (total_pages + chunk_size - 1) // chunk_size
            logger.info(f"Using chunk size: {chunk_size} pages per chunk, {num_chunks} total chunks")

            # Process pages in chunks
            processed_pdfs = []
            chunk_number = 1

            for chunk_start in range(0, total_pages, chunk_size):
                chunk_end = min(chunk_start + chunk_size, total_pages)

                logger.info(f"Processing chunk {chunk_number}/{num_chunks}: pages {chunk_start + 1}-{chunk_end}")

                # Create temporary file for this chunk
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_chunk:
                    temp_chunk_path = temp_chunk.name

                # Extract pages for this chunk
                with open(input_path, 'rb') as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    pdf_writer = PyPDF2.PdfWriter()

                    for page_num in range(chunk_start, chunk_end):
                        pdf_writer.add_page(pdf_reader.pages[page_num])

                    with open(temp_chunk_path, 'wb') as chunk_file:
                        pdf_writer.write(chunk_file)

                # Process this chunk with OCR
                with tempfile.NamedTemporaryFile(suffix='_ocr.pdf', delete=False) as temp_ocr:
                    temp_ocr_path = temp_ocr.name

                try:
                    # Perform OCR on this chunk
                    ocrmypdf.ocr(
                        input_file=temp_chunk_path,
                        output_file=temp_ocr_path,
                        force_ocr=True,
                        deskew=True,
                        progress_bar=False,
                        optimize=1
                    )

                    # Verify OCR overlay was created successfully
                    ocr_verified, verify_message = self._verify_ocr_overlay(temp_ocr_path)
                    if ocr_verified:
                        processed_pdfs.append(temp_ocr_path)
                        logger.info(f"OCR completed and verified for chunk {chunk_number}: {verify_message}")
                    else:
                        logger.warning(f"OCR verification failed for chunk {chunk_number}: {verify_message}")
                        # Use original chunk if OCR verification fails
                        processed_pdfs.append(temp_chunk_path)

                except Exception as chunk_error:
                    logger.warning(f"Error processing chunk {chunk_number}: {chunk_error}")
                    # Use original chunk if OCR fails
                    processed_pdfs.append(temp_chunk_path)

                finally:
                    # Clean up temporary chunk file if it's different from what we're keeping
                    if temp_chunk_path != processed_pdfs[-1]:
                        try:
                            os.unlink(temp_chunk_path)
                        except:
                            pass

                chunk_number += 1

            logger.info("Merging processed chunks and extracting text...")

            # Extract text from all processed chunks (OCR-processed PDFs with text overlay)
            final_content = ""
            for processed_pdf in processed_pdfs:
                try:
                    with open(processed_pdf, 'rb') as file:
                        pdf_reader = PyPDF2.PdfReader(file)
                        for page_num in range(len(pdf_reader.pages)):
                            page = pdf_reader.pages[page_num]
                            final_content += page.extract_text() + "\n"

                    # Clean up temporary file
                    os.unlink(processed_pdf)
                except Exception as e:
                    logger.warning(f"Error extracting text from processed chunk: {e}")

            final_content = final_content.strip()

            # Verify that OCR-processed content is being used for context
            logger.info(f"OCR processing complete - final content extracted from OCR-processed PDFs: {len(final_content)} characters")

            # Final verification of OCR results
            if len(final_content) < 50:
                return f"OCR processing completed but extracted minimal text ({len(final_content)} characters). The document may contain complex layouts, poor image quality, or OCR overlay may not have been created properly."

            # Count meaningful words as additional validation
            words = final_content.split()
            if len(words) < 10:
                return f"OCR processing completed but extracted limited content ({len(words)} words, {len(final_content)} characters). The OCR overlay may be incomplete or the document may have complex formatting."

            logger.info(f"OCR processing successful - extracted {len(final_content)} characters, {len(words)} words with verified OCR overlay")
            return final_content

        except ImportError as e:
            return f"OCR processing requires additional libraries: {str(e)}"
        except Exception as e:
            logger.error(f"Error during OCR processing: {e}")
            return f"Error during OCR processing: {str(e)}"

    def _verify_ocr_overlay(self, pdf_path: str) -> tuple[bool, str]:
        """Verify that a PDF contains OCR overlay (searchable text)"""
        try:
            import PyPDF2

            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_text = ""

                # Extract text from all pages
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text().strip()
                    total_text += page_text

                total_text = total_text.strip()

                # Check if we have meaningful text content
                if len(total_text) < 10:
                    return False, f"No OCR overlay detected - only {len(total_text)} characters found"

                # Additional validation: check for readable words
                words = total_text.split()
                if len(words) < 5:
                    return False, f"OCR overlay appears incomplete - only {len(words)} words found"

                return True, f"OCR overlay verified - {len(total_text)} characters, {len(words)} words"

        except Exception as e:
            return False, f"Error verifying OCR overlay: {str(e)}"

    def _auto_search_results(self, query: str) -> list:
        """
        Attempt an automatic Google Custom Search for the given query.
        Returns a list of result dicts with keys: title, snippet, link.
        If ENABLE_AUTO_SEARCH is false or an error occurs, returns an empty list.
        """
        results = []
        try:
            if os.getenv('ENABLE_AUTO_SEARCH', 'true').lower() in ('1', 'true', 'yes', 'on'):
                import google_search_utils
                raw = google_search_utils.google_search(query, num_results=3) or []
                # Normalize items to ensure consistent keys
                for item in raw:
                    item['title'] = item.get('title', '')
                    item['snippet'] = item.get('snippet', '')
                    link = item.get('link') or item.get('url') or item.get('href') or ''
                    item['link'] = link
                results = raw
                if results:
                    logger.info(f"Auto-search found {len(results)} result(s) for query: {query}")
        except Exception as e:
            # Do not crash user flow if search fails
            logger.warning(f"Auto-search failed for query '{query}': {e}", exc_info=True)
            results = []
        return results

    def _extract_llm_message(self, response) -> str:
        """
        Robustly extract assistant text from different response shapes.
        Tries (in order): choices[0].message.content, choices[0].text,
        function_call (formatted), delta/content fragments, or fall back to empty string.
        """
        try:
            # Prefer working with a dict form when possible for safety
            try:
                resp = response.to_dict()
            except Exception:
                resp = response

            # If dict-like, inspect keys consistently
            if isinstance(resp, dict):
                choices = resp.get('choices') or []
                if choices:
                    c = choices[0]
                    # message may be dict or string
                    msg = c.get('message') or {}
                    if isinstance(msg, dict):
                        content = msg.get('content')
                        if content and str(content).strip():
                            return content

                        # function_call present -> format for user
                        fc = msg.get('function_call') or c.get('function_call')
                        if fc:
                            name = fc.get('name')
                            args = fc.get('arguments')
                            try:
                                args_str = json.dumps(args, ensure_ascii=False)
                            except Exception:
                                args_str = str(args)
                            return f"[function_call] {name}({args_str})"

                        # fallback to text field
                        if c.get('text') and str(c.get('text')).strip():
                            return c.get('text')

                        # delta fragments or other nested shapes
                        delta = c.get('delta') or msg.get('delta')
                        if isinstance(delta, dict):
                            # try common delta content locations
                            for k in ('content', 'text', 'message'):
                                if delta.get(k):
                                    if str(delta.get(k)).strip():
                                        return delta.get(k)

                    elif isinstance(msg, str) and msg.strip():
                        return msg

            # If response is an SDK object, try attribute access
            try:
                if hasattr(response, 'choices') and response.choices:
                    ch = response.choices[0]
                    # message object
                    if getattr(ch, 'message', None) is not None:
                        content = getattr(ch.message, 'content', None)
                        if content and str(content).strip():
                            return content
                        # function_call on message
                        fc = getattr(ch.message, 'function_call', None)
                        if fc:
                            name = getattr(fc, 'name', None)
                            args = getattr(fc, 'arguments', None)
                            try:
                                args_str = json.dumps(args, ensure_ascii=False)
                            except Exception:
                                args_str = str(args)
                            return f"[function_call] {name}({args_str})"

                    # plain text fallback
                    if getattr(ch, 'text', None):
                        return ch.text
            except Exception:
                pass
        except Exception:
            pass

        return ''

    def _perform_chunked_ocr_on_pdf_with_progress(self, input_path: str, task_id: str) -> str:
        """Perform OCR on PDF using chunking strategy with progress updates - based on working OCR app"""
        try:
            import PyPDF2
            import tempfile
            import os
            import ocrmypdf

            self.update_progress(task_id, 65, "Starting OCR processing...")

            logger.info(f"Starting chunked OCR processing: {input_path}")

            # Read the input PDF to get page count
            with open(input_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                total_pages = len(pdf_reader.pages)

            logger.info(f"PDF has {total_pages} pages - processing in chunks")

            self.update_progress(task_id, 70, f"Analyzing PDF: {total_pages} pages found")

            # Determine chunk size based on document size
            if total_pages > 50:
                chunk_size = 1  # Single page chunks for large documents
            elif total_pages > 20:
                chunk_size = 2  # 2 pages per chunk for medium documents
            else:
                chunk_size = min(5, total_pages)  # Up to 5 pages for small documents

            # Calculate number of chunks
            num_chunks = (total_pages + chunk_size - 1) // chunk_size
            logger.info(f"Using chunk size: {chunk_size} pages per chunk, {num_chunks} total chunks")

            self.update_progress(task_id, 75, f"Processing {num_chunks} chunks ({chunk_size} pages each)")

            # Process pages in chunks
            processed_pdfs = []
            chunk_number = 1

            for chunk_start in range(0, total_pages, chunk_size):
                chunk_end = min(chunk_start + chunk_size, total_pages)

                progress_percent = 75 + int((chunk_number - 1) / num_chunks * 20)  # 75-95% for processing

                self.update_progress(task_id, progress_percent, f"Processing chunk {chunk_number}/{num_chunks}: pages {chunk_start + 1}-{chunk_end}")

                logger.info(f"Processing chunk {chunk_number}/{num_chunks}: pages {chunk_start + 1}-{chunk_end}")

                # Create temporary file for this chunk
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_chunk:
                    temp_chunk_path = temp_chunk.name

                # Extract pages for this chunk
                with open(input_path, 'rb') as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    pdf_writer = PyPDF2.PdfWriter()

                    for page_num in range(chunk_start, chunk_end):
                        pdf_writer.add_page(pdf_reader.pages[page_num])

                    with open(temp_chunk_path, 'wb') as chunk_file:
                        pdf_writer.write(chunk_file)

                # Process this chunk with OCR
                with tempfile.NamedTemporaryFile(suffix='_ocr.pdf', delete=False) as temp_ocr:
                    temp_ocr_path = temp_ocr.name

                try:
                    # Perform OCR on this chunk
                    ocrmypdf.ocr(
                        input_file=temp_chunk_path,
                        output_file=temp_ocr_path,
                        force_ocr=True,
                        deskew=True,
                        progress_bar=False,
                        optimize=1
                    )

                    # Verify OCR overlay was created successfully
                    ocr_verified, verify_message = self._verify_ocr_overlay(temp_ocr_path)
                    if ocr_verified:
                        processed_pdfs.append(temp_ocr_path)
                        logger.info(f"OCR completed and verified for chunk {chunk_number}: {verify_message}")
                    else:
                        logger.warning(f"OCR verification failed for chunk {chunk_number}: {verify_message}")
                        # Use original chunk if OCR verification fails
                        processed_pdfs.append(temp_chunk_path)

                except Exception as chunk_error:
                    logger.warning(f"Error processing chunk {chunk_number}: {chunk_error}")
                    # Use original chunk if OCR fails
                    processed_pdfs.append(temp_chunk_path)

                finally:
                    # Clean up temporary chunk file if it's different from what we're keeping
                    if temp_chunk_path != processed_pdfs[-1]:
                        try:
                            os.unlink(temp_chunk_path)
                        except:
                            pass

                chunk_number += 1

            self.update_progress(task_id, 95, "Merging processed chunks and extracting text...")

            logger.info("Merging processed chunks and extracting text...")

            # Create merged OCR PDF for download and extract text
            download_dir = os.path.join(os.path.dirname(__file__), 'downloads')
            os.makedirs(download_dir, exist_ok=True)

            # Generate download filename
            download_id = task_id
            original_filename = os.path.basename(input_path)
            base_name = os.path.splitext(original_filename)[0]
            download_filename = f"{download_id}_{base_name}.ocr.pdf"
            download_path = os.path.join(download_dir, download_filename)

            # Merge all OCR-processed PDFs into one file
            final_content = ""
            try:
                from PyPDF2 import PdfWriter
                pdf_writer = PdfWriter()

                for processed_pdf in processed_pdfs:
                    try:
                        with open(processed_pdf, 'rb') as file:
                            pdf_reader = PyPDF2.PdfReader(file)
                            # Add pages to merged PDF
                            for page_num in range(len(pdf_reader.pages)):
                                page = pdf_reader.pages[page_num]
                                pdf_writer.add_page(page)
                                # Extract text for content
                                final_content += page.extract_text() + "\n"
                    except Exception as e:
                        logger.warning(f"Error processing chunk for merge: {e}")

                # Save merged OCR PDF
                with open(download_path, 'wb') as output_file:
                    pdf_writer.write(output_file)

                logger.info(f"Saved merged OCR PDF: {download_path}")

                # Store download_id in progress data for frontend
                self.progress_data[task_id].update({
                    'download_id': download_id,
                    'download_filename': f"{base_name}.ocr.pdf"
                })

            except Exception as e:
                logger.warning(f"Error creating merged PDF: {e}")
                # Continue with text extraction even if merge fails
                for processed_pdf in processed_pdfs:
                    try:
                        with open(processed_pdf, 'rb') as file:
                            pdf_reader = PyPDF2.PdfReader(file)
                            for page_num in range(len(pdf_reader.pages)):
                                page = pdf_reader.pages[page_num]
                                final_content += page.extract_text() + "\n"
                    except Exception as extract_error:
                        logger.warning(f"Error extracting text from processed chunk: {extract_error}")

            # Clean up temporary chunk files
            for processed_pdf in processed_pdfs:
                try:
                    os.unlink(processed_pdf)
                except:
                    pass

            final_content = final_content.strip()

            # Verify that OCR-processed content is being used for context
            logger.info(f"OCR processing complete - final content extracted from OCR-processed PDFs: {len(final_content)} characters")

            # Final verification of OCR results
            if len(final_content) < 50:
                return f"OCR processing completed but extracted minimal text ({len(final_content)} characters). The document may contain complex layouts, poor image quality, or OCR overlay may not have been created properly."

            # Count meaningful words as additional validation
            words = final_content.split()
            if len(words) < 10:
                return f"OCR processing completed but extracted limited content ({len(words)} words, {len(final_content)} characters). The OCR overlay may be incomplete or the document may have complex formatting."

            logger.info(f"OCR processing successful - extracted {len(final_content)} characters, {len(words)} words with verified OCR overlay")
            return final_content

        except ImportError as e:
            return f"OCR processing requires additional libraries: {str(e)}"
        except Exception as e:
            logger.error(f"Error during OCR processing: {e}")
            return f"Error during OCR processing: {str(e)}"

    def _process_docx_file(self, file_path: str) -> str:
        """Process DOCX file"""
        try:
            import docx
            doc = docx.Document(file_path)
            content = ""
            for paragraph in doc.paragraphs:
                content += paragraph.text + "\n"
            return content.strip()
        except ImportError:
            return "DOCX processing requires python-docx library. Please install it."
        except Exception as e:
            return f"Error processing DOCX: {str(e)}"

    def _process_rtf_file(self, file_path: str) -> str:
        """Process RTF file"""
        try:
            from striprtf.striprtf import rtf_to_text
            with open(file_path, 'r', encoding='utf-8') as f:
                rtf_content = f.read()
            return rtf_to_text(rtf_content)
        except ImportError:
            return "RTF processing requires striprtf library. Please install it."
        except Exception as e:
            return f"Error processing RTF: {str(e)}"

    def _process_image_file(self, file_path: str) -> str:
        """Process image file using OCR"""
        try:
            import pytesseract
            from PIL import Image

            logger.info(f"Performing OCR on image file: {file_path}")

            # Open and process the image
            image = Image.open(file_path)

            # Perform OCR
            extracted_text = pytesseract.image_to_string(image)
            extracted_text = extracted_text.strip()

            if len(extracted_text) < 10:
                return f"Image processed but minimal text extracted ({len(extracted_text)} characters). The image may not contain readable text or may have poor quality."

            logger.info(f"OCR successful - extracted {len(extracted_text)} characters from image")
            return extracted_text

        except ImportError as e:
            return f"Image OCR processing requires additional libraries: {str(e)}"
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return f"Error processing image: {str(e)}"

    def _generate_pdf_content(self, conversation):
        """Generate PDF content from conversation history"""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib.colors import blue, black
            from io import BytesIO

            # Create a BytesIO buffer to hold the PDF
            buffer = BytesIO()

            # Create PDF document
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()

            # Custom styles for text message conversation layout
            user_style = ParagraphStyle(
                'UserMessage',
                parent=styles['Normal'],
                leftIndent=2*inch,  # Right-justify user messages by adding left indent
                rightIndent=0.2*inch,
                spaceAfter=8,
                spaceBefore=4,
                textColor=blue,
                alignment=2,  # Right alignment
                fontSize=10,
                fontName='Helvetica'
            )

            assistant_style = ParagraphStyle(
                'AssistantMessage',
                parent=styles['Normal'],
                leftIndent=0.2*inch,  # Left-justify AI responses with minimal indent
                rightIndent=2*inch,  # Add right margin to keep messages from going too wide
                spaceAfter=8,
                spaceBefore=4,
                textColor=black,
                alignment=0,  # Left alignment
                fontSize=10,
                fontName='Helvetica'
            )

            # Build the content
            content = []
            content.append(Paragraph("Chat History Export", styles['Title']))
            content.append(Spacer(1, 0.2*inch))
            content.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
            content.append(Spacer(1, 0.3*inch))

            # Add conversation messages in text message format
            for msg in conversation:
                if msg['role'] == 'user':
                    username = msg.get('username', 'User')
                    # Clean up content for PDF display
                    clean_content = self._clean_content_for_pdf(msg['content'])
                    # Format as right-aligned user message bubble
                    content.append(Paragraph(f"<b>{username}:</b><br/>{clean_content}", user_style))
                elif msg['role'] == 'assistant':
                    # Clean up content for PDF display
                    clean_content = self._clean_content_for_pdf(msg['content'])
                    # Format as left-aligned assistant message bubble
                    content.append(Paragraph(f"<b>Assistant:</b><br/>{clean_content}", assistant_style))
                content.append(Spacer(1, 0.05*inch))  # Smaller spacing between messages

            # Build PDF
            doc.build(content)
            buffer.seek(0)
            return buffer.getvalue()

        except ImportError:
            # Fallback to simple text format if reportlab is not available
            content = "Chat History Export\n"
            content += "=" * 50 + "\n\n"
            content += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

            for msg in conversation:
                if msg['role'] == 'user':
                    username = msg.get('username', 'User')
                    content += f"{username}: {msg['content']}\n\n"
                elif msg['role'] == 'assistant':
                    content += f"Assistant: {msg['content']}\n\n"

            return content.encode('utf-8')

        except Exception as e:
            logger.error(f"Error generating PDF content: {e}")
            # Return simple text fallback
            content = f"Error generating PDF: {str(e)}\n\nConversation data:\n"
            for msg in conversation:
                content += f"{msg['role']}: {msg['content']}\n\n"
            return content.encode('utf-8')

    def _clean_content_for_pdf(self, content):
        """Clean markdown/HTML content for PDF display"""
        import re

        # Remove markdown links and keep just the text
        content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)

        # Remove markdown bold/italic markers
        content = re.sub(r'\*\*([^\*]+)\*\*', r'\1', content)  # **bold**
        content = re.sub(r'\*([^\*]+)\*', r'\1', content)      # *italic*
        content = re.sub(r'__([^_]+)__', r'\1', content)       # __bold__
        content = re.sub(r'_([^_]+)_', r'\1', content)         # _italic_

        # Remove code block markers
        content = re.sub(r'```[^\n]*\n', '', content)  # Opening ```
        content = re.sub(r'```', '', content)          # Closing ```
        content = re.sub(r'`([^`]+)`', r'\1', content) # Inline code

        # Remove HTML elements (including download links)
        content = re.sub(r'<[^>]+>', '', content)

        # Remove headers
        content = re.sub(r'^#{1,6}\s*', '', content, flags=re.MULTILINE)

        # Clean up extra whitespace
        content = re.sub(r'\n\s*\n', '\n\n', content)  # Multiple newlines to double
        content = content.strip()

        # Escape special characters for ReportLab
        content = content.replace('&', '&amp;')
        content = content.replace('<', '&lt;')
        content = content.replace('>', '&gt;')

        return content

    def _create_web_scrape_pdf(self, url, title, content):
        """Create PDF content from scraped web content"""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib.colors import blue, black
            from io import BytesIO




            # Create a BytesIO buffer to hold the PDF
            buffer = BytesIO()

            # Create PDF document
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()

            # Custom styles for web content
            title_style = ParagraphStyle(
                'WebTitle',
                parent=styles['Title'],
                fontSize=16,
                spaceAfter=12,
                textColor=blue,
                alignment=1  # Center alignment
            )

            url_style = ParagraphStyle(
                'SourceUrl',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=16,
                textColor=blue,
                alignment=1  # Center alignment
            )

            content_style = ParagraphStyle(
                'WebContent',
                parent=styles['Normal'],
                fontSize=11,
                spaceAfter=6,
                spaceBefore=3,
                leftIndent=0.2*inch,
                rightIndent=0.2*inch,
                alignment=0  # Left alignment
            )

            # Build PDF content
            story = []

            # Add title
            if title:
                story.append(Paragraph(f"Scraped Content: {title}", title_style))
            else:
                story.append(Paragraph("Scraped Web Content", title_style))

            # Add source URL
            story.append(Paragraph(f"Source: {url}", url_style))
            story.append(Spacer(1, 12))

            # Add content (split into paragraphs for better formatting)
            if content:
                # Split content into paragraphs
                paragraphs = content.split('\n')
                for para in paragraphs:
                    if para.strip():  # Only add non-empty paragraphs
                        # Escape HTML characters and handle special characters
                        escaped_para = para.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                        story.append(Paragraph(escaped_para, content_style))
                        story.append(Spacer(1, 6))
            else:
                story.append(Paragraph("No content could be extracted from the URL.", content_style))

            # Build PDF
            doc.build(story)

            # Get PDF content
            pdf_content = buffer.getvalue()
            buffer.close()

            return pdf_content

        except Exception as e:
            logger.error(f"Error creating web scrape PDF: {e}")
            raise

    def _save_pdf_file(self, pdf_content, pdf_path):
        """Save PDF content to file"""
        try:
            with open(pdf_path, 'wb') as f:
                f.write(pdf_content)
            logger.info(f"PDF saved to: {pdf_path}")
        except Exception as e:
            logger.error(f"Error saving PDF file: {e}")
            raise

    def run(self, host='0.0.0.0', port=3000, debug=False):
        """Run the Flask application"""
        logger.info(f'Starting Basic Chatbot on {host}:{port}')
        self.socketio.run(self.app, host=host, port=port, debug=debug)

if __name__ == '__main__':
# __STARTUP_FIRST_LINE__
    TRACE("startup")
    app = FlaskChatbotApp()

    # Get configuration from environment
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 3000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'

    app.run(host=host, port=port, debug=debug)
else:
    # For Gunicorn deployment
    application = FlaskChatbotApp()
    app = application.app  # Expose Flask app for Gunicorn