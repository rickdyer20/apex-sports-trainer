# Commercial Implementation Guide
## Technical Features for Basketball Analysis Service Launch

### 🎯 Overview
This guide covers the technical implementation of commercial features needed for the Basketball Analysis Service launch, building on your existing V9 infrastructure.

---

## 1. User Dashboard & Account Management

### 1.1 Enhanced User Interface
Create a comprehensive user dashboard that integrates with your existing authentication system:

```python
# File: user_dashboard.py
from flask import Flask, render_template, request, session, redirect, url_for
from auth_manager import AuthenticationManager, require_auth
from payment_manager import PaymentManager
import sqlite3
from datetime import datetime, timedelta

class UserDashboard:
    def __init__(self, app: Flask, auth_manager: AuthenticationManager, payment_manager: PaymentManager):
        self.app = app
        self.auth = auth_manager
        self.payment = payment_manager
        self._setup_routes()
    
    def _setup_routes(self):
        @self.app.route('/dashboard')
        @require_auth
        def dashboard():
            user = self.auth.get_current_user()
            subscription = self.payment.get_user_subscription(user['id'])
            
            # Get user's recent analyses
            recent_analyses = self.get_user_analyses(user['id'], limit=10)
            
            # Get usage statistics
            usage_stats = self.get_usage_statistics(user['id'])
            
            return render_template('dashboard.html', 
                user=user,
                subscription=subscription,
                recent_analyses=recent_analyses,
                usage_stats=usage_stats
            )
        
        @self.app.route('/account-settings')
        @require_auth
        def account_settings():
            user = self.auth.get_current_user()
            subscription = self.payment.get_user_subscription(user['id'])
            return render_template('account_settings.html', 
                user=user, 
                subscription=subscription
            )
    
    def get_user_analyses(self, user_id: str, limit: int = 10):
        """Get user's recent video analyses"""
        conn = sqlite3.connect('basketball_analysis.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, video_filename, created_at, status, 
                   overall_score, feedback_summary
            FROM analysis_jobs 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (user_id, limit))
        
        analyses = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'filename': row[1],
                'created_at': row[2],
                'status': row[3],
                'score': row[4],
                'summary': row[5]
            }
            for row in analyses
        ]
    
    def get_usage_statistics(self, user_id: str):
        """Get user's monthly usage statistics"""
        conn = sqlite3.connect('basketball_analysis.db')
        cursor = conn.cursor()
        
        # Get current month usage
        current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        cursor.execute('''
            SELECT COUNT(*) as analyses_this_month,
                   AVG(overall_score) as avg_score
            FROM analysis_jobs 
            WHERE user_id = ? AND created_at >= ?
        ''', (user_id, current_month_start))
        
        stats = cursor.fetchone()
        conn.close()
        
        return {
            'analyses_this_month': stats[0] or 0,
            'average_score': round(stats[1] or 0, 1)
        }
```

