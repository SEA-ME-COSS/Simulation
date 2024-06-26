cmake_minimum_required(VERSION 3.5)
project(sim)

if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 14)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()


find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(tf2 REQUIRED)


add_executable(sim_rviz_odom src/sim_rviz_odom.cpp)
ament_target_dependencies(sim_rviz_odom rclcpp nav_msgs tf2)


install(TARGETS
  sim_rviz_odom
  DESTINATION lib/${PROJECT_NAME})

install(DIRECTORY
  launch
  worlds
  description
  meshes
  models
  map
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
