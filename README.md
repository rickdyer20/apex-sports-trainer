# 🏀 Basketball Shot Analysis Service

A sophisticated basketball shot analysis service that uses computer vision and MediaPipe for pose estimation to provide detailed biomechanical analysis and personalized coaching feedback.

## Features

### 🎯 Advanced Computer Vision Analysis
- **MediaPipe Pose Estimation**: Real-time body landmark detection
- **Biomechanical Analysis**: Joint angle calculations and movement analysis
- **Shot Phase Identification**: Automatic detection of load/dip, release, and follow-through phases
- **8 Types of Flaw Detection**: Comprehensive shooting form analysis

### 📊 Detailed Flaw Analysis
1. **Elbow Flare**: Shooting elbow positioning analysis
2. **Knee Bend Issues**: Insufficient or excessive knee bend detection
3. **Poor Follow-Through**: Wrist snap and follow-through analysis
4. **Balance Problems**: Center of gravity and stability analysis
5. **Rushing Shot**: Timing and rhythm evaluation
6. **Guide Hand Interference**: Off-hand positioning analysis
7. **Inconsistent Release Point**: Release consistency evaluation
8. **Release Point Analysis**: Optimal release positioning

### 🎥 Visual Analysis Output
- **Slow-Motion Analysis Video**: Frame-by-frame breakdown with overlays
- **Educational Frame Stills**: 8 key frames showing detected flaws with explanations
- **Biomechanical Overlays**: Highlighted landmarks and angle measurements
- **Plain Language Coaching**: Easy-to-understand feedback for all skill levels

### 📋 Professional PDF Reports
- **60-Day Improvement Plan**: Structured training program
- **Detailed Flaw Analysis**: Scientific explanations of detected issues
- **Progressive Training Phases**: Foundation → Development → Integration → Mastery
- **Comprehensive Drill Library**: Step-by-step instructions with coaching points
- **Progress Tracking System**: Benchmarks, goals, and re-evaluation schedules
- **Scientific References**: Research-backed training methodologies

### 🌐 Web Interface
- **User-Friendly Upload**: Drag-and-drop video upload with validation
- **Real-Time Progress**: Live analysis progress tracking
- **Complete Download Package**: ZIP files with all analysis components
- **Professional Results Display**: Clean, organized results presentation

## Technology Stack

- **Python 3.12**: Core application framework
- **MediaPipe 0.10.21**: Google's pose estimation framework
- **OpenCV 4.11.0.86**: Video processing and computer vision
- **Flask 3.1.1**: Web application framework with Bootstrap UI
- **ReportLab 4.4.2**: Professional PDF generation
- **NumPy**: Mathematical computations for biomechanical analysis

## Project Structure

```
basketball_analysis_service/
├── basketball_analysis_service.py    # Core analysis engine
├── pdf_generator.py                  # Professional PDF generation
├── web_app.py                       # Flask web application
├── templates/
│   ├── index.html                   # Upload interface
│   └── results.html                 # Results display
├── static/
│   └── style.css                    # Web interface styling
├── results/                         # Generated analysis outputs
├── uploads/                         # Temporary upload storage
└── README.md                        # This file
```

## Installation

1. **Clone Repository**:
   ```bash
   git clone <repository-url>
   cd basketball_analysis_service
   ```

2. **Create Python Environment**:
   ```bash
   conda create -n basketball_analysis python=3.12
   conda activate basketball_analysis
   ```

3. **Install Dependencies**:
   ```bash
   pip install mediapipe==0.10.21
   pip install opencv-python==4.11.0.86
   pip install flask==3.1.1
   pip install reportlab==4.4.2
   pip install numpy
   ```

## Usage

### Web Application

1. **Start the Web Server**:
   ```bash
   python web_app.py
python basketball_analysis_service.py
   ```

2. **Open Browser**: Navigate to `http://127.0.0.1:5000`

3. **Upload Video**: Upload a basketball shooting video (MP4, AVI, MOV)

4. **Receive Analysis**: Download complete package including:
   - Analyzed video with slow-motion and overlays
   - 8 educational frame stills with flaw explanations
   - 60-day improvement plan PDF
   - Text summary of findings

### Command Line

```bash
python basketball_analysis_service.py
```

## Analysis Components

### Biomechanical Metrics
- **Joint Angles**: Elbow, knee, wrist positioning
- **Movement Velocities**: Joint movement speeds and accelerations
- **Balance Analysis**: Center of gravity and stability metrics
- **Timing Analysis**: Phase durations and rhythm evaluation

