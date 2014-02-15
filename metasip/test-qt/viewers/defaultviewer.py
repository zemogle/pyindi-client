from PyQt4 import QtCore, QtGui

import ctypes
try:
     ctypes.CDLL('libindi.so.0',  ctypes.RTLD_GLOBAL)
except OSError:
     print('libindi.so library not found. Please check the LD_LIBRARY_PATH environment variable')
     print('   export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/path/to/libindi.so')
     sys.exit(1)
import PyIndi
# on Ubuntu 12.04, version of pyfits is too old (apt-get remove python-pyfits)
# install last release from pip pip install pyfits
import pyfits
import numpy
#use PyPNG package (pure python png) pip install pypng
#import png

# From f2n (installed in /opt/Downloads/f2n)
# http://obswww.unige.ch/~tewes/f2n_dot_py/

def numpy2qimage(array):
	if numpy.ndim(array) == 2:
		return gray2qimage(array)
	elif numpy.ndim(array) == 3:
		return rgb2qimage(array)
	raise ValueError("can only convert 2D or 3D arrays")

def gray2qimage(gray):
	"""Convert the 2D numpy array `gray` into a 8-bit QImage with a gray
	colormap.  The first dimension represents the vertical image axis."""
	if len(gray.shape) != 2:
		raise ValueError("gray2QImage can only convert 2D arrays")

	gray = numpy.require(gray, numpy.uint8, 'C')

	h, w = gray.shape

	result = QtGui.QImage(gray.data, w, h, QtGui.QImage.Format_Indexed8)
	result.ndarray = gray
	for i in range(256):
 		result.setColor(i, QtGui.QColor(i, i, i).rgb())
	return result

def rgb2qimage(rgb):
	"""Convert the 3D numpy array `rgb` into a 32-bit QImage.  `rgb` must
	have three dimensions with the vertical, horizontal and RGB image axes."""
	if len(rgb.shape) != 3:
		raise ValueError("rgb2QImage can expects the first (or last) dimension to contain exactly three (R,G,B) channels")
	if rgb.shape[2] != 3:
		raise ValueError("rgb2QImage can only convert 3D arrays")

	h, w, channels = rgb.shape

	# Qt expects 32bit BGRA data for color images:
	bgra = numpy.empty((h, w, 4), numpy.uint8, 'C')
	bgra[...,0] = rgb[...,2]
	bgra[...,1] = rgb[...,1]
	bgra[...,2] = rgb[...,0]
	bgra[...,3].fill(255)

	result = QtGui.QImage(bgra.data, w, h, QtGui.QImage.Format_RGB32)
	result.ndarray = bgra
	return result

def lingray(x, a=None, b=None):
	"""
	Auxiliary function that specifies the linear gray scale.
	a and b are the cutoffs : if not specified, min and max are used
	"""
	if a == None:
		a = numpy.min(x)
	if b == None:
		b = numpy.max(x)
	
	return 255.0 * (x-float(a))/(b-a)

def loggray(x, a=None, b=None):
	"""
	Auxiliary function that specifies the logarithmic gray scale.
	a and b are the cutoffs : if not specified, min and max are used
	"""
	if a == None:
		a = numpy.min(x)
	if b == None:
		b = numpy.max(x)
		
	linval = 10.0 + 990.0 * (x-float(a))/(b-a)
	return (numpy.log10(linval)-1.0)*0.5 * 255.0

	

class FitsImage(QtCore.QObject):
  def __init__(self, blobdata, parent=None):
      QtCore.QObject.__init__(self)
      self.pixmap=parent
      #self.blobdata=blobdata
      self.hdus=pyfits.HDUList.fromstring(blobdata)
      print("FitsImage init")
      self.hdus.info()
      self.hdus.readall()
  def nhdus(self):
       return len(self.hdus)
  def updatePixmap(self, blobdata, hduidx):
       self.hdus=pyfits.HDUList.fromstring(blobdata)
       hdu=self.hdus[hduidx]
       bitpix=hdu.header['BITPIX']
       print("updateFits: hdu "+str(hduidx)+"BITPIX = "+str(bitpix) + " shape = "+str(hdu.data.shape))
       if bitpix == -32 or bitpix == 16 or bitpix == 8:
            # BIPIX == -32 -> IEEE 32 bits
            self.numpyarray = hdu.data.astype(numpy.float32)
            #self.numpyarray = hdu.data
            #calcarray = self.numpyarray.transpose()
            #calcarray = lingray(self.numpyarray, None, None)
            calcarray = loggray(self.numpyarray, None, None)
            bwarray = numpy.zeros(calcarray.shape, dtype=numpy.uint8)
            calcarray.round(out=bwarray)
       #elif bitpix == 8:
       #     bwarray=hdu.data
       self.img=numpy2qimage(bwarray)
       #self.png=png.from_array(bwarray,'L')
       self.pixmap.convertFromImage(self.img)
       #self.pixmap.loadFromData(self.png)

class DefaultViewer(QtCore.QObject):
  def __init__(self, blob, parent=None):
      QtCore.QObject.__init__(self)
      self.widget=parent
      self.blob=blob
      self.fits=None
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
 #     decoding/uncompress is made in basedevice->SetValue called by dispatchComand in receive thread
 #      base64data=base64.b64decode(self.blob.blob.tobytes())
       indiformat=self.blob.format.lower()
 #      if indiformat.endswith('.z'):
 #           blobdata=zlib.decompress(base64data)
 #      else:
 #           blobdata=base64data
       blobdata=self.blob.blob.tobytes()
       blobformat=indiformat.rsplit('.')[1]
       if blobformat in QtGui.QImageReader.supportedImageFormats():
            if not self.pixmap.loadFromData(blobdata):
                 print("DefaultViewer: Can't load "+blobformat+" blob data into pixmap")
            else:
                 print("DefaultViewer: successfully loaded pixmap supported "+blobformat+" blob image")
       elif blobformat == 'fits':
            if self.fits == None:
                 self.fits=FitsImage(blobdata, self.pixmap)
            self.fits.updatePixmap(blobdata, 0)
       else:
            print("DefaultViewer: "+blobformat+" format is not supported")
       #img=Image(blob=blobdata)
       #print('DefaultViewer update: width ='+str(img.width)+', height ='+str(img.height)+', format ='+img.format)
       #if not self.pixmap.loadFromData(img.make_blob('png')):
       #     print("  Can't load ImageMagick blob data into pixmap")
       self.scene.removeItem(self.pixmapitem)
       self.pixmapitem=self.scene.addPixmap(self.pixmap)
       self.widget.update()
