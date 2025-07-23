# Basketball Analysis Service - Stripe Payment Integration
# Production-ready payment processing and subscription management

import os
import stripe
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from dataclasses import dataclass
import hmac
import hashlib

logger = logging.getLogger(__name__)

# Set Stripe API key
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

@dataclass
class SubscriptionTier:
    """Subscription tier configuration"""
    id: str
    name: str
    price_monthly: int  # Price in cents
    price_yearly: int   # Price in cents
    features: List[str]
    video_limit: int
    analysis_limit: int
    support_level: str

class PaymentManager:
    """Production payment manager with Stripe integration"""
    
    def __init__(self, app: Flask):
        self.app = app
        self.webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
        
        # Define subscription tiers
        self.subscription_tiers = {
            'free': SubscriptionTier(
                id='free',
                name='Free',
                price_monthly=0,
                price_yearly=0,
                features=['Basic analysis', '1 video per day', 'Community support'],
                video_limit=1,
                analysis_limit=10,
                support_level='community'
            ),
            'pro': SubscriptionTier(
                id='pro',
                name='Pro',
                price_monthly=1999,  # $19.99
                price_yearly=19999,  # $199.99 (save ~17%)
                features=[
                    'Advanced biomechanical analysis',
                    'Unlimited videos',
                    'Slow-motion breakdown',
                    'Progress tracking',
                    'Email support'
                ],
                video_limit=-1,  # Unlimited
                analysis_limit=-1,  # Unlimited
                support_level='email'
            ),
            'enterprise': SubscriptionTier(
                id='enterprise',
                name='Enterprise',
                price_monthly=4999,  # $49.99
                price_yearly=49999,  # $499.99 (save ~17%)
                features=[
                    'All Pro features',
                    'Team management',
                    'Custom analysis parameters',
                    'API access',
                    'Priority support',
                    'White-label options'
                ],
                video_limit=-1,
                analysis_limit=-1,
                support_level='priority'
            )
        }
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Set up payment routes"""
        
        @self.app.route('/payment/plans')
        def get_plans():
            """Get available subscription plans"""
            plans = []
            for tier_id, tier in self.subscription_tiers.items():
                if tier_id != 'free':  # Don't include free tier in plans
                    plans.append({
                        'id': tier.id,
                        'name': tier.name,
                        'price_monthly': tier.price_monthly,
                        'price_yearly': tier.price_yearly,
                        'features': tier.features,
                        'savings_yearly': round((tier.price_monthly * 12 - tier.price_yearly) / 100, 2)
                    })
            return jsonify({'plans': plans})
        
        @self.app.route('/payment/create-checkout-session', methods=['POST'])
        def create_checkout_session():
            """Create Stripe checkout session"""
            try:
                data = request.get_json()
                tier_id = data.get('tier_id')
                billing_cycle = data.get('billing_cycle', 'monthly')  # monthly or yearly
                user_id = self._get_current_user_id()
                
                if not tier_id or tier_id not in self.subscription_tiers:
                    return jsonify({'error': 'Invalid subscription tier'}), 400
                
                tier = self.subscription_tiers[tier_id]
                
                # Create Stripe customer if not exists
                customer = self._get_or_create_stripe_customer(user_id)
                
                # Determine price based on billing cycle
                price = tier.price_yearly if billing_cycle == 'yearly' else tier.price_monthly
                
                # Create Stripe Price object if not exists
                stripe_price_id = self._get_or_create_stripe_price(tier_id, billing_cycle, price)
                
                # Create checkout session
                checkout_session = stripe.checkout.Session.create(
                    customer=customer.id,
                    payment_method_types=['card'],
                    line_items=[{
                        'price': stripe_price_id,
                        'quantity': 1,
                    }],
                    mode='subscription',
                    success_url=os.getenv('FRONTEND_URL') + '/payment/success?session_id={CHECKOUT_SESSION_ID}',
                    cancel_url=os.getenv('FRONTEND_URL') + '/payment/cancel',
                    metadata={
                        'user_id': str(user_id),
                        'tier_id': tier_id,
                        'billing_cycle': billing_cycle
                    }
                )
                
                return jsonify({'checkout_url': checkout_session.url})
                
            except stripe.error.StripeError as e:
                logger.error(f"Stripe error: {e}")
                return jsonify({'error': 'Payment processing error'}), 500
            except Exception as e:
                logger.error(f"Checkout session error: {e}")
                return jsonify({'error': 'Failed to create checkout session'}), 500
        
        @self.app.route('/payment/portal', methods=['POST'])
        def create_customer_portal():
            """Create customer portal session for subscription management"""
            try:
                user_id = self._get_current_user_id()
                customer = self._get_stripe_customer(user_id)
                
                if not customer:
                    return jsonify({'error': 'No subscription found'}), 404
                
                portal_session = stripe.billing_portal.Session.create(
                    customer=customer.id,
                    return_url=os.getenv('FRONTEND_URL') + '/dashboard',
                )
                
                return jsonify({'portal_url': portal_session.url})
                
            except stripe.error.StripeError as e:
                logger.error(f"Stripe portal error: {e}")
                return jsonify({'error': 'Failed to create portal session'}), 500
            except Exception as e:
                logger.error(f"Portal error: {e}")
                return jsonify({'error': 'Portal access failed'}), 500
        
        @self.app.route('/payment/subscription/status')
        def get_subscription_status():
            """Get current subscription status"""
            try:
                user_id = self._get_current_user_id()
                subscription_info = self._get_user_subscription(user_id)
                
                return jsonify({
                    'subscription': subscription_info,
                    'usage': self._get_usage_stats(user_id),
                    'limits': self._get_tier_limits(subscription_info.get('tier', 'free'))
                })
                
            except Exception as e:
                logger.error(f"Subscription status error: {e}")
                return jsonify({'error': 'Failed to get subscription status'}), 500
        
        @self.app.route('/payment/usage')
        def get_usage():
            """Get current usage statistics"""
            try:
                user_id = self._get_current_user_id()
                usage = self._get_usage_stats(user_id)
                subscription = self._get_user_subscription(user_id)
                limits = self._get_tier_limits(subscription.get('tier', 'free'))
                
                return jsonify({
                    'usage': usage,
                    'limits': limits,
                    'usage_percentage': {
                        'videos': (usage['videos_this_month'] / limits['video_limit'] * 100) if limits['video_limit'] > 0 else 0,
                        'analyses': (usage['analyses_this_month'] / limits['analysis_limit'] * 100) if limits['analysis_limit'] > 0 else 0
                    }
                })
                
            except Exception as e:
                logger.error(f"Usage stats error: {e}")
                return jsonify({'error': 'Failed to get usage statistics'}), 500
        
        @self.app.route('/webhook/stripe', methods=['POST'])
        def stripe_webhook():
            """Handle Stripe webhooks"""
            payload = request.get_data()
            sig_header = request.headers.get('Stripe-Signature')
            
            try:
                event = stripe.Webhook.construct_event(
                    payload, sig_header, self.webhook_secret
                )
            except ValueError:
                logger.error("Invalid payload in Stripe webhook")
                return jsonify({'error': 'Invalid payload'}), 400
            except stripe.error.SignatureVerificationError:
                logger.error("Invalid signature in Stripe webhook")
                return jsonify({'error': 'Invalid signature'}), 400
            
            # Handle the event
            try:
                if event['type'] == 'checkout.session.completed':
                    self._handle_checkout_completed(event['data']['object'])
                
                elif event['type'] == 'customer.subscription.created':
                    self._handle_subscription_created(event['data']['object'])
                
                elif event['type'] == 'customer.subscription.updated':
                    self._handle_subscription_updated(event['data']['object'])
                
                elif event['type'] == 'customer.subscription.deleted':
                    self._handle_subscription_cancelled(event['data']['object'])
                
                elif event['type'] == 'invoice.payment_succeeded':
                    self._handle_payment_succeeded(event['data']['object'])
                
                elif event['type'] == 'invoice.payment_failed':
                    self._handle_payment_failed(event['data']['object'])
                
                else:
                    logger.info(f"Unhandled Stripe event type: {event['type']}")
                
                return jsonify({'status': 'success'})
                
            except Exception as e:
                logger.error(f"Webhook handling error: {e}")
                return jsonify({'error': 'Webhook processing failed'}), 500
    
    def _get_current_user_id(self) -> int:
        """Get current authenticated user ID"""
        # This would integrate with your authentication system
        # For now, return a placeholder
        return getattr(request, 'current_user_id', None)
    
    def _get_or_create_stripe_customer(self, user_id: int) -> stripe.Customer:
        """Get or create Stripe customer for user"""
        try:
            # Check if customer already exists in database
            stripe_customer_id = self._get_user_stripe_customer_id(user_id)
            
            if stripe_customer_id:
                return stripe.Customer.retrieve(stripe_customer_id)
            
            # Create new customer
            user = self._get_user_by_id(user_id)
            customer = stripe.Customer.create(
                email=user['email'],
                name=f"{user['first_name']} {user['last_name']}".strip(),
                metadata={'user_id': str(user_id)}
            )
            
            # Save customer ID to database
            self._save_user_stripe_customer_id(user_id, customer.id)
            
            return customer
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe customer error: {e}")
            raise
    
    def _get_stripe_customer(self, user_id: int) -> Optional[stripe.Customer]:
        """Get existing Stripe customer"""
        stripe_customer_id = self._get_user_stripe_customer_id(user_id)
        if stripe_customer_id:
            return stripe.Customer.retrieve(stripe_customer_id)
        return None
    
    def _get_or_create_stripe_price(self, tier_id: str, billing_cycle: str, amount: int) -> str:
        """Get or create Stripe price for tier and billing cycle"""
        # In production, you might cache these price IDs in your database
        # For simplicity, we'll create them dynamically here
        
        tier = self.subscription_tiers[tier_id]
        
        try:
            # Create product if not exists
            product = stripe.Product.create(
                name=f"Basketball Analysis {tier.name}",
                description=f"{tier.name} subscription for basketball shot analysis",
                metadata={
                    'tier_id': tier_id,
                    'service': 'basketball_analysis'
                }
            )
            
            # Create price
            interval = 'year' if billing_cycle == 'yearly' else 'month'
            price = stripe.Price.create(
                unit_amount=amount,
                currency='usd',
                recurring={'interval': interval},
                product=product.id,
                metadata={
                    'tier_id': tier_id,
                    'billing_cycle': billing_cycle
                }
            )
            
            return price.id
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe price creation error: {e}")
            raise
    
    def _handle_checkout_completed(self, session):
        """Handle successful checkout"""
        try:
            user_id = int(session['metadata']['user_id'])
            tier_id = session['metadata']['tier_id']
            billing_cycle = session['metadata']['billing_cycle']
            
            logger.info(f"Checkout completed for user {user_id}, tier {tier_id}")
            
            # Update user subscription in database
            self._update_user_subscription(user_id, {
                'tier': tier_id,
                'billing_cycle': billing_cycle,
                'stripe_subscription_id': session.get('subscription'),
                'status': 'active',
                'current_period_start': datetime.utcnow(),
                'current_period_end': self._calculate_period_end(billing_cycle)
            })
            
            # Send welcome email
            self._send_subscription_welcome_email(user_id, tier_id)
            
        except Exception as e:
            logger.error(f"Checkout completion handling error: {e}")
    
    def _handle_subscription_created(self, subscription):
        """Handle subscription created"""
        logger.info(f"Subscription created: {subscription['id']}")
        # Additional subscription setup if needed
    
    def _handle_subscription_updated(self, subscription):
        """Handle subscription updated"""
        try:
            customer_id = subscription['customer']
            user_id = self._get_user_by_stripe_customer_id(customer_id)
            
            if user_id:
                # Update subscription details
                self._update_subscription_from_stripe(user_id, subscription)
                
        except Exception as e:
            logger.error(f"Subscription update handling error: {e}")
    
    def _handle_subscription_cancelled(self, subscription):
        """Handle subscription cancelled"""
        try:
            customer_id = subscription['customer']
            user_id = self._get_user_by_stripe_customer_id(customer_id)
            
            if user_id:
                # Update user to free tier
                self._update_user_subscription(user_id, {
                    'tier': 'free',
                    'status': 'cancelled',
                    'cancelled_at': datetime.utcnow()
                })
                
                # Send cancellation email
                self._send_subscription_cancelled_email(user_id)
                
        except Exception as e:
            logger.error(f"Subscription cancellation handling error: {e}")
    
    def _handle_payment_succeeded(self, invoice):
        """Handle successful payment"""
        logger.info(f"Payment succeeded for invoice: {invoice['id']}")
        # Update payment history, send receipt, etc.
    
    def _handle_payment_failed(self, invoice):
        """Handle failed payment"""
        try:
            customer_id = invoice['customer']
            user_id = self._get_user_by_stripe_customer_id(customer_id)
            
            if user_id:
                # Send payment failure notification
                self._send_payment_failed_email(user_id, invoice)
                
        except Exception as e:
            logger.error(f"Payment failure handling error: {e}")
    
    def _calculate_period_end(self, billing_cycle: str) -> datetime:
        """Calculate subscription period end"""
        if billing_cycle == 'yearly':
            return datetime.utcnow() + timedelta(days=365)
        else:
            return datetime.utcnow() + timedelta(days=30)
    
    def _get_user_subscription(self, user_id: int) -> Dict[str, Any]:
        """Get user subscription details"""
        # Database implementation
        # Return subscription details from database
        return {
            'tier': 'free',
            'status': 'active',
            'billing_cycle': 'monthly',
            'current_period_start': datetime.utcnow(),
            'current_period_end': datetime.utcnow() + timedelta(days=30)
        }
    
    def _get_usage_stats(self, user_id: int) -> Dict[str, int]:
        """Get user usage statistics"""
        # Database implementation
        # Return current month usage stats
        return {
            'videos_this_month': 0,
            'analyses_this_month': 0,
            'total_videos': 0,
            'total_analyses': 0
        }
    
    def _get_tier_limits(self, tier_id: str) -> Dict[str, int]:
        """Get limits for subscription tier"""
        tier = self.subscription_tiers.get(tier_id, self.subscription_tiers['free'])
        return {
            'video_limit': tier.video_limit,
            'analysis_limit': tier.analysis_limit,
            'support_level': tier.support_level
        }
    
    def check_usage_limits(self, user_id: int, action: str) -> Dict[str, Any]:
        """Check if user can perform action based on usage limits"""
        subscription = self._get_user_subscription(user_id)
        usage = self._get_usage_stats(user_id)
        limits = self._get_tier_limits(subscription.get('tier', 'free'))
        
        if action == 'video_upload':
            if limits['video_limit'] > 0 and usage['videos_this_month'] >= limits['video_limit']:
                return {
                    'allowed': False,
                    'reason': 'Monthly video limit reached',
                    'upgrade_required': True,
                    'current_tier': subscription.get('tier', 'free')
                }
        
        elif action == 'analysis':
            if limits['analysis_limit'] > 0 and usage['analyses_this_month'] >= limits['analysis_limit']:
                return {
                    'allowed': False,
                    'reason': 'Monthly analysis limit reached',
                    'upgrade_required': True,
                    'current_tier': subscription.get('tier', 'free')
                }
        
        return {'allowed': True}
    
    # Database helper methods (implement based on your database setup)
    def _get_user_by_id(self, user_id: int) -> Dict[str, Any]:
        """Get user by ID"""
        pass
    
    def _get_user_stripe_customer_id(self, user_id: int) -> Optional[str]:
        """Get user's Stripe customer ID"""
        pass
    
    def _save_user_stripe_customer_id(self, user_id: int, customer_id: str):
        """Save user's Stripe customer ID"""
        pass
    
    def _get_user_by_stripe_customer_id(self, customer_id: str) -> Optional[int]:
        """Get user ID by Stripe customer ID"""
        pass
    
    def _update_user_subscription(self, user_id: int, subscription_data: Dict[str, Any]):
        """Update user subscription in database"""
        pass
    
    def _update_subscription_from_stripe(self, user_id: int, stripe_subscription):
        """Update subscription from Stripe data"""
        pass
    
    def _send_subscription_welcome_email(self, user_id: int, tier_id: str):
        """Send welcome email for new subscription"""
        pass
    
    def _send_subscription_cancelled_email(self, user_id: int):
        """Send cancellation confirmation email"""
        pass
    
    def _send_payment_failed_email(self, user_id: int, invoice):
        """Send payment failure notification"""
        pass
