%module(directors="1") PyIndiDriver

%rename(indi_main) main;

%{
#include <Python.h>
#include <lilxml.h>
#include <eventloop.h>
#include <indidevapi.h>
#include <basedevice.h>
#include <indilogger.h>
#include <indidriver.h>
#include <defaultdevice.h>
#include <memory.h>

%}

%include "std_string.i"
%include "carrays.i"

%typemap(in) char *[] {
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
%typemap(freearg) char *[] {
  free((char *) $1);
}

%typemap(in) double * {
  /* Check if is a list */
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
    //$1[i] = 0;
  } else {
    PyErr_SetString(PyExc_TypeError,"not a list");
    return NULL;
  }
}

// This cleans up the char ** array we malloc'd before the function call
%typemap(freearg) double * {
  free((double *) $1);
}


%import "indiclientpython.i"

%feature("director") ;

%include <lilxml.h>
%include <eventloop.h>
%include <indidevapi.h>
%include <basedevice.h>
%include <indidriver.h>
%include <defaultdevice.h>

%array_functions(ISState, ISStateArray);

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
    PyObject *main_module, *global_dict, *pFunc, *pValue;
    main_module = PyImport_AddModule("__main__");
    global_dict = PyModule_GetDict(main_module);

    pFunc=PyDict_GetItemString(global_dict, "ISNewBLOB");
    if (pFunc && PyCallable_Check(pFunc)) {
      fprintf(stderr, "calling function \"%s\"\n", "ISNewBLOB");
      //pValue=PyObject_CallFunction(pFunc, "sschar *format, ...)
    } else {
      if (PyErr_Occurred())
	PyErr_Print();
      fprintf(stderr, "Cannot find function \"%s\"\n", "ISNewBLOB");
    }

    Py_XDECREF(pFunc);
    Py_DECREF(global_dict);
    Py_DECREF(main_module);
  
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

  // extern in lilxml.h, but seems to be called lilxmlMalloc in lilxml.c
  // prevents module to load...
  void indi_xmlMalloc (void *(*newmalloc)(size_t size),
		       void *(*newrealloc)(void *ptr, size_t size), void (*newfree)(void *ptr)) {
  }
 
  %}
