#!/usr/bin/env python3
"""
Quick test for orientation correction logic
"""
import cv2
import numpy as np
from basketball_analysis_service import detect_and_correct_orientation

def test_orientation_correction():
    print("Testing Orientation Correction Logic")
    print("=" * 40)
    
    # Test 1: Normal landscape frame (no correction needed)
    normal_frame = np.zeros((480, 640, 3), dtype=np.uint8)  # 640x480 (landscape)
    result1 = detect_and_correct_orientation(normal_frame)
    print(f"Test 1 - Normal landscape (640x480):")
    print(f"  Input shape: {normal_frame.shape}")
    print(f"  Output shape: {result1.shape}")
    print(f"  Aspect ratio: {result1.shape[1]/result1.shape[0]:.2f}")
    print()
    
    # Test 2: Portrait frame (should be corrected)
    portrait_frame = np.zeros((640, 480, 3), dtype=np.uint8)  # 480x640 (portrait)
    result2 = detect_and_correct_orientation(portrait_frame)
    print(f"Test 2 - Portrait orientation (480x640):")
    print(f"  Input shape: {portrait_frame.shape}")
    print(f"  Output shape: {result2.shape}")  
    print(f"  Aspect ratio: {result2.shape[1]/result2.shape[0]:.2f}")
    print()
    
    # Test 3: Very wide frame (might need counter-clockwise)
    wide_frame = np.zeros((300, 900, 3), dtype=np.uint8)  # 900x300 (very wide)
    result3 = detect_and_correct_orientation(wide_frame)
    print(f"Test 3 - Very wide (900x300):")
    print(f"  Input shape: {wide_frame.shape}")
    print(f"  Output shape: {result3.shape}")
    print(f"  Aspect ratio: {result3.shape[1]/result3.shape[0]:.2f}")
    print()
    
    print("✅ Orientation correction tests completed!")
    print("\nLogic Summary:")
    print("- Aspect ratio < 0.75: Apply 90° clockwise rotation")
    print("- Aspect ratio > 1.8: Apply 90° counter-clockwise rotation") 
    print("- Normal range (0.75-1.8): No correction applied")

if __name__ == "__main__":
    test_orientation_correction()
