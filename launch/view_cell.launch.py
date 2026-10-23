#!/usr/bin/env python3
"""
VENTEK Autonomous Welding - View Cell Launch
Lightweight inspection of the complete welding cell in RViz2:
- Robot Model, Fixture, Part, Clamps, Torch, Camera
- Interactive joint state slider GUI
- TF coordinate frame visualizer
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    xacro_file = os.path.join(pkg_dir, "urdf", "welding_cell", "welding_cell.urdf.xacro")
    rviz_config_file = os.path.join(pkg_dir, "config", "welding_cell.rviz")

    # Ensure this package is found in AMENT_PREFIX_PATH
    ws_install = os.path.abspath(os.path.join(pkg_dir, "..", "..", "install", "ventek_autonomous_welding"))
    current_ament = os.environ.get("AMENT_PREFIX_PATH", "")
    new_ament = f"{ws_install}:{current_ament}" if os.path.exists(ws_install) else current_ament
    set_ament_env = SetEnvironmentVariable(name="AMENT_PREFIX_PATH", value=new_ament)

    # Generate robot_description via xacro command wrapped in ParameterValue
    robot_description = ParameterValue(Command(["xacro ", xacro_file]), value_type=str)

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[{
            "robot_description": robot_description,
            "use_sim_time": False
        }]
    )

    joint_state_publisher_gui_node = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
        name="joint_state_publisher_gui",
        output="screen"
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", rviz_config_file]
    )

    return LaunchDescription([
        set_ament_env,
        robot_state_publisher_node,
        joint_state_publisher_gui_node,
        rviz_node
    ])
