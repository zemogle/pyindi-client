# See Tutorial: http://www.youtube.com/watch?v=VcN94yMOkyU

from PyQt4 import QtCore, QtGui
import sys
import thread
import icons_rc

import ctypes
try:
     ctypes.CDLL('libindi.so.0',  ctypes.RTLD_GLOBAL)
except OSError:
     print('libindi.so library not found. Please check the LD_LIBRARY_PATH environment variable')
     print('   export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/path/to/libindi.so')
     sys.exit(1)
import PyIndi

class IndiItemDelegate(QtGui.QStyledItemDelegate):
    def __init__(self):
        super(IndiItemDelegate, self).__init__()
        #self.mouseClick=False
    def setEditorData(self, editor, index):
         print('  setEditorData for index '+ str(index.row())+','+str(index.column()))
         super(IndiItemDelegate, self).setEditorData(editor, index)
    def paint(self, painter, option, index):
        node=index.internalPointer()
        if isinstance(node, SwitchNode):
            self.initStyleOption(option, index)
            buttonoption=QtGui.QStyleOptionButton()
            buttonoption.text=node.name()
            buttonoption.rect=option.rect
            if node.data(2):
                buttonoption.state = QtGui.QStyle.State_On | QtGui.QStyle.State_Enabled
            else:
                buttonoption.state = QtGui.QStyle.State_Raised | QtGui.QStyle.State_Enabled
            #buttonoption.features=QtGui.QStyleOptionButton.DefaultButton
            QtGui.QApplication.style().drawControl(QtGui.QStyle.CE_PushButton, buttonoption, painter)
        elif isinstance(node, BlobNode):
            self.initStyleOption(option, index)
            labeltext=node.data(1)
            flags=QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter | QtCore.Qt.TextSingleLine
            labelrect=painter.drawText(option.rect, flags, " "+labeltext)
            buttonoption=QtGui.QStyleOptionButton()
            buttonoption.text="Receive Blob"
            buttonoption.rect=option.rect
            #buttonoption.rect.setWidth(option.rect.width() - labelrect.width())
            buttonoption.rect.setX(option.rect.x()+labelrect.width()+6)
            if node.receiveblob:
                 buttonoption.state = QtGui.QStyle.State_On | QtGui.QStyle.State_Enabled
            else:
                buttonoption.state = QtGui.QStyle.State_Raised | QtGui.QStyle.State_Enabled
            #buttonoption.features=QtGui.QStyleOptionButton.DefaultButton
            QtGui.QApplication.style().drawControl(QtGui.QStyle.CE_CheckBox, buttonoption, painter)
            node.buttonopt=buttonoption
        else:
            super(IndiItemDelegate, self).paint(painter, option, index)
    def editorEvent(self, event, model, option, index):
        node=index.internalPointer()
        if not (isinstance(node, SwitchNode) or isinstance(node, BlobNode)):
            return super(IndiItemDelegate, self).editorEvent(event, model, option, index)           
        leftClick=isinstance(event, QtGui.QMouseEvent) and (event.type() == QtCore.QEvent.MouseButtonPress)\
                and (event.button() == QtCore.Qt.LeftButton)
        if isinstance(node, SwitchNode) and leftClick:
             print("Switch toggle: "+node.name())
             indiproperty=node.parent().property
             propertyname=indiproperty.indiproperty.getName()
             device=indiproperty.device
             server=device.server
             if (propertyname == "CONNECTION"):
                  if (node.iswitch.name == "CONNECT"):
                       server.indiclient.connectDevice(device.device.getDeviceName())
                  elif (node.iswitch.name == "DISCONNECT"):
                       server.indiclient.disconnectDevice(device.device.getDeviceName())
                  else:
                       return True
             else:
                  svp=indiproperty.indiproperty.getSwitch()
                  if (svp.r == PyIndi.ISR_1OFMANY ):
                       for sw in svp.sp:
                            sw.s = PyIndi.ISS_OFF
                       node.iswitch.s=PyIndi.ISS_ON
                       server.indiclient.sendNewSwitch(svp)
                  else:
                       server.indiclient.sendNewSwitch(str(device.device.getDeviceName()), propertyname, node.iswitch.name)
                  model.dataChanged.emit(index, index)
             return True
        if isinstance(node, BlobNode) and leftClick:
            if node.buttonopt.rect.contains(event.pos()):
                 print("toggle blob mode for "+node.name())
                 node.receiveblob=not node.receiveblob
                 pyindiproperty=node.parent().property
                 pyindidevice=pyindiproperty.device
                 if node.receiveblob:
                      pyindidevice.server.indiclient.setBLOBMode(PyIndi.B_ALSO, pyindidevice.device.getDeviceName(),\
                                                                      pyindiproperty.indiproperty.getName())
                 else:
                      pyindidevice.server.indiclient.setBLOBMode(PyIndi.B_NEVER, pyindidevice.device.getDeviceName(),\
                                                                      pyindiproperty.indiproperty.getName())
            return True
        return True

