# pyINDI-client

** I did not write this library. I ported from GoogleCode to make my deployment easier https://code.google.com/p/pyindi-client/ **

pyindi-client is a python binding for the libindi library. It contains a PyIndi module which mainly defines an IndiClient class. This class could be used to build python scripts able to interact with indi servers using sendNew* methods and implementing new* methods of the BaseMediator class. PyQt applications may also be built on top of IndiClient, thus allowing rapid development of GUI Indi clients.
SWIG Binding

The swig-indi directory contains several bindings for the libindiclient library:

    Python binding: in the swig-indi/swing-indi-python directory. To build and install:

    svn co http://pyindi-client.googlecode.com/svn/trunk/swig-indi/swig-indi-python 
    mkdir libindipython
    cd libindipython
    cmake ../swing-indi-python
    make
    sudo make install

    You may have to install swig2.0 together with python and Indi itself. There is a small test/example script in the source directory. 

    Node.js binding: in the swig-indi/swing-indi-nodejs directory. To build and install a local nodejs extension:

    svn co http://pyindi-client.googlecode.com/svn/trunk/swig-indi/swig-indi-nodejs 
    mkdir indinodejs
    cd indinodejs
    cmake -DCMAKE_INSTALL_PREFIX=. ../swing-indi-nodejs 
    make
    make install
    # the extension lies in lib/node_modules/indiclientnodejs. You may run the test script with
    NODE_PATH=./lib/node_modules/ node ../swing-indi-nodejs/test-indiclientnodejs.js

    You may have to install swig2.0/3.0 together with node/npm and Indi itself. There is a small test/example script in the source directory. 

    Tcl Binding: in the swig-indi/swing-indi-tcl directory. VectorProperty should be wrapped as you can only see the first property of the vector as for now. Same procedure as for Python to build it.
    PHP Binding: in the swig-indi/swing-indi-php directory. VectorProperty should be wrapped as you can only see the first property of the vector as for now. Same procedure as for Python to build it. Thread not supported so it is actually quite unuseful, but that's fun, 

## Indi Python WebSocket server

Built on top of the swig binding for Python, a WebSocket server may be implemented to serve standard Indi protocol messages as JSON messages to WebBrowser clients. This uses the ws4py implementation together with a cherrypy server. To build and run:

# install cherrypy version 3
sudo apt-get install python-cherrypy3
#install ws4py
sudo mkdir /opt/ws4py;chown localuser.localuser /opt/ws4py
cd ws4py
git clone https://github.com/Lawouach/WebSocket-for-Python.git
sudo cd /opt/ws4py/WebSocket-for-Python; python setup.py install
#install and run the websocket server
svn co http://pyindi-client.googlecode.com/svn/trunk/pyindi-ws
cd pyindi-ws
python indi_simple_html_cherrypy_server.py
#run an indiserver somewhere
indiserver indi_eqmod_telescope indi_v4l2_ccd

You can then browse the websocket server and connect therein to your indi servers. Below is a snapshot of the simple html server (no style/no theme for the moment). You can run the websocket server to serve your local network and use an android device to browse your indi servers. Simply run

python indi_simple_html_cherrypy_server.py --host 192.168.0.15 #use your local IP here

## SIP Generated Python Binding (DEPRECATED)

This is now deprecated as I use swig to build the wrappers
How to build

This binding uses metasip to generate the sip files. The metasip project file is pyindi.msp. After editing the project file, just run:

pyqt-indi$ msip pyindi.msp         // Edit the project file
pyqt-indi$ msip -g sip pyindi.msp  // Generate the sip files in sip/ directory
pyqt-indi$ python3 pyindi-configure.py // Generate the Makefile for compiling sip files
pyqt-indi$ cd build
pyqt-indi$ make

The build directory will contain the PyIndi.so file to import in Python. Be aware to use the python3 sip version if you build for python3. Ubuntu has two sip packages, one for python3 and one for python2.
Treeview Indi Client

User interfaces for the driver manager come from kstars. To build the client UIs

pykdeuic4 drivermanager.ui -o drivermanagergui.py
pykdeuic4 indihostconf.ui -o indihostconfgui.py
pyuic4 pyqtindi.ui -o pyqtindigui.py

Icons are located in the directory pyqt-indi/pyqt-indi/resources. To build them

pyrcc4 icons.qrc -o icons_rc.py
cp icons_rc.py ..

## Freecad 3D Equatorial Mount Simulator

I added a 3D mount simulator that I plan to connect with pyindi-client to INDI device for monitoring purpose. The simulator was built as an exercise to use freecad/python.

