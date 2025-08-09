# User Analysis Tracking System
# Enforces "1 free analysis per year" limit

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging

class UserAnalysisTracker:
    """Tracks user analysis usage to enforce limits"""
    
    def __init__(self, data_file='user_analysis_data.json'):
        self.data_file = data_file
        self.users_data = self._load_data()
        
    def _load_data(self) -> Dict:
        """Load user analysis data from file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Error loading user data: {e}")
                return {}
        return {}
    
    def _save_data(self):
        """Save user analysis data to file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.users_data, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving user data: {e}")
    
    def can_user_analyze(self, user_identifier: str, tier: str = 'free') -> Dict:
        """
        Check if user can perform analysis based on their tier and usage
        
        Args:
            user_identifier: Email, IP address, or user ID
            tier: 'free', 'onetime', 'pro', 'enterprise'
            
        Returns:
            Dict with 'allowed' boolean and 'reason' if not allowed
        """
        # Paid tiers have unlimited or high limits
        if tier in ['pro', 'enterprise']:
            return {'allowed': True, 'reason': None}
        
        # One-time purchases get 5 analyses
        if tier == 'onetime':
            user_data = self.users_data.get(user_identifier, {})
            onetime_count = user_data.get('onetime_analyses', 0)
            if onetime_count < 5:
                return {'allowed': True, 'reason': None}
            else:
                return {
                    'allowed': False, 
                    'reason': 'You have used all 5 analyses from your one-time purchase. Upgrade to Pro for unlimited analyses.'
                }
        
        # Free tier: 1 analysis per year
        if tier == 'free':
            user_data = self.users_data.get(user_identifier, {})
            
            # Check if user has any free analyses
            if 'last_free_analysis' not in user_data:
                return {'allowed': True, 'reason': None}
            
            # Check if it's been a year since last free analysis
            last_analysis_date = datetime.fromisoformat(user_data['last_free_analysis'])
            one_year_ago = datetime.now() - timedelta(days=365)
            
            if last_analysis_date < one_year_ago:
                return {'allowed': True, 'reason': None}
            else:
                days_until_reset = 365 - (datetime.now() - last_analysis_date).days
                return {
                    'allowed': False,
                    'reason': f'You have used your free analysis for this year. Try again in {days_until_reset} days, or upgrade to a paid plan for immediate access.'
                }
        
        return {'allowed': False, 'reason': 'Invalid tier specified'}
    
    def record_analysis(self, user_identifier: str, tier: str = 'free'):
        """Record that user performed an analysis"""
        if user_identifier not in self.users_data:
            self.users_data[user_identifier] = {}
        
        user_data = self.users_data[user_identifier]
        current_time = datetime.now().isoformat()
        
        if tier == 'free':
            user_data['last_free_analysis'] = current_time
            user_data['total_free_analyses'] = user_data.get('total_free_analyses', 0) + 1
        
        elif tier == 'onetime':
            user_data['onetime_analyses'] = user_data.get('onetime_analyses', 0) + 1
            user_data['last_onetime_analysis'] = current_time
        
        elif tier in ['pro', 'enterprise']:
            user_data[f'total_{tier}_analyses'] = user_data.get(f'total_{tier}_analyses', 0) + 1
            user_data[f'last_{tier}_analysis'] = current_time
        
        # Update user tier info
        user_data['current_tier'] = tier
        user_data['last_activity'] = current_time
        
        self._save_data()
        logging.info(f"Recorded {tier} analysis for user: {user_identifier}")
    
    def get_user_stats(self, user_identifier: str) -> Dict:
        """Get user's analysis statistics"""
        user_data = self.users_data.get(user_identifier, {})
        
        stats = {
            'current_tier': user_data.get('current_tier', 'free'),
            'total_free_analyses': user_data.get('total_free_analyses', 0),
            'total_onetime_analyses': user_data.get('onetime_analyses', 0),
            'total_pro_analyses': user_data.get('total_pro_analyses', 0),
            'total_enterprise_analyses': user_data.get('total_enterprise_analyses', 0),
            'last_activity': user_data.get('last_activity'),
            'last_free_analysis': user_data.get('last_free_analysis')
        }
        
        # Calculate when they can use free tier again
        if stats['last_free_analysis']:
            last_free = datetime.fromisoformat(stats['last_free_analysis'])
            next_free_date = last_free + timedelta(days=365)
            stats['next_free_analysis_date'] = next_free_date.isoformat()
            stats['days_until_next_free'] = (next_free_date - datetime.now()).days
        
        return stats


# Convenience functions for easy integration
def enforce_analysis_limit(user_email: str, user_tier: str) -> Dict:
    """Check if user can perform analysis"""
    tracker = UserAnalysisTracker()
    return tracker.can_user_analyze(user_email, user_tier)

def record_user_analysis(user_email: str, user_tier: str):
    """Record that user performed an analysis"""
    tracker = UserAnalysisTracker()
    tracker.record_analysis(user_email, user_tier)

def get_user_usage_stats(user_email: str) -> Dict:
    """Get user's usage statistics"""
    tracker = UserAnalysisTracker()
    return tracker.get_user_stats(user_email)


if __name__ == "__main__":
    # Test the tracking system
    tracker = UserAnalysisTracker()
    
    print("🏀 User Analysis Tracker - Test")
    print("=" * 40)
    
    # Test free user
    test_email = "test@example.com"
    
    # First analysis should be allowed
    result = tracker.can_user_analyze(test_email, 'free')
    print(f"First free analysis allowed: {result['allowed']}")
    
    if result['allowed']:
        tracker.record_analysis(test_email, 'free')
        print("✅ Recorded first free analysis")
    
    # Second analysis should be blocked
    result = tracker.can_user_analyze(test_email, 'free')
    print(f"Second free analysis allowed: {result['allowed']}")
    if not result['allowed']:
        print(f"Reason: {result['reason']}")
    
    # Get user stats
    stats = tracker.get_user_stats(test_email)
    print(f"\nUser Stats: {stats}")
