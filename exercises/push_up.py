"""
Push-Up Exercise Tracking Module
Tracks push-up repetitions using elbow angle analysis
"""

import cv2
import time
from pose_estimation.angle_calculation import calculate_angle
from feedback.movement_suggestions import get_push_up_suggestions


class PushUp:
    def __init__(self, use_time_throttle=True):
        self.counter = 0
        self.stage = "Initial"
        self.angle_threshold_up = 150
        self.angle_threshold_down = 70
        self.last_counter_update = time.time()
        self.use_time_throttle = use_time_throttle

    def calculate_shoulder_elbow_wrist_angle(self, shoulder, elbow, wrist):
        return calculate_angle(shoulder, elbow, wrist)

    def track_push_up(self, landmarks, frame):
        shoulder_left = [int(landmarks[11].x * frame.shape[1]), int(landmarks[11].y * frame.shape[0])]
        elbow_left = [int(landmarks[13].x * frame.shape[1]), int(landmarks[13].y * frame.shape[0])]
        wrist_left = [int(landmarks[15].x * frame.shape[1]), int(landmarks[15].y * frame.shape[0])]

        shoulder_right = [int(landmarks[12].x * frame.shape[1]), int(landmarks[12].y * frame.shape[0])]
        elbow_right = [int(landmarks[14].x * frame.shape[1]), int(landmarks[14].y * frame.shape[0])]
        wrist_right = [int(landmarks[16].x * frame.shape[1]), int(landmarks[16].y * frame.shape[0])]

        angle_left = self.calculate_shoulder_elbow_wrist_angle(shoulder_left, elbow_left, wrist_left)
        angle_right = self.calculate_shoulder_elbow_wrist_angle(shoulder_right, elbow_right, wrist_right)

        self.draw_line_with_style(frame, shoulder_left, elbow_left, (0, 0, 255), 2)
        self.draw_line_with_style(frame, elbow_left, wrist_left, (0, 0, 255), 2)

        self.draw_line_with_style(frame, shoulder_right, elbow_right, (102, 0, 0), 2)
        self.draw_line_with_style(frame, elbow_right, wrist_right, (102, 0, 0), 2)

        self.draw_circle(frame, shoulder_left, (0, 0, 255), 8)
        self.draw_circle(frame, elbow_left, (0, 0, 255), 8)
        self.draw_circle(frame, wrist_left, (0, 0, 255), 8)

        self.draw_circle(frame, shoulder_right, (102, 0, 0), 8)
        self.draw_circle(frame, elbow_right, (102, 0, 0), 8)
        self.draw_circle(frame, wrist_right, (102, 0, 0), 8)

        angle_text_position_left = (elbow_left[0] + 10, elbow_left[1] - 10)
        cv2.putText(frame, f'Angle: {int(angle_left)}', angle_text_position_left, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        angle_text_position_right = (elbow_right[0] + 10, elbow_right[1] - 10)
        cv2.putText(frame, f'Angle: {int(angle_right)}', angle_text_position_right, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        current_time = time.time()

        if angle_left > self.angle_threshold_up:
            self.stage = "Starting position"
        elif self.angle_threshold_down < angle_left < self.angle_threshold_up and self.stage == "Starting position":
            self.stage = "Descent"
        elif angle_left < self.angle_threshold_down and self.stage == "Descent":
            self.stage = "Ascent"
            if self.use_time_throttle:
                if current_time - self.last_counter_update > 1:
                    self.counter += 1
                    self.last_counter_update = current_time
            else:
                self.counter += 1
        elif angle_left > self.angle_threshold_up and self.stage == "Ascent":
            self.stage = "Starting position"

        suggestions = get_push_up_suggestions(landmarks, angle_left, self.stage, frame)

        return self.counter, angle_left, self.stage, suggestions

    def draw_line_with_style(self, frame, start_point, end_point, color, thickness):
        cv2.line(frame, start_point, end_point, color, thickness, lineType=cv2.LINE_AA)

    def draw_circle(self, frame, center, color, radius):
        cv2.circle(frame, center, radius, color, -1)
