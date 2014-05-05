'''
	
     TestON is free software: you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation, either version 2 of the License, or
     (at your option) any later version.

     TestON is distributed in the hope that it will be useful,
     but WITHOUT ANY WARRANTY; without even the implied warranty of
     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
     GNU General Public License for more details.


'''
#ex 
#import sys
#sys.path.append("../../drivers/common/api/")
#from  drivers.common.api import modifiedTestUtils
#from API import modifiedTestUtils
#sys.path.append(path+"/drivers/common/api/")
#import modifiedTestUtils as modifiedTestUtils
class FVTestProto :

    def __init__(self) :
        self.default = ''

    def CASE1(self,main) :

        main.case("Beginning FlowVisor Tests")
	
        main.step("Start fake devices")
        main.FakeDevice1.startController()
        main.FakeDevice1.startSwitch()
        main.step("Checking for a slice named sliceA")
        a = main.FlowVisor.listSlices()
        a = main.FlowVisor.listSlices("SliceA")
        utilities.assert_equals(expect=main.TRUE,actual=a,onpass="SliceA exists already" ,onfail="SliceA does not exist")

        main.step("Checking for a slice named sliceB")
        b = main.FlowVisor.listSlices("SliceB")
        utilities.assert_equals(expect=main.TRUE,actual=b,onpass="SliceB exists already" ,onfail="SliceB does not exist")
   
        if a:
            main.step("Removing sliceA")
            a = main.FlowVisor.removeSlice("SliceA")
            utilities.assert_equals(expect=main.TRUE,actual=a,onpass="SliceA Removed" ,onfail="Failed to remove sliceA")

        if b:
            main.step("Removing sliceB")
            b = main.FlowVisor.removeSlice("SliceB")
            utilities.assert_equals(expect=main.TRUE,actual=b,onpass="SliceB Removed" ,onfail="Failed to remove sliceB")

        main.step("Adding a slice named sliceA")
        a = main.FlowVisor.addSlice(slice_name="SliceA", controller_url="tcp:10.128.100.111:10100",  admin_email="jhall@onlab.us")
        utilities.assert_equals(expect=main.TRUE,actual=a,onpass="SliceA created" ,onfail="Failed to create sliceA")

        main.step("Adding a slice named sliceB")
        b = main.FlowVisor.addSlice()
        utilities.assert_equals(expect=main.TRUE,actual=b,onpass="SliceB created" ,onfail="Failed to create sliceB")

        main.step("Adding FlowSpace")
        addflowspace_result_1 = main.FlowVisor.addFlowSpace("flow1 0 100 in_port=0 SliceA=7")
        utilities.assert_equals(expect=main.TRUE,actual=addflowspace_result_1,onpass="Added FlowSpace Successfully",onfail="Failed to add FlowSpace")

        main.FakeDevice1.handshake()
 
        '''
        addflowspace_result_2 = main.FlowVisor.addFlowSpace("")
        utilities.assert_equals(expect=main.TRUE,actual=addflowspace_result_2,onpass="Added FlowSpace Successfully",onfail="Failed to add FlowSpace")
    
        addflowspace_result_3 = main.FlowVisor.addFlowSpace("any 100 dl_type=0x800,nw_proto=6,nw_src=10.128.4.6,tp_dst=22 Slice:SSH=4")
        utilities.assert_equals(expect=main.TRUE,actual=addflowspace_result_3,onpass="Added FlowSpace Successfully",onfail="Failed to add FlowSpace")
    
        addflowspace_result_4 = main.FlowVisor.addFlowSpace("any 100 dl_type=0x800,nw_proto=6,nw_src=10.128.4.5,tp_dst=22 Slice:SSH=4")
        utilities.assert_equals(expect=main.TRUE,actual=addflowspace_result_4,onpass="Added FlowSpace Successfully",onfail="Failed to add FlowSpace")
    
        addflowspace_result_5 = main.FlowVisor.addFlowSpace("any 100 dl_type=0x800,nw_proto=6,nw_src=10.128.4.6,tp_src=22 Slice:SSH=4")
        utilities.assert_equals(expect=main.TRUE,actual=addflowspace_result_5,onpass="Added FlowSpace Successfully",onfail="Failed to add FlowSpace")
    
        addflowspace_result_6 = main.FlowVisor.addFlowSpace("any 100 dl_type=0x800,nw_proto=6,nw_src=10.128.4.5,tp_src=22 Slice:SSH=4")
        utilities.assert_equals(expect=main.TRUE,actual=addflowspace_result_6,onpass="Added FlowSpace Successfully",onfail="Failed to add FlowSpace")
        '''
    
        '''
        main.step("Showing the flowSpaces")
        listflowspace_result = main.FlowVisor.listFlowSpace()
        utilities.assert_equals(expect=main.TRUE,actual=listflowspace_result,onpass="FlowSpace Listed successfully",onfail="Failed to listthe FlowSpace")
        '''


        SwitchNames = main.FakeDevice1.ctr1.getSwitches()
        print "Switch Names=", SwitchNames

        print "****************************************************"

        SRC_MAC_FOR_CTL0_0 = "00:00:00:00:00:02"
        print "Generating a Simple Packet"
        print "\n"
        pkt = main.TestUtils.simplePacket(dl_src = SRC_MAC_FOR_CTL0_0)
        in_port = 0 #CTL0 has this port
        msg = main.TestUtils.genPacketIn(in_port=in_port, pkt=pkt)
        print "Packet = ", pkt
        print "\n"
        print "Message = ", msg
        print "\n"


        snd_list = ["switch", 0, msg]
        exp_list = [["controller", 0, msg]]
        print "Comparing expected and actual messages"
        swList = main.FakeDevice1.getswList()
        contList = main.FakeDevice1.getcontList()
        print "swList: "
        print swList
        print "contList: "
        print contList
        res = main.TestUtils.ofmsgSndCmp(snd_list, exp_list, swList, contList, xid_ignore=True)
        print "Result = ", res
        if res == True:
            res = main.TRUE
        else:
            res = main.FALSE
        utilities.assert_equals(expect=main.TRUE,actual=res,onpass="Packet In by port testcase passed!",onfail="Packet In by Port testcase Failed!")
        #self.assertTrue(res, "%s: Received unexpected message" %(self.__class__.__name__))


    
