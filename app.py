from flask import Flask, render_template, Response, request, jsonify, session, redirect, url_for, send_file
import cv2
import threading
import time
import sys
import traceback
import logging
import os
import uuid
import subprocess
import shutil
from werkzeug.utils import secure_filename
import numpy as np

"""
HomeFit - AI-Powered Fitness Trainer
Main Flask application for real-time exercise tracking
"""

logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)
try:
    from pose_estimation.estimation import PoseEstimator
    from exercises.squat import Squat
    from exercises.hammer_curl import HammerCurl
    from exercises.push_up import PushUp
    from feedback.information import get_exercise_info
    from feedback.layout import layout_indicators
    from utils.draw_text_with_background import draw_text_with_background
    logger.info("Successfully imported pose estimation modules")
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    traceback.print_exc()
    sys.exit(1)

# Try to import WorkoutLogger with fallback
try:
    from db.workout_logger import WorkoutLogger
    workout_logger = WorkoutLogger()
    logger.info("Successfully initialized workout logger")
except ImportError:
    logger.warning("WorkoutLogger import failed, creating dummy class")
    
    class DummyWorkoutLogger:
        def __init__(self):
            pass
        def log_workout(self, *args, **kwargs):
            return {}
        def get_recent_workouts(self, *args, **kwargs):
            return []
        def get_weekly_stats(self, *args, **kwargs):
            return {}
        def get_exercise_distribution(self, *args, **kwargs):
            return {}
        def get_user_stats(self, *args, **kwargs):
            return {'total_workouts': 0, 'total_exercises': 0, 'streak_days': 0}
    
    workout_logger = DummyWorkoutLogger()

logger.info("Setting up Flask application")
app = Flask(__name__)
app.secret_key = 'homefit_secret_key'

UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv'}

# Create upload and processed directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Global variables
camera = None
output_frame = None
lock = threading.Lock()
exercise_running = False
current_exercise = None
current_exercise_data = None
exercise_counter = 0
exercise_goal = 0
sets_completed = 0
sets_goal = 0
workout_start_time = None

video_processing_progress = {}

def initialize_camera():
    global camera
    if camera is None:
        camera = cv2.VideoCapture(0)
    return camera

def release_camera():
    global camera
    if camera is not None:
        camera.release()
        camera = None

