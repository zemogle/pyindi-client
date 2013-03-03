from PyQt4 import QtCore, QtGui

import ctypes
try:
     ctypes.CDLL('libindi.so.0',  ctypes.RTLD_GLOBAL)
except OSError:
     print('libindi.so library not found. Please check the LD_LIBRARY_PATH environment variable')
     print('   export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/path/to/libindi.so')
     sys.exit(1)
import PyIndi

# Default viewer uses Wand binding to ImageMagick
# See http://docs.wand-py.org/en/0.2-maintenance/
from wand.image import Image

class DefaultViewer(QtCore.QObject):
  def __init__(self, blob, parent=None):
      QtCore.QObject.__init__(self)
      self.widget=parent
      self.blob=blob
      #self.pixmap=QtGui.QPixmap("/home/geehale//Images/Qastrocam/jupiter-2010.10.08-22h27m17s/9.png")
      self.pixmap=QtGui.QPixmap()
      self.scene=QtGui.QGraphicsScene()
      #self.scene.addSimpleText("This is the BLOB")
      self.pixmapitem=self.scene.addPixmap(self.pixmap)
      self.gview=QtGui.QGraphicsView(self.scene)
      self.layout=QtGui.QGridLayout()
      self.layout.addWidget(self.gview)
      self.widget.setLayout(self.layout)
      self.gview.show()

  def update(self):
       img=Image(blob=self.blob.blob.tobytes())
       print('DefaultViewer update: width ='+str(img.width)+', height ='+str(img.height)+', format ='+img.format)
       if not self.pixmap.loadFromData(img.make_blob('ppm')):
            print("  Can't load ImageMagick blob data into pixmap")
       self.widget.update()
