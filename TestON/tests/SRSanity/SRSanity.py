import pexpect
import time

class SRSanity:

    def __init__(self) :
        self.default = ''

#*****************************************************************************************************************************************************************************************
#Test startup
    def CASE1(self,main) : 
        import pexpect
        import time
        main.ONOSbench.handle.sendline("cd ~/onos")
        #main.step( "Git checkout and pull master" )
        main.ONOSbench.gitCheckout( "review/unknown/route_update" )
        #main.ONOSbench.gitCheckout( "master" )
        #gitPullResult = main.ONOSbench.gitPull()

        main.ONOSbench.handle.sendline("cp ~/onos/org.onosproject.provider.lldp.impl.LLDPLinkProvider.cfg.sr ~/onos/tools/package/etc/org.onosproject.provider.lldp.impl.LLDPLinkProvider.cfg")
        main.ONOSbench.handle.sendline("rm ~/onos/tools/package/etc/org.onosproject.openflow.controller.impl.OpenFlowControllerImpl.cfg")

        #main.step( "Using mvn clean & install & No Test" )
        #cleanInstallResult = main.TRUE
        #if gitPullResult == main.TRUE or gitPullResult == 3:
        #    cleanInstallResult = main.ONOSbench.cleanInstallSkipTest()
        #else:
        #    main.log.warn( "Did not pull new code so skipping mvn " +
        #                   "clean install" )
        main.ONOSbench.getVersion( report=True )	
 
        cellName = main.params[ 'ENV' ][ 'cellName' ]
        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]
        main.step( "Set cell for ONOS-cli environment" )
        main.ONOSbench.handle.sendline("cell spring")
        main.ONOScli.setCell( "spring" )
        verifyResult = main.ONOSbench.verifyCell()

        time.sleep( 10 )

#**********************************************************************************************************************************************************************************************
# A simple test for default connectivity in a fish topology

    def CASE2(self,main) :
        import time
 
        main.step("Copy the config file")
        main.ONOSbench.handle.sendline("cp ~/TestON/tests/SRSanity/fish.conf ~/onos/tools/package/config/segmentrouting.conf")
        cleanInstallResult = main.ONOSbench.cleanInstallSkipTest()
        main.ONOSbench.onosPackage()        

        main.log.report( "Removing raft logs" )
        main.ONOSbench.onosRemoveRaftLogs()
        main.log.report( "Uninstalling ONOS" )
        main.ONOSbench.onosUninstall( ONOS1Ip )

        main.step( "Installing ONOS package" )
        onos1InstallResult = main.ONOSbench.onosInstall(
            options="-f", node=ONOS1Ip )

        onos1Isup = main.ONOSbench.isup( ONOS1Ip )
        if not onos1Isup:
            main.log.report( "ONOS1 didn't start!" )

        main.step( "Start ONOS-cli" )

        main.ONOScli.startOnosCli( ONOS1Ip )

        time.sleep(10)

        main.log.info( "Installing segmentrouting feature" )
        main.ONOScli.handle.sendline( "app activate org.onosproject.segmentrouting" )
        time.sleep( 10 )

        main.log.report("Running mininet")
        main.Mininet.connect()
        main.Mininet.handle.sendline("sudo python /home/admin/TestON/tests/SRSanity/mininet/testEcmp_6sw.py")
        main.step("waiting 20 secs for switches to connect and go thru handshake")
        time.sleep(20)
        main.step("verifying all to all connectivity")
        
        p1 = main.Mininet.pingHost(SRC="h2",TARGET="h1")
        p2 = main.Mininet.pingHost(SRC="h1",TARGET="192.168.0.5")
        pa = main.Mininet.pingall()
        result = p1 and p2 and pa
        utilities.assert_equals(expect=main.TRUE,actual=result,
                                onpass="Default connectivity check PASS",
                                onfail="Default connectivity check FAIL")
        #cleanup mininet
        main.ONOScli.logout()
        main.ONOSbench.onosStop(ONOS1Ip);
        main.Mininet.stopNet()
        main.Mininet.disconnect()
       

