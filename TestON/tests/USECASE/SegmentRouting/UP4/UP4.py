class UP4:

    def __init__(self):
        self.default = ''

    def CASE1(self, main):
        main.case("Fabric UPF traffic terminated in the fabric")
        """
        Program UPF entities for UEs
        Verify UPF entities
        Generate traffic from UE to PDN
        Verify traffic received from PDN
        Generate traffic from PDN to UE
        Verify traffic received from UE
        Remove UPF entities for UEs
        Verify removed UPF entities
        """
        try:
            from tests.USECASE.SegmentRouting.dependencies.up4 import UP4
            from tests.USECASE.SegmentRouting.dependencies.Testcaselib import \
                Testcaselib as run
        except ImportError as e:
            main.log.error("Import not found. Exiting the test")
            main.log.error(e)
            main.cleanAndExit()
        n_switches = int(main.params["TOPO"]["switchNum"])

        run.initTest(main)
        main.log.info(main.Cluster.numCtrls)
        main.Cluster.setRunningNode(3)
        run.installOnos(main, skipPackage=True, cliSleep=5)

        main.step("Start scapy and p4rt client")
        # Use the first available ONOS instance CLI
        onos_cli = main.Cluster.active(0).CLI
        up4 = UP4()
        # Get the P4RT client connected to UP4 in the first available ONOS instance
        up4.setup(main.Cluster.active(0).p4rtUp4)

        main.step("Program and Verify UPF entities via UP4")
        up4.attachUes()
        up4.verifyUp4Flow(onos_cli)

        # ------- Test Upstream traffic (enb->pdn)
        for app_filter_name in up4.app_filters:
            main.step("Test upstream traffic %s" % app_filter_name)
            up4.testUpstreamTraffic(app_filter_name=app_filter_name)

        # ------- Test Downstream traffic (pdn->enb)
        for app_filter_name in up4.app_filters:
            main.step("Test downstream traffic %s" % app_filter_name)
            up4.testDownstreamTraffic(app_filter_name=app_filter_name)

        main.step("Remove and Verify UPF entities via UP4")
        up4.detachUes()
        up4.verifyNoUesFlow(onos_cli)

        main.step("Stop scapy and p4rt client")
        up4.teardown()

        run.cleanup(main)

    def CASE2(self, main):
        main.case("BESS traffic routed")
        """
        Program UPF entities for UEs managed via UP4
        Verify UPF entities
        Verify Upstream Traffic: eNB -> Fabric -> BESS (encapped)
        Verify Upstream Traffic: BESS -> Fabric -> PDN (not encapped)
        Verify Downstream Traffic: PDN -> Fabric -> BESS (not encapped)
        Verify Downstream Traffic: BESS -> Fabric -> eNB (encapped)
        Remove UPF entities for UEs managed via UP4
        Verify removed UPF entities
        """
        BESS_TEID = 300
        GPDU_PORT = 2152
        UE_PORT = 400
        PDN_PORT = 800
        try:
            from tests.USECASE.SegmentRouting.dependencies.up4 import UP4
            from tests.USECASE.SegmentRouting.dependencies.Testcaselib import \
                Testcaselib as run
        except ImportError as e:
            main.log.error("Import not found. Exiting the test")
            main.log.error(e)
            main.cleanAndExit()
        n_switches = int(main.params["TOPO"]["switchNum"])

        run.initTest(main)
        main.log.info(main.Cluster.numCtrls)
        main.Cluster.setRunningNode(3)
        run.installOnos(main, skipPackage=True, cliSleep=5)

        main.step("Start scapy and p4rt client + Scapy on BESS Host")
        # Use the first available ONOS instance CLI
        onos_cli = main.Cluster.active(0).CLI
        up4 = UP4()
        # Get the P4RT client connected to UP4 in the first available ONOS instance
        up4.setup(main.Cluster.active(0).p4rtUp4)

        # Setup the emulated BESS host and required parameters
        bess_host = getattr(main, main.params["BESS_UPF"]["bess_host"])
        bess_interface = bess_host.interfaces[0]
        bess_s1u_address = bess_interface["ips"][0]
        bess_host.startScapy(ifaceName=bess_interface["name"], enableGtp=True)
        bess_ue_address = main.params["BESS_UPF"]["ue_address"]
        enodeb_host = getattr(main, main.params["BESS_UPF"]["enodeb_host"])
        enodeb_address = main.params["BESS_UPF"]["enb_address"]
        enodeb_interface = enodeb_host.interfaces[0]["name"]
        pdn_host = up4.pdn_host
        pdn_interface = up4.pdn_interface

        main.step("Program and Verify UPF entities for UEs via UP4")
        up4.attachUes()
        up4.verifyUp4Flow(onos_cli)

        # ------------------- UPSTREAM -------------------
        # ------- eNB -> fabric -> BESS (encapped)
        main.step("Test upstream eNB -> fabric -> BESS")
        # Start filter before sending packets, BESS should receive GTP encapped
        # packets
        pkt_filter_upstream = "ip and udp src port %d and udp dst port %d and src host %s and dst host %s" % (
            GPDU_PORT, GPDU_PORT, enodeb_address, bess_s1u_address)
        main.log.info("Start listening on %s intf %s" % (
            bess_host.name, bess_interface["name"]))
        main.log.debug("BPF Filter BESS Upstream: \n %s" % pkt_filter_upstream)
        bess_host.startFilter(ifaceName=bess_interface["name"],
                              sniffCount=1,
                              pktFilter=pkt_filter_upstream)
        # Send GTP Packet
        UP4.buildGtpPacket(enodeb_host,
                           src_ip_outer=enodeb_address,
                           dst_ip_outer=bess_s1u_address,
                           src_ip_inner=bess_ue_address,
                           dst_ip_inner=pdn_interface["ips"][0],
                           src_udp_inner=UE_PORT,
                           dst_udp_inner=PDN_PORT,
                           teid=BESS_TEID)
        enodeb_host.sendPacket()

        packets = UP4.checkFilterAndGetPackets(bess_host)
        # FIXME: with newer scapy TEID becomes teid (required for Scapy 2.4.5)
        n_packets = packets.count("TEID=" + hex(BESS_TEID) + "L ")
        tot_packets = packets.count('Ether')
        utilities.assert_equal(expect=True,
                               actual=n_packets == 1 and tot_packets == 1,
                               onpass="BESS correctly received 1 GTP encapped packet",
                               onfail="ERROR: BESS received %d GTP encapped packets and filter captured %d packets" % (
                                   n_packets, tot_packets))

        # ------- BESS -> fabric -> PDN (not-encapped)
        main.step("Test upstream BESS -> fabric -> PDN")
        # Start filter before sending packets, PDN should receive non-GTP packet
        pkt_filter_upstream = "ip and udp src port %d and udp dst port %d and src host %s and dst host %s" % (
            UE_PORT, PDN_PORT, bess_ue_address, pdn_interface["ips"][0])
        main.log.info("Start listening on %s intf %s" % (
            pdn_host.name, pdn_interface["name"]))
        main.log.debug("BPF Filter PDN Upstream: \n %s" % pkt_filter_upstream)
        pdn_host.startFilter(ifaceName=pdn_interface["name"],
                             sniffCount=1,
                             pktFilter=pkt_filter_upstream)
        # Send UDP Packet
        UP4.buildUdpPacket(bess_host,
                           src_ip=bess_ue_address,
                           dst_ip=pdn_interface["ips"][0],
                           src_udp=UE_PORT,
                           dst_udp=PDN_PORT)
        bess_host.sendPacket()

        packets = UP4.checkFilterAndGetPackets(pdn_host)
        tot_packets = packets.count('Ether')
        utilities.assert_equal(expect=True,
                               actual=tot_packets == 1,
                               onpass="PDN correctly received 1 packet",
                               onfail="ERROR: PDN received %d packets" % (
                                   tot_packets))
        # ------------------------------------------------

        # ------------------ DOWNSTREAM ------------------
        # ------- PDN -> fabric -> BESS (not-encapped)
        main.step("Test downstream PDN -> fabric -> BESS")
        pkt_filter_downstream = "ip and udp src port %d and udp dst port %d and src host %s and dst host %s" % (
            PDN_PORT, UE_PORT, pdn_interface["ips"][0], bess_ue_address)
        main.log.info("Start listening on %s intf %s" % (
            bess_host.name, bess_interface["name"]))
        main.log.debug(
            "BPF Filter BESS Downstream: \n %s" % pkt_filter_downstream)
        bess_host.startFilter(ifaceName=bess_interface["name"],
                              sniffCount=1,
                              pktFilter=pkt_filter_downstream)
        UP4.buildUdpPacket(pdn_host,
                           dst_eth=up4.router_mac,
                           src_ip=pdn_interface["ips"][0],
                           dst_ip=bess_ue_address,
                           src_udp=PDN_PORT,
                           dst_udp=UE_PORT)
        pdn_host.sendPacket()

        packets = UP4.checkFilterAndGetPackets(bess_host)

        tot_packets = packets.count('Ether')
        utilities.assert_equal(expect=True,
                               actual=tot_packets == 1,
                               onpass="BESS correctly received 1 packet",
                               onfail="ERROR: BESS received %d packets" % (
                                   tot_packets))

        # ------- BESS -> fabric -> eNB (encapped)
        main.step("Test downstream BESS -> fabric -> eNB")
        pkt_filter_downstream = "ip and udp src port %d and udp dst port %d and src host %s and dst host %s" % (
            GPDU_PORT, GPDU_PORT, bess_s1u_address, enodeb_address)
        main.log.info("Start listening on %s intf %s" % (
            enodeb_host.name, enodeb_interface))
        main.log.debug(
            "BPF Filter BESS Downstream: \n %s" % pkt_filter_downstream)
        enodeb_host.startFilter(ifaceName=enodeb_interface,
                                sniffCount=1,
                                pktFilter=pkt_filter_downstream)
        # Build GTP packet from BESS host
        UP4.buildGtpPacket(bess_host,
                           src_ip_outer=bess_s1u_address,
                           dst_ip_outer=enodeb_address,
                           src_ip_inner=pdn_interface["ips"][0],
                           dst_ip_inner=bess_ue_address,
                           src_udp_inner=PDN_PORT,
                           dst_udp_inner=UE_PORT,
                           teid=BESS_TEID)
        bess_host.sendPacket()

        packets = UP4.checkFilterAndGetPackets(enodeb_host)

        # FIXME: with newer scapy TEID becomes teid (required for Scapy 2.4.5)
        n_packets = packets.count("TEID=" + hex(BESS_TEID) + "L ")
        tot_packets = packets.count('Ether')
        utilities.assert_equal(expect=True,
                               actual=n_packets == 1 and tot_packets == 1,
                               onpass="eNodeB correctly received 1 GTP encapped packet",
                               onfail="ERROR: eNodeb received %d GTP encapped packets and filter captured %d packets" % (
                                   n_packets, tot_packets))
        # ------------------------------------------------

        main.step("Remove and Verify UPF entities for UEs via UP4")
        up4.detachUes()
        up4.verifyNoUesFlow(onos_cli)

        main.step("Stop scapy and p4rt client")
        up4.teardown()
        bess_host.stopScapy()

        run.cleanup(main)

    def CASE3(self, main):
        main.case("Verify UP4 from different ONOS instances")
        """
        Program UPF entitiesvia UP4 on first ONOS instance
        Repeat for all ONOS Instances:
            Verify UPF entities via P4RT
            Disconnect P4RT client
        Verify and delete UPF entities via UP4 on the third ONOS instance
        Repeat for all ONOS Instance:
            Verify removed UPF entities via P4RT
            Disconnect P4RT client
        """
        try:
            from tests.USECASE.SegmentRouting.dependencies.up4 import UP4
            from tests.USECASE.SegmentRouting.dependencies.Testcaselib import \
                Testcaselib as run
        except ImportError as e:
            main.log.error("Import not found. Exiting the test")
            main.log.error(e)
            main.cleanAndExit()
        n_switches = int(main.params["TOPO"]["switchNum"])

        run.initTest(main)
        main.log.info(main.Cluster.numCtrls)
        main.Cluster.setRunningNode(3)
        run.installOnos(main, skipPackage=True, cliSleep=5)

        onos_cli_0 = main.Cluster.active(0).CLI
        onos_cli_1 = main.Cluster.active(1).CLI
        onos_cli_2 = main.Cluster.active(2).CLI
        up4_0 = UP4()
        up4_1 = UP4()
        up4_2 = UP4()

        main.step("Program and Verify UPF entities via UP4 on ONOS 0")
        up4_0.setup(main.Cluster.active(0).p4rtUp4, no_host=True)
        up4_0.attachUes()
        up4_0.verifyUp4Flow(onos_cli_0)
        up4_0.teardown()

        main.step("Verify UPF entities number via UP4 P4RT on ONOS 1")
        up4_1.setup(main.Cluster.active(1).p4rtUp4, no_host=True)
        utilities.assert_equal(
            expect=True,
            actual=up4_1.verifyUesFlowNumberP4rt(),
            onpass="Correct number of UPF entities",
            onfail="Wrong number of UPF entities"
        )
        up4_1.teardown()

        main.step("Verify UPF entities number via UP4 P4RT on ONOS 2")
        up4_2.setup(main.Cluster.active(2).p4rtUp4, no_host=True)
        utilities.assert_equal(
            expect=True,
            actual=up4_2.verifyUesFlowNumberP4rt(),
            onpass="Correct number of UPF entities",
            onfail="Wrong number of UPF entities"
        )

        main.step("Verify all ONOS instances have the same number of flows")
        onos_0_flow_count = onos_cli_0.checkFlowCount()
        onos_1_flow_count = onos_cli_1.checkFlowCount()
        onos_2_flow_count = onos_cli_2.checkFlowCount()
        utilities.assert_equal(
            expect=True,
            actual=onos_0_flow_count == onos_1_flow_count == onos_2_flow_count,
            onpass="All ONOS instances have the same number of flows",
            onfail="ONOS instances have different number of flows: (%d, %d, %d)" % (
                onos_0_flow_count, onos_1_flow_count, onos_2_flow_count)
        )

        main.step("Remove and Verify UPF entities via UP4 on ONOS 2")
        up4_2.detachUes()
        up4_2.verifyNoUesFlow(onos_cli_2)

        main.step("Verify no UPF entities via UP4 P4RT on ONOS 2")
        utilities.assert_equal(
            expect=True,
            actual=up4_2.verifyNoUesFlowNumberP4rt(),
            onpass="No UPF entities",
            onfail="Stale UPF entities"
        )
        up4_2.teardown()

        main.step("Verify no UPF entities via UP4 P4RT on ONOS 1")
        up4_1.setup(main.Cluster.active(1).p4rtUp4, no_host=True)
        utilities.assert_equal(
            expect=True,
            actual=up4_1.verifyNoUesFlowNumberP4rt(),
            onpass="No UPF entities",
            onfail="Stale UPF entities"
        )
        up4_1.teardown()

        main.step("Verify no UPF entities via UP4 P4RT on ONOS 0")
        up4_0.setup(main.Cluster.active(0).p4rtUp4, no_host=True)
        utilities.assert_equal(
            expect=True,
            actual=up4_0.verifyNoUesFlowNumberP4rt(),
            onpass="No UPF entities",
            onfail="Stale UPF entities"
        )
        up4_0.teardown()

        main.step("Verify all ONOS instances have the same number of flows")
        onos_0_flow_count = onos_cli_0.checkFlowCount()
        onos_1_flow_count = onos_cli_1.checkFlowCount()
        onos_2_flow_count = onos_cli_2.checkFlowCount()
        utilities.assert_equal(
            expect=True,
            actual=onos_0_flow_count == onos_1_flow_count == onos_2_flow_count,
            onpass="All ONOS instances have the same number of flows",
            onfail="ONOS instances have different number of flows: (%d, %d, %d)" % (
                onos_0_flow_count, onos_1_flow_count, onos_2_flow_count)
        )

        run.cleanup(main)

    def CASE4(self, main):
        main.case("Verify UP4 wipe-out after ONOS reboot")
        """
        Program UPF entities
        Kill ONOS POD
        Verify UPF entities from other ONOS instances
        Remove UPF entities
        Wait/Verify ONOS is back
        Verify no UPF entities from rebooted instance
        Re-program UPF entities from rebooted instance
        Verify all instances have same number of flows
        Remove UPF entities (cleanup)
        """
        try:
            from tests.USECASE.SegmentRouting.dependencies.up4 import UP4
            from tests.USECASE.SegmentRouting.dependencies.Testcaselib import \
                Testcaselib as run
            from tests.USECASE.SegmentRouting.SRStaging.dependencies.SRStagingTest import \
                SRStagingTest
        except ImportError as e:
            main.log.error("Import not found. Exiting the test")
            main.log.error(e)
            main.cleanAndExit()
        n_switches = int(main.params["TOPO"]["switchNum"])

        run.initTest(main)
        main.log.info(main.Cluster.numCtrls)
        main.Cluster.setRunningNode(3)
        run.installOnos(main, skipPackage=True, cliSleep=5)

        onos_cli_0 = main.Cluster.active(0).CLI
        onos_cli_1 = main.Cluster.active(1).CLI
        onos_cli_2 = main.Cluster.active(2).CLI
        ctrl_0 = main.Cluster.active(0)

        up4_0 = UP4()
        up4_1 = UP4()
        up4_2 = UP4()

        main.step("Program and Verify UPF entities via UP4 on ONOS 0")
        up4_0.setup(main.Cluster.active(0).p4rtUp4, no_host=True)
        up4_0.attachUes()
        up4_0.verifyUp4Flow(onos_cli_0)
        up4_0.teardown()

        onosPod = main.params["UP4_delete_pod"]

        # Save ONOS diags of the POD we are killing otherwise we lose ONOS logs
        main.ONOSbench.onosDiagnosticsK8s(
            [onosPod],
            main.logdir,
            "-CASE%d-%s_BeforeKill" % (main.CurrentTestCaseNumber, onosPod)
        )

        onosK8sNode = SRStagingTest.onosDown(main, ctrl_0, preventRestart=True)

        main.step("Verify UPF entities number via UP4 P4RT on ONOS 2")
        up4_2.setup(main.Cluster.active(2).p4rtUp4, no_host=True)
        utilities.assert_equal(
            expect=True,
            actual=up4_2.verifyUesFlowNumberP4rt(),
            onpass="Correct number of UPF entities",
            onfail="Wrong number of UPF entities"
        )

        main.step("Remove and Verify UPF entities via UP4 on ONOS 2")
        up4_2.detachUes()
        up4_2.verifyNoUesFlow(onos_cli_2)

        main.step("Verify no UPF entities via UP4 P4RT on ONOS 2")
        utilities.assert_equal(
            expect=True,
            actual=up4_2.verifyNoUesFlowNumberP4rt(),
            onpass="No UPF entities",
            onfail="Stale UPF entities"
        )
        up4_2.teardown()

        main.step(
            "Verify all active ONOS instances have the same number of flows")
        onos_1_flow_count = onos_cli_1.checkFlowCount()
        onos_2_flow_count = onos_cli_2.checkFlowCount()
        utilities.assert_equal(
            expect=True,
            actual=onos_1_flow_count == onos_2_flow_count,
            onpass="All ONOS instances have the same number of flows",
            onfail="ONOS instances have different number of flows: (%d, %d)" % (
                onos_1_flow_count, onos_2_flow_count)
        )

        SRStagingTest.onosUp(main, onosK8sNode, ctrl_0)

        main.step("Verify ONOS cluster is in good shape")
        onosNodesStatus = utilities.retry(
            f=main.Cluster.nodesCheck,
            retValue=False,
            sleep=5,
            attempts=10
        )
        utilities.assert_equal(
            expect=True,
            actual=onosNodesStatus,
            onpass="ONOS nodes status correct",
            onfail="Wrong ONOS nodes status"
        )

        main.step("Verify no UPF entities via UP4 P4RT on ONOS 0")
        up4_0.setup(main.Cluster.active(0).p4rtUp4, no_host=True)
        utilities.assert_equal(
            expect=True,
            actual=up4_0.verifyNoUesFlowNumberP4rt(),
            onpass="No UPF entities",
            onfail="Stale UPF entities"
        )

        main.step("Re-program UPF entities via UP4 on ONOS 0 after restart")
        up4_0.attachUes()
        up4_0.verifyUp4Flow(onos_cli_0)
        up4_0.teardown()

        main.step("Verify UPF entities via UP4 on ONOS 1")
        up4_1.setup(main.Cluster.active(1).p4rtUp4, no_host=True)
        up4_1.verifyUp4Flow(onos_cli_1)

        main.step("Verify all ONOS instances have the same number of flows")
        onos_0_flow_count = onos_cli_0.checkFlowCount()
        onos_1_flow_count = onos_cli_1.checkFlowCount()
        onos_2_flow_count = onos_cli_2.checkFlowCount()
        utilities.assert_equal(
            expect=True,
            actual=onos_0_flow_count == onos_1_flow_count == onos_2_flow_count,
            onpass="All ONOS instances have the same number of flows",
            onfail="ONOS instances have different number of flows: (%d, %d, %d)" % (
                onos_0_flow_count, onos_1_flow_count, onos_2_flow_count)
        )

        main.step("Cleanup UPF entities via UP4 on ONOS 1")
        up4_1.detachUes()
        up4_1.verifyNoUesFlow(onos_cli_1)
        up4_1.teardown()

        run.cleanup(main)

    def CASE5(self, main):
        main.case("UP4 Data Plane Failure Test")
        """
        Program UPF entities
        Kill one switch
        Set label on switch K8S node to prevent K8S to redeploy stratum
        Verify that traffic from eNodebs that are connected to that switch fails
        Verify that traffic from other eNodeBs is being forwarded
        Wait for the switch to be up again
        Check flows
        Remove UPF entities (cleanup)
        """
        try:
            from tests.USECASE.SegmentRouting.dependencies.up4 import UP4
            from tests.USECASE.SegmentRouting.dependencies.Testcaselib import \
                Testcaselib as run
            from tests.USECASE.SegmentRouting.SRStaging.dependencies.SRStagingTest import \
                SRStagingTest
            import time
            import itertools
        except ImportError as e:
            main.log.error("Import not found. Exiting the test")
            main.log.error(e)
            main.cleanAndExit()
        n_switches = int(main.params["TOPO"]["switchNum"])
        switch_to_kill = main.params["UP4"]["UP4_dataplane_fail"]["switch_to_kill"]
        k8s_switch_node = main.params["UP4"]["UP4_dataplane_fail"]["k8s_switch_node"]
        k8s_label = main.params["UP4"]["UP4_dataplane_fail"]["k8s_label"]
        k8s_label_value_test = main.params["UP4"]["UP4_dataplane_fail"]["k8s_label_value_test"]
        k8s_label_value_normal = main.params["UP4"]["UP4_dataplane_fail"]["k8s_label_value_normal"]

        run.initTest(main)
        main.log.info(main.Cluster.numCtrls)
        main.Cluster.setRunningNode(3)
        run.installOnos(main, skipPackage=True, cliSleep=5)

        onos_cli = main.Cluster.active(0).CLI
        kubectl = main.Cluster.active(0).Bench
        kubeconfig = main.Cluster.active(0).k8s.kubeConfig
        namespace = main.params['kubernetes']['namespace']

        up4 = UP4()

        main.step("Program and Verify UPF entities via UP4")
        up4.setup(main.Cluster.active(0).p4rtUp4)
        up4.attachUes()
        up4.verifyUp4Flow(onos_cli)

        main.step("Set label to switch k8s node and kill switch")
        # K8s node name correspond to the switch name in lowercase
        utilities.assert_equal(
            expect=main.TRUE,
            actual=kubectl.kubectlSetLabel(
                nodeName=k8s_switch_node,
                label=k8s_label,
                value=k8s_label_value_test,
                kubeconfig=kubeconfig,
                namespace=namespace,
            ),
            onpass="Label has been set correctly on node %s" % k8s_switch_node,
            onfail="Label has not been set on node %s" % k8s_switch_node
        )
        try:
            def checkNumberStratumPods(n_value):
                pods = kubectl.kubectlGetPodNames(
                    kubeconfig=kubeconfig,
                    namespace=namespace,
                    name="stratum"
                )
                main.log.info("PODS: " + str(pods))
                return n_value == len(pods) if pods is not main.FALSE else False
            # Execute the following in try/except/finally to be sure to restore the
            # k8s label even in case of unhandled exception.

            # Wait for stratum pod to be removed from the switch
            removed = utilities.retry(checkNumberStratumPods,
                            False,
                            args=[n_switches-1],
                            attempts=50
            )
            main.log.info("Stratum has been removed from the switch? %s" % removed)

            switch_component = getattr(main, switch_to_kill)
            switch_component.handle.sendline("sudo reboot")

            sleepTime = 20
            main.log.info("Sleeping %s seconds for Fabric to react" % sleepTime)
            time.sleep(sleepTime)

            available = utilities.retry(SRStagingTest.switchIsConnected,
                                        True,
                                        args=[switch_component],
                                        attempts=300,
                                        getRetryingTime=True)
            main.log.info("Switch %s is available in ONOS? %s" % (
                switch_to_kill, available))
            utilities.assert_equal(
                expect=True,
                actual=not available and removed,
                onpass="Switch was rebooted (ONL reboot) successfully and stratum" +
                       " removed from switch k8s node",
                onfail="Switch was not rebooted (ONL reboot) successfully or stratum " +
                       "not removed from switch k8s node"
            )

            enodebs_fail = main.params["UP4"]["UP4_dataplane_fail"]["enodebs_fail"].split(",")
            enodebs_no_fail = list(set(up4.enodebs.keys()) - set(enodebs_fail))


            for app_filter_name in up4.app_filters:
                # Failure only when we forward traffic, when dropping we should
                # still see traffic being dropped.
                if up4.app_filters["action"] == "allow":
                    main.step("Test upstream traffic FAIL %s" % app_filter_name)
                    up4.testUpstreamTraffic(enb_names=enodebs_fail, app_filter_name=app_filter_name, shouldFail=True)
                    main.step("Test downstream traffic FAIL %s" % app_filter_name)
                    up4.testDownstreamTraffic(enb_names=enodebs_fail, app_filter_name=app_filter_name, shouldFail=True)
                else:
                    main.step("Test upstream traffic FAIL %s" % app_filter_name)
                    up4.testUpstreamTraffic(enb_names=enodebs_fail, app_filter_name=app_filter_name)
                    main.step("Test downstream traffic FAIL %s" % app_filter_name)
                    up4.testDownstreamTraffic(enb_names=enodebs_fail, app_filter_name=app_filter_name)

                main.step("Test upstream traffic NO FAIL %s" % app_filter_name)
                up4.testUpstreamTraffic(enb_names=enodebs_no_fail, app_filter_name=app_filter_name)
                main.step("Test downstream traffic NO FAIL %s" % app_filter_name)
                up4.testDownstreamTraffic(enb_names=enodebs_no_fail, app_filter_name=app_filter_name)

        except Exception as e:
            main.log.error("Unhandled exception!")
            main.log.error(e)
        finally:
            utilities.assert_equal(
                expect=main.TRUE,
                actual=kubectl.kubectlSetLabel(
                    nodeName=k8s_switch_node,
                    label=k8s_label,
                    value=k8s_label_value_normal,
                    kubeconfig=kubeconfig,
                    namespace=namespace,
                ),
                onpass="Label has been set correctly on node %s" % k8s_switch_node,
                onfail="Label has not been set on node %s" % k8s_switch_node
            )
            # Reconnect to the switch
            connect = utilities.retry(switch_component.connect,
                                      main.FALSE,
                                      attempts=30,
                                      getRetryingTime=True)
            main.log.info("Connected to the switch %s? %s" % (
                switch_to_kill, connect))

            # Wait for stratum pod to be re-deployed on the switch
            deployed = utilities.retry(checkNumberStratumPods,
                            False,
                            args=[n_switches],
                            attempts=50
                            )
            main.log.info("Stratum has been redeployed on the switch? %s" % deployed)

            # Wait switch to be back in ONOS
            available = utilities.retry(SRStagingTest.switchIsConnected,
                                        False,
                                        args=[switch_component],
                                        attempts=300,
                                        getRetryingTime=True)
            main.log.info("Switch %s is available in ONOS? %s" % (
                switch_to_kill, available))
            utilities.assert_equal(
                expect=True,
                actual=available and connect == main.TRUE and deployed,
                onpass="Switch is back available in ONOS and stratum has been redeployed",
                onfail="Switch is not available in ONOS, may influence subsequent tests!"
            )

        for app_filter_name in up4.app_filters:
            main.step("Test upstream traffic AFTER switch reboot %s" % app_filter_name)
            up4.testUpstreamTraffic(app_filter_name=app_filter_name)

        main.step("Cleanup UPF entities via UP4")
        up4.detachUes()
        up4.verifyNoUesFlow(onos_cli)
        up4.teardown()

        # Teardown
        run.cleanup(main)