### Shot Phases
1. **Load/Dip Phase**: Preparation and energy storage
2. **Release Phase**: Ball release mechanics
3. **Follow-Through Phase**: Post-release form

### Feedback System
- **Frame-Specific Analysis**: Exact problematic moments identified
- **Severity Scoring**: Quantified impact on shooting performance
- **Coaching Tips**: Actionable improvement strategies
- **Drill Recommendations**: Specific practice exercises

## PDF Improvement Plan

### Structure
- **Executive Summary**: Overview of analysis and priority areas
- **Detailed Flaw Analysis**: Scientific explanations of detected issues
- **60-Day Progressive Plan**: Structured improvement timeline
- **Weekly Training Schedules**: Daily practice plans (45-60 minutes)
- **Comprehensive Drill Library**: Step-by-step coaching instructions
- **Progress Tracking**: Benchmarks and re-evaluation guidelines
- **Professional Resources**: Video references and scientific citations

### Training Phases
1. **Foundation (Days 1-15)**: Basic mechanics and critical flaw correction
2. **Development (Days 16-30)**: Technique refinement
3. **Integration (Days 31-45)**: Game-like shooting scenarios
4. **Mastery (Days 46-60)**: Advanced techniques and pressure situations

## File Formats

### Supported Input
- **Video**: MP4, AVI, MOV (with visible human poses)
- **Resolution**: 640x480 minimum recommended
- **Duration**: 2-30 seconds optimal for analysis

### Generated Output
- **Analyzed Video**: MP4 with overlays and slow-motion
- **Frame Stills**: PNG images with educational overlays
- **PDF Report**: Professional improvement plan
- **Summary**: Text file with key findings
- **ZIP Package**: Complete analysis bundle

## Production Considerations

### Scalability
- **Cloud Storage Integration**: S3/GCS compatibility for video processing
- **Queue-Based Processing**: Background job handling for multiple users
- **Microservices Architecture**: Modular component design
- **API Endpoints**: RESTful service integration

### Performance
- **Optimized MediaPipe**: Efficient pose estimation processing
- **Video Compression**: Smart output file size management
- **Caching Strategy**: Reduced processing for similar analyses
- **Progress Tracking**: Real-time user feedback

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/improvement`)
5. Create Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Citation

If you use this software in research or commercial applications, please cite:

```
Basketball Shot Analysis Service
Advanced Computer Vision and Biomechanical Analysis for Basketball Shooting Improvement
2025
```

## Support

For technical support or questions:
- Create an issue in the GitHub repository
- Check the documentation for common solutions
- Review the PDF improvement plans for coaching guidance

## Acknowledgments

- **MediaPipe Team**: For providing excellent pose estimation capabilities
- **OpenCV Community**: For comprehensive computer vision tools
- **Basketball Coaching Community**: For domain expertise and validation
- **Scientific Research**: Biomechanical analysis methodologies

---

Transform your basketball shooting with AI-powered analysis and professional coaching guidance! 🏀
2. **Pose Detection**: MediaPipe body landmark extraction
3. **Metric Calculation**: Joint angle and velocity computations
4. **Temporal Analysis**: Multi-frame pattern recognition

### Cloud Integration
- **Storage**: Simulated S3/GCS integration for video files
- **Processing**: Queue-based job management
- **Monitoring**: Comprehensive logging and error handling
- **Scalability**: Designed for serverless deployment

## Development

### Local Testing
Place a basketball shot video named `user_shot.mp4` in the project directory for realistic testing. The script will create a dummy video if none exists.

### Configuration
Ideal shot parameters can be customized via `ideal_shot_guide.json`:

```json
{
  "release_elbow_angle": {"min": 160, "max": 180},
  "load_knee_angle": {"min": 110, "max": 130},
  "common_remedies": {
    "elbow_extension": "Focus on fully extending your elbow towards the basket.",
    "knee_drive": "Explode upwards by pushing through your heels."
  }
}
```

## Deployment

### Serverless Functions
The service is designed for deployment as AWS Lambda, Google Cloud Functions, or Azure Functions with minimal modifications.

### Container Deployment
Can be containerized using Docker for deployment in Kubernetes or container services.

### Queue Integration
Supports integration with AWS SQS, Google Pub/Sub, or Azure Service Bus for scalable processing.

## License

This project is designed for educational and demonstration purposes.

## Contributing

Contributions are welcome! Please ensure all code follows the established patterns and includes appropriate testing.
