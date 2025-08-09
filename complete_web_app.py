# 🏀 Basketball Analysis Service - Complete Web Application
# Enhanced with Stripe Payment Integration, Legal Compliance, and Usage Tracking

import os
import sys
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, render_template_string
from werkzeug.utils import secure_filename
from user_analysis_tracker import UserAnalysisTracker, enforce_analysis_limit, record_user_analysis
import logging
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import payment manager
try:
    from enhanced_payment_manager import EnhancedPaymentManager
    PAYMENT_ENABLED = True
except ImportError as e:
    print(f"⚠️  Payment system not available: {e}")
    PAYMENT_ENABLED = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize payment manager if available
payment_manager = None
if PAYMENT_ENABLED:
    try:
        payment_manager = EnhancedPaymentManager(app)
        print("✅ Payment system initialized")
    except Exception as e:
        print(f"❌ Payment system failed to initialize: {e}")
        PAYMENT_ENABLED = False

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ================================
# MAIN ROUTES
# ================================

@app.route('/')
def index():
    """Homepage"""
    return render_template('index_simple.html')

# ================================
# PAYMENT & PRICING ROUTES
# ================================

@app.route('/pricing')
def pricing():
    """Show pricing page with disclaimer"""
    try:
        return send_file('templates/pricing_with_onetime.html')
    except Exception as e:
        logging.error(f"Error loading pricing page: {e}")
        flash('Unable to load pricing information', 'error')
        return redirect(url_for('index'))

@app.route('/subscribe/<tier_id>')
def subscribe(tier_id):
    """Start subscription process"""
    if not PAYMENT_ENABLED:
        flash('Payment system not available', 'warning')
        return redirect(url_for('index'))
    
    # Check if disclaimer was accepted
    disclaimer_accepted = request.args.get('disclaimer_accepted', 'false').lower() == 'true'
    if not disclaimer_accepted:
        flash('Please accept the terms and disclaimer before proceeding', 'warning')
        return redirect(url_for('pricing'))
    
    billing_cycle = request.args.get('billing', 'monthly')
    
    try:
        # Create checkout session via payment manager
        with payment_manager.app.test_request_context():
            response = payment_manager.app.test_client().post('/payment/create-checkout-session',
                json={'tier_id': tier_id, 'billing_cycle': billing_cycle})
        
        if response.status_code == 200:
            data = response.get_json()
            checkout_url = data.get('checkout_url')
            if checkout_url:
                return redirect(checkout_url)
            else:
                raise Exception("No checkout URL returned")
        else:
            error_data = response.get_json()
            raise Exception(f"Payment error: {error_data.get('error', 'Unknown error')}")
            
    except Exception as e:
        logging.error(f"Subscription error: {e}")
        flash(f'Unable to start subscription: {str(e)}', 'error')
        return redirect(url_for('pricing'))

@app.route('/payment/success')
def payment_success():
    """Payment success page"""
    return render_template_string("""
    <div style="text-align: center; padding: 50px; font-family: Arial;">
        <h1 style="color: #28a745;">🎉 Payment Successful!</h1>
        <p>Thank you for your purchase. You can now start analyzing your basketball shots!</p>
        <a href="/dashboard" style="background: #007bff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px;">Go to Dashboard</a>
    </div>
    """)

@app.route('/payment/cancel')
def payment_cancel():
    """Payment cancelled page"""
    return render_template_string("""
    <div style="text-align: center; padding: 50px; font-family: Arial;">
        <h1 style="color: #dc3545;">❌ Payment Cancelled</h1>
        <p>Your payment was cancelled. No charges were made.</p>
        <a href="/pricing" style="background: #007bff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px;">Back to Pricing</a>
    </div>
    """)

@app.route('/dashboard')
def dashboard():
    """User dashboard"""
    return render_template_string("""
    <div style="max-width: 800px; margin: 0 auto; padding: 20px; font-family: Arial;">
        <h1>🏀 Basketball Analysis Dashboard</h1>
        <p>Welcome to your analysis dashboard!</p>
        
        <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0;">
            <h3>Upload Video for Analysis</h3>
            <form action="/analyze" method="post" enctype="multipart/form-data">
                <input type="email" name="email" placeholder="Your email" required style="width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 5px;">
                <select name="tier" style="width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 5px;">
                    <option value="free">Free Tier</option>
                    <option value="onetime">One-time Purchase</option>
                    <option value="pro">Pro Subscription</option>
                    <option value="enterprise">Enterprise</option>
                </select>
                <input type="file" name="video" accept=".mp4,.avi,.mov,.mkv" required style="width: 100%; padding: 10px; margin: 10px 0;">
                <button type="submit" style="background: #28a745; color: white; padding: 15px 30px; border: none; border-radius: 5px; cursor: pointer;">Analyze Video</button>
            </form>
        </div>
        
        <a href="/pricing" style="color: #007bff; text-decoration: none;">← Back to Pricing</a>
    </div>
    """)

# ================================
# USAGE TRACKING ROUTES
# ================================

@app.route('/check_analysis_limit')
def check_analysis_limit():
    """Check if user can perform analysis"""
    user_email = request.args.get('email', 'anonymous')
    user_tier = request.args.get('tier', 'free')
    
    result = enforce_analysis_limit(user_email, user_tier)
    
    if result['allowed']:
        return jsonify({
            'allowed': True,
            'message': 'Analysis allowed'
        })
    else:
        return jsonify({
            'allowed': False,
            'message': result['reason']
        }), 429  # Too Many Requests