### 1.2 Dashboard HTML Template
```html
<!-- File: templates/dashboard.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Basketball Analysis Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gray-100">
    <div class="min-h-screen">
        <!-- Navigation -->
        <nav class="bg-blue-600 text-white p-4">
            <div class="container mx-auto flex justify-between items-center">
                <h1 class="text-xl font-bold">Basketball Analysis</h1>
                <div class="flex items-center space-x-4">
                    <span>{{ user.first_name }} {{ user.last_name }}</span>
                    <a href="{{ url_for('account_settings') }}" class="hover:underline">Settings</a>
                    <a href="{{ url_for('auth.logout') }}" class="hover:underline">Logout</a>
                </div>
            </div>
        </nav>

        <div class="container mx-auto px-4 py-8">
            <!-- Subscription Status -->
            <div class="bg-white rounded-lg shadow-md p-6 mb-6">
                <h2 class="text-2xl font-semibold mb-4">Subscription Status</h2>
                <div class="flex justify-between items-center">
                    <div>
                        <p class="text-lg">Current Plan: 
                            <span class="font-semibold text-blue-600">{{ subscription.plan_name }}</span>
                        </p>
                        <p class="text-gray-600">
                            {{ usage_stats.analyses_this_month }} / {{ subscription.monthly_limit }} analyses used this month
                        </p>
                    </div>
                    <div class="text-right">
                        {% if subscription.plan_name == 'Free' %}
                            <a href="{{ url_for('upgrade') }}" 
                               class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                                Upgrade Plan
                            </a>
                        {% else %}
                            <a href="{{ url_for('manage_subscription') }}" 
                               class="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700">
                                Manage Subscription
                            </a>
                        {% endif %}
                    </div>
                </div>
                
                <!-- Usage Progress Bar -->
                <div class="w-full bg-gray-200 rounded-full h-2 mt-4">
                    <div class="bg-blue-600 h-2 rounded-full" 
                         style="width: {{ (usage_stats.analyses_this_month / subscription.monthly_limit * 100) }}%">
                    </div>
                </div>
            </div>

            <!-- Quick Actions -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div class="bg-white rounded-lg shadow-md p-6 text-center">
                    <div class="text-3xl text-blue-600 mb-2">📹</div>
                    <h3 class="text-lg font-semibold mb-2">New Analysis</h3>
                    <p class="text-gray-600 mb-4">Upload a new video for analysis</p>
                    <a href="{{ url_for('upload') }}" 
                       class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                        Upload Video
                    </a>
                </div>
                
                <div class="bg-white rounded-lg shadow-md p-6 text-center">
                    <div class="text-3xl text-green-600 mb-2">📊</div>
                    <h3 class="text-lg font-semibold mb-2">Progress Report</h3>
                    <p class="text-gray-600 mb-4">View your improvement over time</p>
                    <a href="{{ url_for('progress') }}" 
                       class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">
                        View Progress
                    </a>
                </div>
                
                <div class="bg-white rounded-lg shadow-md p-6 text-center">
                    <div class="text-3xl text-purple-600 mb-2">🎯</div>
                    <h3 class="text-lg font-semibold mb-2">Training Tips</h3>
                    <p class="text-gray-600 mb-4">Personalized coaching advice</p>
                    <a href="{{ url_for('training_tips') }}" 
                       class="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700">
                        Get Tips
                    </a>
                </div>
            </div>

            <!-- Recent Analyses -->
            <div class="bg-white rounded-lg shadow-md p-6">
                <h2 class="text-2xl font-semibold mb-4">Recent Analyses</h2>
                {% if recent_analyses %}
                    <div class="overflow-x-auto">
                        <table class="w-full table-auto">
                            <thead>
                                <tr class="bg-gray-50">
                                    <th class="px-4 py-2 text-left">Video</th>
                                    <th class="px-4 py-2 text-left">Date</th>
                                    <th class="px-4 py-2 text-left">Score</th>
                                    <th class="px-4 py-2 text-left">Status</th>
                                    <th class="px-4 py-2 text-left">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for analysis in recent_analyses %}
                                <tr class="border-b">
                                    <td class="px-4 py-2">{{ analysis.filename }}</td>
                                    <td class="px-4 py-2">{{ analysis.created_at[:10] }}</td>
                                    <td class="px-4 py-2">
                                        {% if analysis.score %}
                                            <span class="text-lg font-semibold 
                                                {% if analysis.score >= 80 %}text-green-600
                                                {% elif analysis.score >= 60 %}text-yellow-600
                                                {% else %}text-red-600{% endif %}">
                                                {{ analysis.score }}%
                                            </span>
                                        {% else %}
                                            <span class="text-gray-400">Processing...</span>
                                        {% endif %}
                                    </td>
                                    <td class="px-4 py-2">
                                        <span class="px-2 py-1 rounded text-sm 
                                            {% if analysis.status == 'completed' %}bg-green-100 text-green-800
                                            {% elif analysis.status == 'processing' %}bg-yellow-100 text-yellow-800
                                            {% else %}bg-red-100 text-red-800{% endif %}">
                                            {{ analysis.status.title() }}
                                        </span>
                                    </td>
                                    <td class="px-4 py-2">
                                        {% if analysis.status == 'completed' %}
                                            <a href="{{ url_for('view_analysis', id=analysis.id) }}" 
                                               class="text-blue-600 hover:underline">View</a>
                                        {% endif %}
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                {% else %}
                    <p class="text-gray-600">No analyses yet. Upload your first video to get started!</p>
                {% endif %}
            </div>
        </div>
    </div>
</body>
</html>
```

