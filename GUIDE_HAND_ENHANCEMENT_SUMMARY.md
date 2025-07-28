## Guide Hand Positioning Enhancement Summary

### Problem Identified
The user reported that guide hand detection was incorrectly classifying "guide hand on top of ball" as "guide hand under ball". The system needed better positioning logic to distinguish between different placement issues.

### Solution Implemented

#### 1. Enhanced Guide Hand Position Calculation
- **Improved angle calculation**: Removed `abs()` to preserve directional information
- **Added vertical offset tracking**: `guide_hand_vertical_offset = guide_dy` (negative = above, positive = below)  
- **Added horizontal separation**: `guide_hand_horizontal_offset = abs(guide_dx)` for interference detection
- **Better coordinate interpretation**: Uses proper video coordinate system understanding

#### 2. New Flaw Type Added
- **guide_hand_on_top**: Separate flaw type for "on top" positioning
- **Threshold**: 15 pixels (more sensitive than under_ball detection)
- **Specific coaching tips**: "Move your guide hand to the side of the ball, not on top"
- **Dedicated drill library**: Side placement drills, wall form shooting, awareness training

#### 3. Enhanced Detection Logic
- **guide_hand_under_ball**: Now detects underneath (vertical_offset > 15) and interference (horizontal_offset < 20)
- **guide_hand_on_top**: Detects positioning on top of ball (vertical_offset < -15)  
- **Proper timing**: Both restricted to ±3 frames of release point
- **Better logging**: Detailed position assessment and severity calculation

#### 4. Comprehensive Documentation Updates
- **PDF Generator**: Added complete support for guide_hand_on_top flaw
- **Drill Libraries**: 3 new drills specifically for "on top" positioning
- **Coaching Tips**: Enhanced feedback messaging
- **JSON Configuration**: Updated ideal_shot_guide.json

### Test Results
✅ **"Guide Hand ON TOP"**: Correctly detects vertical_offset=-25 as on top positioning
✅ **"Guide Hand UNDER BALL"**: Correctly detects vertical_offset=30 as underneath  
✅ **"Guide Hand PROPER SIDE"**: Correctly shows no flaws for vertical_offset=5
✅ **"Guide Hand TOO CENTERED"**: Correctly detects interference when horizontal_offset=15

### Current Status
- Enhanced positioning logic implemented and tested
- Both "on top" and "under ball" flaws now correctly distinguished  
- Improved accuracy in guide hand positioning detection
- Ready for production use with basketball shot analysis

### Next Steps
- Monitor real-world performance with actual basketball videos
- Fine-tune thresholds based on user feedback
- Consider adding additional guide hand positioning variations if needed
