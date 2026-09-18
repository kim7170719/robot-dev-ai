cmake_minimum_required(VERSION 3.16)
project(simple_diff_robot)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY urdf config launch rviz
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
