"""
Movement Suggestions Module
Provides real-time coaching and form corrections based on pose analysis
"""

def get_squat_suggestions(landmarks, angle, stage, frame):
    """
    Analyze squat form and provide real-time suggestions
    
    Args:
        landmarks: MediaPipe pose landmarks
        angle: Current knee angle
        stage: Current stage of the squat
        frame: Video frame for coordinate calculations
    
    Returns:
        List of suggestion strings
    """
    suggestions = []
    
    # Get landmark coordinates
    hip_left = [int(landmarks[23].x * frame.shape[1]), int(landmarks[23].y * frame.shape[0])]
    knee_left = [int(landmarks[25].x * frame.shape[1]), int(landmarks[25].y * frame.shape[0])]
    ankle_left = [int(landmarks[27].x * frame.shape[1]), int(landmarks[27].y * frame.shape[0])]
    shoulder_left = [int(landmarks[11].x * frame.shape[1]), int(landmarks[11].y * frame.shape[0])]
    
    hip_right = [int(landmarks[24].x * frame.shape[1]), int(landmarks[24].y * frame.shape[0])]
    knee_right = [int(landmarks[26].x * frame.shape[1]), int(landmarks[26].y * frame.shape[0])]
    ankle_right = [int(landmarks[28].x * frame.shape[1]), int(landmarks[28].y * frame.shape[0])]
    shoulder_right = [int(landmarks[12].x * frame.shape[1]), int(landmarks[12].y * frame.shape[0])]
    
    # Calculate key measurements
    knee_forward_left = knee_left[0] - ankle_left[0]  # Positive if knee is forward
    knee_forward_right = knee_right[0] - ankle_right[0]
    
    # Check back alignment (shoulder-hip-knee alignment)
    back_angle_left = abs(shoulder_left[1] - hip_left[1]) / abs(hip_left[1] - knee_left[1]) if abs(hip_left[1] - knee_left[1]) > 0 else 0
    back_angle_right = abs(shoulder_right[1] - hip_right[1]) / abs(hip_right[1] - knee_right[1]) if abs(hip_right[1] - knee_right[1]) > 0 else 0
    
    # Stage-based suggestions
    if stage == "Starting Position":
        if angle > 170:
            suggestions.append("✓ Good starting position!")
        else:
            suggestions.append("→ Stand up straight to begin")
    
    elif stage == "Descent":
        # Depth check
        if angle > 120:
            suggestions.append("↓ Lower your hips more")
            suggestions.append("→ Aim for thighs parallel to ground")
        elif 90 < angle <= 120:
            suggestions.append("✓ Good depth, keep going!")
        
        # Knee position check
        if knee_forward_left > 50 or knee_forward_right > 50:
            suggestions.append("⚠ Keep knees behind toes")
            suggestions.append("→ Push hips back more")
        elif knee_forward_left < -30 or knee_forward_right < -30:
            suggestions.append("→ Shift weight forward slightly")
        
        # Back alignment check
        if back_angle_left > 0.8 or back_angle_right > 0.8:
            suggestions.append("⚠ Keep your back straight")
            suggestions.append("→ Chest up, core engaged")
    
    elif stage == "Ascent":
        if angle < 90:
            suggestions.append("↑ Push through your heels")
            suggestions.append("→ Drive hips up and forward")
        else:
            suggestions.append("✓ Great form! Keep pushing up")
    
    # General form tips
    if len(suggestions) == 0:
        suggestions.append("→ Keep your core tight")
        suggestions.append("→ Maintain steady breathing")
    
    return suggestions


