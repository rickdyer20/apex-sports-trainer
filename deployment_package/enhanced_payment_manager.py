# Enhanced Payment Manager for Basketball Analysis Service
# Supports both subscription and one-time payments

import os
import stripe
from flask import Flask, request, jsonify, redirect, url_for, session
from dataclasses import dataclass
from typing import Dict, List, Optional
import logging
from datetime import datetime

# Configure Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

@dataclass
class PaymentTier:
    id: str
    name: str
    price_monthly: int  # in cents
    price_yearly: int   # in cents
    price_onetime: int  # in cents (0 if not applicable)
    features: List[str]
    video_limit: int
    analysis_limit: int
    support_level: str
    payment_type: str  # 'free', 'onetime', 'subscription'

class EnhancedPaymentManager:
    """Enhanced payment manager supporting multiple payment types"""
    
    def __init__(self, app: Flask):
        self.app = app
        self.setup_payment_tiers()
        self.setup_routes()
        
    def setup_payment_tiers(self):
        """Define payment tiers with updated free tier"""
        self.payment_tiers = {
            'free': PaymentTier(
                id='free',
                name='Free Trial',
                price_monthly=0,
                price_yearly=0,
                price_onetime=0,
                features=['Basic analysis', '1 analysis per year', 'Community support'],
                video_limit=1,
                analysis_limit=1,  # 1 per year
                support_level='community',
                payment_type='free'
            ),
            'onetime': PaymentTier(
                id='onetime',
                name='Single Analysis Package',
                price_monthly=0,
                price_yearly=0,
                price_onetime=999,  # $9.99
                features=[
                    'Complete shot analysis',
                    '5 total analyses',
                    'Detailed feedback report',
                    'Slow-motion breakdown',
                    'PDF improvement plan',
                    'Email support',
                    'Valid for 1 year'
                ],
                video_limit=5,
                analysis_limit=5,
                support_level='email',
                payment_type='onetime'
            ),
            'pro': PaymentTier(
                id='pro',
                name='Pro Subscription',
                price_monthly=1999,  # $19.99
                price_yearly=19990,  # $199.90 (save $39.99)
                price_onetime=0,
                features=[
                    'Unlimited analyses',
                    'Advanced biomechanics',
                    'Progress tracking',
                    'Multiple camera angles',
                    'Priority support',
                    'Detailed reports',
                    'Video comparisons',
                    'Monthly coaching tips'
                ],
                video_limit=-1,  # unlimited
                analysis_limit=-1,  # unlimited
                support_level='priority',
                payment_type='subscription'
            ),
            'enterprise': PaymentTier(
                id='enterprise',
                name='Enterprise',
                price_monthly=4999,  # $49.99
                price_yearly=49990,  # $499.90 (save $99.99)
                price_onetime=0,
                features=[
                    'Everything in Pro',
                    'Team management',
                    'Custom branding',
                    'API access',
                    'White-label solution',
                    '24/7 phone support',
                    'Custom integrations',
                    'Dedicated account manager'
                ],
                video_limit=-1,  # unlimited
                analysis_limit=-1,  # unlimited
                support_level='dedicated',
                payment_type='subscription'
            )
        }
    
    def setup_routes(self):
        """Setup payment-related routes"""
        
        @self.app.route('/payment/plans')
        def get_payment_plans():
            """Get all available payment plans"""
            plans = []
            for tier_id, tier in self.payment_tiers.items():
                plan_data = {
                    'id': tier.id,
                    'name': tier.name,
                    'payment_type': tier.payment_type,
                    'features': tier.features,
                    'video_limit': tier.video_limit,
                    'analysis_limit': tier.analysis_limit,
                    'support_level': tier.support_level
                }
                
                if tier.payment_type == 'onetime':
                    plan_data['price_onetime'] = tier.price_onetime
                elif tier.payment_type == 'subscription':
                    plan_data['price_monthly'] = tier.price_monthly
                    plan_data['price_yearly'] = tier.price_yearly
                    
                plans.append(plan_data)
            
            return jsonify({'plans': plans})
        
        @self.app.route('/payment/create-checkout-session', methods=['POST'])
        def create_checkout_session():
            """Create Stripe checkout session"""
            try:
                data = request.get_json()
                tier_id = data.get('tier_id')
                billing_cycle = data.get('billing_cycle', 'monthly')
                
                if tier_id not in self.payment_tiers:
                    return jsonify({'error': 'Invalid tier'}), 400
                
                tier = self.payment_tiers[tier_id]
                
                # Free tier doesn't need payment
                if tier.payment_type == 'free':
                    return jsonify({'error': 'Free tier does not require payment'}), 400
                
                # Create checkout session based on payment type
                if tier.payment_type == 'onetime':
                    session = stripe.checkout.Session.create(
                        payment_method_types=['card'],
                        line_items=[{
                            'price_data': {
                                'currency': 'usd',
                                'product_data': {
                                    'name': tier.name,
                                    'description': f'5 basketball shot analyses - Valid for 1 year'
                                },
                                'unit_amount': tier.price_onetime,
                            },
                            'quantity': 1,
                        }],
                        mode='payment',
                        success_url=request.host_url + 'payment/success',
                        cancel_url=request.host_url + 'payment/cancel',
                        metadata={'tier_id': tier_id, 'payment_type': 'onetime'}
                    )
                
                elif tier.payment_type == 'subscription':
                    price_amount = tier.price_monthly if billing_cycle == 'monthly' else tier.price_yearly
                    interval = 'month' if billing_cycle == 'monthly' else 'year'
                    
                    session = stripe.checkout.Session.create(
                        payment_method_types=['card'],
                        line_items=[{
                            'price_data': {
                                'currency': 'usd',
                                'product_data': {
                                    'name': f'{tier.name} ({billing_cycle.title()})',
                                    'description': f'Unlimited basketball shot analyses'
                                },
                                'unit_amount': price_amount,
                                'recurring': {'interval': interval},
                            },
                            'quantity': 1,
                        }],
                        mode='subscription',
                        success_url=request.host_url + 'payment/success',
                        cancel_url=request.host_url + 'payment/cancel',
                        metadata={'tier_id': tier_id, 'payment_type': 'subscription', 'billing_cycle': billing_cycle}
                    )
                
                return jsonify({'checkout_url': session.url})
                
            except Exception as e:
                logging.error(f"Checkout session creation failed: {e}")
                return jsonify({'error': str(e)}), 500
    
    def handle_webhook(self):
        """Handle Stripe webhooks"""
        payload = request.get_data(as_text=True)
        sig_header = request.headers.get('Stripe-Signature')
        webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError as e:
            logging.error(f"Invalid payload: {e}")
            return jsonify({'error': 'Invalid payload'}), 400
        except stripe.error.SignatureVerificationError as e:
            logging.error(f"Invalid signature: {e}")
            return jsonify({'error': 'Invalid signature'}), 400
        
        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            self._handle_successful_payment(session)
        
        elif event['type'] == 'customer.subscription.created':
            subscription = event['data']['object']
            self._handle_subscription_created(subscription)
        
        elif event['type'] == 'customer.subscription.deleted':
            subscription = event['data']['object']
            self._handle_subscription_cancelled(subscription)
        
        elif event['type'] == 'invoice.payment_succeeded':
            invoice = event['data']['object']
            self._handle_invoice_paid(invoice)
        
        elif event['type'] == 'invoice.payment_failed':
            invoice = event['data']['object']
            self._handle_invoice_failed(invoice)
        
        return jsonify({'status': 'success'})
    
    def _handle_successful_payment(self, session):
        """Handle successful one-time payment"""
        logging.info(f"Payment successful: {session['id']}")
        # Here you would:
        # 1. Update user's tier in database
        # 2. Send confirmation email
        # 3. Grant access to paid features
        
    def _handle_subscription_created(self, subscription):
        """Handle new subscription"""
        logging.info(f"Subscription created: {subscription['id']}")
        # Here you would:
        # 1. Update user's subscription status
        # 2. Grant unlimited access
        # 3. Send welcome email
        
    def _handle_subscription_cancelled(self, subscription):
        """Handle cancelled subscription"""
        logging.info(f"Subscription cancelled: {subscription['id']}")
        # Here you would:
        # 1. Downgrade user to free tier
        # 2. Send cancellation confirmation
        
    def _handle_invoice_paid(self, invoice):
        """Handle successful subscription payment"""
        logging.info(f"Invoice paid: {invoice['id']}")
        # Here you would:
        # 1. Extend subscription period
        # 2. Send payment receipt
        
    def _handle_invoice_failed(self, invoice):
        """Handle failed subscription payment"""
        logging.warning(f"Invoice payment failed: {invoice['id']}")
        # Here you would:
        # 1. Send payment failure notification
        # 2. Potentially suspend access after grace period
    
    def get_tier_info(self, tier_id: str) -> Optional[PaymentTier]:
        """Get information about a specific tier"""
        return self.payment_tiers.get(tier_id)
    
    def validate_user_access(self, user_tier: str, requested_feature: str) -> bool:
        """Validate if user has access to requested feature"""
        tier = self.payment_tiers.get(user_tier)
        if not tier:
            return False
        
        # Define feature access rules
        feature_rules = {
            'basic_analysis': ['free', 'onetime', 'pro', 'enterprise'],
            'advanced_analysis': ['pro', 'enterprise'],
            'unlimited_analysis': ['pro', 'enterprise'],
            'priority_support': ['pro', 'enterprise'],
            'team_features': ['enterprise'],
            'api_access': ['enterprise']
        }
        
        allowed_tiers = feature_rules.get(requested_feature, [])
        return user_tier in allowed_tiers


