#!/usr/bin/env python3
"""
Quick Stripe Configuration for Basketball Analysis Service v9.0
Updates your .env file with Stripe keys for production on apexsports-llc.com
"""

import os
from pathlib import Path

def quick_stripe_setup():
    """Quick setup for Stripe configuration"""
    print("🏀 Basketball Analysis Service v9.0 - Quick Stripe Setup")
    print("=" * 60)
    print("Setting up payments for apexsports-llc.com")
    print()
    
    # Read current .env
    env_path = Path('.env')
    if not env_path.exists():
        print("❌ .env file not found. Please run setup_production_v9.py first")
        return
    
    # Read existing .env
    with open('.env', 'r') as f:
        lines = f.readlines()
    
    print("📋 Please provide your Stripe configuration:")
    print("(Get these from: https://dashboard.stripe.com/test/apikeys)")
    print()
    
    # Get Stripe keys
    stripe_publishable = input("🔑 Stripe Publishable Key (pk_test_... or pk_live_...): ").strip()
    if not stripe_publishable:
        print("❌ No key provided. Setup cancelled.")
        return
    
    stripe_secret = input("🔐 Stripe Secret Key (sk_test_... or sk_live_...): ").strip()
    if not stripe_secret:
        print("❌ No key provided. Setup cancelled.")
        return
    
    # Check if live or test
    is_live = stripe_publishable.startswith('pk_live_')
    mode = "LIVE" if is_live else "TEST"
    
    print(f"\n✅ Detected {mode} mode")
    
    if is_live:
        confirm = input("⚠️  You're using LIVE keys for production. Continue? (y/N): ")
        if confirm.lower() != 'y':
            print("Setup cancelled.")
            return
    
    # Optional webhook secret
    webhook_secret = input("🪝 Webhook Secret (whsec_... - optional, press Enter to skip): ").strip()
    
    # Update .env file
    new_lines = []
    stripe_keys_updated = False
    
    for line in lines:
        if line.startswith('STRIPE_PUBLISHABLE_KEY='):
            new_lines.append(f'STRIPE_PUBLISHABLE_KEY={stripe_publishable}\n')
            stripe_keys_updated = True
        elif line.startswith('STRIPE_SECRET_KEY='):
            new_lines.append(f'STRIPE_SECRET_KEY={stripe_secret}\n')
        elif line.startswith('STRIPE_WEBHOOK_SECRET=') or line.startswith('# STRIPE_WEBHOOK_SECRET='):
            if webhook_secret:
                new_lines.append(f'STRIPE_WEBHOOK_SECRET={webhook_secret}\n')
            else:
                new_lines.append('# STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here\n')
        else:
            new_lines.append(line)
    
    # Write updated .env
    with open('.env', 'w') as f:
        f.writelines(new_lines)
    
    print(f"\n✅ Stripe configuration updated in .env file!")
    print(f"🎯 Mode: {mode}")
    print()
    
    print("🚀 Next Steps:")
    print("1. Set up webhooks in your Stripe dashboard:")
    print(f"   - Endpoint URL: https://apexsports-llc.com/webhook/stripe")
    print("   - Events to send:")
    print("     • checkout.session.completed")
    print("     • customer.subscription.created")
    print("     • customer.subscription.updated")
    print("     • customer.subscription.deleted")
    print("     • invoice.payment_succeeded")
    print("     • invoice.payment_failed")
    print()
    print("2. Test your integration:")
    if is_live:
        print("   - Use real payment methods")
        print("   - Monitor live transactions carefully")
    else:
        print("   - Use Stripe test cards: 4242424242424242")
        print("   - Test the subscription flows")
    
    print()
    print("🔗 Stripe Dashboard:")
    if is_live:
        print("   https://dashboard.stripe.com/")
    else:
        print("   https://dashboard.stripe.com/test/")
    
    print()
    print("✅ Your Basketball Analysis Service v9.0 is now ready for payments!")
    print("💳 Subscription plans available:")
    print("   • Free: Basic analysis")
    print("   • Pro ($9.99/month): Advanced features")
    print("   • Enterprise ($29.99/month): Full suite")

if __name__ == "__main__":
    quick_stripe_setup()
