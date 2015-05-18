%module(directors="1") indiclientnodejs
//%module(directors="1") indiclientpython
//%module indiclientpython
%{

#include <indibase.h>
#include <indiapi.h>
#include <baseclient.h>
#include <basedevice.h>
#include <indiproperty.h>

#include <stdexcept>
#include <node.h>
#include <node_object_wrap.h>

#include "baseclientwrap.h"
%}

%include "std_vector.i"
%include "std_except.i"

 //%feature("director") BaseClient;
 //%feature("director") BaseClientWrap;

//Warning 451
%typemap(varin) const char * {
   SWIG_Error(SWIG_AttributeError,"Variable $symname is read-only.");
   SWIG_fail;
}

// Memory leak const std::string *
/*
%typemap(out) std::string {
  $result = PyString_FromString($1.c_str());
 } 

%typemap(in) const std::string & (std::string temp) {
  char * buf;
  Py_ssize_t len;
  if (PyString_AsStringAndSize($input, &buf, &len) == -1)
    return NULL;
  temp = std::string(buf, len);
  $1 = &temp;
 }
*/

%template(BaseDeviceVector) std::vector<INDI::BaseDevice *>;
%template(PropertyVector) std::vector<INDI::Property *>;

%include <indibasetypes.h>
%include <indibase.h>
%include <indiapi.h>
%include <baseclient.h>
%include <basedevice.h>
%include <indiproperty.h>

 //%include "baseclientwrap.h"

typedef enum {
B_NEVER=0,
B_ALSO,
B_ONLY
} BLOBHandling;

%init %{
  BaseClientWrap::Initialize(SWIGV8_CURRENT_CONTEXT()->Global());
  %}

%{

  using namespace v8;
void BaseClientImpl::newDevice(INDI::BaseDevice *dp) {

  HandleScope scope;
  
  if (!newDeviceCallback_->IsFunction())
    return;

  const unsigned argc = 1;
    Handle<Value> argv[argc] = {
      SWIG_NewPointerObj(SWIG_as_voidptr(dp), SWIGTYPE_p_INDI__BaseDevice, 0 |  0 )
  };


  Handle<Function> cb = Persistent<Function>::Cast(newDeviceCallback_);
    
  cb->Call(Context::GetCurrent()->Global(), argc, argv);
}
void BaseClientImpl::removeDevice(INDI::BaseDevice *dp) {

  HandleScope scope;
  
  if (!removeDeviceCallback_->IsFunction())
    return;

  const unsigned argc = 1;
    Handle<Value> argv[argc] = {
      SWIG_NewPointerObj(SWIG_as_voidptr(dp), SWIGTYPE_p_INDI__BaseDevice, 0 |  0 )
  };


  Handle<Function> cb = Persistent<Function>::Cast(removeDeviceCallback_);
    
  cb->Call(Context::GetCurrent()->Global(), argc, argv);
}

void BaseClientImpl::newProperty(INDI::Property *p) {

  HandleScope scope;
  
  if (!newPropertyCallback_->IsFunction())
    return;

  const unsigned argc = 1;
    Handle<Value> argv[argc] = {
      SWIG_NewPointerObj(SWIG_as_voidptr(p), SWIGTYPE_p_INDI__Property, 0 |  0 )
  };


  Handle<Function> cb = Persistent<Function>::Cast(newPropertyCallback_);
    
  cb->Call(Context::GetCurrent()->Global(), argc, argv);
}
void BaseClientImpl::removeProperty(INDI::Property *p) {

  HandleScope scope;
  
  if (!removePropertyCallback_->IsFunction())
    return;

  const unsigned argc = 1;
    Handle<Value> argv[argc] = {
      SWIG_NewPointerObj(SWIG_as_voidptr(p), SWIGTYPE_p_INDI__Property, 0 |  0 )
  };


  Handle<Function> cb = Persistent<Function>::Cast(removePropertyCallback_);
    
  cb->Call(Context::GetCurrent()->Global(), argc, argv);
}
void BaseClientImpl::newBLOB(IBLOB *bp) {

  HandleScope scope;
  
  if (!newBLOBCallback_->IsFunction())
    return;

  const unsigned argc = 1;
    Handle<Value> argv[argc] = {
      SWIG_NewPointerObj(SWIG_as_voidptr(bp), SWIGTYPE_p_IBLOB, 0 |  0 )
  };


  Handle<Function> cb = Persistent<Function>::Cast(newBLOBCallback_);
    
  cb->Call(Context::GetCurrent()->Global(), argc, argv);
}

void BaseClientImpl::newSwitch(ISwitchVectorProperty *svp) {

  HandleScope scope;
  
  if (!newSwitchCallback_->IsFunction())
    return;

  const unsigned argc = 1;
    Handle<Value> argv[argc] = {
      SWIG_NewPointerObj(SWIG_as_voidptr(svp), SWIGTYPE_p__ISwitchVectorProperty, 0 |  0 )
  };


  Handle<Function> cb = Persistent<Function>::Cast(newSwitchCallback_);
    
  cb->Call(Context::GetCurrent()->Global(), argc, argv);
}
void BaseClientImpl::newNumber(INumberVectorProperty *nvp) {

  HandleScope scope;
  
  if (!newNumberCallback_->IsFunction())
    return;

  const unsigned argc = 1;
    Handle<Value> argv[argc] = {
      SWIG_NewPointerObj(SWIG_as_voidptr(nvp), SWIGTYPE_p__INumberVectorProperty, 0 |  0 )
  };


  Handle<Function> cb = Persistent<Function>::Cast(newNumberCallback_);
    
  cb->Call(Context::GetCurrent()->Global(), argc, argv);
}
void BaseClientImpl::newText(ITextVectorProperty *tvp) {

  HandleScope scope;
  
  if (!newTextCallback_->IsFunction())
    return;

  const unsigned argc = 1;
    Handle<Value> argv[argc] = {
      SWIG_NewPointerObj(SWIG_as_voidptr(tvp), SWIGTYPE_p__ITextVectorProperty, 0 |  0 )
  };


  Handle<Function> cb = Persistent<Function>::Cast(newTextCallback_);
    
  cb->Call(Context::GetCurrent()->Global(), argc, argv);
}
void BaseClientImpl::newLight(ILightVectorProperty *lvp) {

  HandleScope scope;
  
  if (!newLightCallback_->IsFunction())
    return;

  const unsigned argc = 1;
    Handle<Value> argv[argc] = {
      SWIG_NewPointerObj(SWIG_as_voidptr(lvp), SWIGTYPE_p__ILightVectorProperty, 0 |  0 )
  };


  Handle<Function> cb = Persistent<Function>::Cast(newSwitchCallback_);
    
  cb->Call(Context::GetCurrent()->Global(), argc, argv);
}
void BaseClientImpl::newMessage(INDI::BaseDevice *dp, int messageID) {

  HandleScope scope;
  
  if (!newMessageCallback_->IsFunction())
    return;

  const unsigned argc = 2;
    Handle<Value> argv[argc] = {
      SWIG_NewPointerObj(SWIG_as_voidptr(dp), SWIGTYPE_p_INDI__BaseDevice, 0 |  0 ),
      SWIGV8_INTEGER_NEW(messageID)
  };


  Handle<Function> cb = Persistent<Function>::Cast(newMessageCallback_);
    
  cb->Call(Context::GetCurrent()->Global(), argc, argv);
}
void BaseClientImpl::serverConnected() {
  HandleScope scope;
  
  if (!serverConnectedCallback_->IsFunction())
    return;

  const unsigned argc = 0;
  Handle<Value> argv[argc] = {};
  Handle<Function> cb = Persistent<Function>::Cast(serverConnectedCallback_);
    
  cb->Call(Context::GetCurrent()->Global(), argc, argv);
}

void BaseClientImpl::serverDisconnected(int exit_code) {
  HandleScope scope;
  
  if (!serverConnectedCallback_->IsFunction())
    return;

  const unsigned argc = 1;
  Handle<Value> argv[argc] = {
    SWIGV8_INTEGER_NEW(exit_code)
  };
  Handle<Function> cb = Persistent<Function>::Cast(serverDisconnectedCallback_);
    
  cb->Call(Context::GetCurrent()->Global(), argc, argv);
}

 %}

