#!/usr/bin/python -d
 
import sys
import time
import logging
import mutex
import thread

from PyQt4 import QtCore, QtGui, QtXml
from PyKDE4.kdecore import KStandardDirs
from pyqtindigui import Ui_PyQtIndi
from drivermanagergui import Ui_DriverManager
from indihostconfgui import Ui_INDIHostConf
from blobgui import Ui_BlobForm
from treemodelIndi import IndiItemDelegate, IndiModel, Node, ServerNode, DeviceNode, PropertyNode
from modeltest import ModelTest
from defaultviewer import DefaultViewer

import ctypes
try:
     ctypes.CDLL('libindi.so.0',  ctypes.RTLD_GLOBAL)
except OSError:
     print('libindi.so library not found. Please check the LD_LIBRARY_PATH environment variable')
     print('   export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/path/to/libindi.so')
     sys.exit(1)
import PyIndi

class IndiClient(PyIndi.INDI.BaseClient):
    def __init__(self, server):
        super(IndiClient, self).__init__()
        self.logger = logging.getLogger('PyQtIndi.IndiClient')
        self.logger.info('creating an instance of PyQtIndi.IndiClient')
        self.server=server
    def newDevice(self, d):
        self.logger.info("new device " + d.getDeviceName())
        #self.server.devices[d.getDeviceName()]=Device(d, self.server)
        self.server.newdevice.emit(d)
    def newProperty(self, p):
        self.logger.info("new property "+ p.getName() + " for device "+ p.getDeviceName())
        #d=self.server.devices[p.getDeviceName()]
        #d.properties[p.getName()]=IndiProperty(p,d)
        self.server.newproperty.emit(p)
    def removeProperty(self, p):
        self.logger.info("remove property "+ p.getName() + " for device "+ p.getDeviceName())
        dev=self.server.devices[p.getDeviceName()]
        grp=dev.groups[p.getGroupName()]
        prop=grp.properties[p.getName()]
        #self.server.mutexdevices.lock(self.server.handlerRemoveProperty, p)
        # Property p is removed in the client just after the signal is emitted, thus losing p
        # emitting a signal would require much more complex synchronization
        #self.server.removeproperty.emit(p)
        self.server.removeproperty.emit(prop)
    def newBLOB(self, bp):
        self.logger.info("new BLOB "+ bp.name.decode())
        p=bp.bvp
        bpnames=[k.name for k in p.bp]
        index=bpnames.index(bp.name)
        pname=p.name
        dname=p.device
        gname=p.group
        device=self.server.devices[dname]
        group=device.groups[gname]
        theproperty=group.properties[pname]
        self.server.newblob.emit(device, theproperty, index)
    def newSwitch(self, svp):
        self.logger.info ("new Switch "+ svp.name.decode() + " for device "+ svp.device.decode())
        self.server.newswitch.emit(svp)
    def newNumber(self, nvp):
        self.logger.info("new Number "+ nvp.name.decode() + " for device "+ nvp.device.decode())
        self.server.newnumber.emit(nvp)
    def newText(self, tvp):
        self.logger.info("new Text "+ tvp.name.decode() + " for device "+ tvp.device.decode())
        self.server.newtext.emit(tvp)
    def newLight(self, lvp):
        self.logger.info("new Light "+ lvp.name.decode() + " for device "+ lvp.device.decode())
        self.server.newlight.emit(lvp)
    def newMessage(self, d, m):
        self.logger.info("new Message "+ d.messageQueue(m).decode())
        self.server.newmessage.emit(d, m)
    def serverConnected(self):
        self.logger.info("Server connected ("+self.getHost()+":"+str(self.getPort())+")")
        self.server.isConnected=True
        self.server.serverconnected.emit()
    def serverDisconnected(self, code):
        self.logger.info("Server disconnected (exit code = "+str(code)+","+str(self.getHost())+":"+str(self.getPort())+")")
        self.server.isConnected=False
        self.server.serverdisconnected.emit(code)

class Device(QtCore.QObject):
  def __init__(self, indidevice, server):
    QtCore.QObject.__init__(self)
    self.name=indidevice.getDeviceName()
    self.device=indidevice
    self.server=server
    self.node=None
    self.groups=dict()
    self.properties=dict()


class Group(QtCore.QObject):
  def __init__(self, groupname, indidevice):
    QtCore.QObject.__init__(self)
    self.name=groupname
    self.device=indidevice
    self.node=None
    self.properties=dict()

class IndiProperty(QtCore.QObject):
  def __init__(self, indiproperty, indidevice, group):
    QtCore.QObject.__init__(self)
    self.name=indiproperty.getName()
    self.label=indiproperty.getLabel()
    if not self.label or self.label=="":
         self.label=self.name
    self.indiproperty=indiproperty
    self.device=indidevice
    self.group=group
    #self.server=server
    self.node=None
    self.handlerwidget=None
    #self.properties=dict()

