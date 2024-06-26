import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
import launch_ros.actions

import xacro


def generate_launch_description():
    robot_file = "piracer.xacro"
    package_name = "sim"
    world_file_name = "map.world"
    map_file_name = "map.yaml"

    pkg_path = os.path.join(get_package_share_directory(package_name))
    pkg_gazebo_ros = FindPackageShare(package='gazebo_ros').find('gazebo_ros')

    xacro_file = os.path.join(pkg_path, "description", robot_file)
    world_path = os.path.join(pkg_path, "worlds", world_file_name)
    map_path = os.path.join(pkg_path, "map", map_file_name)

    # Start Gazebo server
    start_gazebo_server_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py')),
        launch_arguments={'world': world_path}.items()
    )

    # Start Gazebo client    
    start_gazebo_client_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py'))
    )

    # Robot State Publisher
    doc = xacro.parse(open(xacro_file))
    xacro.process_doc(doc)
    robot_description = {'robot_description': doc.toxml()}
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description]
    )

    # Spawn entity
    spawn_entity = Node(
        package='gazebo_ros', 
        executable='spawn_entity.py',
        output='screen',
        arguments=['-topic', 'robot_description', '-entity', 'piracer'],
    )

    return LaunchDescription(
        [
            start_gazebo_server_cmd,
            start_gazebo_client_cmd,
            robot_state_publisher_node,
            spawn_entity,
            Node(
                package='tf2_ros',
                executable='static_transform_publisher',
                arguments = ['0', '0', '0', '0', '0', '0', 'map', 'odom']
            ),
            Node(
                package='sim',
                executable='sim_rviz_odom',
                output='screen',
            ),
            Node(
                package='nav2_map_server',
                executable='map_server',
                output='screen',
                parameters=[{'yaml_filename': map_path}]
            ),
            launch_ros.actions.Node(
                package='nav2_lifecycle_manager',
                executable='lifecycle_manager',
                name='map_lifecycle_manager',  # unique name
                output='screen',
                emulate_tty=True,
                parameters=[{'use_sim_time': True},
                            {'autostart': True},
                            {'node_names': ['map_server']}]
            ),
        ]
    )
