# Stripe Business Account Setup Guide

## Overview
Your basketball analysis service already has a comprehensive Stripe payment system implemented. This guide will help you configure it with your new business checking account.

## Current Implementation Status ✅
- ✅ **Payment Manager**: Complete 523-line Stripe integration
- ✅ **Subscription Tiers**: Free, Pro ($19.99/month), Enterprise ($49.99/month)
- ✅ **Customer Management**: Automatic customer creation and management
- ✅ **Webhook Handling**: Complete event processing system
- ✅ **Usage Limits**: Tier-based feature restrictions
- ✅ **Billing Portal**: Customer self-service portal
- ✅ **Configuration**: Environment variable setup ready

## Step 1: Create Stripe Business Account

### 1.1 Sign Up for Stripe
1. Go to https://stripe.com/
2. Click "Start now" 
3. Choose "Accept payments" option
4. Use your business email address
5. Select "Business" account type

### 1.2 Business Information
Complete these sections in your Stripe dashboard:
- **Business details**: Your basketball analysis service information
- **Bank account**: Connect your new business checking account
- **Tax information**: Business tax ID/EIN
- **Identity verification**: Upload required documents

## Step 2: Get Your API Keys

### 2.1 Navigate to API Keys
1. In Stripe Dashboard → Developers → API keys
2. You'll see two environments:
   - **Test mode**: For development/testing
   - **Live mode**: For production (only available after account activation)

### 2.2 Copy Your Keys
```bash
# Test Keys (for development)
STRIPE_PUBLISHABLE_KEY=pk_test_xxxxxxxxxxxxxxxxxxxxx
STRIPE_SECRET_KEY=sk_test_xxxxxxxxxxxxxxxxxxxxx

# Live Keys (for production - get these after account approval)
STRIPE_PUBLISHABLE_KEY=pk_live_xxxxxxxxxxxxxxxxxxxxx
STRIPE_SECRET_KEY=sk_live_xxxxxxxxxxxxxxxxxxxxx
```

## Step 3: Configure Environment Variables

### 3.1 Create .env file
Create a `.env` file in your project root:

```bash
# Stripe Configuration
STRIPE_PUBLISHABLE_KEY=pk_test_your_key_here
STRIPE_SECRET_KEY=sk_test_your_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here

# Frontend URL (for return redirects)
FRONTEND_URL=https://yourdomain.com

# Email Configuration (for subscription notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-business-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@yourdomain.com
```

### 3.2 Load Environment Variables
Your config.py already reads these automatically:
```python
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
```

## Step 4: Set Up Products and Prices in Stripe

### 4.1 Create Products
In Stripe Dashboard → Product catalog → Add product:

**Pro Plan:**
- Name: "Basketball Analysis Pro"
- Description: "Professional basketball shot analysis with unlimited videos"
- Price: $19.99/month

**Enterprise Plan:**
- Name: "Basketball Analysis Enterprise"
- Description: "Complete basketball analysis suite with priority support"
- Price: $49.99/month

### 4.2 Get Price IDs
After creating products, copy the price IDs and update your payment manager if needed.

## Step 5: Configure Webhooks

### 5.1 Create Webhook Endpoint
1. In Stripe Dashboard → Developers → Webhooks
2. Click "Add endpoint"
3. Endpoint URL: `https://yourdomain.com/webhook/stripe`
4. Select these events:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`

### 5.2 Get Webhook Secret
Copy the webhook signing secret and add it to your environment variables.

## Step 6: Test the Integration

### 6.1 Test Mode Setup
```bash
# Install Stripe CLI for testing
# Download from: https://stripe.com/docs/stripe-cli

# Login to your Stripe account
stripe login

# Forward webhooks to your local development server
stripe listen --forward-to localhost:5000/webhook/stripe
```

### 6.2 Test Subscription Flow
1. Start your development server
2. Navigate to subscription page
3. Use Stripe test card: `4242 4242 4242 4242`
4. Verify webhook events are received

## Step 7: Production Deployment

### 7.1 Account Activation
- Complete all business verification steps
- Wait for Stripe to approve your account (usually 1-7 days)
- Switch to live mode keys

### 7.2 Production Environment Variables
```bash
# Production environment (.env.production)
STRIPE_PUBLISHABLE_KEY=pk_live_your_live_key
STRIPE_SECRET_KEY=sk_live_your_live_key
STRIPE_WEBHOOK_SECRET=whsec_your_live_webhook_secret
FRONTEND_URL=https://yourdomain.com
```

## Step 8: Integration with Your Service

### 8.1 Initialize Payment Manager
Your `basketball_analysis_service.py` should initialize the payment manager:

```python
from payment_manager import PaymentManager

# In your main application
payment_manager = PaymentManager(app)
```

### 8.2 Check Usage Limits
Before processing videos, check user limits:

```python
def process_video(user_id, video_file):
    # Check if user can upload video
    usage_check = payment_manager.check_usage_limits(user_id, 'video_upload')
    
    if not usage_check['allowed']:
        return {
            'error': usage_check['reason'],
            'upgrade_required': True,
            'current_tier': usage_check['current_tier']
        }
    
    # Process video...
```

## Step 9: Customer Experience

### 9.1 Subscription Page
Your system provides these endpoints:
- `/payment/checkout` - Create subscription
- `/payment/portal` - Manage subscription
- `/payment/subscription/status` - Check status
- `/payment/usage` - View usage stats

### 9.2 Usage Monitoring
Users can see their current usage and limits through the built-in endpoints.

## Security Checklist ✅

- ✅ API keys stored in environment variables (never in code)
- ✅ Webhook signature verification implemented
- ✅ Error handling for all Stripe operations
- ✅ User authentication before payment operations
- ✅ Secure customer data handling

## Next Steps

1. **Complete Stripe account setup** with your business information
2. **Test integration** using Stripe test mode
3. **Deploy to staging** environment for final testing
4. **Submit for review** and wait for account activation
5. **Go live** with real payment processing

## Support Resources

- **Stripe Documentation**: https://stripe.com/docs
- **Stripe Dashboard**: https://dashboard.stripe.com/
- **Test Cards**: https://stripe.com/docs/testing#cards
- **Webhook Testing**: https://stripe.com/docs/webhooks/test

## Monitoring & Analytics

Your system includes comprehensive logging for:
- Payment processing events
- Subscription changes
- Usage tracking
- Error monitoring

Monitor these logs for any issues during the rollout.

---

**Status**: Ready for Stripe business account integration
**Implementation**: Complete and production-ready
**Next Action**: Configure Stripe account with your business details