class Server(QtCore.QObject):
  newdevice=QtCore.pyqtSignal(PyIndi.INDI.BaseDevice)
  newproperty=QtCore.pyqtSignal(PyIndi.INDI.Property)
  removeproperty=QtCore.pyqtSignal(IndiProperty)
  #newblob=QtCore.pyqtSignal(PyIndi._IBLOBVectorProperty, int)
  newblob=QtCore.pyqtSignal(Device, IndiProperty, int)
  newswitch=QtCore.pyqtSignal(PyIndi._ISwitchVectorProperty)
  newnumber=QtCore.pyqtSignal(PyIndi._INumberVectorProperty)
  newtext=QtCore.pyqtSignal(PyIndi._ITextVectorProperty)
  newlight=QtCore.pyqtSignal(PyIndi._ILightVectorProperty)
  newmessage=QtCore.pyqtSignal(PyIndi.INDI.BaseDevice, int)
  serverconnected=QtCore.pyqtSignal()
  serverdisconnected=QtCore.pyqtSignal(int)

  def __init__(self, host, port, name):
    QtCore.QObject.__init__(self)
    self.host=host
    self.port=port
    self.name=name
    self.indiclient=None
    self.isConnected=False
    self.node=None
    self.devices=dict()
    #self.mutexdevices=mutex.mutex()

  def handlerMessage(self, device, mnum):
       pyqtindi.ui.textBrowserMessages.insertPlainText(device.messageQueue(mnum)+"("+device.getDeviceName()+"@"+self.name+")\n")

  def handlerDevice(self, device):
    d=Device(device, self)
    self.devices[device.getDeviceName()]=d
    l=self.devices.keys()
    l.sort()
    position=l.index(device.getDeviceName())
    indimodel.insertDevice(position, self, d)
    #self.mutexdevices.unlock()

  def handlerProperty(self, indiproperty):
    device=self.devices[indiproperty.getDeviceName()]
    groupname=indiproperty.getGroupName()
    if not groupname:
         groupname=""
    group=None
    if not groupname in device.groups:
         group=Group(groupname, device)
         device.groups[groupname]=group
         g=[gn for gn in device.groups.keys()]
         g.sort()
         gposition=g.index(groupname)
         indimodel.insertGroup(gposition, device, group)
    else:
         group=device.groups[groupname]
    p=IndiProperty(indiproperty,device, group)
    #group.properties[indiproperty.getName()]=p
    group.properties[p.name]=p
    #l=device.properties.keys()
    l= [d.label for d in group.properties.values()]
    l.sort()
    #position=l.index(indiproperty.getLabel())
    position=l.index(p.label)
    indimodel.insertProperty(position, group, p)
    #self.mutexdevices.unlock()

  def handlerRemoveProperty(self, theproperty):
       pyqtindi.ui.treeViewServer.selectionModel().clearSelection()
       pyqtindi.ui.treeViewServer.selectionModel().setCurrentIndex(QtCore.QModelIndex(), QtGui.QItemSelectionModel.NoUpdate)
       group=theproperty.group
       device=theproperty.device
    #l=device.properties.keys()
       l= [d.label for d in group.properties.values()]
       l.sort()
       position=l.index(theproperty.label)
       print("Handler Thread "+str(thread.get_ident())+" handlerRemoveProperty: "+theproperty.name+" at "+str(position)+" among "+str(len(l)))
       indimodel.removeProperty(position, group, theproperty)
       theproperty.node=None
       print("Handler Thread "+str(thread.get_ident())+" handlerRemoveProperty: "+theproperty.name+" removed from group "+group.name)
       del group.properties[theproperty.name]
       if len(group.properties) == 0:
            g=[gn for gn in device.groups.keys()]
            g.sort()
            gposition=g.index(group.name)
            print("Handler Thread "+str(thread.get_ident())+" handlerRemoveProperty: removing group "+group.name+" at "+str(gposition)+" from device "+device.name)
            indimodel.removeGroup(gposition, device, group)
            group.node=None
            del device.groups[group.name]
       #self.mutexdevices.unlock()

  def handlerBlob(self, device, theproperty, index):
       if not theproperty.handlerwidget:
            theproperty.handlerwidget=BlobForm(device, theproperty, index)
            theproperty.subwindow=pyqtindi.ui.mdiArea.addSubWindow(theproperty.handlerwidget)
            theproperty.handlerwidget.show()
       theproperty.handlerwidget.updateBLOB()

  def makeConnections(self):
    self.serverconnected.connect(lambda: indimodel.insertServer(0, self))
    self.serverdisconnected.connect(lambda(code): indimodel.removeServer(self))
    #self.newdevice.connect(lambda(device):self.mutexdevices.lock(self.handlerDevice, device))
    #self.newproperty.connect(lambda(indiproperty):self.mutexdevices.lock(self.handlerProperty, indiproperty)) 
    #self.removeproperty.connect(lambda(indiproperty):self.mutexdevices.lock(self.handlerRemoveProperty, indiproperty)) 
    self.newdevice.connect(self.handlerDevice)
    self.newproperty.connect(self.handlerProperty) 
    self.removeproperty.connect(self.handlerRemoveProperty) 
    self.newmessage.connect(self.handlerMessage)
    self.newblob.connect(self.handlerBlob)


