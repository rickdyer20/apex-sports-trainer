"""
Video Recording Guidelines Component for Basketball Shot Analysis
Provides comprehensive user guidance to ensure proper video orientation and quality
"""

RECORDING_GUIDELINES = {
    "orientation": {
        "title": "📱 Proper Video Orientation",
        "description": "Follow these guidelines to ensure your video is oriented correctly for accurate analysis",
        "guidelines": [
            {
                "icon": "📱",
                "title": "Hold Your Phone Horizontally (Landscape)",
                "description": "Always record in landscape mode (phone held sideways) for best results",
                "details": [
                    "Turn your phone 90 degrees so it's wider than it is tall",
                    "This gives our AI the full field view needed for accurate analysis",
                    "Avoid portrait mode (vertical) as it limits what we can see"
                ],
                "importance": "critical"
            },
            {
                "icon": "🎯",
                "title": "Frame the Shot Properly",
                "description": "Position yourself to capture the complete shooting motion",
                "details": [
                    "Stand to the side of the shooter (not in front or behind)",
                    "Include the entire body from feet to fingertips",
                    "Make sure the basket is visible in the frame",
                    "Keep 2-3 feet of space around the shooter"
                ],
                "importance": "critical"
            },
            {
                "icon": "⚖️",
                "title": "Keep Camera Level",
                "description": "Hold your phone straight and steady during recording",
                "details": [
                    "Don't tilt the phone left or right while recording",
                    "Use both hands to keep the phone steady",
                    "If using a tripod, ensure it's level"
                ],
                "importance": "important"
            }
        ]
    },
    "camera_angles": {
        "title": "📐 Best Camera Angles",
        "description": "Different angles reveal different aspects of shooting form",
        "angles": [
            {
                "name": "Side View (Recommended)",
                "icon": "👁️",
                "description": "Stand directly to the side of the shooter",
                "benefits": [
                    "Shows shot arc and release point",
                    "Reveals knee bend and body alignment", 
                    "Displays follow-through mechanics",
                    "Best for overall form analysis"
                ],
                "positioning": "Stand 8-10 feet to the shooter's right or left side",
                "optimal": True
            },
            {
                "name": "Front View",
                "icon": "👀", 
                "description": "Stand directly in front of the shooter",
                "benefits": [
                    "Shows shooting hand alignment",
                    "Reveals elbow positioning",
                    "Displays guide hand placement",
                    "Great for hand mechanics analysis"
                ],
                "positioning": "Stand 8-10 feet directly in front, slightly off-center",
                "optimal": False
            },
            {
                "name": "45-Degree Angle",
                "icon": "📐",
                "description": "Stand at a 45-degree angle to the shooter",
                "benefits": [
                    "Combines benefits of side and front views",
                    "Good compromise for overall analysis",
                    "Shows both arc and hand positioning"
                ],
                "positioning": "Stand 8-10 feet at a 45-degree angle to either side",
                "optimal": False
            }
        ]
    },
    "recording_tips": {
        "title": "🎥 Recording Best Practices",
        "description": "Technical tips for high-quality video capture",
        "tips": [
            {
                "category": "Lighting",
                "recommendations": [
                    "Record in good lighting - avoid backlighting",
                    "Indoor gym lighting is usually perfect",
                    "Avoid recording directly into sunlight outdoors",
                    "Make sure the shooter is well-lit, not shadowy"
                ]
            },
            {
                "category": "Timing",
                "recommendations": [
                    "Start recording 2-3 seconds before the shot begins",
                    "Keep recording until the ball reaches the basket",
                    "Capture the complete motion from setup to follow-through",
                    "One shot per video works best for analysis"
                ]
            },
            {
                "category": "Stability",
                "recommendations": [
                    "Hold the phone with both hands",
                    "Keep your elbows close to your body for stability",
                    "Don't follow the ball's flight - keep the camera on the shooter",
                    "Use a tripod if available for best results"
                ]
            },
            {
                "category": "Quality",
                "recommendations": [
                    "Use your phone's highest video quality setting",
                    "Ensure the shooter fills about 60-80% of the frame",
                    "Keep the camera still - don't zoom during recording",
                    "Make sure focus is locked on the shooter"
                ]
            }
        ]
    },
    "common_mistakes": {
        "title": "❌ Common Recording Mistakes to Avoid",
        "description": "These mistakes can affect analysis accuracy",
        "mistakes": [
            {
                "mistake": "Recording in Portrait Mode",
                "icon": "📱",
                "why_bad": "Limits field of view and makes analysis difficult",
                "solution": "Always hold phone horizontally (landscape mode)"
            },
            {
                "mistake": "Standing Too Close",
                "icon": "🔍",
                "why_bad": "Cuts off parts of the shooting motion",
                "solution": "Stand 8-10 feet away to capture full body"
            },
            {
                "mistake": "Following the Ball",
                "icon": "🏀",
                "why_bad": "Loses focus on the shooter's form",
                "solution": "Keep camera focused on the shooter, not the ball"
            },
            {
                "mistake": "Recording in Poor Lighting",
                "icon": "🌑",
                "why_bad": "Makes body landmarks hard to detect",
                "solution": "Ensure good, even lighting on the shooter"
            },
            {
                "mistake": "Tilted Camera",
                "icon": "📐",
                "why_bad": "Creates orientation issues for analysis",
                "solution": "Keep phone level and straight during recording"
            },
            {
                "mistake": "Recording Multiple Shots",
                "icon": "🎯",
                "why_bad": "Confuses the analysis algorithm",
                "solution": "Record one shot per video for best results"
            }
        ]
    },
    "device_specific": {
        "title": "📲 Device-Specific Tips",
        "description": "Platform-specific guidance for optimal recording",
        "platforms": [
            {
                "device": "iPhone",
                "tips": [
                    "Use built-in Camera app for best quality",
                    "Enable 'Record Video' at 1080p or 4K",
                    "Turn OFF 'Auto' settings during recording",
                    "Use Volume buttons to start/stop recording for stability"
                ]
            },
            {
                "device": "Android",
                "tips": [
                    "Use native camera app or Google Camera",
                    "Set video quality to 1080p minimum",
                    "Disable auto-rotation during recording",
                    "Use Pro mode for manual focus if available"
                ]
            },
            {
                "device": "Tablet",
                "tips": [
                    "Tablets work great as larger screens show more detail",
                    "Use a stand or tripod as tablets are harder to hold steady",
                    "Same orientation rules apply - always landscape",
                    "Consider using timer mode to avoid shake when starting"
                ]
            }
        ]
    }
}