#**********************************************************************************************************************************************************************************************
# A simple test for verify controller's recovery functionality in a fish topology

    def CASE3(self,main) :
        import time
 
        main.step("Copy the config file")       
        main.ONOSbench.handle.sendline("cp ~/TestON/tests/SRSanity/fish.conf ~/onos/tools/package/config/segmentrouting.conf")
        cleanInstallResult = main.ONOSbench.cleanInstallSkipTest()
        main.ONOSbench.onosPackage()

        main.log.report( "Removing raft logs" )
        main.ONOSbench.onosRemoveRaftLogs()
        main.log.report( "Uninstalling ONOS" )
        main.ONOSbench.onosUninstall( ONOS1Ip )

        main.step( "Installing ONOS package" )
        onos1InstallResult = main.ONOSbench.onosInstall(
            options="-f", node=ONOS1Ip )

        onos1Isup = main.ONOSbench.isup( ONOS1Ip )
        if not onos1Isup:
            main.log.report( "ONOS1 didn't start!" )

        main.step( "Start ONOS-cli" )

        main.ONOScli.startOnosCli( ONOS1Ip )
        time.sleep(20)

        main.log.info( "Installing segmentrouting feature" )
        main.ONOScli.handle.sendline( "app activate org.onosproject.segmentrouting" )        
        time.sleep( 10 )

        main.log.report("Running mininet")
        main.Mininet.connect()
        main.Mininet.handle.sendline("sudo python /home/admin/TestON/tests/SRSanity/mininet/testEcmp_6sw.py")
        main.step("waiting 30 secs for switches to connect and go thru handshake")
        time.sleep(30)
        main.step("verifying all to all connectivity")
        
        p1 = main.Mininet.pingHost(SRC="h2",TARGET="h1")
        p2 = main.Mininet.pingHost(SRC="h1",TARGET="192.168.0.5")
        pa = main.Mininet.pingall()
        result_normal = p1 and p2 and pa
        utilities.assert_equals(expect=main.TRUE,actual=result_normal, 
                                  onpass="Default connectivity check PASS", 
                                  onfail="Default connectivity check FAIL")    
        #Yank the cable on switch1-intf3, switch2-intf3 and switch4-intf3
        #to force the traffic to go via s1->s2->s3->s4->s5->s6
        main.Mininet.link(END1="s1",END2="s2",OPTION="down")
        time.sleep(2)
        main.Mininet.link(END1="s3",END2="s4",OPTION="down")
        time.sleep(2)
        main.Mininet.link(END1="s5",END2="s6",OPTION="down")
        main.step("waiting 10 secs for controller to perform recovery operations")
        time.sleep(10)
        main.step("verifying connectivity between hosts after link down")
        p1 = main.Mininet.pingHost(SRC="h1",TARGET="h2")
        result_during_failure = p1
        utilities.assert_equals(expect=main.TRUE,actual=result_during_failure,
                                onpass="Connectivity check after network element failure PASS",
                                onfail="Connectivity check after network element failure FAIL")

        
        #Plug back the cable on switch1-intf3, switch2-intf3 and switch4-intf3
        #so that traffic moves back to normal ECMP paths
        #main.Mininet.plugcpqd(SW="s1",INTF="s1-eth3")
        #main.Mininet.plugcpqd(SW="s2",INTF="s2-eth3")
        #main.Mininet.plugcpqd(SW="s4",INTF="s4-eth3")
        main.Mininet.link(END1="s1",END2="s2",OPTION="up")
        main.Mininet.link(END1="s3",END2="s4",OPTION="up")
        main.Mininet.link(END1="s5",END2="s6",OPTION="up")
        main.step("waiting 10 secs for controller to perform recovery operations")
        time.sleep(10)
        main.step("verifying connectivity between hosts after link down")
        p1 = main.Mininet.pingHost(SRC="h1",TARGET="h2")
        result_during_recovery = p1
        utilities.assert_equals(expect=main.TRUE,actual=result_during_recovery,
                                onpass="Connectivity check after network element recovery PASS",
                                onfail="Connectivity check after network element recovery FAIL")

        result = result_normal and result_during_failure and result_during_recovery 
        utilities.assert_equals(expect=main.TRUE,actual=result,
                                onpass="Controller recovery procedure check PASS",
                                onfail="Controller recovery procedure check FAIL")
        #cleanup mininet
        main.ONOScli.logout()
        main.ONOSbench.onosStop(ONOS1Ip);
        main.Mininet.stopNet()
        main.Mininet.disconnect()

