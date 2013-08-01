'''
	
 *   TestON is free software: you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *   the Free Software Foundation, either version 2 of the License, or
 *   (at your option) any later version.

 *   TestON is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details.


'''
class FVProtoSlicing :

    def __init__(self) :
        self.default = ''

    def CASE1(self,main) :

        main.case("Verifying SSH protocol based slicing")
    
        main.step("Deleting the flowspace by using 'removeFlowSpace'")
        removeflowspace_result = main.FlowVisor.removeFlowSpace("all")
        utilities.assert_equals(expect=main.TRUE,actual=removeflowspace_result,onpass="Removed FlowSpace Successfully",onfail="Failed to remove FlowSpace")
    
        main.step("Showing the connected devices by USING 'listDevices'")
        listdevices_result = main.FlowVisor.listDevices()
        utilities.assert_equals(expect=main.TRUE,actual=listdevices_result,onpass="Listed devices Successfully",onfail="Failed to list the devices")
    
        main.step("Adding FlowSpace")
        addflowspace_result_1 = main.FlowVisor.addFlowSpace("any 100 dl_type=0x806,dl_src=9e:f5:8b:78:c3:93,nw_dst=10.128.4.6 Slice:SSH=4")
        utilities.assert_equals(expect=main.TRUE,actual=addflowspace_result_1,onpass="Added FlowSpace Successfully",onfail="Failed to add FlowSpace")
    
        addflowspace_result_2 = main.FlowVisor.addFlowSpace("any 100 dl_type=0x806,dl_src=d2:df:f1:53:d4:49,nw_dst=10.128.4.5 Slice:SSH=4")
        utilities.assert_equals(expect=main.TRUE,actual=addflowspace_result_2,onpass="Added FlowSpace Successfully",onfail="Failed to add FlowSpace")
    
        addflowspace_result_3 = main.FlowVisor.addFlowSpace("any 100 dl_type=0x800,nw_proto=6,nw_src=10.128.4.6,tp_dst=22 Slice:SSH=4")
        utilities.assert_equals(expect=main.TRUE,actual=addflowspace_result_3,onpass="Added FlowSpace Successfully",onfail="Failed to add FlowSpace")
    
        addflowspace_result_4 = main.FlowVisor.addFlowSpace("any 100 dl_type=0x800,nw_proto=6,nw_src=10.128.4.5,tp_dst=22 Slice:SSH=4")
        utilities.assert_equals(expect=main.TRUE,actual=addflowspace_result_4,onpass="Added FlowSpace Successfully",onfail="Failed to add FlowSpace")
    
        addflowspace_result_5 = main.FlowVisor.addFlowSpace("any 100 dl_type=0x800,nw_proto=6,nw_src=10.128.4.6,tp_src=22 Slice:SSH=4")
        utilities.assert_equals(expect=main.TRUE,actual=addflowspace_result_5,onpass="Added FlowSpace Successfully",onfail="Failed to add FlowSpace")
    
        addflowspace_result_6 = main.FlowVisor.addFlowSpace("any 100 dl_type=0x800,nw_proto=6,nw_src=10.128.4.5,tp_src=22 Slice:SSH=4")
        utilities.assert_equals(expect=main.TRUE,actual=addflowspace_result_6,onpass="Added FlowSpace Successfully",onfail="Failed to add FlowSpace")
    
        main.step("Showing the flowSpace USING 'listFlowSpace'")
        listflowspace_result = main.FlowVisor.listFlowSpace()
        utilities.assert_equals(expect=main.TRUE,actual=listflowspace_result,onpass="FlowSpace Listed successfully",onfail="Failed to listthe FlowSpace")
    
        main.step("Verifying the Slice, by checking SSH is happening to the destination or not")
        ssh_result = main.Pax_DPVM1.SSH(user_name=main.params['CASE1']['destination_username'],ip_address=main.params['CASE1']['destination_host'], pwd=main.params['CASE1']['destination_password'], port=main.params['CASE1']['destination_port'], options=main.componentDictionary['Pax_DPVM1']['COMPONENTS'])
        utilities.assert_equals(expect=main.TRUE,actual=ssh_result,onpass="Remote host connected throgh SSH ",onfail="Failed to connect remote host throgh SSH")
    
        main.step(" Showcasing the Parsing the response in required format")
        myOutput  = "<ipaddress>10.128.4.2</ipaddress><username>paxterra</username><password>paxterra</password><port>22</port><location>Bangalore</location>"
        myVar= main.response_parser(myOutput,"table")
        main.log.info(myVar)
    
