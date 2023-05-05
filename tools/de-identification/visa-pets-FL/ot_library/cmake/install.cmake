


#############################################
#            Install                        #
#############################################


configure_file("${CMAKE_CURRENT_LIST_DIR}/findDependancies.cmake" "findDependancies.cmake" COPYONLY)

# make cache variables for install destinations
include(GNUInstallDirs)
include(CMakePackageConfigHelpers)


# generate the config file that is includes the exports
configure_package_config_file(
  "${CMAKE_CURRENT_LIST_DIR}/Config.cmake.in"
  "${CMAKE_CURRENT_BINARY_DIR}/dropOtConfig.cmake"
  INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/dropOt
  NO_SET_AND_CHECK_MACRO
  NO_CHECK_REQUIRED_COMPONENTS_MACRO
)

if(NOT DEFINED dropOt_VERSION_MAJOR)
    message("\n\n\n\n warning, dropOt_VERSION_MAJOR not defined ${dropOt_VERSION_MAJOR}")
endif()

set_property(TARGET dropOt PROPERTY VERSION ${dropOt_VERSION})

# generate the version file for the config file
write_basic_package_version_file(
  "${CMAKE_CURRENT_BINARY_DIR}/dropOtConfigVersion.cmake"
  VERSION "${dropOt_VERSION_MAJOR}.${dropOt_VERSION_MINOR}.${dropOt_VERSION_PATCH}"
  COMPATIBILITY AnyNewerVersion
)

# install the configuration file
install(FILES
          "${CMAKE_CURRENT_BINARY_DIR}/dropOtConfig.cmake"
          "${CMAKE_CURRENT_BINARY_DIR}/dropOtConfigVersion.cmake"
          "${CMAKE_CURRENT_BINARY_DIR}/findDependancies.cmake"
        DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/dropOt
)

# install library
install(
    TARGETS dropOt
    DESTINATION ${CMAKE_INSTALL_LIBDIR}
    EXPORT dropOtTargets)

# install headers
install(
    DIRECTORY "${CMAKE_CURRENT_LIST_DIR}/../dropOt"
    DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}/"
    FILES_MATCHING PATTERN "*.h")

# install config
install(EXPORT dropOtTargets
  FILE dropOtTargets.cmake
  DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/dropOt
       NAMESPACE visa::
)
 export(EXPORT dropOtTargets
       FILE "${CMAKE_CURRENT_BINARY_DIR}/dropOtTargets.cmake"
       NAMESPACE visa::
)