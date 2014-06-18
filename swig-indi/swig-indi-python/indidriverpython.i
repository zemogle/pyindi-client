%module(directors="1",allprotected="1") PyIndiDriver
//%module(directors="1") PyIndiDriver

%rename(indi_main) main;

%{
#include <Python.h>
#include <indibase.h>
#include <indiapi.h>
#include <lilxml.h>
#include <eventloop.h>
#include <indidevapi.h>
#include <basedevice.h>
#include <indilogger.h>
#include <indidriver.h>
#include <defaultdevice.h>
#include <memory.h>

#include <fitsio.h>
#include <indiguiderinterface.h>
#include <indiccd.h>

#include <stdexcept>
  /*
class PyCCD: public INDI::CCD {
 public:
  bool InExposure;
  //CCDChip PrimaryCCD;
  PyCCD(): INDI::CCD() {
  IDLog("PyCCD constructor Ver %d.%d\n", this->getMajorVersion(), this->getMinorVersion());
  }
  virtual ~PyCCD() {
  }
  bool PyExposureComplete(CCDChip *targetChip) {
    IDLog("PyExposureComplete C++\n");
    return ExposureComplete(targetChip);
  }

 };
  */
%}
%include "std_vector.i"
%include "std_except.i"

%template(PropertyVector) std::vector<INDI::Property *>;

%include "std_string.i"
%include "carrays.i"

%typemap(in) char *formats[], char *names[], char *blobs[], char *texts[] {
  /* Check if is a list */
  if (PyList_Check($input)) {
    int size = PyList_Size($input);
    int i = 0;
    $1 = (char **) malloc((size+1)*sizeof(char *));
    for (i = 0; i < size; i++) {
      PyObject *o = PyList_GetItem($input,i);
      if (PyString_Check(o))
	$1[i] = PyString_AsString(PyList_GetItem($input,i));
      else {
	PyErr_SetString(PyExc_TypeError,"list must contain strings");
	free($1);
	return NULL;
      }
    }
    $1[i] = 0;
  } else {
    PyErr_SetString(PyExc_TypeError,"not a list");
    return NULL;
  }
}

// This cleans up the char ** array we malloc'd before the function call
%typemap(freearg) char *formats[], char *names[], char *blobs[], char *texts[] {
  free((char *) $1);
}

// Now these are to be manually wrapped in Python using I*Array functions
// For IUFillNumberVector, could check $symname
/*
%typemap(in) INumber *nonp {
  int size = 1; 
  /* Check if is a list /
  if (PyList_Check($input)) { 
    size = PyList_Size($input);
    int i = 0;
    $1 = (INumber *) malloc((size)*sizeof(INumber));
    for (i = 0; i < size; i++) {
      PyObject *o = PyList_GetItem($input,i);
      try {
	strncpy($1[i].name, PyString_AsString(PyObject_GetAttrString(o, "name")), MAXINDINAME);
	strncpy($1[i].label, PyString_AsString(PyObject_GetAttrString(o, "label")), MAXINDILABEL);
	strncpy($1[i].format, PyString_AsString(PyObject_GetAttrString(o, "format")), MAXINDIFORMAT);
	$1[i].min = PyFloat_AsDouble(PyObject_GetAttrString(o,"min"));
	$1[i].max = PyFloat_AsDouble(PyObject_GetAttrString(o,"max"));
	$1[i].step = PyFloat_AsDouble(PyObject_GetAttrString(o,"step"));
	$1[i].value = PyFloat_AsDouble(PyObject_GetAttrString(o,"value"));
      }
      catch (...){
	PyErr_SetString(PyExc_TypeError,"list must contain INumbers");
	free($1);
	return NULL;
      }
    }
  } else {
    $1 = (INumber *) malloc(sizeof(INumber));
    PyObject *o = $input;
    try {
	strncpy($1->name, PyString_AsString(PyObject_GetAttrString(o, "name")), MAXINDINAME);
	strncpy($1->label, PyString_AsString(PyObject_GetAttrString(o, "label")), MAXINDILABEL);
	strncpy($1->format, PyString_AsString(PyObject_GetAttrString(o, "format")), MAXINDIFORMAT);
	$1->min = PyFloat_AsDouble(PyObject_GetAttrString(o,"min"));
	$1->max = PyFloat_AsDouble(PyObject_GetAttrString(o,"max"));
	$1->step = PyFloat_AsDouble(PyObject_GetAttrString(o,"step"));
	$1->value = PyFloat_AsDouble(PyObject_GetAttrString(o,"value"));
      }
      catch (...){
	PyErr_SetString(PyExc_TypeError,"object must contain INumber");
	free($1);
	return NULL;
      }
  }
}
*/
// This cleans up the char ** array we malloc'd before the function call
//%typemap(freearg) INumber *np {
//  free((INumber *) $1);
//}

