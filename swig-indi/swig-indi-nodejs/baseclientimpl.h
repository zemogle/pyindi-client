#ifndef BASECLIENTIMPL_H
#define BASECLIENTIMPL_H

#include <indibase.h>
#include <indiapi.h>
#include <baseclient.h>
#include <basedevice.h>
#include <indiproperty.h>

#include <node.h>
#include <node_object_wrap.h>

#if NODE_MODULE_VERSION >= 0x000D
#include <uv.h>
#endif
#include <stdlib.h>

class BaseClientImpl : public INDI::BaseClient {
 public:
  BaseClientImpl();
  ~BaseClientImpl();  

  void newDeviceEvent(v8::Handle<v8::Function> func);
  void removeDeviceEvent(v8::Handle<v8::Function> func);
  void newPropertyEvent(v8::Handle<v8::Function> func);
  void removePropertyEvent(v8::Handle<v8::Function> func);
  void newBLOBEvent(v8::Handle<v8::Function> func);
  void newSwitchEvent(v8::Handle<v8::Function> func);
  void newNumberEvent(v8::Handle<v8::Function> func);
  void newTextEvent(v8::Handle<v8::Function> func);
  void newLightEvent(v8::Handle<v8::Function> func);
  void newMessageEvent(v8::Handle<v8::Function> func);
  void serverConnectedEvent(v8::Handle<v8::Function> func);
  void serverDisconnectedEvent(v8::Handle<v8::Function> func);

 private:
  v8::Persistent<v8::Value> newDeviceCallback_;
  v8::Persistent<v8::Value> removeDeviceCallback_;
  v8::Persistent<v8::Value> newPropertyCallback_;
  v8::Persistent<v8::Value> removePropertyCallback_;
  v8::Persistent<v8::Value> newBLOBCallback_;
  v8::Persistent<v8::Value> newSwitchCallback_;
  v8::Persistent<v8::Value> newNumberCallback_;
  v8::Persistent<v8::Value> newTextCallback_;
  v8::Persistent<v8::Value> newLightCallback_;
  v8::Persistent<v8::Value> newMessageCallback_;
  v8::Persistent<v8::Value> serverConnectedCallback_;
  v8::Persistent<v8::Value> serverDisconnectedCallback_;

  void newDevice(INDI::BaseDevice *dp);
  void removeDevice(INDI::BaseDevice *dp);
  void newProperty(INDI::Property *property);
  void removeProperty(INDI::Property *property);
  void newBLOB(IBLOB *bp);
  void newSwitch(ISwitchVectorProperty *svp);
  void newNumber(INumberVectorProperty *nvp);
  void newText(ITextVectorProperty *tvp);
  void newLight(ILightVectorProperty *lvp);
  void newMessage(INDI::BaseDevice *dp, int messageID);
  void serverConnected();
  void serverDisconnected(int exit_code);

  static void nop(uv_work_t* req);
  static void newDeviceCallback(uv_work_t* req, int status);
  static void removeDeviceCallback(uv_work_t* req, int status);
  static void newPropertyCallback(uv_work_t* req, int status);
  static void removePropertyCallback(uv_work_t* req, int status);
  static void newBLOBCallback(uv_work_t* req, int status);
  static void newSwitchCallback(uv_work_t* req, int status);
  static void newNumberCallback(uv_work_t* req, int status);
  static void newTextCallback(uv_work_t* req, int status);
  static void newLightCallback(uv_work_t* req, int status);
  static void newMessageCallback(uv_work_t* req, int status);
  static void serverConnectedCallback(uv_work_t* req, int status);
  static void serverDisconnectedCallback(uv_work_t* req, int status);

};

#endif
