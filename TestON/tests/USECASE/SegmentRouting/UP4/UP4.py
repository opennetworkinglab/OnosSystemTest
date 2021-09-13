class UP4:

    def __init__(self):
        self.default = ''

    # TODO: add test case that checks entries are being inserted and deleted from ONOS correclty
    def CASE1(self, main):
        main.case("Fabric UPF traffic terminated in the fabric")
        """
        Program PDRs and FARs for UEs
        Verify PDRs and FARs
        Generate traffic from UE to PDN
        Verify traffic received from PDN
        Generate traffic from PDN to UE
        Verify traffic received from UE
        Remove PDRs and FARs for UEs
        Verify removed PDRs and FARs
        """
        try:
            from tests.USECASE.SegmentRouting.dependencies.up4 import UP4
            from tests.USECASE.SegmentRouting.dependencies.Testcaselib import \
                Testcaselib as run
        except ImportError as e:
            main.log.error("Import not found. Exiting the test")
            main.log.error(e)
            main.cleanAndExit()

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

        main.step("Program PDRs and FARs via UP4")
        up4.attachUes()

        main.step("Verify PDRs and FARs in ONOS")
        up4.verifyUp4Flow(onos_cli)

        # ------- Test Upstream traffic (enb->pdn)
        main.step("Test upstream traffic")
        up4.testUpstreamTraffic()

        # ------- Test Downstream traffic (pdn->enb)
        main.step("Test downstream traffic")
        up4.testDownstreamTraffic()

        main.step("Remove PDRs and FARs via UP4")
        up4.detachUes()

        main.step("Verify removed PDRs and FARs from ONOS")
        up4.verifyNoUesFlow(onos_cli)

        main.step("Stop scapy and p4rt client")
        up4.teardown()
        run.cleanup(main)

    def CASE2(self):
        main.case("BESS traffic routed")
        """
        Program PDRs and FARs for UEs managed via UP4
        Verify PDRs and FARs
        Verify Upstream Traffic: eNB -> Fabric -> BESS (encapped)
        Verify Upstream Traffic: BESS -> Fabric -> PDN (not encapped)
        Verify Downstream Traffic: PDN -> Fabric -> BESS (not encapped)
        Verify Downstream Traffic: BESS -> Fabric -> eNB (encapped)
        Remove PDRs and FARs for UEs managed via UP4
        Verify removed PDRs and FARs
        """
        BESS_TEID = 300
        BESS_UE_ADDR = "10.241.0.1"
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
        bess_host = main.Compute2  # FIXME: Parametrize?
        bess_interface = bess_host.interfaces[0]
        bess_s1u_address = bess_interface["ips"][0]
        bess_host.startScapy(ifaceName=bess_interface["name"], enableGtp=True)
        enodeb_host = up4.enodeb_host
        enodeb_interface = up4.enodeb_interface
        pdn_host = up4.pdn_host
        pdn_interface = up4.pdn_interface

        main.step("Program PDRs and FARs for UEs via UP4")
        up4.attachUes()

        main.step("Verify PDRs and FARs in ONOS")
        up4.verifyUp4Flow(onos_cli)

        # ------------------- UPSTREAM -------------------
        # ------- eNB -> fabric -> BESS (encapped)
        main.step("Test upstream eNB -> fabric -> BESS")
        # Start filter before sending packets, BESS should receive GTP encapped
        # packets
        pkt_filter_upstream = "ip and udp src port %d and udp dst port %d and src host %s and dst host %s" % (
            GPDU_PORT, GPDU_PORT, up4.enb_address, bess_s1u_address)
        main.log.info("Start listening on %s intf %s" % (
            bess_host.name, bess_interface["name"]))
        main.log.debug("BPF Filter BESS Upstream: \n %s" % pkt_filter_upstream)
        bess_host.startFilter(ifaceName=bess_interface["name"],
                              sniffCount=1,
                              pktFilter=pkt_filter_upstream)
        # Send GTP Packet
        UP4.buildGtpPacket(enodeb_host,
                           src_ip_outer=up4.enb_address,
                           dst_ip_outer=bess_s1u_address,
                           src_ip_inner=BESS_UE_ADDR,
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
            UE_PORT, PDN_PORT, BESS_UE_ADDR, pdn_interface["ips"][0])
        main.log.info("Start listening on %s intf %s" % (
            pdn_host.name, pdn_interface["name"]))
        main.log.debug("BPF Filter PDN Upstream: \n %s" % pkt_filter_upstream)
        pdn_host.startFilter(ifaceName=pdn_interface["name"],
                             sniffCount=1,
                             pktFilter=pkt_filter_upstream)
        # Send UDP Packet
        UP4.buildUdpPacket(bess_host,
                           src_ip=BESS_UE_ADDR,
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
            PDN_PORT, UE_PORT, pdn_interface["ips"][0], BESS_UE_ADDR)
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
                           dst_ip=BESS_UE_ADDR,
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
            GPDU_PORT, GPDU_PORT, bess_s1u_address, up4.enb_address)
        main.log.info("Start listening on %s intf %s" % (
            enodeb_host.name, enodeb_interface["name"]))
        main.log.debug(
            "BPF Filter BESS Downstream: \n %s" % pkt_filter_downstream)
        enodeb_host.startFilter(ifaceName=enodeb_interface["name"],
                                sniffCount=1,
                                pktFilter=pkt_filter_downstream)
        # Build GTP packet from BESS host
        UP4.buildGtpPacket(bess_host,
                           src_ip_outer=bess_s1u_address,
                           dst_ip_outer=up4.enb_address,
                           src_ip_inner=pdn_interface["ips"][0],
                           dst_ip_inner=BESS_UE_ADDR,
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

        main.step("Remove PDRs and FARs for UEs via UP4")
        up4.detachUes()

        main.step("Verify removed PDRs and FARs from ONOS")
        up4.verifyNoUesFlow(onos_cli)

        main.step("Stop scapy and p4rt client")
        up4.teardown()
        bess_host.stopScapy()
        run.cleanup(main)
