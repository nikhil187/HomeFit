"""
Hammer Curl Exercise Tracking Module
Tracks bilateral hammer curl repetitions with form analysis
"""

import cv2
import numpy as np
from pose_estimation.angle_calculation import calculate_angle
from feedback.movement_suggestions import get_hammer_curl_suggestions


class HammerCurl:
    def __init__(self):
        self.counter_right = 0
        self.counter_left = 0
        self.stage_right = None
        self.stage_left = None
        self.angle_threshold = 40
        self.flexion_angle_up = 155
        self.flexion_angle_down = 35
        self.angle_threshold_up = 155
        self.angle_threshold_down = 47

    def calculate_shoulder_elbow_hip_angle(self, shoulder, elbow, hip):
        return calculate_angle(elbow, shoulder, hip)

    def calculate_shoulder_elbow_wrist(self, shoulder, elbow, wrist):
        return calculate_angle(shoulder, elbow, wrist)

    def track_hammer_curl(self, landmarks, frame):
        shoulder_right = [int(landmarks[11].x * frame.shape[1]), int(landmarks[11].y * frame.shape[0])]
        elbow_right = [int(landmarks[13].x * frame.shape[1]), int(landmarks[13].y * frame.shape[0])]
        hip_right = [int(landmarks[23].x * frame.shape[1]), int(landmarks[23].y * frame.shape[0])]
        wrist_right = [int(landmarks[15].x * frame.shape[1]), int(landmarks[15].y * frame.shape[0])]

        shoulder_left = [int(landmarks[12].x * frame.shape[1]), int(landmarks[12].y * frame.shape[0])]
        elbow_left = [int(landmarks[14].x * frame.shape[1]), int(landmarks[14].y * frame.shape[0])]
        hip_left = [int(landmarks[24].x * frame.shape[1]), int(landmarks[24].y * frame.shape[0])]
        wrist_left = [int(landmarks[16].x * frame.shape[1]), int(landmarks[16].y * frame.shape[0])]

        angle_right_counter = self.calculate_shoulder_elbow_wrist(shoulder_right, elbow_right, wrist_right)
        angle_left_counter = self.calculate_shoulder_elbow_wrist(shoulder_left, elbow_left, wrist_left)
        angle_right = self.calculate_shoulder_elbow_hip_angle(shoulder_right, elbow_right, hip_right)
        angle_left = self.calculate_shoulder_elbow_hip_angle(shoulder_left, elbow_left, hip_left)

        self.draw_line_with_style(frame, shoulder_left, elbow_left, (0, 0, 255), 4)
        self.draw_line_with_style(frame, elbow_left, wrist_left, (0, 0, 255), 4)

        self.draw_line_with_style(frame, shoulder_right, elbow_right, (0, 0, 255), 4)
        self.draw_line_with_style(frame, elbow_right, wrist_right, (0, 0, 255), 4)

        self.draw_circle(frame, shoulder_left, (0, 0, 255), 8)
        self.draw_circle(frame, elbow_left, (0, 0, 255), 8)
        self.draw_circle(frame, wrist_left, (0, 0, 255), 8)

        self.draw_circle(frame, shoulder_right, (0, 0, 255), 8)
        self.draw_circle(frame, elbow_right, (0, 0, 255), 8)
        self.draw_circle(frame, wrist_right, (0, 0, 255), 8)

        angle_text_position_left = (elbow_left[0] + 10, elbow_left[1] - 10)
        cv2.putText(frame, f'Angle: {int(angle_left_counter)}', angle_text_position_left, cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                     (255, 255, 255), 2)

        angle_text_position_right = (elbow_right[0] + 10, elbow_right[1] - 10)
        cv2.putText(frame, f'Angle: {int(angle_right_counter)}', angle_text_position_right, cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255), 2)

        warning_message_right = None
        warning_message_left = None

        if abs(angle_right) > self.angle_threshold:
            warning_message_right = f"Right Shoulder-Elbow-Hip Misalignment! Angle: {angle_right:.2f}°"
        if abs(angle_left) > self.angle_threshold:
            warning_message_left = f"Left Shoulder-Elbow-Hip Misalignment! Angle: {angle_left:.2f}°"

        if angle_right_counter > self.angle_threshold_up:
            self.stage_right = "Flex"
        elif self.angle_threshold_down < angle_right_counter < self.angle_threshold_up and self.stage_right == "Flex":
            self.stage_right = "Up"
        elif angle_right_counter < self.angle_threshold_down and self.stage_right == "Up":
            self.stage_right = "Down"
            self.counter_right += 1
        elif angle_right_counter > self.angle_threshold_up and self.stage_right == "Down":
            self.stage_right = "Flex"

        if angle_left_counter > self.angle_threshold_up:
            self.stage_left = "Flex"
        elif self.angle_threshold_down < angle_left_counter < self.angle_threshold_up and self.stage_left == "Flex":
            self.stage_left = "Up"
        elif angle_left_counter < self.angle_threshold_down and self.stage_left == "Up":
            self.stage_left = "Down"
            self.counter_left += 1
        elif angle_left_counter > self.angle_threshold_up and self.stage_left == "Down":
            self.stage_left = "Flex"

        progress_right = 1 if self.stage_right == "up" else 0
        progress_left = 1 if self.stage_left == "up" else 0

        suggestions_right = get_hammer_curl_suggestions(landmarks, angle_right_counter, angle_right, self.stage_right, "right", frame)
        suggestions_left = get_hammer_curl_suggestions(landmarks, angle_left_counter, angle_left, self.stage_left, "left", frame)

        return self.counter_right, angle_right_counter, self.counter_left, angle_left_counter, warning_message_right, warning_message_left, progress_right, progress_left, self.stage_right, self.stage_left, suggestions_right, suggestions_left

    def draw_line_with_style(self, frame, start_point, end_point, color, thickness):
        cv2.line(frame, start_point, end_point, color, thickness, lineType=cv2.LINE_AA)

    def draw_circle(self, frame, center, color, radius):
        cv2.circle(frame, center, radius, color, -1)