---

## 2. Subscription Management Integration

### 2.1 Enhanced Payment Integration
Extend your existing `payment_manager.py` with subscription management features:

```python
# Add to payment_manager.py
class SubscriptionManager:
    def __init__(self, payment_manager: PaymentManager):
        self.payment = payment_manager
    
    def create_checkout_session(self, user_id: str, plan_id: str, success_url: str, cancel_url: str):
        """Create Stripe checkout session for subscription"""
        try:
            tier = self.payment.subscription_tiers[plan_id]
            
            session = stripe.checkout.Session.create(
                customer_email=self.get_user_email(user_id),
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': tier.name + ' Plan',
                            'description': f'{tier.video_limit} analyses per month'
                        },
                        'unit_amount': tier.price_monthly,
                        'recurring': {'interval': 'month'}
                    },
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=cancel_url,
                metadata={
                    'user_id': user_id,
                    'plan_id': plan_id
                }
            )
            
            return session.url
            
        except Exception as e:
            logger.error(f"Failed to create checkout session: {e}")
            return None
    
    def handle_successful_subscription(self, session_id: str):
        """Handle successful subscription creation"""
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            subscription = stripe.Subscription.retrieve(session.subscription)
            
            user_id = session.metadata['user_id']
            plan_id = session.metadata['plan_id']
            
            # Update user subscription in database
            self.update_user_subscription(
                user_id=user_id,
                stripe_subscription_id=subscription.id,
                plan_id=plan_id,
                status='active'
            )
            
            logger.info(f"Successfully activated subscription for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to handle successful subscription: {e}")
            return False
    
    def update_user_subscription(self, user_id: str, stripe_subscription_id: str, 
                               plan_id: str, status: str):
        """Update user subscription in database"""
        conn = sqlite3.connect('basketball_analysis.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO subscriptions 
            (user_id, stripe_subscription_id, plan_id, status, updated_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, stripe_subscription_id, plan_id, status, datetime.now()))
        
        # Update user's subscription type
        cursor.execute('''
            UPDATE users SET subscription_type = ? WHERE id = ?
        ''', (plan_id, user_id))
        
        conn.commit()
        conn.close()
```

### 2.2 Usage Tracking & Limits
```python
# File: usage_tracker.py
class UsageTracker:
    def __init__(self):
        pass
    
    def check_usage_limit(self, user_id: str) -> dict:
        """Check if user has remaining usage for current month"""
        subscription = self.get_user_subscription(user_id)
        current_usage = self.get_monthly_usage(user_id)
        
        return {
            'can_analyze': current_usage < subscription['monthly_limit'],
            'current_usage': current_usage,
            'monthly_limit': subscription['monthly_limit'],
            'plan_name': subscription['plan_name']
        }
    
    def get_monthly_usage(self, user_id: str) -> int:
        """Get user's analyses count for current month"""
        conn = sqlite3.connect('basketball_analysis.db')
        cursor = conn.cursor()
        
        # Get first day of current month
        current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        cursor.execute('''
            SELECT COUNT(*) FROM analysis_jobs 
            WHERE user_id = ? AND created_at >= ?
        ''', (user_id, current_month))
        
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def increment_usage(self, user_id: str, analysis_id: str):
        """Record new analysis usage"""
        conn = sqlite3.connect('basketball_analysis.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO usage_records (user_id, analysis_id, created_at)
            VALUES (?, ?, ?)
        ''', (user_id, analysis_id, datetime.now()))
        
        conn.commit()
        conn.close()
    
    def get_user_subscription(self, user_id: str) -> dict:
        """Get user's current subscription details"""
        conn = sqlite3.connect('basketball_analysis.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT subscription_type FROM users WHERE id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        subscription_type = result[0] if result else 'free'
        
        # Define subscription limits
        subscription_limits = {
            'free': {'monthly_limit': 2, 'plan_name': 'Free'},
            'starter': {'monthly_limit': 10, 'plan_name': 'Starter'},
            'pro': {'monthly_limit': 50, 'plan_name': 'Pro'},
            'coach': {'monthly_limit': 200, 'plan_name': 'Coach'}
        }
        
        conn.close()
        return subscription_limits.get(subscription_type, subscription_limits['free'])
```

