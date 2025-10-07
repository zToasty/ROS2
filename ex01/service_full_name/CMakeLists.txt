cmake_minimum_required(VERSION 3.8)
project(service_full_name)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclpy REQUIRED)
find_package(rosidl_default_generators REQUIRED)

# Генерируем интерфейсы
rosidl_generate_interfaces(${PROJECT_NAME}
  "srv/SummFullName.srv"
)

# Устанавливаем Python файлы
install(PROGRAMS
  src/service_node.py
  src/client_node.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
