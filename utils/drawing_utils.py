import cv2
import numpy as np
import math
from utils.draw_text_with_background import draw_text_with_background

def display_counter(frame, counter, position=(40, 240), color=(0, 0, 0), background_color=(192, 192, 192)):
    """Display the repetition counter."""
    text = f"Count: {counter}"
    draw_text_with_background(frame, text, position, 
                             cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, background_color, 1)

def display_stage(frame, stage, label="Stage", position=(40, 270), color=(0, 0, 0), background_color=(192, 192, 192)):
    """Display the current exercise stage."""
    text = f"{label}: {stage}"
    draw_text_with_background(frame, text, position, 
                             cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, background_color, 1)

def draw_progress_bar(frame, exercise, value, position, size=(200, 20), color=(0, 255, 0), background_color=(255, 255, 255)):
    """Draw a progress bar for tracking exercise repetitions."""
    x, y = position
    width, height = size
    
    # Get max value for the exercise type
    max_value = 10  # Default
    if exercise == "squat":
        max_value = 15
    elif exercise == "push_up":
        max_value = 10
    elif exercise == "hammer_curl":
        max_value = 12
    
    # Calculate fill width
    fill_width = int((value / max_value) * width)
    fill_width = min(fill_width, width)  # Ensure it doesn't exceed max width
    
    # Draw background
    cv2.rectangle(frame, (x, y), (x + width, y + height), background_color, -1)
    cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 0, 0), 1)
    
    # Draw fill
    if fill_width > 0:
        cv2.rectangle(frame, (x, y), (x + fill_width, y + height), color, -1)
    
    # Draw text
    text = f"{value}/{max_value}"
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
    text_x = x + (width - text_size[0]) // 2
    text_y = y + (height + text_size[1]) // 2
    cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    
    # Draw label above the progress bar
    label = f"{exercise.replace('_', ' ').title()} Progress"
    draw_text_with_background(frame, label, (x, y - 10), 
                             cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), (118, 29, 14), 1)

def draw_gauge_meter(frame, angle, text, position, radius=50, color=(0, 0, 255)):
    """Draw a gauge meter visualization showing the angle."""
    x, y = position
    start_angle = 180
    end_angle = 0
    
    # Draw outer circle
    cv2.circle(frame, (x, y), radius, (200, 200, 200), 2)
    
    # Calculate the angle position on the gauge
    gauge_angle = start_angle - (angle * (start_angle - end_angle) / 180)
    gauge_angle = max(min(gauge_angle, start_angle), end_angle) # Constrain angle
    
    # Convert to radians
    gauge_angle_rad = math.radians(gauge_angle)
    
    # Calculate point on circle
    gauge_x = int(x + radius * math.cos(gauge_angle_rad))
    gauge_y = int(y - radius * math.sin(gauge_angle_rad))
    
    # Draw line from center to angle point
    cv2.line(frame, (x, y), (gauge_x, gauge_y), color, 2)
    
    # Draw center circle
    cv2.circle(frame, (x, y), 5, color, -1)
    
    # Draw text
    cv2.putText(frame, f"{int(angle)}°", (x - 20, y + radius + 20), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    # Draw title
    cv2.putText(frame, text, (x - radius, y - radius - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

def display_suggestions(frame, suggestions, position=None, max_suggestions=3):
    """
    Display movement suggestions on the frame - optimized for long-distance visibility.
    Positioned at top center of screen with large, high-contrast text.
    
    Args:
        frame: Video frame
        suggestions: List of suggestion strings
        position: Starting position (x, y) - if None, centers at top
        max_suggestions: Maximum number of suggestions to display
    """
    if not suggestions:
        return
    
    # Limit number of suggestions
    suggestions_to_show = suggestions[:max_suggestions]
    
    # Get frame dimensions
    frame_height, frame_width = frame.shape[:2]
    
    # Position at top center if position not specified
    if position is None:
        # Center horizontally, position near top
        start_y = 60
    else:
        start_y = position[1] if len(position) > 1 else 60
    
    # Large font settings for distance visibility
    font_scale = 1.2  # Much larger font
    thickness = 3  # Thicker text for visibility
    line_height = 55  # More spacing between lines
    
    # Calculate panel width based on longest suggestion
    max_text_width = 0
    for suggestion in suggestions_to_show:
        (text_width, _), _ = cv2.getTextSize(suggestion, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
        max_text_width = max(max_text_width, text_width)
    
    panel_width = max_text_width + 80  # Add padding
    panel_height = len(suggestions_to_show) * line_height + 50
    
    # Center the panel horizontally
    panel_x = (frame_width - panel_width) // 2
    panel_y = start_y
    
    # Draw semi-transparent dark background for better visibility
    # Create overlay
    overlay = frame.copy()
    cv2.rectangle(overlay, (panel_x - 20, panel_y - 40), 
                  (panel_x + panel_width + 20, panel_y + panel_height), 
                  (0, 0, 0), -1)  # Black background
    # Blend overlay with original frame
    cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)
    
    # Draw bright border for visibility
    cv2.rectangle(frame, (panel_x - 20, panel_y - 40), 
                  (panel_x + panel_width + 20, panel_y + panel_height), 
                  (255, 255, 255), 5)  # Thick white border for visibility
    
    # Draw title at top
    title_text = "MOVEMENT GUIDANCE"
    title_font_scale = 1.0
    title_thickness = 2
    (title_width, title_height), _ = cv2.getTextSize(title_text, cv2.FONT_HERSHEY_DUPLEX, title_font_scale, title_thickness)
    title_x = panel_x + (panel_width - title_width) // 2
    title_y = panel_y - 10
    
    cv2.putText(frame, title_text, (title_x, title_y), 
                cv2.FONT_HERSHEY_DUPLEX, title_font_scale, (255, 255, 255), title_thickness)
    
    # Draw each suggestion - centered
    for i, suggestion in enumerate(suggestions_to_show):
        y_pos = panel_y + 30 + (i + 1) * line_height
        
        # Determine color based on suggestion type - high contrast colors
        if suggestion.startswith("✓"):
            text_color = (0, 255, 0)  # Bright green for positive feedback
        elif suggestion.startswith("⚠"):
            text_color = (0, 165, 255)  # Bright orange for warnings
        elif suggestion.startswith("↓"):
            text_color = (255, 255, 0)  # Bright yellow for descent cues
        elif suggestion.startswith("↑"):
            text_color = (255, 255, 0)  # Bright yellow for ascent cues
        else:
            text_color = (135, 206, 250)  # Light blue for tips
        
        # Calculate text width for centering
        (text_width, text_height), _ = cv2.getTextSize(suggestion, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
        text_x = panel_x + (panel_width - text_width) // 2
        
        # Draw text with shadow for better visibility
        # Shadow
        cv2.putText(frame, suggestion, (text_x + 2, y_pos + 2), 
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), thickness + 1)
        # Main text
        cv2.putText(frame, suggestion, (text_x, y_pos), 
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, thickness)
