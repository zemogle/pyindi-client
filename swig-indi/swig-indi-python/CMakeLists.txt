cmake_minimum_required(VERSION 2.8)

project(swig-libindipython)

#paths
set(CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake_modules/")

#swig
find_package(SWIG REQUIRED)
include(${SWIG_USE_FILE})

#PHP
find_package(PythonLibs REQUIRED)
include_directories(${PYTHON_INCLUDE_DIRS})

#INDI
#set(INDI_SRC_DIR "/home/geehale/svnprojects/sourceforge/indi-code/libindi")
#include_directories(${INDI_SRC_DIR})
find_package(INDI)
include_directories(${INDI_INCLUDE_DIR})

include_directories(${CMAKE_CURRENT_SOURCE_DIR})

#Build
set(CMAKE_SWIG_FLAGS "-c++" "-Wall" "-v" "-threads")

#SET_SOURCE_FILES_PROPERTIES(baseclient.i PROPERTIES CPLUSPLUS ON)
#SET_SOURCE_FILES_PROPERTIES(baseclient.i PROPERTIES SWIG_FLAGS "-includeall")
#SWIG_ADD_MODULE(indiclienttcl tcl baseclient.i ${INDI_SRC_DIR}/libs/indibase/baseclient.cpp)

# INDI::Baseclient is abstract, so SWIG does not generate constructor
#SET_SOURCE_FILES_PROPERTIES(baseclient.i PROPERTIES CPLUSPLUS ON)
#SWIG_ADD_MODULE(indiclienttcl tcl baseclient.i)

# Create a BaseClient derived class which implements every virtual methods 
SET_SOURCE_FILES_PROPERTIES(indiclientpython.i PROPERTIES CPLUSPLUS ON)
#set_property(SOURCE indiclientphp.i PROPERTY SWIG_FLAGS "-fPIC")
#SET_SOURCE_FILES_PROPERTIES(tclclient.cpp PROPERTIES CPLUSPLUS ON)
SWIG_ADD_MODULE(PyIndi python indiclientpython.i)

SWIG_LINK_LIBRARIES(PyIndi ${PYTHON_LIBRARIES} ${INDI_CLIENT_LIBRARIES} -lindi -lz)

execute_process(COMMAND python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()" OUTPUT_VARIABLE PYTHON_SITE_PACKAGES OUTPUT_STRIP_TRAILING_WHITESPACE)
install(TARGETS _PyIndi DESTINATION ${PYTHON_SITE_PACKAGES})
install(FILES ${CMAKE_BINARY_DIR}/PyIndi.py DESTINATION ${PYTHON_SITE_PACKAGES})