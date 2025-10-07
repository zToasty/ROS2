import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from action_cleaning_robot_interfaces.action import CleaningTask

class CleaningActionClient(Node):

    def __init__(self):
        super().__init__('cleaning_action_client')
        self._client = ActionClient(self, CleaningTask, 'cleaning_task')
        self.results = []

    def send_goal(self, task_type, area_size=0.0, target_x=0.0, target_y=0.0):
        goal_msg = CleaningTask.Goal()
        goal_msg.task_type = task_type
        goal_msg.area_size = area_size
        goal_msg.target_x = target_x
        goal_msg.target_y = target_y

        self._client.wait_for_server()
        self.get_logger().info(f'Sending goal: {task_type} (area_size: {area_size})')
        
        # Синхронная отправка цели
        future = self._client.send_goal_async(goal_msg, feedback_callback=self.feedback_cb)
        rclpy.spin_until_future_complete(self, future)
        
        if not future.result().accepted:
            self.get_logger().info('Goal rejected')
            return

        self.get_logger().info('Goal accepted')
        result_future = future.result().get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        
        result = result_future.result().result
        self.results.append(result)
        self.get_logger().info(f'Task completed: Success={result.success}, '
                            f'Points={result.cleaned_points}, Distance={result.total_distance:.2f}')

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected')
            return

        self.get_logger().info('Goal accepted')
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        result = future.result().result
        self.results.append(result)
        self.get_logger().info(f'Task completed: Success={result.success}, '
                              f'Points={result.cleaned_points}, Distance={result.total_distance:.2f}')

    def feedback_cb(self, feedback_msg):
        feedback = feedback_msg.feedback
        self.get_logger().info(f'Progress: {feedback.progress_percent}% | '
                              f'Points: {feedback.current_cleaned_points} | '
                              f'Position: ({feedback.current_x:.2f}, {feedback.current_y:.2f})')

def main(args=None):
    rclpy.init(args=args)
    client = CleaningActionClient()

    tasks = [
        ('clean_square', 3.0, 0.0, 0.0),
        ('return_home', 0.0, 1.0, 1.0),
        ('clean_square', 5.0, 0.0, 0.0),
    ]

    for task in tasks:
        client.send_goal(*task)

    # Вывод итоговой статистики
    client.get_logger().info("=== CLEANING COMPLETED ===")
    total_points = sum(r.cleaned_points for r in client.results)
    total_distance = sum(r.total_distance for r in client.results)
    client.get_logger().info(f"Total points cleaned: {total_points}")
    client.get_logger().info(f"Total distance traveled: {total_distance:.2f}")

    client.destroy_node()
    rclpy.shutdown()