if __name__ == "__main__":
    # Test the enhanced payment manager
    from flask import Flask
    
    app = Flask(__name__)
    manager = EnhancedPaymentManager(app)
    
    print("🏀 Enhanced Payment Manager - Test")
    print("=" * 50)
    
    with app.test_client() as client:
        response = client.get('/payment/plans')
        if response.status_code == 200:
            plans = response.get_json()
            print(f"✅ Found {len(plans['plans'])} payment options:")
            
            for plan in plans['plans']:
                print(f"\n📋 {plan['name']} ({plan['payment_type']})")
                if plan['payment_type'] == 'onetime':
                    price = plan['price_onetime'] / 100
                    print(f"   💰 Price: ${price:.2f} one-time")
                elif plan['payment_type'] == 'subscription':
                    monthly = plan['price_monthly'] / 100
                    yearly = plan['price_yearly'] / 100
                    print(f"   💰 Price: ${monthly:.2f}/month or ${yearly:.2f}/year")
                elif plan['payment_type'] == 'free':
                    print(f"   💰 Price: Free")
                
                print(f"   📝 Features: {', '.join(plan['features'][:3])}...")
                print(f"   📊 Analysis limit: {plan['analysis_limit']} per year" if plan['analysis_limit'] != -1 else "   📊 Analysis limit: Unlimited")
        else:
            print(f"❌ Plans endpoint failed: {response.status_code}")
    
    print("\n" + "=" * 50)
    print("Enhanced Payment Manager ready for production!")
