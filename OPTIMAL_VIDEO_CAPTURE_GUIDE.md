# Optimal Video Capture Guidelines for Basketball Shot Analysis

## Recommended Video Specifications

### **Duration: 3-4 seconds**
- **Minimum**: 3.0 seconds (adequate for basic analysis)
- **Optimal**: 3.5-4.0 seconds (comprehensive analysis)
- **Maximum useful**: 5.0 seconds (diminishing returns beyond this)

### **Frame Rate: 30-60 FPS**
- **30 FPS**: Minimum for smooth analysis (90-120 frames total)
- **60 FPS**: Preferred for detailed motion capture (180-240 frames total)
- Higher frame rates provide better temporal resolution for detecting subtle flaws

## Shot Phase Timing Analysis

### **Phase 1: Pre-Shot Setup (0.5-0.8s)**
```
Frames: 15-24 (at 30fps) | 30-48 (at 60fps)
Key Metrics:
- Initial foot positioning
- Hand placement on ball
- Body alignment with target
- Eye focus establishment
```

### **Phase 2: Load/Dip (0.3-0.5s)**
```
Frames: 9-15 (at 30fps) | 18-30 (at 60fps)
Key Metrics:
- Knee bend angle (ideal: 110-130°)
- Ball dip depth and control
- Weight distribution
- Core engagement
```

### **Phase 3: Release (0.2-0.4s)**
```
Frames: 6-12 (at 30fps) | 12-24 (at 60fps)
Key Metrics:
- Leg drive initiation
- Elbow extension (ideal: 160-180°)
- Shooting hand position
- Guide hand placement
```

### **Phase 4: Follow-Through (0.8-1.2s)**
```
Frames: 24-36 (at 30fps) | 48-72 (at 60fps)
Key Metrics:
- Wrist snap completion (ideal: 70-90°)
- Arm extension hold
- Finger pointing direction
- Body balance maintenance
```

### **Phase 5: Recovery (0.5-0.8s)**
```
Frames: 15-24 (at 30fps) | 30-48 (at 60fps)
Key Metrics:
- Landing position vs takeoff
- Balance stability
- Return to athletic position
```

## Optimal Video Start Points

### **Option 1: Ball Catch (Recommended)**
```
Timeline: -0.2s to +3.5s from release
Benefits:
✅ Captures complete shooting motion
✅ Shows catch mechanics and setup
✅ Allows for stance and alignment analysis
✅ Provides context for shot preparation
```

### **Option 2: Shot Setup Begin**
```
Timeline: 0.0s to +3.0s from setup initiation
Benefits:
✅ Focuses purely on shooting mechanics
✅ Eliminates pre-shot movement variables
✅ Shorter video for faster processing
⚠️ Misses catch and initial setup analysis
```

### **Option 3: Pre-Catch (Extended Analysis)**
```
Timeline: -0.5s to +4.0s from release
Benefits:
✅ Full context including approach
✅ Comprehensive stance analysis
✅ Complete movement pattern capture
⚠️ Longer processing time
⚠️ May include irrelevant movement
```

## Frame Count Optimization

### **At 30 FPS (Minimum Recommended):**
- **3.0 seconds**: 90 frames (adequate)
- **3.5 seconds**: 105 frames (optimal)
- **4.0 seconds**: 120 frames (comprehensive)

### **At 60 FPS (Preferred):**
- **3.0 seconds**: 180 frames (detailed)
- **3.5 seconds**: 210 frames (highly detailed)
- **4.0 seconds**: 240 frames (maximum useful detail)

## Camera Positioning Guidelines

### **Side View (Profile) - Primary Analysis**
```
Distance: 8-12 feet from shooter
Height: Chest level with shooter
Angle: 90° perpendicular to shooting line
Captures: Elbow mechanics, knee bend, arc analysis
```

### **Front View - Secondary Analysis**
```
Distance: 10-15 feet from shooter
Height: Chest level with shooter
Angle: Directly facing shooter
Captures: Elbow flare, balance, hand positioning
```

### **3/4 Angle View - Comprehensive**
```
Distance: 10-12 feet from shooter
Height: Chest level with shooter
Angle: 45° from shooting line
Captures: Most metrics with good visibility
```

## Processing Efficiency Considerations

### **Shorter Videos (2.5-3.0s):**
- ✅ Faster processing (15-20% speed improvement)
- ✅ Lower storage requirements
- ✅ Quicker analysis feedback
- ⚠️ May miss setup phase details
- ❌ Less context for rhythm analysis

### **Optimal Length Videos (3.5-4.0s):**
- ✅ Complete phase capture
- ✅ Comprehensive flaw detection
- ✅ Better rhythm and timing analysis
- ✅ Full biomechanical assessment
- ⚠️ Slightly longer processing time
- ⚠️ Higher storage requirements

### **Extended Videos (4.5-5.0s+):**
- ✅ Maximum context
- ✅ Multiple shot attempts possible
- ❌ Diminishing analytical returns
- ❌ Significantly longer processing
- ❌ Potential for analysis confusion

## Practical Implementation

### **For Mobile App Recording:**
```python
# Recommended settings
OPTIMAL_DURATION = 3.5  # seconds
MINIMUM_FPS = 30
PREFERRED_FPS = 60
START_TRIGGER = "ball_catch_detected"  # or manual trigger
RESOLUTION = "720p"  # Balance of quality vs file size
```

### **For Professional Analysis:**
```python
# Enhanced settings
OPTIMAL_DURATION = 4.0  # seconds
MINIMUM_FPS = 60
PREFERRED_FPS = 120  # if available
START_TRIGGER = "movement_detection"
RESOLUTION = "1080p"
MULTIPLE_ANGLES = True  # Side + Front view
```

## Quality Factors Beyond Length

### **Lighting Requirements:**
- Minimum brightness: 80-200 (0-255 scale)
- Avoid harsh shadows on shooting arm
- Consistent lighting throughout shot

### **Background Considerations:**
- Contrasting background to player
- Minimal distracting elements
- Stable camera positioning

### **Audio Cues (Optional):**
- Ball contact sounds for timing
- Coaching cues for context
- Net swish for shot outcome

## Summary Recommendation

**For optimal basketball shot analysis:**
- **Duration**: 3.5 seconds
- **Start Point**: Ball catch or 0.2s before
- **Frame Rate**: 60 FPS preferred, 30 FPS minimum
- **Total Frames**: ~210 frames at 60fps
- **Camera Angle**: Side view primary, front view secondary

This provides the best balance of:
✅ Complete biomechanical analysis
✅ All shot phases captured
✅ Reasonable processing time
✅ Comprehensive flaw detection
✅ Sufficient context for coaching feedback
