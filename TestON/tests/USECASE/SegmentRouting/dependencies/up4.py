from distutils.util import strtobool

FALSE = '0'
TRUE = '1'
DIR_UPLINK = '1'
DIR_DOWNLINK = '2'
IFACE_ACCESS = '1'
IFACE_CORE = '2'
TUNNEL_SPORT = '2152'
TUNNEL_TYPE_GPDU = '3'

UE_PORT = 400
PDN_PORT = 800
GPDU_PORT = 2152


class UP4:
    """
    Utility that manages interaction with UP4 via a P4RuntimeCliDriver available
    in the cluster. Additionally, can verify connectivity by crafting GTP packets
    via Scapy with an HostDriver component, specified via <enodeb_host>, <pdn_host>,
    and <router_mac> parameters.

    Example params file:
    <UP4>
        <pdn_host>Compute1</pdn_host> # Needed to verify connectivity with scapy
        <enodeb_host>Compute3</enodeb_host> # Needed to verify connectivity with scapy
        <router_mac>00:00:0A:4C:1C:46</router_mac> # Needed to verify connectivity with scapy
        <s1u_address>10.32.11.126</s1u_address>
        <enb_address>10.32.11.100</enb_address>
        <ues>
            <ue2>
                <pfcp_session_id>100</pfcp_session_id>
                <ue_address>10.240.0.2</ue_address>
                <teid>200</teid>
                <up_id>20</up_id>
                <down_id>21</down_id>
                <qfi>2</qfi>
                <five_g>False</five_g>
            </ue2>
        </ues>
    </UP4>
    """

    def __init__(self):
        self.s1u_address = None
        self.enb_address = None
        self.enodeb_host = None
        self.enodeb_interface = None
        self.pdn_host = None
        self.pdn_interface = None
        self.router_mac = None
        self.emulated_ues = []
        self.up4_client = None

    def setup(self, p4rt_client):
        self.s1u_address = main.params["UP4"]["s1u_address"]
        self.enb_address = main.params["UP4"]["enb_address"]
        self.emulated_ues = main.params["UP4"]['ues']
        self.up4_client = p4rt_client

        # Optional Parameters
        if "enodeb_host" in main.params["UP4"]:
            self.enodeb_host = getattr(main, main.params["UP4"]["enodeb_host"])
            self.enodeb_interface = self.enodeb_host.interfaces[0]
        if "pdn_host" in main.params["UP4"]:
            self.pdn_host = getattr(main, main.params["UP4"]["pdn_host"])
            self.pdn_interface = self.pdn_host.interfaces[0]
        self.router_mac = main.params["UP4"].get("router_mac", None)

        # Start components
        self.up4_client.startP4RtClient()
        if self.enodeb_host is not None:
            self.enodeb_host.startScapy(ifaceName=self.enodeb_interface["name"],
                                        enableGtp=True)
        if self.pdn_host is not None:
            self.pdn_host.startScapy(ifaceName=self.pdn_interface["name"])

    def teardown(self):
        self.up4_client.stopP4RtClient()
        if self.enodeb_host is not None:
            self.enodeb_host.stopScapy()
        if self.pdn_host is not None:
            self.pdn_host.stopScapy()

    def attachUes(self):
        for ue in self.emulated_ues.values():
            # Sanitize values coming from the params file
            ue = UP4.__sanitizeUeData(ue)
            self.attachUe(**ue)

    def detachUes(self):
        for ue in self.emulated_ues.values():
            # No need to sanitize, has already been done in attach
            self.detachUe(**ue)

    def testUpstreamTraffic(self):
        if self.enodeb_host is None or self.pdn_host is None:
            main.log.error(
                "Need eNodeB and PDN host params to generate scapy traffic")
            return
        # Scapy filter needs to start before sending traffic
        pkt_filter_upstream = ""
        for ue in self.emulated_ues.values():
            if "ue_address" in ue:
                if len(pkt_filter_upstream) != 0:
                    pkt_filter_upstream += " or "
                pkt_filter_upstream += "src host " + ue["ue_address"]
        pkt_filter_upstream = "ip and udp dst port %s and (%s) and dst host %s" % \
                              (PDN_PORT, pkt_filter_upstream,
                               self.pdn_interface["ips"][0])
        main.log.info("Start listening on %s intf %s" %
                      (self.pdn_host.name, self.pdn_interface["name"]))
        main.log.debug("BPF Filter Upstream: \n %s" % pkt_filter_upstream)
        self.pdn_host.startFilter(ifaceName=self.pdn_interface["name"],
                                  sniffCount=len(self.emulated_ues),
                                  pktFilter=pkt_filter_upstream)

        main.log.info(
            "Sending %d packets from eNodeB host" % len(self.emulated_ues))
        for ue in self.emulated_ues.values():
            UP4.buildGtpPacket(self.enodeb_host,
                               src_ip_outer=self.enb_address,
                               dst_ip_outer=self.s1u_address,
                               src_ip_inner=ue["ue_address"],
                               dst_ip_inner=self.pdn_interface["ips"][0],
                               src_udp_inner=UE_PORT,
                               dst_udp_inner=PDN_PORT,
                               teid=int(ue["teid"]))

            self.enodeb_host.sendPacket(iface=self.enodeb_interface["name"])

        packets = UP4.checkFilterAndGetPackets(self.pdn_host)
        fail = False
        if len(self.emulated_ues) != packets.count('Ether'):
            fail = True
            msg = "Failed to capture packets in PDN. "
        else:
            msg = "Correctly captured packet in PDN. "
        # We expect exactly 1 packet per UE
        pktsFiltered = [packets.count("src=" + ue["ue_address"])
                        for ue in self.emulated_ues.values()]
        if pktsFiltered.count(1) != len(pktsFiltered):
            fail = True
            msg += "More than one packet per UE in downstream. "
        else:
            msg += "One packet per UE in upstream. "

        utilities.assert_equal(
            expect=False, actual=fail, onpass=msg, onfail=msg)

    def testDownstreamTraffic(self):
        if self.enodeb_host is None or self.pdn_host is None:
            main.log.error(
                "Need eNodeB and PDN host params to generate scapy traffic")
            return
        pkt_filter_downstream = "ip and udp src port %d and udp dst port %d and dst host %s and src host %s" % (
            GPDU_PORT, GPDU_PORT, self.enb_address, self.s1u_address)
        main.log.info("Start listening on %s intf %s" % (
            self.enodeb_host.name, self.enodeb_interface["name"]))
        main.log.debug("BPF Filter Downstream: \n %s" % pkt_filter_downstream)
        self.enodeb_host.startFilter(ifaceName=self.enodeb_interface["name"],
                                     sniffCount=len(self.emulated_ues),
                                     pktFilter=pkt_filter_downstream)

        main.log.info(
            "Sending %d packets from PDN host" % len(self.emulated_ues))
        for ue in self.emulated_ues.values():
            # From PDN we have to set dest MAC, otherwise scapy will do ARP
            # request for the UE IP address.
            UP4.buildUdpPacket(self.pdn_host,
                               dst_eth=self.router_mac,
                               src_ip=self.pdn_interface["ips"][0],
                               dst_ip=ue["ue_address"],
                               src_udp=PDN_PORT,
                               dst_udp=UE_PORT)
            self.pdn_host.sendPacket(iface=self.pdn_interface["name"])

        packets = UP4.checkFilterAndGetPackets(self.enodeb_host)

        # The BPF filter might capture non-GTP packets because we can't filter
        # GTP header in BPF. For this reason, check that the captured packets
        # are from the expected tunnels.
        # TODO: check inner UDP and IP fields as well
        # FIXME: with newer scapy TEID becomes teid (required for Scapy 2.4.5)
        pktsFiltered = [packets.count("TEID=" + hex(int(ue["teid"])) + "L ")
                        for ue in self.emulated_ues.values()]

        fail = False
        if len(self.emulated_ues) != sum(pktsFiltered):
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

    def verifyNoUesFlow(self, onosCli, retries=3):
        """
        Verify that no PDRs and FARs are installed in ONOS.

        :param onosCli:  An instance of a OnosCliDriver
        :param retries: number of retries
        :return:
        """
        retValue = utilities.retry(f=UP4.__verifyNoPdrsFarsOnos,
                                   retValue=False,
                                   args=[onosCli],
                                   sleep=1,
                                   attempts=retries)
        utilities.assert_equal(expect=True,
                               actual=retValue,
                               onpass="No PDRs and FARs in ONOS",
                               onfail="Stale PDRs or FARs")

    @staticmethod
    def __verifyNoPdrsFarsOnos(onosCli):
        """
        Verify that no PDRs and FARs are installed in ONOS

        :param onosCli: An instance of a OnosCliDriver
        """
        pdrs = onosCli.sendline(cmdStr="up4:read-pdrs", showResponse=True,
                                noExit=True, expectJson=False)
        fars = onosCli.sendline(cmdStr="up4:read-fars", showResponse=True,
                                noExit=True, expectJson=False)
        return pdrs == "" and fars == ""

    def verifyUp4Flow(self, onosCli):
        """
        Verify PDRs and FARs installed via UP4 using the ONOS CLI.

        :param onosCli: An instance of a OnosCliDriver
        """
        pdrs = onosCli.sendline(cmdStr="up4:read-pdrs", showResponse=True,
                                noExit=True, expectJson=False)
        fars = onosCli.sendline(cmdStr="up4:read-fars", showResponse=True,
                                noExit=True, expectJson=False)
        fail = False
        failMsg = ""
        for ue in self.emulated_ues.values():
            if pdrs.count(self.upPdrOnosString(**ue)) != 1:
                failMsg += self.upPdrOnosString(**ue) + "\n"
                fail = True
            if pdrs.count(self.downPdrOnosString(**ue)) != 1:
                failMsg += self.downPdrOnosString(**ue) + "\n"
                fail = True
            if fars.count(self.upFarOnosString(**ue)) != 1:
                failMsg += self.upFarOnosString(**ue) + "\n"
                fail = True
            if fars.count(self.downFarOnosString(**ue)) != 1:
                failMsg += self.downFarOnosString(**ue) + "\n"
                fail = True
        utilities.assert_equal(expect=False, actual=fail,
                               onpass="Correct PDRs and FARs in ONOS",
                               onfail="Wrong PDRs and FARs in ONOS. Missing PDR/FAR:\n" + failMsg)

    def upPdrOnosString(self, pfcp_session_id, teid=None, up_id=None,
                        teid_up=None, far_id_up=None, ctr_id_up=None, qfi=None,
                        **kwargs):
        # TODO: consider that with five_g the output might be different
        if up_id is not None:
            far_id_up = up_id
            ctr_id_up = up_id
        if teid is not None:
            teid_up = teid
        if qfi is not None:
            return "PDR{{Match(Dst={}, TEID={}) -> LoadParams(SEID={}, FAR={}, CtrIdx={}, QFI={})}}".format(
                self.s1u_address, hex(int(teid_up)), hex(int(pfcp_session_id)),
                far_id_up,
                ctr_id_up, qfi)
        return "PDR{{Match(Dst={}, TEID={}) -> LoadParams(SEID={}, FAR={}, CtrIdx={})}}".format(
            self.s1u_address, hex(int(teid_up)), hex(int(pfcp_session_id)),
            far_id_up, ctr_id_up)

    def downPdrOnosString(self, pfcp_session_id, ue_address, down_id=None,
                          far_id_down=None, ctr_id_down=None, **kwargs):
        # TODO: consider that with five_g the output might be different
        if down_id is not None:
            far_id_down = down_id
            ctr_id_down = down_id
        return "PDR{{Match(Dst={}, !GTP) -> LoadParams(SEID={}, FAR={}, CtrIdx={})}}".format(
            ue_address, hex(int(pfcp_session_id)), far_id_down, ctr_id_down)

    def downFarOnosString(self, pfcp_session_id, teid=None, down_id=None,
                          teid_down=None, far_id_down=None, **kwargs):
        if down_id is not None:
            far_id_down = down_id
        if teid is not None:
            teid_down = teid
        return "FAR{{Match(ID={}, SEID={}) -> Encap(Src={}, SPort={}, TEID={}, Dst={})}}".format(
            far_id_down, hex(int(pfcp_session_id)), self.s1u_address, GPDU_PORT,
            hex(int(teid_down)),
            self.enb_address)

    def upFarOnosString(self, pfcp_session_id, up_id=None, far_id_up=None,
                        **kwargs):
        if up_id is not None:
            far_id_up = up_id
        return "FAR{{Match(ID={}, SEID={}) -> Forward()}}".format(
            far_id_up, hex(int(pfcp_session_id)))

    @staticmethod
    def __sanitizeUeData(ue):
        if "five_g" in ue:
            ue["five_g"] = bool(strtobool(ue["five_g"]))
        if "qfi" in ue and ue["qfi"] == "":
            ue["qfi"] = None
        return ue

    def attachUe(self, pfcp_session_id, ue_address,
                 teid=None, up_id=None, down_id=None,
                 teid_up=None, teid_down=None,
                 pdr_id_up=None, far_id_up=None, ctr_id_up=None,
                 pdr_id_down=None, far_id_down=None, ctr_id_down=None,
                 qfi=None, five_g=False):
        self.__programUp4Rules(pfcp_session_id,
                               ue_address,
                               teid, up_id, down_id,
                               teid_up, teid_down,
                               pdr_id_up, far_id_up, ctr_id_up,
                               pdr_id_down, far_id_down, ctr_id_down,
                               qfi, five_g, action="program")

    def detachUe(self, pfcp_session_id, ue_address,
                 teid=None, up_id=None, down_id=None,
                 teid_up=None, teid_down=None,
                 pdr_id_up=None, far_id_up=None, ctr_id_up=None,
                 pdr_id_down=None, far_id_down=None, ctr_id_down=None,
                 qfi=None, five_g=False):
        self.__programUp4Rules(pfcp_session_id,
                               ue_address,
                               teid, up_id, down_id,
                               teid_up, teid_down,
                               pdr_id_up, far_id_up, ctr_id_up,
                               pdr_id_down, far_id_down, ctr_id_down,
                               qfi, five_g, action="clear")

    def __programUp4Rules(self, pfcp_session_id, ue_address,
                          teid=None, up_id=None, down_id=None,
                          teid_up=None, teid_down=None,
                          pdr_id_up=None, far_id_up=None, ctr_id_up=None,
                          pdr_id_down=None, far_id_down=None, ctr_id_down=None,
                          qfi=None, five_g=False, action="program"):
        if up_id is not None:
            pdr_id_up = up_id
            far_id_up = up_id
            ctr_id_up = up_id
        if down_id is not None:
            pdr_id_down = down_id
            far_id_down = down_id
            ctr_id_down = down_id
        if teid is not None:
            teid_up = teid
            teid_down = teid

        entries = []

        # ========================#
        # PDR Entries
        # ========================#

        # Uplink
        tableName = 'PreQosPipe.pdrs'
        actionName = ''
        matchFields = {}
        actionParams = {}
        if qfi is None:
            actionName = 'PreQosPipe.set_pdr_attributes'
        else:
            actionName = 'PreQosPipe.set_pdr_attributes_qos'
            if five_g:
                # TODO: currently QFI_MATCH is unsupported in TNA
                matchFields['has_qfi'] = TRUE
                matchFields["qfi"] = str(qfi)
            actionParams['needs_qfi_push'] = FALSE
            actionParams['qfi'] = str(qfi)
        # Match fields
        matchFields['src_iface'] = IFACE_ACCESS
        matchFields['ue_addr'] = str(ue_address)
        matchFields['teid'] = str(teid_up)
        matchFields['tunnel_ipv4_dst'] = str(self.s1u_address)
        # Action params
        actionParams['id'] = str(pdr_id_up)
        actionParams['fseid'] = str(pfcp_session_id)
        actionParams['ctr_id'] = str(ctr_id_up)
        actionParams['far_id'] = str(far_id_up)
        actionParams['needs_gtpu_decap'] = TRUE
        if not self.__add_entry(tableName, actionName, matchFields,
                                actionParams, entries, action):
            return False

        # Downlink
        tableName = 'PreQosPipe.pdrs'
        matchFields = {}
        actionParams = {}
        if qfi is None:
            actionName = 'PreQosPipe.set_pdr_attributes'
        else:
            actionName = 'PreQosPipe.set_pdr_attributes_qos'
            # TODO: currently QFI_PUSH is unsupported in TNA
            actionParams['needs_qfi_push'] = TRUE if five_g else FALSE
            actionParams['qfi'] = str(qfi)
        # Match fields
        matchFields['src_iface'] = IFACE_CORE
        matchFields['ue_addr'] = str(ue_address)
        # Action params
        actionParams['id'] = str(pdr_id_down)
        actionParams['fseid'] = str(pfcp_session_id)
        actionParams['ctr_id'] = str(ctr_id_down)
        actionParams['far_id'] = str(far_id_down)
        actionParams['needs_gtpu_decap'] = FALSE
        if not self.__add_entry(tableName, actionName, matchFields,
                                actionParams, entries, action):
            return False

        # ========================#
        # FAR Entries
        # ========================#

        # Uplink
        tableName = 'PreQosPipe.load_far_attributes'
        actionName = 'PreQosPipe.load_normal_far_attributes'
        matchFields = {}
        actionParams = {}

        # Match fields
        matchFields['far_id'] = str(far_id_up)
        matchFields['session_id'] = str(pfcp_session_id)
        # Action params
        actionParams['needs_dropping'] = FALSE
        actionParams['notify_cp'] = FALSE
        if not self.__add_entry(tableName, actionName, matchFields,
                                actionParams, entries, action):
            return False

        # Downlink
        tableName = 'PreQosPipe.load_far_attributes'
        actionName = 'PreQosPipe.load_tunnel_far_attributes'
        matchFields = {}
        actionParams = {}

        # Match fields
        matchFields['far_id'] = str(far_id_down)
        matchFields['session_id'] = str(pfcp_session_id)
        # Action params
        actionParams['needs_dropping'] = FALSE
        actionParams['notify_cp'] = FALSE
        actionParams['needs_buffering'] = FALSE
        actionParams['tunnel_type'] = TUNNEL_TYPE_GPDU
        actionParams['src_addr'] = str(self.s1u_address)
        actionParams['dst_addr'] = str(self.enb_address)
        actionParams['teid'] = str(teid_down)
        actionParams['sport'] = TUNNEL_SPORT
        if not self.__add_entry(tableName, actionName, matchFields,
                                actionParams, entries, action):
            return False
        if action == "program":
            main.log.info("All entries added successfully.")
        elif action == "clear":
            self.__clear_entries(entries)

    def __add_entry(self, tableName, actionName, matchFields, actionParams,
                    entries, action):
        if action == "program":
            self.up4_client.buildP4RtTableEntry(
                tableName=tableName, actionName=actionName,
                actionParams=actionParams, matchFields=matchFields)
            if self.up4_client.pushTableEntry(debug=True) == main.TRUE:
                main.log.info("*** Entry added.")
            else:
                main.log.error("Error during table insertion")
                self.__clear_entries(entries)
                return False
        entries.append({"tableName": tableName, "actionName": actionName,
                        "matchFields": matchFields,
                        "actionParams": actionParams})
        return True

    def __clear_entries(self, entries):
        for i, entry in enumerate(entries):
            self.up4_client.buildP4RtTableEntry(**entry)
            if self.up4_client.deleteTableEntry(debug=True) == main.TRUE:
                main.log.info(
                    "*** Entry %d of %d deleted." % (i + 1, len(entries)))
            else:
                main.log.error("Error during table delete")

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
