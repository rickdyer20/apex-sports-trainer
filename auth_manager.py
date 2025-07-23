# Basketball Analysis Service - OAuth2 User Authentication
# Production-ready authentication with multiple providers

import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, request, jsonify, session, redirect, url_for
from authlib.integrations.flask_client import OAuth
import google.auth.transport.requests
import google.oauth2.id_token
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class AuthenticationManager:
    """Production authentication manager with OAuth2 and JWT support"""
    
    def __init__(self, app: Flask):
        self.app = app
        self.oauth = OAuth(app)
        self.jwt_secret = os.getenv('JWT_SECRET_KEY', 'change-this-in-production')
        self.jwt_algorithm = 'HS256'
        self.jwt_expiration_hours = 24
        
        # Configure OAuth providers
        self._setup_oauth_providers()
        self._setup_routes()
    
    def _setup_oauth_providers(self):
        """Configure OAuth2 providers"""
        
        # Google OAuth2
        self.google = self.oauth.register(
            name='google',
            client_id=os.getenv('GOOGLE_CLIENT_ID'),
            client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
            server_metadata_url='https://accounts.google.com/.well-known/openid_configuration',
            client_kwargs={
                'scope': 'openid email profile'
            }
        )
        
        # GitHub OAuth2 (optional)
        self.github = self.oauth.register(
            name='github',
            client_id=os.getenv('GITHUB_CLIENT_ID'),
            client_secret=os.getenv('GITHUB_CLIENT_SECRET'),
            access_token_url='https://github.com/login/oauth/access_token',
            authorize_url='https://github.com/login/oauth/authorize',
            api_base_url='https://api.github.com/',
            client_kwargs={'scope': 'user:email'},
        )
        
        # Microsoft OAuth2 (optional)
        self.microsoft = self.oauth.register(
            name='microsoft',
            client_id=os.getenv('MICROSOFT_CLIENT_ID'),
            client_secret=os.getenv('MICROSOFT_CLIENT_SECRET'),
            access_token_url='https://login.microsoftonline.com/common/oauth2/v2.0/token',
            authorize_url='https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
            api_base_url='https://graph.microsoft.com/',
            client_kwargs={'scope': 'openid email profile'},
        )
    
    def _setup_routes(self):
        """Set up authentication routes"""
        
        @self.app.route('/auth/login')
        def login():
            """Login page with OAuth options"""
            return jsonify({
                'message': 'Choose authentication method',
                'providers': {
                    'google': url_for('auth_google', _external=True),
                    'github': url_for('auth_github', _external=True),
                    'microsoft': url_for('auth_microsoft', _external=True),
                    'email': url_for('auth_email_login', _external=True)
                }
            })
        
        @self.app.route('/auth/google')
        def auth_google():
            """Google OAuth2 login"""
            redirect_uri = url_for('auth_google_callback', _external=True)
            return self.google.authorize_redirect(redirect_uri)
        
        @self.app.route('/auth/google/callback')
        def auth_google_callback():
            """Google OAuth2 callback"""
            try:
                token = self.google.authorize_access_token()
                user_info = token.get('userinfo')
                
                if user_info:
                    user = self._create_or_update_user({
                        'email': user_info['email'],
                        'first_name': user_info.get('given_name', ''),
                        'last_name': user_info.get('family_name', ''),
                        'provider': 'google',
                        'provider_id': user_info['sub'],
                        'email_verified': user_info.get('email_verified', False)
                    })
                    
                    # Generate JWT token
                    jwt_token = self._generate_jwt_token(user)
                    
                    # Set session
                    session['user_id'] = user['id']
                    session['jwt_token'] = jwt_token
                    
                    return redirect(url_for('dashboard'))
                else:
                    return jsonify({'error': 'Failed to get user info from Google'}), 400
                    
            except Exception as e:
                logger.error(f"Google OAuth error: {e}")
                return jsonify({'error': 'Authentication failed'}), 400
        
        @self.app.route('/auth/github')
        def auth_github():
            """GitHub OAuth2 login"""
            redirect_uri = url_for('auth_github_callback', _external=True)
            return self.github.authorize_redirect(redirect_uri)
        
        @self.app.route('/auth/github/callback')
        def auth_github_callback():
            """GitHub OAuth2 callback"""
            try:
                token = self.github.authorize_access_token()
                resp = self.github.get('user', token=token)
                user_info = resp.json()
                
                # Get user email (GitHub may not provide email in user endpoint)
                email_resp = self.github.get('user/emails', token=token)
                emails = email_resp.json()
                primary_email = next((email['email'] for email in emails if email['primary']), None)
                
                if user_info and primary_email:
                    user = self._create_or_update_user({
                        'email': primary_email,
                        'first_name': user_info.get('name', '').split(' ')[0] if user_info.get('name') else '',
                        'last_name': ' '.join(user_info.get('name', '').split(' ')[1:]) if user_info.get('name') else '',
                        'provider': 'github',
                        'provider_id': str(user_info['id']),
                        'email_verified': True  # GitHub emails are verified
                    })
                    
                    jwt_token = self._generate_jwt_token(user)
                    session['user_id'] = user['id']
                    session['jwt_token'] = jwt_token
                    
                    return redirect(url_for('dashboard'))
                else:
                    return jsonify({'error': 'Failed to get user info from GitHub'}), 400
                    
            except Exception as e:
                logger.error(f"GitHub OAuth error: {e}")
                return jsonify({'error': 'Authentication failed'}), 400
        
        @self.app.route('/auth/email/login', methods=['POST'])
        def auth_email_login():
            """Email/password login"""
            try:
                data = request.get_json()
                email = data.get('email')
                password = data.get('password')
                
                if not email or not password:
                    return jsonify({'error': 'Email and password required'}), 400
                
                user = self._authenticate_user(email, password)
                if user:
                    jwt_token = self._generate_jwt_token(user)
                    session['user_id'] = user['id']
                    session['jwt_token'] = jwt_token
                    
                    return jsonify({
                        'success': True,
                        'token': jwt_token,
                        'user': {
                            'id': user['id'],
                            'email': user['email'],
                            'first_name': user['first_name'],
                            'last_name': user['last_name']
                        }
                    })
                else:
                    return jsonify({'error': 'Invalid credentials'}), 401
                    
            except Exception as e:
                logger.error(f"Email login error: {e}")
                return jsonify({'error': 'Authentication failed'}), 500
        
        @self.app.route('/auth/email/register', methods=['POST'])
        def auth_email_register():
            """Email/password registration"""
            try:
                data = request.get_json()
                email = data.get('email')
                password = data.get('password')
                first_name = data.get('first_name', '')
                last_name = data.get('last_name', '')
                
                if not email or not password:
                    return jsonify({'error': 'Email and password required'}), 400
                
                # Check if user already exists
                if self._user_exists(email):
                    return jsonify({'error': 'User already exists'}), 409
                
                # Create new user
                user = self._create_user({
                    'email': email,
                    'password': password,
                    'first_name': first_name,
                    'last_name': last_name,
                    'provider': 'email',
                    'email_verified': False
                })
                
                # Send verification email
                self._send_verification_email(user)
                
                return jsonify({
                    'success': True,
                    'message': 'Registration successful. Please check your email for verification.',
                    'user_id': user['id']
                })
                
            except Exception as e:
                logger.error(f"Registration error: {e}")
                return jsonify({'error': 'Registration failed'}), 500
        
        @self.app.route('/auth/logout', methods=['POST'])
        def auth_logout():
            """User logout"""
            session.clear()
            return jsonify({'success': True, 'message': 'Logged out successfully'})
        
        @self.app.route('/auth/verify/<token>')
        def auth_verify_email(token):
            """Email verification"""
            try:
                user_id = self._verify_email_token(token)
                if user_id:
                    self._mark_email_verified(user_id)
                    return jsonify({'success': True, 'message': 'Email verified successfully'})
                else:
                    return jsonify({'error': 'Invalid or expired verification token'}), 400
            except Exception as e:
                logger.error(f"Email verification error: {e}")
                return jsonify({'error': 'Verification failed'}), 500
        
        @self.app.route('/auth/forgot-password', methods=['POST'])
        def auth_forgot_password():
            """Password reset request"""
            try:
                data = request.get_json()
                email = data.get('email')
                
                if not email:
                    return jsonify({'error': 'Email required'}), 400
                
                user = self._get_user_by_email(email)
                if user:
                    self._send_password_reset_email(user)
                
                # Always return success to prevent email enumeration
                return jsonify({
                    'success': True,
                    'message': 'Password reset instructions sent to your email'
                })
                
            except Exception as e:
                logger.error(f"Password reset error: {e}")
                return jsonify({'error': 'Password reset failed'}), 500
        
        @self.app.route('/auth/reset-password', methods=['POST'])
        def auth_reset_password():
            """Password reset"""
            try:
                data = request.get_json()
                token = data.get('token')
                new_password = data.get('password')
                
                if not token or not new_password:
                    return jsonify({'error': 'Token and new password required'}), 400
                
                user_id = self._verify_password_reset_token(token)
                if user_id:
                    self._update_password(user_id, new_password)
                    return jsonify({'success': True, 'message': 'Password updated successfully'})
                else:
                    return jsonify({'error': 'Invalid or expired reset token'}), 400
                    
            except Exception as e:
                logger.error(f"Password reset error: {e}")
                return jsonify({'error': 'Password reset failed'}), 500
        
        @self.app.route('/auth/profile', methods=['GET'])
        @self.require_auth
        def auth_profile():
            """Get user profile"""
            user = self._get_current_user()
            return jsonify({
                'user': {
                    'id': user['id'],
                    'email': user['email'],
                    'first_name': user['first_name'],
                    'last_name': user['last_name'],
                    'subscription_tier': user.get('subscription_tier', 'free'),
                    'email_verified': user.get('email_verified', False),
                    'created_at': user.get('created_at'),
                    'last_login': user.get('last_login')
                }
            })
    
    def require_auth(self, f):
        """Decorator to require authentication"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = None
            
            # Check for JWT token in Authorization header
            auth_header = request.headers.get('Authorization')
            if auth_header:
                try:
                    token = auth_header.split(' ')[1]  # Bearer <token>
                except IndexError:
                    pass
            
            # Check for JWT token in session
            if not token:
                token = session.get('jwt_token')
            
            if not token:
                return jsonify({'error': 'Authentication required'}), 401
            
            try:
                payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
                user_id = payload['user_id']
                
                # Store user info in request context
                request.current_user_id = user_id
                
            except jwt.ExpiredSignatureError:
                return jsonify({'error': 'Token has expired'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'error': 'Invalid token'}), 401
            
            return f(*args, **kwargs)
        return decorated_function
    
    def require_subscription(self, tier: str):
        """Decorator to require specific subscription tier"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                user = self._get_current_user()
                if not self._has_subscription_tier(user, tier):
                    return jsonify({
                        'error': 'Subscription upgrade required',
                        'required_tier': tier,
                        'current_tier': user.get('subscription_tier', 'free')
                    }), 403
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    def _generate_jwt_token(self, user: Dict[str, Any]) -> str:
        """Generate JWT token for user"""
        payload = {
            'user_id': user['id'],
            'email': user['email'],
            'exp': datetime.utcnow() + timedelta(hours=self.jwt_expiration_hours),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    def _create_or_update_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update user from OAuth data"""
        # This would interact with your database
        # Implementation depends on your database setup
        pass
    
    def _authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with email/password"""
        # This would interact with your database
        # Implementation depends on your database setup
        pass
    
    def _user_exists(self, email: str) -> bool:
        """Check if user exists"""
        # Database implementation
        pass
    
    def _create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new user"""
        # Hash password
        if 'password' in user_data:
            user_data['password_hash'] = bcrypt.hashpw(
                user_data['password'].encode('utf-8'), 
                bcrypt.gensalt()
            ).decode('utf-8')
            del user_data['password']
        
        # Database implementation
        pass
    
    def _get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        # Database implementation
        pass
    
    def _get_current_user(self) -> Dict[str, Any]:
        """Get current authenticated user"""
        user_id = getattr(request, 'current_user_id', None)
        if user_id:
            return self._get_user_by_id(user_id)
        return None
    
    def _get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        # Database implementation
        pass
    
    def _has_subscription_tier(self, user: Dict[str, Any], required_tier: str) -> bool:
        """Check if user has required subscription tier"""
        tier_levels = {'free': 0, 'pro': 1, 'enterprise': 2}
        user_tier = user.get('subscription_tier', 'free')
        return tier_levels.get(user_tier, 0) >= tier_levels.get(required_tier, 0)
    
    def _send_verification_email(self, user: Dict[str, Any]):
        """Send email verification"""
        # Email implementation
        pass
    
    def _send_password_reset_email(self, user: Dict[str, Any]):
        """Send password reset email"""
        # Email implementation
        pass
    
    def _verify_email_token(self, token: str) -> Optional[int]:
        """Verify email verification token"""
        # Token verification implementation
        pass
    
    def _verify_password_reset_token(self, token: str) -> Optional[int]:
        """Verify password reset token"""
        # Token verification implementation
        pass
    
    def _mark_email_verified(self, user_id: int):
        """Mark user email as verified"""
        # Database implementation
        pass
    
    def _update_password(self, user_id: int, new_password: str):
        """Update user password"""
        password_hash = bcrypt.hashpw(
            new_password.encode('utf-8'), 
            bcrypt.gensalt()
        ).decode('utf-8')
        # Database implementation
        pass
