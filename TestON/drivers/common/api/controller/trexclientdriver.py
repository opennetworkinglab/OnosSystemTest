"""
Copyright 2021 Open Networking Foundation (ONF)

Please refer questions to either the onos test mailing list at <onos-test@onosproject.org>,
the System Testing Plans and Results wiki page at <https://wiki.onosproject.org/x/voMg>,
or the System Testing Guide page at <https://wiki.onosproject.org/x/WYQg>

"""
import time
import os
import copy
import sys
import importlib
import collections
import numpy as np

from drivers.common.api.controllerdriver import Controller

from socket import error as ConnectionRefusedError
from distutils.util import strtobool

TREX_FILES_DIR = "/tmp/trex_files/"

LatencyStats = collections.namedtuple(
    "LatencyStats",
    [
        "pg_id",
        "jitter",
        "average",
        "total_max",
        "total_min",
        "last_max",
        "histogram",
        "dropped",
        "out_of_order",
        "duplicate",
        "seq_too_high",
        "seq_too_low",
        "percentile_50",
        "percentile_75",
        "percentile_90",
        "percentile_99",
        "percentile_99_9",
        "percentile_99_99",
        "percentile_99_999",
    ],
)

PortStats = collections.namedtuple(
    "PortStats",
    [
        "tx_packets",
        "rx_packets",
        "tx_bytes",
        "rx_bytes",
        "tx_errors",
        "rx_errors",
        "tx_bps",
        "tx_pps",
        "tx_bps_L1",
        "tx_util",
        "rx_bps",
        "rx_pps",
        "rx_bps_L1",
        "rx_util",
    ],
)

FlowStats = collections.namedtuple(
    "FlowStats",
    [
        "pg_id",
        "tx_packets",
        "rx_packets",
        "tx_bytes",
        "rx_bytes",
    ],
)