class Node(object):
    
    def __init__(self, name, parent=None):
        
        self._name = name
        self._children = []
        self._parent = parent
        
        if parent is not None:
            parent.addChild(self)


    def typeInfo(self):
        return "NODE"

    def addChild(self, child):
        self._children.append(child)

    def insertChild(self, position, child):
        
        if position < 0 or position > len(self._children):
            return False
        
        self._children.insert(position, child)
        child._parent = self
        return True

    def removeChild(self, position):
        
        if position < 0 or position > len(self._children):
            return False
        
        child = self._children.pop(position)
        child._parent = None

        return True


    def name(self):
        return self._name

    def setName(self, name):
        self._name = name

    def child(self, row):
        #return self._children[row]
        try:
             return self._children[row]
        except IndexError:
        #     print("Thread "+str(thread.get_ident())+" Node child: index out of bounds "+str(row)+" in node "+self.name())
             return None

    def childCount(self):
        return len(self._children)

    def parent(self):
        return self._parent
    
    def row(self):
        if self._parent is not None:
            return self._parent._children.index(self)


    def log(self, tabLevel=-1):

        output     = ""
        tabLevel += 1
        
        for i in range(tabLevel):
            output += "\t"
        
        output += "|------" + self._name + "\n"
        
        for child in self._children:
            output += child.log(tabLevel)
        
        tabLevel -= 1
        output += "\n"
        
        return output

    def __repr__(self):
        return self.log()

    def columnCount(self):
        return 3

    def data(self, column):
        return self._name

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

class ServerNode(Node):
    
    def __init__(self, name, server, parent=None):
        super(ServerNode, self).__init__(name, parent)
        self.server=server
        self.server.node=self
        
    def typeInfo(self):
        return "SERVER"

class DeviceNode(Node):
    
    def __init__(self, name, device, parent=None):
        super(DeviceNode, self).__init__(name, parent)
        self.device=device
        self.device.node=self

    def typeInfo(self):
        return "DEVICE"

class GroupNode(Node):
    
    def __init__(self, name, group, parent=None):
        super(GroupNode, self).__init__(name, parent)
        self.group=group
        self.group.node=self

    def typeInfo(self):
        return "GROUP"


class PropertyNode(Node):
    
    def __init__(self, name, indiproperty, parent=None):
        super(PropertyNode, self).__init__(name, parent)
        self.property=indiproperty
        self.property.node=self

    def typeInfo(self):
        return "PROPERTY"

    def columnCount(self):
        return 3

    def data(self, column):
        if (column == 0):
            return self._name
        if (column == 1):
            return self.property.indiproperty.getState()
    
    def childflags(self, index):
        p=self.property.indiproperty.getPermission()
        if index.column()==2 and (p==PyIndi.IP_RW or p==PyIndi.IP_WO):
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
        else:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

class TextNode(Node):
    
    def __init__(self, name, itext, parent=None):
        super(TextNode, self).__init__(name, parent)
        self.itext=itext
        #self.property.node=self

    def typeInfo(self):
        return "ITEXT"     

    def columnCount(self):
        return 3

    def data(self, column):
        if (column == 0):
            return self._name
        if (column == 2):
            return self.itext.text
    def setValue(self, value, column):
        if column==2:
        #    self.itext.text=str(value)
            indiproperty=self.parent().property
            propertyname=indiproperty.indiproperty.getName()
            device=indiproperty.device
            server=device.server
            server.indiclient.sendNewText(str(device.device.getDeviceName()), propertyname, self.itext.name, value.toPyObject())
        return False
    # Data is modified back by the indiclient in the itext property by a message from the server, 
    # and as the itext property is monitored by the view, there is no need to catch the new text signal
 
    def flags(self,index):
        return self.parent().childflags(index)

