#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
import math
import sys

class MoveToGoal(Node):
    def __init__(self, target_x, target_y, target_theta):
        super().__init__('move_to_goal')
        
        self.target_x = target_x
        self.target_y = target_y
        self.target_theta = target_theta
        
        self.current_pose = Pose()
        self.reached_goal = False
        
        # Публикуем команды скорости
        self.cmd_vel_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        
        # Подписываемся на позицию черепахи
        self.pose_sub = self.create_subscription(
            Pose, 
            '/turtle1/pose', 
            self.pose_callback, 
            10
        )
        
        # Таймер для управления
        self.timer = self.create_timer(0.1, self.control_loop)
        
        self.get_logger().info(f'Moving to goal: x={target_x}, y={target_y}, theta={target_theta}')
        
    def pose_callback(self, msg):
        self.current_pose = msg
        
    def control_loop(self):
        if self.reached_goal:
            return
            
        # Вычисляем ошибку позиции
        dx = self.target_x - self.current_pose.x
        dy = self.target_y - self.current_pose.y
        distance = math.sqrt(dx**2 + dy**2)
        
        # Вычисляем желаемый угол
        target_angle = math.atan2(dy, dx)
        angle_error = target_angle - self.current_pose.theta
        
        # Нормализуем угол ошибки в диапазон [-pi, pi]
        while angle_error > math.pi:
            angle_error -= 2 * math.pi
        while angle_error < -math.pi:
            angle_error += 2 * math.pi
            
        cmd_vel = Twist()
        
        # Если далеко от цели - сначала поворачиваем, потом едем
        if distance > 0.1:
            if abs(angle_error) > 0.1:  # Сначала выравниваем угол
                cmd_vel.angular.z = 0.5 * angle_error
            else:  # Затем едем вперед
                cmd_vel.linear.x = 0.5 * distance
        else:
            # Достигли позиции, теперь выравниваем финальный угол
            theta_error = self.target_theta - self.current_pose.theta
            while theta_error > math.pi:
                theta_error -= 2 * math.pi
            while theta_error < -math.pi:
                theta_error += 2 * math.pi
                
            if abs(theta_error) > 0.05:
                cmd_vel.angular.z = 0.5 * theta_error
            else:
                # Цель достигнута!
                cmd_vel.linear.x = 0.0
                cmd_vel.angular.z = 0.0
                self.reached_goal = True
                self.get_logger().info('Goal reached!')
                self.timer.cancel()  # Останавливаем таймер
                rclpy.shutdown()  # Завершаем работу узла
                return
        
        # Ограничиваем максимальную скорость
        cmd_vel.linear.x = max(min(cmd_vel.linear.x, 2.0), -2.0)
        cmd_vel.angular.z = max(min(cmd_vel.angular.z, 2.0), -2.0)
        
        self.cmd_vel_pub.publish(cmd_vel)

def main(args=None):
    rclpy.init(args=args)
    
    if len(sys.argv) != 4:
        print("Usage: ros2 run move_to_goal move_to_goal <x> <y> <theta>")
        print("Example: ros2 run move_to_goal move_to_goal 5.0 5.0 0.0")
        return 1
    
    try:
        target_x = float(sys.argv[1])
        target_y = float(sys.argv[2]) 
        target_theta = float(sys.argv[3])
    except ValueError:
        print("Error: All parameters must be numbers")
        return 1
    
    node = MoveToGoal(target_x, target_y, target_theta)
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

