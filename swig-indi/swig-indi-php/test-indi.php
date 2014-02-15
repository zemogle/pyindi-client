include('indiclientphp.php');

class IndiClient extends BaseClient  {

    function newDevice(BaseDevice $basedevice) {
        global $newdev;
        //echo "newDevice: ".$basedevice->getDeviceName()."\n";
        echo "newDevice"."\n";
        $newdev = $basedevice;
        var_dump($basedevice);
        echo serialize($basedevice)."\n";
    }
    function newProperty($property){
        //echo "newProperty: ".$property->getName()."\n";
        echo "newProperty: "."\n";
        }
    function removeProperty($property) {}
    function newBLOB($iblob) {}
    function newSwitch($svp) {}
    function newNumber($nvp){}
    function newMessage($basedevice, $messageID) {}
    function newText($tvp) {}
    function newLight($lvp) {}
    function serverConnected() {}
    function serverDisconnected($exit_code) {}

};
$newdev=NULL;
$c=new IndiClient();
$c->setServer("localhost",7624);
$c->connectServer();



$d=$c->getDevice("CCD Simulator");
echo "Device: ".$d->getDeviceName()."\n";

$l=$c->getDevices();
//$d=$l[0];
echo $l->get(0)->getDeviceName();

$d=$l->get(0);
$lp=$d->getProperties();
for ($i=0; $i < $lp->size(); $i++) echo $lp->get($i)->getName()."\n";


$c->disconnectServer();