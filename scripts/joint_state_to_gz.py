#!/usr/bin/env python3
"""
VENTEK Autonomous Welding - Joint State to Gazebo Command Bridge
Subscribes to:
- /joint_states (sensor_msgs/JointState from joint_state_publisher_gui)

Publishes to:
- /model/ventek_welding_cell/joint/joint_a1/cmd_pos .. joint_a6/cmd_pos (std_msgs/Float64)
which are forwarded to Gazebo Sim's JointPositionController plugins via ros_gz_bridge.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64


class JointStateToGzBridge(Node):
    def __init__(self):
        super().__init__('joint_state_to_gz_bridge')

        self.joint_names = [f'joint_a{i}' for i in range(1, 7)]
        self.pubs = {}
        for name in self.joint_names:
            topic = f'/model/ventek_welding_cell/joint/{name}/cmd_pos'
            self.pubs[name] = self.create_publisher(Float64, topic, 10)

        self.sub = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_state_callback,
            10
        )

        self.get_logger().info('JointState -> Gazebo Bridge active.')
        self.get_logger().info(f'Forwarding joints: {self.joint_names}')

    def joint_state_callback(self, msg: JointState):
        name_to_pos = dict(zip(msg.name, msg.position))
        for name in self.joint_names:
            if name in name_to_pos:
                cmd = Float64()
                cmd.data = float(name_to_pos[name])
                self.pubs[name].publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = JointStateToGzBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
