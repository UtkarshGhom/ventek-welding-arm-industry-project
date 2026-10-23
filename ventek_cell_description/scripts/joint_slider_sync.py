#!/usr/bin/env python3
"""
VENTEK Joint Slider Synchronizer Node with Smooth Dynamic Motion Filter
Synchronizes GUI slider movements from /joint_states with Gazebo Sim joint position controllers.
Applies continuous exponential smoothing (EMA) at 50 Hz to prevent inertia shock,
stopping the FANUC R-2000iA/165F arm from oscillating back and forth ("to and fro").
Initializes at the nominal inspection pose facing Fixture Station 1.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64

class JointSliderSync(Node):
    def __init__(self):
        super().__init__('joint_slider_sync')
        
        # Tracked joints
        self.joint_names = [
            'joint_1', 'joint_2', 'joint_3',
            'joint_4', 'joint_5', 'joint_6',
            'cell_door_joint'
        ]
        
        # Default nominal workpiece inspection posture
        self.initial_positions = {
            'joint_1': -0.4872,
            'joint_2': 0.6147,
            'joint_3': 1.0346,
            'joint_4': 0.0,
            'joint_5': -1.4147,
            'joint_6': 0.0,
            'cell_door_joint': 0.0
        }
        
        # Target positions from GUI sliders (start at nominal pose)
        self.target_positions = dict(self.initial_positions)
        # Current command values being sent to Gazebo
        self.current_positions = dict(self.initial_positions)
        
        # Smoothing alpha (0.18 at 50 Hz gives smooth industrial robot acceleration)
        self.alpha = 0.18
        
        # Create publishers for each joint command topic
        self.publishers_map = {}
        for name in self.joint_names:
            topic = f'/model/ventek_spot_welding_cell/joint/{name}/cmd_pos'
            self.publishers_map[name] = self.create_publisher(Float64, topic, 10)
        
        # Subscribe to /joint_states from joint_state_publisher_gui
        self.subscription = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_state_callback,
            10
        )
        
        # 50 Hz interpolation loop for ultra-smooth trajectory delivery to Gazebo
        self.timer = self.create_timer(1.0 / 50.0, self.smooth_publish_loop)
        
        self.get_logger().info('JointSliderSync initialized with 50 Hz motion smoothing.')
        self.get_logger().info(f'Initialized at nominal inspection pose: joint_1={self.initial_positions["joint_1"]:.3f}, joint_2={self.initial_positions["joint_2"]:.3f}, joint_3={self.initial_positions["joint_3"]:.3f}')

    def joint_state_callback(self, msg: JointState):
        name_pos = dict(zip(msg.name, msg.position))
        for joint_name in self.joint_names:
            if joint_name in name_pos:
                self.target_positions[joint_name] = float(name_pos[joint_name])

    def smooth_publish_loop(self):
        for name, pub in self.publishers_map.items():
            target = self.target_positions[name]
            current = self.current_positions[name]
            
            # Exponential moving average filter
            diff = target - current
            if abs(diff) < 0.0005:
                updated = target
            else:
                updated = current + self.alpha * diff
            
            self.current_positions[name] = updated
            
            cmd = Float64()
            cmd.data = float(updated)
            pub.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = JointSliderSync()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
