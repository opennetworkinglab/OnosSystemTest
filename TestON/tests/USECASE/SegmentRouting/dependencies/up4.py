from distutils.util import strtobool
import ipaddress as ip
import copy
import re
import pexpect

FALSE = '0'
TRUE = '1'
DIR_UPLINK = '1'
DIR_DOWNLINK = '2'
IFACE_ACCESS = '1'
IFACE_CORE = '2'
TUNNEL_SPORT = '2152'
TUNNEL_TYPE_GPDU = '3'

UE_PORT = 400
DEFAULT_PDN_PORT = 800
GPDU_PORT = 2152

DEFAULT_APP_ID = 0
DEFAULT_APP_NAME = "Default"
DEFAULT_SESSION_METER_IDX = 0
DEFAULT_APP_METER_IDX = 0


class UP4:
    """
    Utility that manages interaction with UP4 via a P4RuntimeCliDriver available
    in the cluster. Additionally, can verify connectivity by crafting GTP packets
    via Scapy with an HostDriver component, specified via <enodebs>, <pdn_host>,
    and <router_mac> parameters.

    Example params file:
    <UP4>
        <pdn_host>Compute1</pdn_host> # Needed to verify connectivity with scapy
         <enodebs> # List of emulated eNodeBs
            <enode_1>
                <host>Compute1</host>  # Host that emulates this eNodeB
                <interface>eno3</interface> # Name of the linux interface to use on the host, if not specified take the default
                <enb_address>10.32.11.122</enb_address> # IP address of the eNodeB
                <ues>ue3</ues> # Emulated ues connected to this eNB
            </enode_1>
            <enodeb_2>
                <host>Compute3</host>
                <enb_address>10.32.11.194</enb_address>
                <ues>ue1,ue2</ues>
            </enodeb_2>
        </enodebs>
        <enodeb_host>Compute3</enodeb_host>
        <router_mac>00:00:0A:4C:1C:46</router_mac> # Needed to verify connectivity with scapy
        <s1u_address>10.32.11.126</s1u_address>
        <slice_id>1</slice_id> # Mobile SLICE ID, used when pushing application filtering entries
        <ues>
            <ue2>
                <ue_address>10.240.0.2</ue_address>
                <teid>200</teid>
                <up_id>20</up_id>
                <down_id>21</down_id>
                <!-- TC 0 means BEST EFFORT -->
                <tc>2</tc>
                <five_g>False</five_g>
                <max_bps>200000000</max_bps>
            </ue2>
        </ues>
        <switch_to_kill>Leaf2</switch_to_kill> # Component name of the switch to kill in CASE 5
        <enodebs_fail>enodeb_1</enodebs_fail> # List of eNodeBs that should fail traffic forwarding in CASE 5
    </UP4>
    """

    def __init__(self):
        self.s1u_address = None
        self.enodebs = None
        self.pdn_host = None
        self.pdn_interface = None
        self.router_mac = None
        self.emulated_ues = {}
        self.DEFAULT_APP = {DEFAULT_APP_NAME: {'ip_prefix': None, 'ip_proto': None, 'port_range': None,
                            'app_id': DEFAULT_APP_ID, 'action': 'allow' } }
        self.app_filters = self.DEFAULT_APP
        self.up4_client = None
        self.mock_smf = None
        self.no_host = False
        self.slice_id = None
        self.next_seid = 1

    def setup(self, p4rt_client, mock_smf=None, no_host=False, pfcpAddress=None, pfcpPort=8805, app_filters=True):
        """
        Set up P4RT and scapy on eNB and PDN hosts. If mock_smf is not None, will also connect
        to the pfcp agent using a mock smf and the test will use this to create ue sessions instead of P4RT
        :param p4rt_client: a P4RuntimeCliDriver component
        :param mock_smf: The optional mocksmfdriver component to use
        :param no_host: True if you don't want to start scapy on the hosts
        :param pfcpAddress: Address of the PFCP agent to connect to when using mock smf
        :param pfcpPort: Port of the PFCP agent to connect to when using mock smf
        :param app_filters: If True, will add app_filters defined in the params file, else use the default application filter
        :return:
        """
        self.s1u_address = main.params["UP4"]["s1u_address"]
        self.emulated_ues = main.params["UP4"]['ues']
        self.app_filters = main.params["UP4"]['app_filters'] if app_filters else self.DEFAULT_APP
        self.slice_id = main.params["UP4"]['slice_id']
        self.up4_client = p4rt_client
        self.mock_smf = mock_smf
        self.no_host = no_host

        # Optional Parameters

        self.enodebs = copy.deepcopy((main.params["UP4"]["enodebs"]))
        for enb in self.enodebs.values():
            enb["ues"] = enb["ues"].split(",")
            enb["host"] = getattr(main, enb["host"])
            # If interface not provided by the params, use the default in the host
            if "interface" not in enb.keys():
                enb["interface"] = enb["host"].interfaces[0]["name"]
        if "pdn_host" in main.params["UP4"]:
            self.pdn_host = getattr(main, main.params["UP4"]["pdn_host"])
            self.pdn_interface = self.pdn_host.interfaces[0]
        self.router_mac = main.params["UP4"].get("router_mac", None)

        for app_filter in self.app_filters.values():
            if app_filter.get('slice_id', None) is None:
                app_filter['slice_id'] = self.slice_id
        # Start components
        if self.up4_client:
            self.up4_client.startP4RtClient()
        if self.mock_smf:
            if not pfcpAddress:
                pfcpAddress = self.mock_smf.kubectlGetServiceIP( "pfcp-agent" )
            self.startMockSmfPcap(self.mock_smf)
            self.mock_smf.startSMF()
            self.mock_smf.configure(self.s1u_address, pfcpAddress, pfcpPort)
            # TODO Start pcap on mock_smf host
            self.mock_smf.associate()
        if not self.no_host:
            if self.enodebs is not None:
                for enb in self.enodebs.values():
                    enb["host"].startScapy(ifaceName=enb["interface"],
                                           enableGtp=True)
            if self.pdn_host is not None:
                self.pdn_host.startScapy(ifaceName=self.pdn_interface["name"])

    def startMockSmfPcap(self, smfComponent, pcapIface="eth0"):
        compName = "smf-pcap"
        # Create another component/bash session for tshark
        main.Network.copyComponent(smfComponent.name, compName)
        pcap = getattr(main, compName)
        pcapFile = "%s/CASE%s-%s" % (main.logdir, main.CurrentTestCaseNumber, compName)
        commands = ['touch %s.pcap' % pcapFile,
                    'chmod o=rw %s.pcap' % pcapFile]
        for command in commands:
            pcap.handle.sendline(command)
            pcap.handle.expect(pcap.prompt)
            main.log.debug("%s: %s" % (pcap.name, str(pcap.handle.before)))
        pcap.handle.sendline("sudo /usr/bin/tshark -i %s -w %s.pcap &> %s.log" % (pcapIface, pcapFile, pcapFile))
        i = pcap.handle.expect(["password", pexpect.TIMEOUT], timeout=5)
        if i == 0:
            pcap.handle.sendline(pcap.pwd if pcap.pwd else "jenkins")
        pcap.preDisconnect = pcap.exitFromProcess

    def teardown(self):
        if self.up4_client:
            self.up4_client.stopP4RtClient()
        if self.mock_smf:
            self.mock_smf.disassociate()
            self.mock_smf.stop()
        if not self.no_host:
            if self.enodebs is not None:
                for enb in self.enodebs.values():
                    enb["host"].stopScapy()
            if self.pdn_host is not None:
                self.pdn_host.stopScapy()

    def attachUes(self):
        filter_desc = []
        for app_name, app_filter in sorted(self.app_filters.items(), key=lambda (k, v): int(v.get('priority', 0))):
            if self.mock_smf:
                if app_name != DEFAULT_APP_NAME:
                    filter_desc.append(self.__pfcpSDFString(**app_filter))
                    self.app_filters[app_name]['app_id'] = None
                    self.app_filters[app_name]['priority'] = None

            else:
                self.insertAppFilter(**app_filter)
        for (ue_name, ue) in self.emulated_ues.items():
            ue = UP4.__sanitizeUeData(ue, smf=True if self.mock_smf else False)
            if self.mock_smf:
                if not ue.get("seid"):
                    ue["seid"] = self.next_seid
                    self.next_seid = self.next_seid + 1
                    self.emulated_ues[ue_name]["seid"] = ue["seid"]
                self.smfAttachUe(ue_name, sdf=filter_desc[-1:], **ue) # TODO: pass whole filter list once multi app support is fixed
            else:
                self.attachUe(ue_name, **ue)

    def detachUes(self):
        if not self.mock_smf:
            for app_filter in self.app_filters.values():
                self.removeAppFilter(**app_filter)
        for (ue_name, ue) in self.emulated_ues.items():
            ue = UP4.__sanitizeUeData(ue, smf=True if self.mock_smf else False)
            if self.mock_smf:
                self.smfDetachUe(ue_name, **ue)
            else:
                self.detachUe(ue_name, **ue)

    def __pickPortFromRange(self, range):
        if range is None or len(range) == 0:
            return DEFAULT_PDN_PORT
        # First port in range
        return int(range.split('..')[0])

    def testUpstreamTraffic(self, enb_names=None, app_filter_name=None, shouldFail=False):
        if self.enodebs is None or self.pdn_host is None:
            main.log.error(
                "Need eNodeB and PDN host params to generate scapy traffic")
            return
        if enb_names is None or enb_names == []:
            enodebs = self.enodebs.values()
        else:
            enodebs = [self.enodebs[enb] for enb in enb_names]

        port_range = None
        app_filter_should_drop = False
        if app_filter_name and app_filter_name != DEFAULT_APP_NAME:
            app_filter = self.app_filters[app_filter_name]
            port_range = app_filter.get("port_range", None)
            app_filter_should_drop = app_filter["action"] != "allow"
        pdn_port = self.__pickPortFromRange(port_range)

        pkt_filter_upstream = ""
        ues = []
        for enb in enodebs:
            for ue_name in enb["ues"]:
                ue = self.emulated_ues[ue_name]
                if "ue_address" in ue:
                    ues.append(ue)
                    if len(pkt_filter_upstream) != 0:
                        pkt_filter_upstream += " or "
                    pkt_filter_upstream += "src host " + ue["ue_address"]
        pkt_filter_upstream = "ip and udp dst port %s and (%s) and dst host %s" % \
                              (pdn_port, pkt_filter_upstream,
                               self.pdn_interface["ips"][0])
        main.log.info("Start listening on %s intf %s" %
                      (self.pdn_host.name, self.pdn_interface["name"]))
        main.log.debug("BPF Filter Upstream: \n %s" % pkt_filter_upstream)
        self.pdn_host.startFilter(ifaceName=self.pdn_interface["name"],
                                  sniffCount=len(ues),
                                  pktFilter=pkt_filter_upstream)

        main.log.info(
            "Sending %d packets from eNodeB host" % len(ues))
        for enb in enodebs:
            for ue_name in enb["ues"]:
                main.log.info(ue_name)
                ue = self.emulated_ues[ue_name]
                main.log.info(str(ue))
                UP4.buildGtpPacket(enb["host"],
                                   src_ip_outer=enb["enb_address"],
                                   dst_ip_outer=self.s1u_address,
                                   src_ip_inner=ue["ue_address"],
                                   dst_ip_inner=self.pdn_interface["ips"][0],
                                   src_udp_inner=UE_PORT,
                                   dst_udp_inner=pdn_port,
                                   teid=int(ue["teid"]))
                enb["host"].sendPacket(iface=enb["interface"])

        packets = UP4.checkFilterAndGetPackets(self.pdn_host)
        if app_filter_should_drop:
            expected_pkt_count = 0
        else:
            # We expect exactly 1 packet per UE.
            expected_pkt_count = len(ues)
        actual_pkt_count = packets.count('Ether')
        fail = False
        if expected_pkt_count != actual_pkt_count:
            fail = True
            msg = "Received %d packets (expected %d)\n%s\n" % (
                actual_pkt_count, expected_pkt_count, str(packets)
            )
        else:
            msg = "Received %d packets (expected %d)\n" % (
                actual_pkt_count, expected_pkt_count
            )

        if expected_pkt_count > 0:
            # Make sure the captured packets are from the expected UE addresses.
            for ue in ues:
                ue_pkt_count = packets.count("src=" + ue["ue_address"])
                if ue_pkt_count != 1:
                    fail = True
                msg += "Received %d packet(s) from UE %s (expected 1)\n" % (
                    ue_pkt_count, ue["ue_address"]
                )
        utilities.assert_equal(
            expect=shouldFail, actual=fail, onpass=msg, onfail=msg
        )

    def testDownstreamTraffic(self, enb_names=None, app_filter_name=None, shouldFail=False):
        if self.enodebs is None or self.pdn_host is None:
            main.log.error(
                "Need eNodeB and PDN host params to generate scapy traffic")
            return
        if enb_names is None or enb_names == []:
            enodebs = self.enodebs.values()
        else:
            enodebs = [self.enodebs[enb] for enb in enb_names]

        port_range = None
        app_filter_should_drop = False
        if app_filter_name and app_filter_name != DEFAULT_APP_NAME:
            app_filter = self.app_filters[app_filter_name]
            port_range = app_filter.get("port_range", None)
            app_filter_should_drop = app_filter["action"] != "allow"
        pdn_port = self.__pickPortFromRange(port_range)

        pkt_filter_downstream = "ip and udp src port %d and udp dst port %d and src host %s" % (
            GPDU_PORT, GPDU_PORT, self.s1u_address)
        ues = []
        for enb in enodebs:
            filter_down = pkt_filter_downstream + " and dst host %s" % enb[
                "enb_address"]
            main.log.info("Start listening on %s intf %s" % (
                enb["host"], enb["interface"]))
            main.log.debug("BPF Filter Downstream: \n %s" % filter_down)
            enb["host"].startFilter(ifaceName=enb["interface"],
                                    sniffCount=len(enb["ues"]),
                                    pktFilter=filter_down)
            ues.extend([self.emulated_ues[ue_name] for ue_name in enb["ues"]])

        main.log.info(
            "Sending %d packets from PDN host" % len(ues))
        for ue in ues:
            # From PDN we have to set dest MAC, otherwise scapy will do ARP
            # request for the UE IP address.
            UP4.buildUdpPacket(self.pdn_host,
                               dst_eth=self.router_mac,
                               src_ip=self.pdn_interface["ips"][0],
                               dst_ip=ue["ue_address"],
                               src_udp=pdn_port,
                               dst_udp=UE_PORT)
            self.pdn_host.sendPacket(iface=self.pdn_interface["name"])
        packets = ""
        for enb in enodebs:
            pkt = UP4.checkFilterAndGetPackets(enb["host"])
            packets += pkt
        # The BPF filter might capture non-GTP packets because we can't filter
        # GTP header in BPF. For this reason, check that the captured packets
        # are from the expected tunnels.
        # TODO: check inner IP fields as well
        # FIXME: with newer scapy TEID becomes teid (required for Scapy 2.4.5)
        downlink_teids = [int(ue["teid"]) + 1 for ue in ues]
        # Number of GTP packets from expected TEID per UEs
        gtp_pkts = [
            packets.count("TEID=" + hex(teid) + "L ") for teid in downlink_teids
        ]
        # Number of packets from the expected PDN port
        app_pkts = packets.count("UDP  sport=" + str(pdn_port))
        if app_filter_should_drop:
            expected_pkt_count = 0
        else:
            # We expect exactly 1 packet per UE.
            expected_pkt_count = len(ues)

        fail = False
        if expected_pkt_count != sum(gtp_pkts):
            fail = True
            msg = "Received %d packets (expected %d) from TEIDs %s\n%s\n" % (
                sum(gtp_pkts), expected_pkt_count, downlink_teids, str(packets)
            )
        else:
            msg = "Received %d packets (expected %d) from TEIDs %s\n" % (
                sum(gtp_pkts), expected_pkt_count, downlink_teids
            )
        if expected_pkt_count != app_pkts:
            fail = True
            msg += "Received %d packets (expected %d) from PDN port %s\n%s\n" % (
                sum(gtp_pkts), expected_pkt_count, pdn_port, str(packets)
            )
        else:
            msg += "Received %d packets (expected %d) from PDN port %s\n" % (
                sum(gtp_pkts), expected_pkt_count, pdn_port
            )
        if expected_pkt_count > 0:
            if gtp_pkts.count(1) != len(gtp_pkts):
                fail = True
                msg += "Received %s packet(s) per UE (expected %s)\n%s\n" % (
                    gtp_pkts, [1] * len(gtp_pkts), packets
                )
            else:
                msg += "Received %s packet(s) per UE (expected %s)\n" % (
                    gtp_pkts, [1] * len(gtp_pkts)
                )

        utilities.assert_equal(
            expect=shouldFail, actual=fail, onpass=msg, onfail=msg
        )

    def readUeSessionsNumber(self):
        """
        Read the UE session tables and return the number of entries

        :return: Number of entries in the UE session tables
        """
        tableName = 'PreQosPipe.sessions_uplink'
        nUeSess = self.up4_client.readNumberTableEntries(tableName)
        tableName = 'PreQosPipe.sessions_downlink'
        nUeSess += self.up4_client.readNumberTableEntries(tableName)
        return nUeSess

    def readTerminationsNumber(self):
        """
        Read the terminations and return the number of entities

        :return: Number of terminations entities
        """
        tableName = 'PreQosPipe.terminations_uplink'
        nTerm = self.up4_client.readNumberTableEntries(tableName)
        tableName = 'PreQosPipe.terminations_downlink'
        nTerm += self.up4_client.readNumberTableEntries(tableName)
        return nTerm

    def verifyUesFlowNumberP4rt(self):
        """
        Verify via P4RT CLI that the number of UE sessions and terminations
        is the expected one

        :return: True if the number of UE sessions and terminations is expected,
        False otherwise
        """
        return self.readUeSessionsNumber() == len(self.emulated_ues) * 2 and \
               self.readTerminationsNumber() == len(self.emulated_ues) * 2 * len(self.app_filters)

    def verifyNoUesFlowNumberP4rt(self, preInstalledUes=0):
        """
        Verify via P4RT CLI that there is no UE sessions and terminations installed.

        :param preInstalledUes: Number of UEs whose UE sessions and terminations
         are still programmed
        :return:
        """
        return self.readUeSessionsNumber() == preInstalledUes * 2 and \
               self.readTerminationsNumber() == preInstalledUes * 2 * len(self.app_filters)

    def verifyNoUesFlow(self, onosCli, retries=10):
        """
        Verify that no UE session, terminations are installed in ONOS.

        :param onosCli:  An instance of a OnosCliDriver
        :param retries: number of retries
        :return:
        """
        retValue = utilities.retry(f=UP4.__verifyNoUeSessionAndTerminationOnos,
                                   retValue=False,
                                   args=[onosCli],
                                   sleep=5,
                                   attempts=retries)
        utilities.assert_equal(expect=True,
                               actual=retValue,
                               onpass="No UE session and terminations in ONOS",
                               onfail="Stale UE session or terminations")

    @staticmethod
    def __verifyNoUeSessionAndTerminationOnos(onosCli):
        """
        Verify that no UE session, terminations are installed in ONOS

        :param onosCli: An instance of a OnosCliDriver
        """
        sessions = onosCli.sendline(cmdStr="up4:read-entities -s",
                                    showResponse=True,
                                    noExit=True, expectJson=False)
        terminations = onosCli.sendline(cmdStr="up4:read-entities -t",
                                        showResponse=True,
                                        noExit=True, expectJson=False)
        return sessions == "" and terminations == ""

    def verifyUp4Flow(self, onosCli, retries=10):
        """
        Verify UE session, terminations and GTP tunnel peers installed via UP4
        using the ONOS CLI.

        :param onosCli: An instance of a OnosCliDriver
        :param retries: Number of retries
        """
        failString = []
        retValue = utilities.retry(f=self.__internalVerifyUp4Flow,
                                   retValue=False,
                                   args=[onosCli, failString],
                                   sleep=5,
                                   attempts=retries)
        utilities.assert_equal(
            expect=True,
            actual=retValue,
            onpass="Correct UE session, terminations and GTP tunnel peers in ONOS",
            onfail="Wrong Application Filters, UE sessions, terminations and/or GTP tunnel peers in ONOS. " +
                   "Missing:\n" + '\n'.join(failString)
        )

    def __internalVerifyUp4Flow(self, onosCli, failMsg=[]):
        # Need to pass a list, so it's an object and we can use failMsg to
        # return a string values from this method.

        # Cleanup failMsg if any remaining from previous runs
        del failMsg[:]
        applications = onosCli.sendline(cmdStr="up4:read-entities -f",
                                        showResponse=True,
                                        noExit=True, expectJson=False)
        sessions = onosCli.sendline(cmdStr="up4:read-entities -s",
                                    showResponse=True,
                                    noExit=True, expectJson=False)
        terminations = onosCli.sendline(cmdStr="up4:read-entities -t",
                                        showResponse=True,
                                        noExit=True, expectJson=False)
        tunn_peer = onosCli.sendline(cmdStr="up4:read-entities -g",
                                     showResponse=True,
                                     noExit=True, expectJson=False)
        fail = False
        for app_filter in self.app_filters.values():
            if not UP4.__defaultApp(**app_filter):
                if len(re.findall(self.appFilterOnosString(**app_filter), applications)) != 1:
                    failMsg.append(self.appFilterOnosString(**app_filter))
                    fail = True
        for (ue_name, ue) in self.emulated_ues.items():
            if len(re.findall(self.upUeSessionOnosString(**ue), sessions)) != 1:
                failMsg.append(self.upUeSessionOnosString(**ue))
                fail = True
            if len(re.findall(self.downUeSessionOnosString(**ue), sessions)) != 1:
                failMsg.append(self.downUeSessionOnosString(**ue))
                fail = True
            for app_filter in self.app_filters.values():
                if len(re.findall(self.upTerminationOnosString(app_filter=app_filter, **ue), terminations)) != 1:
                    failMsg.append(self.upTerminationOnosString(app_filter=app_filter, **ue))
                    fail = True
                if len(re.findall(self.downTerminationOnosString(app_filter=app_filter, **ue), terminations)) != 1:
                    failMsg.append(self.downTerminationOnosString(app_filter=app_filter, **ue))
                    fail = True
            if len(re.findall(self.gtpTunnelPeerOnosString(ue_name, **ue), tunn_peer)) != 1:
                failMsg.append(self.gtpTunnelPeerOnosString(ue_name, **ue))
                fail = True
        return not fail

    def appFilterOnosString(self, app_id=None, priority=None, slice_id=None, ip_proto=None, ip_prefix=None, port_range=None, **kwargs):
        if app_id is None:
            app_id = "\d+"
        if priority is None:
            priority = "\d+"
        if slice_id is None:
            slice_id = self.slice_id
        matches = []
        if ip_prefix:
            matches.append("ip_prefix=%s" % ip_prefix)
        if port_range:
            matches.append("l4_port_range=\[%s\]" % port_range)
        if ip_proto:
            matches.append("ip_proto=%s" % ip_proto)
        matches.append("slice_id=%s" % slice_id)

        return "UpfApplication\(priority=%s, Match\(%s\) -> Action\(app_id=%s\)\)" % (
            priority,
            ", ".join(matches),
            app_id
        )

    def upUeSessionOnosString(self, teid=None, teid_up=None, up_id=None,
                              sess_meter_idx=None, max_bps=None, **kwargs):
        if teid_up is None and teid is not None:
            teid_up = teid
        if up_id is not None:
            if max_bps is not None:
                sess_meter_idx = up_id
            else:
                sess_meter_idx = DEFAULT_SESSION_METER_IDX
        if sess_meter_idx is None:
            sess_meter_idx = "\d+"
        return "UpfSessionUL\(Match\(tun_dst_addr={}, teid={}\) -> Action\(FWD, session_meter_idx={}\)\)".format(
            self.s1u_address, teid_up, sess_meter_idx)

    def downUeSessionOnosString(self, ue_address, down_id=None,
                                tunn_peer_id=None, sess_meter_idx=None, max_bps=None,
                                **kwargs):
        if down_id is not None:
            tunn_peer_id = down_id
            if max_bps is not None:
                sess_meter_idx = down_id
            else:
                sess_meter_idx = DEFAULT_SESSION_METER_IDX
        if tunn_peer_id is None:
            tunn_peer_id = "\d+"
        if sess_meter_idx is None:
            sess_meter_idx = "\d+"
        return "UpfSessionDL\(Match\(ue_addr={}\) -> Action\(FWD,  tun_peer={}, session_meter_idx={}\)\)".format(
            ue_address, tunn_peer_id, sess_meter_idx)

    def upTerminationOnosString(self, ue_address, app_filter, up_id=None,
                                ctr_id_up=None, tc=None, app_meter_idx=None, **kwargs):
        if up_id is not None:
            ctr_id_up = up_id
            if "max_bps" in app_filter:
                app_meter_idx = int(up_id) + int(app_filter["app_id"])
            else:
                app_meter_idx = DEFAULT_APP_METER_IDX
        if ctr_id_up is None:
            ctr_id_up = "\d+"
        if tc is None or int(tc) == 0:
            tc = "(?:0|null)"
        if app_meter_idx is None:
            app_meter_idx = "\d+"
        app_id = app_filter["app_id"]
        if app_id is None:
            app_id = "\d+"
        if app_filter["action"] == "deny":
            return "UpfTerminationUL\(Match\(ue_addr={}, app_id={}\) -> Action\(DROP, ctr_id={}, tc=null, app_meter_idx=0\)\)".format(
                ue_address, app_id, ctr_id_up)
        else:
            return "UpfTerminationUL\(Match\(ue_addr={}, app_id={}\) -> Action\(FWD, ctr_id={}, tc={}, app_meter_idx={}\)\)".format(
                ue_address, app_id, ctr_id_up, tc, app_meter_idx)

    def downTerminationOnosString(self, ue_address, app_filter, teid=None,
                                  down_id=None, ctr_id_down=None, teid_down=None,
                                  tc=None, app_meter_idx=None,
                                  **kwargs):
        if down_id is not None:
            ctr_id_down = down_id
        if ctr_id_down is None:
            ctr_id_down = "\d+"
        if teid_down is None and teid is not None:
            teid_down = int(teid) + 1
            if "max_bps" in app_filter:
                app_meter_idx = int(down_id) + int(app_filter["app_id"])
            else:
                app_meter_idx = DEFAULT_APP_METER_IDX
        if tc is None or int(tc) == 0:
            tc = "(?:0|null)"
        if app_meter_idx is None:
            app_meter_idx = "\d+"
        app_id = app_filter["app_id"]
        if app_id is None:
            app_id = "\d+"
        if app_filter["action"] == "deny":
            return "UpfTerminationDL\(Match\(ue_addr={}, app_id={}\) -> Action\(DROP, teid=null, ctr_id={}, qfi=null, tc=null, app_meter_idx=0\)\)".format(
                ue_address, app_id, ctr_id_down)
        else:
            return "UpfTerminationDL\(Match\(ue_addr={}, app_id={}\) -> Action\(FWD, teid={}, ctr_id={}, qfi={}, tc={}, app_meter_idx={}\)\)".format(
                ue_address, app_id, teid_down, ctr_id_down, tc, tc, app_meter_idx)

    def gtpTunnelPeerOnosString(self, ue_name, down_id=None, tunn_peer_id=None,
                                **kwargs):
        if down_id is not None:
            tunn_peer_id = down_id
        if tunn_peer_id is None:
            tunn_peer_id = "\d+"
        enb_address = self.__getEnbAddress(ue_name)
        return "UpfGtpTunnelPeer\(tunn_peer_id={} -> src={}, dst={} src_port={}\)".format(
            tunn_peer_id, self.s1u_address, enb_address, GPDU_PORT)

    @staticmethod
    def __sanitizeUeData(ue, smf=False):
        if "five_g" in ue and type(ue["five_g"]) != bool:
            ue["five_g"] = bool(strtobool(ue["five_g"]))
        if "tc" in ue and ue["tc"] == "":
            ue["tc"] = 0
        if "max_bps" in ue:
            if ue["max_bps"] == "" or ue["max_bps"] is None:
                ue["max_bps"] = None
            else:
                ue["max_bps"] = int(ue["max_bps"])
        if smf:
            ue["up_id"] = None
            ue["down_id"] = None
        return ue

    def insertAppFilter(self, **kwargs):
        if not UP4.__defaultApp(**kwargs):
            self.__programAppFilter(op="program", **kwargs)

    def removeAppFilter(self, **kwargs):
        if not UP4.__defaultApp(**kwargs):
            self.__programAppFilter(op="clear", **kwargs)

    def smfAttachUe(self, ue_name, ue_address, prefix_len=31, seid=1, teid=None, sdf=[], **kwargs):
        enb_addr = None
        for enb_name, enb in self.enodebs.items():
            if ue_name in enb["ues"]:
                enb_addr = enb["enb_address"]
                break
        assert enb_addr, "Unknown eNodeB address"
        ue_address = str(ip.ip_address(unicode(ue_address)) - 1)
        base = seid

        create = self.mock_smf.create(ue_pool="%s/%s" % (ue_address, prefix_len),
                                      gnb_addr=enb_addr,
                                      base_id=base,
                                      sdf=sdf)
        modify = self.mock_smf.modify(ue_pool="%s/%s" % (ue_address, prefix_len),
                                      gnb_addr=enb_addr,
                                      base_id=seid)
        self.emulated_ues[ue_name]['seid'] = base
        self.emulated_ues[ue_name]['teid'] = base
        self.emulated_ues[ue_name]['sess_meter_idx'] = None
        self.emulated_ues[ue_name]['app_meter_idx'] = None
        return create and modify

    def smfDetachUe(self, ue_name, ue_address, prefix_len=31, seid=1, teid=None, **kwargs):
        enb_addr = None
        for enb_name, enb in self.enodebs.items():
            if ue_name in enb["ues"]:
                enb_addr = enb["enb_address"]
                break
        assert enb_addr, "Unknown eNodeB address"
        ue_address = str( ip.ip_address( unicode( ue_address ) ) - 1 )

        return self.mock_smf.delete( base_id=seid )

    def attachUe(self, ue_name, ue_address,
                 teid=None, up_id=None, down_id=None,
                 teid_up=None, teid_down=None,
                 ctr_id_up=None, ctr_id_down=None,
                 tunn_peer_id=None,
                 tc=None, five_g=False, max_bps=None,
                 sess_meter_idx_up=None, sess_meter_idx_down=None, **kwargs):
        self.__programUeRules(ue_name,
                              ue_address,
                              teid, up_id, down_id,
                              teid_up, teid_down,
                              ctr_id_up, ctr_id_down,
                              tunn_peer_id,
                              tc, five_g, max_bps,
                              sess_meter_idx_up, sess_meter_idx_down,
                              op="program")

    def detachUe(self, ue_name, ue_address,
                 teid=None, up_id=None, down_id=None,
                 teid_up=None, teid_down=None,
                 ctr_id_up=None, ctr_id_down=None,
                 tunn_peer_id=None,
                 tc=None, five_g=False, max_bps=None,
                 sess_meter_idx_up=None, sess_meter_idx_down=None, **kwargs):
        self.__programUeRules(ue_name,
                              ue_address,
                              teid, up_id, down_id,
                              teid_up, teid_down,
                              ctr_id_up, ctr_id_down,
                              tunn_peer_id,
                              tc, five_g, max_bps,
                              sess_meter_idx_up, sess_meter_idx_down,
                              op="clear")

    def __programAppFilter(self, app_id, slice_id, ip_prefix=None, ip_proto=None,
                           port_range=None, priority=0, op="program", **kwargs):

        entries = []

        tableName = 'PreQosPipe.applications'
        actionName = 'PreQosPipe.set_app_id'
        actionParams = {'app_id': str(app_id)}
        matchFields = {
            'slice_id': str(slice_id)
        }
        if ip_prefix:
            matchFields['app_ip_addr'] = str(ip_prefix)
        if ip_proto:
            matchFields['app_ip_proto'] = str(ip_proto)
        if port_range:
            matchFields['app_l4_port'] = str(port_range)

        if not self.__add_entry(tableName, actionName, matchFields,
                                actionParams, entries, op, priority):
            return False

        if op == "program":
            main.log.info("Application entry added successfully.")
        elif op == "clear":
            self.__clear_entries(entries)

    def __pfcpSDFString(self, ip_prefix=None, ip_proto=None, port_range=None,
                        action="allow", **kwargs):
        if ip_proto is None or str(ip_proto) == "255":
            protoString = "ip"
        elif str(ip_proto) == "6":
            descList.append("tcp")
        elif str(ip_proto) == "17":
            protoString = "udp"
        else:
            #  TODO: is there a python library for this? Can we just pass the number?
            raise NotImplemented
        if port_range is None:
            port_range = "any"
        if ip_prefix is None:
            ip_prefix = "any"
        return "--app-filter '%s:%s:%s:%s'" % ( protoString,
                                                ip_prefix,
                                                port_range.replace("..","-"),
                                                action )

    def __programUeRules(self, ue_name, ue_address,
                         teid=None, up_id=None, down_id=None,
                         teid_up=None, teid_down=None, ctr_id_up=None,
                         ctr_id_down=None, tunn_peer_id=None,
                         tc=0, five_g=False, max_bps=None,
                         sess_meter_idx_up=None, sess_meter_idx_down=None,
                         op="program"):
        if max_bps is None:
            sess_meter_idx_up = DEFAULT_SESSION_METER_IDX
            sess_meter_idx_down = DEFAULT_SESSION_METER_IDX
        if up_id is not None:
            ctr_id_up = up_id
            if max_bps is not None:
                sess_meter_idx_up = int(up_id)
        if down_id is not None:
            tunn_peer_id = down_id
            ctr_id_down = down_id
            if max_bps is not None:
                sess_meter_idx_down = int(down_id)
        if teid is not None:
            teid_up = teid
            teid_down = int(teid) + 1

        entries = []

        # Retrieve eNobeB address from eNodeB list
        enb_address = self.__getEnbAddress(ue_name)

        # ========================#
        # Session Meters
        # ========================#
        if max_bps is not None:
            if not self.__mod_meter(
                    'PreQosPipe.session_meter',
                    sess_meter_idx_up,
                    max_bps,
                    op
            ):
                return False
            if not self.__mod_meter(
                    'PreQosPipe.session_meter',
                    sess_meter_idx_down,
                    max_bps,
                    op
            ):
                return False

        # ========================#
        # UE Session Entries
        # ========================#

        # Uplink
        tableName = 'PreQosPipe.sessions_uplink'
        actionName = 'PreQosPipe.set_session_uplink'
        matchFields = {}
        actionParams = {}
        # Match fields
        matchFields['n3_address'] = str(self.s1u_address)
        matchFields['teid'] = str(teid_up)
        # Action params
        actionParams["session_meter_idx"] = str(sess_meter_idx_up)
        if five_g:
            # TODO: currently QFI match is unsupported in TNA
            main.log.warn("Matching on QFI is currently unsupported in TNA")
        if not self.__add_entry(tableName, actionName, matchFields,
                                actionParams, entries, op):
            return False

        # Downlink
        tableName = 'PreQosPipe.sessions_downlink'
        actionName = 'PreQosPipe.set_session_downlink'
        matchFields = {}
        actionParams = {}
        # Match fields
        matchFields['ue_address'] = str(ue_address)
        # Action params
        actionParams['tunnel_peer_id'] = str(tunn_peer_id)
        actionParams["session_meter_idx"] = str(sess_meter_idx_down)
        if not self.__add_entry(tableName, actionName, matchFields,
                                actionParams, entries, op):
            return False

        # ========================#
        # Terminations Entries
        # ========================#

        # Insert one termination entry per app filtering rule,

        # Uplink
        for f in self.app_filters.values():
            if "max_bps" in f:
                app_meter_idx_up = sess_meter_idx_up + int(f['app_id'])
                if not self.__mod_meter(
                        'PreQosPipe.app_meter',
                        app_meter_idx_up,
                        int(f["max_bps"]),
                        op
                ):
                    return False
            else:
                app_meter_idx_up = DEFAULT_APP_METER_IDX
            tableName = 'PreQosPipe.terminations_uplink'
            matchFields = {}
            actionParams = {}

            # Match fields
            matchFields['ue_address'] = str(ue_address)
            matchFields['app_id'] = str(f["app_id"])

            # Action params
            if f['action'] == 'allow':
                actionName = 'PreQosPipe.uplink_term_fwd'
                actionParams['app_meter_idx'] = str(app_meter_idx_up)
                actionParams['tc'] = str(tc)
            else:
                actionName = 'PreQosPipe.uplink_term_drop'
            actionParams['ctr_idx'] = str(ctr_id_up)
            if not self.__add_entry(
                    tableName, actionName, matchFields, actionParams, entries, op
            ):
                return False

        # Downlink
        for f in self.app_filters.values():
            if "max_bps" in f:
                app_meter_idx_down = sess_meter_idx_down + int(f['app_id'])
                if not self.__mod_meter(
                        'PreQosPipe.app_meter',
                        app_meter_idx_down,
                        int(f["max_bps"]),
                        op
                ):
                    return False
            else:
                app_meter_idx_down = DEFAULT_APP_METER_IDX
            tableName = 'PreQosPipe.terminations_downlink'
            matchFields = {}
            actionParams = {}

            # Match fields
            matchFields['ue_address'] = str(ue_address)
            matchFields['app_id'] = str(f["app_id"])

            # Action params
            if f['action'] == 'allow':
                actionName = 'PreQosPipe.downlink_term_fwd'
                actionParams['teid'] = str(teid_down)
                # 1-1 mapping between QFI and TC
                actionParams['tc'] = str(tc)
                actionParams['qfi'] = str(tc)
                actionParams['app_meter_idx'] = str(app_meter_idx_down)
            else:
                actionName = 'PreQosPipe.downlink_term_drop'
            actionParams['ctr_idx'] = str(ctr_id_down)

            if not self.__add_entry(tableName, actionName, matchFields,
                                    actionParams, entries, op):
                return False

        # ========================#
        # Tunnel Peer Entry
        # ========================#
        tableName = 'PreQosPipe.tunnel_peers'
        actionName = 'PreQosPipe.load_tunnel_param'
        matchFields = {}
        actionParams = {}
        # Match fields
        matchFields['tunnel_peer_id'] = str(tunn_peer_id)
        # Action params
        actionParams['src_addr'] = str(self.s1u_address)
        actionParams['dst_addr'] = str(enb_address)
        actionParams['sport'] = TUNNEL_SPORT
        if not self.__add_entry(tableName, actionName, matchFields,
                                actionParams, entries, op):
            return False
        if op == "program":
            main.log.info("All entries added successfully.")
        elif op == "clear":
            self.__clear_entries(entries)

    def __add_entry(self, tableName, actionName, matchFields, actionParams,
                    entries, op, priority=0):
        if op == "program":
            self.up4_client.buildP4RtTableEntry(
                tableName=tableName, actionName=actionName,
                actionParams=actionParams, matchFields=matchFields, priority=priority)
            if self.up4_client.pushTableEntry(debug=True) == main.TRUE:
                main.log.info("*** Entry added.")
            else:
                main.log.error("Error during table insertion")
                self.__clear_entries(entries)
                return False
        entries.append({
            "tableName": tableName, "actionName": actionName,
            "matchFields": matchFields,
            "actionParams": actionParams,
            "priority": priority
        })
        return True

    def __mod_meter(self, name, index, max_bps, op):
        cir = 0
        cburst = 0
        pir = max_bps // 8
        # TRex/DPDK can generate burst of 32 packets, considering MTU=1500, 32x1500B=48KB
        # Burst must be greater than 48KB
        pburst = 100000
        if op == "program":
            self.up4_client.buildP4RtMeterEntry(
                meterName=name, index=index, cir=cir, cburst=cburst, pir=pir,
                pburst=pburst
            )
        else:
            # in case of "clear" don't specify bands to clear meters
            self.up4_client.buildP4RtMeterEntry(meterName=name, index=index)
        if self.up4_client.modifyMeterEntry(debug=True) == main.TRUE:
            main.log.info("*** Meter modified.")
        else:
            main.log.error("Error during meter modification")
            return False
        return True

    def __clear_entries(self, entries):
        for i, entry in enumerate(entries):
            self.up4_client.buildP4RtTableEntry(**entry)
            if self.up4_client.deleteTableEntry(debug=True) == main.TRUE:
                main.log.info(
                    "*** Entry %d of %d deleted." % (i + 1, len(entries)))
            else:
                main.log.error("Error during table delete")

    def __getEnbAddress(self, ue_name):
        for enb in self.enodebs.values():
            if ue_name in enb["ues"]:
                return enb["enb_address"]
        main.log.error("Missing eNodeB address!")
        return ""

    @staticmethod
    def buildGtpPacket(host, src_ip_outer, dst_ip_outer, src_ip_inner,
                       dst_ip_inner, src_udp_inner, dst_udp_inner, teid):
        host.buildEther()
        host.buildIP(src=src_ip_outer, dst=dst_ip_outer)
        host.buildUDP(ipVersion=4, dport=GPDU_PORT)
        # FIXME: With newer scapy TEID becomes teid (required for Scapy 2.4.5)
        host.buildGTP(gtp_type=0xFF, TEID=teid)
        host.buildIP(overGtp=True, src=src_ip_inner, dst=dst_ip_inner)
        host.buildUDP(ipVersion=4, overGtp=True, sport=src_udp_inner,
                      dport=dst_udp_inner)

    @staticmethod
    def buildUdpPacket(host, src_ip, dst_ip, src_udp, dst_udp, src_eth=None,
                       dst_eth=None):
        host.buildEther(src=src_eth, dst=dst_eth)
        host.buildIP(src=src_ip, dst=dst_ip)
        host.buildUDP(ipVersion=4, sport=src_udp, dport=dst_udp)

    @staticmethod
    def checkFilterAndGetPackets(host):
        finished = host.checkFilter()
        if finished:
            packets = host.readPackets(detailed=True)
            for p in packets.splitlines():
                main.log.debug(p)
            # We care only of the last line from readPackets
            return packets.splitlines()[-1]
        else:
            kill = host.killFilter()
            main.log.debug(kill)
        return ""

    @staticmethod
    def __defaultApp(ip_prefix=None, ip_proto=None, port_range=None, **kwargs):
        if ip_prefix is None and ip_proto is None and port_range is None:
            return True
        return False

