class QOSNonMobile:

    def __init__(self):
        self.default = ''

    def CASE1(self):
        main.case("Leaf Edge with NON-Mobile Traffic Classification")
        try:
            from tests.USECASE.SegmentRouting.QOSNonMobile.dependencies.QOSNonMobileTest import QOSNonMobileTest
        except ImportError as e:
            main.log.error("Import not found. Exiting the test")
            main.log.error(e)
            main.cleanAndExit()

        test = QOSNonMobileTest()
        test.runTest(main, test_idx=1, n_switches=2)

    def CASE2(self):
        main.case("Leaf Pair Link with NON-Mobile Traffic Classification")
        try:
            from tests.USECASE.SegmentRouting.QOSNonMobile.dependencies.QOSNonMobileTest import QOSNonMobileTest
        except ImportError as e:
            main.log.error("Import not found. Exiting the test")
            main.log.error(e)
            main.cleanAndExit()

        test = QOSNonMobileTest()
        test.runTest(main, test_idx=2, n_switches=2)
