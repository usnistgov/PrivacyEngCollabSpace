
if("${CMAKE_CURRENT_SOURCE_DIR}" STREQUAL "${CMAKE_SOURCE_DIR}")

	############################################
	#          If top level cmake              #
	############################################
	if(MSVC)
	else()
		set(COMMON_FLAGS "-Wall -Wfatal-errors")

		if(NOT DEFINED NO_ARCH_NATIVE)
			set(COMMON_FLAGS "${COMMON_FLAGS} -march=native")
		endif()

		SET(CMAKE_CXX_FLAGS_RELEASE "-O3  -DNDEBUG")
		SET(CMAKE_CXX_FLAGS_RELWITHDEBINFO " -O2 -g -ggdb")
		SET(CMAKE_CXX_FLAGS_DEBUG  "-O0 -g -ggdb")
		#set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS}  -std=c++17")
		
	endif()



	set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${COMMON_FLAGS}")
	set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${COMMON_FLAGS}")
	

	############################################
	#           Build mode checks              #
	############################################

	# Set a default build type for single-configuration
	# CMake generators if no build type is set.
	if(NOT CMAKE_CONFIGURATION_TYPES AND NOT CMAKE_BUILD_TYPE)
	   SET(CMAKE_BUILD_TYPE Release)
	endif()

	if(    NOT "${CMAKE_BUILD_TYPE}" STREQUAL "Release"
       AND NOT "${CMAKE_BUILD_TYPE}" STREQUAL "Debug"
       AND NOT "${CMAKE_BUILD_TYPE}" STREQUAL "RelWithDebInfo" )

        message(WARNING ": Unknown build type - \${CMAKE_BUILD_TYPE}=${CMAKE_BUILD_TYPE}.  Please use one of Debug, Release, or RelWithDebInfo. e.g. call\n\tcmake . -DCMAKE_BUILD_TYPE=Release\n" )
	endif()
endif()

if(MSVC)
    set(DROP_OT_CONFIG_NAME "${CMAKE_BUILD_TYPE}")
    if("${DROP_OT_CONFIG_NAME}" STREQUAL "RelWithDebInfo" OR "${DROP_OT_CONFIG_NAME}" STREQUAL "")
        set(DROP_OT_CONFIG_NAME "Release")
	endif()
    set(DROP_OT_CONFIG "x64-${DROP_OT_CONFIG_NAME}")
elseif(APPLE)
    set(DROP_OT_CONFIG "osx")
else()
    set(DROP_OT_CONFIG "linux")
endif()

if(EXISTS ${CMAKE_CURRENT_LIST_DIR}/install.cmake)
	set(DROP_OT_IN_BUILD_TREE ON)
else()
	set(DROP_OT_IN_BUILD_TREE OFF)
endif()

if(DROP_OT_IN_BUILD_TREE)

    # we currenty are in the vole psi source tree, vole-psi/cmake
	if(NOT DEFINED DROP_OT_BUILD_DIR)
		set(DROP_OT_BUILD_DIR "${CMAKE_CURRENT_LIST_DIR}/../out/build/${DROP_OT_CONFIG}")
		get_filename_component(DROP_OT_BUILD_DIR ${DROP_OT_BUILD_DIR} ABSOLUTE)
	endif()

	if(NOT (${CMAKE_BINARY_DIR} STREQUAL ${DROP_OT_BUILD_DIR}))
		message(WARNING "incorrect build directory. \n\tCMAKE_BINARY_DIR=${CMAKE_BINARY_DIR}\nbut expect\n\tDROP_OT_BUILD_DIR=${DROP_OT_BUILD_DIR}")
	endif()

	if(NOT DEFINED DROP_OT_THIRDPARTY_DIR)
		set(DROP_OT_THIRDPARTY_DIR "${CMAKE_CURRENT_LIST_DIR}/../out/install/${DROP_OT_CONFIG}")
		get_filename_component(DROP_OT_THIRDPARTY_DIR ${DROP_OT_THIRDPARTY_DIR} ABSOLUTE)
	endif()
else()
    # we currenty are in install tree, <install-prefix>/lib/cmake/vole-psi
	if(NOT DEFINED DROP_OT_THIRDPARTY_DIR)
		set(DROP_OT_THIRDPARTY_DIR "${CMAKE_CURRENT_LIST_DIR}/../../..")
		get_filename_component(DROP_OT_THIRDPARTY_DIR ${DROP_OT_THIRDPARTY_DIR} ABSOLUTE)
	endif()
endif()

