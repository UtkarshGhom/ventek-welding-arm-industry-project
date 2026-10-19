#!/usr/bin/env python3
"""
VENTEK Autonomous Welding - Gazebo Sim Simulation Launch
Launches:
1. Gazebo Sim (Harmonic) with the welding cell world (table, floor, fence, lights)
2. Robot State Publisher with the unified welding cell URDF (robot + torch + fixture + part + clamps + camera)
3. Spawner to spawn the cell into Gazebo Sim
4. ros_gz_bridge for clock, camera images, depth maps, and point clouds
5. RViz2 visualization with welding cell config
"""

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, SetEnvironmentVariable, TimerAction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    # Clean up any orphaned or stale Gazebo processes from previous sessions
    os.system("pkill -9 -f 'gz sim server' 2>/dev/null || true")

    pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    xacro_file = os.path.join(pkg_dir, "urdf", "welding_cell", "welding_cell.urdf.xacro")
    world_file = os.path.join(pkg_dir, "simulation", "worlds", "welding_cell.sdf")
    rviz_config_file = os.path.join(pkg_dir, "config", "welding_cell.rviz")

    pkg_parent = os.path.dirname(pkg_dir)
    ws_install = os.path.abspath(os.path.join(pkg_dir, "..", "..", "install"))
    share_dir = os.path.join(ws_install, "ventek_autonomous_welding", "share")

    res_paths = f"{pkg_parent}:{share_dir}:{ws_install}:{pkg_dir}:{pkg_dir}/simulation:{pkg_dir}/simulation/cell/meshes:{pkg_dir}/simulation/tool/meshes:{pkg_dir}/simulation/robot/meshes"

    # Set Gazebo resource path to resolve meshes
    gz_resource_path = SetEnvironmentVariable(
        name="GZ_SIM_RESOURCE_PATH",
        value=res_paths
    )
    ign_resource_path = SetEnvironmentVariable(
        name="IGN_GAZEBO_RESOURCE_PATH",
        value=res_paths
    )

    # Ensure this package is found in AMENT_PREFIX_PATH
    pkg_install = os.path.abspath(os.path.join(pkg_dir, "..", "..", "install", "ventek_autonomous_welding"))
    current_ament = os.environ.get("AMENT_PREFIX_PATH", "")
    new_ament = f"{pkg_install}:{current_ament}" if os.path.exists(pkg_install) else current_ament
    set_ament_env = SetEnvironmentVariable(name="AMENT_PREFIX_PATH", value=new_ament)

    # Launch Arguments
    use_rviz_arg = DeclareLaunchArgument(
        "rviz",
        default_value="true",
        description="Whether to launch RViz2"
    )

    use_sim_time_arg = DeclareLaunchArgument(
        "use_sim_time",
        default_value="true",
        description="Use simulation clock"
    )

    headless_arg = DeclareLaunchArgument(
        "headless",
        default_value="false",
        description="Run Gazebo in headless mode"
    )

    gui_slider_arg = DeclareLaunchArgument(
        "gui_slider",
        default_value="true",
        description="Launch Joint State Publisher GUI slider for interactive joint posing"
    )

    depth_viewer_arg = DeclareLaunchArgument(
        "depth_viewer",
        default_value="false",
        description="Launch OpenCV interactive Live Depth Map viewer window"
    )

    # Process Xacro
    robot_description_content = Command(["xacro ", xacro_file])
    robot_description_param = ParameterValue(robot_description_content, value_type=str)

    # 1. Robot State Publisher
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[{
            "robot_description": robot_description_param,
            "use_sim_time": LaunchConfiguration("use_sim_time")
        }]
    )

    # 2. Gazebo Sim Process
    gz_sim = ExecuteProcess(
        cmd=["gz", "sim", "-r", world_file],
        output="screen",
        additional_env={
            "GZ_SIM_RESOURCE_PATH": res_paths,
            "IGN_GAZEBO_RESOURCE_PATH": res_paths,
            "AMENT_PREFIX_PATH": new_ament
        }
    )

    # 3. Spawn Cell / Robot in Gazebo Sim (delayed by 2.0s to ensure Gazebo runner is ready)
    spawn_cell = TimerAction(
        period=2.0,
        actions=[
            Node(
                package="ros_gz_sim",
                executable="create",
                output="screen",
                arguments=[
                    "-string", robot_description_content,
                    "-name", "ventek_welding_cell",
                    "-allow_renaming", "true",
                    "-z", "0.0"
                ]
            )
        ]
    )

    # 4. ROS-Gazebo Topic Bridge (Clock, Camera, Depth Image, PointCloud, and 6-DOF Joint Commands)
    bridge_node = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        output="screen",
        arguments=[
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
            "/ventek/vision/camera/image@sensor_msgs/msg/Image[gz.msgs.Image",
            "/ventek/vision/camera/depth_image@sensor_msgs/msg/Image[gz.msgs.Image",
            "/ventek/vision/camera/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked",
            "/ventek/vision/camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo",
            # Joint Position Command Bridges (ROS std_msgs/Float64 -> Gazebo gz.msgs.Double)
            "/model/ventek_welding_cell/joint/joint_a1/cmd_pos@std_msgs/msg/Float64]gz.msgs.Double",
            "/model/ventek_welding_cell/joint/joint_a2/cmd_pos@std_msgs/msg/Float64]gz.msgs.Double",
            "/model/ventek_welding_cell/joint/joint_a3/cmd_pos@std_msgs/msg/Float64]gz.msgs.Double",
            "/model/ventek_welding_cell/joint/joint_a4/cmd_pos@std_msgs/msg/Float64]gz.msgs.Double",
            "/model/ventek_welding_cell/joint/joint_a5/cmd_pos@std_msgs/msg/Float64]gz.msgs.Double",
            "/model/ventek_welding_cell/joint/joint_a6/cmd_pos@std_msgs/msg/Float64]gz.msgs.Double",
        ],
        parameters=[{"use_sim_time": LaunchConfiguration("use_sim_time")}]
    )

    # 5. Interactive Joint State Publisher GUI (Sliders for joint_a1 to joint_a6)
    joint_state_publisher_gui_node = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
        name="joint_state_publisher_gui",
        output="screen",
        condition=IfCondition(LaunchConfiguration("gui_slider"))
    )

    # 6. Joint State to Gazebo Command Bridge Node
    joint_slider_bridge_node = Node(
        package="ventek_autonomous_welding",
        executable="joint_state_to_gz",
        name="joint_state_to_gz_bridge",
        output="screen",
        condition=IfCondition(LaunchConfiguration("gui_slider"))
    )

    # 7. RViz2 Node
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", rviz_config_file],
        condition=IfCondition(LaunchConfiguration("rviz")),
        parameters=[{"use_sim_time": LaunchConfiguration("use_sim_time")}]
    )

    # 8. Optional OpenCV Live Depth Map Viewer
    depth_viewer_node = Node(
        package="ventek_autonomous_welding",
        executable="view_depth_feed",
        name="live_depth_viewer",
        output="screen",
        condition=IfCondition(LaunchConfiguration("depth_viewer"))
    )

    return LaunchDescription([
        gz_resource_path,
        ign_resource_path,
        set_ament_env,
        use_rviz_arg,
        use_sim_time_arg,
        headless_arg,
        gui_slider_arg,
        depth_viewer_arg,
        robot_state_publisher_node,
        gz_sim,
        spawn_cell,
        bridge_node,
        joint_state_publisher_gui_node,
        joint_slider_bridge_node,
        rviz_node,
        depth_viewer_node
    ])
