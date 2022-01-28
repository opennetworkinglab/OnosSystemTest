class QOS:

    def __init__(self):
        self.default = ''

    def CASE1(self, main):
        main.case("Leaf Edge with Mobile Traffic Classification")
        # Leaf-Edge-Mobile
        # Attach 2 UEs with different TC
        # Generate traffic with Trex for the two UEs
        # --> no packet drop on RT flow, reasonable latency on RT flow
        try:
            from tests.USECASE.SegmentRouting.QOS.dependencies.QOSTest import \
                QOSTest
        except ImportError as e:
            main.log.error("Import not found. Exiting the test")
            main.log.error(e)
            main.cleanAndExit()
        test = QOSTest()
        test.runTest(
            main,
            test_idx=1,
            n_switches=int(main.params["TOPO"]["switchNum"])
        )

    def CASE2(self, main):
        main.case("Leaf Pair Link with Mobile Traffic Classification")
        # Leaf Infra Mobile Traffic
        # Attach 2 UEs with different TC
        # Generate traffic with TRex from UEs towards PDN, generating congestion
        # on the 40Gbps pair link
        # --> no packet drop on RT flow, reasonable latency on RT flow
        try:
            from tests.USECASE.SegmentRouting.QOS.dependencies.QOSTest import \
                QOSTest
        except ImportError as e:
            main.log.error("Import not found. Exiting the test")
            main.log.error(e)
            main.cleanAndExit()
        test = QOSTest()
        test.runTest(
            main,
            test_idx=2,
            n_switches=int(main.params["TOPO"]["switchNum"])
        )
