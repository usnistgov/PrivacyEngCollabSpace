include(${CMAKE_CURRENT_LIST_DIR}/preamble.cmake)

message(STATUS "DROP_OT_THIRDPARTY_DIR=${DROP_OT_THIRDPARTY_DIR}")


set(PUSHED_CMAKE_PREFIX_PATH ${CMAKE_PREFIX_PATH})
set(CMAKE_PREFIX_PATH "${DROP_OT_THIRDPARTY_DIR};${CMAKE_PREFIX_PATH}")


#######################################
# CRYPTOTOOLS

macro(FIND_CRYPTOTOOLS)
    set(ARGS ${ARGN})
    set(COMP)
    
    if(DROP_OT_ENABLE_RELIC)
        set(COMP ${COMP} relic)
    else()
        #set(COMP ${COMP} no_relic)
    endif()
    if(DROP_OT_ENABLE_SODIUM)
        set(COMP ${COMP} sodium)
    else()
        #set(COMP ${COMP} no_sodium)
    endif()
    #if(DROP_OT_ENABLE_PIC)
    #    set(COMP ${COMP} pic)
    #else()
    #    set(COMP ${COMP} no_pic)
    #endif()
    message(STATUS "COMP=${COMP}")
    #explicitly asked to fetch CRYPTOTOOLS
    if(FETCH_CRYPTOTOOLS)
        list(APPEND ARGS NO_DEFAULT_PATH PATHS ${DROP_OT_THIRDPARTY_DIR})
    endif()
    
    find_package(cryptoTools ${ARGS} COMPONENTS ${COMP})

    if(TARGET oc::cryptoTools)
        set(CRYPTOTOOLS_FOUND ON)
    else()
        set(CRYPTOTOOLS_FOUND  OFF)
    endif()
endmacro()

if(DROP_OT_FETCH_CRYPTOTOOLS_AUTO)
    FIND_CRYPTOTOOLS(QUIET)
    include(${CMAKE_CURRENT_LIST_DIR}/../thirdparty/getCryptoTools.cmake)
endif()

FIND_CRYPTOTOOLS(REQUIRED)



#######################################
# diskhash

if(NOT EXISTS ${CMAKE_CURRENT_LIST_DIR}/../diskhash/Makefile)

    include(${CMAKE_CURRENT_LIST_DIR}/../thirdparty/getDiskHash.cmake)

endif()

# resort the previous prefix path
set(CMAKE_PREFIX_PATH ${PUSHED_CMAKE_PREFIX_PATH})
