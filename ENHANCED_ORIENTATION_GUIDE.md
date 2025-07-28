# Enhanced Orientation Correction v2.0 Guide

## Overview
The enhanced orientation correction system automatically detects and fixes sideways videos and stills in basketball shot analysis downloads. Version 2.0 uses multiple detection methods for improved accuracy.

## Key Improvements in v2.0

### 🔍 Enhanced Detection Methods
1. **Improved Aspect Ratio Analysis**
   - More sensitive thresholds (0.8 instead of 0.75)
   - Better handling of edge cases
   - Focus on basketball viewing optimization

2. **Phone Recording Detection**
   - Automatically detects common portrait phone resolutions:
     - 1080x1920 (iPhone portrait)
     - 720x1280 (Android portrait)
   - Converts to landscape for better basketball viewing

3. **Content-Based Analysis**
   - Uses gradient analysis for square-ish videos
   - Analyzes pixel intensity patterns
   - Intelligent decision making for edge cases

4. **Ultra-Wide Detection**
   - Handles videos with extreme aspect ratios (>2.2:1)
   - Corrects likely sideways ultra-wide recordings

### 🏀 Basketball-Focused Logic
The system is specifically optimized for basketball video viewing:
- **Goal**: Convert portrait videos to landscape format
- **Reasoning**: Basketball courts are horizontal, players move side-to-side
- **Result**: Better viewing experience in analysis downloads

## How It Works

### Detection Process
```
1. Analyze frame dimensions and aspect ratio
2. Check for common phone recording formats
3. Apply content-based analysis if needed
4. Determine optimal rotation for basketball viewing
5. Apply rotation and verify improvement
```

### Rotation Logic
- **Portrait videos (aspect < 0.8)**: Rotate to landscape (90° counter-clockwise)
- **Ultra-wide videos (aspect > 2.2)**: Likely sideways, rotate to normal (90° clockwise)
- **Phone formats**: Convert vertical recordings to horizontal
- **Square videos**: Use content analysis to determine if rotation needed

## Usage

### Easy Toggle System
```bash
# Enable enhanced orientation correction
python toggle_orientation_v2.py on

# Disable orientation correction
python toggle_orientation_v2.py off

# Check current status
python toggle_orientation_v2.py status
```

### Testing
```bash
# Test with basketball-focused scenarios
python test_basketball_orientation.py

# Comprehensive testing (all scenarios)
python test_orientation_v2.py
```

## Examples

### Common Scenarios

| Original Format | Action Taken | Result | Reason |
|----------------|--------------|---------|---------|
| 1080x1920 (portrait) | ✅ Rotate 90° CCW | 1920x1080 (landscape) | Better basketball viewing |
| 1920x1080 (landscape) | ℹ️ No change | 1920x1080 (landscape) | Already optimal |
| 1080x1080 (square) | 🔍 Content analysis | Varies | Depends on content |
| 720x1280 (portrait) | ✅ Rotate 90° CCW | 1280x720 (landscape) | Phone recording fix |

### Real User Cases
1. **"User holds phone vertically while recording"**
   - Before: 1080x1920 (portrait, hard to see court)
   - After: 1920x1080 (landscape, perfect for basketball)

2. **"Proper landscape recording"**
   - Before: 1920x1080 (already good)
   - After: 1920x1080 (no change needed)

3. **"Tablet held wrong way"**
   - Before: 1536x2048 (portrait tablet)
   - After: 2048x1536 (landscape, much better)

## Technical Details

### Detection Thresholds
- **Portrait detection**: aspect ratio < 0.8
- **Ultra-wide detection**: aspect ratio > 2.2
- **Content analysis trigger**: 0.9 ≤ aspect ratio ≤ 1.1
- **Gradient threshold**: vertical strength > horizontal × 1.8

### Safety Features
- **Easy disable**: Single flag to turn off if problems occur
- **Error handling**: Falls back to original frame if rotation fails
- **Logging**: Detailed logs of all decisions for debugging
- **Verification**: Confirms rotation improved aspect ratio

## Troubleshooting

### If Videos Still Appear Sideways
```bash
# Check current status
python toggle_orientation_v2.py status

# If disabled, enable it
python toggle_orientation_v2.py on

# Test with your video format
python test_basketball_orientation.py
```

### If Rotation Is Wrong Direction
The system is designed for basketball viewing optimization. If videos look wrong:
1. Check if the original video was actually recorded sideways
2. The system prioritizes landscape format for basketball courts
3. Use the easy disable if this doesn't work for your use case

### Quick Disable
```bash
# If anything goes wrong, quickly disable
python toggle_orientation_v2.py off
```

## Performance Impact

### Minimal Overhead
- Only processes frames that need rotation
- Fast OpenCV rotation operations
- No impact on videos that don't need correction

### Memory Efficient
- Processes frames individually
- No batch operations that could cause memory issues
- Same memory footprint as original system

## Deployment Status

### Current Status: ✅ ACTIVE
- Enhanced v2.0 deployed to Railway
- Available at: https://trite-comb-production.up.railway.app
- All safety mechanisms in place
- Easy rollback available

### Monitoring
- Rotation decisions logged for analysis
- Performance metrics tracked
- Error handling with fallbacks

## Version History

### v2.0 (Current)
- Enhanced multi-heuristic detection
- Basketball-focused optimization
- Content-based analysis
- Phone recording format detection
- Improved accuracy and logging

### v1.0 (Previous)
- Basic aspect ratio detection
- Simple threshold-based rotation
- Conservative approach

---

## Quick Commands Reference

```bash
# Enable enhanced orientation correction
python toggle_orientation_v2.py on

# Disable if needed  
python toggle_orientation_v2.py off

# Check status
python toggle_orientation_v2.py status

# Test functionality
python test_basketball_orientation.py
```

**Note**: The enhanced system is specifically optimized for basketball video analysis and focuses on providing the best viewing experience for basketball content in landscape format.
