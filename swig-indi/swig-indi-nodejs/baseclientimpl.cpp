#include "baseclientimpl.h"

using namespace v8;

//
// BaseClientImpl()
//

BaseClientImpl::BaseClientImpl() : INDI::BaseClient() {
  // Initialize callbacks as boolean values so we can test if the callback
  // has been set via ->IsFunction() below
  newDeviceCallback_ = Persistent<Boolean>::New(Boolean::New(false));
  removeDeviceCallback_ = Persistent<Boolean>::New(Boolean::New(false));  
  newPropertyCallback_ = Persistent<Boolean>::New(Boolean::New(false));
  removePropertyCallback_ = Persistent<Boolean>::New(Boolean::New(false));
  newBLOBCallback_ = Persistent<Boolean>::New(Boolean::New(false));
  newSwitchCallback_ = Persistent<Boolean>::New(Boolean::New(false));
  newNumberCallback_ = Persistent<Boolean>::New(Boolean::New(false));
  newTextCallback_ = Persistent<Boolean>::New(Boolean::New(false));
  newLightCallback_ = Persistent<Boolean>::New(Boolean::New(false));
  newMessageCallback_ = Persistent<Boolean>::New(Boolean::New(false));
  serverConnectedCallback_ = Persistent<Boolean>::New(Boolean::New(false));
  serverDisconnectedCallback_ = Persistent<Boolean>::New(Boolean::New(false));
}

BaseClientImpl::~BaseClientImpl() {
  newDeviceCallback_.Dispose();
  removeDeviceCallback_.Dispose();
  newPropertyCallback_.Dispose();
  removePropertyCallback_.Dispose();
  newBLOBCallback_.Dispose();
  newSwitchCallback_.Dispose();
  newNumberCallback_.Dispose();
  newTextCallback_.Dispose();
  newLightCallback_.Dispose();
  newMessageCallback_.Dispose();
  serverConnectedCallback_.Dispose();
  serverDisconnectedCallback_.Dispose();
}

// Queue the javascript callbacks in the node event loop
// from the Indi event receiving thread
void BaseClientImpl::newDevice(INDI::BaseDevice *dp) {
  struct data {
    void * member;
    INDI::BaseDevice *dp;
  } *data = (struct data *)malloc(sizeof(struct data));
  data->member=this;
  data->dp=dp;
  uv_work_t* req = new uv_work_t;
  req->data = data;
  uv_queue_work(uv_default_loop(), req, nop, newDeviceCallback);
}
void BaseClientImpl::removeDevice(INDI::BaseDevice *dp) {
  struct data {
    void * member;
    INDI::BaseDevice *dp;
  } *data = (struct data *)malloc(sizeof(struct data));
  data->member=this;
  data->dp=dp;
  uv_work_t* req = new uv_work_t;
  req->data = data;
  uv_queue_work(uv_default_loop(), req, nop, removeDeviceCallback);
}
void BaseClientImpl::newProperty(INDI::Property *p) {
  struct data {
    void * member;
    INDI::Property *p;
  } *data = (struct data *)malloc(sizeof(struct data));
  data->member=this;
  data->p=p;
  uv_work_t* req = new uv_work_t;
  req->data = data;
  uv_queue_work(uv_default_loop(), req, nop, newPropertyCallback);
}
void BaseClientImpl::removeProperty(INDI::Property *p) {
  struct data {
    void * member;
    INDI::Property *p;
  } *data = (struct data *)malloc(sizeof(struct data));
  data->member=this;
  data->p=p;
  uv_work_t* req = new uv_work_t;
  req->data = data;
  uv_queue_work(uv_default_loop(), req, nop, removePropertyCallback);
}
void BaseClientImpl::newBLOB(IBLOB *bp) {
  struct data {
    void * member;
    IBLOB *bp;
  } *data = (struct data *)malloc(sizeof(struct data));
  data->member=this;
  data->bp=bp;
  uv_work_t* req = new uv_work_t;
  req->data = data;
  uv_queue_work(uv_default_loop(), req, nop, newBLOBCallback);
}
void BaseClientImpl::newSwitch(ISwitchVectorProperty *svp) {
  struct data {
    void * member;
    ISwitchVectorProperty *svp;
  } *data = (struct data *)malloc(sizeof(struct data));
  data->member=this;
  data->svp=svp;
  uv_work_t* req = new uv_work_t;
  req->data = data;
  uv_queue_work(uv_default_loop(), req, nop, newSwitchCallback);
}
void BaseClientImpl::newNumber(INumberVectorProperty *nvp) {
  struct data {
    void * member;
    INumberVectorProperty *nvp;
  } *data = (struct data *)malloc(sizeof(struct data));
  data->member=this;
  data->nvp=nvp;
  uv_work_t* req = new uv_work_t;
  req->data = data;
  uv_queue_work(uv_default_loop(), req, nop, newNumberCallback);
}
void BaseClientImpl::newText(ITextVectorProperty *tvp) {
  struct data {
    void * member;
    ITextVectorProperty *tvp;
  } *data = (struct data *)malloc(sizeof(struct data));
  data->member=this;
  data->tvp=tvp;
  uv_work_t* req = new uv_work_t;
  req->data = data;
  uv_queue_work(uv_default_loop(), req, nop, newTextCallback);
}
void BaseClientImpl::newLight(ILightVectorProperty *lvp) {
  struct data {
    void * member;
    ILightVectorProperty *lvp;
  } *data = (struct data *)malloc(sizeof(struct data));
  data->member=this;
  data->lvp=lvp;
  uv_work_t* req = new uv_work_t;
  req->data = data;
  uv_queue_work(uv_default_loop(), req, nop, newLightCallback);
}
void BaseClientImpl::newMessage(INDI::BaseDevice *dp, int messageID) {
  struct data {
    void * member;
    INDI::BaseDevice *dp;
    int messageID;
  } *data = (struct data *)malloc(sizeof(struct data));
  data->member=this;
  data->dp=dp;
  data->messageID=messageID;
  uv_work_t* req = new uv_work_t;
  req->data = data;
  uv_queue_work(uv_default_loop(), req, nop, newMessageCallback);
}
void BaseClientImpl::serverConnected() {
  uv_work_t* req = new uv_work_t;
  req->data = this;
  uv_queue_work(uv_default_loop(), req, nop, serverConnectedCallback);
}
void BaseClientImpl::serverDisconnected(int exit_code) {
  struct data {
    void * member;
    int exit_code;
  } *data = (struct data *)malloc(sizeof(struct data));
  data->member=this;
  data->exit_code=exit_code;
  uv_work_t* req = new uv_work_t;
  req->data = data;
  uv_queue_work(uv_default_loop(), req, nop, serverDisconnectedCallback);
}


