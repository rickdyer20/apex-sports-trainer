"""
Recording Guidance Notice for Basketball Shot Analysis Web Interface
Simple HTML snippet to embed in upload forms
"""

RECORDING_GUIDANCE_HTML = """
<!-- RECORDING GUIDANCE NOTICE -->
<div class="alert alert-info mb-4" style="border-left: 4px solid #007bff; background: linear-gradient(135deg, #e3f2fd 0%, #f8f9fa 100%);">
    <div class="row align-items-center">
        <div class="col-md-1 text-center">
            <i class="fas fa-mobile-alt fa-3x text-primary"></i>
        </div>
        <div class="col-md-11">
            <h5 class="alert-heading mb-2">
                <i class="fas fa-exclamation-triangle text-warning"></i>
                <strong>Important: Record Your Video Correctly!</strong>
            </h5>
            <p class="mb-2">
                <strong>🔄 We DO NOT auto-rotate sideways videos.</strong> 
                For best analysis results, please follow these guidelines:
            </p>
            <div class="row">
                <div class="col-md-6">
                    <ul class="list-unstyled mb-0">
                        <li><i class="fas fa-check text-success"></i> <strong>Hold phone sideways</strong> (landscape mode)</li>
                        <li><i class="fas fa-check text-success"></i> <strong>Lock screen rotation</strong> before recording</li>
                        <li><i class="fas fa-check text-success"></i> <strong>Stand 8-10 feet to the side</strong> of shooter</li>
                    </ul>
                </div>
                <div class="col-md-6">
                    <ul class="list-unstyled mb-0">
                        <li><i class="fas fa-check text-success"></i> <strong>Show full body</strong> (head to toes)</li>
                        <li><i class="fas fa-check text-success"></i> <strong>Keep camera steady</strong> - don't follow ball</li>
                        <li><i class="fas fa-check text-success"></i> <strong>One shot per video</strong> works best</li>
                    </ul>
                </div>
            </div>
            <div class="mt-2">
                <small class="text-muted">
                    <i class="fas fa-info-circle"></i>
                    <strong>Why we don't auto-rotate:</strong> 
                    Proper recording ensures better analysis accuracy and video quality. 
                    Taking 30 seconds to set up correctly saves time later!
                </small>
            </div>
        </div>
    </div>
</div>

<!-- QUICK VISUAL GUIDE -->
<div class="card mb-4" style="border: 2px solid #28a745;">
    <div class="card-header bg-success text-white">
        <h6 class="mb-0">
            <i class="fas fa-video"></i>
            Quick Visual Guide: How to Hold Your Phone
        </h6>
    </div>
    <div class="card-body">
        <div class="row text-center">
            <div class="col-md-6">
                <div class="p-3 bg-success text-white rounded mb-2">
                    <i class="fas fa-mobile-alt fa-3x" style="transform: rotate(90deg);"></i>
                    <h6 class="mt-2 mb-0">✅ CORRECT</h6>
                    <small>Landscape (sideways)</small>
                </div>
                <p class="text-success"><strong>Perfect for basketball analysis!</strong></p>
            </div>
            <div class="col-md-6">
                <div class="p-3 bg-danger text-white rounded mb-2">
                    <i class="fas fa-mobile-alt fa-3x"></i>
                    <h6 class="mt-2 mb-0">❌ WRONG</h6>
                    <small>Portrait (upright)</small>
                </div>
                <p class="text-danger"><strong>Will display sideways in results!</strong></p>
            </div>
        </div>
    </div>
</div>
"""

SIMPLE_NOTICE_HTML = """
<!-- SIMPLE RECORDING NOTICE -->
<div class="alert alert-warning mb-3" role="alert">
    <strong><i class="fas fa-mobile-alt"></i> Recording Tip:</strong> 
    Hold your phone <strong>sideways (landscape mode)</strong> and show the shooter's full body from the side. 
    We don't auto-rotate videos, so proper recording ensures the best analysis results!
    <a href="#" class="alert-link" onclick="toggleRecordingGuide()">View detailed guide →</a>
</div>
"""

MOBILE_SPECIFIC_NOTICE = """
<!-- MOBILE-SPECIFIC NOTICE (Shows only on mobile devices) -->
<div class="alert alert-primary d-block d-md-none mb-3" role="alert">
    <h6><i class="fas fa-smartphone"></i> Mobile Recording Steps:</h6>
    <ol class="mb-0">
        <li><strong>Turn your phone sideways</strong> (landscape mode)</li>
        <li><strong>Lock screen rotation</strong> in Control Center/Settings</li>
        <li><strong>Stand to the side</strong> of the shooter (8-10 feet away)</li>
        <li><strong>Record the complete shot</strong> from setup to follow-through</li>
    </ol>
    <small class="text-muted">
        💡 <strong>Remember:</strong> We don't auto-rotate sideways videos for better quality!
    </small>
</div>
"""

JAVASCRIPT_HELPERS = """
<script>
function toggleRecordingGuide() {
    const guide = document.getElementById('recordingGuideDetails');
    if (guide.style.display === 'none' || guide.style.display === '') {
        guide.style.display = 'block';
        guide.scrollIntoView({ behavior: 'smooth' });
    } else {
        guide.style.display = 'none';
    }
}

function detectMobileAndShowTips() {
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    if (isMobile) {
        // Show mobile-specific recording tips
        const mobileNotices = document.querySelectorAll('.mobile-only');
        mobileNotices.forEach(notice => notice.style.display = 'block');
        
        // Add mobile-specific CSS classes
        document.body.classList.add('mobile-device');
    }
}

// Run on page load
document.addEventListener('DOMContentLoaded', detectMobileAndShowTips);
</script>
"""

def get_recording_guidance_notice(notice_type="full"):
    """
    Get HTML for recording guidance notice
    
    Args:
        notice_type: "full", "simple", "mobile", or "javascript"
    """
    notices = {
        "full": RECORDING_GUIDANCE_HTML,
        "simple": SIMPLE_NOTICE_HTML,
        "mobile": MOBILE_SPECIFIC_NOTICE,
        "javascript": JAVASCRIPT_HELPERS
    }
    
    return notices.get(notice_type, SIMPLE_NOTICE_HTML)