#**********************************************************************************************************************************************************************************************
# A simple test for verifying tunnels and policies

    def CASE4(self,main) :
        import time
        main.ONOS.stop()
        # starts the controller with 3-node topology
        main.step("Restarting ONOS and Zookeeper")
        ret = main.ONOS.start()
        if ret == main.FALSE:
            main.log.report("ONOS did not start ... Aborting")
            main.cleanup()
            main.exit()
        main.log.report("Running mininet")
        main.Mininet.connect()
        main.Mininet.handle.sendline("sudo python /home/onos/mininet/custom/testEcmp_6sw.py")
        main.step("waiting 40 secs for switches to connect and go thru handshake")
        time.sleep(40)
        main.step("verifying all to all connectivity")
        
        p1 = main.Mininet.pingHost(SRC="h2",TARGET="h1")
        p2 = main.Mininet.pingHost(SRC="h1",TARGET="192.168.0.5")
        pa = main.Mininet.pingall()
        result_step1 = p1 and p2 and pa
        utilities.assert_equals(expect=main.TRUE,actual=result_step1, 
                                  onpass="Default connectivity check PASS", 
                                  onfail="Default connectivity check FAIL")    

        main.step("Verifying create tunnel functionality")
        ret = main.ONOS.create_tunnel(onosRESTIP="127.0.0.1",
                                      onosRESTPort=str(8080),
                                      tunnelURL="wm/onos/segmentrouting/tunnel",
                                      params="{\"tunnel_id\":\"t1\",\"label_path\":[101,102,103,104,105,106]}")
        result_step2 = ret
        utilities.assert_equals(expect=main.TRUE,actual=result_step2, 
                                  onpass="Tunnel create check PASS", 
                                  onfail="Tunnel create check FAIL")    
        
        main.step("Verifying groups created as part tunnel t1 : 3groups@s1 and 1group@s5")
        switch_groups = main.ONOS.get_all_groups_of_tunnel(onosRESTIP="127.0.0.1",
                                      onosRESTPort=str(8080),
                                      tunnelURL="wm/onos/segmentrouting/tunnel",
                                      tunnel_id="t1")
        print "Groups created for tunnel t1",switch_groups
        ret_sw1 = main.FALSE
        ret_sw5 = main.FALSE
        ret_sw1_3groups = main.FALSE
        ret_sw5_1groups = main.FALSE
        ret_stats = main.FALSE
        for entry in switch_groups:
            if entry.has_key("SW"):
                #print "entry[SW]: ",entry['SW']
                if (entry['SW'] == "00:00:00:00:00:00:00:01"):
                    ret_sw1 = main.TRUE
                    if (len(entry['GROUPS']) == 2):
                        ret_sw1_3groups = main.TRUE
                if (entry['SW'] == "00:00:00:00:00:00:00:04"):
                    ret_sw5 = main.TRUE
                    if (len(entry['GROUPS']) == 1):
                        ret_sw5_1groups = main.TRUE
                before_stats = main.ONOS.get_switch_group_stats(onosRESTIP="127.0.0.1",
                                      onosRESTPort=str(8080),
                                      dpid=entry['SW'])
                #print "before_stats: ",before_stats
                if (before_stats != main.FALSE):
                    ret_stats = main.TRUE
                    entry['STATS'] = before_stats 
        #print "results for group check: ", ret_sw1, ret_sw1_3groups, ret_sw5, ret_sw5_1groups, ret_stats    
        result_step3 = ret_sw1 and ret_sw1_3groups and ret_sw5 and ret_sw5_1groups and ret_stats
        utilities.assert_equals(expect=main.TRUE,actual=result_step3,
                                onpass="Tunnel groups check PASS",
                                onfail="Tunnel groups check FAIL")
        
        main.step("Verifying create policy functionality")
        #ret = main.ONOS.create_policy("http://127.0.0.1:8080/wm/onos/segmentrouting/policy","{\"priority\": 2223, \"dst_tp_port_op\": \"eq\", \"src_tp_port_op\": \"eq\", \"src_tp_port\": \"1000\", \"tunnel_id\": \"t1\", \"src_ip\": \"10.0.1.1/32\", \"policy_type\": \"tunnel-flow\", \"dst_ip\": \"7.7.7.7/32\", \"dst_tp_port\": \"2000\", \"proto_type\": \"ip\", \"policy_id\": \"pol1\"}")
        ret = main.ONOS.create_policy(onosRESTIP="127.0.0.1",
                                      onosRESTPort=str(8080),
                                      policyURL="/wm/onos/segmentrouting/policy",
                                      params="{\"priority\": 2223, \"tunnel_id\": \"t1\", \"src_ip\": \"10.0.1.1/32\", \"policy_type\": \"tunnel-flow\", \"dst_ip\": \"7.7.7.7/32\", \"proto_type\": \"ip\", \"policy_id\": \"pol1\"}")
        result_step4 = ret
        utilities.assert_equals(expect=main.TRUE,actual=result_step4,
                                onpass="Policy creation check PASS",
                                onfail="Policy creation check FAIL")

        main.step("waiting 5 secs to push the tunnels and policies to the switches")
        time.sleep(5)
        main.step("verifying connectivity between hosts after tunnel policy creation")
        p1 = main.Mininet.pingHost(SRC="h1",TARGET="h2")
        ret_group_stats = main.FALSE
        for entry in switch_groups:
            if entry.has_key("SW"):
                #print "entry[SW]: ",entry['SW']
                after_stats = main.ONOS.get_switch_group_stats(onosRESTIP="127.0.0.1",
                                      onosRESTPort=str(8080),
                                      dpid=entry['SW'])
                #print "after_stats: ",after_stats
                if after_stats != main.FALSE:
                    before_pkt_count = 0
                    after_pkt_count = 0
                    for group in entry['GROUPS']:
                        for beforeStat in before_stats:
                            if beforeStat['groupId'] == group:
                                before_pkt_count = beforeStat['packetCount']
                                break
                        for afterStat in after_stats:
                            if afterStat['groupId'] == group:
                                after_pkt_count = afterStat['packetCount']
                                break
                    if (((after_pkt_count-before_pkt_count) > 0) and
                        ((after_pkt_count-before_pkt_count) < 3)):
                        ret_group_stats = main.TRUE
                    else:
                        ret_group_stats = main.FALSE
                        break;
                            
        result_step5 = p1 and ret_group_stats
        utilities.assert_equals(expect=main.TRUE,actual=result_step5,
                                onpass="Connectivity check on tunnel policy PASS",
                                onfail="Connectivity check on tunnel policy FAIL")

        result_phase1 = result_step1 and result_step2 and result_step3 and result_step4 and result_step5 

        main.step("Verifying delete policy functionality")
        ret = main.ONOS.delete_policy(onosRESTIP="127.0.0.1",
                                      onosRESTPort=str(8080),
                                      policyURL="/wm/onos/segmentrouting/policy",
                                      params="{\"policy_id\": \"pol1\"}")
        result_step6 = ret
        utilities.assert_equals(expect=main.TRUE,actual=result_step5,
                                onpass="Policy deletion check PASS",
                                onfail="Policy deletion check FAIL")

        main.step("Verifying delete tunnel functionality")
        ret = main.ONOS.delete_tunnel(onosRESTIP="127.0.0.1",
                                      onosRESTPort=str(8080),
                                      tunnelURL="wm/onos/segmentrouting/tunnel",
                                      params="{\"tunnel_id\":\"t1\"}")
        result_step7 = ret
        utilities.assert_equals(expect=main.TRUE,actual=result_step7,
                                onpass="Tunnel deletion check PASS",
                                onfail="Tunnel deletion check FAIL")
        
        main.step("waiting 5 secs for tunnel and policy remove to happen")
        time.sleep(5)
        main.step("verifying connectivity between hosts after tunnel policy deletion")
        p1 = main.Mininet.pingHost(SRC="h1",TARGET="h2")
        result_step8 = p1
        utilities.assert_equals(expect=main.TRUE,actual=result_step8,
                                onpass="Connectivity check after tunnel policy deletion PASS",
                                onfail="Connectivity check after tunnel policy deletion FAIL")

        result = result_phase1 and result_step6 and result_step7 and result_step8 
        utilities.assert_equals(expect=main.TRUE,actual=result,
                                onpass="Tunnel Policy handling check PASS",
                                onfail="Tunnel Policy handling check FAIL")

        #cleanup mininet
        main.Mininet.disconnect()



