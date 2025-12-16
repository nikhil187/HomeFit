"""
Text Drawing Utility
Draws text with background for better visibility
"""

import cv2


def draw_text_with_background(frame, text, position, font, font_scale, text_color, bg_color, thickness=2):
    """
    Draw text with a background rectangle for improved visibility.
    
    Args:
        frame: OpenCV image frame
        text: Text string to display
        position: (x, y) coordinates for text
        font: OpenCV font type
        font_scale: Font size multiplier
        text_color: RGB color tuple for text
        bg_color: RGB color tuple for background
        thickness: Text thickness
    """
    (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, thickness)
    
    x, y = position
    background_top_left = (x, y - text_height - 5)
    background_bottom_right = (x + text_width, y + 5)
    
    cv2.rectangle(frame, background_top_left, background_bottom_right, bg_color, cv2.FILLED)
    cv2.putText(frame, text, (x, y), font, font_scale, text_color, thickness)
