#!/usr/bin/env python3
"""
VENTEK Spot Welding Cell - Intel RealSense D435 Live Camera Feed & Depth Dashboard
Pop-out standalone window providing real-time eye-in-hand RGB stream, colorized depth heatmap,
interactive crosshair distance probe, and telemetry.

Subscribes to:
- /realsense/image       (sensor_msgs/Image, RGB)
- /realsense/depth_image (sensor_msgs/Image, 32FC1 in meters)

Controls:
- Mouse hover : Read live depth probe in millimeters at cursor position
- 's'         : Toggle side-by-side view (RGB + Depth Heatmap) vs Depth only vs RGB only
- '+' / '-'   : Adjust depth contrast range
- 'c'         : Save high-resolution snapshot to disk
- 'q' or ESC  : Exit
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


class RealSenseDashboardViewer(Node):
    def __init__(self):
        super().__init__('realsense_dashboard_viewer')
        try:
            self.declare_parameter('use_sim_time', False)
        except rclpy.exceptions.ParameterAlreadyDeclaredException:
            pass

        self.bridge = CvBridge()
        self.depth_image = None
        self.rgb_image = None
        self.cursor_pos = None

        self.depth_frame_count = 0
        self.rgb_frame_count = 0
        self.fps = 0.0
        self._fps_counter = 0
        self._fps_timer = time.time()

        # Display modes: 0 = side-by-side, 1 = depth only, 2 = rgb only
        self.view_mode = 0
        self.min_dist_m = 0.15
        self.max_dist_m = 3.5

        # QoS matching ros_gz_bridge
        qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        # Subscribers
        self.sub_depth = self.create_subscription(
            Image,
            '/realsense/depth_image',
            self.depth_callback,
            qos
        )

        self.sub_rgb = self.create_subscription(
            Image,
            '/realsense/image',
            self.rgb_callback,
            qos
        )

        self.window_name = "VENTEK Spot Welding - RealSense D435 Eye-In-Hand Feed"
        cv2.namedWindow(self.window_name, cv2.WINDOW_AUTOSIZE)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)

        # 30 Hz rendering loop
        self.timer = self.create_timer(1.0 / 30.0, self.render_loop)

        self.get_logger().info("RealSense D435 Camera Dashboard initialized.")
        self.get_logger().info("Subscribing to /realsense/image and /realsense/depth_image")

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_MOUSEMOVE:
            self.cursor_pos = (x, y)

    def depth_callback(self, msg):
        try:
            depth_cv = self.bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")
            self.depth_image = np.nan_to_num(depth_cv, nan=0.0, posinf=0.0, neginf=0.0)
            self.depth_frame_count += 1

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
        canvas = np.zeros((520, 800, 3), dtype=np.uint8)
        canvas[:] = (26, 28, 32)

        # Animated status pulse
        pulse = int(45 * (np.sin(time.time() * 3.5) + 1.0))
        fanuc_yellow = (5, 185 + pulse, 245)  # BGR for yellow accent

        # Header Title
        cv2.putText(canvas, "VENTEK SPOT WELDING CELL - REALSENSE D435", (40, 65),
                    cv2.FONT_HERSHEY_DUPLEX, 0.75, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.line(canvas, (40, 80), (760, 80), fanuc_yellow, 2)

        cv2.putText(canvas, "CAMERA STREAM STATUS: CONNECTING TO SIMULATION...", (40, 130),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.60, fanuc_yellow, 2, cv2.LINE_AA)

        # Channel status
        y = 190
        channels = [
            ("/realsense/image (RGB Stream)", self.rgb_frame_count > 0, self.rgb_frame_count),
            ("/realsense/depth_image (Depth Map)", self.depth_frame_count > 0, self.depth_frame_count),
        ]
        for name, active, count in channels:
            status_txt = f"[ACTIVE - {count} frames]" if active else "[WAITING FOR GAZEBO]"
            color = (80, 240, 80) if active else (130, 130, 210)
            cv2.putText(canvas, name, (50, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.48, (210, 210, 210), 1, cv2.LINE_AA)
            cv2.putText(canvas, status_txt, (520, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.48, color, 1, cv2.LINE_AA)
            y += 40

        # Launch Box
        cv2.rectangle(canvas, (40, 310), (760, 470), (36, 39, 46), -1)
        cv2.rectangle(canvas, (40, 310), (760, 470), (70, 75, 88), 1)
        cv2.putText(canvas, "Quick Launch Guide:", (60, 345),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(canvas, "1. Launch Gazebo Spot Welding Cell in your terminal:", (60, 380),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.48, (200, 200, 200), 1, cv2.LINE_AA)
        cv2.putText(canvas, "   ros2 launch ventek_cell_description gazebo_cell.launch.py", (60, 410),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.50, (0, 220, 255), 1, cv2.LINE_AA)
        cv2.putText(canvas, "2. Live Eye-in-Hand camera view will automatically stream into this window.", (60, 445),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.44, (160, 160, 160), 1, cv2.LINE_AA)

        return canvas

    def render_loop(self):
        if self.depth_image is None and self.rgb_image is None:
            display = self.render_waiting_screen()
            cv2.imshow(self.window_name, display)
            self.handle_keys(display)
            return

        h, w = (480, 640)
        if self.depth_image is not None:
            h, w = self.depth_image.shape[:2]
        elif self.rgb_image is not None:
            h, w = self.rgb_image.shape[:2]

        # Prepare Depth Heatmap
        if self.depth_image is not None:
            clipped = np.clip(self.depth_image, self.min_dist_m, self.max_dist_m)
            norm_depth = ((clipped - self.min_dist_m) / (self.max_dist_m - self.min_dist_m) * 255.0).astype(np.uint8)
            depth_colormap = cv2.applyColorMap(norm_depth, cv2.COLORMAP_TURBO)
            depth_colormap[self.depth_image <= 0.05] = [25, 25, 25]
        else:
            depth_colormap = np.zeros((h, w, 3), dtype=np.uint8)
            cv2.putText(depth_colormap, "Waiting for depth stream...", (w // 4, h // 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 180, 180), 1, cv2.LINE_AA)

        # Prepare RGB Image
        if self.rgb_image is not None:
            rgb_disp = cv2.resize(self.rgb_image, (w, h))
        else:
            rgb_disp = np.zeros((h, w, 3), dtype=np.uint8)
            cv2.putText(rgb_disp, "Waiting for RGB stream...", (w // 4, h // 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 180, 180), 1, cv2.LINE_AA)

        # Interactive Mouse Depth Probe
        probe_text = "Hover cursor to inspect distance"
        if self.cursor_pos and self.depth_image is not None:
            cx, cy = self.cursor_pos
            probe_x = cx
            if self.view_mode == 0 and cx >= w:
                probe_x = cx - w  # Cursor is on depth panel in side-by-side mode

            if 0 <= probe_x < w and 0 <= cy < h:
                dist = self.depth_image[cy, probe_x]
                if dist > 0.05:
                    probe_text = f"Distance at ({probe_x}, {cy}): {dist:.3f} m  ({dist * 1000.0:.0f} mm)"
                    # Crosshairs on both panels
                    for panel, offset in [(rgb_disp, 0), (depth_colormap, 0)]:
                        cv2.circle(panel, (probe_x, cy), 6, (0, 255, 255), 2)
                        cv2.line(panel, (probe_x - 12, cy), (probe_x + 12, cy), (0, 255, 255), 1)
                        cv2.line(panel, (probe_x, cy - 12), (probe_x, cy + 12), (0, 255, 255), 1)
                else:
                    probe_text = f"Distance at ({probe_x}, {cy}): Beyond range / Occluded"

        # Overlay HUD on RGB
        cv2.rectangle(rgb_disp, (8, 8), (w - 8, 48), (20, 22, 26), -1)
        cv2.putText(rgb_disp, f"Intel RealSense D435 | Eye-in-Hand RGB ({w}x{h})",
                    (16, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(rgb_disp, "FOV: 87 deg H-FOV | Zero-Occlusion Fixture & Clamps POV",
                    (16, 42), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (0, 215, 255), 1, cv2.LINE_AA)

        # Overlay HUD on Depth
        cv2.rectangle(depth_colormap, (8, 8), (w - 8, 48), (20, 22, 26), -1)
        cv2.putText(depth_colormap, f"Depth Heatmap [{self.min_dist_m:.2f}m - {self.max_dist_m:.2f}m] | FPS: {self.fps:.1f}",
                    (16, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(depth_colormap, probe_text,
                    (16, 42), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 255, 255), 1, cv2.LINE_AA)

        # Select layout according to view_mode
        if self.view_mode == 0:
            display = np.hstack([rgb_disp, depth_colormap])
        elif self.view_mode == 1:
            display = depth_colormap
        else:
            display = rgb_disp

        cv2.imshow(self.window_name, display)
        self.handle_keys(display)

    def handle_keys(self, display_canvas):
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            rclpy.shutdown()
        elif key == ord('s'):
            self.view_mode = (self.view_mode + 1) % 3
        elif key == ord('+') or key == ord('='):
            self.max_dist_m = min(6.0, self.max_dist_m + 0.25)
        elif key == ord('-') or key == ord('_'):
            self.max_dist_m = max(self.min_dist_m + 0.25, self.max_dist_m - 0.25)
        elif key == ord('c'):
            save_path = f"/tmp/ventek_realsense_snapshot_{int(time.time())}.png"
            cv2.imwrite(save_path, display_canvas)
            self.get_logger().info(f"Saved snapshot to: {save_path}")


def main(args=None):
    rclpy.init(args=args)
    node = RealSenseDashboardViewer()
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
