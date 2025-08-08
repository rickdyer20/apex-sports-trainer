#!/bin/bash
# Quick Deployment Script for ApexSports-LLC.com
# Run this on your server after uploading the files

echo "🚀 Deploying Basketball Analysis Service to ApexSports-LLC.com"
echo "==============================================================="

# Install required Python packages
echo "📦 Installing dependencies..."
pip install flask stripe python-dotenv

# Check if essential files exist
echo "📋 Checking essential files..."
files=(
    "complete_web_app.py"
    "enhanced_payment_manager.py"
    "user_analysis_tracker.py"
    ".env"
    "templates/pricing_with_onetime.html"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file - Found"
    else
        echo "❌ $file - Missing"
    fi
done

# Check environment variables
echo "🔑 Checking environment configuration..."
if grep -q "pk_live_" .env; then
    echo "✅ Stripe live keys detected"
else
    echo "❌ Live Stripe keys not found in .env"
fi

# Start the application
echo "🏀 Starting Basketball Analysis Service..."
echo "Application will be available at: https://apexsports-llc.com"
echo "==============================================================="

# For development/testing (use port 5000)
# python complete_web_app.py

# For production (use Gunicorn)
echo "To start in production mode, run:"
echo "gunicorn -w 4 -b 0.0.0.0:80 complete_web_app:app"

echo "🎉 Deployment complete!"
