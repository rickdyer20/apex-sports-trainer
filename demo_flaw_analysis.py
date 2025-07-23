"""
Demo script to show flaw detection overlay capabilities
"""
import cv2
import numpy as np
from basketball_analysis_service import create_flaw_overlay, wrap_text

def create_demo_flaw_still():
    """Create a demo still frame showing flaw detection overlay"""
    
    # Create a sample frame (basketball court background)
    width, height = 640, 480
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Draw court background
    cv2.rectangle(frame, (0, height-50), (width, height), (139, 69, 19), -1)  # Court
    cv2.line(frame, (width//2, 0), (width//2, height), (255, 255, 255), 2)    # Center line
    
    # Draw simple player figure
    player_x, player_y = width//2, height-200
    
    # Head
    cv2.circle(frame, (player_x, player_y - 80), 20, (255, 255, 255), 2)
    
    # Torso
    cv2.line(frame, (player_x, player_y - 60), (player_x, player_y + 40), (255, 255, 255), 3)
    
    # Arms - showing elbow flare problem
    # Right arm (shooting arm) - positioned too far out (flare)
    cv2.line(frame, (player_x + 25, player_y - 40), (player_x + 60, player_y - 10), (255, 255, 255), 3)  # Upper arm
    cv2.line(frame, (player_x + 60, player_y - 10), (player_x + 80, player_y - 40), (255, 255, 255), 3)    # Forearm
    
    # Left arm (guide hand)
    cv2.line(frame, (player_x - 25, player_y - 40), (player_x - 35, player_y - 20), (255, 255, 255), 3)
    cv2.line(frame, (player_x - 35, player_y - 20), (player_x - 25, player_y - 50), (255, 255, 255), 3)
    
    # Legs - showing insufficient knee bend
    hip_y = player_y + 40
    knee_y = hip_y + 80  # Not bent enough
    ankle_y = knee_y + 60
    
    # Right leg
    cv2.line(frame, (player_x + 10, hip_y), (player_x + 15, knee_y), (255, 255, 255), 3)
    cv2.line(frame, (player_x + 15, knee_y), (player_x + 20, ankle_y), (255, 255, 255), 3)
    
    # Left leg  
    cv2.line(frame, (player_x - 10, hip_y), (player_x - 15, knee_y), (255, 255, 255), 3)
    cv2.line(frame, (player_x - 15, knee_y), (player_x - 20, ankle_y), (255, 255, 255), 3)
    
    # Highlight the problematic elbow (elbow flare)
    cv2.circle(frame, (player_x + 60, player_y - 10), 15, (0, 255, 255), 3)  # Yellow highlight
    cv2.circle(frame, (player_x + 60, player_y - 10), 8, (255, 0, 0), -1)   # Blue center
    
    # Highlight the problematic knees (insufficient bend)
    cv2.circle(frame, (player_x + 15, knee_y), 15, (0, 255, 255), 3)  # Yellow highlight
    cv2.circle(frame, (player_x + 15, knee_y), 8, (255, 0, 0), -1)   # Blue center
    cv2.circle(frame, (player_x - 15, knee_y), 15, (0, 255, 255), 3)  # Yellow highlight
    cv2.circle(frame, (player_x - 15, knee_y), 8, (255, 0, 0), -1)   # Blue center
    
    return frame

def demo_flaw_overlays():
    """Create demo flaw detection stills with overlays"""
    
    print("🏀 Creating Basketball Shot Flaw Detection Demo")
    print("=" * 50)
    
    # Create base frame
    base_frame = create_demo_flaw_still()
    
    # Sample flaw data for demonstration
    sample_flaws = [
        {
            'flaw_type': 'elbow_flare',
            'frame_number': 25,
            'phase': 'Release',
            'severity': 28.5,
            'description': 'Shooting elbow positioned too far from body',
            'plain_language': 'Your shooting elbow is sticking out too far from your body. This reduces accuracy and consistency.',
            'coaching_tip': 'Keep your shooting elbow directly under the ball. Imagine shooting through a narrow tunnel.',
            'drill_suggestion': 'Wall shooting drill: Stand close to a wall and practice your shooting motion without hitting the wall.'
        },
        {
            'flaw_type': 'insufficient_knee_bend',
            'frame_number': 12,
            'phase': 'Load/Dip',
            'severity': 22.3,
            'description': 'Knee bend too shallow for proper power generation',
            'plain_language': 'You\'re not bending your knees enough. Get lower to generate more power and improve your shooting range.',
            'coaching_tip': 'Bend your knees more to get into a proper athletic position. Think "sit back" into your shot.',
            'drill_suggestion': 'Chair shooting: Practice shooting while sitting on a chair, then stand up as you shoot.'
        },
        {
            'flaw_type': 'poor_follow_through',
            'frame_number': 35,
            'phase': 'Release',
            'severity': 19.7,
            'description': 'Insufficient wrist snap on follow-through',
            'plain_language': 'Your follow-through needs work. Snap your wrist down like you\'re reaching into a cookie jar.',
            'coaching_tip': 'Snap your wrist down aggressively. Hold your follow-through until the ball hits the rim.',
            'drill_suggestion': 'Bed shooting: Lie on your back and practice shooting straight up, focusing on wrist snap.'
        },
        {
            'flaw_type': 'guide_hand_interference',
            'frame_number': 28,
            'phase': 'Release',
            'severity': 15.2,
            'description': 'Off-hand affecting ball trajectory',
            'plain_language': 'Your guide hand is interfering with the shot. Keep it on the side of the ball, not underneath.',
            'coaching_tip': 'Your guide hand should be a passenger. Remove it just before release.',
            'drill_suggestion': 'One-handed shooting: Practice shooting with only your shooting hand.'
        },
        {
            'flaw_type': 'balance_issues',
            'frame_number': 31,
            'phase': 'Release',
            'severity': 17.8,
            'description': 'Poor balance affecting shot accuracy',
            'plain_language': 'Your balance is off during the shot. Focus on staying centered and landing where you started.',
            'coaching_tip': 'Focus on your base. Keep your feet shoulder-width apart and land in the same spot.',
            'drill_suggestion': 'One-foot shooting: Practice shooting while standing on one foot to improve balance.'
        },
        {
            'flaw_type': 'rushing_shot',
            'frame_number': 20,
            'phase': 'Release',
            'severity': 25.4,
            'description': 'Shot release too quick, lacks rhythm',
            'plain_language': 'You\'re rushing your shot. Slow down and find your shooting rhythm for better consistency.',
            'coaching_tip': 'Slow down your shooting motion. Count "1-2-shoot" to develop better rhythm.',
            'drill_suggestion': 'Slow motion shooting: Practice your entire shooting motion in slow motion 10 times.'
        },
        {
            'flaw_type': 'inconsistent_release_point',
            'frame_number': 26,
            'phase': 'Release',
            'severity': 21.1,
            'description': 'Release point varies significantly between frames',
            'plain_language': 'Your release point is not consistent. Try to release the ball from the same spot every time.',
            'coaching_tip': 'Practice your shooting pocket. Release from the same spot every time.',
            'drill_suggestion': 'Form shooting: Stand close to the basket and focus only on perfect form.'
        },
        {
            'flaw_type': 'excessive_knee_bend',
            'frame_number': 8,
            'phase': 'Load/Dip',
            'severity': 18.9,
            'description': 'Knee bend too deep, wasting energy',
            'plain_language': 'You\'re bending your knees too much. This wastes energy and can make your shot inconsistent.',
            'coaching_tip': 'Don\'t over-bend your knees. Find a comfortable athletic stance that you can repeat consistently.',
            'drill_suggestion': 'Mirror work: Practice your shooting stance in front of a mirror to find the right knee bend.'
        }
    ]
    
    # Create overlay images for each flaw
    created_files = []
    
    for i, flaw in enumerate(sample_flaws, 1):
        print(f"\n{i}. Creating flaw analysis: {flaw['flaw_type']}")
        print(f"   Phase: {flaw['phase']}")
        print(f"   Severity: {flaw['severity']:.1f}")
        print(f"   Issue: {flaw['plain_language']}")
        
        # Create flaw overlay (simplified since we don't have real landmarks)
        overlay_frame = create_simple_flaw_overlay(base_frame.copy(), flaw)
        
        # Save the frame
        filename = f"demo_flaw_{i}_{flaw['flaw_type']}.png"
        cv2.imwrite(filename, overlay_frame)
        created_files.append(filename)
        
        print(f"   ✅ Created: {filename}")
    
    print(f"\n🎯 Demo Complete!")
    print(f"Created {len(created_files)} flaw analysis images:")
    for file in created_files:
        print(f"   • {file}")
    
    print(f"\n📝 Each image shows:")
    print(f"   • Detected flaw with severity rating")
    print(f"   • Plain language explanation")
    print(f"   • Specific coaching tip")
    print(f"   • Recommended drill")
    print(f"   • Visual highlighting of problem areas")

def create_simple_flaw_overlay(frame, flaw_data):
    """Create simplified flaw overlay for demo purposes"""
    height, width = frame.shape[:2]
    
    # Add semi-transparent background for text
    cv2.rectangle(frame, (10, 10), (width-10, 200), (0, 0, 0), -1)
    cv2.rectangle(frame, (10, 10), (width-10, 200), (255, 255, 255), 2)
    
    # Add flaw title
    cv2.putText(frame, f"FLAW: {flaw_data['flaw_type'].replace('_', ' ').upper()}", 
                (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    
    # Add phase information
    cv2.putText(frame, f"Phase: {flaw_data['phase']}", 
                (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Add severity
    severity_color = (0, 255, 255) if flaw_data['severity'] < 20 else (0, 165, 255) if flaw_data['severity'] < 40 else (0, 0, 255)
    cv2.putText(frame, f"Severity: {flaw_data['severity']:.1f}", 
                (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, severity_color, 2)
    
    # Add description (wrapped text)
    description_lines = wrap_text(flaw_data['plain_language'], 60)
    for i, line in enumerate(description_lines[:3]):  # Max 3 lines
        cv2.putText(frame, line, 
                    (20, 130 + i*25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Add bottom overlay with coaching tip
    cv2.rectangle(frame, (10, height-120), (width-10, height-10), (0, 100, 0), -1)
    cv2.rectangle(frame, (10, height-120), (width-10, height-10), (255, 255, 255), 2)
    
    cv2.putText(frame, "COACHING TIP:", 
                (20, height-90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    tip_lines = wrap_text(flaw_data['coaching_tip'], 70)
    for i, line in enumerate(tip_lines[:2]):  # Max 2 lines
        cv2.putText(frame, line, 
                    (20, height-65 + i*20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    
    return frame

if __name__ == "__main__":
    demo_flaw_overlays()
