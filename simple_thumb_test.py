#!/usr/bin/env python3
"""
Simple test to check thumb flick detection issues
"""

import sys
import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Test if basic imports work
try:
    from basketball_analysis_service import analyze_basketball_shot
    print("✅ Successfully imported basketball_analysis_service")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Test video analysis
try:
    print("🏀 Testing basketball shot analysis...")
    results = analyze_basketball_shot("basketball_shot_demo.mp4")
    
    if results:
        print(f"✅ Analysis completed successfully")
        print(f"📊 Found {len(results.get('detailed_flaws', []))} flaws")
        
        # Check for thumb flick specifically
        thumb_flick_found = False
        for flaw in results.get('detailed_flaws', []):
            print(f"  - {flaw['flaw_type']}: Severity {flaw['severity']}")
            if flaw['flaw_type'] == 'guide_hand_thumb_flick':
                thumb_flick_found = True
                
        if not thumb_flick_found:
            print("❌ No thumb flick detected - this might be the issue!")
        else:
            print("✅ Thumb flick was detected")
            
    else:
        print("❌ No results returned from analysis")
        
except Exception as e:
    print(f"❌ Error during analysis: {e}")
    import traceback
    traceback.print_exc()
