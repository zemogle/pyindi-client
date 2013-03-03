import wand
wand.api.load_library()
from wand.image import Image
f=open('/home/geehale/file_2013-01-28T07:26:08..fits')
fblob=f.read()
img=Image(blob=fblob)
wand.api.libmagick.MagickGetImageWidth(img.wand)

#theimg= wand.api.libmagick.BlobToImage(info, fblob,2626560,err)
