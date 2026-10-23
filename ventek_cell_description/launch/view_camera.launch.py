#!/usr/bin/env python3
"""
VENTEK Spot Welding Cell - Pop-Out RealSense D435 Camera Dashboard Launch
Launches the standalone camera pop-out window with live RGB stream,
colorized depth heatmap, and interactive crosshair millimeter distance probe.
"""

from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    dashboard_node = Node(
        package='ventek_cell_description',
        executable='view_realsense_feed.py',
        name='realsense_dashboard_viewer',
        output='screen',
    )

    return LaunchDescription([
        dashboard_node,
    ])