// Binds a javascript callback to INDI event
//
void BaseClientImpl::newDeviceEvent(v8::Handle<v8::Function> func) {

#if NODE_MODULE_VERSION >= 0x000D
        newDeviceCallback_.Reset(v8::Isolate::GetCurrent(), func);
#else
        newDeviceCallback_ = v8::Persistent<v8::Function>::New(func);
#endif
}

void BaseClientImpl::removeDeviceEvent(v8::Handle<v8::Function> func) {
#if NODE_MODULE_VERSION >= 0x000D
        removeDeviceCallback_.Reset(v8::Isolate::GetCurrent(), func);
#else
        removeDeviceCallback_ = v8::Persistent<v8::Function>::New(func);
#endif
}
void BaseClientImpl::newPropertyEvent(v8::Handle<v8::Function> func) {
#if NODE_MODULE_VERSION >= 0x000D
        newPropertyCallback_.Reset(v8::Isolate::GetCurrent(), func);
#else
        newPropertyCallback_ = v8::Persistent<v8::Function>::New(func);
#endif
}

void BaseClientImpl::removePropertyEvent(v8::Handle<v8::Function> func) {
#if NODE_MODULE_VERSION >= 0x000D
        removePropertyCallback_.Reset(v8::Isolate::GetCurrent(), func);
#else
        removePropertyCallback_ = v8::Persistent<v8::Function>::New(func);
#endif
}

void BaseClientImpl::newBLOBEvent(v8::Handle<v8::Function> func) {
#if NODE_MODULE_VERSION >= 0x000D
        newBLOBCallback_.Reset(v8::Isolate::GetCurrent(), func);
#else
        newBLOBCallback_ = v8::Persistent<v8::Function>::New(func);
#endif
}
void BaseClientImpl::newSwitchEvent(v8::Handle<v8::Function> func) {
#if NODE_MODULE_VERSION >= 0x000D
        newSwitchCallback_.Reset(v8::Isolate::GetCurrent(), func);
#else
        newSwitchCallback_ = v8::Persistent<v8::Function>::New(func);
#endif
}
void BaseClientImpl::newNumberEvent(v8::Handle<v8::Function> func) {
#if NODE_MODULE_VERSION >= 0x000D
        newNumberCallback_.Reset(v8::Isolate::GetCurrent(), func);
#else
        newNumberCallback_ = v8::Persistent<v8::Function>::New(func);
#endif
}
void BaseClientImpl::newTextEvent(v8::Handle<v8::Function> func) {
#if NODE_MODULE_VERSION >= 0x000D
        newTextCallback_.Reset(v8::Isolate::GetCurrent(), func);
#else
        newTextCallback_ = v8::Persistent<v8::Function>::New(func);
#endif
}

void BaseClientImpl::newLightEvent(v8::Handle<v8::Function> func) {
#if NODE_MODULE_VERSION >= 0x000D
        newLightCallback_.Reset(v8::Isolate::GetCurrent(), func);
#else
        newLightCallback_ = v8::Persistent<v8::Function>::New(func);
#endif
}
void BaseClientImpl::newMessageEvent(v8::Handle<v8::Function> func) {
#if NODE_MODULE_VERSION >= 0x000D
        newMessageCallback_.Reset(v8::Isolate::GetCurrent(), func);
#else
        newMessageCallback_ = v8::Persistent<v8::Function>::New(func);
#endif
}

void BaseClientImpl::serverConnectedEvent(v8::Handle<v8::Function> func) {
#if NODE_MODULE_VERSION >= 0x000D
        serverConnectedCallback_.Reset(v8::Isolate::GetCurrent(), func);
#else
        serverConnectedCallback_ = v8::Persistent<v8::Function>::New(func);
#endif
}

void BaseClientImpl::serverDisconnectedEvent(v8::Handle<v8::Function> func) {
#if NODE_MODULE_VERSION >= 0x000D
        serverDisconnectedCallback_.Reset(v8::Isolate::GetCurrent(), func);
#else
        serverDisconnectedCallback_ = v8::Persistent<v8::Function>::New(func);
#endif
}
