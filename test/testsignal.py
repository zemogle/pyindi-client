#Test Inheritance with Qt: Ok
from PyQt4 import QtCore

class A:
    def f(self):
        print("in A: f")

class B(A, QtCore.QObject):
    trigger=QtCore.pyqtSignal(int, int)
    def __init__(self):
        A.__init__(self)
        QtCore.QObject.__init__(self)
        self.value=123
    def g(self):
        print("in B; g")
    def s(self, i):
        self.trigger.emit(self.value, i)

def handletrigger(n, i):
    print("Signalling trigger n="+str(n)+" i="+str(i))

b=B()
b.f()
b.g()

b.trigger.connect(handletrigger)

b.s(15)

#Test inheritance with QT and PyIndi: Problem with signals c not a QObject
import PyQtIndi

import PyIndi

class C(PyIndi.INDI.BaseClient, QtCore.QObject):
    newdevice=QtCore.pyqtSignal(PyIndi.INDI.BaseDevice)
    def __init(self):
        PyIndi.INDI.BaseClient.__init__()
        QtCore.QObject.__init__()
    def h(self):
        print("in C; h")
    def newDevice(self, d):
        #print("new device " + d.getDeviceName().decode())
        self.newdevice.emit(d)

c=C()
c.h()
print(C.__mro__)

#Using Delegation without signalling

class IndiClient(PyIndi.INDI.BaseClient):
    def __init__(self):
        super(IndiClient, self).__init__()
        self.logger = logging.getLogger('PyQtIndi.IndiClient')
        self.logger.info('creating an instance of PyQtIndi.IndiClient')
    def newDevice(self, d):
        self.logger.info("new device " + d.getDeviceName().decode())
        #self.newdevice.emit(d)
    def newProperty(self, p):
        self.logger.info("new property "+ p.getName().decode() + " for device "+ p.getDeviceName().decode())
        #self.newproperty.emit(p)
    def removeProperty(self, p):
        self.logger.info("remove property "+ p.getName().decode() + " for device "+ p.getDeviceName().decode())
        #self.removeproperty.emit(p)
    def newBLOB(self, bp):
        self.logger.info("new BLOB "+ bp.name.decode())
        #self.newblob.emit(bp)
    def newSwitch(self, svp):
        self.logger.info ("new Switch "+ svp.name.decode() + " for device "+ svp.device.decode())
        #self.newswitch.emit(svp)
    def newNumber(self, nvp):
        self.logger.info("new Number "+ nvp.name.decode() + " for device "+ nvp.device.decode())
        #self.newnumber.emit(nvp)
    def newText(self, tvp):
        self.logger.info("new Text "+ tvp.name.decode() + " for device "+ tvp.device.decode())
        #self.newtext.emit(tvp)
    def newLight(self, lvp):
        self.logger.info("new Light "+ lvp.name.decode() + " for device "+ lvp.device.decode())
        #self.newlight.emit(lvp)
    def newMessage(self, d, m):
        self.logger.info("new Message "+ d.messageQueue(m).decode())
        #self.newmessage.emit(d, m)
    def serverConnected(self):
        print("Server connected ("+self.getHost().decode()+":"+str(self.getPort())+")")
        #self.serverconnected.emit()
    def serverDisconnected(self, code):
        self.logger.info("Server disconnected (exit code = "+str(code)+","+str(self.getHost())+":"+str(self.getPort())+")")
        #self.serverdisconnected.emit(code)


class C(QtCore.QObject):
    newdevice=QtCore.pyqtSignal(PyIndi.INDI.BaseDevice)
    def __init__(self):
        super(C,self).__init__()
        self.__client=IndiClient()
    def __getattr__(self, name):
        return getattr(self.__client, name)

def handlernewdevice(d):
    print("Signalling new device "+d.getName().decode())

c=C()
c.newdevice.connect(handlernewdevice) #Ok

#Using Delegation with signalling
import sys
import logging

from PyQt4 import QtCore

import ctypes
try:
     ctypes.CDLL('libindi.so.0',  ctypes.RTLD_GLOBAL)
except OSError:
     print('libindi.so library not found. Please check the LD_LIBRARY_PATH environment variable')
     print('   export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/path/to/libindi.so')
     sys.exit(1)

import PyIndi

class IndiClient(PyIndi.INDI.BaseClient):
    def __init__(self, delegate):
        super(IndiClient, self).__init__()
        self.delegate=delegate
#        print(self.delegate.newdevice)
        self.logger = logging.getLogger('PyQtIndi.IndiClient')
        self.logger.info('creating an instance of PyQtIndi.IndiClient')