def generate_frames():
    global output_frame, lock, exercise_running, current_exercise, current_exercise_data
    global exercise_counter, exercise_goal, sets_completed, sets_goal
    
    pose_estimator = PoseEstimator()
    
    while True:
        if camera is None:
            continue
            
        success, frame = camera.read()
        if not success:
            continue
        
        if exercise_running and current_exercise:
            results = pose_estimator.estimate_pose(frame, current_exercise_data['type'])
            
            if results.pose_landmarks:
                if current_exercise_data['type'] == "squat":
                    counter, angle, stage, suggestions = current_exercise.track_squat(results.pose_landmarks.landmark, frame)
                    layout_indicators(frame, current_exercise_data['type'], (counter, angle, stage, suggestions))
                    exercise_counter = counter
                    
                elif current_exercise_data['type'] == "push_up":
                    counter, angle, stage, suggestions = current_exercise.track_push_up(results.pose_landmarks.landmark, frame)
                    layout_indicators(frame, current_exercise_data['type'], (counter, angle, stage, suggestions))
                    exercise_counter = counter
                    
                elif current_exercise_data['type'] == "hammer_curl":
                    (counter_right, angle_right, counter_left, angle_left,
                     warning_message_right, warning_message_left, progress_right, 
                     progress_left, stage_right, stage_left, suggestions_right, suggestions_left) = current_exercise.track_hammer_curl(
                        results.pose_landmarks.landmark, frame)
                    layout_indicators(frame, current_exercise_data['type'], 
                                     (counter_right, angle_right, counter_left, angle_left,
                                      warning_message_right, warning_message_left, 
                                      progress_right, progress_left, stage_right, stage_left,
                                      suggestions_right, suggestions_left))
                    exercise_counter = max(counter_right, counter_left)
                
                # Display exercise information
                exercise_info = get_exercise_info(current_exercise_data['type'])
                draw_text_with_background(frame, f"Exercise: {exercise_info.get('name', 'N/A')}", (40, 50),
                                         cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), (118, 29, 14), 1)
                draw_text_with_background(frame, f"Reps Goal: {exercise_goal}", (40, 80),
                                         cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), (118, 29, 14), 1)
                draw_text_with_background(frame, f"Sets Goal: {sets_goal}", (40, 110),
                                         cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), (118, 29, 14), 1)
                draw_text_with_background(frame, f"Current Set: {sets_completed + 1}", (40, 140),
                                         cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), (118, 29, 14), 1)
                
                # Check if rep goal is reached for current set
                if exercise_counter >= exercise_goal:
                    sets_completed += 1
                    exercise_counter = 0
                    # Reset exercise counter in the appropriate exercise object
                    if current_exercise_data['type'] == "squat" or current_exercise_data['type'] == "push_up":
                        current_exercise.counter = 0
                    elif current_exercise_data['type'] == "hammer_curl":
                        current_exercise.counter_right = 0
                        current_exercise.counter_left = 0
                    
                    # Check if all sets are completed
                    if sets_completed >= sets_goal:
                        exercise_running = False
                        draw_text_with_background(frame, "WORKOUT COMPLETE!", (frame.shape[1]//2 - 150, frame.shape[0]//2),
                                                cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 255, 255), (0, 200, 0), 2)
                    else:
                        draw_text_with_background(frame, f"SET {sets_completed} COMPLETE! Rest for 30 sec", 
                                                (frame.shape[1]//2 - 200, frame.shape[0]//2),
                                                cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), (0, 0, 200), 2)
        else:
            cv2.putText(frame, "Select an exercise to begin", (frame.shape[1]//2 - 150, frame.shape[0]//2),
                       cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)
                
        with lock:
            output_frame = frame.copy()
            
        ret, buffer = cv2.imencode('.jpg', output_frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    logger.info("Rendering index page")
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering index: {e}")
        return f"Error rendering template: {str(e)}", 500

@app.route('/dashboard')
def dashboard():
    logger.info("Rendering dashboard page")
    try:
        recent_workouts = workout_logger.get_recent_workouts(5)
        weekly_stats = workout_logger.get_weekly_stats()
        exercise_distribution = workout_logger.get_exercise_distribution()
        user_stats = workout_logger.get_user_stats()
        
        formatted_workouts = []
        for workout in recent_workouts:
            formatted_workouts.append({
                'date': workout['date'],
                'exercise': workout['exercise_type'].replace('_', ' ').title(),
                'sets': workout['sets'],
                'reps': workout['reps'],
                'duration': f"{workout['duration_seconds'] // 60}:{workout['duration_seconds'] % 60:02d}"
            })
        
        # Calculate total workouts this week
        weekly_workout_count = sum(day['workout_count'] for day in weekly_stats.values())
        
        return render_template('dashboard.html',
                              recent_workouts=formatted_workouts,
                              weekly_workouts=weekly_workout_count,
                              total_workouts=user_stats['total_workouts'],
                              total_exercises=user_stats['total_exercises'],
                              streak_days=user_stats['streak_days'])
    except Exception as e:
        logger.error(f"Error in dashboard: {e}")
        traceback.print_exc()
        return f"Error loading dashboard: {str(e)}", 500

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_exercise', methods=['POST'])
def start_exercise():
    global exercise_running, current_exercise, current_exercise_data
    global exercise_counter, exercise_goal, sets_completed, sets_goal
    global workout_start_time
    
    data = request.json
    exercise_type = data.get('exercise_type')
    sets_goal = int(data.get('sets', 3))
    exercise_goal = int(data.get('reps', 10))
    
    initialize_camera()
    
    exercise_counter = 0
    sets_completed = 0
    workout_start_time = time.time()
    
    # Initialize the appropriate exercise class
    if exercise_type == "squat":
        current_exercise = Squat()
    elif exercise_type == "push_up":
        current_exercise = PushUp()
    elif exercise_type == "hammer_curl":
        current_exercise = HammerCurl()
    else:
        return jsonify({'success': False, 'error': 'Invalid exercise type'})
    
    # Store exercise data
    current_exercise_data = {
        'type': exercise_type,
        'sets': sets_goal,
        'reps': exercise_goal
    }
    
    exercise_running = True
    
    return jsonify({'success': True})

@app.route('/stop_exercise', methods=['POST'])
def stop_exercise():
    global exercise_running, current_exercise_data, workout_start_time
    global exercise_counter, exercise_goal, sets_completed, sets_goal
    
    if exercise_running and current_exercise_data:
        duration = int(time.time() - workout_start_time) if workout_start_time else 0
        
        workout_logger.log_workout(
            exercise_type=current_exercise_data['type'],
            sets=sets_completed + (1 if exercise_counter > 0 else 0),
            reps=exercise_goal,
            duration_seconds=duration
        )
    
    exercise_running = False
    return jsonify({'success': True})

@app.route('/get_status', methods=['GET'])
def get_status():
    global exercise_counter, sets_completed, exercise_goal, sets_goal, exercise_running
    
    return jsonify({
        'exercise_running': exercise_running,
        'current_reps': exercise_counter,
        'current_set': sets_completed + 1 if exercise_running else 0,
        'total_sets': sets_goal,
        'rep_goal': exercise_goal
    })

@app.route('/profile')
def profile():
    return "Profile page - Coming soon!"

@app.route('/upload_video', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'success': False, 'error': 'No video file provided'}), 400
    
    file = request.files['video']
    exercise_type = request.form.get('exercise_type', 'squat')
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())
        file_extension = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{unique_id}.{file_extension}"
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        return jsonify({
            'success': True,
            'file_id': unique_id,
            'filename': filename,
            'exercise_type': exercise_type
        })
    
    return jsonify({'success': False, 'error': 'Invalid file type'}), 400

