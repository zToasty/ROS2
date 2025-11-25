#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import math

class CircleMovement(Node):
    def __init__(self):
        super().__init__('circle_movement')
        
        self.linear_speed = 1.0  # м/с
        self.angular_speed = 0.8  # рад/с
        
        self.cmd_vel_publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.timer_callback)
        
        self.get_logger().info('Circle movement node started!')
        self.get_logger().info(f'Linear: {self.linear_speed} m/s, Angular: {self.angular_speed} rad/s')

    def timer_callback(self):
        """Публикует команды для движения по кругу"""
        msg = Twist()
        msg.linear.x = self.linear_speed
        msg.angular.z = self.angular_speed
        
        self.cmd_vel_publisher.publish(msg)
        self.get_logger().info(f'Publishing cmd_vel: linear={msg.linear.x:.2f}, angular={msg.angular.z:.2f}', throttle_duration_sec=2)

def main(args=None):
    rclpy.init(args=args)
    
    node = CircleMovement()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Stopping robot...')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()