class NumberNode(Node):
    
    def __init__(self, name, inumber, parent=None):
        super(NumberNode, self).__init__(name, parent)
        self.inumber=inumber
        #self.property.node=self

    def typeInfo(self):
        return "INUMBER"     

    def columnCount(self):
        return 2

    def data(self, column):
        if (column == 0):
            return self._name
        if (column == 2):
            s=''
            s=s.zfill(PyIndi.numberFormat(s, self.inumber.format, self.inumber.value))
            PyIndi.numberFormat(s, self.inumber.format, self.inumber.value)
            return s

    def setValue(self, value, column):
         if column==2:
        #    self.itext.text=str(value)
              indiproperty=self.parent().property
              propertyname=indiproperty.indiproperty.getName()
              device=indiproperty.device
              server=device.server
              nbstr=value.toPyObject()
              numval=0.0
              (r, numval)=PyIndi.f_scansexa(nbstr)
              if (r == -1):
                   print("Enter a numeric/sexagesimal value")
                   return False
              server.indiclient.sendNewNumber(str(device.device.getDeviceName()), propertyname, self.inumber.name, numval)
              return True
         return False

    def flags(self,index):
        return self.parent().childflags(index)

class SwitchNode(Node):
    
    def __init__(self, name, iswitch, parent=None):
        super(SwitchNode, self).__init__(name, parent)
        self.iswitch=iswitch
        #self.property.node=self

    def typeInfo(self):
        return "ISWITCH"     

    def columnCount(self):
        return 2

    def data(self, column):
        if (column == 0):
            return self._name
        if (column == 2):
            if self.iswitch.s == PyIndi.ISS_ON:
                return True
            else:
                return False
    def setValue(self, value, column):
        #if column==1:
        #    self.itext.text=str(value)
         print("setvalue switch "+self.name())
         pass
    def flags(self,index):
        return self.parent().childflags(index)

class LightNode(Node):
    
    def __init__(self, name, ilight, parent=None):
        super(LightNode, self).__init__(name, parent)
        self.ilight=ilight
        #self.property.node=self

    def typeInfo(self):
        return "ILIGHT"     

    def columnCount(self):
        return 2

    def data(self, column):
        if (column == 0):
            return self._name
        if (column == 2):
            if self.ilight.s == PyIndi.IPS_OK:
                 return "Ok"
            elif self.ilight.s == PyIndi.IPS_IDLE:
                 return "Idle"
            elif self.ilight.s == PyIndi.IPS_BUSY:
                 return "Busy"
            elif self.ilight.s == PyIndi.IPS_ALERT:
                 return "Alert"

    def setValue(self, value, column):
        #if column==1:
        #    self.itext.text=str(value)
        pass
    def flags(self,index):
        return self.parent().childflags(index)

class BlobNode(Node):
    
    def __init__(self, name, iblob, parent=None):
        super(BlobNode, self).__init__(name, parent)
        self.iblob=iblob
        self.buttonopt=None
        self.receiveblob=True
        if self.receiveblob:
             pyindiproperty=self.parent().property
             pyindidevice=pyindiproperty.device
             pyindidevice.server.indiclient.setBLOBMode(PyIndi.B_ALSO, pyindidevice.device.getDeviceName(),\
                                                            pyindiproperty.indiproperty.getName())
        #self.property.node=self

    def typeInfo(self):
        return "IBLOB"     

    def columnCount(self):
        return 2

    def data(self, column):
        if (column == 0):
            return self._name
        if (column == 2):
            return "BINARY DATA "+str(self.iblob.size)+" byte(s)"

    def setValue(self, value, column):
        #if column==1:
        #    self.itext.text=str(value)
        pass
    def flags(self,index):
        return self.parent().childflags(index)

