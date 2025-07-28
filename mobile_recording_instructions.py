"""
Mobile Recording Instructions for Basketball Shot Analysis
Provides device-specific guidance for proper video orientation
"""

MOBILE_INSTRUCTIONS = {
    "ios": {
        "title": "📱 iPhone Recording Instructions",
        "steps": [
            {
                "step": 1,
                "title": "Lock Screen Rotation",
                "instruction": "Before recording, lock your screen rotation to landscape",
                "details": [
                    "Swipe down from top-right corner (Control Center)",
                    "Tap the screen rotation lock button",
                    "Turn your phone sideways to landscape orientation"
                ]
            },
            {
                "step": 2,
                "title": "Open Camera App",
                "instruction": "Use the built-in Camera app for best quality",
                "details": [
                    "Tap on 'Video' mode at the bottom",
                    "Make sure you're holding the phone horizontally",
                    "Check that the video preview shows landscape orientation"
                ]
            },
            {
                "step": 3,
                "title": "Frame Your Shot",
                "instruction": "Position yourself 8-10 feet to the side of the shooter",
                "details": [
                    "The entire shooter should be visible from feet to fingertips",
                    "Focus on shooter's form (hoop optional)",
                    "Tap on the shooter to focus the camera"
                ]
            },
            {
                "step": 4,
                "title": "Start Recording",
                "instruction": "Use volume buttons to start/stop for stability",
                "details": [
                    "Press Volume Up or Volume Down to start recording",
                    "Keep the phone steady - don't follow the ball",
                    "Record the complete shot motion"
                ]
            }
        ]
    },
    "android": {
        "title": "🤖 Android Recording Instructions", 
        "steps": [
            {
                "step": 1,
                "title": "Disable Auto-Rotate",
                "instruction": "Turn off auto-rotation before recording",
                "details": [
                    "Swipe down to open notification panel",
                    "Look for 'Auto-rotate' or screen rotation icon",
                    "Tap to disable, then turn phone to landscape"
                ]
            },
            {
                "step": 2,
                "title": "Open Camera App",
                "instruction": "Use your phone's native camera app",
                "details": [
                    "Switch to Video mode",
                    "Hold phone horizontally (landscape orientation)",
                    "Set video quality to 1080p or higher if available"
                ]
            },
            {
                "step": 3,
                "title": "Manual Focus",
                "instruction": "Set focus on the shooter for clear analysis",
                "details": [
                    "Tap on the shooter to focus camera",
                    "If available, use Pro mode for manual focus",
                    "Ensure good lighting on the subject"
                ]
            },
            {
                "step": 4,
                "title": "Record Video",
                "instruction": "Start recording before the shot begins",
                "details": [
                    "Press record button or use volume keys",
                    "Keep camera focused on shooter, not the ball",
                    "Maintain steady hands throughout recording"
                ]
            }
        ]
    }
}

QUICK_REFERENCE_CARD = """
📱 QUICK RECORDING CHECKLIST

BEFORE YOU RECORD:
✅ Turn phone sideways (landscape mode)  
✅ Lock screen rotation to prevent flipping
✅ Stand 8-10 feet to the shooter's side
✅ Focus on shooter's form (hoop optional)

DURING RECORDING:
✅ Keep phone steady with both hands
✅ Don't follow the ball - focus on shooter
✅ Record from setup through follow-through
✅ Use volume buttons to start/stop

AFTER RECORDING:
✅ Check video shows full body in landscape
✅ Verify good lighting and clarity
✅ Upload immediately for best quality
✅ One shot per video works best

❌ AVOID THESE MISTAKES:
• Recording in portrait (vertical) mode
• Standing too close or too far away  
• Following the ball's flight path
• Recording multiple shots in one video
• Poor lighting or shaky footage
"""

def generate_device_detection_script():
    """Generate JavaScript to detect device and show appropriate instructions"""
    return """
    <script>
    function detectDeviceAndShowInstructions() {
        const userAgent = navigator.userAgent.toLowerCase();
        const isIOS = /iphone|ipad|ipod/.test(userAgent);
        const isAndroid = /android/.test(userAgent);
        const isMobile = isIOS || isAndroid;
        
        if (isMobile) {
            showMobileInstructions(isIOS ? 'ios' : 'android');
        }
    }
    
    function showMobileInstructions(platform) {
        const instructionsModal = document.getElementById('mobileInstructionsModal');
        const instructionsContent = document.getElementById('mobileInstructionsContent');
        
        if (platform === 'ios') {
            instructionsContent.innerHTML = generateIOSInstructions();
        } else {
            instructionsContent.innerHTML = generateAndroidInstructions();
        }
        
        // Show modal automatically for mobile users
        const modal = new bootstrap.Modal(instructionsModal);
        modal.show();
    }
    
    function generateIOSInstructions() {
        return `
            <h5><i class="fab fa-apple me-2"></i>iPhone Recording Instructions</h5>
            <div class="alert alert-primary">
                <strong>Important:</strong> Hold your phone sideways (landscape) for best results!
            </div>
            <ol>
                <li class="mb-2">
                    <strong>Lock Screen Rotation:</strong><br>
                    <small>Control Center → Tap rotation lock → Turn phone sideways</small>
                </li>
                <li class="mb-2">
                    <strong>Open Camera App:</strong><br>
                    <small>Select Video mode → Hold phone horizontally</small>
                </li>
                <li class="mb-2">
                    <strong>Position Yourself:</strong><br>
                    <small>Stand 8-10 feet to the shooter's side</small>
                </li>
                <li class="mb-2">
                    <strong>Start Recording:</strong><br>
                    <small>Use volume buttons to record → Keep steady</small>
                </li>
            </ol>
        `;
    }
    
    function generateAndroidInstructions() {
        return `
            <h5><i class="fab fa-android me-2"></i>Android Recording Instructions</h5>
            <div class="alert alert-success">
                <strong>Important:</strong> Hold your phone sideways (landscape) for best results!
            </div>
            <ol>
                <li class="mb-2">
                    <strong>Disable Auto-Rotate:</strong><br>
                    <small>Notification panel → Turn off auto-rotate → Turn phone sideways</small>
                </li>
                <li class="mb-2">
                    <strong>Open Camera:</strong><br>
                    <small>Switch to Video mode → Set to 1080p quality</small>
                </li>
                <li class="mb-2">
                    <strong>Focus on Shooter:</strong><br>
                    <small>Tap shooter to focus → Use Pro mode if available</small>
                </li>
                <li class="mb-2">
                    <strong>Record Video:</strong><br>
                    <small>Press record → Keep steady → Don't follow ball</small>
                </li>
            </ol>
        `;
    }
    
    // Run detection when page loads
    document.addEventListener('DOMContentLoaded', detectDeviceAndShowInstructions);
    </script>
    `;
}

def get_mobile_instructions_modal():
    """Generate HTML for mobile instructions modal"""
    return """
    <!-- Mobile Instructions Modal -->
    <div class="modal fade" id="mobileInstructionsModal" tabindex="-1" aria-labelledby="mobileInstructionsLabel" aria-hidden="true">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="mobileInstructionsLabel">
                        <i class="fas fa-mobile-alt me-2"></i>Mobile Recording Instructions
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body" id="mobileInstructionsContent">
                    <!-- Content populated by JavaScript -->
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-primary" data-bs-dismiss="modal">Got It!</button>
                </div>
            </div>
        </div>
    </div>
    """
