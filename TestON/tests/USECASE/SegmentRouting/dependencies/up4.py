from distutils.util import strtobool
import copy

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

N_FLOWS_PER_UE = 4


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
        self.up4_client = None
        self.no_host = False

    def setup(self, p4rt_client, no_host=False):
        """
        Set up P4RT and scapy on eNB and PDN hosts
        :param p4rt_client: a P4RuntimeCliDriver component
        :param no_host: True if you don't want to start scapy on the hosts
        :return:
        """
        self.s1u_address = main.params["UP4"]["s1u_address"]
        self.emulated_ues = main.params["UP4"]['ues']
        self.up4_client = p4rt_client
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

        # Start components
        self.up4_client.startP4RtClient()
        if not self.no_host:
            if self.enodebs is not None:
                for enb in self.enodebs.values():
                    enb["host"].startScapy(ifaceName=enb["interface"],
                                            enableGtp=True)
            if self.pdn_host is not None:
                self.pdn_host.startScapy(ifaceName=self.pdn_interface["name"])

    def teardown(self):
        self.up4_client.stopP4RtClient()
        if not self.no_host:
            if self.enodebs is not None:
                for enb in self.enodebs.values():
                    enb["host"].stopScapy()
            if self.pdn_host is not None:
                self.pdn_host.stopScapy()

    def attachUes(self):
        for (name, ue) in self.emulated_ues.items():
            ue = UP4.__sanitizeUeData(ue)
            self.attachUe(name, **ue)

    def detachUes(self):
        for (name, ue) in self.emulated_ues.items():
            ue = UP4.__sanitizeUeData(ue)
            self.detachUe(name, **ue)

    def testUpstreamTraffic(self, enb_names=None, shouldFail=False):
        if self.enodebs is None or self.pdn_host is None:
            main.log.error(
                "Need eNodeB and PDN host params to generate scapy traffic")
            return
        # Scapy filter needs to start before sending traffic
        if enb_names is None or enb_names == []:
            enodebs = self.enodebs.values()
        else:
            enodebs = [self.enodebs[enb] for enb in enb_names]
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
                              (PDN_PORT, pkt_filter_upstream,
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
                                   dst_udp_inner=PDN_PORT,
                                   teid=int(ue["teid"]))
                enb["host"].sendPacket(iface=enb["interface"])

        packets = UP4.checkFilterAndGetPackets(self.pdn_host)
        fail = False
        if len(ues) != packets.count('Ether'):
            fail = True
            msg = "Failed to capture packets in PDN.\n" + str(packets)
        else:
            msg = "Correctly captured packet in PDN. "
        # We expect exactly 1 packet per UE
        pktsFiltered = [packets.count("src=" + ue["ue_address"]) for ue in ues]
        if pktsFiltered.count(1) != len(pktsFiltered):
            fail = True
            msg += "\nError on the number of packets per UE in downstream.\n" + str(packets)
        else:
            msg += "\nOne packet per UE in upstream. "

        utilities.assert_equal(
            expect=shouldFail, actual=fail, onpass=msg, onfail=msg)

    def testDownstreamTraffic(self, enb_names=None, shouldFail=False):
        if self.enodebs is None or self.pdn_host is None:
            main.log.error(
                "Need eNodeB and PDN host params to generate scapy traffic")
            return
        if enb_names is None or enb_names == []:
            enodebs = self.enodebs.values()
        else:
            enodebs = [self.enodebs[enb] for enb in enb_names]
        pkt_filter_downstream = "ip and udp src port %d and udp dst port %d and src host %s" % (
            GPDU_PORT, GPDU_PORT, self.s1u_address)
        ues = []
        for enb in enodebs:
            filter_down = pkt_filter_downstream + " and dst host %s" % enb["enb_address"]
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
                               src_udp=PDN_PORT,
                               dst_udp=UE_PORT)
            self.pdn_host.sendPacket(iface=self.pdn_interface["name"])
        packets = ""
        for enb in enodebs:
            pkt = UP4.checkFilterAndGetPackets(enb["host"])
            packets += pkt
        # The BPF filter might capture non-GTP packets because we can't filter
        # GTP header in BPF. For this reason, check that the captured packets
        # are from the expected tunnels.
        # TODO: check inner UDP and IP fields as well
        # FIXME: with newer scapy TEID becomes teid (required for Scapy 2.4.5)
        pktsFiltered= [packets.count("TEID=" + hex(int(ue["teid"])) + "L ")
             for ue in ues]
        main.log.info("PACKETS: " + str(packets))
        main.log.info("PKTs Filtered: " + str(pktsFiltered))
        fail = False
        if len(ues) != sum(pktsFiltered):
            fail = True
            msg = "Failed to capture packets in eNodeB.\n" + str(packets)
        else:
            msg = "Correctly captured packets in eNodeB. "
        # We expect exactly 1 packet per UE
        if pktsFiltered.count(1) != len(pktsFiltered):
            fail = True
            msg += "\nError on the number of packets per GTP TEID in downstream.\n" + str(packets)
        else:
            msg += "\nOne packet per GTP TEID in downstream. "

        utilities.assert_equal(
            expect=shouldFail, actual=fail, onpass=msg, onfail=msg)

    def readPdrsNumber(self):
        """
        Read the PDRs table and return the number of entries in the PDRs table

        :return: Number of entries in the PDRs table
        """
        tableName = 'PreQosPipe.pdrs'
        return self.up4_client.readNumberTableEntries(tableName)

    def readFarsNumber(self):
        """
        Read the FARs table and return the number of entries in the FARs table

        :return: Number of entries in the FARs table
        """
        tableName = 'PreQosPipe.load_far_attributes'
        return self.up4_client.readNumberTableEntries(tableName)

    def verifyUesFlowNumberP4rt(self):
        """
        Verify via P4RT CLI that the number of PDRs and FARs is the expected one

        :return: True if the number of PDRs and FARs is expected, False otherwise
        """
        nPdrs = self.readPdrsNumber()
        nFars = self.readFarsNumber()
        return nPdrs == nFars == len(self.emulated_ues) * 2

    def verifyNoUesFlowNumberP4rt(self, preInstalledUes=0):
        """
        Verify via P4RT CLI that there is no PDRs and FARs installed.

        :param preInstalledUes: Number of UEs whose PDRs and FARs are still programmed
        :return:
        """
        return self.readPdrsNumber() == self.readFarsNumber() == preInstalledUes * 2

    def verifyNoUesFlow(self, onosCli, retries=10):
        """
        Verify that no PDRs and FARs are installed in ONOS.

        :param onosCli:  An instance of a OnosCliDriver
        :param retries: number of retries
        :return:
        """
        retValue = utilities.retry(f=UP4.__verifyNoPdrsFarsOnos,
                                   retValue=False,
                                   args=[onosCli],
                                   sleep=5,
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

    def verifyUp4Flow(self, onosCli, retries=10):
        """
        Verify PDRs and FARs installed via UP4 using the ONOS CLI.

        :param onosCli: An instance of a OnosCliDriver
        :param retries: Number of retries
        """
        failString=""
        retValue = utilities.retry(f=self.__internalVerifyUp4Flow,
                                   retValue=False,
                                   args=[onosCli, failString],
                                   sleep=5,
                                   attempts=retries)
        utilities.assert_equal(
            expect=True,
            actual=retValue,
            onpass="Correct PDRs and FARs in ONOS",
            onfail="Wrong PDRs and FARs in ONOS. Missing PDR/FAR:\n" + failString
        )

    def __internalVerifyUp4Flow(self, onosCli, failMsg=""):
        pdrs = onosCli.sendline(cmdStr="up4:read-pdrs", showResponse=True,
                                noExit=True, expectJson=False)
        fars = onosCli.sendline(cmdStr="up4:read-fars", showResponse=True,
                                noExit=True, expectJson=False)
        fail = False
        for (ue_name, ue) in self.emulated_ues.items():
            if pdrs.count(self.upPdrOnosString(**ue)) != 1:
                failMsg += self.upPdrOnosString(**ue) + "\n"
                fail = True
            if pdrs.count(self.downPdrOnosString(**ue)) != 1:
                failMsg += self.downPdrOnosString(**ue) + "\n"
                fail = True
            if fars.count(self.upFarOnosString(**ue)) != 1:
                failMsg += self.upFarOnosString(**ue) + "\n"
                fail = True
            if fars.count(self.downFarOnosString(ue_name, **ue)) != 1:
                failMsg += self.downFarOnosString(ue_name, **ue) + "\n"
                fail = True
        return not fail

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
                far_id_up, ctr_id_up, qfi)
        return "PDR{{Match(Dst={}, TEID={}) -> LoadParams(SEID={}, FAR={}, CtrIdx={})}}".format(
            self.s1u_address, hex(int(teid_up)), hex(int(pfcp_session_id)),
            far_id_up, ctr_id_up)

    def downPdrOnosString(self, pfcp_session_id, ue_address, down_id=None,
                          far_id_down=None, ctr_id_down=None, qfi=None,
                          **kwargs):
        # TODO: consider that with five_g the output might be different
        if down_id is not None:
            far_id_down = down_id
            ctr_id_down = down_id
        if qfi is not None:
            return "PDR{{Match(Dst={}, !GTP) -> LoadParams(SEID={}, FAR={}, CtrIdx={}, QFI={})}}".format(
                ue_address, hex(int(pfcp_session_id)), far_id_down, ctr_id_down,
                qfi)
        return "PDR{{Match(Dst={}, !GTP) -> LoadParams(SEID={}, FAR={}, CtrIdx={})}}".format(
            ue_address, hex(int(pfcp_session_id)), far_id_down, ctr_id_down)

    def downFarOnosString(self, ue_name, pfcp_session_id, teid=None, down_id=None,
                          teid_down=None, far_id_down=None, **kwargs):
        if down_id is not None:
            far_id_down = down_id
        if teid is not None:
            teid_down = teid
        enb_address = self.__getEnbAddress(ue_name)
        return "FAR{{Match(ID={}, SEID={}) -> Encap(Src={}, SPort={}, TEID={}, Dst={})}}".format(
            far_id_down, hex(int(pfcp_session_id)), self.s1u_address, GPDU_PORT,
            hex(int(teid_down)), enb_address)

    def upFarOnosString(self, pfcp_session_id, up_id=None, far_id_up=None,
                        **kwargs):
        if up_id is not None:
            far_id_up = up_id
        return "FAR{{Match(ID={}, SEID={}) -> Forward()}}".format(
            far_id_up, hex(int(pfcp_session_id)))

    @staticmethod
    def __sanitizeUeData(ue):
        if "five_g" in ue and type(ue["five_g"]) != bool:
            ue["five_g"] = bool(strtobool(ue["five_g"]))
        if "qfi" in ue and ue["qfi"] == "":
            ue["qfi"] = None
        return ue

    def attachUe(self, ue_name, pfcp_session_id, ue_address,
                 teid=None, up_id=None, down_id=None,
                 teid_up=None, teid_down=None,
                 pdr_id_up=None, far_id_up=None, ctr_id_up=None,
                 pdr_id_down=None, far_id_down=None, ctr_id_down=None,
                 qfi=None, five_g=False):
        self.__programUp4Rules(ue_name,
                               pfcp_session_id,
                               ue_address,
                               teid, up_id, down_id,
                               teid_up, teid_down,
                               pdr_id_up, far_id_up, ctr_id_up,
                               pdr_id_down, far_id_down, ctr_id_down,
                               qfi, five_g, action="program")

    def detachUe(self, ue_name, pfcp_session_id, ue_address,
                 teid=None, up_id=None, down_id=None,
                 teid_up=None, teid_down=None,
                 pdr_id_up=None, far_id_up=None, ctr_id_up=None,
                 pdr_id_down=None, far_id_down=None, ctr_id_down=None,
                 qfi=None, five_g=False):
        self.__programUp4Rules(ue_name,
                               pfcp_session_id,
                               ue_address,
                               teid, up_id, down_id,
                               teid_up, teid_down,
                               pdr_id_up, far_id_up, ctr_id_up,
                               pdr_id_down, far_id_down, ctr_id_down,
                               qfi, five_g, action="clear")

    def __programUp4Rules(self, ue_name, pfcp_session_id, ue_address,
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

        # Retrieve eNobeB address from eNodeB list
        enb_address = self.__getEnbAddress(ue_name)

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
        actionParams['dst_addr'] = str(enb_address)
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