@app.route('/process_video', methods=['POST'])
def process_video():
    data = request.json
    file_id = data.get('file_id')
    exercise_type = data.get('exercise_type', 'squat')
    
    if not file_id:
        return jsonify({'success': False, 'error': 'No file ID provided'}), 400
    
    uploaded_file = None
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if filename.startswith(file_id):
            uploaded_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            break
    
    if not uploaded_file or not os.path.exists(uploaded_file):
        return jsonify({'success': False, 'error': 'File not found'}), 404
    
    video_processing_progress[file_id] = {
        'progress': 0,
        'status': 'processing',
        'result': None,
        'error': None
    }
    
    def process_in_background():
        try:
            def update_progress(current_frame, total_frames):
                if total_frames > 0:
                    progress = int((current_frame / total_frames) * 100)
                    video_processing_progress[file_id]['progress'] = progress
            
            result = process_uploaded_video(uploaded_file, exercise_type, file_id, update_progress)
            video_processing_progress[file_id]['status'] = 'complete'
            video_processing_progress[file_id]['result'] = result
            video_processing_progress[file_id]['progress'] = 100
        except Exception as e:
            logger.error(f"Error processing video: {e}")
            traceback.print_exc()
            video_processing_progress[file_id]['status'] = 'error'
            video_processing_progress[file_id]['error'] = str(e)
    
    thread = threading.Thread(target=process_in_background)
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True, 'file_id': file_id, 'message': 'Processing started'})

@app.route('/video_progress/<file_id>', methods=['GET'])
def video_progress(file_id):
    if file_id not in video_processing_progress:
        return jsonify({'success': False, 'error': 'File ID not found'}), 404
    
    progress_data = video_processing_progress[file_id]
    
    if progress_data['status'] == 'complete':
        return jsonify({
            'success': True,
            'status': 'complete',
            'progress': 100,
            'result': progress_data['result']
        })
    elif progress_data['status'] == 'error':
        return jsonify({
            'success': False,
            'status': 'error',
            'error': progress_data['error']
        })
    else:
        return jsonify({
            'success': True,
            'status': 'processing',
            'progress': progress_data['progress']
        })