def get_recording_guidelines_html():
    """Generate HTML for the recording guidelines section"""
    return """
    <div class="recording-guidelines">
        <div class="alert alert-info">
            <h5><i class="fas fa-info-circle me-2"></i>Important: Record in Landscape Mode</h5>
            <p class="mb-0">For best results, always hold your phone sideways (landscape) when recording. This gives our AI the full view needed for accurate analysis.</p>
        </div>
        
        <div class="row">
            <div class="col-md-6">
                <div class="card mb-3">
                    <div class="card-header bg-success text-white">
                        <h6 class="mb-0"><i class="fas fa-check me-2"></i>Correct - Landscape Mode</h6>
                    </div>
                    <div class="card-body text-center">
                        <div class="orientation-demo landscape-demo mb-2">
                            <i class="fas fa-mobile-alt fa-3x"></i>
                        </div>
                        <small class="text-success">Phone held sideways - captures full shooting form</small>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card mb-3">
                    <div class="card-header bg-danger text-white">
                        <h6 class="mb-0"><i class="fas fa-times me-2"></i>Incorrect - Portrait Mode</h6>
                    </div>
                    <div class="card-body text-center">
                        <div class="orientation-demo portrait-demo mb-2">
                            <i class="fas fa-mobile-alt fa-3x"></i>
                        </div>
                        <small class="text-danger">Phone held upright - limits field of view</small>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """

def get_recording_checklist():
    """Generate a simple checklist for users"""
    return [
        "📱 Phone is held horizontally (landscape mode)",
        "👁️ Standing to the side of the shooter (8-10 feet away)", 
        "🎯 Entire body visible from feet to fingertips",
        "🏀 Basket is visible in the frame",
        "💡 Good lighting on the shooter",
        "📐 Camera is level and steady",
        "⏱️ Recording starts before the shot begins",
        "🎥 Using highest video quality setting"
    ]
