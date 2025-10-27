import math
from geometry_msgs.msg import TransformStamped
import rclpy
from rclpy.node import Node
from tf2_ros import TransformBroadcaster
from turtlesim.msg import Pose
from tf_transformations import quaternion_from_euler

class TurtleTf2Broadcaster(Node):
    def __init__(self):
        super().__init__('turtle_tf2_broadcaster')
        
        # Получаем имя черепахи из параметра
        self.declare_parameter('turtle_name', 'turtle1')
        turtle_name = self.get_parameter('turtle_name').get_parameter_value().string_value
        
        self.tf_broadcaster = TransformBroadcaster(self)
        
        # Подписываемся на topic позы черепахи
        self.subscription = self.create_subscription(
            Pose,
            f'/{turtle_name}/pose',
            self.handle_turtle_pose,
            10)
        
        self.get_logger().info(f'Starting TF broadcaster for {turtle_name}')
        
    def handle_turtle_pose(self, msg):
        # Получаем имя черепахи из параметра каждый раз (на случай изменения)
        turtle_name = self.get_parameter('turtle_name').get_parameter_value().string_value
        
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'world'
        t.child_frame_id = turtle_name
        
        t.transform.translation.x = msg.x
        t.transform.translation.y = msg.y
        t.transform.translation.z = 0.0
        
        q = quaternion_from_euler(0, 0, msg.theta)
        t.transform.rotation.x = q[0]
        t.transform.rotation.y = q[1]
        t.transform.rotation.z = q[2]
        t.transform.rotation.w = q[3]
        
        self.tf_broadcaster.sendTransform(t)
        self.get_logger().info(f'Published transform for {turtle_name}', throttle_duration_sec=5)

def main():
    rclpy.init()
    node = TurtleTf2Broadcaster()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    rclpy.shutdown()

if __name__ == '__main__':
    main()