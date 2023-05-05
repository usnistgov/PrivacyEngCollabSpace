
macro(EVAL var)
     if(${ARGN})
         set(${var} ON)
     else()
         set(${var} OFF)
     endif()
endmacro()

option(DROP_OT_FETCH_AUTO      "automatically download and build dependencies" OFF)
option(DROP_OT_ENABLE_SSE      "build with sse" ON)
option(DROP_OT_ENABLE_AVX      "build with avx" ON)
option(DROP_OT_ENABLE_PIC      "build with PIC" OFF)
option(DROP_OT_ENABLE_ASAN     "build with asan" OFF)
option(DROP_OT_ENABLE_RELIC    "build with Relic" ON)
option(DROP_OT_ENABLE_SODIUM   "build with Sodium" OFF)

if(NOT DEFINED DROP_OT_STD_VER)
    set(DROP_OT_STD_VER 14)
endif()

#option(DROP_OT_FETCH_CRYPTOTOOLS		"download and build CRYPTOTOOLS" OFF))
EVAL(DROP_OT_FETCH_CRYPTOTOOLS_AUTO 
	(DEFINED DROP_OT_FETCH_CRYPTOTOOLS AND DROP_OT_FETCH_CRYPTOTOOLS) OR
	((NOT DEFINED DROP_OT_FETCH_CRYPTOTOOLS) AND (DROP_OT_FETCH_AUTO)))
    


message(STATUS "dropOt options\n=======================================================")

message(STATUS "Option: DROP_OT_FETCH_AUTO        = ${DROP_OT_FETCH_AUTO}")
message(STATUS "Option: DROP_OT_FETCH_CRYPTOTOOLS = ${DROP_OT_FETCH_CRYPTOTOOLS}")
message(STATUS "Option: DROP_OT_ENABLE_SSE        = ${DROP_OT_ENABLE_SSE}")
message(STATUS "Option: DROP_OT_ENABLE_AVX        = ${DROP_OT_ENABLE_AVX}")
message(STATUS "Option: DROP_OT_ENABLE_PIC        = ${DROP_OT_ENABLE_PIC}")
message(STATUS "Option: DROP_OT_ENABLE_ASAN       = ${DROP_OT_ENABLE_ASAN}")
message(STATUS "Option: DROP_OT_ENABLE_RELIC      = ${DROP_OT_ENABLE_RELIC}")
message(STATUS "Option: DROP_OT_ENABLE_SODIUM     = ${DROP_OT_ENABLE_SODIUM}")
message(STATUS "Option: DROP_OT_STD_VER           = ${DROP_OT_STD_VER}\n")