/*
%typemap(in) double * {
  /* Check if is a list /
  if (PyList_Check($input)) {
    int size = PyList_Size($input);
    int i = 0;
    $1 = (double *) malloc((size)*sizeof(double));
    for (i = 0; i < size; i++) {
      PyObject *o = PyList_GetItem($input,i);
      if (PyFloat_Check(o))
	$1[i] = PyFloat_AsDouble(PyList_GetItem($input,i));
      else {
	PyErr_SetString(PyExc_TypeError,"list must contain strings");
	free($1);
	return NULL;
      }
    }
    $1[i] = 0;
  } else {
    PyErr_SetString(PyExc_TypeError,"not a list");
    return NULL;
  }
}

// This cleans up the char ** array we malloc'd before the function call
%typemap(freearg) double * {
  free((double *) $1);
}

*/
//%import "indiclientpython.i"

%feature("director") ;
%feature("nodirector") BaseDevice;
//%feature("nodirector") CCD;

%feature("director:except") {
    if( $error != NULL ) {
        PyObject *ptype, *pvalue, *ptraceback;
        PyErr_Fetch( &ptype, &pvalue, &ptraceback );
        PyErr_Restore( ptype, pvalue, ptraceback );
        PyErr_Print();
	// Py_Exit(1);
    }
}
%include <indibase.h>
%include <indiapi.h>
%include <lilxml.h>
%include <eventloop.h>
%include <basedevice.h>
%include <indidevapi.h>
%include <indidriver.h>
%include <defaultdevice.h>
 //%include <fitsio.h>
%include <indiguiderinterface.h>
%include <indiccd.h>
 /*
class PyCCD: public INDI::CCD {
 public:
  bool InExposure;
  //CCDChip PrimaryCCD;
  PyCCD(): INDI::CCD() {
  IDLog("PyCCD constructor Ver %d.%d\n", this->getMajorVersion(), this->getMinorVersion());
  }
  virtual ~PyCCD() {
  }
  bool PyExposureComplete(CCDChip *targetChip) {
    IDLog("PyExposureComplete C++\n");
    return ExposureComplete(targetChip);
  }

 };
 */

%array_functions(ISState, ISStateArray);
%array_functions(double, doubleArray);
%array_functions(int, intArray);
%array_functions(IText, ITextArray);
%array_functions(INumber, INumberArray);
%array_functions(ILight, ILightArray);
%array_functions(ISwitch, ISwitchArray);
%array_functions(IBLOB, IBLOBArray);

%pythoncode %{
class CCDCapability:
    def __init__(self):
        self.canAbort = False
        self.canBin = False
        self.canSubFrame = False
	self.hasCooler = False
	self.hasGuideHead = False
	self.hasShutter = False
	self.hasST4Port = False 
 %}