#    def connectServer(self):
#        print("Oh oh connect server")
    def newDevice(self, d):
        self.logger.info("new device " + d.getDeviceName().decode()+" signalling "+str(self.delegate.newdevice))
        #self.delegate.emit(PyQt4.QtCore.PYSIGNAL("newdevice(PyIndi.INDI.BaseDevice)"), d)
        try:
            self.delegate.newdevice.emit(d)
        except:
            self.logger.info("Can't emit newdevice signal")
        #self.delegate.emitnewdevice(d)
    def newProperty(self, p):
        self.logger.info("new property "+ p.getName().decode() + " for device "+ p.getDeviceName().decode())
        self.delegate.newproperty.emit(p)
    def removeProperty(self, p):
        self.logger.info("remove property "+ p.getName().decode() + " for device "+ p.getDeviceName().decode())
        self.delegate.removeproperty.emit(p)
    def newBLOB(self, bp):
        self.logger.info("new BLOB "+ bp.name.decode())
        self.delegate.newblob.emit(bp)
    def newSwitch(self, svp):
        self.logger.info ("new Switch "+ svp.name.decode() + " for device "+ svp.device.decode())
        self.delegate.newswitch.emit(svp)
    def newNumber(self, nvp):
        self.logger.info("new Number "+ nvp.name.decode() + " for device "+ nvp.device.decode())
        self.delegate.newnumber.emit(nvp)
    def newText(self, tvp):
        self.logger.info("new Text "+ tvp.name.decode() + " for device "+ tvp.device.decode())
        self.delegate.newtext.emit(tvp)
    def newLight(self, lvp):
        self.logger.info("new Light "+ lvp.name.decode() + " for device "+ lvp.device.decode())
        self.delegate.newlight.emit(lvp)
    def newMessage(self, d, m):
        self.logger.info("new Message "+ d.messageQueue(m).decode())
        self.delegate.newmessage.emit(d, m)
    def serverConnected(self):
        self.logger.info("Server connected ("+self.getHost().decode()+":"+str(self.getPort())+")")
        self.delegate.serverconnected.emit()
    def serverDisconnected(self, code):
        self.logger.info("Server disconnected (exit code = "+str(code)+","+self.getHost().decode()+":"+str(self.getPort())+")")
        self.delegate.serverdisconnected.emit(code)

class PyQtIndiClient(QtCore.QObject):
    newdevice=QtCore.pyqtSignal(PyIndi.INDI.BaseDevice)
    newproperty=QtCore.pyqtSignal(PyIndi.INDI.Property)
    removeproperty=QtCore.pyqtSignal(PyIndi.INDI.Property)
    newblob=QtCore.pyqtSignal(PyIndi.IBLOB)
    newswitch=QtCore.pyqtSignal(PyIndi._ISwitchVectorProperty)
    newnumber=QtCore.pyqtSignal(PyIndi._INumberVectorProperty)
    newtext=QtCore.pyqtSignal(PyIndi._ITextVectorProperty)
    newlight=QtCore.pyqtSignal(PyIndi._ILightVectorProperty)
    newmessage=QtCore.pyqtSignal(PyIndi.INDI.BaseDevice, int)
    serverconnected=QtCore.pyqtSignal()
    serverdisconnected=QtCore.pyqtSignal(int)
    def __init__(self):
        super(PyQtIndiClient,self).__init__()
        self.client=IndiClient(self)
    def __getattr__(self, name):
        return getattr(self.client, name)
    def emitnewdevice(self, d):
        self.newdevice.emit(d)

# A QThread is needed to receive Qt signals
# We first create a receiver object which will be move to a new QThread
# See http://www.christeck.de/wp/2010/10/23/the-great-qthread-mess/
class Receiver(QtCore.QObject):
    finish=QtCore.pyqtSignal()
    @QtCore.pyqtSlot(PyIndi.INDI.BaseDevice)
    def handlernewdevice(self, d):
        logging.info("Signalling new device "+d.getDeviceName().decode())
    @QtCore.pyqtSlot(PyIndi.INDI.Property)
    def handlernewproperty(self, p):
        print("Signalling new property "+p.getName().decode()+" for device "+p.getDeviceName().decode())

# A QApplication is needed to sart QThreading 
from PyQt4 import QtGui
from PyQt4.QtGui import QApplication

simapp=QtGui.QApplication(sys.argv)

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
indiclient=PyQtIndiClient()

receiver=Receiver()
indiclient.newdevice.connect(receiver.handlernewdevice)
indiclient.newproperty.connect(receiver.handlernewproperty)
receiverthread=QtCore.QThread()
receiver.moveToThread(receiverthread)
receiverthread.start()

indiclient.setServer(b"localhost", 7624)
indiclient.connectServer()

#Tracing
import sys
import trace

tracer = trace.Trace(
    ignoredirs=[sys.prefix, sys.exec_prefix],
    trace=1, count=1, countfuncs=1, countcallers=1)

tracer.run("indiclient.connectServer()")
r = tracer.results()
r.write_results(show_missing=True, coverdir="/tmp/r/")
