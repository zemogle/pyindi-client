%module(directors="1") indiclientnodejs

%{
#include <indibase.h>
#include <indiapi.h>
#include <baseclient.h>
#include <basedevice.h>
#include <indiproperty.h>

#include <stdexcept>

#include <node.h>
#include <node_object_wrap.h>

#include "baseclientimpl.h"
%}

%include "std_vector.i"
%include "std_except.i"

%feature("director") BaseClientImpl;

//Warning 451
%typemap(varin) const char * {
   SWIG_Error(SWIG_AttributeError,"Variable $symname is read-only.");
   SWIG_fail;
}

%typemap(in) (v8::Handle<v8::Function> func) {
  $1 = v8::Local<v8::Function>::Cast($input);
}


%template(BaseDeviceVector) std::vector<INDI::BaseDevice *>;
%template(PropertyVector) std::vector<INDI::Property *>;

%ignore ISwitchVectorProperty::sp;
%ignore ITextVectorProperty::tp;
%ignore INumberVectorProperty::np;
%ignore ILightVectorProperty::lp;
%ignore IBlobVectorProperty::bp;

%include <indibasetypes.h>
%include <indibase.h>
%include <indiapi.h>
%include <baseclient.h>
%include <basedevice.h>
%include <indiproperty.h>

%include "baseclientimpl.h"

typedef enum {
B_NEVER=0,
B_ALSO,
B_ONLY
} BLOBHandling;

%extend _ISwitchVectorProperty {
 ISwitch *getISwitch(int index) throw (std::out_of_range) {
  if ((index < 0) || (index >= $self->nsp)) {
    throw std::out_of_range("vector property index out of range");
  } 
  return $self->sp + index;
 }
}
%extend _ITextVectorProperty {
 IText *getIText(int index) throw (std::out_of_range) {
  if ((index < 0) || (index >= $self->ntp)) {
    throw std::out_of_range("vector property index out of range");
  } 
  return $self->tp + index;
 }
}
%extend _INumberVectorProperty {
 INumber *getINumber(int index) throw (std::out_of_range) {
  if ((index < 0) || (index >= $self->nnp)) {
    throw std::out_of_range("vector property index out of range");
  } 
  return $self->np + index;
 }
}
%extend _ILightVectorProperty {
 ILight *getILight(int index) throw (std::out_of_range) {
  if ((index < 0) || (index >= $self->nlp)) {
    throw std::out_of_range("vector property index out of range");
  } 
  return $self->lp + index;
 }
}
%extend _IBLOBVectorProperty {
 IBLOB *getIBlob(int index) throw (std::out_of_range) {
  if ((index < 0) || (index >= $self->nbp)) {
    throw std::out_of_range("vector property index out of range");
  } 
  return $self->bp + index;
 }
}

// use if you need some module initialization
//%init %{
//  BaseClientImpl::Initialize(SWIGV8_CURRENT_CONTEXT()->Global());
//  %}

