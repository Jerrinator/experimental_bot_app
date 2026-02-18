"""
SSO Client Utilities for H.E.R.O.S. Microservices
This file should be copied to each client application
"""
import os
import requests
from typing import Optional, Dict, Any
from flask import request, redirect, session, jsonify, current_app, g
from functools import wraps
import logging

# Try to import JWT library
try:
    import jwt
except ImportError:
    try:
        import PyJWT as jwt
    except ImportError:
        raise ImportError("PyJWT library is required. Install with: pip install PyJWT")

from datetime import datetime

logger = logging.getLogger(__name__)

class SSOClient:
    """Client for SSO authentication across H.E.R.O.S. microservices"""
    
    def __init__(self, app_name: str, auth_service_url: Optional[str] = None):
        self.app_name = app_name
        # Updated default auth service URL per request
        self.auth_service_url = auth_service_url or os.getenv('AUTH_SERVICE_URL', 'https://unlocking-ai-auth-system-0477b057b952.herokuapp.com')
        self.secret_key = os.getenv('SSO_SECRET_KEY') or os.getenv('SECRET_KEY')
        # Allow redirects back to apps only when explicitly enabled by env
        self.allow_redirects = str(os.getenv('SSO_ALLOW_REDIRECTS', 'False')).lower() in ('1','true','yes')

        if not self.secret_key:
            logger.warning("SSO_SECRET_KEY not found in environment variables")
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate a JWT token locally
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload or None if invalid
        """
        if not self.secret_key:
            logger.warning("No secret key available for token validation")
            return None
            
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=['HS256']
            )
            
            # Check if token has expired
            if payload.get('exp', 0) < datetime.utcnow().timestamp():
                logger.info("Token has expired")
                return None
                
            # Check if this app is in permissions
            permissions = payload.get('permissions', [])
            app_permission = self._get_app_permission()
            
            if app_permission and app_permission not in permissions:
                logger.warning(f"App '{self.app_name}' not in token permissions: {permissions}")
                return None
                
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.info("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
    
    def validate_token_remote(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate token using the auth service API (fallback method)
        
        Args:
            token: JWT token string
            
        Returns:
            User data or None if invalid
        """
        try:
            response = requests.post(
                f"{self.auth_service_url}/api/sso/validate",
                json={'token': token, 'app_name': self.app_name},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('user') if data.get('valid') else None
            else:
                logger.warning(f"Token validation failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error validating token remotely: {e}")
            return None
    
    def _get_app_permission(self) -> Optional[str]:
        """Get the permission string for this app"""
        app_permissions = {
            'Globalingo': 'globalingo',
            'KnowledgeNinja': 'knowledgeninja', 
            'OCR': 'ocr',
            'BasicChatbot': 'basic_chatbot',
            'HERO_Assistant': 'hero_assistant'
        }
        return app_permissions.get(self.app_name)
    
    def get_sso_login_url(self, return_url: Optional[str] = None) -> str:
        """
        Get the SSO login URL
        
        Args:
            return_url: URL to return to after login
            
        Returns:
            SSO login URL
        """
        login_url = f"{self.auth_service_url}/auth/sso/login"
        # Only append redirect_uri when operator explicitly enables redirects
        if return_url and self.allow_redirects:
            login_url += f"?redirect_uri={return_url}&app_name={self.app_name}"
        return login_url
    
    def get_sso_logout_url(self, return_url: Optional[str] = None) -> str:
        """
        Get the SSO logout URL
        
        Args:
            return_url: URL to return to after logout
            
        Returns:
            SSO logout URL
        """
        logout_url = f"{self.auth_service_url}/auth/sso/logout"
        if return_url and self.allow_redirects:
            logout_url += f"?redirect_uri={return_url}"
        return logout_url


# Initialize the global SSO client (to be set by each app)
_sso_client: Optional[SSOClient] = None

def init_sso(app_name: str, auth_service_url: Optional[str] = None):
    """Initialize the global SSO client"""
    global _sso_client
    _sso_client = SSOClient(app_name, auth_service_url)

def get_sso_client() -> SSOClient:
    """Get the global SSO client"""
    if _sso_client is None:
        raise RuntimeError("SSO client not initialized. Call init_sso() first.")
    return _sso_client

def sso_token_required(f):
    """
    Decorator to require SSO token authentication for Flask routes
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip authentication for local testing when FLASK_ENV is development
        if os.environ.get('FLASK_ENV') == 'development':
            return f(*args, **kwargs)
        
        client = get_sso_client()
        
        # Try to get token from various sources
        token = None
        
        # 1. From URL parameter (for redirects) - check both 'sso_token' and 'token'
        token = request.args.get('sso_token') or request.args.get('token')
        
        # 2. From session (if stored)
        if not token:
            token = session.get('sso_token')
        
        # 3. From Authorization header
        if not token:
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        # 4. From form data (for POST requests)
        if not token and request.method == 'POST':
            token = request.form.get('token')
        
        # 5. From JSON body
        if not token and request.is_json:
            token = request.json.get('token') if request.json else None
        
        if not token:
            logger.warning(f"No token found for protected route: {request.endpoint}")
            # Redirect to platform root (do not preserve redirect URI)
            platform_root = os.environ.get('PLATFORM_SSO_ROOT') or os.environ.get('LAUNCH_PLATFORM_ROOT') or os.getenv('AUTH_SERVICE_URL', 'https://unlocking-ai-auth-system-0477b057b952.herokuapp.com/')
            return redirect(platform_root)
        
        # Validate token
        user_data = client.validate_token(token)
        if not user_data:
            logger.warning(f"Invalid token for route: {request.endpoint}")
            # Try remote validation as fallback
            user_data = client.validate_token_remote(token)
            
        if not user_data:
            logger.warning(f"Token validation failed for route: {request.endpoint}")
            # Clear invalid token from session and redirect to platform root (do not preserve redirect URI)
            session.pop('sso_token', None)
            platform_root = os.environ.get('PLATFORM_SSO_ROOT') or os.environ.get('LAUNCH_PLATFORM_ROOT') or os.getenv('AUTH_SERVICE_URL', 'https://unlocking-ai-auth-system-0477b057b952.herokuapp.com/')
            return redirect(platform_root)
        
        # Store user data in Flask's g object for use in the route
        g.current_user = user_data
        g.sso_token = token
        
        # Store valid token in session for future requests
        session['sso_token'] = token
        
        return f(*args, **kwargs)
    
    return decorated_function

def get_current_user() -> Optional[Dict[str, Any]]:
    """Get the current authenticated user from Flask's g object"""
    return getattr(g, 'current_user', None)

def get_current_token() -> Optional[str]:
    """Get the current SSO token from Flask's g object"""
    return getattr(g, 'sso_token', None)

def logout_user():
    """Logout the current user by clearing session data"""
    session.pop('sso_token', None)
    session.pop('return_url', None)
    if hasattr(g, 'current_user'):
        delattr(g, 'current_user')
    if hasattr(g, 'sso_token'):
        delattr(g, 'sso_token')

def require_permission(permission: str):
    """
    Decorator to require a specific permission for a route
    Must be used after @sso_token_required
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user:
                return jsonify({'error': 'Authentication required'}), 401
            
            permissions = user.get('permissions', [])
            if permission not in permissions:
                logger.warning(f"User {user.get('username')} lacks permission: {permission}")
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
