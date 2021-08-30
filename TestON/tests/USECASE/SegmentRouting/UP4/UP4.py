class UP4:

    def __init__(self):
        self.default = ''

    # TODO: add test case that checks entries are being inserted and deleted from ONOS correclty
    def CASE1(self, main):
        """
        Attach UE
        Generate traffic from UE to PDN
        Verify traffic received from PDN
        Generate traffic from PDN to UE
        Verify traffic received from UE
        Detach UE
        """
        UE_PORT = 400
        PDN_PORT = 800
        GPDU_PORT = 2152
        try:
            from tests.USECASE.SegmentRouting.dependencies.up4libcli import \
                Up4LibCli
            from tests.USECASE.SegmentRouting.dependencies.Testcaselib import \
                Testcaselib as run
            from distutils.util import strtobool
        except ImportError as e:
            main.log.error("Import not found. Exiting the test")
            main.log.error(e)
            main.cleanAndExit()

        # TODO: Move to a setup script
        run.initTest(main)
        main.log.info(main.Cluster.numCtrls)
        main.Cluster.setRunningNode(3)
        run.installOnos(main, skipPackage=True, cliSleep=5)

        # Get the P4RT client connected to UP4 in the first available ONOS instance
        up4Client = main.Cluster.active(0).p4rtUp4

        s1u_address = main.params["UP4"]["s1u_address"]
        enb_address = main.params["UP4"]["enb_address"]
        router_mac = main.params["UP4"]["router_mac"]

        pdn_host = getattr(main, main.params["UP4"]["pdn_host"])
        pdn_interface = pdn_host.interfaces[0]

        enodeb_host = getattr(main, main.params["UP4"]["enodeb_host"])
        enodeb_interface = enodeb_host.interfaces[0]

        emulated_ues = main.params["UP4"]['ues']
        n_ues = len(emulated_ues)

        main.step("Start scapy and p4rt client")
        pdn_host.startScapy(ifaceName=pdn_interface["name"])
        enodeb_host.startScapy(ifaceName=enodeb_interface["name"],
                               enableGtp=True)
        up4Client.startP4RtClient()

        # TODO: move to library in dependencies
        main.step("Attach UEs")
        for ue in emulated_ues.values():
            # Sanitize values coming from the params file
            if "five_g" in ue:
                ue["five_g"] = bool(strtobool(ue["five_g"]))
            if "qfi" in ue and ue["qfi"] == "":
                ue["qfi"] = None
            Up4LibCli.attachUe(up4Client, s1u_address=s1u_address,
                               enb_address=enb_address,
                               **ue)

        # ----------------- Test Upstream traffic (enb->pdn)
        main.step("Test upstream traffic")
        # Scapy filter needs to start before sending traffic
        pkt_filter_upstream = ""
        for ue in emulated_ues.values():
            if "ue_address" in ue:
                if len(pkt_filter_upstream) != 0:
                    pkt_filter_upstream += " or "
                pkt_filter_upstream += "src host " + ue["ue_address"]
        pkt_filter_upstream = "ip and udp dst port %s and (%s) and dst host %s" % \
                              (PDN_PORT, pkt_filter_upstream,
                               pdn_interface["ips"][0])
        main.log.info("Start listening on %s intf %s" %
                      (main.params["UP4"]["pdn_host"], pdn_interface["name"]))
        main.log.debug("BPF Filter Upstream: \n %s" % pkt_filter_upstream)
        pdn_host.startFilter(ifaceName=pdn_interface["name"],
                             sniffCount=n_ues,
                             pktFilter=pkt_filter_upstream)

        main.log.info("Sending %d packets from eNodeB host" % len(emulated_ues))
        for ue in emulated_ues.values():
            enodeb_host.buildEther()
            enodeb_host.buildIP(src=enb_address, dst=s1u_address)
            enodeb_host.buildUDP(ipVersion=4, dport=GPDU_PORT)
            # FIXME: With newer scapy TEID becomes teid (required for Scapy 2.4.5)
            enodeb_host.buildGTP(gtp_type=0xFF, TEID=int(ue["teid"]))
            enodeb_host.buildIP(overGtp=True, src=ue["ue_address"],
                                dst=pdn_interface["ips"][0])
            enodeb_host.buildUDP(ipVersion=4, overGtp=True, sport=UE_PORT,
                                 dport=PDN_PORT)

            enodeb_host.sendPacket(iface=enodeb_interface["name"])

        finished = pdn_host.checkFilter()
        packets = ""
        if finished:
            packets = pdn_host.readPackets(detailed=True)
            for p in packets.splitlines():
                main.log.debug(p)
            # We care only of the last line from readPackets
            packets = packets.splitlines()[-1]
        else:
            kill = pdn_host.killFilter()
            main.log.debug(kill)

        fail = False
        if len(emulated_ues) != packets.count('Ether'):
            fail = True
            msg = "Failed to capture packets in PDN. "
        else:
            msg = "Correctly captured packet in PDN. "
        # We expect exactly 1 packet per UE
        pktsFiltered = [packets.count("src=" + ue["ue_address"])
                        for ue in emulated_ues.values()]
        if pktsFiltered.count(1) != len(pktsFiltered):
            fail = True
            msg += "More than one packet per UE in downstream. "
        else:
            msg += "One packet per UE in upstream. "

        utilities.assert_equal(
            expect=False, actual=fail, onpass=msg, onfail=msg)

        # --------------- Test Downstream traffic (pdn->enb)
        main.step("Test downstream traffic")
        pkt_filter_downstream = "ip and udp src port %d and udp dst port %d and dst host %s and src host %s" % (
            GPDU_PORT, GPDU_PORT, enb_address, s1u_address)
        main.log.info("Start listening on %s intf %s" % (
            main.params["UP4"]["enodeb_host"], enodeb_interface["name"]))
        main.log.debug("BPF Filter Downstream: \n %s" % pkt_filter_downstream)
        enodeb_host.startFilter(ifaceName=enodeb_interface["name"],
                                sniffCount=len(emulated_ues),
                                pktFilter=pkt_filter_downstream)

        main.log.info("Sending %d packets from PDN host" % len(emulated_ues))
        for ue in emulated_ues.values():
            # From PDN we have to set dest MAC, otherwise scapy will do ARP
            # request for the UE IP address.
            pdn_host.buildEther(dst=router_mac)
            pdn_host.buildIP(src=pdn_interface["ips"][0],
                             dst=ue["ue_address"])
            pdn_host.buildUDP(ipVersion=4, sport=PDN_PORT, dport=UE_PORT)
            pdn_host.sendPacket(iface=pdn_interface["name"])

        finished = enodeb_host.checkFilter()
        packets = ""
        if finished:
            packets = enodeb_host.readPackets(detailed=True)
            for p in packets.splitlines():
                main.log.debug(p)
            # We care only of the last line from readPackets
            packets = packets.splitlines()[-1]
        else:
            kill = enodeb_host.killFilter()
            main.log.debug(kill)

        # The BPF filter might capture non-GTP packets because we can't filter
        # GTP header in BPF. For this reason, check that the captured packets
        # are from the expected tunnels.
        # TODO: check inner UDP and IP fields as well
        # FIXME: with newer scapy TEID becomes teid (required for Scapy 2.4.5)
        pktsFiltered = [packets.count("TEID=" + hex(int(ue["teid"])) + "L ")
                        for ue in emulated_ues.values()]

        fail = False
        if len(emulated_ues) != sum(pktsFiltered):
            fail = True
            msg = "Failed to capture packets in eNodeB. "
        else:
            msg = "Correctly captured packets in eNodeB. "
        # We expect exactly 1 packet per UE
        if pktsFiltered.count(1) != len(pktsFiltered):
            fail = True
            msg += "More than one packet per GTP TEID in downstream. "
        else:
            msg += "One packet per GTP TEID in downstream. "

        utilities.assert_equal(
            expect=False, actual=fail, onpass=msg, onfail=msg)

        # Detach UEs
        main.step("Detach UEs")
        for ue in emulated_ues.values():
            # No need to sanitize values, already sanitized during attachment
            Up4LibCli.detachUe(up4Client, s1u_address=s1u_address,
                               enb_address=enb_address,
                               **ue)

        # Teardown
        main.step("Stop scapy and p4rt client")
        enodeb_host.stopScapy()
        pdn_host.stopScapy()
        up4Client.stopP4RtClient()
        run.cleanup(main)
