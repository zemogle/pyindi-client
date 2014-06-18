#!/usr/bin/python

import sys
import time
import logging
import os

import PyIndi
import PyIndiDriver

import random

def strISState(s):
    if (s == PyIndi.ISS_OFF):
        return "Off"
    else:
        return "On"

def strIPState(s):
    if (s == PyIndi.IPS_IDLE):
        return "Idle"
    elif (s == PyIndi.IPS_OK):
        return "Ok"
    elif (s == PyIndi.IPS_BUSY):
        return "Busy"
    elif (s == PyIndi.IPS_ALERT):
        return "Alert"

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
    PyIndiDriver.IDLog("Main ISNewBLOB\n")
    indidriver.ISNewBLOB(dev, name, sizes, blobsizes, blobs, formats, names, n)

# This is tutorial 4 Simple Skeleton

class IndiDriver(PyIndiDriver.DefaultDevice):
    def __init__(self):
        super(IndiDriver, self).__init__()
        self.name="Python Skeleton"
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
            cvalues=PyIndiDriver.new_doubleArray(n)
            for i in range(len(values)):
                self.logger.info('  ' + names[i] + ' = ' + str(values[i])) 
                PyIndiDriver.doubleArray_setitem(cvalues, i, values[i])
            PyIndiDriver.IUUpdateNumber(nvp, cvalues, names, n)
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
        # Build Clike array to call C++ method
        # names is handled by swig (see %typemap(in) char *[]) 
        cstates=PyIndiDriver.new_ISStateArray(n)
        for i in range(len(states)):
            self.logger.info('  '+names[i] + ' = ' + str(states[i]))
            PyIndiDriver.ISStateArray_setitem(cstates, i, states[i])
        if super(IndiDriver, self).ISNewSwitch(dev, name, cstates, names, n):
            return True

        svp=self.getSwitch(name)
        lvp=self.getLight('Light Property')
        if not svp:
            return False
        if not self.isConnected():
            svp.s=PyIndi.IPS_ALERT
            PyIndiDriver.IDSetSwitch(svp, "Cannot change property while device is disconnected.")
            return False
        if not lvp:
            return False       
        if (name == "Menu"):
            # Use the Clike array to call C methods
            PyIndiDriver.IUUpdateSwitch(svp, cstates, names, n)
            onSW=PyIndiDriver.IUFindOnSwitch(svp)
            lightIndex=PyIndiDriver.IUFindOnSwitchIndex(svp)
            if (lightIndex < 0 or lightIndex > lvp.nlp):
                return False
            if (onSW):
                lightState=random.randint(0,3)
                lvp[lightIndex].s=lightState # direct indexing of the vector, do not use lvp.lp
                svp.s=PyIndi.IPS_OK
                lvp.s=PyIndi.IPS_OK
                PyIndiDriver.IDSetSwitch(svp, 'Setting to switch '+onSW.name+' is successful. Changing corresponding light property to '+strIPState(lvp[lightIndex].s))
                PyIndiDriver.IDSetLight(lvp, None)
            return True           
        PyIndiDriver.delete_ISStateArray(cstates)
        return False
    def ISNewBLOB (self, dev, name, sizes, blobsizes, blobs, formats, names, n):
        self.logger.info("ISNewBLOB " + dev + " property " + name)
        if (dev != self.name):
            return False
        bvp=self.getBLOB(name)
        if not bvp:
            return False
        if not self.isConnected():
            bvp.s=PyIndi.IPS_ALERT
            PyIndiDriver.IDSetNumber(bvp, "Cannot change property while device is disconnected.")
            return False
        if (bvp.name == "BLOB Test"):
            csizes=PyIndiDriver.new_intArray(n)
            for i in range(len(sizes)):
                PyIndiDriver.intArray_setitem(csizes, i, sizes[i])
                #PyIndiDriver.IDLog('BLOB '+str(i)+' Content:\n##################################\n'+blobs[i]+'\n##################################\n')
            cblobsizes=PyIndiDriver.new_intArray(n)
            for i in range(len(blobsizes)):
                PyIndiDriver.intArray_setitem(cblobsizes, i, blobsizes[i])
            
            PyIndiDriver.IUUpdateBLOB(bvp, csizes, cblobsizes, blobs, formats, names, n);
            bp = PyIndiDriver.IUFindBLOB(bvp, names[0])
            if (not bp):
                return False
            PyIndiDriver.IDLog('Received BLOB with name '+bp.name+', format '+getattr(bp,'format')+', and size '+str(bp.size)+', and bloblen '+str(bp.bloblen)+'\n')
            #PyIndiDriver.IDLog('BLOB Content:\n##################################\n'+str(bp.getblobdata())+'\n##################################\n')
            bp.size=0
            bvp.s = PyIndi.IPS_OK
            PyIndiDriver.IDSetBLOB(bvp, None)
        return True

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
            PyIndiDriver.IDLog('Property '+p.getName()+' - ' + p.getLabel() + '\n')
            if p.getType()==PyIndi.INDI_TEXT:
                tpy=p.getText()
                for t in tpy:
                    PyIndiDriver.IDLog("       "+t.name+"("+t.label+")= "+t.text + '\n')
            elif p.getType()==PyIndi.INDI_NUMBER:
                tpy=p.getNumber()
                for t in tpy:
                    PyIndiDriver.IDLog("       "+t.name+"("+t.label+")= "+str(t.value) + '\n')
            elif p.getType()==PyIndi.INDI_SWITCH:
                tpy=p.getSwitch()
                for t in tpy:
                    PyIndiDriver.IDLog("       "+t.name+"("+t.label+")= "+strISState(t.s) + '\n')
            elif p.getType()==PyIndi.INDI_LIGHT:
                tpy=p.getLight()
                for t in tpy:
                    PyIndiDriver.IDLog("       "+t.name+"("+t.label+")= "+strIPState(t.s) + '\n')
            elif p.getType()==PyIndi.INDI_BLOB:
                tpy=p.getBLOB()
                for t in tpy:
                    PyIndiDriver.IDLog("       "+t.name+"("+t.label+")= <blob "+str(t.size)+" bytes>" + '\n')
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
