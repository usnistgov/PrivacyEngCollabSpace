file(GLOB_RECURSE SRCS *.cpp)
#file(GLOB_RECURSE SRCS *.c)

include_directories(${CMAKE_SOURCE_DIR}/wrapper/)

add_library(wrapper SHARED ${SRCS})

target_link_libraries(wrapper diskhash dropOt)
