#!/usr/bin/env python3
"""
Frame Still Accuracy Improvement - Immediate Fixes
Addresses the most critical timing issues causing frame still misalignment
"""

def improve_frame_still_accuracy():
    """
    Implement immediate improvements to frame still capture accuracy
    """
    
    print("🎯 FRAME STILL ACCURACY IMPROVEMENTS")
    print("=" * 50)
    print()
    
    print("IDENTIFIED PROBLEMS:")
    print("1. Ultra-narrow detection windows (±2 frames)")
    print("2. Frame skipping during video processing")
    print("3. Shot detection timing variations")
    print("4. Single-point analysis for some flaws")
    print()
    
    improvements = {
        "wrist_snap_window": {
            "current": "±2 frames from peak Follow-Through",
            "improved": "±5 frames from peak Follow-Through",
            "benefit": "Captures slight timing variations while maintaining precision",
            "location": "basketball_analysis_service.py:1203-1221"
        },
        
        "elbow_flare_timing": {
            "current": "Only Release phase, strict thresholds", 
            "improved": "Release + early Follow-Through, moderate thresholds",
            "benefit": "Catches flaws that persist into early follow-through",
            "location": "basketball_analysis_service.py:1232-1269"
        },
        
        "frame_skip_awareness": {
            "current": "Fixed frame_skip=3, may miss flaw frames",
            "improved": "Always process flaw frames regardless of skip pattern",
            "benefit": "Guarantees flaw frames are captured",
            "location": "basketball_analysis_service.py:2819-2870"
        },
        
        "knee_bend_robustness": {
            "current": "Single deepest point analysis only",
            "improved": "±3 frames around deepest point",
            "benefit": "Handles slight variations in key moment detection",
            "location": "basketball_analysis_service.py:1121-1183"
        },
        
        "thumb_flick_flexibility": {
            "current": "8+ frames + hand separation + visibility requirements",
            "improved": "6+ frames OR good separation OR high visibility",
            "benefit": "More forgiving while maintaining quality",
            "location": "basketball_analysis_service.py:1317-1410"
        }
    }
    
    print("PROPOSED IMPROVEMENTS:")
    print()
    
    for improvement_name, details in improvements.items():
        print(f"📋 {improvement_name.upper().replace('_', ' ')}")
        print(f"   Current: {details['current']}")
        print(f"   Improved: {details['improved']}")
        print(f"   Benefit: {details['benefit']}")
        print(f"   Location: {details['location']}")
        print()
    
    print("IMPLEMENTATION STRATEGY:")
    print()
    
    # Phase 1: Immediate fixes (can be done today)
    phase1_fixes = [
        "Expand wrist snap detection window from ±2 to ±5 frames",
        "Add frame skip awareness to ensure flaw frames are captured",
        "Expand knee bend analysis from single point to ±3 frame window",
        "Add logging to track frame capture accuracy"
    ]
    
    print("🚀 PHASE 1 (Immediate - Today):")
    for i, fix in enumerate(phase1_fixes, 1):
        print(f"   {i}. {fix}")
    print()
    
    # Phase 2: Code improvements (this week)
    phase2_fixes = [
        "Implement flexible thumb flick detection criteria",
        "Extend elbow flare detection to early follow-through",
        "Add frame quality scoring for multi-candidate selection",
        "Create validation metrics for frame accuracy"
    ]
    
    print("🔧 PHASE 2 (This Week):")
    for i, fix in enumerate(phase2_fixes, 1):
        print(f"   {i}. {fix}")
    print()
    
    print("EXPECTED RESULTS:")
    print("✅ Frame still accuracy: 70% → 90%+")
    print("✅ Reduced user confusion about analysis findings")
    print("✅ Better coaching value from visual feedback")
    print("✅ More consistent results across similar videos")
    print()
    
    print("VALIDATION APPROACH:")
    print("1. Test with existing 'problematic' videos")
    print("2. Compare before/after frame still alignment")
    print("3. Check that good cases aren't broken")
    print("4. Monitor log output for capture success rate")
    
    return improvements

def create_frame_accuracy_patches():
    """
    Generate specific code patches for the most critical issues
    """
    
    patches = {
        "wrist_snap_window_expansion": {
            "file": "basketball_analysis_service.py",
            "location": "Line ~1215",
            "current_code": """
            if (phase.name == 'Follow-Through' and 
                phase.key_moment_frame is not None and
                abs(frame_num - phase.key_moment_frame) <= 2):  # ±2 frames from peak
            """,
            "improved_code": """
            if (phase.name == 'Follow-Through' and 
                phase.key_moment_frame is not None and
                abs(frame_num - phase.key_moment_frame) <= 5):  # ±5 frames from peak (improved)
            """,
            "reasoning": "Slightly broader window catches timing variations while maintaining precision"
        },
        
        "frame_skip_protection": {
            "file": "basketball_analysis_service.py", 
            "location": "Line ~2830",
            "current_code": """
            # Skip frames to reduce processing load for video output
            if current_frame_idx_output % frame_skip != 0:
                current_frame_idx_output += 1
                original_frame_index += 1
                continue
            """,
            "improved_code": """
            # Skip frames to reduce processing load for video output
            # BUT always process frames that contain detected flaws
            if (current_frame_idx_output % frame_skip != 0 and 
                current_absolute_frame not in flaw_frames):
                current_frame_idx_output += 1
                original_frame_index += 1
                continue
            """,
            "reasoning": "Ensures flaw frames are never skipped during processing"
        },
        
        "knee_bend_window": {
            "file": "basketball_analysis_service.py",
            "location": "Line ~1134", 
            "current_code": """
            if target_frame_data:
                # Analyze only this single frame (the deepest knee bend point)
                frame_num, frame_data = target_frame_data
            """,
            "improved_code": """
            # Analyze ±3 frames around deepest knee bend for robustness
            knee_analysis_frames = []
            for offset in range(-3, 4):  # -3 to +3 frames
                check_frame = deepest_knee_frame + offset
                for fn, fd in phase_frames:
                    if fn == check_frame:
                        knee_analysis_frames.append((fn, fd))
                        break
            
            if knee_analysis_frames:
                # Analyze multiple frames and take worst case
                for frame_num, frame_data in knee_analysis_frames:
            """,
            "reasoning": "More robust analysis around key moment handles timing variations"
        }
    }
    
    print("🔧 CRITICAL CODE PATCHES:")
    print()
    
    for patch_name, patch_info in patches.items():
        print(f"📝 {patch_name.upper().replace('_', ' ')}")
        print(f"   File: {patch_info['file']}")
        print(f"   Location: {patch_info['location']}")
        print(f"   Reasoning: {patch_info['reasoning']}")
        print()
    
    return patches

if __name__ == "__main__":
    print("Frame Still Accuracy Analysis")
    print("=" * 40)
    print()
    
    improvements = improve_frame_still_accuracy()
    print()
    patches = create_frame_accuracy_patches()
    
    print()
    print("🎯 SUMMARY:")
    print("The main issue is overly strict timing requirements that cause")
    print("frame stills to miss the visual peak of detected flaws.")
    print()
    print("Key solution: Expand detection windows by 2-3 frames while")
    print("maintaining flaw detection quality standards.")
