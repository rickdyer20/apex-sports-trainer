# DEPLOYMENT PACKAGE FOR APEXSPORTS-LLC.COM
# Copy these files to your server

## ESSENTIAL FILES TO UPLOAD:

### Core Application Files:
1. complete_web_app.py          # Main Flask application
2. enhanced_payment_manager.py  # Stripe payment processing
3. user_analysis_tracker.py     # Usage tracking system
4. .env                         # Environment variables (with live keys)

### Templates and Static Files:
5. templates/pricing_with_onetime.html    # Pricing page
6. templates/privacy_policy.md            # Privacy policy
7. terms_of_service.md                    # Terms of service

### Analysis Engine (Optional - for full functionality):
8. basketball_analysis_service.py         # Core analysis engine
9. pdf_generator.py                       # PDF report generation

## DEPLOYMENT COMMANDS:

### 1. Install Dependencies on Server:
```bash
pip install flask stripe python-dotenv opencv-python mediapipe numpy
```

### 2. Set Environment Variables:
Make sure .env file contains:
```
STRIPE_PUBLISHABLE_KEY=pk_live_51RtbJzQkZf3dUgUP...
STRIPE_SECRET_KEY=sk_live_51RtbJzQkZf3dUgUP...
STRIPE_WEBHOOK_SECRET=whsec_FruVgwdWGPf0nKrHgE9MsHhrTgcqCdTp
SECRET_KEY=apex-sports-llc-super-secure-production-key-v9-2025
FLASK_ENV=production
FLASK_DEBUG=False
FRONTEND_URL=https://apexsports-llc.com
```

### 3. Start the Application:
```bash
python complete_web_app.py
```

OR for production with Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:80 complete_web_app:app
```

## POST-DEPLOYMENT CHECKLIST:

1. ✅ Verify https://apexsports-llc.com loads
2. ✅ Test https://apexsports-llc.com/pricing
3. ✅ Verify Stripe payments work
4. ✅ Test webhook endpoint: https://apexsports-llc.com/webhook
5. ✅ Check legal pages: /terms and /privacy

## READY FOR LIVE PAYMENTS!
