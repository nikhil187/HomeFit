# HomeFit - AI-Powered Fitness Trainer

A real-time exercise tracking system using computer vision that provides form feedback and repetition counting for squats, push-ups, and hammer curls.

## Features

- Real-time pose estimation using MediaPipe
- Exercise tracking: Squats, Push-ups, Hammer Curls
- Automatic repetition counting
- Real-time form analysis and feedback
- Web-based interface (no installation needed)
- Video upload support for analysis

## Installation

1. Clone the repository:
```bash
git clone https://github.com/nikhil187/HomeFit.git
cd fitness-trainer-pose-estimation
```

2. Install dependencies:
```bash
pip install flask opencv-python mediapipe numpy werkzeug
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to:
```
http://127.0.0.1:5000
```

## Usage

### Live Camera Mode
1. Select an exercise type (Squat, Push-up, or Hammer Curl)
2. Set your desired repetitions and sets
3. Click "Start Workout"
4. Position yourself in front of the camera
5. Perform the exercise and follow on-screen feedback

### Video Upload Mode
1. Click "Upload Video" tab
2. Select a video file from your computer
3. Choose the exercise type
4. Click "Process Video"
5. Download the processed video with pose detection and feedback

## Test Video

A sample test video is included in the `data/` folder: `dumbel-workout.mp4`

## Technologies

- **Flask** - Web framework
- **OpenCV** - Computer vision processing
- **MediaPipe** - Pose estimation
- **Python** - Backend logic

## Project Structure

```
fitness-trainer-pose-estimation/
├── app.py                 # Main Flask application
├── main.py               # Standalone video processing
├── exercises/            # Exercise tracking classes
├── pose_estimation/      # MediaPipe integration
├── feedback/            # Form analysis and suggestions
├── templates/           # HTML templates
├── static/              # CSS, JavaScript, images
└── data/                # Test videos
```

## How It Works

1. **Pose Detection**: MediaPipe detects 33 body landmarks in real-time
2. **Angle Calculation**: Geometric calculations determine joint angles
3. **State Machine**: Tracks exercise phases (Starting → Descent → Ascent)
4. **Rep Counting**: Counts repetitions when full range of motion is completed
5. **Form Feedback**: Provides real-time suggestions based on biomechanics research


