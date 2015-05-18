cmake_minimum_required(VERSION 2.8)

project(swig-libindinodejs)

#paths
set(CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake_modules/")

#swig
find_package(SWIG REQUIRED)
include(${SWIG_USE_FILE})

#Nodejs
find_package(Nodejs REQUIRED)
include_directories(${NODE_INCLUDE_DIRS})

#INDI
#set(INDI_SRC_DIR "/home/geehale/svnprojects/sourceforge/indi-code/libindi")
#include_directories(${INDI_SRC_DIR})
find_package(INDI)
include_directories(${INDI_INCLUDE_DIR})
find_package(CFITSIO)
include_directories(${CFITSIO_INCLUDE_DIR})

include_directories(${CMAKE_CURRENT_SOURCE_DIR})

#Build
set(CMAKE_SWIG_FLAGS "-c++" "-Wall" "-v" "-node")

#SET_SOURCE_FILES_PROPERTIES(baseclient.i PROPERTIES CPLUSPLUS ON)
#SET_SOURCE_FILES_PROPERTIES(baseclient.i PROPERTIES SWIG_FLAGS "-includeall")
#SWIG_ADD_MODULE(indiclienttcl tcl baseclient.i ${INDI_SRC_DIR}/libs/indibase/baseclient.cpp)

# INDI::Baseclient is abstract, so SWIG does not generate constructor
#SET_SOURCE_FILES_PROPERTIES(baseclient.i PROPERTIES CPLUSPLUS ON)
#SWIG_ADD_MODULE(indiclienttcl tcl baseclient.i)

# Create a BaseClient derived class which implements every virtual methods 
SET_SOURCE_FILES_PROPERTIES(indiclientnodejs.i PROPERTIES CPLUSPLUS ON)
SET_SOURCE_FILES_PROPERTIES(baseclientimpl.cpp PROPERTIES CPLUSPLUS ON)
#SET_SOURCE_FILES_PROPERTIES(indidriverpython.i PROPERTIES CPLUSPLUS ON)
#set_property(SOURCE indiclientphp.i PROPERTY SWIG_FLAGS "-fPIC")
#SET_SOURCE_FILES_PROPERTIES(tclclient.cpp PROPERTIES CPLUSPLUS ON)
SWIG_ADD_MODULE(indiclientnodejs javascript baseclientimpl.cpp indiclientnodejs.i)
#SWIG_ADD_MODULE(PyIndiDriver python indidriverpython.i)

SWIG_LINK_LIBRARIES(indiclientnodejs ${NODE_LIBRARIES} ${INDI_CLIENT_LIBRARIES} -lindi -lz)
#SWIG_LINK_LIBRARIES(PyIndiDriver ${PYTHON_LIBRARIES} ${CFITSIO_LIBRARIES} ${INDI_DRIVER_LIBRARIES} ${INDI_CLIENT_LIBRARIES} -lstdc++ -lindi -lz)

set_target_properties (indiclientnodejs PROPERTIES
  COMPILE_FLAGS "${CMAKE_CXX_FLAGS} -DBUILDING_NODE_EXTENSION -DSWIGJAVASCRIPT=${SWIG_FOUND}"
  PREFIX ""
  OUTPUT_NAME indiclientnodejs
  SUFFIX ".node"
)

macro (indiclientnodejs_CREATE_INSTALL_PACKAGE_JSON generated_file install_location)
  configure_file (${generated_file}.cmake ${CMAKE_CURRENT_BINARY_DIR}/${generated_file} @ONLY)
  install (FILES ${CMAKE_CURRENT_BINARY_DIR}/${generated_file} DESTINATION ${install_location})
endmacro (indiclientnodejs_CREATE_INSTALL_PACKAGE_JSON)
indiclientnodejs_create_install_package_json (package.json lib/node_modules/indiclientnodejs)

macro (indiclientnodejs_CREATE_BINDING_GYP generated_file)
  set (indiclientnodejs_LIB_SRCS_GYP "")
  foreach (srcfile ${indiclientnodejs_LIB_SRCS_NOAUTO})
    file (RELATIVE_PATH rel ${CMAKE_SOURCE_DIR} ${srcfile})
    set (indiclientnodejs_LIB_SRCS_GYP "'${rel}',\n${indiclientnodejs_LIB_SRCS_GYP}")
  endforeach (srcfile)
  foreach (includedir ${indiclientnodejs_LIB_INCLUDE_DIRS})
    file (RELATIVE_PATH rel ${CMAKE_SOURCE_DIR} ${includedir})
    set (indiclientnodejs_LIB_INCLUDE_DIRS_GYP "'${rel}',\n${indiclientnodejs_LIB_INCLUDE_DIRS_GYP}")
  endforeach (includedir)
  configure_file (${generated_file}.cmake ${CMAKE_CURRENT_BINARY_DIR}/${generated_file} @ONLY)
endmacro (indiclientnodejs_CREATE_BINDING_GYP)
indiclientnodejs_create_binding_gyp (binding.gyp)

add_custom_target (npmpkg)
add_custom_command (TARGET npmpkg POST_BUILD COMMAND ${CMAKE_COMMAND} -E copy
        ${CMAKE_CURRENT_BINARY_DIR}/indiclientnodejsJAVASCRIPT_wrap.cxx ${CMAKE_SOURCE_DIR}/src
        COMMAND ${CMAKE_COMMAND} -E copy
        ${CMAKE_BINARY_DIR}/src/version.c ${CMAKE_SOURCE_DIR}/src
        COMMAND ${CMAKE_COMMAND} -E copy
        ${CMAKE_CURRENT_BINARY_DIR}/package.json ${CMAKE_SOURCE_DIR}
        COMMAND sed -i "'s/indiclientnodejs.node/build\\/Release\\/indiclientnodejs.node/'"
        ${CMAKE_SOURCE_DIR}/package.json
        COMMAND ${CMAKE_COMMAND} -E copy
        ${CMAKE_CURRENT_BINARY_DIR}/binding.gyp ${CMAKE_SOURCE_DIR}
        COMMAND ${CMAKE_COMMAND} -E copy
        ${CMAKE_SOURCE_DIR}/docs/npm.md ${CMAKE_SOURCE_DIR}/READMEFIRST)
add_dependencies (npmpkg indiclientnodejsjs)

install (FILES ${CMAKE_CURRENT_BINARY_DIR}/indiclientnodejs.node
         DESTINATION lib/node_modules/indiclientnodejs)
#execute_process(COMMAND python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()" OUTPUT_VARIABLE PYTHON_SITE_PACKAGES OUTPUT_STRIP_TRAILING_WHITESPACE)
#install(TARGETS _PyIndi DESTINATION ${PYTHON_SITE_PACKAGES})
#install(FILES ${CMAKE_BINARY_DIR}/PyIndi.py DESTINATION ${PYTHON_SITE_PACKAGES})
#install(TARGETS _PyIndiDriver DESTINATION ${PYTHON_SITE_PACKAGES})
#install(FILES ${CMAKE_BINARY_DIR}/PyIndiDriver.py DESTINATION ${PYTHON_SITE_PACKAGES})
