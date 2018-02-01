
class SRRouting:
    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        """
        Tests routing between single-homed untagged host and single-homed
        untagged host residing on the same leaf.
        """

        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import SRRoutingTest

        SRRoutingTest.runTest( main,
                                test_idx = 1,
                                onosNodes = 3,
                                dhcp=0,
                                routers=0,
                                ipv4=1,
                                ipv6=0,
                                h1="h1v4",
                                h2="h2v4",
                                description = "Routing test for untagged to\
                              untagged single homed hosts residing on the same\
                              leaf")