/*
%extend _ITextVectorProperty {
  IText *__getitem__(int index) throw(std::out_of_range) {
    if (index >= $self->ntp) throw std::out_of_range("VectorProperty index out of bounds");
    return $self->tp + index;
  }
  int __len__() {
    return $self->ntp;
  }
 };
%extend _INumberVectorProperty {
  INumber *__getitem__(int index) throw(std::out_of_range) {
    if (index >= $self->nnp) throw std::out_of_range("VectorProperty index out of bounds");
    return $self->np + index;
  }
  int __len__() {
    return $self->nnp;
  }
 };
%extend _ISwitchVectorProperty {
  ISwitch *__getitem__(int index) throw(std::out_of_range) {
    if (index >= $self->nsp) throw std::out_of_range("VectorProperty index out of bounds");
    return $self->sp + index;
  }
  int __len__() {
    return $self->nsp;
  }
 };
%extend _ILightVectorProperty {
  ILight *__getitem__(int index) throw(std::out_of_range) {
    if (index >= $self->nlp) throw std::out_of_range("VectorProperty index out of bounds");
    return $self->lp + index;
  }
  int __len__() {
    return $self->nlp;
  }
 };
%extend _IBLOBVectorProperty {
  IBLOB *__getitem__(int index) throw(std::out_of_range) {
    if (index >= $self->nbp) throw std::out_of_range("VectorProperty index out of bounds");
    return $self->bp + index;
  }
  int __len__() {
    return $self->nbp;
  }
 };


%extend IBLOB {
  PyObject *getblobdata() {
    PyObject *result;

    result = PyByteArray_FromStringAndSize((const char*) $self->blob, $self->size);
    return result;
  }
 }
*/