#**********************************************************************************************************************************************************************************************
# A simple test for verifying tunnels and policies with auto generated adjacencySid

    def CASE5(self,main) :
        import time
        main.ONOS.stop()
        # starts the controller with 3-node topology
        main.step("Restarting ONOS and Zookeeper")
        ret = main.ONOS.start()
        if ret == main.FALSE:
            main.log.report("ONOS did not start ... Aborting")
            main.cleanup()
            main.exit()
        main.log.report("Running mininet")
        main.Mininet.connect()
        main.Mininet.handle.sendline("sudo python /home/onos/mininet/custom/testEcmp_6sw.py")
        main.step("waiting 40 secs for switches to connect and go thru handshake")
        time.sleep(40)
        main.step("verifying all to all connectivity")

        p1 = main.Mininet.pingHost(SRC="h2",TARGET="h1")
        p2 = main.Mininet.pingHost(SRC="h1",TARGET="192.168.0.5")
        pa = main.Mininet.pingall()
        result_step1 = p1 and p2 and pa
        utilities.assert_equals(expect=main.TRUE,actual=result_step1,
                                  onpass="Default connectivity check PASS",
                                  onfail="Default connectivity check FAIL")

        main.step("Verifying create tunnel functionality")
        ret = main.ONOS.create_tunnel(onosRESTIP="127.0.0.1",
                                      onosRESTPort=str(8080),
                                      tunnelURL="wm/onos/segmentrouting/tunnel",
                                      params="{\"tunnel_id\":\"t2\",\"label_path\":[101,102,102002,103,103003,104,105,106]}")
        result_step2 = ret
        utilities.assert_equals(expect=main.TRUE,actual=result_step2,
                                  onpass="Tunnel create check PASS",
                                  onfail="Tunnel create check FAIL")

        main.step("Verifying groups created as part tunnel t2 : 3groups@s1 and 1group@s5")
        switch_groups = main.ONOS.get_all_groups_of_tunnel(onosRESTIP="127.0.0.1",
                                      onosRESTPort=str(8080),
                                      tunnelURL="wm/onos/segmentrouting/tunnel",
                                      tunnel_id="t2")
        print "Groups created for tunnel t2",switch_groups
        ret_sw1 = main.FALSE
        ret_sw5 = main.FALSE
        ret_sw1_3groups = main.FALSE
        ret_sw5_1groups = main.FALSE
        ret_stats = main.FALSE
        for entry in switch_groups:
            if entry.has_key("SW"):
                #print "entry[SW]: ",entry['SW']
                if (entry['SW'] == "00:00:00:00:00:00:00:01"):
                    ret_sw1 = main.TRUE
                    if (len(entry['GROUPS']) == 2):
                        ret_sw1_3groups = main.TRUE
                if (entry['SW'] == "00:00:00:00:00:00:00:04"):
                    ret_sw5 = main.TRUE
                    if (len(entry['GROUPS']) == 1):
                        ret_sw5_1groups = main.TRUE
                before_stats = main.ONOS.get_switch_group_stats(onosRESTIP="127.0.0.1",
                                      onosRESTPort=str(8080),
                                      dpid=entry['SW'])
                #print "before_stats: ",before_stats
                if (before_stats != main.FALSE):
                    ret_stats = main.TRUE
                    entry['STATS'] = before_stats
        #print "results for group check: ", ret_sw1, ret_sw1_3groups, ret_sw5, ret_sw5_1groups, ret_stats    
        result_step3 = ret_sw1 and ret_sw1_3groups and ret_sw5 and ret_sw5_1groups and ret_stats
        utilities.assert_equals(expect=main.TRUE,actual=result_step3,
                                onpass="Tunnel groups check PASS",
                                onfail="Tunnel groups check FAIL")

        main.step("Verifying create policy functionality")
        #ret = main.ONOS.create_policy("http://127.0.0.1:8080/wm/onos/segmentrouting/policy","{\"priority\": 2223, \"dst_tp_port_op\": \"eq\", \"src_tp_port_op\": \"eq\", \"src_tp_port\": \"1000\", \"tunnel_id\": \"t1\", \"src_ip\": \"10.0.1.1/32\", \"policy_type\": \"tunnel-flow\", \"dst_ip\": \"7.7.7.7/32\", \"dst_tp_port\": \"2000\", \"proto_type\": \"ip\", \"policy_id\": \"pol1\"}")
        ret = main.ONOS.create_policy(onosRESTIP="127.0.0.1",
                                      onosRESTPort=str(8080),
                                      policyURL="/wm/onos/segmentrouting/policy",
                                      params="{\"priority\": 3223, \"tunnel_id\": \"t2\", \"src_ip\": \"10.0.1.1/32\", \"policy_type\": \"tunnel-flow\", \"dst_ip\": \"7.7.7.7/32\", \"proto_type\": \"ip\", \"policy_id\": \"pol2\"}")
        result_step4 = ret
        utilities.assert_equals(expect=main.TRUE,actual=result_step4,
                                onpass="Policy creation check PASS",
                                onfail="Policy creation check FAIL")
                                     
        main.step("waiting 5 secs to push the tunnels and policies to the switches")
        time.sleep(5)
        main.step("verifying connectivity between hosts after tunnel policy creation")
        p1 = main.Mininet.pingHost(SRC="h2",TARGET="h1")
        ret_group_stats = main.FALSE
        for entry in switch_groups:
            if entry.has_key("SW"):
                #print "entry[SW]: ",entry['SW']
                after_stats = main.ONOS.get_switch_group_stats(onosRESTIP="127.0.0.1",
                                      onosRESTPort=str(8080),
                                      dpid=entry['SW'])
                #print "after_stats: ",after_stats
                if after_stats != main.FALSE:
                    before_pkt_count = 0
                    after_pkt_count = 0
                    for group in entry['GROUPS']:
                        for beforeStat in before_stats:
                            if beforeStat['groupId'] == group:
                                before_pkt_count = beforeStat['packetCount']
                                break
                        for afterStat in after_stats:
                            if afterStat['groupId'] == group:
                                after_pkt_count = afterStat['packetCount']
                                break
                    if (((after_pkt_count-before_pkt_count) > 0) and
                        ((after_pkt_count-before_pkt_count) < 3)):
                        ret_group_stats = main.TRUE
                    else:
                        ret_group_stats = main.FALSE
                        break;

        result_step5 = p1 and ret_group_stats
        utilities.assert_equals(expect=main.TRUE,actual=result_step5,
                                onpass="Connectivity check on tunnel policy PASS",
                                onfail="Connectivity check on tunnel policy FAIL")

        result_phase1 = result_step1 and result_step2 and result_step3 and result_step4 and result_step5

        main.step("Verifying delete policy functionality")
        ret = main.ONOS.delete_policy(onosRESTIP="127.0.0.1",
                                      onosRESTPort=str(8080),
                                      policyURL="/wm/onos/segmentrouting/policy",
                                      params="{\"policy_id\": \"pol2\"}")
        result_step6 = ret
        utilities.assert_equals(expect=main.TRUE,actual=result_step5,
                                onpass="Policy deletion check PASS",
                                onfail="Policy deletion check FAIL")

        main.step("Verifying delete tunnel functionality")
        ret = main.ONOS.delete_tunnel(onosRESTIP="127.0.0.1",
                                      onosRESTPort=str(8080),
                                      tunnelURL="wm/onos/segmentrouting/tunnel",
                                      params="{\"tunnel_id\":\"t2\"}")
        result_step7 = ret
        
        utilities.assert_equals(expect=main.TRUE,actual=result_step7,
                                onpass="Tunnel deletion check PASS",
                                onfail="Tunnel deletion check FAIL")

        main.step("waiting 5 secs for tunnel and policy remove to happen")
        time.sleep(5)
        main.step("verifying connectivity between hosts after tunnel policy deletion")
        p1 = main.Mininet.pingHost(SRC="h2",TARGET="h1")
        result_step8 = p1
        utilities.assert_equals(expect=main.TRUE,actual=result_step8,
                                onpass="Connectivity check after tunnel policy deletion PASS",
                                onfail="Connectivity check after tunnel policy deletion FAIL")

        result = result_phase1 and result_step6 and result_step7 and result_step8
        utilities.assert_equals(expect=main.TRUE,actual=result,
                                onpass="Tunnel Policy handling check PASS",
                                onfail="Tunnel Policy handling check FAIL")

        #cleanup mininet
        main.Mininet.disconnect()