class IndiModel(QtCore.QAbstractItemModel):
    
    """INPUTS: Node, QObject"""
    def __init__(self, root, parent=None):
        super(IndiModel, self).__init__(parent)
        self._rootNode = root

    """INPUTS: QModelIndex"""
    """OUTPUT: int"""
    def rowCount(self, parent):
        if not parent.isValid():
            parentNode = self._rootNode
        else:
            parentNode = parent.internalPointer()
            if (parent.column() != 0):
                 return 0
        return parentNode.childCount()

    """INPUTS: QModelIndex"""
    """OUTPUT: int"""
    def columnCount(self, parent):
        if parent.isValid():
             return parent.internalPointer().columnCount()
        else:
            return self._rootNode.columnCount()
    
    """INPUTS: QModelIndex, int"""
    """OUTPUT: QVariant, strings are cast to QString which is a QVariant"""
    def data(self, index, role=QtCore.Qt.DisplayRole):
        
        if not index.isValid():
            return None

        node = index.internalPointer()

        if (role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole) and not (index.column() == 1):
            return node.data(index.column())
            
        if role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                typeInfo = node.typeInfo()
                
                if typeInfo == "SERVER":
                    return QtGui.QIcon(QtGui.QPixmap(":/server.png"))
                
                if typeInfo == "DEVICE":
                    return QtGui.QIcon(QtGui.QPixmap(":/device.png"))
                
                if typeInfo == "PROPERTY":
                    return QtGui.QIcon(QtGui.QPixmap(":/property.png"))
            if index.column() == 1 and node.typeInfo() == "PROPERTY":
                state = node.data(1)
                if state == PyIndi.IPS_IDLE:
                    return QtGui.QIcon(QtGui.QPixmap(":/led-grey_light.png"))
                if state == PyIndi.IPS_ALERT:
                    return QtGui.QIcon(QtGui.QPixmap(":/led-red.png"))
                if state == PyIndi.IPS_BUSY:
                    return QtGui.QIcon(QtGui.QPixmap(":/led-yellow.png"))
                if state == PyIndi.IPS_OK:
                    return QtGui.QIcon(QtGui.QPixmap(":/led-green.png"))

    """INPUTS: QModelIndex, QVariant, int (flag)"""
    def setData(self, index, value, role=QtCore.Qt.EditRole):

        if index.isValid():
            
            if role == QtCore.Qt.EditRole:
                
                node = index.internalPointer()
                return node.setValue(value, index.column())
                
        return False
    
    """INPUTS: int, Qt::Orientation, int"""
    """OUTPUT: QVariant, strings are cast to QString which is a QVariant"""
    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if section == 0:
                return "Indi Devices"
            if section == 1:
                 return "Status"
            else:
                return "Infos/Values"

    """INPUTS: QModelIndex"""
    """OUTPUT: int (flag)"""
    def flags(self, index):
        return index.internalPointer().flags(index)

    """INPUTS: QModelIndex"""
    """OUTPUT: QModelIndex"""
    """Should return the parent of the node with the given QModelIndex"""
    def parent(self, index):
         if (not index.isValid()):
              return QtCore.QModelIndex()

         node = self.getNode(index)
         parentNode = node.parent()
        
         if (parentNode == self._rootNode or parentNode==None):
            return QtCore.QModelIndex()
        
         return self.createIndex(parentNode.row(), 0, parentNode)

 
    """INPUTS: int, int, QModelIndex"""
    """OUTPUT: QModelIndex"""
    """Should return a QModelIndex that corresponds to the given row, column and parent node"""
    def index(self, row, column, parent):
        if (parent.isValid() and (parent.column() != 0)):
             return QtCore.QModelIndex()

        parentNode = self.getNode(parent)
        
        childItem = parentNode.child(row)
        

        if childItem and column >= 0 and column < self.columnCount(parent):
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()



    """CUSTOM"""
    """INPUTS: QModelIndex"""
    def getNode(self, index):
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node
            
        return self._rootNode

    def insertServer(self, position, server):
        self.layoutAboutToBeChanged.emit()
        parent=QtCore.QModelIndex()
        parentNode = self.getNode(parent)
        print("insertServer: "+server.name +" in "+parentNode.name() + " at position "+str(position) + " among "+str(self.rowCount(parent)))
        ##self.beginInsertRows(parent, position, position )
        childNode = ServerNode(server.name, server)
        success = parentNode.insertChild(position, childNode)
        
        ##self.endInsertRows()
        #print("insertServer("+str(success)+"): inserted "+server.name +" in "+parentNode.name() + " at position "+str(position) + " now ("+str(parent.row())+","+str(parent.column())+")="+str(self.rowCount(parent)) + " parentNode= "+str(parentNode.childCount()) + " rootNode="+str(self._rootNode.childCount()))
        return success

    def removeServer(self, server):
        self.layoutAboutToBeChanged.emit()
        parent=QtCore.QModelIndex()
        parentNode = self.getNode(parent)
        position=server.node.row()

        ##self.beginRemoveRows(parent, position, position)
        success = parentNode.removeChild(position)
        ##self.endRemoveRows()
        server.node=None
        self.layoutChanged.emit()
        return success
        
    def insertDevice(self, position, server, device):
        self.layoutAboutToBeChanged.emit()
        parentNode = server.node
        parent = self.createIndex(0, 0, parentNode)
        print("insertDevice: "+device.name+ " in "+parentNode.name()+" at position "+str(position))
        ##self.beginInsertRows(parent, position, position )
        childNode = DeviceNode(device.name, device)
        success = parentNode.insertChild(position, childNode)
        #print(parentNode.log())
        ##self.endInsertRows()
        self.layoutChanged.emit()
        return success

    def insertGroup(self, position, device, group):
        self.layoutAboutToBeChanged.emit()
        parentNode = device.node
        parent = self.createIndex(0, 0, parentNode)
        print("insertGroup: "+group.name+ " in "+parentNode.name()+" at position "+str(position))
        ##self.beginInsertRows(parent, position, position )
        childNode = GroupNode(group.name, group)
        success = parentNode.insertChild(position, childNode)
        #print(parentNode.log())
        ##self.endInsertRows()
        self.layoutChanged.emit()
        return success


    def insertProperty(self, position, group, newproperty):        
        self.layoutAboutToBeChanged.emit()
        parentNode = group.node
        parent = self.createIndex(0, 0, parentNode)
        print("insertProperty: "+newproperty.name+" in "+parentNode.name()+" at position "+str(position))
        ##self.beginInsertRows(parent, position, position )
        childNode = PropertyNode(newproperty.label, newproperty)
        success = parentNode.insertChild(position, childNode)
        ##self.endInsertRows()
        propertytype = newproperty.indiproperty.getType()
        child=self.createIndex(0, 0, childNode)
        if (propertytype == PyIndi.INDI_TEXT):
          textproperty=newproperty.indiproperty.getText()
          ##self.beginInsertRows(child, 0,  len(textproperty.tp) - 1)
          for t in textproperty.tp:
            tn=t.label
            if not tn or tn=="":
                 tn=t.name
            textNode=TextNode(tn, t)
            success=childNode.insertChild(childNode.childCount(), textNode)
            #self.beginInsertColumns(self.createIndex(0,0,textNode), 1 ,1)
            #self.endInsertColumns()
        elif (propertytype == PyIndi.INDI_NUMBER):
          numberproperty=newproperty.indiproperty.getNumber()
          ##self.beginInsertRows(child, 0,  len(numberproperty.np) - 1)
          for n in numberproperty.np:
            nn=n.label
            if not nn or nn == "":
                 nn=n.name
            numberNode=NumberNode(nn, n)
            success=childNode.insertChild(childNode.childCount(), numberNode)
            #self.beginInsertColumns(self.createIndex(0,0,numberNode), 1 ,1)
            #self.endInsertColumns()
        elif (propertytype == PyIndi.INDI_SWITCH):
          switchproperty=newproperty.indiproperty.getSwitch()
          ##self.beginInsertRows(child, 0, len(switchproperty.sp) - 1)
          for s in switchproperty.sp:
            sn=s.label
            if not sn or sn=="":
                 sn=s.name
            switchNode=SwitchNode(sn, s)
            success=childNode.insertChild(childNode.childCount(), switchNode)
            #self.beginInsertColumns(self.createIndex(0,0,switchNode), 1 ,1)
            #self.endInsertColumns()
        elif (propertytype == PyIndi.INDI_LIGHT):
          lightproperty=newproperty.indiproperty.getLight()
          ##self.beginInsertRows(child, 0, len(lightproperty.lp) - 1)
          for s in lightproperty.lp:
            ln=s.label
            if not ln or ln =="":
                 ln=s.name
            lightNode=LightNode(ln, s)
            success=childNode.insertChild(childNode.childCount(), lightNode)
            #self.beginInsertColumns(self.createIndex(0,0,lightNode), 1 ,1)
            #self.endInsertColumns()
        elif (propertytype == PyIndi.INDI_BLOB):
          blobproperty=newproperty.indiproperty.getBLOB()
          ##self.beginInsertRows(child, 0, len(blobproperty.bp) - 1)
          for s in blobproperty.bp:
            bn=s.label+"("+s.name+")"
            if not bn or bn=="":
                 bn=s.name
            blobNode=BlobNode(bn, s, childNode)
            success=childNode.insertChild(childNode.childCount(), blobNode)
            #self.beginInsertColumns(self.createIndex(0,0,blobNode), 1 ,1)
            #self.endInsertColumns()
        ##self.endInsertRows()
        #insertedrow=self.createIndex(position-1,1,parentNode)
        #self.dataChanged.emit(insertedrow, insertedrow)
        self.layoutChanged.emit()
        return success

    # groups are removed automatically where there are no more properties
    def removeGroup(self, position, device, group):
        self.layoutAboutToBeChanged.emit()
        parent=self.createIndex(0,0, device.node)
        parentNode = device.node
        print("TreeModel Thread "+str(thread.get_ident())+" Remove group: "+ group.node.name() +" in " + device.node.name() +" at "+str(position)+" among "+str(parentNode.childCount()))
        ##self.beginRemoveRows(parent, position, position)
        success = parentNode.removeChild(position)
        ##self.endRemoveRows()
        print("  Group removed")        
        self.layoutChanged.emit()
        return success

    def removeProperty(self, position, group, theproperty):
        self.layoutAboutToBeChanged.emit()
        parent=self.createIndex(0,0, group.node)
        parentNode = group.node
        print("TreeModel Thread "+str(thread.get_ident())+" Remove property: "+ theproperty.node.name() +" in " + group.node.name() +" at "+str(position)+" among "+str(parentNode.childCount()))

        child=self.createIndex(0,0, theproperty.node)
        childNode = theproperty.node
        print("  Removing "+str(childNode.childCount())+" childs from: "+ theproperty.node.name())
        ##self.beginRemoveRows(child, 0, childNode.childCount()-1)
        for c in range(childNode.childCount()):
             print("    suppress "+childNode.child(0).name())
             success = childNode.removeChild(0)
        ##self.endRemoveRows()
        print("  Childs removed from: "+ theproperty.node.name())
        ##self.beginRemoveRows(parent, position, position)
        success = parentNode.removeChild(position)
        ##self.endRemoveRows()
        print("  Property removed")
        #removedrow=self.createIndex(device.node.row()+position,0,theproperty.node)        
        #self.dataChanged.emit(removedrow, removedrow)
        #self.rowsRemoved.emit(parent, position, position)
        #self.reset()
        #self.update(parent)
        #theproperty.node=None
        #super(IndiModel, self).removeRows(position, 1, parent)
        self.layoutChanged.emit()
        return success

    """INPUTS: int, int, QModelIndex"""
    def insertRows(self, position, rows, parent=QtCore.QModelIndex()):
        
        parentNode = self.getNode(parent)
        
        self.beginInsertRows(parent, position, position + rows - 1)
        
        for row in range(rows):
            
            childCount = parentNode.childCount()
            childNode = Node("untitled" + str(childCount))
            success = parentNode.insertChild(position, childNode)
        
        self.endInsertRows()

        return success

    """INPUTS: int, int, QModelIndex"""
    def removeRows(self, position, rows, parent=QtCore.QModelIndex()):
        
        parentNode = self.getNode(parent)
        self.beginRemoveRows(parent, position, position + rows - 1)
        
        for row in range(rows):
            success = parentNode.removeChild(position)
            
        self.endRemoveRows()
        
        return success

