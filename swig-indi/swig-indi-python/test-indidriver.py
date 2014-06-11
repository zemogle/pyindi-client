#!/usr/bin/python

import sys
import time
import logging
import os

import PyIndi
import PyIndiDriver

isInit=False
indidriver=None

def ISInit():
    if not isInit:
        indidriver=IndiDriver()
        isInit=True

def ISGetProperties(dev):
    indidriver.ISGetProperties(dev)

def ISNewNumber(dev, name, values, names, n):
    indidriver.ISNewNumber(dev, name, values, names, n)

def ISNewText(dev, name, texts, names, n):
    indidriver.ISNewText(dev, name, texts, names, n)

def ISNewSwitch(dev, name, states, names, n):
    indidriver.ISNewSwitch(dev, name, states, names, n)

def ISNewBLOB(dev, name, sizes, blobsizes, blobs, formats, names, n):
    indidriver.ISNewBLOB(dev, name, sizes, blobsizes, blobs, formats, names, n)

# This is tutorial 4 Simple Skeleton

class IndiDriver(PyIndiDriver.DefaultDevice):
    def __init__(self):
        super(IndiDriver, self).__init__()
        self.name="Python Simple Skeleton"
        self.logger = logging.getLogger('PyIndiDriver.IndiDriver')
        self.logger.info('creating an instance of PyIndiDriver.BaseDevice')
    def ISGetProperties (self, dev):
        self.logger.info("ISGetProperties " + str(dev))
        super(IndiDriver, self).ISGetProperties(dev)
    def ISNewNumber (self, dev, name, values, names, n):
        self.logger.info("ISNewNumber " + dev + " property " + name)
        if (dev != self.name):
            return False
        nvp=self.getNumber(name)
        if not nvp:
            return False
        if not self.isConnected():
            nvp.s=PyIndi.IPS_ALERT
            PyIndiDriver.IDSetNumber(nvp, "Cannot change property while device is disconnected.")
            return False
        if (name == "Number Property"):
            PyIndiDriver.IUUpdateNumber(nvp, values, names, n)
            print names
            nvp.s=PyIndi.IPS_OK
            PyIndiDriver.IDSetNumber(nvp, None)
            return True           
        return False
    def ISNewText (self, dev, name, texts, names, n):
        self.logger.info("ISNewText " + dev + " property " + name)
    def ISNewSwitch (self, dev, name, states, names, n):
        self.logger.info("ISNewSwitch " + dev + " property " + name)
        if (dev != self.name):
            return False    
        cstates=PyIndiDriver.new_ISStateArray(n)
        for i in range(len(states)):
            self.logger.info("ISNewSwitch switches" + str(states[i]))
            PyIndiDriver.ISStateArray_setitem(cstates, i, states[i])
        if super(IndiDriver, self).ISNewSwitch(dev, name, cstates, names, n):
            return True
        PyIndiDriver.delete_ISStateArray(cstates)
        svp=self.getSwitch(name)
        svp=self.getLight('Light Property')
        if not svp:
            return False
        if not self.isConnected():
            svp.s=PyIndi.IPS_ALERT
            PyIndiDriver.IDSetSwitch(svp, "Cannot change property while device is disconnected.")
            return False
        if not lvp:
            return False       
        if (name == "Menu"):
            PyIndiDriver.IUUpdateSwitch(svp, states, names, n)
            print names
            svp.s=PyIndi.IPS_OK
            lvp.s=PyIndi.IPS_OK
            #PyIndiDriver.IDSetSwitch(svp, "Setting to switch %s is successful. Changing corresponding light property to %s.", onSW->name, pstateStr(lvp->lp[lightIndex].s))
            PyIndiDriver.IDSetLight(lvp, None)
            return True           
        return False
    def ISNewBLOB (self, dev, name, sizes, blobsizes, blobs, formats, names, n):
        self.logger.info("ISNewBLOB " + dev + " property " + name)
    def getDefaultName(self):
        #self.logger.info("getDefaultName "+ self.name)
        return self.name
    # Always overload getDriverName as the current C implementation is unsecure with SWIG
    def getDriverName(self):
        #self.logger.info("getDriverName "+ self.name)
        return os.path.basename(__file__)
    def initProperties(self):
        self.logger.info("initProperties "+self.getDefaultName())
        super(IndiDriver, self).initProperties()
        #self.logger.info("initProperties loading skeleton")
        self.skelFileName = "tutorial_four_sk.xml"
        self.skel = os.getenv("INDISKEL")
        if self.skel:
            self.buildSkeleton(self.skel)
        else:
            try:
                os.stat(self.skelFileName)
                self.buildSkeleton(self.skelFileName)
            except OSError as e:
                PyIndiDriver.IDLog("No skeleton file was specified. Set environment variable INDISKEL to the skeleton path and try again.\n");
        # Optional: Add aux controls for configuration, debug & simulation that get added in the Options tab
        # of the driver.
        self.addAuxControls()
        # Let's print a list of all device properties
        lp=self.getProperties()
        for p in lp:
            PyIndiDriver.IDLog("Property "+p.getName()+"\n")
        return True
    def Connect(self):
        self.logger.info("Connect "+self.getDefaultName())
        return True
    def Disconnect(self):
        self.logger.info("Disconnect "+self.getDefaultName())
        return True

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

indidriver=IndiDriver()

#clixml=PyIndiDriver.newLilXML()
#PyIndiDriver.addCallback(0

PyIndiDriver.driver_run()
#indidriver.ISNewSwitch("Python Simple Skeleton", "CONNECTION", [0, 1], ["CONNECT", "DISCONNECT"], 1)