%{

using namespace v8;

// Performs effective calls from the node event loop (queued by implemented C++ callbacks ) 
void BaseClientImpl::nop(uv_work_t* req) {
}

 void BaseClientImpl::newDeviceCallback(uv_work_t* req, int status) {
   struct data {
    void * member;
    INDI::BaseDevice *dp;
  } *data = (struct data *)req->data;
  BaseClientImpl * This=(BaseClientImpl *)data->member;
  INDI::BaseDevice *dp=(INDI::BaseDevice *)data->dp;

  if (!This->newDeviceCallback_->IsFunction())
    return;

  const unsigned argc = 1;
    Handle<Value> argv[argc] = {
      SWIG_NewPointerObj(SWIG_as_voidptr(dp), SWIGTYPE_p_INDI__BaseDevice, 0 |  0 )
  };


  Handle<Function> cb = Persistent<Function>::Cast(This->newDeviceCallback_);

  cb->Call(Context::GetCurrent()->Global(), argc, argv);
  free(req->data);
  delete req;
}

void BaseClientImpl::removeDeviceCallback(uv_work_t* req, int status) {
  struct data {
    void * member;
    INDI::BaseDevice *dp;
  } *data = (struct data *)req->data;
  BaseClientImpl * This=(BaseClientImpl *)data->member;
  INDI::BaseDevice *dp=(INDI::BaseDevice *)data->dp;
  if (!This->removeDeviceCallback_->IsFunction())
    return;

  const unsigned argc = 1;
    Handle<Value> argv[argc] = {
      SWIG_NewPointerObj(SWIG_as_voidptr(dp), SWIGTYPE_p_INDI__BaseDevice, 0 |  0 )
  };


  Handle<Function> cb = Persistent<Function>::Cast(This->removeDeviceCallback_);
    
  cb->Call(Context::GetCurrent()->Global(), argc, argv);
  free(req->data);
  delete req;
}

void BaseClientImpl::newPropertyCallback(uv_work_t* req, int status) {
  struct data {
    void * member;
    INDI::Property *p;
  } *data = (struct data *)req->data;
  BaseClientImpl * This=(BaseClientImpl *)data->member;
  INDI::Property *p=(INDI::Property *)data->p;
  if (!This->newPropertyCallback_->IsFunction())
    return;

  const unsigned argc = 1;
    Handle<Value> argv[argc] = {
      SWIG_NewPointerObj(SWIG_as_voidptr(p), SWIGTYPE_p_INDI__Property, 0 |  0 )
  };


  Handle<Function> cb = Persistent<Function>::Cast(This->newPropertyCallback_);
    
  cb->Call(Context::GetCurrent()->Global(), argc, argv);
  free(req->data);
  delete req;
}

void BaseClientImpl::removePropertyCallback(uv_work_t* req, int status) {
  struct data {
    void * member;
    INDI::Property *p;
  } *data = (struct data *)req->data;
  BaseClientImpl * This=(BaseClientImpl *)data->member;
  INDI::Property *p=(INDI::Property *)data->p;
  if (!This->removePropertyCallback_->IsFunction())
    return;

  const unsigned argc = 1;
    Handle<Value> argv[argc] = {
      SWIG_NewPointerObj(SWIG_as_voidptr(p), SWIGTYPE_p_INDI__Property, 0 |  0 )
  };


  Handle<Function> cb = Persistent<Function>::Cast(This->removePropertyCallback_);
    
  cb->Call(Context::GetCurrent()->Global(), argc, argv);
  free(req->data);
  delete req;
}

void BaseClientImpl::newBLOBCallback(uv_work_t* req, int status) {
  struct data {
    void * member;
    IBLOB *bp;
  } *data = (struct data *)req->data;
  BaseClientImpl * This=(BaseClientImpl *)data->member;
  IBLOB *bp=(IBLOB *)data->bp;
  if (!This->newBLOBCallback_->IsFunction())
    return;

  const unsigned argc = 1;
    Handle<Value> argv[argc] = {
      SWIG_NewPointerObj(SWIG_as_voidptr(bp), SWIGTYPE_p_IBLOB, 0 |  0 )
  };


  Handle<Function> cb = Persistent<Function>::Cast(This->newBLOBCallback_);
    
  cb->Call(Context::GetCurrent()->Global(), argc, argv);
  free(req->data);
  delete req;
}

void BaseClientImpl::newSwitchCallback(uv_work_t* req, int status) {
  struct data {
    void * member;
    ISwitchVectorProperty *svp;
  } *data = (struct data *)req->data;
  BaseClientImpl * This=(BaseClientImpl *)data->member;
  ISwitchVectorProperty *svp=(ISwitchVectorProperty *)data->svp;
  if (!This->newSwitchCallback_->IsFunction())
    return;

  const unsigned argc = 1;
    Handle<Value> argv[argc] = {
      SWIG_NewPointerObj(SWIG_as_voidptr(svp), SWIGTYPE_p__ISwitchVectorProperty, 0 |  0 )
  };


  Handle<Function> cb = Persistent<Function>::Cast(This->newSwitchCallback_);
    
  cb->Call(Context::GetCurrent()->Global(), argc, argv);
  free(req->data);
  delete req;
}
void BaseClientImpl::newNumberCallback(uv_work_t* req, int status) {
  struct data {
    void * member;
    INumberVectorProperty *nvp;
  } *data = (struct data *)req->data;
  BaseClientImpl * This=(BaseClientImpl *)data->member;
  INumberVectorProperty *nvp=(INumberVectorProperty *)data->nvp;
  if (!This->newNumberCallback_->IsFunction())
    return;

  const unsigned argc = 1;
    Handle<Value> argv[argc] = {
      SWIG_NewPointerObj(SWIG_as_voidptr(nvp), SWIGTYPE_p__INumberVectorProperty, 0 |  0 )
  };


  Handle<Function> cb = Persistent<Function>::Cast(This->newNumberCallback_);
    
  cb->Call(Context::GetCurrent()->Global(), argc, argv);
  free(req->data);
  delete req;
}
void BaseClientImpl::newTextCallback(uv_work_t* req, int status) {
  struct data {
    void * member;
    ITextVectorProperty *tvp;
  } *data = (struct data *)req->data;
  BaseClientImpl * This=(BaseClientImpl *)data->member;
  ITextVectorProperty *tvp=(ITextVectorProperty *)data->tvp;

  if (!This->newTextCallback_->IsFunction())
    return;

  const unsigned argc = 1;
    Handle<Value> argv[argc] = {
      SWIG_NewPointerObj(SWIG_as_voidptr(tvp), SWIGTYPE_p__ITextVectorProperty, 0 |  0 )
  };


  Handle<Function> cb = Persistent<Function>::Cast(This->newTextCallback_);
    
  cb->Call(Context::GetCurrent()->Global(), argc, argv);
  free(req->data);
  delete req;
}
void BaseClientImpl::newLightCallback(uv_work_t* req, int status) {
  struct data {
    void * member;
    ILightVectorProperty *lvp;
  } *data = (struct data *)req->data;
  BaseClientImpl * This=(BaseClientImpl *)data->member;
  ILightVectorProperty *lvp=(ILightVectorProperty *)data->lvp;
  if (!This->newLightCallback_->IsFunction())
    return;

  const unsigned argc = 1;
    Handle<Value> argv[argc] = {
      SWIG_NewPointerObj(SWIG_as_voidptr(lvp), SWIGTYPE_p__ILightVectorProperty, 0 |  0 )
  };


  Handle<Function> cb = Persistent<Function>::Cast(This->newSwitchCallback_);
    
  cb->Call(Context::GetCurrent()->Global(), argc, argv);
  free(req->data);
  delete req;
}
void BaseClientImpl::newMessageCallback(uv_work_t* req, int status) {
  struct data {
    void * member;
    INDI::BaseDevice *dp;
    int messageID;
  } *data = (struct data *)req->data;
  BaseClientImpl * This=(BaseClientImpl *)data->member;
  INDI::BaseDevice *dp=(INDI::BaseDevice *)data->dp;
  int messageID = data->messageID;

  if (!This->newMessageCallback_->IsFunction())
    return;

  const unsigned argc = 2;
    Handle<Value> argv[argc] = {
      SWIG_NewPointerObj(SWIG_as_voidptr(dp), SWIGTYPE_p_INDI__BaseDevice, 0 |  0 ),
      SWIGV8_INTEGER_NEW(messageID)
  };


  Handle<Function> cb = Persistent<Function>::Cast(This->newMessageCallback_);
    
  cb->Call(Context::GetCurrent()->Global(), argc, argv);
  free(req->data);
  delete req;
}

void BaseClientImpl::serverConnectedCallback(uv_work_t* req, int status) {
  BaseClientImpl *This=(BaseClientImpl *)req->data;
  if (!This->serverConnectedCallback_->IsFunction())
    return;

  const unsigned argc = 0;
  Handle<Value> argv[argc] = {};
  Handle<Function> cb = Persistent<Function>::Cast(This->serverConnectedCallback_);
    
  cb->Call(Context::GetCurrent()->Global(), argc, argv);
  delete req;
}

void BaseClientImpl::serverDisconnectedCallback(uv_work_t* req, int status) {
  struct data {
    void * member;
    int exit_code;
  } *data = (struct data *)req->data;
  BaseClientImpl * This=(BaseClientImpl *)data->member;
  int exit_code = data->exit_code;

  if (!This->serverDisconnectedCallback_->IsFunction())
    return;

  const unsigned argc = 1;
  Handle<Value> argv[argc] = {
    SWIGV8_INTEGER_NEW(exit_code)
  };
  Handle<Function> cb = Persistent<Function>::Cast(This->serverDisconnectedCallback_);
    
  cb->Call(Context::GetCurrent()->Global(), argc, argv);
  free(req->data);
  delete req;
}

 %}

/*
%extend IBLOB {
  PyObject *getblobdata() {
    PyObject *result;

    result = PyByteArray_FromStringAndSize((const char*) $self->blob, $self->size);
    return result;
  }
 }
*/
