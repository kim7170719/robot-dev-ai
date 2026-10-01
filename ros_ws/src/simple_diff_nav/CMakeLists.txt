cmake_minimum_required(VERSION 3.16)
project(simple_diff_nav)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY config launch maps
  DESTINATION share/${PROJECT_NAME}
)

install(
  PROGRAMS
    scripts/scan_sim.py
    scripts/odom_to_tf.py
  DESTINATION lib/${PROJECT_NAME}
)

install(
  FILES scripts/room_scan.py
  DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_cmake_pytest REQUIRED)
  ament_add_pytest_test(
    test_room_scan
    test/test_room_scan.py
    APPEND_ENV PYTHONPATH=${CMAKE_CURRENT_SOURCE_DIR}/scripts
  )
endif()

ament_package()
