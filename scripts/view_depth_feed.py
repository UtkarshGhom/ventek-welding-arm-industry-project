#!/usr/bin/env python3
"""
VENTEK Autonomous Welding - Live Camera Depth & RGB Feed Viewer
Subscribes to:
- /ventek/vision/camera/depth_image (sensor_msgs/Image, 32FC1 in meters)
- /ventek/vision/camera/image       (sensor_msgs/Image, RGB)

Features:
- Colorized real-time depth heatmap (TURBO / JET colormap)
- Live crosshair distance probe: Hover mouse to read exact depth in millimeters
- Dynamic min/max range adjustment & side-by-side RGB/Depth display
- Always-responsive GUI loop (handles Wayland & X11 smoothly)
- Built-in status diagnostics when waiting for simulation to launch
- Press 'c' to save high-resolution snapshot to disk
- Press 's' to toggle side-by-side view
- Press 'q' or ESC to exit
"""

import sys
import os
import time
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np


class LiveDepthViewer(Node):
    def __init__(self):
        super().__init__('ventek_live_depth_viewer')
        try:
            self.declare_parameter('use_sim_time', True)
        except rclpy.exceptions.ParameterAlreadyDeclaredException:
            pass
        self.bridge = CvBridge()

        self.depth_image = None
        self.rgb_image = None
        self.cursor_pos = None

        self.depth_frame_count = 0
        self.rgb_frame_count = 0
        self.last_depth_time = 0.0
        self.fps = 0.0
        self._fps_counter = 0
        self._fps_timer = time.time()

        # Reliable QoS matching ros_gz_bridge
        qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        # Subscribers
        self.sub_depth = self.create_subscription(
            Image,
            '/ventek/vision/camera/depth_image',
            self.depth_callback,
            qos
        )

        self.sub_rgb = self.create_subscription(
            Image,
            '/ventek/vision/camera/image',
            self.rgb_callback,
            qos
        )

        self.window_name = "VENTEK Welding Cell - Live Camera Feed"
        cv2.namedWindow(self.window_name, cv2.WINDOW_AUTOSIZE)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)

        self.show_side_by_side = True
        self.min_dist_m = 0.3
        self.max_dist_m = 2.2

        # 30 Hz rendering loop to ensure window remains interactive in Wayland/X11
        self.timer = self.create_timer(1.0 / 30.0, self.render_loop)

        self.get_logger().info("VENTEK Depth & RGB Viewer initialized.")
        self.get_logger().info("Listening on: /ventek/vision/camera/depth_image and /ventek/vision/camera/image")
        self.get_logger().info("Controls: 's' = toggle side-by-side | 'c' = capture frame | 'q' = quit")

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_MOUSEMOVE:
            self.cursor_pos = (x, y)

    def depth_callback(self, msg):
        try:
            depth_cv = self.bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")
            self.depth_image = np.nan_to_num(depth_cv, nan=0.0, posinf=0.0, neginf=0.0)
            self.depth_frame_count += 1
            self.last_depth_time = time.time()

            # Calculate FPS
            self._fps_counter += 1
            elapsed = time.time() - self._fps_timer
            if elapsed >= 1.0:
                self.fps = self._fps_counter / elapsed
                self._fps_counter = 0
                self._fps_timer = time.time()
        except Exception as e:
            self.get_logger().error(f"Depth conversion error: {e}")

    def rgb_callback(self, msg):
        try:
            self.rgb_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
            self.rgb_frame_count += 1
        except Exception as e:
            self.get_logger().error(f"RGB conversion error: {e}")

    def render_waiting_screen(self):
        canvas = np.zeros((480, 720, 3), dtype=np.uint8)
        canvas[:] = (30, 32, 36)

        # Pulse animation
        pulse = int(40 * (np.sin(time.time() * 3.0) + 1.0))
        accent_color = (0, 180 + pulse, 255)

        cv2.putText(canvas, "VENTEK AUTONOMOUS WELDING CELL", (40, 70),
                    cv2.FONT_HERSHEY_DUPLEX, 0.85, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.line(canvas, (40, 85), (680, 85), accent_color, 2)

        cv2.putText(canvas, "CAMERA STREAM STATUS: WAITING FOR SIMULATION", (40, 140),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, accent_color, 2, cv2.LINE_AA)

        # Topic diagnostics
        y = 200
        topics = [
            ("/ventek/vision/camera/depth_image", self.depth_frame_count > 0, self.depth_frame_count),
            ("/ventek/vision/camera/image", self.rgb_frame_count > 0, self.rgb_frame_count),
        ]
        for name, active, count in topics:
            status_txt = f"[ACTIVE - {count} frames]" if active else "[WAITING]"
            color = (80, 240, 80) if active else (120, 120, 200)
            cv2.putText(canvas, f"{name}:", (50, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1, cv2.LINE_AA)
            cv2.putText(canvas, status_txt, (460, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1, cv2.LINE_AA)
            y += 35

        cv2.rectangle(canvas, (40, 300), (680, 420), (45, 48, 55), -1)
        cv2.rectangle(canvas, (40, 300), (680, 420), (70, 75, 85), 1)
        cv2.putText(canvas, "Instructions:", (60, 330),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(canvas, "1. Launch Gazebo Sim simulation:", (60, 360),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.48, (200, 200, 200), 1, cv2.LINE_AA)
        cv2.putText(canvas, "   ros2 launch ventek_autonomous_welding simulation.launch.py", (60, 385),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 220, 255), 1, cv2.LINE_AA)
        cv2.putText(canvas, "(Live video will appear automatically once Gazebo publishes)", (60, 410),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (150, 150, 150), 1, cv2.LINE_AA)

        return canvas

    def render_loop(self):
        # If no depth data yet, display waiting dashboard
        if self.depth_image is None:
            display = self.render_waiting_screen()
            cv2.imshow(self.window_name, display)
            self.handle_keys(display)
            return

        h, w = self.depth_image.shape[:2]

        # Normalize depth between min_dist and max_dist for maximum contrast
        clipped = np.clip(self.depth_image, self.min_dist_m, self.max_dist_m)
        norm_depth = ((clipped - self.min_dist_m) / (self.max_dist_m - self.min_dist_m) * 255.0).astype(np.uint8)

        # Apply colorful Turbo heatmap
        depth_colormap = cv2.applyColorMap(norm_depth, cv2.COLORMAP_TURBO)

        # Highlight invalid / zero depth
        depth_colormap[self.depth_image <= 0.05] = [30, 30, 30]

        # Live mouse distance probe
        probe_text = "Hover mouse to probe depth"
        if self.cursor_pos:
            cx, cy = self.cursor_pos
            # Adjust coordinate if side-by-side
            if self.show_side_by_side and self.rgb_image is not None and cx >= w:
                cx -= w
            if 0 <= cx < w and 0 <= cy < h:
                dist = self.depth_image[cy, cx]
                if dist > 0.05:
                    probe_text = f"Depth at ({cx}, {cy}): {dist:.3f} m ({dist*1000:.0f} mm)"
                    cv2.circle(depth_colormap, (cx, cy), 6, (0, 255, 255), 2)
                    cv2.line(depth_colormap, (cx - 10, cy), (cx + 10, cy), (0, 255, 255), 1)
                    cv2.line(depth_colormap, (cx, cy - 10), (cx, cy + 10), (0, 255, 255), 1)
                else:
                    probe_text = f"Depth at ({cx}, {cy}): Out of Range / Occluded"

        # Overlay telemetry HUD on Depth
        cv2.rectangle(depth_colormap, (5, 5), (w - 5, 45), (20, 20, 20), -1)
        cv2.putText(depth_colormap, f"OAK-D Lite Depth [{self.min_dist_m:.1f}m - {self.max_dist_m:.1f}m] | FPS: {self.fps:.1f}",
                    (12, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(depth_colormap, probe_text,
                    (12, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1, cv2.LINE_AA)

        # Assemble display
        if self.show_side_by_side:
            if self.rgb_image is not None:
                rgb_resized = cv2.resize(self.rgb_image, (w, h))
            else:
                rgb_resized = np.zeros((h, w, 3), dtype=np.uint8)
                cv2.putText(rgb_resized, "Waiting for RGB stream...", (w // 4, h // 2),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 180, 180), 1, cv2.LINE_AA)
            cv2.rectangle(rgb_resized, (5, 5), (w - 5, 30), (20, 20, 20), -1)
            cv2.putText(rgb_resized, f"OAK-D Lite RGB Stream ({w}x{h})",
                        (12, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
            display = np.hstack([rgb_resized, depth_colormap])
        else:
            display = depth_colormap

        cv2.imshow(self.window_name, display)
        self.handle_keys(display)

    def handle_keys(self, display_canvas):
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            rclpy.shutdown()
        elif key == ord('s'):
            self.show_side_by_side = not self.show_side_by_side
        elif key == ord('+') or key == ord('='):
            self.max_dist_m = min(5.0, self.max_dist_m + 0.2)
        elif key == ord('-') or key == ord('_'):
            self.max_dist_m = max(self.min_dist_m + 0.2, self.max_dist_m - 0.2)
        elif key == ord('c'):
            save_path = f"/tmp/ventek_camera_snapshot_{int(time.time())}.png"
            cv2.imwrite(save_path, display_canvas)
            self.get_logger().info(f"Saved snapshot to: {save_path}")


def main():
    rclpy.init()
    node = LiveDepthViewer()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
        pass
    finally:
        cv2.destroyAllWindows()
        if rclpy.ok():
            node.destroy_node()
            rclpy.shutdown()


if __name__ == '__main__':
    main()
