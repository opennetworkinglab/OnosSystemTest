class QOS:

    def __init__(self):
        self.default = ''

    def CASE1(self, main):
        # Leaf-Edge-Mobile
        # Attach 2 UEs with different QFI
        # Generate traffic with Trex for the two UEs
        # --> no packet drop on RT flow, reasonable latency on RT flow
        try:
            from tests.USECASE.SegmentRouting.dependencies.up4 import UP4
            from tests.USECASE.SegmentRouting.dependencies.trex import Trex
            from tests.USECASE.SegmentRouting.dependencies.Testcaselib import \
                Testcaselib as run
            import json
        except ImportError as e:
            main.log.error("Import not found. Exiting the test")
            main.log.error(e)
            main.cleanAndExit()

        run.initTest(main)
        main.log.info(main.Cluster.numCtrls)
        main.Cluster.setRunningNode(3)
        run.installOnos(main, skipPackage=True, cliSleep=5)

        main.step("Start P4rt client and setup TRex")
        up4 = UP4()
        trex = Trex()
        # Get the P4RT client connected to UP4 in the first available ONOS instance
        up4.setup(main.Cluster.active(0).p4rtUp4)
        trex.setup(main.TRexClient)

        main.step("Attach UEs")
        up4.attachUes()

        # Load traffic config for the current test case
        main.step("Load test JSON config")
        cfgFile = main.configPath + "/tests/" + "leaf_edge_mobile.json"
        with open(cfgFile) as cfg:
            testCfg = json.load(cfg)

        main.step("Send traffic with TRex")
        for flow in testCfg["flows"]:
            trex.createFlow(flow)
        trex.sendAndReceiveTraffic(testCfg["duration"])

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
                main.step("{}: Assert 99.9 Percentile Latency".format(flow))
                trex.assert99_9PercentileLatency(flow)

        main.step("Detach UEs")
        up4.detachUes()

        main.step("Teardown")
        trex.teardown()
        up4.teardown()
        run.cleanup(main)
