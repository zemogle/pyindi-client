%module indiclienttcl
%{
#include <indibase.h>
#include <indiapi.h>
#include <baseclient.h>
#include <basedevice.h>
#include <indiproperty.h>
#include "tclclient.h"
%}


%include "std_vector.i"

//%feature("notabstract") BaseClient;

%include <indibase.h>
%include <indiapi.h>
%include <baseclient.h>
%include <basedevice.h>
%include <indiproperty.h>

namespace std {
  %template(BaseDeviceVector) vector<INDI::BaseDevice *>;
  %template(PropertyVector) vector<INDI::Property *>;
}


%include "tclclient.h"

