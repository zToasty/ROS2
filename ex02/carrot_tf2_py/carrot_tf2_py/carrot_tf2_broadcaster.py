import math
from geometry_msgs.msg import TransformStamped
import rclpy
from rclpy.node import Node
from tf2_ros import TransformBroadcaster
from tf_transformations import quaternion_from_euler

class CarrotTf2Broadcaster(Node):
    def __init__(self):
        super().__init__('carrot_tf2_broadcaster')
        self.tf_broadcaster = TransformBroadcaster(self)
        self.timer = self.create_timer(0.1, self.broadcast_carrot_frame)
        
        self.declare_parameter('radius', 2.0)
        self.declare_parameter('direction_of_rotation', 1)
        
        self.angle = 0.0
        
    def broadcast_carrot_frame(self):
        radius = self.get_parameter('radius').get_parameter_value().double_value
        direction = self.get_parameter('direction_of_rotation').get_parameter_value().integer_value
        
        self.angle += 0.1 * direction
        
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'turtle1'
        t.child_frame_id = 'carrot'
        
        t.transform.translation.x = radius * math.cos(self.angle)
        t.transform.translation.y = radius * math.sin(self.angle)
        t.transform.translation.z = 0.0
        
        q = quaternion_from_euler(0, 0, 0)
        t.transform.rotation.x = q[0]
        t.transform.rotation.y = q[1]
        t.transform.rotation.z = q[2]
        t.transform.rotation.w = q[3]
        
        self.tf_broadcaster.sendTransform(t)

def main():
    rclpy.init()
    node = CarrotTf2Broadcaster()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    rclpy.shutdown()

if __name__ == '__main__':
    main()