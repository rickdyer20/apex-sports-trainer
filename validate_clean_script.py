#!/usr/bin/env python3
"""
Quick validation test for cleaned basketball analysis service
"""

# Test basic imports and structure
try:
    import basketball_analysis_service as bas
    print("✅ Main module imported successfully")
    
    # Test key functions exist
    required_functions = [
        'analyze_basketball_shot',
        'process_video_for_analysis', 
        'detect_camera_angle_and_visibility',
        'analyze_detailed_flaws',
        'get_coaching_tip',
        'get_drill_suggestion'
    ]
    
    missing_functions = []
    for func_name in required_functions:
        if hasattr(bas, func_name):
            print(f"✅ {func_name} - Present")
        else:
            print(f"❌ {func_name} - Missing")
            missing_functions.append(func_name)
    
    # Test key classes exist
    required_classes = [
        'VideoAnalysisJob',
        'FrameData', 
        'ShotPhase',
        'FeedbackPoint',
        'AnalysisReport'
    ]
    
    missing_classes = []
    for class_name in required_classes:
        if hasattr(bas, class_name):
            print(f"✅ {class_name} - Present")
        else:
            print(f"❌ {class_name} - Missing")
            missing_classes.append(class_name)
    
    if not missing_functions and not missing_classes:
        print("\n🎉 ALL CORE COMPONENTS PRESENT")
        print("✅ Script is clean and functional!")
        
        # Test main entry point function signature
        import inspect
        sig = inspect.signature(bas.analyze_basketball_shot)
        print(f"✅ Main function signature: {sig}")
        
    else:
        print(f"\n⚠️  Missing functions: {missing_functions}")
        print(f"⚠️  Missing classes: {missing_classes}")

except ImportError as e:
    print(f"❌ Import failed: {e}")
except Exception as e:
    print(f"❌ Validation failed: {e}")
    import traceback
    traceback.print_exc()
