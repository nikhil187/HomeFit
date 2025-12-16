document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const exerciseOptions = document.querySelectorAll('.exercise-option');
    const startBtn = document.getElementById('start-btn');
    const stopBtn = document.getElementById('stop-btn');
    const setsInput = document.getElementById('sets');
    const repsInput = document.getElementById('reps');
    const currentExercise = document.getElementById('current-exercise');
    const currentSet = document.getElementById('current-set');
    const currentReps = document.getElementById('current-reps');
    
    // Variables
    let selectedExercise = null;
    let workoutRunning = false;
    let statusCheckInterval = null;
    
    // Select exercise
    exerciseOptions.forEach(option => {
        option.addEventListener('click', function() {
            // Remove selected class from all options
            exerciseOptions.forEach(opt => opt.classList.remove('selected'));
            
            // Add selected class to clicked option
            this.classList.add('selected');
            selectedExercise = this.getAttribute('data-exercise');
        });
    });
    
    // Start workout
    startBtn.addEventListener('click', function() {
        if (!selectedExercise) {
            alert('Please select an exercise first!');
            return;
        }
        
        const sets = parseInt(setsInput.value);
        const reps = parseInt(repsInput.value);
        
        if (isNaN(sets) || sets < 1 || isNaN(reps) || reps < 1) {
            alert('Please enter valid numbers for sets and repetitions.');
            return;
        }
        
        // Start the exercise via API
        fetch('/start_exercise', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                exercise_type: selectedExercise,
                sets: sets,
                reps: reps
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                workoutRunning = true;
                startBtn.disabled = true;
                stopBtn.disabled = false;
                
                // Update UI
                currentExercise.textContent = selectedExercise.replace('_', ' ').toUpperCase();
                currentSet.textContent = `1 / ${sets}`;
                currentReps.textContent = `0 / ${reps}`;
                
                // Start status polling
                statusCheckInterval = setInterval(checkStatus, 1000);
            } else {
                alert('Failed to start exercise: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while starting the exercise.');
        });
    });
    
    // Stop workout
    stopBtn.addEventListener('click', function() {
        fetch('/stop_exercise', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                resetWorkoutUI();
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
    
    // Function to check status
    function checkStatus() {
        fetch('/get_status')
        .then(response => response.json())
        .then(data => {
            if (!data.exercise_running && workoutRunning) {
                // Workout has ended
                resetWorkoutUI();
                return;
            }
            
            // Update status display
            currentSet.textContent = `${data.current_set} / ${data.total_sets}`;
            currentReps.textContent = `${data.current_reps} / ${data.rep_goal}`;
        })
        .catch(error => {
            console.error('Error checking status:', error);
        });
    }
    
    // Reset UI after workout ends
    function resetWorkoutUI() {
        workoutRunning = false;
        startBtn.disabled = false;
        stopBtn.disabled = true;
        
        if (statusCheckInterval) {
            clearInterval(statusCheckInterval);
            statusCheckInterval = null;
        }
        
        currentExercise.textContent = 'None';
        currentSet.textContent = '0 / 0';
        currentReps.textContent = '0 / 0';
    }
    
    // ========== Video Upload Mode ==========
    const modeTabs = document.querySelectorAll('.mode-tab');
    const liveMode = document.getElementById('live-mode');
    const uploadMode = document.getElementById('upload-mode');
    const videoFileInput = document.getElementById('video-file-input');
    const uploadArea = document.getElementById('upload-area');
    const analyzeBtn = document.getElementById('analyze-btn');
    const uploadProgress = document.getElementById('upload-progress');
    const progressFill = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');
    const analysisResults = document.getElementById('analysis-results');
    const resultsContent = document.getElementById('results-content');
    const processedVideo = document.getElementById('processed-video');
    const uploadExerciseType = document.getElementById('upload-exercise-type');
    
    let uploadedFileId = null;
    let uploadedFileName = null;
    
    // Mode switching
    modeTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const mode = this.getAttribute('data-mode');
            
            // Update active tab
            modeTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            // Show/hide mode content
            if (mode === 'live') {
                liveMode.classList.add('active');
                uploadMode.classList.remove('active');
            } else {
                liveMode.classList.remove('active');
                uploadMode.classList.add('active');
            }
        });
    });
    
    // File upload handling
    uploadArea.addEventListener('click', () => {
        videoFileInput.click();
    });
    
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('drag-over');
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('drag-over');
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    });
    
    videoFileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });
    
    function handleFileSelect(file) {
        if (!file.type.startsWith('video/')) {
            alert('Please select a valid video file.');
            return;
        }
        
        uploadedFileName = file.name;
        
        // Show file name
        const placeholder = uploadArea.querySelector('.upload-placeholder');
        placeholder.innerHTML = `
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
            </svg>
            <p><strong>${file.name}</strong></p>
            <p class="upload-hint">Click to change file</p>
        `;
        
        // Upload file
        const formData = new FormData();
        formData.append('video', file);
        formData.append('exercise_type', uploadExerciseType.value);
        
        fetch('/upload_video', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                uploadedFileId = data.file_id;
                analyzeBtn.disabled = false;
                analyzeBtn.textContent = 'Analyze Video';
            } else {
                alert('Upload failed: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Upload error:', error);
            alert('Error uploading file. Please try again.');
        });
    }
    
    // Analyze video
    analyzeBtn.addEventListener('click', function() {
        if (!uploadedFileId) {
            alert('Please upload a video first.');
            return;
        }
        
        analyzeBtn.disabled = true;
        analyzeBtn.textContent = 'Analyzing...';
        uploadProgress.style.display = 'block';
        progressFill.style.width = '0%';
        progressText.textContent = 'Starting video processing...';
        analysisResults.style.display = 'none';
        
        // Start processing (async)
        fetch('/process_video', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                file_id: uploadedFileId,
                exercise_type: uploadExerciseType.value
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Start polling for progress
                pollVideoProgress(uploadedFileId);
            } else {
                alert('Analysis failed: ' + (data.error || 'Unknown error'));
                analyzeBtn.disabled = false;
                analyzeBtn.textContent = 'Analyze Video';
                uploadProgress.style.display = 'none';
            }
        })
        .catch(error => {
            console.error('Analysis error:', error);
            alert('Error starting video processing. Please try again.');
            analyzeBtn.disabled = false;
            analyzeBtn.textContent = 'Analyze Video';
            uploadProgress.style.display = 'none';
        });
    });
    
    // Poll for video processing progress
    function pollVideoProgress(fileId) {
        const progressInterval = setInterval(() => {
            fetch(`/video_progress/${fileId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        if (data.status === 'complete') {
                            // Processing complete
                            clearInterval(progressInterval);
                            displayResults(data.result);
                            uploadProgress.style.display = 'none';
                        } else if (data.status === 'error') {
                            // Processing error
                            clearInterval(progressInterval);
                            alert('Analysis failed: ' + (data.error || 'Unknown error'));
                            analyzeBtn.disabled = false;
                            analyzeBtn.textContent = 'Analyze Video';
                            uploadProgress.style.display = 'none';
                        } else {
                            // Update progress
                            progressFill.style.width = data.progress + '%';
                            progressText.textContent = `Processing video... ${data.progress}%`;
                        }
                    } else {
                        clearInterval(progressInterval);
                        alert('Error checking progress: ' + (data.error || 'Unknown error'));
                        analyzeBtn.disabled = false;
                        analyzeBtn.textContent = 'Analyze Video';
                        uploadProgress.style.display = 'none';
                    }
                })
                .catch(error => {
                    console.error('Progress check error:', error);
                    clearInterval(progressInterval);
                    alert('Error checking progress. Please try again.');
                    analyzeBtn.disabled = false;
                    analyzeBtn.textContent = 'Analyze Video';
                    uploadProgress.style.display = 'none';
                });
        }, 500); // Poll every 500ms
    }
    
    function displayResults(data) {
        const stats = data.statistics;
        const exerciseName = uploadExerciseType.value.replace('_', ' ').toUpperCase();
        
        let statsHTML = `
            <div class="result-stats">
                <div class="stat-item">
                    <span class="stat-label">Exercise:</span>
                    <span class="stat-value">${exerciseName}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Total Reps:</span>
                    <span class="stat-value">${stats.total_reps}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Duration:</span>
                    <span class="stat-value">${stats.duration_seconds} seconds</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Frames Processed:</span>
                    <span class="stat-value">${stats.total_frames}</span>
                </div>
        `;
        
        // Add processing time if available
        if (stats.processing_time_seconds) {
            statsHTML += `
                <div class="stat-item">
                    <span class="stat-label">Processing Time:</span>
                    <span class="stat-value">${stats.processing_time_seconds} seconds</span>
                </div>
            `;
        }
        
        // Add processing FPS if available
        if (stats.processing_fps) {
            statsHTML += `
                <div class="stat-item">
                    <span class="stat-label">Processing Speed:</span>
                    <span class="stat-value">${stats.processing_fps} FPS</span>
                </div>
            `;
        }
        
        statsHTML += `</div>`;
        
        resultsContent.innerHTML = statsHTML;
        
        // Show processed video
        processedVideo.src = data.processed_video;
        processedVideo.style.display = 'block';
        analysisResults.style.display = 'block';
        
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = 'Analyze Video';
        progressFill.style.width = '100%';
        progressText.textContent = 'Analysis complete!';
    }
});