%inline %{


  void callPythonGlobal(const char *fname, PyObject *pArgs) {
    PyObject *main_module, *global_dict, *pFunc, *pValue;    
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();

    main_module = PyImport_AddModule("__main__");
    if (main_module)
      global_dict = PyModule_GetDict(main_module);
    else
      fprintf(stderr, "no __main__ module found\n");

    pFunc=PyDict_GetItemString(global_dict, fname);
    if (pFunc && PyCallable_Check(pFunc)) {
      fprintf(stderr, "calling function \"%s\"\n", fname);
      pValue=PyObject_CallObject(pFunc, pArgs);
      if (!pValue) {
	if (PyErr_Occurred())
	  PyErr_Print();
	fprintf(stderr, "Python function call \"%s\" failed\n", fname);
      } else 
	return;
    } else {
      if (PyErr_Occurred())
	PyErr_Print();
      fprintf(stderr, "Cannot find function \"%s\"\n", fname);
    }

    Py_XDECREF(pFunc);
    Py_DECREF(global_dict);
    Py_DECREF(main_module);
    PyGILState_Release(gstate);
  
  }

  void ISGetProperties (const char *dev) {
    PyObject *main_module, *global_dict, *pFunc, *pValue;    
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();

    main_module = PyImport_AddModule("__main__");
    if (main_module)
      global_dict = PyModule_GetDict(main_module);
    else
      fprintf(stderr, "no globals module \"%s\"\n", "ISGetProperties");

    pFunc=PyDict_GetItemString(global_dict, "ISGetProperties");
    if (pFunc && PyCallable_Check(pFunc)) {
      fprintf(stderr, "calling function \"%s\"\n", "ISGetProperties");
      pValue=PyObject_CallFunction(pFunc, "s", dev);
      if (!pValue) {
	if (PyErr_Occurred())
	  PyErr_Print();
	fprintf(stderr, "Python function call \"%s\" failed\n", "ISGetProperties");
      } else 
	return;
    } else {
      if (PyErr_Occurred())
	PyErr_Print();
      fprintf(stderr, "Cannot find function \"%s\"\n", "ISGetProperties");
    }

    Py_XDECREF(pFunc);
    Py_DECREF(global_dict);
    Py_DECREF(main_module);
    PyGILState_Release(gstate);
  
  }

  void ISNewText (const char *dev, const char *name, char *texts[], char *names[], int n) {
    PyObject *pArgs, *pValue;
    int i;
    pArgs = PyTuple_New(5);
    PyTuple_SetItem(pArgs, 0, PyString_FromString(dev));
    PyTuple_SetItem(pArgs, 1, PyString_FromString(name));
    pValue = PyList_New(n);
    for (i=0; i < n; i++)
      PyList_SetItem(pValue, i, PyString_FromString(*(texts + i)));
    PyTuple_SetItem(pArgs, 2, pValue);
    pValue = PyList_New(n);
    for (i=0; i < n; i++)
      PyList_SetItem(pValue, i, PyString_FromString(*(names + i)));
    PyTuple_SetItem(pArgs, 3, pValue);
    PyTuple_SetItem(pArgs, 4, PyInt_FromLong(n));
    callPythonGlobal("ISNewText", pArgs);
  }

  void ISNewNumber (const char *dev, const char *name, double *doubles, char *names[], int n) {
    PyObject *pArgs, *pValue;
    int i;
    pArgs = PyTuple_New(5);
    PyTuple_SetItem(pArgs, 0, PyString_FromString(dev));
    PyTuple_SetItem(pArgs, 1, PyString_FromString(name));
    pValue = PyList_New(n);
    for (i=0; i < n; i++)
      PyList_SetItem(pValue, i, PyFloat_FromDouble(*(doubles + i)));
    PyTuple_SetItem(pArgs, 2, pValue);
    pValue = PyList_New(n);
    for (i=0; i < n; i++)
      PyList_SetItem(pValue, i, PyString_FromString(*(names + i)));
    PyTuple_SetItem(pArgs, 3, pValue);
    PyTuple_SetItem(pArgs, 4, PyInt_FromLong(n));
    callPythonGlobal("ISNewNumber", pArgs);
  }

  void ISNewSwitch (const char *dev, const char *name, ISState *states, char *names[], int n) {
    PyObject *pArgs, *pValue;;
    int i;
    pArgs = PyTuple_New(5);
    PyTuple_SetItem(pArgs, 0, PyString_FromString(dev));
    PyTuple_SetItem(pArgs, 1, PyString_FromString(name));
    pValue = PyList_New(n);
    for (i=0; i < n; i++) {
      PyList_SetItem(pValue, i, Py_BuildValue("B", *(states + i)));
    }
    PyTuple_SetItem(pArgs, 2, pValue);
    pValue = PyList_New(n);
    for (i=0; i < n; i++)
      PyList_SetItem(pValue, i, PyString_FromString(*(names + i)));
    PyTuple_SetItem(pArgs, 3, pValue);
    PyTuple_SetItem(pArgs, 4, PyInt_FromLong(n));
    callPythonGlobal("ISNewSwitch", pArgs);
  }
  
  void ISNewBLOB (const char *dev, const char *name, int sizes[], int blobsizes[], char *blobs[], char *formats[], char *names[], int n) {
    PyObject *pArgs, *pValue;;
    int i;
    pArgs = PyTuple_New(8);
    PyTuple_SetItem(pArgs, 0, PyString_FromString(dev));
    PyTuple_SetItem(pArgs, 1, PyString_FromString(name));
    pValue = PyList_New(n);
    for (i=0; i < n; i++) {
      PyList_SetItem(pValue, i, Py_BuildValue("i", *(sizes + i)));
    }
    PyTuple_SetItem(pArgs, 2, pValue);
    pValue = PyList_New(n);
    for (i=0; i < n; i++) {
      PyList_SetItem(pValue, i, Py_BuildValue("i", *(blobsizes + i)));
    }
    PyTuple_SetItem(pArgs, 3, pValue);
    pValue = PyList_New(n);
    for (i=0; i < n; i++) {
      PyList_SetItem(pValue, i, PyString_FromStringAndSize(*(blobs + i), *(blobsizes + i)));
    }
    PyTuple_SetItem(pArgs, 4, pValue);
    pValue = PyList_New(n);
    for (i=0; i < n; i++)
      PyList_SetItem(pValue, i, PyString_FromString(*(formats + i)));
    PyTuple_SetItem(pArgs, 5, pValue);
    pValue = PyList_New(n);
    for (i=0; i < n; i++)
      PyList_SetItem(pValue, i, PyString_FromString(*(names + i)));
    PyTuple_SetItem(pArgs, 6, pValue);
    PyTuple_SetItem(pArgs, 7, PyInt_FromLong(n));
    callPythonGlobal("ISNewBLOB", pArgs);
  }

  void ISSnoopDevice (XMLEle *root) {
    

  }

  void driver_run() {
    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();
    clixml = newLilXML();
    addCallback (0, clientMsgCB, NULL);
    /* service client */
    PyGILState_Release(gstate); //release python GIL ??
    eventLoop(); 
    //PyGILState_Release(gstate); //release python GIL
  }

  /*
  void INDI::DefaultDevice::TimerHit() {
    //INDI::CCD *ccdptr = static_cast<INDI::CCD *>(this);
    IDLog("TimerHit overloaded\n");
    //ccdptr->TimerHit();
    //SwigDirector_DefaultDevice::TimerHit();
  }
  */

  // extern in lilxml.h, but seems to be called lilxmlMalloc in lilxml.c
  // prevents module to load...
  void indi_xmlMalloc (void *(*newmalloc)(size_t size),
		       void *(*newrealloc)(void *ptr, size_t size), void (*newfree)(void *ptr)) {
  }

  void CCDChip::setCompressed(bool cmp) {

  }
 
  %}