#**********************************************************************************************************************************************************************************************
# A simple test for verifying tunnels and policies with adjacencySid with multiple ports

    def CASE6(self,main) :
        import time
        main.ONOS.stop()
        # starts the controller with 3-node topology
        main.ONOS.handle.sendline("sed -i 's/sr-.*$/sr-ecmp10.conf/' conf/onos.properties")
        main.step("Restarting ONOS and Zookeeper")
        ret = main.ONOS.start()
        if ret == main.FALSE:
            main.log.report("ONOS did not start ... Aborting")
            main.cleanup()
            main.exit()
        main.log.report("Running mininet")
        main.Mininet.connect()
        main.Mininet.handle.sendline("sudo python /home/onos/mininet/custom/testEcmp_10sw.py")
        main.step("waiting 40 secs for switches to connect and go thru handshake")
        time.sleep(40)
        main.step("verifying all to all connectivity")

        p1 = main.Mininet.pingHost(SRC="h1",TARGET="h2")
        p2 = main.Mininet.pingHost(SRC="h1",TARGET="192.168.0.5")
        pa = main.Mininet.pingall()
        result_step1 = p1 and p2 and pa
        utilities.assert_equals(expect=main.TRUE,actual=result_step1,
                                  onpass="Default connectivity check PASS",
                                  onfail="Default connectivity check FAIL")

        main.step("Verifying create tunnel functionality")
        ret = main.ONOS.create_tunnel(onosRESTIP="127.0.0.1",
                                      onosRESTPort=str(8080),
                                      tunnelURL="wm/onos/segmentrouting/tunnel",
                                      params="{\"tunnel_id\":\"t3\",\"label_path\":[107,12345,102,104,106]}")
        result_step2 = ret
        utilities.assert_equals(expect=main.TRUE,actual=result_step2,
                                  onpass="Tunnel create check PASS",
                                  onfail="Tunnel create check FAIL")

        main.step("Verifying groups created as part tunnel t3 : 3groups@s7 (actually 6)")
        switch_groups = main.ONOS.get_all_groups_of_tunnel(onosRESTIP="127.0.0.1",
                                      onosRESTPort=str(8080),
                                      tunnelURL="wm/onos/segmentrouting/tunnel",
                                      tunnel_id="t3")
        print "Groups created for tunnel t3",switch_groups
        ret_sw7 = main.FALSE
        ret_sw7_3groups = main.FALSE
        ret_stats = main.FALSE
        for entry in switch_groups:
            if entry.has_key("SW"):
                #print "entry[SW]: ",entry['SW']
                if (entry['SW'] == "00:00:00:00:00:00:00:07"):
                    ret_sw7 = main.TRUE
                    #print "entry['GROUPS']:",len(entry['GROUPS'])
                    if (len(entry['GROUPS']) == 3):
                        ret_sw7_3groups = main.TRUE
                before_stats = main.ONOS.get_switch_group_stats(onosRESTIP="127.0.0.1",
                                      onosRESTPort=str(8080),
                                      dpid=entry['SW'])
                #print "before_stats: ",before_stats
                if (before_stats != main.FALSE):
                    ret_stats = main.TRUE
                    entry['STATS'] = before_stats
        #print "results for group check: ", ret_sw7, ret_sw7_3groups, ret_sw5, ret_stats    
        result_step3 = ret_sw7 and ret_sw7_3groups and ret_stats
        utilities.assert_equals(expect=main.TRUE,actual=result_step3,
                                onpass="Tunnel groups check PASS",
                                onfail="Tunnel groups check FAIL")

        main.step("Verifying create policy functionality")
        #ret = main.ONOS.create_policy("http://127.0.0.1:8080/wm/onos/segmentrouting/policy","{\"priority\": 2223, \"dst_tp_port_op\": \"eq\", \"src_tp_port_op\": \"eq\", \"src_tp_port\": \"1000\", \"tunnel_id\": \"t3\", \"src_ip\": \"10.1.1.1/32\", \"policy_type\": \"tunnel-flow\", \"dst_ip\": \"7.7.7.7/32\", \"dst_tp_port\": \"2000\", \"proto_type\": \"ip\", \"policy_id\": \"pol3\"}")
        ret = main.ONOS.create_policy(onosRESTIP="127.0.0.1",
                                      onosRESTPort=str(8080),
                                      policyURL="/wm/onos/segmentrouting/policy",
                                      params="{\"priority\": 3223, \"tunnel_id\": \"t3\", \"src_ip\": \"10.1.1.1/32\", \"policy_type\": \"tunnel-flow\", \"dst_ip\": \"7.7.7.7/32\", \"proto_type\": \"ip\", \"policy_id\": \"pol3\"}")
        result_step4 = ret
        utilities.assert_equals(expect=main.TRUE,actual=result_step4,
                                onpass="Policy creation check PASS",
                                onfail="Policy creation check FAIL")

        main.step("waiting 5 secs to push the tunnels and policies to the switches")
        time.sleep(5)
        main.step("verifying connectivity between hosts after tunnel policy creation")
        p1 = main.Mininet.pingHost(SRC="h2",TARGET="h3")
        ret_group_stats = main.FALSE
        for entry in switch_groups:
            if entry.has_key("SW"):
                #print "entry[SW]: ",entry['SW']
                after_stats = main.ONOS.get_switch_group_stats(onosRESTIP="127.0.0.1",
                                      onosRESTPort=str(8080),
                                      dpid=entry['SW'])
                #print "after_stats: ",after_stats
                if after_stats != main.FALSE:
                    before_pkt_count = 0
                    after_pkt_count = 0
                    for group in entry['GROUPS']:
                        for beforeStat in before_stats:
                            if beforeStat['groupId'] == group:
                                before_pkt_count = beforeStat['packetCount']
                                break
                        for afterStat in after_stats:
                            if afterStat['groupId'] == group:
                                after_pkt_count = afterStat['packetCount']
                                break
                    #print "after_pkt_count-before_pkt_count:", after_pkt_count-before_pkt_count
                    if (((after_pkt_count-before_pkt_count) > 0) and
                        ((after_pkt_count-before_pkt_count) < 3)):
                        ret_group_stats = main.TRUE
                    else:
                        ret_group_stats = main.FALSE
                        break;

        result_step5 = p1 and ret_group_stats
        utilities.assert_equals(expect=main.TRUE,actual=result_step5,
                                onpass="Connectivity check on tunnel policy PASS",
                                onfail="Connectivity check on tunnel policy FAIL")

        result_phase1 = result_step1 and result_step2 and result_step3 and result_step4 and result_step5

        main.step("Verifying delete policy functionality")
        ret = main.ONOS.delete_policy(onosRESTIP="127.0.0.1",
                                      onosRESTPort=str(8080),
                                      policyURL="/wm/onos/segmentrouting/policy",
                                      params="{\"policy_id\": \"pol3\"}")
        result_step6 = ret
        utilities.assert_equals(expect=main.TRUE,actual=result_step5,
                                onpass="Policy deletion check PASS",
                                onfail="Policy deletion check FAIL")

        main.step("Verifying delete tunnel functionality")
        ret = main.ONOS.delete_tunnel(onosRESTIP="127.0.0.1",
                                      onosRESTPort=str(8080),
                                      tunnelURL="wm/onos/segmentrouting/tunnel",
                                      params="{\"tunnel_id\":\"t3\"}")
        result_step7 = ret

        utilities.assert_equals(expect=main.TRUE,actual=result_step7,
                                onpass="Tunnel deletion check PASS",
                                onfail="Tunnel deletion check FAIL")

        main.step("waiting 5 secs for tunnel and policy remove to happen")
        time.sleep(5)
        main.step("verifying connectivity between hosts after tunnel policy deletion")
        p1 = main.Mininet.pingHost(SRC="h1",TARGET="h3")
        result_step8 = p1
        utilities.assert_equals(expect=main.TRUE,actual=result_step8,
                                onpass="Connectivity check after tunnel policy deletion PASS",
                                onfail="Connectivity check after tunnel policy deletion FAIL")

        result = result_phase1 and result_step6 and result_step7 and result_step8
        utilities.assert_equals(expect=main.TRUE,actual=result,
                                onpass="Tunnel Policy handling check PASS",
                                onfail="Tunnel Policy handling check FAIL")

        #cleanup mininet
        main.Mininet.disconnect()