---

## 3. Enhanced Video Processing with User Management

### 3.1 Updated Analysis Service
Modify your existing `basketball_analysis_service.py` to include user and subscription management:

```python
# Add to basketball_analysis_service.py (after existing imports)
from user_dashboard import UserDashboard
from usage_tracker import UsageTracker

# Initialize new components
usage_tracker = UsageTracker()
user_dashboard = UserDashboard(app, auth_manager, payment_manager)

# Modify the analyze_video endpoint
@app.route('/analyze', methods=['POST'])
@require_auth
def analyze_video():
    try:
        # Get current user
        user = auth_manager.get_current_user()
        user_id = user['id']
        
        # Check usage limits
        usage_status = usage_tracker.check_usage_limit(user_id)
        
        if not usage_status['can_analyze']:
            return jsonify({
                'error': 'Monthly usage limit exceeded',
                'current_usage': usage_status['current_usage'],
                'monthly_limit': usage_status['monthly_limit'],
                'plan_name': usage_status['plan_name'],
                'upgrade_url': url_for('pricing')
            }), 403
        
        # Process video upload
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        video_file = request.files['video']
        if video_file.filename == '':
            return jsonify({'error': 'No video file selected'}), 400
        
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Save uploaded video
        video_filename = f"{job_id}_{secure_filename(video_file.filename)}"
        video_path = os.path.join('/tmp', video_filename)
        video_file.save(video_path)
        
        # Create analysis job record
        conn = sqlite3.connect('basketball_analysis.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO analysis_jobs 
            (id, user_id, video_filename, video_path, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (job_id, user_id, video_filename, video_path, 'processing', datetime.now()))
        conn.commit()
        conn.close()
        
        # Increment usage counter
        usage_tracker.increment_usage(user_id, job_id)
        
        # Process video asynchronously
        result = process_basketball_video(video_path, job_id, user_id)
        
        return jsonify({
            'job_id': job_id,
            'status': 'processing',
            'message': 'Video uploaded successfully. Processing will begin shortly.',
            'remaining_analyses': usage_status['monthly_limit'] - usage_status['current_usage'] - 1
        })
        
    except Exception as e:
        logging.error(f"Error in analyze_video: {e}")
        return jsonify({'error': 'Analysis failed. Please try again.'}), 500

# Add progress tracking endpoint
@app.route('/progress/<user_id>')
@require_auth
def user_progress(user_id):
    """Get user's progress over time"""
    current_user = auth_manager.get_current_user()
    
    # Ensure user can only access their own progress
    if current_user['id'] != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    conn = sqlite3.connect('basketball_analysis.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT created_at, overall_score, 
               json_extract(detailed_analysis, '$.elbow_flare_score') as elbow_score,
               json_extract(detailed_analysis, '$.knee_bend_score') as knee_score,
               json_extract(detailed_analysis, '$.follow_through_score') as follow_through_score
        FROM analysis_jobs 
        WHERE user_id = ? AND status = 'completed' AND overall_score IS NOT NULL
        ORDER BY created_at ASC
    ''', (user_id,))
    
    progress_data = cursor.fetchall()
    conn.close()
    
    # Format data for charting
    formatted_data = []
    for row in progress_data:
        formatted_data.append({
            'date': row[0][:10],  # Extract date part
            'overall_score': row[1],
            'elbow_score': row[2],
            'knee_score': row[3],
            'follow_through_score': row[4]
        })
    
    return jsonify({
        'progress_data': formatted_data,
        'total_analyses': len(formatted_data)
    })
```

