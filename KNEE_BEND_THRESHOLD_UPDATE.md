# Knee Bend Detection Threshold Update

## Change Applied ✅
**Update**: Made insufficient knee bend detection more strict
**New Threshold**: 130° (was 135°)

## What Changed

### **Before**
- Insufficient knee bend flagged when > 135°
- Tolerance range: 105° - 135° (30° window)
- More lenient detection

### **After**  
- Insufficient knee bend flagged when > 130°
- Tolerance range: 105° - 130° (25° window)
- Stricter detection for better coaching

## Impact Analysis

### **Angles Now Flagged**
- **131° - 135°**: Previously acceptable, now flagged as insufficient
- Better catches marginally shallow knee bends

### **Still Acceptable**
- **105° - 130°**: Good knee bend range
- **At 130°**: Right at the ideal maximum, still OK

### **Detection Ranges**
```
Excessive:     < 105°  [Unchanged - very deep bends]
Acceptable:  105° - 130°  [Narrowed by 5° for stricter standards]  
Insufficient:  > 130°  [Stricter - better coaching precision]
```

## Example Scenarios

| Knee Angle | Previous | New | Impact |
|------------|----------|-----|---------|
| 125° | ✅ Good | ✅ Good | No change |
| 130° | ✅ Good | ✅ Good | No change |
| 132° | ✅ Good | ⚠️ Insufficient | Now flagged |
| 135° | ⚠️ Insufficient | ⚠️ Insufficient | No change |
| 140° | ⚠️ Insufficient | ⚠️ Insufficient | No change |

## Coaching Benefits

### **Improved Detection**
- ✅ Catches marginally insufficient knee bends
- ✅ Better alignment with ideal 110° - 130° range
- ✅ More precise coaching feedback
- ✅ Encourages proper loading technique

### **Balanced Approach**
- 🎯 Still conservative (not overly strict)
- 🎯 Focuses on meaningful improvements
- 🎯 Maintains reasonable tolerance
- 🎯 Avoids false positives for borderline cases

## Technical Details

### **Threshold Logic**
```python
# OLD: if actual > ideal_min + 25 (135°)
# NEW: if actual > 130
```

### **Severity Calculation**
- Adjusted severity factor for new threshold
- Maintains reasonable severity scores
- Cap at 40 maximum severity

## Current Status
🎉 **Insufficient knee bend detection is now more strict at 130°**

This change provides better coaching precision while maintaining a balanced approach to flaw detection. Players with knee bends between 131° - 135° will now receive feedback to improve their loading technique for better power generation.
