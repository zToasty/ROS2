import math
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster
import numpy as np


def euler_to_quaternion(roll: float, pitch: float, yaw: float):
    """Конвертация Эйлера → Кватернион (аналог tf_transformations.quaternion_from_euler)."""
    roll, pitch, yaw = roll / 2.0, pitch / 2.0, yaw / 2.0
    cr, sr = math.cos(roll), math.sin(roll)
    cp, sp = math.cos(pitch), math.sin(pitch)
    cy, sy = math.cos(yaw), math.sin(yaw)

    qx = sp * cr * cy - cp * sr * sy
    qy = cp * sr * cy + sp * cr * sy
    qz = cp * cr * sy - sp * sr * cy
    qw = cp * cr * cy + sp * sr * sy
    return qx, qy, qz, qw


class TurtleTFBroadcaster(Node):
    """Рассылает TF-фреймы для всех заданных черепах."""

    def __init__(self):
        super().__init__('turtle_tf_broadcaster')

        self.tf_broadcaster = TransformBroadcaster(self)
        self.turtles = ['turtle1', 'turtle2', 'turtle3']

        for name in self.turtles:
            topic = f'/{name}/pose'
            self.create_subscription(Pose, topic, self._make_pose_callback(name), 10)

        self.get_logger().info(f"🐢 TF broadcaster запущен для: {', '.join(self.turtles)}")

    def _make_pose_callback(self, turtle_name: str):
        """Создаёт callback под конкретную черепаху."""
        def callback(msg: Pose):
            t = TransformStamped()
            t.header.stamp = self.get_clock().now().to_msg()
            t.header.frame_id = 'world'
            t.child_frame_id = turtle_name
            t.transform.translation.x = msg.x
            t.transform.translation.y = msg.y
            t.transform.translation.z = 0.0

            qx, qy, qz, qw = euler_to_quaternion(0, 0, msg.theta)
            t.transform.rotation.x = qx
            t.transform.rotation.y = qy
            t.transform.rotation.z = qz
            t.transform.rotation.w = qw

            self.tf_broadcaster.sendTransform(t)
        return callback


def main():
    rclpy.init()
    node = TurtleTFBroadcaster()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