---

## 4. Database Schema Updates

### 4.1 Enhanced Database Structure
```sql
-- Add to setup_database.py or run separately

-- Usage tracking table
CREATE TABLE IF NOT EXISTS usage_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    analysis_id TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (analysis_id) REFERENCES analysis_jobs (id)
);

-- Enhanced analysis_jobs table
ALTER TABLE analysis_jobs ADD COLUMN overall_score INTEGER;
ALTER TABLE analysis_jobs ADD COLUMN feedback_summary TEXT;
ALTER TABLE analysis_jobs ADD COLUMN detailed_analysis TEXT; -- JSON field

-- User preferences table
CREATE TABLE IF NOT EXISTS user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL UNIQUE,
    email_notifications BOOLEAN DEFAULT TRUE,
    progress_reports BOOLEAN DEFAULT TRUE,
    marketing_emails BOOLEAN DEFAULT FALSE,
    preferred_analysis_detail TEXT DEFAULT 'standard',
    timezone TEXT DEFAULT 'UTC',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Analysis feedback table for improvement tracking
CREATE TABLE IF NOT EXISTS analysis_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id TEXT NOT NULL,
    user_rating INTEGER, -- 1-5 stars
    feedback_text TEXT,
    helpful_vote BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (analysis_id) REFERENCES analysis_jobs (id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_usage_records_user_date ON usage_records(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_analysis_jobs_user_status ON analysis_jobs(user_id, status);
CREATE INDEX IF NOT EXISTS idx_analysis_jobs_created_at ON analysis_jobs(created_at);
```

---

## 5. API Rate Limiting & Security

### 5.1 Rate Limiting Implementation
```python
# File: rate_limiter.py
from flask import request, jsonify, g
import time
import sqlite3
from functools import wraps

class RateLimiter:
    def __init__(self):
        self.setup_rate_limit_table()
    
    def setup_rate_limit_table(self):
        """Create rate limiting table"""
        conn = sqlite3.connect('basketball_analysis.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rate_limits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                endpoint TEXT,
                requests_count INTEGER DEFAULT 1,
                window_start TIMESTAMP,
                UNIQUE(user_id, endpoint)
            )
        ''')
        conn.commit()
        conn.close()
    
    def check_rate_limit(self, user_id: str, endpoint: str, 
                        max_requests: int = 60, window_minutes: int = 60):
        """Check if user has exceeded rate limit"""
        conn = sqlite3.connect('basketball_analysis.db')
        cursor = conn.cursor()
        
        current_time = time.time()
        window_start = current_time - (window_minutes * 60)
        
        # Get current rate limit record
        cursor.execute('''
            SELECT requests_count, window_start FROM rate_limits
            WHERE user_id = ? AND endpoint = ?
        ''', (user_id, endpoint))
        
        result = cursor.fetchone()
        
        if result:
            requests_count, recorded_window_start = result
            
            # Check if we're still in the same window
            if recorded_window_start > window_start:
                if requests_count >= max_requests:
                    conn.close()
                    return False, requests_count
                
                # Increment counter
                cursor.execute('''
                    UPDATE rate_limits 
                    SET requests_count = requests_count + 1
                    WHERE user_id = ? AND endpoint = ?
                ''', (user_id, endpoint))
            else:
                # New window, reset counter
                cursor.execute('''
                    UPDATE rate_limits 
                    SET requests_count = 1, window_start = ?
                    WHERE user_id = ? AND endpoint = ?
                ''', (current_time, user_id, endpoint))
        else:
            # First request, create record
            cursor.execute('''
                INSERT INTO rate_limits (user_id, endpoint, requests_count, window_start)
                VALUES (?, ?, 1, ?)
            ''', (user_id, endpoint, current_time))
        
        conn.commit()
        conn.close()
        return True, 1

def rate_limit(max_requests: int = 60, window_minutes: int = 60):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get user from session/auth
            user = g.get('current_user')
            if not user:
                return jsonify({'error': 'Authentication required'}), 401
            
            rate_limiter = RateLimiter()
            endpoint = request.endpoint
            
            allowed, current_count = rate_limiter.check_rate_limit(
                user['id'], endpoint, max_requests, window_minutes
            )
            
            if not allowed:
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'max_requests': max_requests,
                    'window_minutes': window_minutes,
                    'current_count': current_count
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Usage example:
# @rate_limit(max_requests=10, window_minutes=60)  # 10 requests per hour
# @app.route('/analyze', methods=['POST'])
# def analyze_video():
#     # Your video analysis logic
```