class TrexClientDriver(Controller):
    """
    Implements a Trex Client Driver
    """

    def __init__(self):
        self.trex_address = "localhost"
        self.trex_config = None  # Relative path in dependencies of the test using this driver
        self.force_restart = True
        self.sofware_mode = False
        self.setup_successful = False
        self.stats = None
        self.trex_client = None
        self.trex_daemon_client = None
        self.trex_library_python_path = None
        self.gen_traffic_per_port = {}
        super(TrexClientDriver, self).__init__()

    def connect(self, **connectargs):
        global STLClient, STLStreamDstMAC_PKT, CTRexClient, STLPktBuilder, \
            STLFlowLatencyStats, STLStream, STLTXCont
        try:
            for key in connectargs:
                vars(self)[key] = connectargs[key]
            for key in self.options:
                if key == "trex_address":
                    self.trex_address = self.options[key]
                elif key == "trex_config":
                    self.trex_config = self.options[key]
                elif key == "force_restart":
                    self.force_restart = bool(strtobool(self.options[key]))
                elif key == "software_mode":
                    self.software_mode = bool(strtobool(self.options[key]))
                elif key == "trex_library_python_path":
                    self.trex_library_python_path = self.options[key]
            self.name = self.options["name"]
            if self.trex_library_python_path is not None:
                sys.path.append(self.trex_library_python_path)
            # Import after appending the TRex library Python path
            STLClient = getattr(importlib.import_module("trex.stl.api"), "STLClient")
            STLStreamDstMAC_PKT = getattr(importlib.import_module("trex.stl.api"), "STLStreamDstMAC_PKT")
            CTRexClient = getattr(importlib.import_module("trex_stf_lib.trex_client"), "CTRexClient")
            STLFlowLatencyStats = getattr(importlib.import_module("trex_stl_lib.api"), "STLFlowLatencyStats")
            STLPktBuilder = getattr(importlib.import_module("trex_stl_lib.api"), "STLPktBuilder")
            STLStream = getattr(importlib.import_module("trex_stl_lib.api"), "STLStream")
            STLTXCont = getattr(importlib.import_module("trex_stl_lib.api"), "STLTXCont")
        except Exception as inst:
            main.log.error("Uncaught exception: " + str(inst))
            main.cleanAndExit()
        return super(TrexClientDriver, self).connect()

    def disconnect(self):
        """
        Called when Test is complete
        """
        self.disconnectTrexClient()
        self.stopTrexServer()
        return main.TRUE

    def setupTrex(self, pathToTrexConfig):
        """
        Setup TRex server passing the TRex configuration.
        :return: True if setup successful, False otherwise
        """
        main.log.debug(self.name + ": Setting up TRex server")
        if self.software_mode:
            trex_args = "--software --no-hw-flow-stat"
        else:
            trex_args = None
        self.trex_daemon_client = CTRexClient(self.trex_address,
                                              trex_args=trex_args)
        success = self.__set_up_trex_server(
            self.trex_daemon_client, self.trex_address,
            os.path.join(pathToTrexConfig, self.trex_config),
            self.force_restart
        )
        if not success:
            main.log.error("Failed to set up TRex daemon!")
            return False
        self.setup_successful = True
        return True

    def connectTrexClient(self):
        if not self.setup_successful:
            main.log.error("Cannot connect TRex Client, first setup TRex")
            return False
        main.log.info("Connecting TRex Client")
        self.trex_client = STLClient(server=self.trex_address)
        self.trex_client.connect()
        self.trex_client.acquire()
        self.trex_client.reset()  # Resets configs from all ports
        self.trex_client.clear_stats()  # Clear status from all ports
        # Put all ports to promiscuous mode, otherwise they will drop all
        # incoming packets if the destination mac is not the port mac address.
        self.trex_client.set_port_attr(self.trex_client.get_all_ports(),
                                       promiscuous=True)
        self.gen_traffic_per_port = {}
        self.stats = None
        return True

    def disconnectTrexClient(self):
        # Teardown TREX Client
        if self.trex_client is not None:
            main.log.info("Tearing down STLClient...")
            self.trex_client.stop()
            self.trex_client.release()
            self.trex_client.disconnect()
            self.trex_client = None
            # Do not reset stats

    def stopTrexServer(self):
        if self.trex_daemon_client is not None:
            self.trex_daemon_client.stop_trex()
            self.trex_daemon_client = None

    def addStream(self, pkt, trex_port, l1_bps=None, percentage=None,
                  delay=0, flow_id=None, flow_stats=False):
        """
        :param pkt: Scapy packet, TRex will send copy of this packet
        :param trex_port: Port number to send packet from, must match a port in the TRex config file
        :param l1_bps: L1 Throughput generated by TRex (mutually exclusive with percentage)
        :param percentage: Percentage usage of the selected port bandwidth (mutually exlusive with l1_bps)
        :param flow_id: Flow ID, required when saving latency statistics
        :param flow_stats: True to measure flow statistics (latency and packet), False otherwise, might require software mode
        :return: True if the stream is create, false otherwise
        """
        if (percentage is None and l1_bps is None) or (
                percentage is not None and l1_bps is not None):
            main.log.error(
                "Either percentage or l1_bps must be provided when creating a stream")
            return False
        main.log.debug("Creating flow stream")
        main.log.debug(
            "port: %d, l1_bps: %s, percentage: %s, delay: %d, flow_id:%s, flow_stats: %s" % (
                trex_port, str(l1_bps), str(percentage), delay, str(flow_id),
                str(flow_stats)))
        main.log.debug(pkt.summary())
        if flow_stats:
            traffic_stream = self.__create_latency_stats_stream(
                pkt,
                pg_id=flow_id,
                isg=delay,
                percentage=percentage,
                l1_bps=l1_bps)
        else:
            traffic_stream = self.__create_background_stream(
                pkt,
                percentage=percentage,
                l1_bps=l1_bps)
        self.trex_client.add_streams(traffic_stream, ports=trex_port)
        gen_traffic = self.gen_traffic_per_port.get(trex_port, 0)
        gen_traffic += l1_bps
        self.gen_traffic_per_port[trex_port] = gen_traffic
        return True

    def startAndWaitTraffic(self, duration=10, ports=[]):
        """
        Start generating traffic and wait traffic to be send

        :param duration: Traffic generation duration
        :param ports: Ports IDs to monitor while traffic is active
        :return: port statistics collected while traffic is active
        """
        if not self.trex_client:
            main.log.error(
                "Cannot start traffic, first connect the TRex client")
            return False
        # Reset stats from previous run
        self.stats = None
        main.step("Sending traffic for %d seconds" % duration)
        self.trex_client.start(self.gen_traffic_per_port.keys(), mult="1",
                               duration=duration)
        main.log.info("Waiting until all traffic is sent..")
        result = self.__monitor_port_stats({p: self.gen_traffic_per_port.get(p, None) for p in ports})
        self.trex_client.wait_on_traffic(ports=self.gen_traffic_per_port.keys(),
                                         rx_delay_ms=100)
        main.log.info("...traffic sent!")
        # Reset sender port so we can run other tests with the same TRex client
        self.gen_traffic_per_port = {}
        main.log.info("Getting stats")
        self.stats = self.trex_client.get_stats()
        return result

    def getFlowStats(self, flow_id):
        if self.stats is None:
            main.log.error("No stats saved!")
            return None
        return TrexClientDriver.__get_flow_stats(flow_id, self.stats)

    def logFlowStats(self, flow_id):
        main.log.info("Statistics for flow {}: {}".format(
            flow_id,
            TrexClientDriver.__get_readable_flow_stats(
                self.getFlowStats(flow_id))))

    def getLatencyStats(self, flow_id):
        if self.stats is None:
            main.log.error("No stats saved!")
            return None
        return TrexClientDriver.__get_latency_stats(flow_id, self.stats)

    def logLatencyStats(self, flow_id):
        main.log.info("Latency statistics for flow {}: {}".format(
            flow_id,
            TrexClientDriver.__get_readable_latency_stats(
                self.getLatencyStats(flow_id))))

    def getPortStats(self, port_id):
        if self.stats is None:
            main.log.error("No stats saved!")
            return None
        return TrexClientDriver.__get_port_stats(port_id, self.stats)

    def logPortStats(self, port_id):
        if self.stats is None:
            main.log.error("No stats saved!")
            return None
        main.log.info("Statistics for port {}: {}".format(
            port_id, TrexClientDriver.__get_readable_port_stats(
                self.stats.get(port_id))))

    # From ptf/test/common/ptf_runner.py
    def __set_up_trex_server(self, trex_daemon_client, trex_address,
                             trex_config,
                             force_restart):
        try:
            main.log.info("Pushing Trex config %s to the server" % trex_config)
            if not trex_daemon_client.push_files(trex_config):
                main.log.error("Unable to push %s to Trex server" % trex_config)
                return False

            if force_restart:
                main.log.info("Restarting TRex")
                trex_daemon_client.kill_all_trexes()
                time.sleep(1)

            if not trex_daemon_client.is_idle():
                main.log.info("The Trex server process is running")
                main.log.warn(
                    "A Trex server process is still running, "
                    + "use --force-restart to kill it if necessary."
                )
                return False

            trex_config_file_on_server = TREX_FILES_DIR + os.path.basename(
                trex_config)
            trex_daemon_client.start_stateless(cfg=trex_config_file_on_server)
        except ConnectionRefusedError:
            main.log.error(
                "Unable to connect to server %s.\nDid you start the Trex daemon?" % trex_address)
            return False

        return True

    def __create_latency_stats_stream(self, pkt, pg_id,
                                      name=None,
                                      l1_bps=None,
                                      percentage=None,
                                      isg=0):
        assert (percentage is None and l1_bps is not None) or (
                percentage is not None and l1_bps is None)
        return STLStream(
            name=name,
            packet=STLPktBuilder(pkt=pkt),
            mode=STLTXCont(bps_L1=l1_bps, percentage=percentage),
            isg=isg,
            flow_stats=STLFlowLatencyStats(pg_id=pg_id)
        )

    def __create_background_stream(self, pkt, name=None, percentage=None,
                                   l1_bps=None):
        assert (percentage is None and l1_bps is not None) or (
                percentage is not None and l1_bps is None)
        return STLStream(
            name=name,
            packet=STLPktBuilder(pkt=pkt),
            mode=STLTXCont(bps_L1=l1_bps, percentage=percentage)
        )

    # Multiplier for data rates
    K = 1000
    M = 1000 * K
    G = 1000 * M

    def __monitor_port_stats(self, target_tx_per_port, num_samples=4,
                             ramp_up_timeout=5, time_interval=1, min_tx_bps_margin=0.95):
        """
        List some port stats continuously while traffic is active and verify that
        the generated amount traffic is the expected one

        :param target_tx_per_port: Traffic to be generated per port
        :param time_interval: Interval between read
        :param num_samples: Number of samples of statistics from each monitored ports
        :param ramp_up_timeout: how many seconds to wait before TRex can reach the target TX rate
        :return: Statistics read while traffic is active, or empty result if no
                 target_tx_per_port provided.
        """

        ports = target_tx_per_port.keys()
        local_gen_traffic_per_port = copy.deepcopy(target_tx_per_port)
        results = {
            port_id: {"rx_bps": [], "tx_bps": [], "rx_pps": [], "tx_pps": []}
            for port_id in ports
        }
        results["duration"] = []

        if len(ports) == 0:
            return results

        start_time = time.time()
        prev = {
            port_id: {
                "opackets": 0,
                "ipackets": 0,
                "obytes": 0,
                "ibytes": 0,
                "time": start_time,
            }
            for port_id in ports
        }

        time.sleep(time_interval)
        while self.trex_client.is_traffic_active():
            stats = self.trex_client.get_stats(ports=ports)
            sample_time = time.time()
            elapsed = sample_time - start_time
            if not stats:
                break

            main.log.debug(
                "\nTRAFFIC RUNNING {:.2f} SEC".format(elapsed))
            main.log.debug(
                "{:^4} | {:<10} | {:<10} | {:<10} | {:<10} |".format(
                    "Port", "RX bps", "TX bps", "RX pps", "TX pps"
                )
            )
            main.log.debug(
                "----------------------------------------------------------")

            for (tx_port, target_tx_rate) in local_gen_traffic_per_port.items():
                opackets = stats[tx_port]["opackets"]
                ipackets = stats[tx_port]["ipackets"]
                obytes = stats[tx_port]["obytes"]
                ibytes = stats[tx_port]["ibytes"]
                time_diff = sample_time - prev[tx_port]["time"]

                rx_bps = 8 * (ibytes - prev[tx_port]["ibytes"]) / time_diff
                tx_bps = 8 * (obytes - prev[tx_port]["obytes"]) / time_diff
                rx_pps = ipackets - prev[tx_port]["ipackets"] / time_diff
                tx_pps = opackets - prev[tx_port]["opackets"] / time_diff

                main.log.debug(
                    "{:^4} | {:<10} | {:<10} | {:<10} | {:<10} |".format(
                        tx_port,
                        TrexClientDriver.__to_readable(rx_bps, "bps"),
                        TrexClientDriver.__to_readable(tx_bps, "bps"),
                        TrexClientDriver.__to_readable(rx_pps, "pps"),
                        TrexClientDriver.__to_readable(tx_pps, "pps"),
                    )
                )

                results["duration"].append(sample_time - start_time)
                results[tx_port]["rx_bps"].append(rx_bps)
                results[tx_port]["tx_bps"].append(tx_bps)
                results[tx_port]["rx_pps"].append(rx_pps)
                results[tx_port]["tx_pps"].append(tx_pps)

                prev[tx_port]["opackets"] = opackets
                prev[tx_port]["ipackets"] = ipackets
                prev[tx_port]["obytes"] = obytes
                prev[tx_port]["ibytes"] = ibytes
                prev[tx_port]["time"] = sample_time

                if target_tx_rate is not None:
                    if tx_bps < (target_tx_rate * min_tx_bps_margin):
                        if elapsed > ramp_up_timeout:
                            self.trex_client.stop(ports=ports)
                            utilities.assert_equal(
                                expect=True, actual=False,
                                onpass="Should never reach this",
                                onfail="TX port ({}) did not reach or sustain min sending rate ({})".format(
                                    tx_port, target_tx_rate)
                            )
                            return {}
                        else:
                            results[tx_port]["rx_bps"].pop()
                            results[tx_port]["tx_bps"].pop()
                            results[tx_port]["rx_pps"].pop()
                            results[tx_port]["tx_pps"].pop()

                    if len(results[tx_port]["tx_bps"]) == num_samples:
                        # Stop monitoring ports for which we have enough samples
                        del local_gen_traffic_per_port[tx_port]

            if len(local_gen_traffic_per_port) == 0:
                # Enough samples for all ports
                utilities.assert_equal(
                    expect=True, actual=True,
                    onpass="Enough samples have been generated",
                    onfail="Should never reach this"
                )
                return results

            time.sleep(time_interval)
            main.log.debug("")

        utilities.assert_equal(
            expect=True, actual=True,
            onpass="Traffic sent correctly",
            onfail="Should never reach this"
        )
        return results

    @staticmethod
    def __to_readable(src, unit="bps"):
        """
        Convert number to human readable string.
        For example: 1,000,000 bps to 1Mbps. 1,000 bytes to 1KB

        :parameters:
            src : int
                the original data
            unit : str
                the unit ('bps', 'pps', or 'bytes')
        :returns:
            A human readable string
        """
        if src < 1000:
            return "{:.1f} {}".format(src, unit)
        elif src < 1000000:
            return "{:.1f} K{}".format(src / 1000, unit)
        elif src < 1000000000:
            return "{:.1f} M{}".format(src / 1000000, unit)
        else:
            return "{:.1f} G{}".format(src / 1000000000, unit)

    @staticmethod
    def __get_readable_port_stats(port_stats):
        opackets = port_stats.get("opackets", 0)
        ipackets = port_stats.get("ipackets", 0)
        obytes = port_stats.get("obytes", 0)
        ibytes = port_stats.get("ibytes", 0)
        oerrors = port_stats.get("oerrors", 0)
        ierrors = port_stats.get("ierrors", 0)
        tx_bps = port_stats.get("tx_bps", 0)
        tx_pps = port_stats.get("tx_pps", 0)
        tx_bps_L1 = port_stats.get("tx_bps_L1", 0)
        tx_util = port_stats.get("tx_util", 0)
        rx_bps = port_stats.get("rx_bps", 0)
        rx_pps = port_stats.get("rx_pps", 0)
        rx_bps_L1 = port_stats.get("rx_bps_L1", 0)
        rx_util = port_stats.get("rx_util", 0)
        return """
        Output packets: {}
        Input packets: {}
        Output bytes: {} ({})
        Input bytes: {} ({})
        Output errors: {}
        Input errors: {}
        TX bps: {} ({})
        TX pps: {} ({})
        L1 TX bps: {} ({})
        TX util: {}
        RX bps: {} ({})
        RX pps: {} ({})
        L1 RX bps: {} ({})
        RX util: {}""".format(
            opackets,
            ipackets,
            obytes,
            TrexClientDriver.__to_readable(obytes, "Bytes"),
            ibytes,
            TrexClientDriver.__to_readable(ibytes, "Bytes"),
            oerrors,
            ierrors,
            tx_bps,
            TrexClientDriver.__to_readable(tx_bps),
            tx_pps,
            TrexClientDriver.__to_readable(tx_pps, "pps"),
            tx_bps_L1,
            TrexClientDriver.__to_readable(tx_bps_L1),
            tx_util,
            rx_bps,
            TrexClientDriver.__to_readable(rx_bps),
            rx_pps,
            TrexClientDriver.__to_readable(rx_pps, "pps"),
            rx_bps_L1,
            TrexClientDriver.__to_readable(rx_bps_L1),
            rx_util,
        )

    @staticmethod
    def __get_port_stats(port, stats):
        """
        :param port: int
        :param stats:
        :return:
        """
        port_stats = stats.get(port)
        return PortStats(
            tx_packets=port_stats.get("opackets", 0),
            rx_packets=port_stats.get("ipackets", 0),
            tx_bytes=port_stats.get("obytes", 0),
            rx_bytes=port_stats.get("ibytes", 0),
            tx_errors=port_stats.get("oerrors", 0),
            rx_errors=port_stats.get("ierrors", 0),
            tx_bps=port_stats.get("tx_bps", 0),
            tx_pps=port_stats.get("tx_pps", 0),
            tx_bps_L1=port_stats.get("tx_bps_L1", 0),
            tx_util=port_stats.get("tx_util", 0),
            rx_bps=port_stats.get("rx_bps", 0),
            rx_pps=port_stats.get("rx_pps", 0),
            rx_bps_L1=port_stats.get("rx_bps_L1", 0),
            rx_util=port_stats.get("rx_util", 0),
        )

    @staticmethod
    def __get_latency_stats(pg_id, stats):
        """
        :param pg_id: int
        :param stats:
        :return:
        """

        lat_stats = stats["latency"].get(pg_id)
        lat = lat_stats["latency"]
        # Estimate latency percentiles from the histogram.
        l = list(lat["histogram"].keys())
        l.sort()
        all_latencies = []
        for sample in l:
            range_start = sample
            if range_start == 0:
                range_end = 10
            else:
                range_end = range_start + pow(10, (len(str(range_start)) - 1))
            val = lat["histogram"][sample]
            # Assume whole the bucket experienced the range_end latency.
            all_latencies += [range_end] * val
        q = [50, 75, 90, 99, 99.9, 99.99, 99.999]
        # Prevent exception if we have no latency histogram
        percentiles = np.percentile(all_latencies, q) if len(all_latencies) > 0 else [sys.maxint] * len(q)

        ret = LatencyStats(
            pg_id=pg_id,
            jitter=lat["jitter"],
            average=lat["average"],
            total_max=lat["total_max"],
            total_min=lat["total_min"],
            last_max=lat["last_max"],
            histogram=lat["histogram"],
            dropped=lat_stats["err_cntrs"]["dropped"],
            out_of_order=lat_stats["err_cntrs"]["out_of_order"],
            duplicate=lat_stats["err_cntrs"]["dup"],
            seq_too_high=lat_stats["err_cntrs"]["seq_too_high"],
            seq_too_low=lat_stats["err_cntrs"]["seq_too_low"],
            percentile_50=percentiles[0],
            percentile_75=percentiles[1],
            percentile_90=percentiles[2],
            percentile_99=percentiles[3],
            percentile_99_9=percentiles[4],
            percentile_99_99=percentiles[5],
            percentile_99_999=percentiles[6],
        )
        return ret

    @staticmethod
    def __get_readable_latency_stats(stats):
        """
        :param stats: LatencyStats
        :return:
        """
        histogram = ""
        # need to listify in order to be able to sort them.
        l = list(stats.histogram.keys())
        l.sort()
        for sample in l:
            range_start = sample
            if range_start == 0:
                range_end = 10
            else:
                range_end = range_start + pow(10, (len(str(range_start)) - 1))
            val = stats.histogram[sample]
            histogram = (
                    histogram
                    + "\n        Packets with latency between {0:>5} us and {1:>5} us: {2:>10}".format(
                range_start, range_end, val
            )
            )

        return """
        Latency info for pg_id {}
        Dropped packets: {}
        Out-of-order packets: {}
        Sequence too high packets: {}
        Sequence too low packets: {}
        Maximum latency: {} us
        Minimum latency: {} us
        Maximum latency in last sampling period: {} us
        Average latency: {} us
        50th percentile latency: {} us
        75th percentile latency: {} us
        90th percentile latency: {} us
        99th percentile latency: {} us
        99.9th percentile latency: {} us
        99.99th percentile latency: {} us
        99.999th percentile latency: {} us
        Jitter: {} us
        Latency distribution histogram: {}
        """.format(stats.pg_id, stats.dropped, stats.out_of_order,
                   stats.seq_too_high, stats.seq_too_low, stats.total_max,
                   stats.total_min, stats.last_max, stats.average,
                   stats.percentile_50, stats.percentile_75,
                   stats.percentile_90,
                   stats.percentile_99, stats.percentile_99_9,
                   stats.percentile_99_99,
                   stats.percentile_99_999, stats.jitter, histogram)

    @staticmethod
    def __get_flow_stats(pg_id, stats):
        """
        :param pg_id: int
        :param stats:
        :return:
        """
        FlowStats = collections.namedtuple(
            "FlowStats",
            ["pg_id", "tx_packets", "rx_packets", "tx_bytes", "rx_bytes", ],
        )
        flow_stats = stats["flow_stats"].get(pg_id)
        ret = FlowStats(
            pg_id=pg_id,
            tx_packets=flow_stats["tx_pkts"]["total"],
            rx_packets=flow_stats["rx_pkts"]["total"],
            tx_bytes=flow_stats["tx_bytes"]["total"],
            rx_bytes=flow_stats["rx_bytes"]["total"],
        )
        return ret

    @staticmethod
    def __get_readable_flow_stats(stats):
        """
        :param stats: FlowStats
        :return:
        """
        return """Flow info for pg_id {}
        TX packets: {}
        RX packets: {}
        TX bytes: {}
        RX bytes: {}""".format(stats.pg_id, stats.tx_packets,
                               stats.rx_packets, stats.tx_bytes,
                               stats.rx_bytes)