class XmlIndiHostHandler(QtXml.QXmlDefaultHandler):
  def __init__(self, dm):
    QtXml.QXmlDefaultHandler.__init__(self)
    self.dm=dm
  def startElement(self, ns, localname, qname, attrs):
    if (localname == "INDIHost"):
      newserver = Server(attrs.value("hostname"), attrs.value("port").toInt()[0], attrs.value("name"))
      newserver.makeConnections()
      self.dm.servers[(attrs.value("hostname"), attrs.value("port").toInt()[0])] = newserver
      item = QtGui.QTreeWidgetItem(self.dm.ui.clientTreeWidget)
      item.setIcon(0, self.dm.ui.disconnectedicon)
      item.setText(1, attrs.value("name"))
      item.setText(2, attrs.value("port"))

    return True  

class BlobForm(QtGui.QWidget):
  def __init__(self, device, theproperty, index, parent=None):
    QtGui.QWidget.__init__(self, parent)
    self.ui = Ui_BlobForm()
    self.ui.setupUi(self)
    self.device=device
    self.property=theproperty
    self.blobindex=index
    self.indibvp=self.property.indiproperty.getBLOB()
    self.blob=self.indibvp.bp[self.blobindex]
    self.setWindowTitle("BLOB - " + self.property.label+self.property.name+" from "+ self.device.name+"@"+self.device.server.name)
    self.viewer=DefaultViewer(self.blob, self.ui.widgetViewer)

  def updateBLOB(self):
    self.isCompressed=False
    blobformat=self.blob.format.lower()
    print("updateBLOB: format "+blobformat)
    if blobformat.endswith(".z"):
         self.isCompressed=True
    self.ui.labelTypeValue.setText(self.blob.format)  
    if self.isCompressed:
         self.ui.checkBoxCompressed.setCheckState(QtCore.Qt.Checked)
    else:
         self.ui.checkBoxCompressed.setCheckState(QtCore.Qt.Unchecked)
    self.ui.labelSizeValue.setText(str(self.blob.size)+" bytes")
    self.ui.labelLenValue.setText(str(self.blob.bloblen)+" bytes")
    timestamp=self.indibvp.timestamp
    if timestamp and timestamp!="":
         self.ui.labelTimeStampValue.setText(timestamp)
    else:
         self.ui.labelTimeStampValue.setText("None")
    self.viewer.update()

