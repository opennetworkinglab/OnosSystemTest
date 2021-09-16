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
        up4 = UP4()
        # Get the P4RT client connected to UP4 in the first available ONOS instance
        up4.setup(main.Cluster.active(0).p4rtUp4)

        main.step("Attach UEs")
        up4.attachUes()

        # ------- Test Upstream traffic (enb->pdn)
        main.step("Test upstream traffic")
        up4.testUpstreamTraffic()

        # ------- Test Downstream traffic (pdn->enb)
        main.step("Test downstream traffic")
        up4.testDownstreamTraffic()

        main.step("Detach UEs")
        up4.detachUes()

        main.step("Stop scapy and p4rt client")
        up4.teardown()
        run.cleanup(main)
