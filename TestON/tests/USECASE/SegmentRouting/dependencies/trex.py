from distutils.util import strtobool
from tests.USECASE.SegmentRouting.dependencies import scapy_helper


class Trex:
    """
    Utility that manages interaction with TRex server via TRexDriver component
    Example params:
    <TREX>
        <port_stats>0,1</port_stats>
        <flows>
            <RT_FROM_UE>
                <name>Real Time</name>
                <l1_bps>40000000</l1_bps>
                <trex_port>0</trex_port>
                <packet>
                    <pktlen>1400</pktlen>
                    <ip_src>10.240.0.2</ip_src>
                    <ip_dst>10.32.11.101</ip_dst>
                    <eth_src>3C:EC:EF:3E:0B:A0</eth_src>
                    <eth_dst>00:00:0A:4C:1C:46</eth_dst>
                    <gtp_teid>200</gtp_teid>
                    <s1u_addr>10.32.11.126</s1u_addr>
                    <enb_addr>10.32.11.100</enb_addr>
                </packet>
                <latency_stats>true</latency_stats>
                <flow_id>10</flow_id> <!-- Mandatory when latency_stats=true -->
                <delay>50000</delay> <!-- wait 50 ms till start to let queues fill up -->
                <expected_min_received>1</expected_min_received>
                <expected_max_dropped>0</expected_max_dropped>
                <expected_max_latency>1500</expected_max_latency>
                <expected_99_9_percentile_latency>100</expected_99_9_percentile_latency>
            </RT_FROM_UE>
        </flows>
    <TREX>
    """

    def __init__(self):
        self.trex_client = None
        self.traffic_flows = {}
        self.port_stats = []
        self.packets = {}  # Per-flow dictionary of packets

    def setup(self, trex_client):
        self.trex_client = trex_client
        self.traffic_flows = main.params["TREX"]["flows"]
        if "port_stats" in main.params["TREX"] and \
                main.params["TREX"].get("port_stats") is not '':
            self.port_stats = [int(p) for p in
                               main.params["TREX"].get("port_stats").split(",")]
        self.trex_client.setupTrex(main.configPath)

    def teardown(self):
        self.trex_client.stopTrexServer()

    def createFlow(self, flow_name):
        if flow_name not in self.traffic_flows:
            main.log.error("CFG flow not present in params")
            return False
        self.traffic_flows[flow_name]["packet"] = Trex.__sanitizePacketConfig(
            self.traffic_flows[flow_name]["packet"])
        if "gtp_teid" in self.traffic_flows[flow_name]["packet"]:
            # packets must be GTP encapped
            self.packets[flow_name] = scapy_helper.simple_gtp_udp_packet(
                **self.traffic_flows[flow_name]["packet"])
        else:
            self.packets[flow_name] = scapy_helper.simple_udp_packet(
                **self.traffic_flows[flow_name]["packet"])

    def resetFlows(self):
        self.packets = {}

    def sendAndReceiveTraffic(self, duration):
        """
        Connect the client, create the flows in trex (with packets created with
        createFlow, send and receive the traffic, and disconnect the client.
        :param duration: traffic duration
        :return: port statistics collected while running the test
        """
        self.trex_client.connectTrexClient()
        for flow_name, packet in self.packets.items():
            flow_config = self.traffic_flows[flow_name]
            Trex.__sanitizeFlowConfig(flow_config)
            self.trex_client.addStream(pkt=packet,
                                       trex_port=flow_config["trex_port"],
                                       l1_bps=flow_config["l1_bps"],
                                       percentage=flow_config["percentage"],
                                       delay=flow_config["delay"],
                                       flow_id=flow_config["flow_id"],
                                       flow_stats=flow_config["latency_stats"])
        result = self.trex_client.startAndWaitTraffic(duration=duration,
                                                      ports=self.port_stats)
        self.trex_client.disconnectTrexClient()
        return result

    def verifyCongestion(self, live_stats, multiplier=1):
        """
        Verify and assert that the test was able to generate congestion by
        checking that average TX traffic is greater than average RX traffic from
        stats collected during the test.

        :param live_stats: Stats collected during tests
        :param multiplier: Multiplier for RX traffic in case we encap/decap traffic
        :return:
        """
        avg_tx = sum(
            [sum(v["tx_bps"]) / len(v["tx_bps"])
             for (k, v) in live_stats.items() if k != "duration"]
        )
        avg_rx = sum(
            [sum(v["rx_bps"]) / len(v["rx_bps"])
             for (k, v) in live_stats.items() if k != "duration"]
        )

        utilities.assert_equals(
            expect=True,
            actual=avg_tx > avg_rx * multiplier,
            onpass="Congestion created: AVG TX ({}) > AVG RX ({})".format(
                avg_tx, avg_rx),
            onfail="NO Congestion: AVG TX ({}) <= AVG RX ({})".format(
                avg_tx, avg_rx)
        )

    def assertRxRate(self, flow_name, duration, delta=0.05):
        if not self.isFlowStats(flow_name):
            main.log.info("No flow stats for flow {}".format(flow_name))
            utilities.assert_equals(
                expect=True,
                actual=False,
                onpass="",
                onfail="No Flow stats for requested flow: {}".format(flow_name))
            return
        expected_rx_rate_bps = int(
            self.traffic_flows[flow_name].get("expected_rx_bps", "0"))
        flow_label = self.traffic_flows[flow_name].get("name", flow_name)
        flow_id = self.traffic_flows[flow_name]["flow_id"]
        flow_stats = self.trex_client.getFlowStats(flow_id)
        actual_rx_rate_bps = (flow_stats.rx_bytes * 8) / duration
        rates_within_delta = abs((actual_rx_rate_bps/expected_rx_rate_bps) - 1) <= delta
        utilities.assert_equals(
            expect=True,
            actual=rates_within_delta,
            onpass="Traffic Flow {}: Expected rate ({}) within delta ({}) to actual rate ({})".format(
                flow_label, expected_rx_rate_bps, delta, actual_rx_rate_bps),
            onfail="Traffic Flow {}: Expected rate ({}) outside delta ({}) to actual rate ({})".format(
                flow_label, expected_rx_rate_bps, delta, actual_rx_rate_bps)
        )

    def assertRxPackets(self, flow_name):
        if not self.isFlowStats(flow_name):
            main.log.info("No flow stats for flow {}".format(flow_name))
        expected_min_received = int(
            self.traffic_flows[flow_name].get("expected_min_received", "1"))
        flow_label = self.traffic_flows[flow_name].get("name", flow_name)
        flow_id = self.traffic_flows[flow_name]["flow_id"]
        flow_stats = self.trex_client.getFlowStats(flow_id)
        utilities.assert_equals(
            expect=True,
            actual=flow_stats.rx_packets >= expected_min_received,
            onpass="Traffic Flow {}: Received traffic".format(flow_label),
            onfail="Traffic Flow {}: No traffic received".format(flow_label))

    def assertDroppedPacket(self, flow_name):
        if not self.isFlowStats(flow_name):
            main.log.info("No flow stats for flow {}".format(flow_name))
        expected_max_dropped = int(
            self.traffic_flows[flow_name].get("expected_max_dropped", "0"))
        flow_label = self.traffic_flows[flow_name].get("name", flow_name)
        flow_id = self.traffic_flows[flow_name]["flow_id"]
        flow_stats = self.trex_client.getFlowStats(flow_id)
        actual_dropped = flow_stats.tx_packets - flow_stats.rx_packets
        utilities.assert_equals(
            expect=True,
            actual=actual_dropped <= expected_max_dropped,
            onpass="Traffic Flow {}: {} packets dropped, below threshold={}".format(
                flow_label, actual_dropped, expected_max_dropped
            ),
            onfail="Traffic Flow {}: {} packets dropped, above threshold={}".format(
                flow_label, actual_dropped, expected_max_dropped
            )
        )

    def assertMaxLatency(self, flow_name):
        if not self.isFlowStats(flow_name):
            main.log.info("No flow stats for flow {}".format(flow_name))
        expected_max_latency = int(
            self.traffic_flows[flow_name].get("expected_max_latency", "0"))
        flow_label = self.traffic_flows[flow_name].get("name", flow_name)
        latency_stats = self.__getLatencyStats(flow_name)
        utilities.assert_equals(
            expect=True,
            actual=latency_stats.total_max <= expected_max_latency,
            onpass="Traffic Flow {}: Maximum latency below threshold".format(
                flow_label),
            onfail="Traffic Flow {}: Maximum latency is too high {}".format(
                flow_label, latency_stats.total_max))

    def assert99_9PercentileLatency(self, flow_name):
        if not self.isFlowStats(flow_name):
            main.log.info("No flow stats for flow {}".format(flow_name))
            return
        if not "expected_99_9_percentile_latency" in self.traffic_flows[flow_name].keys():
            main.log.info("No 99.9th percentile parameter for test")
            return
        expected_99_9_percentile_latency = int(
            self.traffic_flows[flow_name].get(
                "expected_99_9_percentile_latency", "0"))
        flow_label = self.traffic_flows[flow_name].get("name", flow_name)
        latency_stats = self.__getLatencyStats(flow_name)
        utilities.assert_equals(
            expect=True,
            actual=latency_stats.percentile_99_9 <= expected_99_9_percentile_latency,
            onpass="Traffic Flow {}: 99.9th percentile latency below threshold".format(
                flow_label),
            onfail="Traffic Flow {}: 99.9th percentile latency is too high {}".format(
                flow_label, latency_stats.percentile_99_9))

    def assert90PercentileLatency(self, flow_name):
        if not self.isFlowStats(flow_name):
            main.log.info("No flow stats for flow {}".format(flow_name))
            return
        if not "expected_90_percentile_latency" in self.traffic_flows[flow_name].keys():
            main.log.info("No 90th percentile parameter for test")
            return
        expected_90_percentile_latency = int(
            self.traffic_flows[flow_name].get(
                "expected_90_percentile_latency", "0"))
        flow_label = self.traffic_flows[flow_name].get("name", flow_name)
        latency_stats = self.__getLatencyStats(flow_name)
        utilities.assert_equals(
            expect=True,
            actual=latency_stats.percentile_90 <= expected_90_percentile_latency,
            onpass="Traffic Flow {}: 90th percentile latency below threshold".format(
                flow_label),
            onfail="Traffic Flow {}: 90th percentile latency is too high {}".format(
                flow_label, latency_stats.percentile_90))

    def logPortStats(self):
        main.log.debug(self.port_stats)
        for port in self.port_stats:
            self.trex_client.logPortStats(port)

    def logFlowStats(self, flow_name):
        if self.isFlowStats(flow_name):
            flow_id = self.traffic_flows[flow_name]["flow_id"]
            self.trex_client.logFlowStats(flow_id)
            self.trex_client.logLatencyStats(flow_id)

    def isFlowStats(self, flow_name):
        return self.traffic_flows[flow_name]["latency_stats"]

    def __getLatencyStats(self, flow_name):
        flow_id = self.traffic_flows[flow_name]["flow_id"]
        return self.trex_client.getLatencyStats(flow_id)

    @staticmethod
    def __sanitizePacketConfig(packet):
        if "gtp_teid" in packet.keys():
            packet["gtp_teid"] = int(packet["gtp_teid"])
        if "pktlen" in packet.keys():
            packet["pktlen"] = int(packet["pktlen"])
        if "udp_dport" in packet.keys():
            packet["udp_dport"] = int(packet["udp_dport"])
        if "udp_sport" in packet.keys():
            packet["udp_sport"] = int(packet["udp_sport"])
        return packet

    @staticmethod
    def __sanitizeFlowConfig(flow_config):
        flow_config["trex_port"] = int(flow_config["trex_port"])
        flow_config["percentage"] = float(
            flow_config["percentage"]) if "percentage" in flow_config else None
        flow_config["l1_bps"] = float(
            flow_config["l1_bps"]) if "l1_bps" in flow_config else None
        flow_config["delay"] = int(flow_config.get("delay", 0))
        flow_config["flow_id"] = int(
            flow_config["flow_id"]) if "flow_id" in flow_config else None
        flow_config["latency_stats"] = bool(
            strtobool(flow_config.get("latency_stats", "False")))
