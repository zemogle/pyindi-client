%module(directors="1") indiclientphp
%{
#include <indibase.h>
#include <indiapi.h>
#include <baseclient.h>
#include <basedevice.h>
#include <indiproperty.h>
  //#include "tclclient.h"
%}

//%include "phppointers.i"
%include "std_vector.i"

//%feature("notabstract") BaseClient;
%feature("director") BaseClient;


 //namespace std {
%template(BaseDeviceVector) std::vector<INDI::BaseDevice *>;
%template(PropertyVector) std::vector<INDI::Property *>;
 //}
/*
%typemap(out) const std::vector<INDI::BaseDevice *>&
{
    array_init( return_value );

    std::vector<INDI::BaseDevice *>::const_iterator itr;

    itr = $1->begin();

    for( itr; itr != $1->end(); itr++ )
    {
        zval* tmp;

	//INDI::BaseDevice * res = new STF::MyOtherClass( *itr );
	INDI::BaseDevice *res=(INDI::BaseDevice *)new INDI::BaseDevice(**itr);

        MAKE_STD_ZVAL( tmp );


        SWIG_SetPointerZval( tmp, (void *)res, SWIGTYPE_p_INDI__BaseDevice, 2 );

        add_next_index_zval( return_value, tmp );
    }
}
*/
%include <indibase.h>
%include <indiapi.h>
%include <baseclient.h>
%include <basedevice.h>
%include <indiproperty.h>


 //%include "tclclient.h"