#**********************************************************************************************************************************************************************************************
# Restarts the controller in a linear 3-node topology

    def CASE10(self,main) :
        main.ONOS.stop()
        # starts the controller with 3-node topology
        main.ONOS.handle.sendline("sed -i 's/sr-.*$/sr-3node.conf/' conf/onos.properties")
        main.step("Restarting ONOS and Zookeeper")
        ret = main.ONOS.start()
        if ret == main.FALSE:
            main.log.report("ONOS did not start ... Aborting")
            main.cleanup()
            main.exit()
        main.log.report("Running mininet")
        main.Mininet.connect()
        #main.Mininet.handle.sendline("sudo mn -c")
        main.Mininet.handle.sendline("sudo python /home/onos/mininet/custom/test13_3sw.py")
        main.step("waiting 40 secs for switches to connect and go thru handshake")
        time.sleep(40)
        #main.step("verifying all to all connectivity")
        
        p1 = main.Mininet.pingHost(SRC="h1",TARGET="h6")
        p2 = main.Mininet.pingHost(SRC="h1",TARGET="192.168.0.2")
        result = p1 and p2
        
        utilities.assert_equals(expect=main.TRUE,actual=result,
                                onpass="Default connectivity check PASS",
                                onfail="Default connectivity check FAIL")
        #cleanup mininet
        main.Mininet.disconnect()
        #main.Mininet.cleanup()
        #main.Mininet.exit()
       

