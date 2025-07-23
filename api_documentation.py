# Basketball Analysis API Documentation
# Comprehensive API documentation for developers

from flask import Flask, jsonify, request
from flask_restx import Api, Resource, fields, Namespace
from functools import wraps
import json

# Initialize Flask-RESTX for API documentation
def create_api_docs(app):
    """Create comprehensive API documentation with Flask-RESTX"""
    
    api = Api(
        app,
        version='1.0',
        title='Basketball Analysis API',
        description='AI-powered basketball shot analysis service API',
        doc='/api/docs/',
        prefix='/api/v1'
    )
    
    # Authentication namespace
    auth_ns = Namespace('auth', description='Authentication operations')
    api.add_namespace(auth_ns, path='/auth')
    
    # Videos namespace
    videos_ns = Namespace('videos', description='Video management operations')
    api.add_namespace(videos_ns, path='/videos')
    
    # Analysis namespace
    analysis_ns = Namespace('analysis', description='Shot analysis operations')
    api.add_namespace(analysis_ns, path='/analysis')
    
    # Payment namespace
    payment_ns = Namespace('payment', description='Payment and subscription operations')
    api.add_namespace(payment_ns, path='/payment')
    
    # User namespace
    user_ns = Namespace('user', description='User profile operations')
    api.add_namespace(user_ns, path='/user')
    
    # Define data models for documentation
    
    # Authentication Models
    login_model = api.model('Login', {
        'email': fields.String(required=True, description='User email address', example='user@example.com'),
        'password': fields.String(required=True, description='User password', example='password123')
    })
    
    register_model = api.model('Register', {
        'first_name': fields.String(required=True, description='First name', example='John'),
        'last_name': fields.String(required=True, description='Last name', example='Doe'),
        'email': fields.String(required=True, description='Email address', example='user@example.com'),
        'password': fields.String(required=True, description='Password (min 8 characters)', example='password123')
    })
    
    token_response = api.model('TokenResponse', {
        'success': fields.Boolean(description='Operation success status'),
        'token': fields.String(description='JWT authentication token'),
        'user': fields.Nested(api.model('UserProfile', {
            'id': fields.Integer(description='User ID'),
            'email': fields.String(description='User email'),
            'first_name': fields.String(description='First name'),
            'last_name': fields.String(description='Last name')
        }))
    })
    
    # Video Models
    video_upload_response = api.model('VideoUploadResponse', {
        'success': fields.Boolean(description='Upload success status'),
        'video_id': fields.String(description='Unique video identifier'),
        'upload_url': fields.String(description='Temporary upload URL for large files'),
        'message': fields.String(description='Status message')
    })
    
    video_model = api.model('Video', {
        'id': fields.String(description='Video ID'),
        'filename': fields.String(description='Original filename'),
        'upload_date': fields.DateTime(description='Upload timestamp'),
        'status': fields.String(description='Processing status', enum=['uploaded', 'processing', 'completed', 'failed']),
        'duration': fields.Float(description='Video duration in seconds'),
        'file_size': fields.Integer(description='File size in bytes'),
        'thumbnail_url': fields.String(description='Thumbnail image URL'),
        'video_url': fields.String(description='Video playback URL')
    })
    
    video_list_response = api.model('VideoListResponse', {
        'videos': fields.List(fields.Nested(video_model)),
        'total': fields.Integer(description='Total number of videos'),
        'page': fields.Integer(description='Current page number'),
        'per_page': fields.Integer(description='Videos per page')
    })
    
    # Analysis Models
    shot_phase_model = api.model('ShotPhase', {
        'phase': fields.String(description='Phase name', enum=['preparation', 'loading', 'release', 'follow_through']),
        'start_frame': fields.Integer(description='Starting frame number'),
        'end_frame': fields.Integer(description='Ending frame number'),
        'duration': fields.Float(description='Phase duration in seconds'),
        'key_points': fields.List(fields.String, description='Key biomechanical points')
    })
    
    biomechanics_model = api.model('Biomechanics', {
        'elbow_angle': fields.Float(description='Elbow angle at release (degrees)'),
        'knee_angle': fields.Float(description='Knee angle during loading (degrees)'),
        'release_height': fields.Float(description='Release height (normalized)'),
        'release_angle': fields.Float(description='Release angle (degrees)'),
        'follow_through_duration': fields.Float(description='Follow-through duration (seconds)'),
        'balance_score': fields.Float(description='Balance score (0-100)'),
        'consistency_score': fields.Float(description='Consistency score (0-100)')
    })
    
    feedback_model = api.model('Feedback', {
        'category': fields.String(description='Feedback category', enum=['form', 'timing', 'balance', 'consistency']),
        'severity': fields.String(description='Issue severity', enum=['minor', 'moderate', 'major']),
        'message': fields.String(description='Feedback message'),
        'recommendation': fields.String(description='Improvement recommendation'),
        'frame_reference': fields.Integer(description='Frame where issue occurs')
    })
    
    analysis_result_model = api.model('AnalysisResult', {
        'video_id': fields.String(description='Video identifier'),
        'analysis_id': fields.String(description='Analysis identifier'),
        'status': fields.String(description='Analysis status'),
        'created_at': fields.DateTime(description='Analysis creation time'),
        'completed_at': fields.DateTime(description='Analysis completion time'),
        'processing_time': fields.Float(description='Processing time in seconds'),
        'shot_phases': fields.List(fields.Nested(shot_phase_model)),
        'biomechanics': fields.Nested(biomechanics_model),
        'feedback': fields.List(fields.Nested(feedback_model)),
        'overall_score': fields.Float(description='Overall shooting form score (0-100)'),
        'improvement_areas': fields.List(fields.String, description='Primary areas for improvement'),
        'analysis_video_url': fields.String(description='URL to annotated analysis video'),
        'report_pdf_url': fields.String(description='URL to downloadable PDF report')
    })
    
    # Payment Models
    subscription_model = api.model('Subscription', {
        'tier': fields.String(description='Subscription tier', enum=['free', 'pro', 'enterprise']),
        'status': fields.String(description='Subscription status', enum=['active', 'cancelled', 'past_due']),
        'billing_cycle': fields.String(description='Billing cycle', enum=['monthly', 'yearly']),
        'current_period_start': fields.DateTime(description='Current billing period start'),
        'current_period_end': fields.DateTime(description='Current billing period end'),
        'cancel_at_period_end': fields.Boolean(description='Will cancel at period end')
    })
    
    usage_model = api.model('Usage', {
        'videos_this_month': fields.Integer(description='Videos uploaded this month'),
        'analyses_this_month': fields.Integer(description='Analyses performed this month'),
        'total_videos': fields.Integer(description='Total videos uploaded'),
        'total_analyses': fields.Integer(description='Total analyses performed'),
        'storage_used': fields.Float(description='Storage used in GB')
    })
    
    checkout_request = api.model('CheckoutRequest', {
        'tier_id': fields.String(required=True, description='Subscription tier', enum=['pro', 'enterprise']),
        'billing_cycle': fields.String(required=True, description='Billing cycle', enum=['monthly', 'yearly'])
    })
    
    checkout_response = api.model('CheckoutResponse', {
        'checkout_url': fields.String(description='Stripe checkout URL')
    })
    
    # Authentication Endpoints
    
    @auth_ns.route('/login')
    class Login(Resource):
        @auth_ns.expect(login_model)
        @auth_ns.marshal_with(token_response)
        @auth_ns.doc('user_login')
        def post(self):
            """Authenticate user with email and password"""
            return {'message': 'Login endpoint'}
    
    @auth_ns.route('/register')
    class Register(Resource):
        @auth_ns.expect(register_model)
        @auth_ns.marshal_with(token_response)
        @auth_ns.doc('user_register')
        def post(self):
            """Register new user account"""
            return {'message': 'Register endpoint'}
    
    @auth_ns.route('/google')
    class GoogleAuth(Resource):
        @auth_ns.doc('google_oauth')
        def get(self):
            """Initiate Google OAuth authentication"""
            return {'redirect_url': '/auth/google'}
    
    @auth_ns.route('/logout')
    class Logout(Resource):
        @auth_ns.doc('user_logout')
        @auth_ns.doc(security='apikey')
        def post(self):
            """Logout current user"""
            return {'success': True}
    
    # Video Management Endpoints
    
    @videos_ns.route('/')
    class VideoList(Resource):
        @videos_ns.marshal_with(video_list_response)
        @videos_ns.doc('list_videos')
        @videos_ns.doc(security='apikey')
        @videos_ns.param('page', 'Page number', type=int, default=1)
        @videos_ns.param('per_page', 'Videos per page', type=int, default=20)
        @videos_ns.param('status', 'Filter by status', enum=['uploaded', 'processing', 'completed', 'failed'])
        def get(self):
            """Get list of user's videos"""
            return {'videos': [], 'total': 0, 'page': 1, 'per_page': 20}
        
        @videos_ns.expect(api.parser().add_argument('video', location='files', type='file', required=True, help='Video file'))
        @videos_ns.marshal_with(video_upload_response)
        @videos_ns.doc('upload_video')
        @videos_ns.doc(security='apikey')
        def post(self):
            """Upload new video for analysis"""
            return {'success': True, 'video_id': 'video_123', 'message': 'Video uploaded successfully'}
    
    @videos_ns.route('/<string:video_id>')
    class VideoDetail(Resource):
        @videos_ns.marshal_with(video_model)
        @videos_ns.doc('get_video')
        @videos_ns.doc(security='apikey')
        def get(self, video_id):
            """Get video details"""
            return {'id': video_id, 'filename': 'example.mp4', 'status': 'completed'}
        
        @videos_ns.doc('delete_video')
        @videos_ns.doc(security='apikey')
        def delete(self, video_id):
            """Delete video"""
            return {'success': True, 'message': 'Video deleted successfully'}
    
    # Analysis Endpoints
    
    @analysis_ns.route('/start')
    class StartAnalysis(Resource):
        @analysis_ns.expect(api.model('AnalysisRequest', {
            'video_id': fields.String(required=True, description='Video ID to analyze')
        }))
        @analysis_ns.doc('start_analysis')
        @analysis_ns.doc(security='apikey')
        def post(self):
            """Start analysis for uploaded video"""
            return {'success': True, 'analysis_id': 'analysis_123', 'message': 'Analysis started'}
    
    @analysis_ns.route('/<string:analysis_id>')
    class AnalysisResult(Resource):
        @analysis_ns.marshal_with(analysis_result_model)
        @analysis_ns.doc('get_analysis')
        @analysis_ns.doc(security='apikey')
        def get(self, analysis_id):
            """Get analysis results"""
            return {
                'analysis_id': analysis_id,
                'status': 'completed',
                'overall_score': 85.5,
                'shot_phases': [],
                'biomechanics': {},
                'feedback': []
            }
    
    @analysis_ns.route('/<string:analysis_id>/report')
    class AnalysisReport(Resource):
        @analysis_ns.doc('download_report')
        @analysis_ns.doc(security='apikey')
        @analysis_ns.param('format', 'Report format', enum=['pdf', 'json'], default='pdf')
        def get(self, analysis_id):
            """Download analysis report"""
            return {'download_url': f'/downloads/report_{analysis_id}.pdf'}
    
    # Payment Endpoints
    
    @payment_ns.route('/subscription/status')
    class SubscriptionStatus(Resource):
        @payment_ns.marshal_with(api.model('SubscriptionStatus', {
            'subscription': fields.Nested(subscription_model),
            'usage': fields.Nested(usage_model),
            'limits': fields.Raw(description='Subscription limits')
        }))
        @payment_ns.doc('get_subscription_status')
        @payment_ns.doc(security='apikey')
        def get(self):
            """Get current subscription status and usage"""
            return {
                'subscription': {'tier': 'pro', 'status': 'active'},
                'usage': {'videos_this_month': 5, 'analyses_this_month': 5},
                'limits': {'video_limit': -1, 'analysis_limit': -1}
            }
    
    @payment_ns.route('/checkout')
    class CreateCheckout(Resource):
        @payment_ns.expect(checkout_request)
        @payment_ns.marshal_with(checkout_response)
        @payment_ns.doc('create_checkout')
        @payment_ns.doc(security='apikey')
        def post(self):
            """Create Stripe checkout session"""
            return {'checkout_url': 'https://checkout.stripe.com/session_123'}
    
    @payment_ns.route('/portal')
    class CustomerPortal(Resource):
        @payment_ns.marshal_with(api.model('PortalResponse', {
            'portal_url': fields.String(description='Customer portal URL')
        }))
        @payment_ns.doc('customer_portal')
        @payment_ns.doc(security='apikey')
        def post(self):
            """Create customer portal session"""
            return {'portal_url': 'https://billing.stripe.com/session_123'}
    
    # User Profile Endpoints
    
    @user_ns.route('/profile')
    class UserProfile(Resource):
        @user_ns.marshal_with(api.model('UserProfileResponse', {
            'user': fields.Nested(api.model('UserDetails', {
                'id': fields.Integer(description='User ID'),
                'email': fields.String(description='Email address'),
                'first_name': fields.String(description='First name'),
                'last_name': fields.String(description='Last name'),
                'created_at': fields.DateTime(description='Account creation date'),
                'last_login': fields.DateTime(description='Last login time'),
                'email_verified': fields.Boolean(description='Email verification status')
            }))
        }))
        @user_ns.doc('get_profile')
        @user_ns.doc(security='apikey')
        def get(self):
            """Get user profile information"""
            return {
                'user': {
                    'id': 123,
                    'email': 'user@example.com',
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'email_verified': True
                }
            }
        
        @user_ns.expect(api.model('ProfileUpdate', {
            'first_name': fields.String(description='First name'),
            'last_name': fields.String(description='Last name')
        }))
        @user_ns.doc('update_profile')
        @user_ns.doc(security='apikey')
        def put(self):
            """Update user profile information"""
            return {'success': True, 'message': 'Profile updated successfully'}
    
    # Add authentication documentation
    authorizations = {
        'apikey': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'JWT Token. Format: Bearer &lt;token&gt;'
        }
    }
    
    api.authorizations = authorizations
    
    # Add error models
    error_model = api.model('Error', {
        'error': fields.String(description='Error message'),
        'code': fields.Integer(description='Error code'),
        'details': fields.Raw(description='Additional error details')
    })
    
    # Add common error responses
    @api.errorhandler
    def default_error_handler(error):
        """Default error handler"""
        return {'error': str(error)}, getattr(error, 'code', 500)
    
    return api