---

## 6. Customer Support Integration

### 6.1 Support Ticket System
```python
# File: support_system.py
class SupportSystem:
    def __init__(self, app: Flask):
        self.app = app
        self.setup_support_tables()
        self._setup_routes()
    
    def setup_support_tables(self):
        """Create support ticket tables"""
        conn = sqlite3.connect('basketball_analysis.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS support_tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                subject TEXT NOT NULL,
                description TEXT NOT NULL,
                priority TEXT DEFAULT 'medium',
                status TEXT DEFAULT 'open',
                assigned_to TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS support_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id INTEGER NOT NULL,
                user_id TEXT,
                message TEXT NOT NULL,
                is_staff_reply BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ticket_id) REFERENCES support_tickets (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _setup_routes(self):
        @self.app.route('/support/new', methods=['GET', 'POST'])
        @require_auth
        def create_support_ticket():
            if request.method == 'POST':
                user = auth_manager.get_current_user()
                subject = request.form.get('subject')
                description = request.form.get('description')
                priority = request.form.get('priority', 'medium')
                
                ticket_id = self.create_ticket(user['id'], subject, description, priority)
                
                # Send notification email
                self.send_ticket_confirmation(user['email'], ticket_id, subject)
                
                return jsonify({
                    'ticket_id': ticket_id,
                    'message': 'Support ticket created successfully'
                })
            
            return render_template('support/new_ticket.html')
        
        @self.app.route('/support/tickets')
        @require_auth  
        def list_user_tickets():
            user = auth_manager.get_current_user()
            tickets = self.get_user_tickets(user['id'])
            return render_template('support/tickets.html', tickets=tickets)
    
    def create_ticket(self, user_id: str, subject: str, description: str, priority: str = 'medium'):
        """Create new support ticket"""
        conn = sqlite3.connect('basketball_analysis.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO support_tickets (user_id, subject, description, priority)
            VALUES (?, ?, ?, ?)
        ''', (user_id, subject, description, priority))
        
        ticket_id = cursor.lastrowid
        
        # Add initial message
        cursor.execute('''
            INSERT INTO support_messages (ticket_id, user_id, message)
            VALUES (?, ?, ?)
        ''', (ticket_id, user_id, description))
        
        conn.commit()
        conn.close()
        
        return ticket_id
    
    def send_ticket_confirmation(self, email: str, ticket_id: int, subject: str):
        """Send ticket confirmation email"""
        # Implement email sending logic
        # Could use SendGrid, AWS SES, or similar service
        pass
```

---

## 7. Analytics & Reporting

