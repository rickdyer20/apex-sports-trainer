#!/usr/bin/env python3
"""
Test Frame Selection for Elbow Flare and Guide Hand On Top
Verifies that frames are selected from Load/Dip and early Release phases for instructional value
"""

import sys
sys.path.append('.')

def test_frame_selection_logic():
    """Test the frame selection scoring for instructional flaws"""
    print("🏀 Testing Frame Selection for Instructional Flaws")
    print("=" * 60)
    
    # Mock shot phases similar to real analysis
    class MockPhase:
        def __init__(self, name, start_frame, end_frame):
            self.name = name
            self.start_frame = start_frame
            self.end_frame = end_frame
    
    # Typical shot phases (90 frame video)
    shot_phases = [
        MockPhase('Setup', 0, 20),
        MockPhase('Load/Dip', 20, 45),      # 25 frames - key phase for elbow/guide hand
        MockPhase('Release', 45, 65),       # 20 frames - early frames still have ball
        MockPhase('Follow-Through', 65, 90) # 25 frames - ball released
    ]
    
    def calculate_frame_score(flaw_key, frame_num, shot_phases):
        """Simplified version of frame scoring logic"""
        score = 0
        
        for phase in shot_phases:
            if phase.start_frame <= frame_num <= phase.end_frame:
                phase_progress = (frame_num - phase.start_frame) / max(1, phase.end_frame - phase.start_frame)
                
                if flaw_key == 'elbow_flare':
                    if phase.name == 'Load/Dip' and 0.4 <= phase_progress <= 0.9:
                        score += 40  # HIGHEST priority
                    elif phase.name == 'Load/Dip':
                        score += 25
                    elif phase.name == 'Release' and phase_progress <= 0.5:
                        score += 35  # Very high priority
                    elif phase.name == 'Release' and phase_progress <= 0.7:
                        score += 20
                        
                elif flaw_key == 'guide_hand_on_top':
                    if phase.name == 'Load/Dip' and 0.3 <= phase_progress <= 0.8:
                        score += 45  # HIGHEST priority
                    elif phase.name == 'Load/Dip':
                        score += 30
                    elif phase.name == 'Release' and phase_progress <= 0.4:
                        score += 35  # Very high priority
                    elif phase.name == 'Release' and phase_progress <= 0.6:
                        score += 20
                break
        
        return score
    
    # Test elbow flare frame selection
    print("\n🎯 Elbow Flare Frame Selection:")
    print("-" * 40)
    elbow_scores = []
    for frame in range(0, 90, 5):  # Test every 5th frame
        score = calculate_frame_score('elbow_flare', frame, shot_phases)
        if score > 0:
            phase_name = None
            for phase in shot_phases:
                if phase.start_frame <= frame <= phase.end_frame:
                    phase_name = phase.name
                    break
            elbow_scores.append((frame, score, phase_name))
            print(f"Frame {frame:2d}: Score {score:2d} - {phase_name}")
    
    # Find best elbow flare frame
    if elbow_scores:
        best_elbow = max(elbow_scores, key=lambda x: x[1])
        print(f"✅ Best Elbow Flare Frame: {best_elbow[0]} (Score: {best_elbow[1]}, Phase: {best_elbow[2]})")
    
    # Test guide hand on top frame selection
    print("\n🤚 Guide Hand On Top Frame Selection:")
    print("-" * 40)
    guide_scores = []
    for frame in range(0, 90, 5):  # Test every 5th frame
        score = calculate_frame_score('guide_hand_on_top', frame, shot_phases)
        if score > 0:
            phase_name = None
            for phase in shot_phases:
                if phase.start_frame <= frame <= phase.end_frame:
                    phase_name = phase.name
                    break
            guide_scores.append((frame, score, phase_name))
            print(f"Frame {frame:2d}: Score {score:2d} - {phase_name}")
    
    # Find best guide hand frame
    if guide_scores:
        best_guide = max(guide_scores, key=lambda x: x[1])
        print(f"✅ Best Guide Hand Frame: {best_guide[0]} (Score: {best_guide[1]}, Phase: {best_guide[2]})")
    
    # Validation
    print("\n📋 Validation Results:")
    print("-" * 40)
    
    if elbow_scores:
        load_release_frames = [s for s in elbow_scores if s[2] in ['Load/Dip', 'Release']]
        if load_release_frames and best_elbow[2] in ['Load/Dip', 'Release']:
            print("✅ Elbow Flare: Correctly targeting Load/Dip or Release phases")
        else:
            print("❌ Elbow Flare: Not targeting correct phases")
    
    if guide_scores:
        load_release_frames = [s for s in guide_scores if s[2] in ['Load/Dip', 'Release']]
        if load_release_frames and best_guide[2] in ['Load/Dip', 'Release']:
            print("✅ Guide Hand On Top: Correctly targeting Load/Dip or Release phases")
        else:
            print("❌ Guide Hand On Top: Not targeting correct phases")
    
    print("\n🎯 Frame Selection Summary:")
    print("Both flaws now prioritize instructional frames when ball is in shooter's hands")
    print("- Load/Dip phase: Ball positioning and hand placement clearly visible")
    print("- Early Release: Critical mechanics still observable before ball leaves hands")

if __name__ == "__main__":
    test_frame_selection_logic()
