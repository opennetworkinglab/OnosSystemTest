from tests.USECASE.SegmentRouting.dependencies.Testcaselib import \
    Testcaselib as run
from tests.USECASE.SegmentRouting.dependencies.trex import Trex
from tests.USECASE.SegmentRouting.dependencies.up4 import UP4
import json


class QOSTest:

    def runTest(self, main, test_idx, n_switches):
        run.initTest(main)
        main.log.info(main.Cluster.numCtrls)
        main.Cluster.setRunningNode(3)
        run.installOnos(main, skipPackage=True, cliSleep=5)

        main.step("Start P4rt client and setup TRex")
        # Use the first available ONOS instance CLI
        onos_cli = main.Cluster.active(0).CLI
        up4 = UP4()
        trex = Trex()
        # Get the P4RT client connected to UP4 in the first available ONOS instance
        up4.setup(main.Cluster.active(0).p4rtUp4, no_host=True)
        trex.setup(main.TRexClient)

        main.step("Program UPF entities via UP4")
        up4.attachUes()
        up4.verifyUp4Flow(onos_cli)

        # Load traffic config for the current test case
        main.step("Load test JSON config")
        cfgFile = main.configPath + "/tests/" + "CASE_%d.json" % test_idx
        with open(cfgFile) as cfg:
            testCfg = json.load(cfg)

        main.step("Send traffic with TRex")
        for flow in testCfg["flows"]:
            trex.createFlow(flow)
        results = trex.sendAndReceiveTraffic(testCfg["duration"])
        trex.verifyCongestion(
            results,
            multiplier=float(testCfg.get("multiplier", "1"))
        )

        main.step("Log port and flow stats")
        trex.logPortStats()
        for flow in testCfg["flows"]:
            trex.logFlowStats(flow)

        # Assert Flow Stats
        for flow in testCfg["flows"]:
            if trex.isFlowStats(flow):
                main.step("{}: Assert RX Packets".format(flow))
                trex.assertRxPackets(flow)
                main.step("{}: Assert Dropped Packets".format(flow))
                trex.assertDroppedPacket(flow)
                main.step("{}: Assert 90 Percentile Latency".format(flow))
                trex.assert90PercentileLatency(flow)
                main.step("{}: Assert 99.9 Percentile Latency".format(flow))
                trex.assert99_9PercentileLatency(flow)

        main.step("Remove UPF entities via UP4")
        up4.detachUes()
        up4.verifyNoUesFlow(onos_cli)

        main.step("Teardown")
        trex.teardown()
        up4.teardown()
        run.cleanup(main)