### 7.1 Business Analytics Dashboard
```python
# File: analytics_dashboard.py
class AnalyticsDashboard:
    def __init__(self, app: Flask):
        self.app = app
        self._setup_admin_routes()
    
    def _setup_admin_routes(self):
        @self.app.route('/admin/analytics')
        @require_admin_auth
        def admin_analytics():
            metrics = self.get_business_metrics()
            return render_template('admin/analytics.html', metrics=metrics)
    
    def get_business_metrics(self):
        """Get key business metrics"""
        conn = sqlite3.connect('basketball_analysis.db')
        cursor = conn.cursor()
        
        # Monthly recurring revenue
        cursor.execute('''
            SELECT 
                COUNT(CASE WHEN subscription_type = 'starter' THEN 1 END) * 19 +
                COUNT(CASE WHEN subscription_type = 'pro' THEN 1 END) * 49 +
                COUNT(CASE WHEN subscription_type = 'coach' THEN 1 END) * 99 as mrr
            FROM users WHERE subscription_status = 'active'
        ''')
        mrr = cursor.fetchone()[0] or 0
        
        # User metrics
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE subscription_type != "free"')
        paid_users = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT COUNT(*) FROM users 
            WHERE created_at >= date('now', '-30 days')
        ''')
        new_users_30d = cursor.fetchone()[0]
        
        # Usage metrics
        cursor.execute('SELECT COUNT(*) FROM analysis_jobs')
        total_analyses = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT COUNT(*) FROM analysis_jobs 
            WHERE created_at >= date('now', '-30 days')
        ''')
        analyses_30d = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'mrr': mrr,
            'total_users': total_users,
            'paid_users': paid_users,
            'conversion_rate': (paid_users / total_users * 100) if total_users > 0 else 0,
            'new_users_30d': new_users_30d,
            'total_analyses': total_analyses,
            'analyses_30d': analyses_30d
        }
```

---

## 8. Deployment Configuration

### 8.1 Production Environment Variables
```bash
# File: .env.production
# Database
DATABASE_URL=postgresql://user:password@host:port/database

# Stripe Configuration
STRIPE_SECRET_KEY=sk_live_your_live_secret_key
STRIPE_PUBLISHABLE_KEY=pk_live_your_live_publishable_key  
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# JWT Secret
JWT_SECRET_KEY=your_super_secure_jwt_secret_256_bits_minimum

# OAuth Configuration
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Email Configuration (for notifications)
SENDGRID_API_KEY=your_sendgrid_api_key
SUPPORT_EMAIL=support@yourdomain.com

# Cloud Storage
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json

# Monitoring
SENTRY_DSN=your_sentry_dsn_for_error_tracking

# Rate Limiting
REDIS_URL=redis://localhost:6379/0

# Feature Flags
ENABLE_SIGNUP=true
ENABLE_FREE_TIER=true
MAINTENANCE_MODE=false
```

### 8.2 Updated App Engine Configuration
```yaml
# File: app.yaml
runtime: python39

env_variables:
  FLASK_ENV: production
  DATABASE_URL: postgresql://user:pass@host/db
  STRIPE_SECRET_KEY: sk_live_xxxxx
  JWT_SECRET_KEY: your_jwt_secret

automatic_scaling:
  target_cpu_utilization: 0.65
  min_instances: 2
  max_instances: 20
  
resources:
  cpu: 2
  memory_gb: 4
  disk_size_gb: 10

handlers:
- url: /static
  static_dir: static
  secure: always

- url: /.*
  script: auto
  secure: always
```

---

## 🚀 Implementation Priority

### Phase 1 (Week 1-2): Core Commercial Features
1. **User Dashboard** - Complete user interface
2. **Subscription Management** - Stripe integration
3. **Usage Tracking** - Enforce subscription limits
4. **Database Updates** - Enhanced schema

### Phase 2 (Week 3-4): Security & Support  
1. **Rate Limiting** - Prevent abuse
2. **Support System** - Customer help desk
3. **Analytics Dashboard** - Business metrics
4. **Legal Integration** - Terms/Privacy display

### Phase 3 (Week 5-6): Production Readiness
1. **Monitoring** - Error tracking and alerts
2. **Performance** - Caching and optimization
3. **Testing** - Load testing and validation
4. **Documentation** - User guides and API docs

**🎯 This implementation provides a complete commercial-ready platform building on your existing V9 infrastructure while adding essential business features for monetization and scale.**
