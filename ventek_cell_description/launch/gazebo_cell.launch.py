#!/usr/bin/env python3
"""
VENTEK Spot Welding Cell - Full Gazebo Sim & Vision Launch Description
Launches:
1. Gazebo Sim (Harmonic) with 1000 Hz physics, industrial lighting, and factory floor
2. Environment variables (GZ_SIM_RESOURCE_PATH) passed directly to process environment
3. Spawner to instantiate the spot welding cell & Fanuc arm into Gazebo
4. ros_gz_bridge for clock, camera images, depth map, point cloud, and joint commands
5. joint_slider_sync with 50 Hz smoothing to eliminate inertia vibration
6. joint_state_publisher_gui for interactive slider control
7. Pop-out RealSense D435 camera dashboard (RGB + Depth heatmap + distance probe)
8. Optional RViz2 visualization
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, SetEnvironmentVariable, TimerAction
from launch.conditions import IfCondition
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    # Clean up stale gz sim processes from previous sessions
    os.system("pkill -9 -f 'gz sim server' 2>/dev/null || true")

    pkg_share = get_package_share_directory('ventek_cell_description')
    pkg_share_parent = os.path.dirname(pkg_share)
    install_base = os.path.dirname(pkg_share_parent)
    ws_src_pkg = os.path.abspath(os.path.join(install_base, '..', 'ventek_project', 'ventek_cell_description'))
    ws_src_parent = os.path.dirname(ws_src_pkg)

    # Assemble comprehensive resource paths for Gazebo Sim
    res_paths = f"{ws_src_parent}:{pkg_share_parent}:{install_base}:{pkg_share}:{ws_src_pkg}:{os.path.join(ws_src_pkg, 'meshes')}"

    # Process-level environment variables
    if 'GZ_SIM_RESOURCE_PATH' in os.environ:
        os.environ['GZ_SIM_RESOURCE_PATH'] += f":{res_paths}"
    else:
        os.environ['GZ_SIM_RESOURCE_PATH'] = res_paths
    os.environ['IGN_GAZEBO_RESOURCE_PATH'] = os.environ['GZ_SIM_RESOURCE_PATH']

    set_gz_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=os.environ['GZ_SIM_RESOURCE_PATH']
    )
    set_ign_resource_path = SetEnvironmentVariable(
        name='IGN_GAZEBO_RESOURCE_PATH',
        value=os.environ['IGN_GAZEBO_RESOURCE_PATH']
    )

    # Launch Arguments
    rviz_arg = DeclareLaunchArgument(
        'rviz',
        default_value='true',
        description='Whether to launch RViz2 alongside Gazebo Sim'
    )
    gui_arg = DeclareLaunchArgument(
        'gui',
        default_value='true',
        description='Whether to launch joint_state_publisher_gui sliders'
    )
    camera_dashboard_arg = DeclareLaunchArgument(
        'camera_dashboard',
        default_value='true',
        description='Launch standalone RealSense D435 pop-out camera dashboard'
    )

    # World path
    world_sdf_path = os.path.join(pkg_share, 'worlds', 'spot_welding_cell.sdf')
    xacro_file = os.path.join(pkg_share, 'urdf', 'ventek_cell.urdf.xacro')
    urdf_temp_file = '/tmp/ventek_cell_model.urdf'

    # Pre-compile xacro to a static URDF file for 100% guaranteed, rock-solid Gazebo Sim spawning
    os.system(f"xacro {xacro_file} > {urdf_temp_file}")

    # Robot Description via XACRO for Robot State Publisher
    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name='xacro')]),
            ' ',
            xacro_file,
        ]
    )
    robot_description = {
        'robot_description': ParameterValue(robot_description_content, value_type=str)
    }

    # 1. Robot State Publisher
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='both',
        parameters=[robot_description, {'use_sim_time': False}],
    )

    # 2. Gazebo Sim Process (with explicit environment for mesh resolution)
    gz_sim = ExecuteProcess(
        cmd=['gz', 'sim', '-r', world_sdf_path],
        output='screen',
        additional_env={
            'GZ_SIM_RESOURCE_PATH': os.environ['GZ_SIM_RESOURCE_PATH'],
            'IGN_GAZEBO_RESOURCE_PATH': os.environ['IGN_GAZEBO_RESOURCE_PATH'],
        }
    )

    # 3. Spawn Entity into Gazebo Sim using -file (instant, robust, never hangs)
    spawn_entity = TimerAction(
        period=1.5,
        actions=[
            Node(
                package='ros_gz_sim',
                executable='create',
                output='screen',
                arguments=[
                    '-file', urdf_temp_file,
                    '-name', 'ventek_spot_welding_cell',
                    '-allow_renaming', 'true',
                    '-z', '0.0',
                ],
            )
        ]
    )

    # 4. ROS-Gz Bridge for Clock, Joint States, Command Topics, and RealSense Streams
    bridge_args = [
        '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
        '/joint_states_gz@sensor_msgs/msg/JointState[gz.msgs.Model',
        # Individual Joint Position Command Bridges (ROS -> Gazebo)
        '/model/ventek_spot_welding_cell/joint/joint_1/cmd_pos@std_msgs/msg/Float64]gz.msgs.Double',
        '/model/ventek_spot_welding_cell/joint/joint_2/cmd_pos@std_msgs/msg/Float64]gz.msgs.Double',
        '/model/ventek_spot_welding_cell/joint/joint_3/cmd_pos@std_msgs/msg/Float64]gz.msgs.Double',
        '/model/ventek_spot_welding_cell/joint/joint_4/cmd_pos@std_msgs/msg/Float64]gz.msgs.Double',
        '/model/ventek_spot_welding_cell/joint/joint_5/cmd_pos@std_msgs/msg/Float64]gz.msgs.Double',
        '/model/ventek_spot_welding_cell/joint/joint_6/cmd_pos@std_msgs/msg/Float64]gz.msgs.Double',
        '/model/ventek_spot_welding_cell/joint/cell_door_joint/cmd_pos@std_msgs/msg/Float64]gz.msgs.Double',
        # Intel RealSense D435 Vision Bridges (Gazebo Sim -> ROS 2)
        '/realsense/image@sensor_msgs/msg/Image[gz.msgs.Image',
        '/realsense/depth_image@sensor_msgs/msg/Image[gz.msgs.Image',
        '/realsense/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
        '/realsense/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked',
    ]

    gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=bridge_args,
        output='screen',
    )

    # 5. Smooth synchronizer node: filters /joint_states with 50 Hz EMA filter
    joint_sync_node = Node(
        package='ventek_cell_description',
        executable='joint_slider_sync.py',
        output='screen',
    )

    # 6. Joint State Publisher GUI (Interactive Sliders initialized at nominal inspection pose)
    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        condition=IfCondition(LaunchConfiguration('gui')),
        parameters=[{
            'zeros.joint_1': -0.4872,
            'zeros.joint_2': 0.6147,
            'zeros.joint_3': 1.0346,
            'zeros.joint_4': 0.0,
            'zeros.joint_5': -1.4147,
            'zeros.joint_6': 0.0,
            'zeros.cell_door_joint': 0.0,
        }],
    )

    # 7. Standalone Pop-Out Camera Dashboard (OpenCV RealSense D435 RGB + Depth)
    camera_dashboard_node = Node(
        package='ventek_cell_description',
        executable='view_realsense_feed.py',
        name='realsense_dashboard_viewer',
        output='screen',
        condition=IfCondition(LaunchConfiguration('camera_dashboard')),
    )

    # 8. RViz2 Node (Optional)
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='log',
        arguments=['-d', os.path.join(pkg_share, 'config', 'rviz.rviz')],
        condition=IfCondition(LaunchConfiguration('rviz')),
    )

    return LaunchDescription([
        set_gz_resource_path,
        set_ign_resource_path,
        rviz_arg,
        gui_arg,
        camera_dashboard_arg,
        robot_state_publisher_node,
        gz_sim,
        spawn_entity,
        gz_bridge,
        joint_sync_node,
        joint_state_publisher_gui_node,
        camera_dashboard_node,
        rviz_node,
    ])
