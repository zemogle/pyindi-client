#!/usr/bin/python

import sys
import time
import logging
import os

import PyIndi
import PyIndiDriver

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

def logProperties(d):
    # print a list of all device properties
    lp=d.getProperties()
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
                
isInit=False
ccd=None

def ISInit():
    if not isInit:
        ccd=CCDSimulator()
        isInit=True

def ISGetProperties(dev):
    ccd.ISGetProperties(dev)

def ISNewNumber(dev, name, values, names, n):
    ccd.ISNewNumber(dev, name, values, names, n)

def ISNewText(dev, name, texts, names, n):
    ccd.ISNewText(dev, name, texts, names, n)

def ISNewSwitch(dev, name, states, names, n):
    ccd.ISNewSwitch(dev, name, states, names, n)

def ISNewBLOB(dev, name, sizes, blobsizes, blobs, formats, names, n):
    ccd.ISNewBLOB(dev, name, sizes, blobsizes, blobs, formats, names, n)

# Problem: with director=1 and allprotected=1 we can access to protected data members
#          but non virtual protected method can not be accessed
#          a turnaround is to derive a class (PyCCD) wrapping non virtual protected calls
#          to public methods, but then protected data member accesses result in a seg fault !
# NO SIMPLE SOLUTION here
#class CCDSimulator(PyIndiDriver.PyCCD):
class CCDSimulator(PyIndiDriver.CCD):
    def __init__(self):
        super(CCDSimulator, self).__init__()
        #PyIndiDriver.PyCCD.__init__(self)
        #self.RA=0.0
        self.name='PyCCD Simulator'
        self.AbortGuideFrame=False
        self.AbortPrimaryFrame = False
        self.ShowStarField=True
        self.timefactor=1.0
        self.InExposure=False
        self.ExposureRequest=1.0
        # CCD Capability is nested structure in C++ class: capability not supported by swig
        self.cap=PyIndiDriver.CCDCapability()
        self.cap.canAbort = True
        self.cap.canBin = True
        self.cap.canSubFrame = True
        self.cap.hasCooler = False
        self.cap.hasGuideHead = True
        self.cap.hasShutter = True
        self.cap.hasST4Port = True
        # no way: capability is private, SetCapability is protected (can not extend for Python)
        #self.setCCDCapability(self.cap)
        #self.SetCapability(self.cap)

        # it is unuseful to keep these objetcs as they are not synchronized with C++ real data
        self.SimulatorSettingsNV = PyIndi.INumberVectorProperty()
        self.SimulatorSettingsN = [PyIndi.INumber() for x in range(13)]
        self.TimeFactorSV = PyIndi.ISwitchVectorProperty()
        self.TimeFactorS = [PyIndi.ISwitch() for x in range(3)]
        self.logger = logging.getLogger('PyIndiDriver.CCD')
        self.logger.info('creating an instance of PyIndiDriver.CCD')
    def ISGetProperties (self, dev):
        self.logger.info("ISGetProperties " + str(dev))
        super(CCDSimulator, self).ISGetProperties(dev)
        self.defineNumber(self.SimulatorSettingsNV)
        self.defineSwitch(self.TimeFactorSV)
    def getDefaultName(self):
        return self.name
    # Always overload getDriverName as the current C implementation is unsecure with SWIG?
    def getDriverName(self):
        #self.logger.info("getDriverName "+ self.name)
        return os.path.basename(__file__)
    def initProperties(self):
        self.logger.info("initProperties "+self.getDefaultName())
        super(CCDSimulator, self).initProperties()
        
        PyIndiDriver.IUFillNumber(self.SimulatorSettingsN[0],"SIM_XRES","CCD X resolution","%4.0f",0,2048,0,1280)
        PyIndiDriver.IUFillNumber(self.SimulatorSettingsN[1],"SIM_YRES","CCD Y resolution","%4.0f",0,2048,0,1024)
        PyIndiDriver.IUFillNumber(self.SimulatorSettingsN[2],"SIM_XSIZE","CCD X Pixel Size","%4.2f",0,60,0,5.2)
        PyIndiDriver.IUFillNumber(self.SimulatorSettingsN[3],"SIM_YSIZE","CCD Y Pixel Size","%4.2f",0,60,0,5.2)
        PyIndiDriver.IUFillNumber(self.SimulatorSettingsN[4],"SIM_MAXVAL","CCD Maximum ADU","%4.0f",0,65000,0,65000)
        PyIndiDriver.IUFillNumber(self.SimulatorSettingsN[5],"SIM_BIAS","CCD Bias","%4.0f",0,6000,0,10)
        PyIndiDriver.IUFillNumber(self.SimulatorSettingsN[6],"SIM_SATURATION","Saturation Mag","%4.1f",0,20,0,1.0)
        PyIndiDriver.IUFillNumber(self.SimulatorSettingsN[7],"SIM_LIMITINGMAG","Limiting Mag","%4.1f",0,20,0,17.0)
        PyIndiDriver.IUFillNumber(self.SimulatorSettingsN[8],"SIM_NOISE","CCD Noise","%4.0f",0,6000,0,10)
        PyIndiDriver.IUFillNumber(self.SimulatorSettingsN[9],"SIM_SKYGLOW","Sky Glow (magnitudes)","%4.1f",0,6000,0,19.5)
        PyIndiDriver.IUFillNumber(self.SimulatorSettingsN[10],"SIM_OAGOFFSET","Oag Offset (arcminutes)","%4.1f",0,6000,0,0)
        PyIndiDriver.IUFillNumber(self.SimulatorSettingsN[11],"SIM_POLAR","PAE (arcminutes)","%4.1f",-600,600,0,0)
        PyIndiDriver.IUFillNumber(self.SimulatorSettingsN[12],"SIM_POLARDRIFT","PAE Drift (minutes)","%4.1f",0,6000,0,0)
        cnumbers=PyIndiDriver.new_INumberArray(13)
        for i in range(len(self.SimulatorSettingsN)):
            PyIndiDriver.INumberArray_setitem(cnumbers, i, self.SimulatorSettingsN[i])
        PyIndiDriver.IUFillNumberVector(self.SimulatorSettingsNV,cnumbers,13,self.getDeviceName(),"SIMULATOR_SETTINGS","Simulator Settings","Simulator Config",PyIndi.IP_RW,60,PyIndi.IPS_IDLE)
        PyIndiDriver.IUFillSwitch(self.TimeFactorS[0],"1X","Actual Time",PyIndi.ISS_ON)
        PyIndiDriver.IUFillSwitch(self.TimeFactorS[1],"10X","10x",PyIndi.ISS_OFF)
        PyIndiDriver.IUFillSwitch(self.TimeFactorS[2],"100X","100x",PyIndi.ISS_OFF)
        cswitchs=PyIndiDriver.new_ISwitchArray(3)
        for i in range(len(self.TimeFactorS)):
            PyIndiDriver.ISwitchArray_setitem(cswitchs, i, self.TimeFactorS[i])
        PyIndiDriver.IUFillSwitchVector(self.TimeFactorSV,cswitchs,3,self.getDeviceName(),"ON_TIME_FACTOR","Time Factor","Simulator Config",PyIndi.IP_RW,PyIndi.ISR_1OFMANY,60,PyIndi.IPS_IDLE)
        self.addDebugControl()
        logProperties(self)
        return True
    def updateProperties(self):
        self.logger.info("updateProperties "+self.getDefaultName())
        super(CCDSimulator, self).updateProperties()
        logProperties(self)
        return True
    def Connect(self):
        self.logger.info("Connect "+self.getDefaultName())
        self.SetTimer(1000)
        return True
    def Disconnect(self):
        self.logger.info("Disconnect "+self.getDefaultName())
        return True
    def ISNewNumber (self, dev, name, values, names, n):
        if (dev != self.name):
            return False    
        self.logger.info("ISNewNumber " + dev + " property " + name)
        nvp=self.getNumber(name)
        if not nvp:
            return False
        if name == 'SIMULATOR_SETTINGS':
            cvalues=PyIndiDriver.new_doubleArray(n)
            for i in range(len(values)):
                self.logger.info('  ' + names[i] + ' = ' + str(values[i])) 
                PyIndiDriver.doubleArray_setitem(cvalues, i, values[i])
            PyIndiDriver.IUUpdateNumber(nvp, cvalues, names, n)
            nvp.s=PyIndi.IPS_OK
            # Reset our parameters now
            #SetupParms();
            PyIndiDriver.IDSetNumber(nvp,None)
            #saveConfig();
            #IDLog("Frame set to %4.0f,%4.0f %4.0f x %4.0f\n",CcdFrameN[0].value,CcdFrameN[1].value,CcdFrameN[2].value,CcdFrameN[3].value);
            #self.seeing=nvp[0].value
            return True
        cvalues=PyIndiDriver.new_doubleArray(n)
        for i in range(len(values)):
            self.logger.info('  ' + names[i] + ' = ' + str(values[i])) 
            PyIndiDriver.doubleArray_setitem(cvalues, i, values[i])
        if super(CCDSimulator, self).ISNewNumber(dev, name, cvalues, names, n):
            return True
        return False
    def ISNewText (self, dev, name, texts, names, n):
        if (dev != self.name):
            return False    
        self.logger.info("ISNewText " + dev + " property " + name)

        if super(CCDSimulator, self).ISNewText(dev, name, texts, names, n):
            return True
        return False
    def ISNewSwitch (self, dev, name, states, names, n):
        if (dev != self.name):
            return False    
        self.logger.info("ISNewSwitch " + dev + " property " + name)
        # Always fetch data from C++ world
        svp=self.getSwitch(name)
        if not svp:
            return False
        cstates=PyIndiDriver.new_ISStateArray(n)
        for i in range(len(states)):
            self.logger.info('  '+names[i] + ' = ' + str(states[i]))
            PyIndiDriver.ISStateArray_setitem(cstates, i, states[i])
        if name == 'ON_TIME_FACTOR':
             svp.s=PyIndi.IPS_OK
             PyIndiDriver.IUUpdateSwitch(svp,cstates,names,n)
             # Update client display
             PyIndiDriver.IDSetSwitch(svp,None)
             #saveConfig();
             if svp[0].s==PyIndi.ISS_ON:
                     PyIndiDriver.IDLog("CCDSim:: Time Factor 1\n")
                     self.timefactor=1.0
             if svp[1].s==PyIndi.ISS_ON:
                     PyIndiDriver.IDLog("CCDSim:: Time Factor 0.1\n")
                     self.timefactor=0.1
             if svp[2].s==PyIndi.ISS_ON:
                     PyIndiDriver.IDLog("CCDSim:: Time Factor 0.01\n")
                     self.timefactor=0.01
             return True 
        if super(CCDSimulator, self).ISNewSwitch(dev, name, cstates, names, n):
            return True
        return False
    def StartExposure(self, duration):
        self.logger.info("StartExposure " + self.name +': '+str(duration)+'s')
        self.AbortPrimaryFrame=False
        self.ExposureRequest=duration
        self.PrimaryCCD.setExposureDuration(duration)
        self.ExpStart=time.time()
        self.DrawCCDFrame(self.PrimaryCCD)
        self.InExposure=True
        return True
    def AbortExposure(self):
        if not self.InExposure:
            return True
        self.AbortPrimaryFrame=True
        return True
    def CalcTimeLeft(self, start, req):
        now=time.time()
        timesince=now-start
        timeleft=req-timesince
        return timeleft
    def TimerHit(self):
        self.nexttimer=1000
        if not self.isConnected():
            return 
        if self.InExposure:
            if self.AbortPrimaryFrame:
                self.InExposure=False
                self.AbortPrimaryFrame=False
            else:
                timeleft=self.CalcTimeLeft(self.ExpStart, self.ExposureRequest)
                if timeleft < 0.0:
                    timeleft=0.0
                self.PrimaryCCD.setExposureLeft(timeleft)
                if timeleft < 1.0:
                        if timeleft <= 0.001:
                            self.InExposure=False
                            self.ExposureComplete(self.PrimaryCCD)
                        else:
                            self.nexttimer=int(timeleft*1000) # set a shorter timer
        self.SetTimer(self.nexttimer)
        return 
    def DrawCCDFrame(self, targetChip):
        return

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

ccd=CCDSimulator()

PyIndiDriver.driver_run()
#indidriver.ISNewSwitch("Python Simple Skeleton", "CONNECTION", [0, 1], ["CONNECT", "DISCONNECT"], 1)

# test
#import PyIndi
#import PyIndiDriver
#ion=[PyIndi.INumber() for x in range(13)]
#PyIndiDriver.IUFillNumber(ion[0],"SIM_XRES","CCD X resolution","%4.0f",0,2048,0,1280)
#PyIndiDriver.IUFillNumber(ion[1],"SIM_YRES","CCD Y resolution","%4.0f",0,2048,0,1024)
#ionv=PyIndi.INumberVectorProperty()
#PyIndiDriver.IUFillNumberVector(ionv, ion,13,"to","SI","Si","Sic",PyIndi.IP_RW, 60, PyIndi.IPS_IDLE)
