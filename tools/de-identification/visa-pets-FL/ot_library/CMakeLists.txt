cmake_minimum_required (VERSION 3.15)
project(dropOt VERSION 0.5.0)

include(cmake/preamble.cmake)
include(cmake/buildOptions.cmake)
include(cmake/findDependancies.cmake)

message(STATUS "Option: CMAKE_BUILD_TYPE = ${CMAKE_BUILD_TYPE}\n\tRelease\n\tDebug\n\tRELWITHDEBINFO")
message(STATUS "        cryptoTools_INC  = ${cryptoTools_INC}")
message(STATUS "        cryptoTools_LIB  = ${cryptoTools_LIB}")
message(STATUS "        ENABLE_BOOST     = ${ENABLE_BOOST}\n\n")

configure_file(drop-ot/config.h.in drop-ot/config.h)

add_subdirectory(drop-ot)
add_subdirectory(frontend)
add_subdirectory(wrapper)
add_subdirectory(diskhash)


include(cmake/install.cmake)