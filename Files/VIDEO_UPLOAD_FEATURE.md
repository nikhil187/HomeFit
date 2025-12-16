# Video Upload Feature - HomeFit

## 🎯 New Feature: Video Upload and Analysis

HomeFit now supports **uploading video files** for offline analysis! Users can upload their workout videos and get the same pose estimation, form feedback, and movement suggestions as the live camera mode.

## ✨ Features

### 1. **Dual Mode Interface**
- **Live Camera Mode**: Real-time analysis from webcam (existing feature)
- **Upload Video Mode**: Upload and analyze pre-recorded videos (new feature)

### 2. **Video Upload**
- Drag and drop or click to upload
- Supports multiple formats: MP4, AVI, MOV, MKV, FLV, WMV
- Maximum file size: 500MB
- Secure file handling with unique IDs

### 3. **Video Processing**
- Frame-by-frame pose estimation
- Same exercise tracking as live mode:
  - Squats
  - Push-ups
  - Hammer Curls
- Real-time movement suggestions overlay
- Visual indicators (angles, counters, gauges)

### 4. **Analysis Results**
- Total repetitions counted
- Video duration
- Frames processed
- Average joint angles
- Processed video with all overlays

## 📋 Implementation Details

### Backend (Flask)

#### New Routes:
1. **`/upload_video` (POST)**
   - Handles file upload
   - Validates file type and size
   - Stores file with unique ID
   - Returns file ID for processing

2. **`/process_video` (POST)**
   - Processes uploaded video
   - Applies pose estimation frame-by-frame
   - Generates processed video with overlays
   - Returns statistics and processed video URL

3. **`/processed/<filename>` (GET)**
   - Serves processed video files
   - Streams MP4 format

#### New Function:
- **`process_uploaded_video(video_path, exercise_type, file_id)`**
  - Opens video file
  - Processes each frame with pose estimation
  - Applies exercise tracking and feedback
  - Generates processed output video
  - Calculates statistics

### Frontend (HTML/CSS/JavaScript)

#### New UI Components:
1. **Mode Selection Tabs**
   - Toggle between Live Camera and Upload Video modes

2. **Upload Area**
   - Drag and drop zone
   - File input button
   - Visual feedback for drag-over state

3. **Exercise Selection**
   - Dropdown for exercise type selection

4. **Progress Indicator**
   - Progress bar during processing
   - Status messages

5. **Results Display**
   - Statistics cards
   - Processed video player
   - Download/view processed video

#### JavaScript Functions:
- Mode switching
- File upload handling
- Drag and drop support
- Progress tracking
- Results display

## 🗂️ File Structure

```
project/
├── uploads/          # Uploaded video files (gitignored)
├── processed/        # Processed video files (gitignored)
├── app.py           # Updated with upload routes
├── templates/
│   └── index.html   # Updated with upload UI
├── static/
│   ├── css/
│   │   └── style.css    # Updated with upload styles
│   └── js/
│       └── script.js    # Updated with upload logic
└── .gitignore       # Excludes uploads/ and processed/
```

## 🚀 Usage

### For Users:

1. **Switch to Upload Mode**
   - Click "Upload Video" tab

2. **Select Exercise Type**
   - Choose from dropdown: Squat, Push Up, or Hammer Curl

3. **Upload Video**
   - Click upload area or drag and drop video file
   - Wait for upload confirmation

4. **Analyze Video**
   - Click "Analyze Video" button
   - Watch progress bar
   - Wait for processing (depends on video length)

5. **View Results**
   - See statistics (reps, duration, etc.)
   - Watch processed video with overlays
   - Download if needed

### Technical Details:

- **Video Processing**: Frame-by-frame analysis using OpenCV
- **Pose Estimation**: Same MediaPipe pipeline as live mode
- **Output Format**: MP4 (H.264 codec)
- **File Storage**: Temporary storage in `uploads/` and `processed/` folders

## 🔧 Configuration

### File Size Limit:
```python
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB
```

### Allowed Formats:
```python
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv'}
```

### Storage Paths:
- Uploads: `uploads/` folder
- Processed: `processed/` folder

## 📊 Statistics Provided

After processing, users receive:
- **Total Reps**: Number of repetitions detected
- **Duration**: Video length in seconds
- **Frames Processed**: Total frames analyzed
- **Average Angle**: Mean joint angle (varies by exercise)

## 🎨 UI/UX Features

- **Responsive Design**: Works on desktop and mobile
- **Visual Feedback**: Progress indicators and status messages
- **Error Handling**: Clear error messages for invalid files
- **Drag & Drop**: Intuitive file upload
- **Results Display**: Clean, organized statistics and video player

## 🔒 Security

- File type validation
- File size limits
- Secure filename handling (prevents path traversal)
- Unique file IDs (prevents conflicts)
- Temporary storage (can be cleaned periodically)

## 🧹 Maintenance

### Cleanup Old Files:
Periodically clean `uploads/` and `processed/` folders to free up disk space:

```bash
# Remove files older than 7 days
find uploads/ -type f -mtime +7 -delete
find processed/ -type f -mtime +7 -delete
```

## 📝 Notes

- Processed videos include all visual overlays (skeleton, angles, suggestions)
- Processing time depends on video length and resolution
- Large videos may take several minutes to process
- Original uploaded files are preserved for reference

---

**Status**: ✅ Complete and Ready!
**Feature**: Video Upload and Analysis
**Date**: December 2024

