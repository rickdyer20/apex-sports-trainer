<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Basketball Shot Analysis Service - Copilot Instructions

This is a sophisticated basketball shot analysis service that uses computer vision and MediaPipe for pose estimation. The service is designed with production-ready architecture including:

## Project Structure
- **Data Models**: VideoAnalysisJob, FrameData, ShotPhase, FeedbackPoint, AnalysisReport
- **Computer Vision**: MediaPipe pose estimation for real-time body landmark detection
- **Analysis Engine**: Biomechanical analysis with angle calculations and phase identification
- **Cloud Integration**: Simulated S3/GCS storage for video processing workflows
- **Output Generation**: Slow-motion analysis videos with overlays and feedback visualization

## Key Technologies
- **MediaPipe**: Google's pose estimation framework
- **OpenCV**: Video processing and computer vision operations
- **NumPy**: Mathematical computations for angle calculations
- **Logging**: Comprehensive logging for production monitoring

## Code Quality Guidelines
- Follow production service patterns with proper error handling
- Use type hints for all function parameters and return values
- Implement comprehensive logging for debugging and monitoring
- Structure code with clear separation between data models, utilities, and processing logic
- Design for scalability with cloud storage and queue-based processing in mind

## Biomechanical Analysis Focus
- Calculate joint angles (elbow, knee, wrist) for shot mechanics
- Identify shot phases (load/dip, release, follow-through)
- Compare user metrics against ideal shooting form ranges
- Generate actionable feedback with specific coaching tips
- Create visual overlays highlighting form discrepancies
