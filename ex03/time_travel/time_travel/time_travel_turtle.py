import math
from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node
from tf2_ros import TransformException, Buffer, TransformListener
from rclpy.duration import Duration


class TimeTravelTurtle(Node):

    def __init__(self):
        super().__init__('time_travel_turtle')

        self.declare_parameter('delay', 5.0)
        self.delay = self.get_parameter('delay').get_parameter_value().double_value

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.publisher = self.create_publisher(Twist, '/turtle2/cmd_vel', 1)

        self.timer = self.create_timer(0.1, self.on_timer)

        self.get_logger().info(f'Started time travel node with delay={self.delay:.1f}s')

    def on_timer(self):
        try:
            lookup_time = self.get_clock().now() - Duration(seconds=self.delay)
            past_transform = self.tf_buffer.lookup_transform(
                'world', 'turtle1', lookup_time.to_msg(), timeout=Duration(seconds=0.5))

            current_transform = self.tf_buffer.lookup_transform(
                'world', 'turtle2', rclpy.time.Time().to_msg(), timeout=Duration(seconds=0.5))

        except TransformException as ex:
            self.get_logger().warn(f'Cannot lookup transform: {ex}')
            return

        dx = past_transform.transform.translation.x - current_transform.transform.translation.x
        dy = past_transform.transform.translation.y - current_transform.transform.translation.y

        distance = math.sqrt(dx**2 + dy**2)

        # === ориентация turtle2 ===
        def quaternion_to_yaw(q):
            siny_cosp = 2 * (q.w * q.z + q.x * q.y)
            cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
            return math.atan2(siny_cosp, cosy_cosp)

        current_yaw = quaternion_to_yaw(current_transform.transform.rotation)
        angle_to_target = math.atan2(dy, dx)
        angle_error = math.atan2(math.sin(angle_to_target - current_yaw),
                                math.cos(angle_to_target - current_yaw))

        # === Пропорциональное управление ===
        msg = Twist()
        msg.linear.x = 2.0 * distance
        msg.angular.z = 6.0 * angle_error

        # ограничим макс скорости
        msg.linear.x = max(min(msg.linear.x, 3.0), -3.0)
        msg.angular.z = max(min(msg.angular.z, 4.0), -4.0)

        self.publisher.publish(msg)



def main():
    rclpy.init()
    node = TimeTravelTurtle()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    rclpy.shutdown()


if __name__ == '__main__':
    main()
