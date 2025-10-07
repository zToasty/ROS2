#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

from service_full_name.srv import SummFullName

class FullNameService(Node):
    def __init__(self):
        super().__init__('service_name')
        self.srv = self.create_service(SummFullName, 'SummFullName', self.summ_full_name_callback)
        self.get_logger().info('Full Name Service started')

    def summ_full_name_callback(self, request, response):
        response.full_name = f"{request.last_name} {request.name} {request.first_name}"
        self.get_logger().info(f'Received: {request.last_name} {request.name} {request.first_name}')
        self.get_logger().info(f'Sending: {response.full_name}')
        return response

def main(args=None):
    rclpy.init(args=args)
    node = FullNameService()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
