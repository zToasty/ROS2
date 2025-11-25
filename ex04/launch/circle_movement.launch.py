import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    pkg_gaz_circle = get_package_share_directory('gaz_circle_movement')
    pkg_pylesos_gazebo = get_package_share_directory('pylesos_gazebo')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    # Используем обновленный URDF (где есть плагины Gazebo)
    urdf_file = os.path.join(pkg_pylesos_gazebo, 'urdf', 'robot.gazebo.xacro')
    robot_desc = ParameterValue(Command(['xacro ', urdf_file]), value_type=str)

    # 1. Запуск Gazebo
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': '-r empty.sdf'}.items()
    )

    # 2. Robot State Publisher (Считает TF на основе joint_states)
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_desc,
            'use_sim_time': True
        }]
    )

    # 3. Спавн робота
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'pylesos_robot',
            '-topic', 'robot_description',
            '-x', '0.0', '-y', '0.0', '-z', '0.1'
        ],
        output='screen'
    )

    # 4. Bridge
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            # Команды скорости (ROS -> Gazebo)
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            
            # Одометрия (Gazebo -> ROS) - пригодится для TF base_link
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            
            # Глобальные TF (Gazebo -> ROS)
            '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            
            # Состояние суставов (Gazebo -> ROS) для колес
            '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model' 
        ],
        output='screen'
    )

    # 5. Узел для движения по кругу
    circle_movement = Node(
        package='gaz_circle_movement',
        executable='circle_movement',
        output='screen'
    )
    
    # 6. RViz
    rviz = Node(
       package='rviz2',
       executable='rviz2',
       parameters=[{'use_sim_time': True}]
    )

    return LaunchDescription([
        gz_sim,
        robot_state_publisher,
        spawn_entity,
        bridge,
        rviz, 
        # Запускаем движение через пару секунд, чтобы робот успел появиться
        TimerAction(period=3.0, actions=[circle_movement])
    ])