def get_push_up_suggestions(landmarks, angle, stage, frame):
    """
    Analyze push-up form and provide real-time suggestions
    
    Args:
        landmarks: MediaPipe pose landmarks
        angle: Current elbow angle
        stage: Current stage of the push-up
        frame: Video frame for coordinate calculations
    
    Returns:
        List of suggestion strings
    """
    suggestions = []
    
    # Get landmark coordinates
    shoulder_left = [int(landmarks[11].x * frame.shape[1]), int(landmarks[11].y * frame.shape[0])]
    elbow_left = [int(landmarks[13].x * frame.shape[1]), int(landmarks[13].y * frame.shape[0])]
    wrist_left = [int(landmarks[15].x * frame.shape[1]), int(landmarks[15].y * frame.shape[0])]
    hip_left = [int(landmarks[23].x * frame.shape[1]), int(landmarks[23].y * frame.shape[0])]
    ankle_left = [int(landmarks[27].x * frame.shape[1]), int(landmarks[27].y * frame.shape[0])]
    
    shoulder_right = [int(landmarks[12].x * frame.shape[1]), int(landmarks[12].y * frame.shape[0])]
    elbow_right = [int(landmarks[14].x * frame.shape[1]), int(landmarks[14].y * frame.shape[0])]
    hip_right = [int(landmarks[24].x * frame.shape[1]), int(landmarks[24].y * frame.shape[0])]
    
    # Calculate body alignment
    body_alignment = abs((shoulder_left[1] + shoulder_right[1])/2 - (hip_left[1] + hip_right[1])/2)
    shoulder_hip_diff = abs(shoulder_left[1] - hip_left[1])
    
    # Check if body is sagging (hips too low)
    hip_too_low = (hip_left[1] + hip_right[1])/2 > (shoulder_left[1] + shoulder_right[1])/2 + 30
    
    # Stage-based suggestions
    if stage == "Starting position":
        if angle > 150:
            suggestions.append("✓ Good starting position!")
            if hip_too_low:
                suggestions.append("⚠ Keep your body straight")
                suggestions.append("→ Engage your core")
        else:
            suggestions.append("→ Extend your arms fully")
    
    elif stage == "Descent":
        # Depth check
        if angle > 100:
            suggestions.append("↓ Lower your body more")
            suggestions.append("→ Aim for 90° elbow angle")
        elif 70 < angle <= 100:
            suggestions.append("✓ Good depth, almost there!")
        elif angle <= 70:
            suggestions.append("✓ Perfect depth!")
        
        # Body alignment check
        if hip_too_low:
            suggestions.append("⚠ Keep your body in a straight line")
            suggestions.append("→ Tighten your core")
        elif shoulder_hip_diff < 20:
            suggestions.append("✓ Great body alignment!")
    
    elif stage == "Ascent":
        if angle < 70:
            suggestions.append("↑ Push up with control")
            suggestions.append("→ Drive through your palms")
        elif angle < 100:
            suggestions.append("✓ Keep pushing, you're doing great!")
        else:
            suggestions.append("→ Fully extend your arms")
    
    # General form tips
    if len(suggestions) == 0:
        suggestions.append("→ Keep your head in line with your body")
        suggestions.append("→ Breathe out on the way up")
    
    return suggestions


def get_hammer_curl_suggestions(landmarks, angle_counter, angle_alignment, stage, side, frame):
    """
    Analyze hammer curl form and provide real-time suggestions
    
    Args:
        landmarks: MediaPipe pose landmarks
        angle_counter: Elbow flexion angle for counting
        angle_alignment: Shoulder-elbow-hip alignment angle
        stage: Current stage (Flex, Up, Down)
        side: "left" or "right"
        frame: Video frame for coordinate calculations
    
    Returns:
        List of suggestion strings
    """
    suggestions = []
    
    # Select landmarks based on side
    if side == "right":
        shoulder = [int(landmarks[12].x * frame.shape[1]), int(landmarks[12].y * frame.shape[0])]
        elbow = [int(landmarks[14].x * frame.shape[1]), int(landmarks[14].y * frame.shape[0])]
        wrist = [int(landmarks[16].x * frame.shape[1]), int(landmarks[16].y * frame.shape[0])]
        hip = [int(landmarks[24].x * frame.shape[1]), int(landmarks[24].y * frame.shape[0])]
    else:  # left
        shoulder = [int(landmarks[11].x * frame.shape[1]), int(landmarks[11].y * frame.shape[0])]
        elbow = [int(landmarks[13].x * frame.shape[1]), int(landmarks[13].y * frame.shape[0])]
        wrist = [int(landmarks[15].x * frame.shape[1]), int(landmarks[15].y * frame.shape[0])]
        hip = [int(landmarks[23].x * frame.shape[1]), int(landmarks[23].y * frame.shape[0])]
    
    # Check arm position relative to body
    arm_away_from_body = abs(angle_alignment) > 30
    
    # Stage-based suggestions
    if stage == "Flex" or stage is None:
        if angle_counter > 150:
            suggestions.append(f"✓ {side.title()} arm ready!")
        else:
            suggestions.append(f"→ Extend your {side} arm fully")
    
    elif stage == "Up":
        # Check if curling too fast or not enough
        if angle_counter > 100:
            suggestions.append(f"↑ Curl your {side} arm more")
            suggestions.append("→ Bring weight to shoulder")
        elif 35 < angle_counter <= 100:
            suggestions.append(f"✓ Good {side} arm position!")
        
        # Alignment check
        if arm_away_from_body:
            suggestions.append(f"⚠ Keep your {side} arm close to body")
            suggestions.append("→ Don't swing your arm")
        else:
            suggestions.append(f"✓ Great {side} arm control!")
    
    elif stage == "Down":
        if angle_counter < 35:
            suggestions.append(f"↓ Lower your {side} arm slowly")
            suggestions.append("→ Control the negative movement")
        else:
            suggestions.append(f"→ Fully extend your {side} arm")
    
    # General form tips
    if len(suggestions) == 0:
        suggestions.append(f"→ Keep your {side} elbow stationary")
        suggestions.append("→ Focus on the muscle contraction")
    
    return suggestions