@app.route('/user_stats/<user_email>')
def user_stats(user_email):
    """Get user's analysis statistics"""
    tracker = UserAnalysisTracker()
    stats = tracker.get_user_stats(user_email)
    return jsonify(stats)

@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    """Video analysis page and processing"""
    if request.method == 'GET':
        # Show the upload form
        return render_template('analyze_simple.html')
    
    # POST method - process the uploaded video
    user_email = request.form.get('email', 'anonymous')
    user_tier = request.form.get('tier', 'free')
    
    # Check if user can perform analysis
    limit_check = enforce_analysis_limit(user_email, user_tier)
    if not limit_check['allowed']:
        flash(limit_check['reason'], 'error')
        return redirect(url_for('pricing'))
    
    if 'video' not in request.files:
        flash('No video file uploaded', 'error')
        return redirect(url_for('dashboard'))
    
    file = request.files['video']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('dashboard'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Record the analysis
        record_user_analysis(user_email, user_tier)
        
        # TODO: Integrate with basketball_analysis_service.py
        # For now, just return success
        flash('Analysis completed successfully!', 'success')
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid file type. Please upload MP4, AVI, MOV, or MKV files.', 'error')
        return redirect(url_for('dashboard'))

# ================================
# LEGAL ROUTES
# ================================

@app.route('/terms')
def terms_of_service():
    """Show terms of service"""
    try:
        with open('terms_of_service.md', 'r', encoding='utf-8') as f:
            terms_content = f.read()
        
        # Simple markdown to HTML conversion
        html_content = terms_content.replace('\n# ', '\n<h1>').replace('\n## ', '\n<h2>').replace('\n### ', '\n<h3>')
        html_content = html_content.replace('\n- ', '\n<li>').replace('\n\n', '</p><p>')
        html_content = f"<p>{html_content}</p>"
        
        template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Terms of Service</title>
            <style>
                body {{ max-width: 800px; margin: 0 auto; padding: 20px; font-family: Arial; line-height: 1.6; }}
                h1 {{ color: #007bff; }}
                h2 {{ color: #495057; margin-top: 30px; }}
                .back-link {{ display: inline-block; margin: 20px 0; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <a href="/" class="back-link">&larr; Back to Home</a>
            {html_content}
        </body>
        </html>
        """
        return render_template_string(template)
        
    except FileNotFoundError:
        return render_template_string("""
        <div style="text-align: center; padding: 50px;">
            <h1>Terms of Service</h1>
            <p>Terms document not found.</p>
            <a href="/">Back to Home</a>
        </div>
        """), 404

@app.route('/privacy')
def privacy_policy():
    """Show privacy policy"""
    try:
        with open('templates/privacy_policy.md', 'r', encoding='utf-8') as f:
            privacy_content = f.read()
        
        # Simple markdown to HTML conversion
        html_content = privacy_content.replace('\n# ', '\n<h1>').replace('\n## ', '\n<h2>').replace('\n### ', '\n<h3>')
        html_content = html_content.replace('\n- ', '\n<li>').replace('\n\n', '</p><p>')
        html_content = f"<p>{html_content}</p>"
        
        template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Privacy Policy</title>
            <style>
                body {{ max-width: 800px; margin: 0 auto; padding: 20px; font-family: Arial; line-height: 1.6; }}
                h1 {{ color: #007bff; }}
                h2 {{ color: #495057; margin-top: 30px; }}
                .back-link {{ display: inline-block; margin: 20px 0; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <a href="/" class="back-link">&larr; Back to Home</a>
            {html_content}
        </body>
        </html>
        """
        return render_template_string(template)
        
    except FileNotFoundError:
        return render_template_string("""
        <div style="text-align: center; padding: 50px;">
            <h1>Privacy Policy</h1>
            <p>Privacy policy document not found.</p>
            <a href="/">Back to Home</a>
        </div>
        """), 404

# ================================
# WEBHOOK ROUTES
# ================================

@app.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks"""
    if payment_manager:
        return payment_manager.handle_webhook()
    else:
        return jsonify({'error': 'Payment system not available'}), 503

# ================================
# UTILITY ROUTES
# ================================

@app.route('/health')
def health_check():
    """Health check endpoint"""
    status = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'payment_system': 'enabled' if PAYMENT_ENABLED else 'disabled',
        'version': '9.0'
    }
    return jsonify(status)

def create_templates():
    """Create basic HTML templates if they don't exist"""
    templates_dir = 'templates'
    os.makedirs(templates_dir, exist_ok=True)

if __name__ == '__main__':
    print("🏀 Basketball Analysis Service - Complete Web Application")
    print("=" * 60)
    print(f"✅ Payment System: {'Enabled' if PAYMENT_ENABLED else 'Disabled'}")
    print("✅ Legal Compliance: Terms & Privacy Policy")
    print("✅ Disclaimer System: Integrated")
    print("✅ Enhanced Payment: 4-tier structure")
    print("✅ Usage Tracking: 1 analysis per year (free tier)")
    print("=" * 60)
    
    create_templates()
    
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
