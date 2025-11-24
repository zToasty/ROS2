import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    pkg_pylesos_work = get_package_share_directory('pylesos_work') # Твой текущий пакет
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    # Используем твой URDF (старый, проверенный)
    # Если захочешь новую модель - просто поменяй путь здесь
    urdf_file = os.path.join(pkg_pylesos_work, 'urdf', 'robot.gazebo.xacro')
    robot_desc = ParameterValue(Command(['xacro ', urdf_file]), value_type=str)

    # Запуск Gazebo
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': '-r empty.sdf'}.items()
    )

    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_desc, 'use_sim_time': True}]
    )

    # Spawn Robot
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-name', 'snake_robot', '-topic', 'robot_description', '-z', '0.1'],
        output='screen'
    )

    # 5. Bridge (Полный, проверенный)
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock', # ФИКС: Время
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            
            # Одометрия (должна приходить с DiffDrive)
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            
            # TF (от OdometryPublisher его теперь нет, используем TF от DiffDrive)
            '/tf_diff_drive@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V', 
            
            '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model'
        ],
        output='screen'
    )

    # НАШ НОВЫЙ СКРИПТ (ЗМЕЙКА)
    snake_patrol = Node(
        package='pylesos_work', # Имя пакета
        executable='snake_patrol',
        output='screen',
        parameters=[{'use_sim_time': True}] # Важно для синхронизации времени
    )

    # RViz (опционально)
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
        # Запускаем змейку через 5 секунд, чтобы робот успел прогрузиться
        TimerAction(period=5.0, actions=[snake_patrol])
    ])