def process_uploaded_video(video_path, exercise_type, file_id, progress_callback=None):
    logger.info(f"Starting video processing for {exercise_type}")
    start_time = time.time()
    
    pose_estimator = PoseEstimator(
        static_image_mode=False,
        model_complexity=1,
        enable_segmentation=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    if exercise_type == "squat":
        exercise = Squat()
    elif exercise_type == "push_up":
        exercise = PushUp(use_time_throttle=False)
    elif exercise_type == "hammer_curl":
        exercise = HammerCurl()
    else:
        raise ValueError(f"Invalid exercise type: {exercise_type}")
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Could not open video file")
    
    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    scale_factor = 1.0
    if width > 1280:
        scale_factor = 1280.0 / width
        width = int(width * scale_factor)
        height = int(height * scale_factor)
        logger.info(f"Downscaling video to {width}x{height} for faster processing")
    
    logger.info(f"Video properties: {total_frames} frames, {fps} FPS, {width}x{height}")
    
    output_filename = f"{file_id}_processed.mp4"
    output_path = os.path.join(app.config['PROCESSED_FOLDER'], output_filename)
    
    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    if not out.isOpened():
        logger.warning("H.264 codec not available, using mp4v")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    total_reps = 0
    frame_count = 0
    angles_history = []
    last_log_time = time.time()
    frames_with_landmarks = 0
    frames_without_landmarks = 0
    
    logger.info(f"Processing {total_frames} frames...")
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        if scale_factor < 1.0:
            frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_LINEAR)
        
        results = pose_estimator.estimate_pose(frame, exercise_type)
        
        if results.pose_landmarks:
            frames_with_landmarks += 1
            if exercise_type == "squat":
                counter, angle, stage, suggestions = exercise.track_squat(
                    results.pose_landmarks.landmark, frame)
                layout_indicators(frame, exercise_type, (counter, angle, stage, suggestions))
                total_reps = counter
                angles_history.append(angle)
                
            elif exercise_type == "push_up":
                counter, angle, stage, suggestions = exercise.track_push_up(
                    results.pose_landmarks.landmark, frame)
                layout_indicators(frame, exercise_type, (counter, angle, stage, suggestions))
                total_reps = counter
                angles_history.append(angle)
                
            elif exercise_type == "hammer_curl":
                (counter_right, angle_right, counter_left, angle_left,
                 warning_message_right, warning_message_left, progress_right, 
                 progress_left, stage_right, stage_left, suggestions_right, suggestions_left) = exercise.track_hammer_curl(
                    results.pose_landmarks.landmark, frame)
                layout_indicators(frame, exercise_type, 
                                 (counter_right, angle_right, counter_left, angle_left,
                                  warning_message_right, warning_message_left, 
                                  progress_right, progress_left, stage_right, stage_left,
                                  suggestions_right, suggestions_left))
                total_reps = max(counter_right, counter_left)
                angles_history.append((angle_right, angle_left))
        
        else:
            frames_without_landmarks += 1
        
        out.write(frame)
        
        if progress_callback and frame_count % 10 == 0:
            progress_callback(frame_count, total_frames)
        
        current_time = time.time()
        if current_time - last_log_time >= 5.0:
            progress = (frame_count / total_frames) * 100 if total_frames > 0 else 0
            fps_processing = frame_count / (current_time - start_time)
            logger.info(f"Progress: {progress:.1f}% ({frame_count}/{total_frames} frames, {fps_processing:.1f} FPS)")
            logger.info(f"Landmarks detected: {frames_with_landmarks}/{frame_count} frames, Reps: {total_reps}")
            last_log_time = current_time
    
    cap.release()
    out.release()
    
    logger.info(f"Video writing complete. Checking output file...")
    
    if not os.path.exists(output_path):
        raise ValueError("Output video file was not created")
    
    output_size = os.path.getsize(output_path)
    logger.info(f"Output video size: {output_size / 1024 / 1024:.2f} MB")
    
    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path:
        logger.info("FFmpeg found. Re-encoding for browser compatibility...")
        temp_output = output_path.replace('.mp4', '_temp.mp4')
        os.rename(output_path, temp_output)
        
        try:
            cmd = [
                ffmpeg_path,
                '-i', temp_output,
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-crf', '23',
                '-pix_fmt', 'yuv420p',
                '-movflags', '+faststart',
                '-y',
                output_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info("FFmpeg re-encoding successful")
                os.remove(temp_output)
            else:
                logger.warning(f"FFmpeg re-encoding failed: {result.stderr}")
                os.rename(temp_output, output_path)
        except Exception as e:
            logger.warning(f"FFmpeg re-encoding error: {e}")
            if os.path.exists(temp_output):
                os.rename(temp_output, output_path)
    else:
        logger.warning("FFmpeg not found. Video may not play in all browsers.")
    
    if progress_callback:
        progress_callback(total_frames, total_frames)
    
    if exercise_type == "hammer_curl" and angles_history:
        if isinstance(angles_history[0], tuple):
            avg_angle_right = sum(a[0] for a in angles_history) / len(angles_history)
            avg_angle_left = sum(a[1] for a in angles_history) / len(angles_history)
            avg_angle = (round(avg_angle_right, 2), round(avg_angle_left, 2))
        else:
            avg_angle = round(sum(angles_history) / len(angles_history), 2) if angles_history else 0
    else:
        avg_angle = round(sum(angles_history) / len(angles_history), 2) if angles_history else 0
    
    duration = frame_count / fps if fps > 0 else 0
    processing_time = time.time() - start_time
    processing_fps = frame_count / processing_time if processing_time > 0 else 0
    
    logger.info(f"Video processing completed in {processing_time:.2f} seconds")
    logger.info(f"Processing speed: {processing_fps:.1f} FPS (video: {fps} FPS)")
    logger.info(f"Pose detection: {frames_with_landmarks}/{frame_count} frames ({100*frames_with_landmarks/frame_count:.1f}%)")
    logger.info(f"Total reps counted: {total_reps}")
    
    return {
        'success': True,
        'processed_video': f'/processed/{output_filename}',
        'statistics': {
            'total_reps': total_reps,
            'duration_seconds': round(duration, 2),
            'total_frames': frame_count,
            'average_angle': round(avg_angle, 2) if isinstance(avg_angle, (int, float)) else avg_angle,
            'processing_time_seconds': round(processing_time, 2),
            'processing_fps': round(processing_fps, 1)
        }
    }

@app.route('/processed/<filename>')
def processed_video(filename):
    filepath = os.path.join(app.config['PROCESSED_FOLDER'], filename)
    
    if not os.path.exists(filepath):
        logger.error(f"Processed video not found: {filepath}")
        return jsonify({'error': 'Video not found'}), 404
    
    logger.info(f"Serving processed video: {filepath} ({os.path.getsize(filepath) / 1024 / 1024:.2f} MB)")
    
    response = send_file(
        filepath, 
        mimetype='video/mp4',
        as_attachment=False
    )
    response.headers['Accept-Ranges'] = 'bytes'
    response.headers['Cache-Control'] = 'no-cache'
    return response

@app.route('/debug/video/<file_id>')
def debug_video(file_id):
    uploaded_file = None
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if filename.startswith(file_id):
            uploaded_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            break
    
    processed_file = os.path.join(app.config['PROCESSED_FOLDER'], f"{file_id}_processed.mp4")
    
    return jsonify({
        'file_id': file_id,
        'uploaded_file': {
            'exists': uploaded_file is not None and os.path.exists(uploaded_file) if uploaded_file else False,
            'path': uploaded_file,
            'size_mb': os.path.getsize(uploaded_file) / 1024 / 1024 if uploaded_file and os.path.exists(uploaded_file) else 0
        },
        'processed_file': {
            'exists': os.path.exists(processed_file),
            'path': processed_file,
            'size_mb': os.path.getsize(processed_file) / 1024 / 1024 if os.path.exists(processed_file) else 0
        },
        'progress': video_processing_progress.get(file_id, {})
    })

if __name__ == '__main__':
    try:
        logger.info("Starting the Flask application on http://127.0.0.1:5000")
        print("Starting HomeFit app, please wait...")
        print("Open http://127.0.0.1:5000 in your web browser when the server starts")
        app.run(debug=True)
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        traceback.print_exc()
