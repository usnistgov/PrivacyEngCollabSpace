
project(frontend)


#############################################
#               Build frontend               #
#############################################

file(GLOB_RECURSE SRC_FRONTEND ${CMAKE_SOURCE_DIR}/frontend/*.cpp)
include_directories(${CMAKE_SOURCE_DIR}/frontend/)

add_executable(frontend ${SRC_FRONTEND})

target_link_libraries(frontend diskhash)
target_link_libraries(frontend dropOt)
