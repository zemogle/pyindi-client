%module indiclienttcl
%{
#include <indibase.h>
#include <baseclient.h>
%}

//%feature("notabstract") BaseClient;

%include <indibase.h>
%include <baseclient.h>