class DriverManager(QtGui.QWidget):
  def __init__(self, parent=None):
    QtGui.QWidget.__init__(self, parent)
    self.servers=dict()
    self.ui = Ui_DriverManager()
    self.ui.setupUi(self)
    self.ui.connectedicon=QtGui.QIcon("network-transmit-receive")
    self.ui.disconnectedicon=QtGui.QIcon("network-offline")
    self.loadSetup()
    QtCore.QObject.connect(self.ui.addB, QtCore.SIGNAL("clicked()"), self.addINDIHost)    
    QtCore.QObject.connect(self.ui.modifyB, QtCore.SIGNAL("clicked()"), self.modifyINDIHost)    
    QtCore.QObject.connect(self.ui.removeB, QtCore.SIGNAL("clicked()"), self.removeINDIHost)    
    QtCore.QObject.connect(self.ui.connectHostB, QtCore.SIGNAL("clicked()"), self.activateHostConnection)    
    QtCore.QObject.connect(self.ui.disconnectHostB, QtCore.SIGNAL("clicked()"), self.activateHostDisconnection)    
    #QtCore.QObject.connect(self.ui.clientTreeWidget, QtCore.SIGNAL("itemClicked(QTreeWidgetItem, int)"), self.connectServer)    

  def loadSetup(self):
    indihostfile=QtCore.QFile(KStandardDirs.locate("data", "kstars/indihosts.xml"))
    #print(indihostfile.fileName())
    if ((indihostfile.size() == 0) or not(indihostfile.open(QtCore.QIODevice.ReadOnly))):
      return
    handler=XmlIndiHostHandler(self)
    xmlreader=QtXml.QXmlSimpleReader()
    xmlreader.setContentHandler(handler)
    xmlreader.setErrorHandler(handler)
    source=QtXml.QXmlInputSource(indihostfile)
    ok=xmlreader.parse(source, True)
    #while (source.data() != ""):
      #source.reset()
      #ok=xmlreader.parseContinue()
    #xmlreader=QtCore.QXmlStreamReader(indihostfile)
    #ok=True
    #while not(xmlreader.atEnd()):
    #  xmlreader.readNext()
    #  if xmlreader.isStartElement():
    #    print("xml token name " + xmlreader.name().toString())
    #if xmlreader.hasError():
    #  ok=False
    if not(ok):
      print("Failed to load indihosts setup")

  def addINDIHost(self):
    hostConfDialog = QtGui.QDialog()
    hostconf = Ui_INDIHostConf()
    hostconf.setupUi(hostConfDialog)
    hostConfDialog.setWindowTitle("Add Host")
    if (hostConfDialog.exec_() == QtGui.QDialog.Accepted):
      (port, portOk) = hostconf.portnumber.text().toInt()
      if not portOk:
          qmessage=QtGui.QMessageBox()
          qmessage.setText(tr("Error: the port number is invalid."))
          qmessage.exec_()
          return
      if (hostconf.hostname.text(), port) in self.servers:
          qmessage=QtGui.QMessageBox()
          qmessage.setText(tr("Host: " + hostconf.hostname.text() +" Port: " + port + " already exists."))
          qmessage.exec_()
          return
      newserver = Server(hostconf.hostname.text(), port, hostconf.nameIN.text())
      newserver.makeConnections()
      self.servers[(hostconf.hostname.text(), port)] = newserver
      item = QtGui.QTreeWidgetItem(self.ui.clientTreeWidget)
      item.setIcon(0, self.ui.disconnectedicon)
      item.setText(1, hostconf.nameIN.text())
      item.setText(2, hostconf.portnumber.text())

  def modifyINDIHost(self):
    print("modify")
  def removeINDIHost(self):
    print("remove")
  def activateHostConnection(self):
      self.processRemoteTree(True)
  def activateHostDisconnection(self):
      self.processRemoteTree(False)
  def processRemoteTree(self, dstate):
      currentItem=self.ui.clientTreeWidget.currentItem()
      if currentItem == None:
        return
      server=self.servers[(currentItem.text(1), currentItem.text(2).toInt()[0])]
      if (server.indiclient == None):
        server.indiclient=IndiClient(server)
      if (server.isConnected == dstate):
        return
      if (dstate):
        server.indiclient.connectServer()
      else:
        server.indiclient.disconnectServer()
 
  def connectServer(self):
    print("connecting server")

class PyQtIndi(QtGui.QMainWindow):
  def __init__(self, parent=None):
    QtGui.QWidget.__init__(self, parent)
    self.ui = Ui_PyQtIndi()
    self.ui.setupUi(self)
 
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

if __name__ == "__main__":
  app = QtGui.QApplication(sys.argv)
  pyqtindi = PyQtIndi()
  drivermanager = DriverManager()
  rootnode=Node("Connected servers")
  indimodel=IndiModel(rootnode)
  #modeltest = ModelTest(indimodel, pyqtindi);
  indiitemdelegate=IndiItemDelegate()
  pyqtindi.ui.treeViewServer.setModel(indimodel)
  pyqtindi.ui.treeViewServer.setColumnWidth(0, 250)
  pyqtindi.ui.treeViewServer.setItemDelegateForColumn(2, indiitemdelegate)
  pyqtindi.ui.treeViewServer.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
  QtCore.QObject.connect(pyqtindi.ui.actionQuit, QtCore.SIGNAL("triggered()"), app.quit)
  QtCore.QObject.connect(pyqtindi.ui.actionServer_Manager, QtCore.SIGNAL("triggered()"), drivermanager.show)
  QtCore.QObject.connect(pyqtindi.ui.actionIndi_Control_Panel, QtCore.SIGNAL("triggered()"), pyqtindi.ui.dockWidgetServer.show)
  QtCore.QObject.connect(pyqtindi.ui.actionLogs_Messages, QtCore.SIGNAL("triggered()"), pyqtindi.ui.dockWidgetMessages.show)
  #QtCore.QMetaType.qRegisterMetaType("PyQtIndi.IBLOB")
  #registerITextVp=QtCore.QVariant(PyIndi._ITextVectorProperty)
  #registerINumberVP=QtCore.QVariant(PyIndi._INumberVectorProperty)
  #registerISwitchVP=QtCore.QVariant(PyIndi._ISwitchVectorProperty)
  #registerILightVP=QtCore.QVariant(PyIndi._ILightVectorProperty)
  #registerIBLOBVP=QtCore.QVariant(PyIndi._IBLOBVectorProperty)
  #registerIBLOB=QtCore.QVariant(PyIndi.IBLOB)
  pyqtindi.show()
  sys.exit(app.exec_())
