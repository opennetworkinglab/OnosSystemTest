
class OnosFlowPerf:

    def __init__(self) :
        self.default = ''
    def CASE1(self,main) :  #Check to be sure ZK, Cass, and ONOS are up, then get ONOS version
        import time
        main.ONOS1.start()
        time.sleep(20)
        main.ONOS1.start_rest()
        test= main.ONOS1.rest_status()
        if test == main.FALSE:
            main.ONOS1.start_rest()
        main.ONOS1.get_version()
        main.log.report("Started Zookeeper, RamCloud, and ONOS")
        main.case("Checking if the startup was clean...")
        main.step("Testing Zookeeper Status")
        data =  main.ONOS1.zk_status()
        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="Zookeeper is up!",onfail="Zookeeper is down...")
        main.step("Testing Ramcloud Coord Status")
        data =  main.ONOS1.rcc_status()
        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="Ramcloud Coord is up!",onfail="Ramcloud Coord is down...")
        main.step("Testing Ramcloud Server Status")
        data =  main.ONOS1.rcs_status()
        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="Ramcloud Server is up!",onfail="Ramcloud Server is down...")
        main.step("Testing ONOS Status")
        data =  main.ONOS1.status()
        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="ONOS is up!",onfail="ONOS is down...")
        main.step("Testing Rest Status")
        data =  main.ONOS1.rest_status()
        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="REST is up!",onfail="REST is down...")

        
#Assign Controllers
#This test first checks the ip of a mininet host, to be certain that the mininet exists(Host is defined in Params as <CASE1><destination>).
#Then the program assignes each ONOS instance a single controller to a switch(To be the initial master), then assigns all controllers.
#NOTE: The reason why all four controllers are assigned although one was already assigned as the master is due to the 'ovs-vsctl set-controller' command erases all present controllers if
#      the controllers already assigned to the switch are not specified.
    def CASE2(self,main) :    #Make sure mininet exists, then assign controllers to switches
        import time
        main.log.report("Check if mininet started properly, then assign controllers ONOS 1,2,3 and 4")
        main.case("Checking if one MN host exists")
        main.step("Host IP Checking using checkIP")
        result = main.Mininet1.checkIP(main.params['CASE1']['destination'])
        main.step("Verifying the result")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Host IP address configured",onfail="Host IP address not configured")
        main.step("assigning ONOS controller to switches")
        for i in range(25):
            if i < 15:
                j=i+1
                main.Mininet1.assign_sw_controller(sw=str(j),ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'])
            else:
                j=i+16
                main.Mininet1.assign_sw_controller(sw=str(j),ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'])
        main.Mininet1.get_sw_controller("s1")
 
# **********************************************************************************************************************************************************************************************
#Proactive Flow Perf. Tests

    def CASE3(self,main) :
        main.log.report("Proactive Flow Performance Tests")
        import datetime
        testIter=5
        #refer to params file if the code does not work properly
        flowParam = main.params["NUMFLOWS"] 
        flow = flowParam.split(",")
        flow = [ int(x) for x in flow]
        numFlows = flow
        flowlen = 0
        addStartTime=[]
        remStartTime=[]
        main.case("Running Flow Perf Test") 
        for i in numFlows:
            main.step("Generating Add Flows")
            result=main.ONOS1.generateFlows(main.params["FLOWDEF"],"add",i,main.params['RestIP'])  
            utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Add FLOWS Gen PASS",onfail="Add FLOWS Gen FAIL")
            
            main.step("Generating Remove Flows")
            result3=main.ONOS1.generateFlows(main.params["FLOWDEF"],"remove",i,main.params['RestIP'])
            utilities.assert_equals(expect=main.TRUE,actual=result3,onpass="Remove FLOWS PASS",onfail="Remove FLOWS Gen FAIL")
            flowlen = flowlen + 1
            
        sendresult = main.ONOS1.getFile(flowlen,main.params['OnosIP'],main.params["TestONIP"],main.params["FLOWDEF"],main.params["OnosDir"],numFlows)
        utilities.assert_equals(expect=main.TRUE,actual=sendresult,onpass="add/rem file successfully sent",onfail="add/rem files NOT sent")
        
        for i in numFlows:
            main.step("Start TSHARK")
            tresult=main.ONOS1.start_tshark("add",i)
            utilities.assert_equals(expect=main.TRUE,actual=tresult,onpass="Start TSHARK PASS",onfail="Start TSHARK FAIL")

            main.step("Adding Flows")
            addStartTime.append(time.time())
            result1=main.ONOS1.addPerfFlows(main.params["OnosDir"],i)
            utilities.assert_equals(expect=main.TRUE,actual=result1,onpass='Add FLOWS PASS',onfail="Add FLOWS FAIL")
            main.step("Checking switch Flows")
            result2=main.Mininet1.getSwitchFlowCount("s1")
            main.log.info("Flow Count on Switch s1: "+ str(result2))
            main.step("Stop TSHARK")
            tresult=main.ONOS1.stop_tshark()
            utilities.assert_equals(expect=main.TRUE,actual=tresult,onpass="Stop TSHARK PASS",onfail="Stop TSHARK FAIL")

            main.step("Start TSHARK")
            tresult=main.ONOS1.start_tshark("remove",i)
            utilities.assert_equals(expect=main.TRUE,actual=tresult,onpass="Start TSHARK PASS",onfail="Start TSHARK FAIL")
            main.step("Removing Flows")
            remStartTime.append(time.time())
            result4=main.ONOS1.removePerfFlows(main.params["OnosDir"],i)
            utilities.assert_equals(expect=main.TRUE,actual=result4,onpass='Remove FLOWS PASS',onfail="Remove FLOWS FAIL")

            main.step("Checking switch Flows")
            result5=main.Mininet1.getSwitchFlowCount("s1")
            main.log.info("Flow Count on Switch s1: "+ result5)
            main.step("Stop TSHARK")
            tresult=main.ONOS1.stop_tshark()
            utilities.assert_equals(expect=main.TRUE,actual=tresult,onpass="Stop TSHARK PASS",onfail="Stop TSHARK FAIL")

        print"**********************************************************************"
        print"               ADD FLOWS PERFORMANCE RESULTS (PROACTIVE)              "
        print"**********************************************************************"        
        main.ONOS1.printPerfResults("add",numFlows,addStartTime,main.params['OnosIP'])
        print"**********************************************************************"
        print"               REMOVE FLOWS PERFORMANCE RESULTS (PROACTIVE)              "
        print"**********************************************************************"
        main.ONOS1.printPerfResults("remove",numFlows,remStartTime,main.params['OnosIP'])
