#!/usr/bin/env python3
import sys
import rclpy
from rclpy.node import Node

from service_full_name.srv import SummFullName

class FullNameClient(Node):
    def __init__(self):
        super().__init__('client_name')
        self.cli = self.create_client(SummFullName, 'SummFullName')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service not available, waiting...')

    def send_request(self, last_name, name, first_name):
        request = SummFullName.Request()
        request.last_name = last_name
        request.name = name
        request.first_name = first_name
        
        self.future = self.cli.call_async(request)
        rclpy.spin_until_future_complete(self, self.future)
        return self.future.result()

def main(args=None):
    rclpy.init(args=args)
    
    if len(sys.argv) != 4:
        print("Usage: ros2 run service_full_name client_name <last_name> <name> <first_name>")
        return 1
    
    client = FullNameClient()
    response = client.send_request(sys.argv[1], sys.argv[2], sys.argv[3])
    
    if response is not None:
        print(f"Full name: {response.full_name}")
    else:
        print("Service call failed")
        return 1
    
    client.destroy_node()
    rclpy.shutdown()
    return 0

if __name__ == '__main__':
    main()
