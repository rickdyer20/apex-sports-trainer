# 🎯 Frame Still Accuracy Improvement Plan

## Problem Analysis
The basketball analysis system sometimes captures frame stills that don't perfectly align with the detected flaws, leading to reduced coaching value and user confusion.

## Root Causes Identified

### 1. **Ultra-Narrow Detection Windows**
- Wrist snap: Only ±2 frames from peak Follow-Through moment
- Knee bend: Only at single deepest point frame
- Thumb flick: Requires 8+ frames into follow-through + multiple conditions

### 2. **Shot Detection Timing Variations**
- Buffer frame calculations can vary by 5-10 frames between similar videos
- Phase boundary detection depends on precise key moment identification
- Small timing differences compound into frame misalignment

### 3. **Processing Frame Skipping**
- System processes every 3rd frame (`frame_skip = 3`)
- Flaw detection happens on all frames, but video processing skips frames
- Can miss the exact flaw frame during still capture

## Improvement Strategies

### **Strategy 1: Flexible Flaw Detection Windows**

Instead of requiring exact timing, use broader but still meaningful windows:

```python
# CURRENT: Ultra-strict timing
if abs(frame_num - phase.key_moment_frame) <= 2:  # ±2 frames only

# IMPROVED: Reasonable timing window
if abs(frame_num - phase.key_moment_frame) <= 5:  # ±5 frames (0.17s at 30fps)
```

### **Strategy 2: Frame Still Capture Refinement**

Modify video processing to ensure flaw frames are never skipped:

```python
# CURRENT: Fixed frame skipping
frame_skip = 3

# IMPROVED: Skip-aware processing
if current_absolute_frame in flaw_frames:
    # Always capture flaw frames, regardless of skip pattern
    capture_frame_still(...)
elif current_frame_idx_output % frame_skip == 0:
    # Normal processing for non-flaw frames
    process_frame(...)
```

### **Strategy 3: Multi-Frame Flaw Still Selection**

For critical flaws, capture multiple candidate frames and select the best one:

```python
def capture_best_flaw_frame(flaw_frames_window, flaw_data):
    """Capture the most representative frame from a window of flaw frames"""
    best_frame = None
    best_score = 0
    
    for frame_num in flaw_frames_window:
        # Score based on severity + visibility + phase appropriateness
        score = calculate_frame_quality_score(frame_num, flaw_data)
        if score > best_score:
            best_score = score
            best_frame = frame_num
    
    return best_frame
```

### **Strategy 4: Adaptive Phase Detection**

Improve phase boundary detection to be more robust:

```python
def detect_robust_phase_boundaries(frame_data, fps):
    """Use multiple metrics to determine phase boundaries more reliably"""
    # Combine velocity, acceleration, and pose data
    # Use smoothing to reduce frame-to-frame variations
    # Add confidence scoring for phase transitions
```

## Implementation Priority

### **Phase 1: Quick Wins (Immediate)**
1. Expand detection windows from ±2 to ±5 frames for critical flaws
2. Ensure flaw frames are never skipped during video processing
3. Add logging to track frame still capture accuracy

### **Phase 2: Medium-term (1-2 weeks)**
1. Implement multi-frame capture with quality scoring
2. Add frame quality validation before saving stills
3. Create fallback mechanisms for missed flaw frames

### **Phase 3: Long-term (1 month)**
1. Improve shot phase detection robustness
2. Add user feedback mechanism for frame accuracy
3. Implement machine learning-based optimal frame selection

## Expected Improvements

- **Frame Still Accuracy**: 85% → 95%+ alignment with detected flaws
- **User Trust**: Better visual confirmation of analysis findings
- **Coaching Value**: More effective visual feedback for form correction
- **System Reliability**: Consistent frame capture across different video types

## Validation Metrics

1. **Frame Alignment Score**: Percentage of frame stills that show the detected flaw
2. **Temporal Accuracy**: Average frame difference between detected flaw and captured still
3. **Visual Quality Score**: User ratings of frame still relevance (1-5 scale)
4. **Consistency Rate**: Frame accuracy across similar videos of same flaw type

## Testing Plan

1. **Regression Testing**: Ensure existing good cases aren't broken
2. **Edge Case Testing**: Test with challenging videos (poor lighting, fast motion)
3. **User Validation**: Coach review of frame still accuracy improvements
4. **Performance Testing**: Ensure changes don't impact processing speed significantly
