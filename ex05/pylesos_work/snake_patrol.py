import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import math
from tf_transformations import euler_from_quaternion

class SnakePatrol(Node):
    def __init__(self):
        super().__init__('snake_patrol')
        
        # Паблишер для управления
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        # Сабскрайбер для одометрии (чтобы знать, где мы)
        self.subscription = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        

        self.waypoints = [
            (10.0, 0.0),  # Едем вправо до упора
            (10.0, 2.0),  # Смещаемся вверх
            (0.0,  2.0),  # Едем влево обратно
            (0.0,  4.0),  # Смещаемся еще выше
            (10.0, 4.0),  # Снова вправо
            (10.0, 6.0),
            (0.0,  6.0),
            (0.0,  8.0),
            (10.0, 8.0),
            (10.0, 10.0), # Финал комнаты
            (0.0,  10.0), # Возврат в левый верхний угол
            (0.0,  0.0)   # Домой
        ]
        
        self.current_point = 0 # Индекс текущей цели
        
        # Текущее положение робота
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0 # Угол поворота
        
        # Таймер цикла управления (10 раз в секунду)
        self.timer = self.create_timer(0.1, self.control_loop)

    def odom_callback(self, msg):
        # Получаем координаты
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y
        
        # Получаем кватернионы
        rot = msg.pose.pose.orientation
        
    
        (roll, pitch, yaw) = euler_from_quaternion([rot.x, rot.y, rot.z, rot.w])
        
        self.yaw = yaw 

    def control_loop(self):
        # Если цель достигнута, переключаемся на следующую
        target_x, target_y = self.waypoints[self.current_point]
        
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        cmd = Twist()
        
        
        if distance < 0.2:
            self.get_logger().info(f'Point {self.current_point} reached!')
            self.current_point = (self.current_point + 1) % len(self.waypoints)
            # Остановимся на мгновение
            self.publisher_.publish(Twist())
            return

        # Вычисляем нужный угол к цели
        target_angle = math.atan2(dy, dx)
        angle_diff = target_angle - self.yaw
        
        # Нормализация угла (чтобы робот не крутился лишний раз через 360)
        while angle_diff > math.pi: angle_diff -= 2 * math.pi
        while angle_diff < -math.pi: angle_diff += 2 * math.pi

        
        if abs(angle_diff) > 0.1:
            # Если смотрим не туда — поворачиваемся на месте
            cmd.linear.x = 0.0
            cmd.angular.z = max(min(angle_diff * 2.0, 1.0), -1.0)
        else:
            # Если смотрим примерно на цель — ГАЗУЕМ ГАЗУ ГАЗУ
            cmd.linear.x = 0.5  
            cmd.angular.z = angle_diff * 0.5 

        self.publisher_.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = SnakePatrol()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()