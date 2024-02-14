
project(dropOt)


#############################################
#              Build dropOt                 #
#############################################

file(GLOB_RECURSE SRCS *.cpp)
 

add_library(dropOt ${SRCS})

target_include_directories(dropOt PUBLIC 
                    $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}/..>
                    $<INSTALL_INTERFACE:include>) 
target_include_directories(dropOt PUBLIC 
                    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/..>
                    $<INSTALL_INTERFACE:include>) 


target_link_libraries(dropOt oc::cryptoTools)



if(MSVC)
    target_compile_options(dropOt PUBLIC $<$<COMPILE_LANGUAGE:CXX>:/std:c++${DROP_OT_STD_VER}>)
    
else()
    target_compile_options(dropOt PUBLIC $<$<COMPILE_LANGUAGE:CXX>:-std=c++${DROP_OT_STD_VER}> -pthread)
endif()