%extend _ITextVectorProperty {
  void __setitem__(int index, IText t) throw(std::out_of_range) {
    if (index >= $self->ntp) throw std::out_of_range("VectorProperty index out of bounds");
    *($self->tp + index) = t;
  }
  IText *__getitem__(int index) throw(std::out_of_range) {
    if (index >= $self->ntp) throw std::out_of_range("VectorProperty index out of bounds");
    return $self->tp + index;
  }
  int __len__() {
    return $self->ntp;
  }
 };
%extend _INumberVectorProperty {
  void __setitem__(int index, INumber n) throw(std::out_of_range) {
    if (index >= $self->nnp) throw std::out_of_range("VectorProperty index out of bounds");
    *($self->np + index) = n;
  }
  INumber *__getitem__(int index) throw(std::out_of_range) {
    if (index >= $self->nnp) throw std::out_of_range("VectorProperty index out of bounds");
    return $self->np + index;
  }
  int __len__() {
    return $self->nnp;
  }
 };
%extend _ILightVectorProperty {
  void __setitem__(int index, ILight l) throw(std::out_of_range) {
    if (index >= $self->nlp) throw std::out_of_range("VectorProperty index out of bounds");
    *($self->lp + index) = l;
  }
  ILight *__getitem__(int index) throw(std::out_of_range) {
    if (index >= $self->nlp) throw std::out_of_range("VectorProperty index out of bounds");
    return $self->lp + index;
  }
  int __len__() {
    return $self->nlp;
  }
 };
