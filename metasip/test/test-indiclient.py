import sys
import time
import logging

import ctypes
try:
     ctypes.CDLL('libindi.so.0',  ctypes.RTLD_GLOBAL)
except OSError:
     print('libindi.so library not found. Please check the LD_LIBRARY_PATH environment variable')
     print('   export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/path/to/libindi.so')
     sys.exit(1)

import PyIndi

class IndiClient(PyIndi.INDI.BaseClient):
    def __init__(self):
        super(IndiClient, self).__init__()
        self.logger = logging.getLogger('PyQtIndi.IndiClient')
        self.logger.info('creating an instance of PyQtIndi.IndiClient')
    def newDevice(self, d):
        self.logger.info("new device " + d.getDeviceName())
    def newProperty(self, p):
        self.logger.info("new property "+ p.getName() + " for device "+ p.getDeviceName())
    def removeProperty(self, p):
        self.logger.info("remove property "+ p.getName() + " for device "+ p.getDeviceName())
    def newBLOB(self, bp):
        self.logger.info("new BLOB "+ bp.name.decode())
    def newSwitch(self, svp):
        self.logger.info ("new Switch "+ svp.name.decode() + " for device "+ svp.device.decode())
    def newNumber(self, nvp):
        self.logger.info("new Number "+ nvp.name.decode() + " for device "+ nvp.device.decode())
    def newText(self, tvp):
        self.logger.info("new Text "+ tvp.name.decode() + " for device "+ tvp.device.decode())
    def newLight(self, lvp):
        self.logger.info("new Light "+ lvp.name.decode() + " for device "+ lvp.device.decode())
    def newMessage(self, d, m):
        self.logger.info("new Message "+ d.messageQueue(m).decode())
    def serverConnected(self):
        print("Server connected ("+self.getHost()+":"+str(self.getPort())+")")
    def serverDisconnected(self, code):
        self.logger.info("Server disconnected (exit code = "+str(code)+","+str(self.getHost())+":"+str(self.getPort())+")")

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

indiclient=IndiClient()

indiclient.setServer("localhost",7624)
print("Connecting and waiting 2secs")
if (not(indiclient.connectServer())):
     print("No indiserver running on "+indiclient.getHost()+":"+str(indiclient.getPort())+" - Try to run")
     print("  indiserver indi_simulator_telescope indi_simulator_ccd")
     sys.exit(1)
time.sleep(1)
print("List of devices")
dl=indiclient.getDevices()
for dev in dl:
    print(dev.getDeviceName())
    
print("Connecting to Telescope Simulator")
d=indiclient.getDevice("Telescope Simulator")
lp=d.getProperties()
for p in lp:
    print(p.getName())

drivertvp=d.getProperty("DRIVER_INFO")
for t in drivertvp.getText().tp:
    print(t.name+"("+t.label+")="+t.text)

porttvp=d.getProperty("DEVICE_PORT")
for t in porttvp.getText().tp:
    print(t.name+"="+t.text)

indiclient.sendNewText("Telescope Simulator", "DEVICE_PORT", "PORT", "/dev/ttyS0")
for t in porttvp.getText().tp:
    print(t.name+"="+t.text)
time.sleep(2)
#print("Connecting again to Telescope Simulator")
#indiclient.connectDevice("Telescope Simulator")
print("Disconnecting  Telescope Simulator")
indiclient.disconnectDevice("Telescope Simulator")
r=input("End?")
print("Disconnecting server")
# The listenINDI thread remains blocked in the select syscall, even if the main thread has written
# in the socketpair and closed the server socket. The main thread blocks in the pthread_join.
# Actually the Indiclient should be run in a separate thread than the main Python thread
indiclient.disconnectServer()
print("Exiting")
sys.exit(0)