#**********************************************************************************************************************************************************************************************
# Restarts the controller in a ring topology

    def CASE20(self,main) :
        main.ONOS.stop()
        # starts the controller with ring topology
        main.ONOS.handle.sendline("sed -i 's/sr-.*$/sr-ring.conf/' conf/onos.properties")
        main.step("Restarting ONOS and Zookeeper")
        ret = main.ONOS.start()
        if ret == main.FALSE:
            main.log.report("ONOS did not start ... Aborting")
            main.cleanup()
            main.exit()
        main.log.report("Running mininet")
        main.Mininet.connect()
        #main.Mininet.handle.sendline("sudo mn -c")
        main.Mininet.handle.sendline("sudo python /home/onos/mininet/custom/testRing_5sw.py")
        main.step("waiting 40 secs for switches to connect and go thru handshake")
        time.sleep(40)
        #main.step("verifying all to all connectivity")

        p1 = main.Mininet.pingHost(SRC="h1",TARGET="192.168.0.2")
        p2 = main.Mininet.pingall()
        result = p1 and p2

        utilities.assert_equals(expect=main.TRUE,actual=result,
                                onpass="Default connectivity check PASS",
                                onfail="Default connectivity check FAIL")
        #cleanup mininet
        main.Mininet.disconnect()
        #main.Mininet.cleanup()
        #main.Mininet.exit() 

