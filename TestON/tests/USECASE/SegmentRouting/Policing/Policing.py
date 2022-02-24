class Policing:

    def __init__(self):
        self.default = ''

    def CASE1(self, main):
        main.case("Session level QER")
        try:
            from tests.USECASE.SegmentRouting.Policing.dependencies.PolicingTest import \
                PolicingTest
        except ImportError as e:
            main.log.error("Import not found. Exiting the test")
            main.log.error(e)
            main.cleanAndExit()
        test = PolicingTest()
        test.runTest(
            main,
            test_idx=1
        )

    def CASE2(self, main):
        main.case("Application level QER")
        try:
            from tests.USECASE.SegmentRouting.Policing.dependencies.PolicingTest import \
                PolicingTest
        except ImportError as e:
            main.log.error("Import not found. Exiting the test")
            main.log.error(e)
            main.cleanAndExit()
        test = PolicingTest()
        test.runTest(
            main,
            test_idx=2
        )
