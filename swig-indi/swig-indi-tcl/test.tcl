#!/bin/tclsh
#run indiserver indi_simlator_ccd for testing

load ./libindiclienttcl.so

TclIndiClient c

c setServer "localhost" 7624
c connectServer

set devs [c getDevices]
# problem here: devs seems to be a TCL list but lindex $devs 0 is the same object as devs
# getDevices returns a ref on a std::vector: SWIG leaves it as is rather than building a TCL list
#for {set devindex 0} {$devindex < [llength $devs]} {incr devindex} {
#    set device [$devs get $devindex]
#    puts [$device getDeviceName]
#}


c connectDevice "CCD Simulator"
set ccd [c getDevice "CCD Simulator"]
$ccd isConnected
set expo [$ccd getProperty "CCD_EXPOSURE"]
$expo getDeviceName
set nvexpo [$expo getNumber]
$nvexpo cget -name
set nexp [$nvexpo cget -np]

set ccdinfo [$ccd getProperty "CCD_INFO"]
set nvinfo [$ccdinfo getNumber]
set ninfo [$nvinfo cget -np]
#problem here: np contains 6 numbers but SWIG dereferences this pointer so we have access to only first number
  
# should take an exposure, to be checked with kstars, as the blob image is forgotten here
c sendNewNumber "CCD Simulator" "CCD_EXPOSURE" "CCD_EXPOSURE_VALUE" 1.0