%extend _ISwitchVectorProperty {
  void __setitem__(int index, ISwitch s) throw(std::out_of_range) {
    if (index >= $self->nsp) throw std::out_of_range("VectorProperty index out of bounds");
    *($self->sp + index) = s;
  }
  ISwitch *__getitem__(int index) throw(std::out_of_range) {
    if (index >= $self->nsp) throw std::out_of_range("VectorProperty index out of bounds");
    return $self->sp + index;
  }
  int __len__() {
    return $self->nsp;
  }
 };
%extend _IBLOBVectorProperty {
  void __setitem__(int index, IBLOB b) throw(std::out_of_range) {
    if (index >= $self->nbp) throw std::out_of_range("VectorProperty index out of bounds");
    *($self->bp + index) = b;
  }
  IBLOB *__getitem__(int index) throw(std::out_of_range) {
    if (index >= $self->nbp) throw std::out_of_range("VectorProperty index out of bounds");
    return $self->bp + index;
  }
  int __len__() {
    return $self->nbp;
  }
 };

/* Don't work: capability private, SetCapability protected */
/*
%extend INDI::CCD {
  void INDI::CCD::setCCDCapability(PyObject *pycap) {
    INDI::CCD::Capability capability ;
    if (PyObject_GetAttrString(pycap,"canAbort") == Py_True) capability.canAbort=true;
    else  capability.canAbort=false;
    if (PyObject_GetAttrString(pycap,"canBin") == Py_True) capability.canBin=true;
    else  capability.canBin=false;
    if (PyObject_GetAttrString(pycap,"canSubFrame") == Py_True) capability.canSubFrame=true;
    else  capability.canSubFrame=false;
    if (PyObject_GetAttrString(pycap,"hasCooler") == Py_True) capability.hasCooler=true;
    else  capability.hasCooler=false;
    if (PyObject_GetAttrString(pycap,"hasGuideHead") == Py_True) capability.hasGuideHead=true;
    else  capability.hasGuideHead=false;
    if (PyObject_GetAttrString(pycap,"hasShutter") == Py_True) capability.hasShutter=true;
    else  capability.hasShutter=false;
    if (PyObject_GetAttrString(pycap,"hasST4Port") == Py_True) capability.hasST4Port=true;
    else  capability.hasST4Port=false;
    $self->SetCapability(&capability);
  }
 };

*/
