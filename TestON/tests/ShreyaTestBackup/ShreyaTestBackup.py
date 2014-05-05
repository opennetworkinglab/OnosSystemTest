
class ShreyaTestBackup :

    def __init__(self) :
        self.default = ''

  
    def CASE1(self,main) :
        main.case("Testing Floodlight")
        main.step("Testing isup() function")
        result = main.Floodlight1.isup()
        main.step("Verifying result")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Floodlight connected",onfail="Floodlight not connected")

    def CASE2(self,main) :

        main.case("Testing the configuration of the host")
        main.step("Host IP Checking using checkIP")
        result = main.Mininet1.checkIP(main.params['CASE1']['destination'])
        main.step("Verifying the result")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Host h2 IP address configured",onfail="Host h2 IP address didn't configured")

    def CASE3(self,main) :
        main.case("Testing OVX")
        main.step("Testing isup() function of OVX")
        result = main.OVX1.isup()
        main.step("Verifying result")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="OVX connected",onfail="OVX not connected")

    def CASE4(self,main):
        main.case("Testing createNetwork")
        main.step("Testing createNetwork API of ovx")
        result = main.OVX1.NetworkCreate(Protocol=main.params['NW_CREATION']['protocol'], IP=main.params['NW_CREATION']['ctrllerIP'],\
Port=main.params['NW_CREATION']['ctrllerPort'],IPrange=main.params['NW_CREATION']['IPRange'], Mask=main.params['NW_CREATION']['mask'])
        main.step("Verifying the result")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Virtual Network created",onfail="Virtual Network not created ")

    def CASE5(self,main):
        main.case("Testing createSwitch")
        main.step("Testing creation of Virtual Switch 1")
        result = main.OVX1.SwitchCreate(Dpid=main.params['SW_CREATION']['sw1dpid'], NwID=main.params['SW_CREATION']['nwID'])
        main.step("Verifying result")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Virtual Switch1 Created",onfail="Virtual Switch1 not created")
        
        main.step("Testing creation of Virtual Switch 2")
        result = main.OVX1.SwitchCreate(Dpid=main.params['SW_CREATION']['sw2dpid'], NwID=main.params['SW_CREATION']['nwID'])
        main.step("Verifying result")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Virtual Switch2 Created",onfail="Virtual Switch2 not created")

        main.step("Testing creation of Virtual Switch 3")
        result = main.OVX1.SwitchCreate(Dpid=main.params['SW_CREATION']['sw3dpid'], NwID=main.params['SW_CREATION']['nwID'])
        main.step("Verifying result")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Virtual Switch3 Created",onfail="Virtual Switch3 not created")

    def CASE6(self,main):
        main.case("Testing createPort")
        main.step("Testing createPort for PhsicalSwitch 1 Port 1")
        result = main.OVX1.PortCreate(NwID=main.params['SW_CREATION']['nwID'], Dpid=main.params['SW_CREATION']['sw1dpid'], PortNo=main.params['PORT_CREATION']['p1sw1'])
        #result = main.OVX1.PortCreate(PortNum="1", NwID=main.params['SW_CREATION']['nwID'], Dpid=main.params['SW_CREATION']['sw1dpid'])
        main.step("Verifying the result")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Virtual Port created",onfail="Virtual port not created")

        main.step("Testing createPort for PhsicalSwitch 1 Port 2")
        result = main.OVX1.PortCreate(NwID=main.params['SW_CREATION']['nwID'], Dpid=main.params['SW_CREATION']['sw1dpid'], PortNo=main.params['PORT_CREATION']['p2sw1'])
        main.step("Verifying the result")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Virtual Port created",onfail="Virtual Port not created")

        main.step("Testing createPort for PhsicalSwitch 2 Port 2")
        result = main.OVX1.PortCreate(NwID=main.params['SW_CREATION']['nwID'], Dpid=main.params['SW_CREATION']['sw2dpid'], PortNo=main.params['PORT_CREATION']['p1sw2'])
        main.step("Verifying the result")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Virtual Port created",onfail="Virtual Port not created")

        main.step("Testing createPort for PhsicalSwitch 2 Port 3")
        result = main.OVX1.PortCreate(NwID=main.params['SW_CREATION']['nwID'], Dpid=main.params['SW_CREATION']['sw2dpid'], PortNo=main.params['PORT_CREATION']['p2sw2'])
        main.step("Verifying the result")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Virtual Port created",onfail="Virtual Port not created")

        main.step("Testing createPort for PhsicalSwitch 3 Port 2")
        result = main.OVX1.PortCreate(NwID=main.params['SW_CREATION']['nwID'], Dpid=main.params['SW_CREATION']['sw3dpid'], PortNo=main.params['PORT_CREATION']['p1sw3'])
        main.step("Verifying the result")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Virtual Port created",onfail="Virtual Port not created")

        main.step("Testing createPort for PhsicalSwitch 3 Port 1")
        result = main.OVX1.PortCreate(NwID=main.params['SW_CREATION']['nwID'], Dpid=main.params['SW_CREATION']['sw3dpid'], PortNo=main.params['PORT_CREATION']['p2sw3'])
        main.step("Verifying the result")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Virtual Port created",onfail="Virtual Port not created")

    def CASE7(self,main):
        main.case("Testing connectLink")
        main.step("Testing creation of Virtual Link 1")
        result = main.OVX1.LinkConnect(NwID=main.params['LINK_CONNECTION']['nwID'], Dpid= main.params['LINK_CONNECTION']['Vdpid1'], PortNo="2"\
,Dpiddt=main.params['LINK_CONNECTION']['Vdpid2'], PortN=main.params['LINK_CONNECTION']['Vsw2port1'], routingType=main.params['LINK_CONNECTION']['routingType'], \
backupPaths=main.params['LINK_CONNECTION']['num_of_backupPaths'])
        main.step("Verifying result")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Virtual Link1 Created",onfail="Virtual Link1 not created")

        #main.step("Testing creation of Virtual Link 2")
        #result = main.OVX1.SwitchCreate(Dpid=main.params['SW_CREATION']['sw2dpid'], NwID=main.params['SW_CREATION']['nwID'])
        #main.step("Verifying result")
        #utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Virtual Switch2 Created",onfail="Virtual Switch2 not created")



