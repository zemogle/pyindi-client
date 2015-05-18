var indi=require('indiclientnodejs');

var ic=new indi.BaseClientImpl();
// define callbacks (default callbacks do not nothing)
ic.serverConnectedEvent(function() { console.log('server connected');});
ic.newDeviceEvent(function(idev) { console.log('new device :'+idev.getDeviceName());});
ic.removeDeviceEvent(function(idev) { console.log('remove device :'+idev.getDeviceName());});
ic.newPropertyEvent(function(iprop) { console.log('new property :'+iprop.getName()+' for device '+iprop.getDeviceName());});
ic.removePropertyEvent(function(iprop) { console.log('remove property :'+iprop.getName()+' for device '+iprop.getDeviceName());});
ic.newBLOBEvent(function(bp) { console.log('new BLOB '+bp.name);});
ic.newSwitchEvent(function(svp) { console.log('new Switch '+svp.name+' for device '+svp.device);});

ic.setServer('localhost', 7624);
ic.connectServer();

/* small tests
var dl= ic.getDevices();
var d=dl.get(0);
var lp=d.getProperties();
var p=lp.get(0);
p.getType()==indi.INDI_SWITCH
var tpy=p.getSwitch();
tpy.getISwitch(1);
*/

console.log('List of Devices:');
var dl= ic.getDevices();
for(var i=0; i < dl.size(); i++) {
    console.log('  '+dl.get(i).getDeviceName());
}

console.log('List of Device Properties')
for(var i=0; i < dl.size(); i++) {
    var d=dl.get(i);
    console.log('-- '+d.getDeviceName());
    var lp=d.getProperties();
    for(var j=0; j < lp.size(); j++) {
	var p=lp.get(j);
	console.log('   > '+p.getName());
        if (p.getType()==indi.INDI_TEXT) {
            var tpy=p.getText();
	    for(var k=0; k < tpy.ntp; k++) {
		var t=tpy.getIText(k);
                console.log('       IText '+t.name+'('+t.label+')= '+t.text);
	    }
	}
        if (p.getType()==indi.INDI_SWITCH) {
            var tpy=p.getSwitch();
	    for(var k=0; k < tpy.nsp; k++) {
		var t=tpy.getISwitch(k);
                console.log('       ISwitch '+t.name+'('+t.label+')= '+t.s);
	    }
	}
        if (p.getType()==indi.INDI_NUMBER) {
            var tpy=p.getNumber();
	    for(var k=0; k < tpy.nnp; k++) {
		var t=tpy.getINumber(k);
                console.log('       INumber '+t.name+'('+t.label+')= '+t.value);
	    }
	}
        if (p.getType()==indi.INDI_LIGHT) {
            var tpy=p.getLight();
	    for(var k=0; k < tpy.nlp; k++) {
		var t=tpy.getILight(k);
                console.log('       ILight '+t.name+'('+t.label+')= '+t.s);
	    }
	}
        if (p.getType()==indi.INDI_BLOB) {
            var tpy=p.getBLOB();
	    for(var k=0; k < tpy.nbp; k++) {
		var t=tpy.getIBlob(k);
                console.log('       IBlob '+t.name+'('+t.label+')= '+t.size+' octets');
	    }
	}
    }

}

ic.disconnectServer();
