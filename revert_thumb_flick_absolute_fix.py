#!/usr/bin/env python3
"""
EASY REVERT - Thumb Flick ABSOLUTE FINAL FRAMES Fix

Quick script to revert the thumb flick absolute final frames restriction if needed.
"""

import os
import shutil
from datetime import datetime

def revert_thumb_flick_fix():
    """Revert the thumb flick absolute final frames fix"""
    service_file = "basketball_analysis_service.py"
    debug_file = "debug_thumb_flick.py"
    
    # Create backups
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    shutil.copy2(service_file, f"{service_file}.backup_revert_{timestamp}")
    shutil.copy2(debug_file, f"{debug_file}.backup_revert_{timestamp}")
    print(f"✅ Created backups with timestamp: {timestamp}")
    
    # Revert basketball_analysis_service.py
    with open(service_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Revert the phase bonus scoring
    content = content.replace(
        """                            # ULTRA-EXTREME LATE BIAS: Give massive bonus for very end of follow-through only
                            if phase.name == 'Follow-Through' and 0.95 <= phase_progress <= 1.0:
                                phase_bonus = 200  # ABSOLUTE MAXIMUM bonus for final 5% (95-100%) 
                            elif phase.name == 'Follow-Through' and 0.9 <= phase_progress < 0.95:
                                phase_bonus = 150  # ULTRA-MAXIMUM bonus for near-end (90-95%)
                            elif phase.name == 'Follow-Through' and 0.8 <= phase_progress < 0.9:
                                phase_bonus = 100  # EXTREME bonus for very late follow-through (80-90%)
                            elif phase.name == 'Follow-Through' and 0.7 <= phase_progress < 0.8:
                                phase_bonus = 40   # Strong bonus for late follow-through (70-80%)
                            elif phase.name == 'Follow-Through' and 0.6 <= phase_progress < 0.7:
                                phase_bonus = 10   # Low bonus for mid-late follow-through (60-70%)
                            elif phase.name == 'Follow-Through' and 0.5 <= phase_progress < 0.6:
                                phase_bonus = -20  # Strong penalty for mid follow-through (50-60%)
                            elif phase.name == 'Follow-Through' and 0.4 <= phase_progress < 0.5:
                                phase_bonus = -40  # Severe penalty for early follow-through (40-50%)
                            elif phase.name == 'Follow-Through' and phase_progress < 0.4:
                                phase_bonus = -100 # DEVASTATING penalty for very early follow-through (<40%)
                            # Note: ABSOLUTE focus on final 5% of Follow-Through phase (95-100%)""",
        """                            # ULTRA-EXTREME LATE BIAS: Give massive bonus for very end of follow-through only
                            if phase.name == 'Follow-Through' and 0.9 <= phase_progress <= 1.0:
                                phase_bonus = 100  # ULTRA-MAXIMUM bonus for absolute end (90-100%) 
                            elif phase.name == 'Follow-Through' and 0.8 <= phase_progress < 0.9:
                                phase_bonus = 75   # EXTREME bonus for very late follow-through (80-90%)
                            elif phase.name == 'Follow-Through' and 0.7 <= phase_progress < 0.8:
                                phase_bonus = 40   # Strong bonus for late follow-through (70-80%)
                            elif phase.name == 'Follow-Through' and 0.6 <= phase_progress < 0.7:
                                phase_bonus = 20   # Moderate bonus for mid-late follow-through (60-70%)
                            elif phase.name == 'Follow-Through' and 0.5 <= phase_progress < 0.6:
                                phase_bonus = 5    # Low bonus for mid follow-through (50-60%)
                            elif phase.name == 'Follow-Through' and 0.4 <= phase_progress < 0.5:
                                phase_bonus = -10  # Penalty for early follow-through (40-50%)
                            elif phase.name == 'Follow-Through' and phase_progress < 0.4:
                                phase_bonus = -25  # Strong penalty for very early follow-through (<40%)
                            # Note: Ultra-heavily favoring absolute end of Follow-Through phase (90-100%)"""
    )
    
    # Revert the absolute restriction
    content = content.replace(
        """                # Skip if not in Follow-Through phase (thumb flick only happens AFTER ball release)
                # ABSOLUTE RESTRICTION: Only detect in final 10% of Follow-Through phase (90-100%)
                if not is_relevant_phase:
                    logging.debug(f"THUMB FLICK SKIPPED - Frame {frame_num}: not in Follow-Through phase (current phase: {current_phase_name or 'Unknown'})")
                    continue
                
                # EXTREME RESTRICTION: Only allow detection in final 10% of Follow-Through
                if shot_phases:
                    final_phase_only = False
                    for phase in shot_phases:
                        if phase.name == 'Follow-Through' and phase.start_frame <= frame_num <= phase.end_frame:
                            phase_progress = (frame_num - phase.start_frame) / max(1, phase.end_frame - phase.start_frame)
                            # ABSOLUTE FINAL FRAMES ONLY: Must be in final 10% (90-100%)
                            if phase_progress >= 0.9:
                                final_phase_only = True
                                logging.debug(f"THUMB FLICK ALLOWED - Frame {frame_num}: in final 10% of Follow-Through ({phase_progress:.2f})")
                            else:
                                logging.debug(f"THUMB FLICK REJECTED - Frame {frame_num}: too early in Follow-Through ({phase_progress:.2f}, need >=0.9)")
                            break
                    
                    if not final_phase_only:
                        continue  # Skip this frame - not in final 10% of Follow-Through""",
        """                # Skip if not in Follow-Through phase (thumb flick only happens AFTER ball release)
                if not is_relevant_phase:
                    logging.debug(f"THUMB FLICK SKIPPED - Frame {frame_num}: not in Follow-Through phase (current phase: {current_phase_name or 'Unknown'})")
                    continue"""
    )
    
    # Revert illustration scoring
    content = content.replace(
        """                elif flaw_key == 'guide_hand_thumb_flick':
                    # Thumb flick is most visible AFTER ball release during follow-through
                    # ABSOLUTE EXTREME LATE BIAS: Only target final 5% of Follow-Through when ball is definitely gone
                    if phase.name == 'Follow-Through' and 0.95 <= phase_progress <= 1.0:
                        score += 300  # ABSOLUTE MAXIMUM for final 5% of follow-through (95-100%)
                    elif phase.name == 'Follow-Through' and 0.9 <= phase_progress < 0.95:
                        score += 200  # ULTRA-MAXIMUM for near-end follow-through (90-95%)
                    elif phase.name == 'Follow-Through' and 0.8 <= phase_progress < 0.9:
                        score += 120  # EXTREME illustration - very late follow-through (80-90%)
                    elif phase.name == 'Follow-Through' and 0.7 <= phase_progress < 0.8:
                        score += 50   # Good illustration - late follow-through (70-80%)
                    elif phase.name == 'Follow-Through' and 0.6 <= phase_progress < 0.7:
                        score += 20   # Low illustration - mid-late follow-through (60-70%)
                    elif phase.name == 'Follow-Through' and 0.5 <= phase_progress < 0.6:
                        score -= 10   # Penalty for mid follow-through (50-60%)
                    elif phase.name == 'Follow-Through' and 0.4 <= phase_progress < 0.5:
                        score -= 50   # Strong penalty for early follow-through (40-50%)
                    elif phase.name == 'Follow-Through' and phase_progress < 0.4:
                        score -= 100  # DEVASTATING penalty for very early follow-through (<40%)
                    # Note: ABSOLUTE focus on final 5% of Follow-Through phase (95-100%)""",
        """                elif flaw_key == 'guide_hand_thumb_flick':
                    # Thumb flick is most visible AFTER ball release during follow-through
                    # ULTRA-EXTREME LATE BIAS: Only target very end of Follow-Through when ball is definitely gone
                    if phase.name == 'Follow-Through' and 0.9 <= phase_progress <= 1.0:
                        score += 200  # ULTRA-MAXIMUM for absolute end of follow-through (90-100%)
                    elif phase.name == 'Follow-Through' and 0.8 <= phase_progress < 0.9:
                        score += 150  # EXTREME illustration - very late follow-through (80-90%)
                    elif phase.name == 'Follow-Through' and 0.7 <= phase_progress < 0.8:
                        score += 60   # Good illustration - late follow-through (70-80%)
                    elif phase.name == 'Follow-Through' and 0.6 <= phase_progress < 0.7:
                        score += 30   # Moderate illustration - mid-late follow-through (60-70%)
                    elif phase.name == 'Follow-Through' and 0.5 <= phase_progress < 0.6:
                        score += 10   # Low score for mid follow-through (50-60%)
                    elif phase.name == 'Follow-Through' and 0.4 <= phase_progress < 0.5:
                        score -= 30   # Strong penalty for early follow-through (40-50%)
                    elif phase.name == 'Follow-Through' and phase_progress < 0.4:
                        score -= 50   # SEVERE penalty for very early follow-through (<40%)
                    # Note: Ultra-heavily targeting absolute end of Follow-Through phase (90-100%)"""
    )
    
    # Write back
    with open(service_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Revert debug_thumb_flick.py
    with open(debug_file, 'r', encoding='utf-8') as f:
        debug_content = f.read()
    
    debug_content = debug_content.replace(
        """    print("Starting analysis with ABSOLUTE FINAL FRAMES restriction...")
    print("🔍 Thumb flick detection now ONLY targets final 10% of Follow-Through phase (90-100%)")
    print("📋 Frames before 90% Follow-Through progress are COMPLETELY REJECTED")
    print("🎯 Frame selection: 99% illustration quality, 1% severity weighting")
    print("🚀 ABSOLUTE EXTREME: 95-100% gets 300 points, 90-95% gets 200 points")
    print("⚠️  DEVASTATING penalties for any frames before 90% Follow-Through")
    print("🎯 ABSOLUTE RESTRICTION: Thumb flick can ONLY be detected in final 10% of Follow-Through")""",
        """    print("Starting analysis with ULTRA-EXTREME LATE Follow-Through restriction...")
    print("🔍 Thumb flick detection now targets 90-100% of Follow-Through phase PRIMARILY")
    print("📋 Early follow-through frames (<40%) now have SEVERE PENALTY scores")
    print("🎯 Frame selection: 99% illustration quality, 1% severity weighting")
    print("🚀 ULTRA-EXTREME: 90-100% gets 200 points, 80-90% gets 150 points")
    print("⚠️  SEVERE penalties for early frames to force late selection")"""
    )
    
    with open(debug_file, 'w', encoding='utf-8') as f:
        f.write(debug_content)
    
    print("✅ THUMB FLICK ABSOLUTE FINAL FRAMES FIX REVERTED")
    print("✅ Original ultra-extreme late bias restored")
    print("✅ Detection can now happen anywhere in Follow-Through phase")

if __name__ == "__main__":
    print("Reverting Thumb Flick Absolute Final Frames Fix...")
    revert_thumb_flick_fix()
    print("Done!")
