# SPDX-FileCopyrightText: Copyright 2021-present Open Networking Foundation.
# SPDX-License-Identifier: GPL-2.0-or-later

class INT:

    def __init__(self):
        self.default = ""

    def CASE1 (self, main):
        main.case("Send ping packets from one host to another host and check flows from DeepInsight")
        import time
        import socket
        from core import utilities
        from tests.USECASE.SegmentRouting.INT.dependencies.IntTest import IntTest
        main.cfgName = "CASE1"

        main.step("Setting up the test")
        intTest = IntTest(scapy=True)
        intTest.setUpTest(main)

        main.step("Setting up hosts and variables")
        srcIfaceName = main.h1.interfaces[0]["name"]
        srcMac = main.h1.getMac(srcIfaceName)
        dstMac = main.params.get("routerMac", "00:00:00:00:00:00")
        srcIp = main.h1.interfaces[0]['ips'][0]
        dstIp = main.h2.interfaces[0]['ips'][0]
        srcPort = 2000
        dstPort = 8888

        main.step("Send ping packets from h1 to h2")
        startTimeMs = (time.time() - 5) * 1000
        pkt = """(
            Ether(src="{}", dst="{}") /
            IP(src="{}", dst="{}") /
            UDP(sport={}, dport={}) /
            ("A"*30)
        )""".format(srcMac, dstMac, srcIp, dstIp, srcPort, dstPort)
        # Send multiple packets incase the server or DeepInsight drop the report accidently
        # FIXME: Find the root cause, might be misconfiguration or Linux(e.g., rp_filter?) issue.
        for _ in range(0, 5):
            main.h1.sendPacket(iface=srcIfaceName, packet=pkt)
        endTimeMs = (time.time() + 5) * 1000

        main.step("Checking total number of flow reports from DeepInsight")
        def getFiveTupleCount(*args, **kwargs):
            flows = main.DeepInsight.getFlows(
                startTimeMs=startTimeMs,
                endTimeMs=endTimeMs,
                srcIp=srcIp,
                dstIp=dstIp,
                ipProto=socket.IPPROTO_UDP
            )
            if "FiveTupleCount" in flows:
                return flows["FiveTupleCount"]
            else:
                return 0
        # Need to wait few seconds until DeepInsight database updated.
        fiveTupleCount = utilities.retry(
            f=getFiveTupleCount,
            retValue=0,
            attempts=60,
        )

        utilities.assert_equals(
            expect=1, actual=fiveTupleCount,
            onpass="Got 1 flow report from DeepInsight as expected.",
            onfail="Got %d flow reports from DeepInsight (expect 1)" % (fiveTupleCount)
        )

        main.step("Clean up the test")
        intTest.cleanUp(main)

    def CASE2 (self, main):
        main.case("Send a packet with invalid VLAN from one host to another host and check if DeepInsight receives drop reports")
        import time
        import socket
        from core import utilities
        from tests.USECASE.SegmentRouting.INT.dependencies.IntTest import IntTest
        main.cfgName = "CASE2"

        main.step("Setting up the test")
        intTest = IntTest(scapy=True)
        intTest.setUpTest(main)

        main.step("Setting up hosts and variables")
        srcIfaceName = main.h1.interfaces[0]["name"]
        dstIfaceName = main.h2.interfaces[0]["name"]
        srcMac = main.h1.getMac(srcIfaceName)
        dstMac = main.params.get("routerMac", "00:00:00:00:00:00")
        srcIp = main.h1.interfaces[0]['ips'][0]
        dstIp = main.h2.interfaces[0]['ips'][0]
        srcPort = 2000
        dstPort = 8888

        main.step("Sending a packet with invalid VLAN ID from h1")
        startTimeMs = (time.time() - 5) * 1000
        pkt = """(
            Ether(src="{}", dst="{}") /
            Dot1Q(vlan=4093) /
            IP(src="{}", dst="{}") /
            UDP(sport={}, dport={}) /
            ("A"*30)
        )""".format(srcMac, dstMac, srcIp, dstIp, srcPort, dstPort)
        # Send multiple packets incase the server or DeepInsight drop the report accidently
        # FIXME: Find the root cause, might be misconfiguration or Linux(e.g., rp_filter?) issue.
        for _ in range(0, 5):
            main.h1.sendPacket(iface=srcIfaceName, packet=pkt)
        endTimeMs = (time.time() + 5) * 1000

        main.step("Checking drop report from DeepInsight")
        def getDropAnomalies(*args, **kwargs):
            return main.DeepInsight.getAnomalyRecords(
                startTime=startTimeMs,
                endTime=endTimeMs,
                srcIp=srcIp,
                dstIp=dstIp,
                srcPort=srcPort,
                dstPort=dstPort,
                ipProto=socket.IPPROTO_UDP,
                anomalyType="packet_drop",
           )

        # Need to wait few seconds until DeepInsight database updated.
        dropAnomalies = utilities.retry(
            f=getDropAnomalies,
            retValue=[[]],
            attempts=60,
        )

        utilities.assert_lesser(
            expect=0, actual=len(dropAnomalies),
            onpass="Got %d drop anomaly from DeepInsight." % (len(dropAnomalies)),
            onfail="Got no drop anomaly from DeepInsight."
        )

        main.step("Checking drop reason from the report")
        try:
            dropAnomaly = dropAnomalies[0]
            dropReason = dropAnomaly["DropReason"]
        except IndexError:
            main.log.warn( "No drop report was found" )
            dropAnomaly = None
            dropReason = None

        # DROP_REASON_PORT_VLAN_MAPPING_MISS = 55
        utilities.assert_equals(
            expect=55, actual=dropReason,
            onpass="Got drop reason '55' as expected.",
            onfail="Got drop reason '%d', expect '55'." % (dropReason)
        )

        main.step("Clean up the test")
        intTest.cleanUp(main)

    def CASE3 (self, main):
        main.case("Send a packet with IP TTL value 1 from one host to another host and check if DeepInsight receives drop reports")
        import time
        import socket
        from core import utilities
        from tests.USECASE.SegmentRouting.INT.dependencies.IntTest import IntTest
        main.cfgName = "CASE3"

        main.step("Setting up the test")
        intTest = IntTest(scapy=True)
        intTest.setUpTest(main)

        main.step("Setting up hosts and variables")
        srcIfaceName = main.h1.interfaces[0]["name"]
        srcMac = main.h1.getMac(srcIfaceName)
        dstMac = main.params.get("routerMac", "00:00:00:00:00:00")
        srcIp = main.h1.interfaces[0]['ips'][0]
        dstIp = main.h2.interfaces[0]['ips'][0]
        srcPort = 3000
        dstPort = 8888

        main.step("Sending a packet with IP TTL value 1 from h1")
        startTimeMs = (time.time() - 5) * 1000
        pkt = """(
            Ether(src="{}", dst="{}") /
            IP(src="{}", dst="{}", ttl=1) /
            UDP(sport={}, dport={}) /
            ("A"*30)
        )""".format(srcMac, dstMac, srcIp, dstIp, srcPort, dstPort)
        # Send multiple packets incase the server or DeepInsight drop the report accidently
        # FIXME: Find the root cause, might be misconfiguration or Linux(e.g., rp_filter?) issue.
        for _ in range(0, 5):
            main.h1.sendPacket(iface=srcIfaceName, packet=pkt)
        endTimeMs = (time.time() + 5) * 1000

        main.step("Checking drop report from DeepInsight")
        def getDropAnomalies(*args, **kwargs):
            return main.DeepInsight.getAnomalyRecords(
                startTime=startTimeMs,
                endTime=endTimeMs,
                srcIp=srcIp,
                dstIp=dstIp,
                srcPort=srcPort,
                dstPort=dstPort,
                ipProto=socket.IPPROTO_UDP,
                anomalyType="packet_drop",
            )

        # Need to wait few seconds until DeepInsight database updated.
        dropAnomalies = utilities.retry(
            f=getDropAnomalies,
            retValue=[[]],
            attempts=60,
        )

        utilities.assert_lesser(
            expect=0, actual=len(dropAnomalies),
            onpass="Got %d drop anomaly from DeepInsight." % (len(dropAnomalies)),
            onfail="Got no drop anomaly from DeepInsight."
        )

        main.step("Checking drop reason from report")
        try:
            dropAnomaly = dropAnomalies[0]
            dropReason = dropAnomaly["DropReason"]
        except IndexError:
            main.log.warn( "No drop report was found" )
            dropAnomaly = None
            dropReason = None
        # DROP_REASON_IP_TTL_ZERO = 26
        utilities.assert_equals(
            expect=26, actual=dropReason,
            onpass="Got drop reason '26' as expected.",
            onfail="Got drop reason '%d', expect '26'." % (dropReason)
        )

        main.step("Clean up the test")
        intTest.cleanUp(main)

    def CASE4(self, main):
        main.case("Generate traffic at high rate and expect queue congestion reports in DeepInsight")
        from core import utilities
        import time
        from tests.USECASE.SegmentRouting.INT.dependencies.IntTest import IntTest
        from tests.USECASE.SegmentRouting.dependencies.trex import Trex
        main.cfgName = 'CASE4'

        main.step("Setting up the test")
        intTest = IntTest(scapy=False)
        intTest.setUpTest(main)
        dstIp = main.params["TREX"]["flows"]["FLOW1"]["packet"]["ip_dst"]

        main.step("Set up TRex client")
        trex = Trex()
        trex.setup(main.TRexClient)

        # See SRpairedLeaves.param for the detail of each flow.
        main.step("Reset queue report filter")
        # Here we are using a low-latency(no congestion) traffic to reset the queue.
        # report filter.
        trex.createFlow("RESET_QUEUE_REPORT_FILTER")
        trex.sendAndReceiveTraffic(5)
        trex.resetFlows()
        main.step("Generating traffic")
        startTimeMs = (time.time() - 5) * 1000
        trex.createFlow("FLOW1")
        trex.createFlow("FLOW2")
        trex.sendAndReceiveTraffic(10)
        endTimeMs = (time.time() + 5) * 1000

        main.step("Checking queue report from DeepInsight")
        def getQueueAnomaly(*args, **kwargs):
            return main.DeepInsight.getAnomalyRecords(
                startTime=startTimeMs,
                endTime=endTimeMs,
                dstIp=dstIp,
                anomalyType="congested_flow",
            )

        # Need to wait few seconds until DeepInsight database updated.
        queueAnomalies = utilities.retry(
            f=getQueueAnomaly,
            retValue=[[]],
            attempts=30,
        )

        # We should get at least two congestion records
        utilities.assert_lesser(
            expect=2, actual=len(queueAnomalies),
            onpass="Got %d anomalies with 'congested_flow' type as expcted." % (len(queueAnomalies)),
            onfail="Did not get any anomaly with 'congested_flow' type."
        )

        main.step("Clean up the test")
        trex.teardown()
        intTest.cleanUp(main)
