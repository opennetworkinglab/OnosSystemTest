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
class MininetSlicing :

    def __init__(self) :
        self.default = ''

    def CASE1(self,main) :

        main.case("Verifying 'SSH protocol' based slicing")
    
        main.step("Deleting flowspace using 'removeFlowSpace'")
        removeflowspace_result = main.FlowVisor1.removeFlowSpace("all")
        utilities.assert_equals(expect=main.TRUE,actual=removeflowspace_result,onpass="Removed FlowSpace Successfully",onfail="Failed to remove FlowSpace")
    
        main.step("Showing connected devices using 'listDevices'")
        listdevices_result = main.FlowVisor1.listDevices()
        utilities.assert_equals(expect=main.TRUE,actual=listdevices_result,onpass="Listed devices Successfully",onfail="Failed to list the devices")
    
        main.step("Verifying hosts reachability through ICMP traffic")
        ping_result = main.Mininet1.pingHost(src='h1',target='h4')
        utilities.assert_equals(expect=main.TRUE,actual=ping_result,onpass="NO PACKET LOSS, HOST IS REACHABLE",onfail="PACKET LOST, HOST IS NOT REACHABLE")
    
        main.step("Showing the flowSpace USING 'listFlowSpace'")
        listflowspace_result = main.FlowVisor1.listFlowSpace()
        ping_result = main.Mininet1.pingHost(src='h1',target='h4')
    
    
        main.step("Adding FlowSpace to create the slice of the Network")
        main.log.info(" Geeting the IP-Addresses of Hosts")
        h1_ipaddress = main.Mininet1.getIPAddress('h1')
        h4_ipaddress  = main.Mininet1.getIPAddress('h4')
    
        main.log.info(" Geeting the MAC-Addresses of Hosts"  )
        h1_macaddress = main.Mininet1.getMacAddress('h1')
        h4_macaddress = main.Mininet1.getMacAddress('h4')
    
        addflowspace_result_1 = main.FlowVisor1.addFlowSpace(dl_src=h1_macaddress,nw_dst=h4_ipaddress)
        utilities.assert_equals(expect=main.TRUE,actual=addflowspace_result_1,onpass="Added FlowSpace Successfully",onfail="Failed to add FlowSpace")
    
        addflowspace_result_2  = main.FlowVisor1.addFlowSpace(dl_src=h4_macaddress,nw_dst=h1_ipaddress)
        utilities.assert_equals(expect=main.TRUE,actual=addflowspace_result_2,onpass="Added FlowSpace Successfully",onfail="Failed to add FlowSpace")
    
        addflowspace_result_3 = main.FlowVisor1.addFlowSpace(nw_src=h1_ipaddress)
        addflowspace_result_3 = main.FlowVisor1.addFlowSpace(nw_src=h4_ipaddress)
    
        addflowspace_result_3 = main.FlowVisor1.addFlowSpace(nw_src=h1_ipaddress, tp_dst='22')
        utilities.assert_equals(expect=main.TRUE,actual=addflowspace_result_3,onpass="Added FlowSpace Successfully",onfail="Failed to add FlowSpace")
    
        addflowspace_result_4 = main.FlowVisor1.addFlowSpace(nw_src=h4_ipaddress,tp_dst='22')
        utilities.assert_equals(expect=main.TRUE,actual=addflowspace_result_4,onpass="Added FlowSpace Successfully",onfail="Failed to add FlowSpace")
    
        addflowspace_result_5 = main.FlowVisor1.addFlowSpace(nw_src=h1_ipaddress,tp_src='22')
        utilities.assert_equals(expect=main.TRUE,actual=addflowspace_result_5,onpass="Added FlowSpace Successfully",onfail="Failed to add FlowSpace")
    
        addflowspace_result_6 = main.FlowVisor1.addFlowSpace(nw_src=h4_ipaddress,tp_src='22')
        utilities.assert_equals(expect=main.TRUE,actual=addflowspace_result_6,onpass="Added FlowSpace Successfully",onfail="Failed to add FlowSpace")
    
        main.log.info("Showing the flowSpace USING 'listFlowSpace'")
        listflowspace_result     = main.FlowVisor1.listFlowSpace()
    
        main.step("Verifying hosts reachability through ICMP traffic and Connectivity through SSH service")
        ping_result = main.Mininet1.pingHost(src='h1',target='h4')
        utilities.assert_equals(expect=main.TRUE,actual=ping_result,onpass="NO PACKET LOSS, HOST IS REACHABLE",onfail="PACKET LOST, HOST IS NOT REACHABLE")
    
        ssh_result = main.Mininet1.verifySSH(user_name=main.params['CASE1']['destination_username'],ip_address=main.params['CASE1']['destination_host'], pwd=main.params['CASE1']['destination_password'], port=main.params['CASE1']['destination_port'])
        utilities.assert_equals(expect=main.TRUE,actual=ssh_result,onpass="Failed to connect remote host throgh SSH",onfail="Remote host connected throgh SSH ")
    
    
    
    
    
    
