#!/usr/bin/env python3
"""
VENTEK Autonomous Welding - Planning Pipeline Launch
Brings up the robot description, planning scene environment, and RViz2 for Team 6 path planning validation.
"""

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    xacro_file = os.path.join(pkg_dir, "urdf", "welding_cell", "welding_cell.urdf.xacro")
    rviz_config_file = os.path.join(pkg_dir, "config", "welding_cell.rviz")

    robot_description = ParameterValue(Command(["xacro ", xacro_file]), value_type=str)

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[{"robot_description": robot_description, "use_sim_time": False}]
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", rviz_config_file]
    )

    return LaunchDescription([
        robot_state_publisher_node,
        rviz_node
    ])