# API Usage Examples and Integration Guide
API_EXAMPLES = {
    "authentication": {
        "login": {
            "curl": """
curl -X POST \\
  https://api.basketball-analysis.com/auth/login \\
  -H 'Content-Type: application/json' \\
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
            """,
            "python": """
import requests

response = requests.post(
    'https://api.basketball-analysis.com/auth/login',
    json={
        'email': 'user@example.com',
        'password': 'password123'
    }
)

token = response.json()['token']
            """,
            "javascript": """
const response = await fetch('https://api.basketball-analysis.com/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123'
  })
});

const data = await response.json();
const token = data.token;
            """
        }
    },
    "video_upload": {
        "curl": """
curl -X POST \\
  https://api.basketball-analysis.com/videos/ \\
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \\
  -F 'video=@/path/to/your/video.mp4'
        """,
        "python": """
import requests

headers = {'Authorization': 'Bearer YOUR_JWT_TOKEN'}
files = {'video': open('video.mp4', 'rb')}

response = requests.post(
    'https://api.basketball-analysis.com/videos/',
    headers=headers,
    files=files
)

video_id = response.json()['video_id']
        """,
        "javascript": """
const formData = new FormData();
formData.append('video', videoFile);

const response = await fetch('https://api.basketball-analysis.com/videos/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_JWT_TOKEN'
  },
  body: formData
});

const data = await response.json();
const videoId = data.video_id;
        """
    },
    "start_analysis": {
        "curl": """
curl -X POST \\
  https://api.basketball-analysis.com/analysis/start \\
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \\
  -H 'Content-Type: application/json' \\
  -d '{
    "video_id": "video_123"
  }'
        """,
        "python": """
import requests

headers = {
    'Authorization': 'Bearer YOUR_JWT_TOKEN',
    'Content-Type': 'application/json'
}

response = requests.post(
    'https://api.basketball-analysis.com/analysis/start',
    headers=headers,
    json={'video_id': 'video_123'}
)

analysis_id = response.json()['analysis_id']
        """
    }
}

