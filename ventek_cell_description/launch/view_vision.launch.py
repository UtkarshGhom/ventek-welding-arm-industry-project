#!/usr/bin/env python3
"""
VENTEK Vision & Depth Map Viewer Launch
Launches a dedicated RViz2 window configured specifically for Intel RealSense D435 inspection:
- Arm POV (Robot Model & TF)
- Live RGB Feed (/realsense/image)
- Live Depth Map with Normalized Gradient (/realsense/depth_image)
- Live 3D RealSense PointCloud (/realsense/points)
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    pkg_share = get_package_share_directory('ventek_cell_description')
    rviz_config = os.path.join(pkg_share, 'config', 'depth_vision.rviz')

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='realsense_vision_rviz',
        output='screen',
        arguments=['-d', rviz_config],
    )

    return LaunchDescription([
        rviz_node,
    ])