#**********************************************************************************************************************************************************************************************
# Restarts the controller in 10 switch topology

    def CASE30(self,main) :
        main.ONOS.stop()
        # starts the controller with 10 switch topology
        main.ONOS.handle.sendline("sed -i 's/sr-.*$/sr-ecmp10.conf/' conf/onos.properties")
        main.step("Restarting ONOS and Zookeeper")
        ret = main.ONOS.start()
        if ret == main.FALSE:
            main.log.report("ONOS did not start ... Aborting")
            main.cleanup()
            main.exit()
        main.log.report("Running mininet")
        main.Mininet.connect()
        #main.Mininet.handle.sendline("sudo mn -c")
        main.Mininet.handle.sendline("sudo python /home/onos/mininet/custom/testEcmp_10sw.py")
        main.step("waiting 40 secs for switches to connect and go thru handshake")
        time.sleep(40)
        #main.step("verifying all to all connectivity")

        p1 = main.Mininet.pingHost(SRC="h1",TARGET="192.168.0.5")
        p2 = main.Mininet.pingall()
        result = p1 and p2

        utilities.assert_equals(expect=main.TRUE,actual=result,
                                onpass="Default connectivity check PASS",
                                onfail="Default connectivity check FAIL")
        #cleanup mininet
        main.Mininet.disconnect()
        #main.Mininet.cleanup()
        #main.Mininet.exit() 

#**********************************************************************************************************************************************************************************************
# Leaf-Spine topology : 4 x 4

    def CASE50(self, main) :
        import time

        main.step("Copy the config file")
        main.ONOSbench.handle.sendline("cp ~/TestON/tests/SRSanity/leafspine.conf ~/onos/tools/package/config/segmentrouting.conf")
        cleanInstallResult = main.ONOSbench.cleanInstallSkipTest()
        main.ONOSbench.onosPackage()

        main.log.report( "Removing raft logs" )
        main.ONOSbench.onosRemoveRaftLogs()
        main.log.report( "Uninstalling ONOS" )
        main.ONOSbench.onosUninstall( ONOS1Ip )

        main.step( "Installing ONOS package" )
        onos1InstallResult = main.ONOSbench.onosInstall(
            options="-f", node=ONOS1Ip )

        onos1Isup = main.ONOSbench.isup( ONOS1Ip )
        if not onos1Isup:
            main.log.report( "ONOS1 didn't start!" )

        main.step( "Start ONOS-cli" )

        main.ONOScli.startOnosCli( ONOS1Ip )
        time.sleep(20)

        main.log.info( "Installing segmentrouting feature" )
        main.ONOScli.handle.sendline( "app activate org.onosproject.segmentrouting" )
        time.sleep( 10 )

        main.log.report("Running mininet")
        main.Mininet.connect()
        main.Mininet.handle.sendline("sudo python /home/admin/TestON/tests/SRSanity/mininet/testLeafSpine.py")
        main.step("waiting 40 secs for switches to connect and go thru handshake")
        time.sleep(40)
        main.step("verifying all to all connectivity")

        p1 = main.Mininet.pingHost(SRC="h2",TARGET="h1")
        p2 = main.Mininet.pingHost(SRC="h1",TARGET="192.168.0.4")
        pa = main.Mininet.pingall()
        result = p1 and p2 and pa
        utilities.assert_equals(expect=main.TRUE,actual=result,
                                onpass="Default connectivity check PASS",
                                onfail="Default connectivity check FAIL")
        #cleanup mininet
        main.ONOScli.logout()
        main.ONOSbench.onosStop(ONOS1Ip);
        main.Mininet.stopNet()
        main.Mininet.disconnect()
        main.Mininet.cleanup()
        main.Mininet.exit() 
       