# Rate Limiting Documentation
RATE_LIMITS = {
    "authentication": "10 requests per minute",
    "video_upload": "5 requests per hour (Free), unlimited (Pro/Enterprise)",
    "analysis": "10 requests per hour (Free), unlimited (Pro/Enterprise)",
    "general_api": "100 requests per hour (Free), 1000 requests per hour (Pro/Enterprise)"
}

# SDK Examples
SDK_EXAMPLES = {
    "python": """
# Basketball Analysis Python SDK
from basketball_analysis import BasketballAnalysisClient

# Initialize client
client = BasketballAnalysisClient(api_key='your_api_key')

# Upload and analyze video
video = client.upload_video('path/to/video.mp4')
analysis = client.start_analysis(video.id)

# Wait for completion
result = client.wait_for_analysis(analysis.id)

# Get feedback
feedback = result.get_feedback()
for item in feedback:
    print(f"{item.category}: {item.message}")
    """,
    "javascript": """
// Basketball Analysis JavaScript SDK
import { BasketballAnalysisClient } from '@basketball-analysis/sdk';

// Initialize client
const client = new BasketballAnalysisClient({
  apiKey: 'your_api_key'
});

// Upload and analyze video
const video = await client.uploadVideo(videoFile);
const analysis = await client.startAnalysis(video.id);

// Wait for completion
const result = await client.waitForAnalysis(analysis.id);

// Get feedback
const feedback = result.getFeedback();
feedback.forEach(item => {
  console.log(`${item.category}: ${item.message}`);
});
    """
}
