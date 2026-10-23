cmake_minimum_required(VERSION 3.8)
project(ventek_cell_description)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)

# Install directories to share
install(
  DIRECTORY config launch meshes urdf worlds
  DESTINATION share/${PROJECT_NAME}
)

# Install model.config and package.xml
install(
  FILES model.config package.xml
  DESTINATION share/${PROJECT_NAME}
)

# Install executable scripts
install(
  PROGRAMS
    scripts/joint_slider_sync.py
    scripts/view_realsense_feed.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
