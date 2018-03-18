class SRMulticast:
    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        """
        Sets up 3 ONOS instance
        Start 2x2 topology
        """
        try:
            from tests.USECASE.SegmentRouting.SRMulticast.dependencies.SRMulticastTest import SRMulticastTest
        except ImportError:
            main.log.error( "SRMulticastTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRMulticastTest()
        main.funcs.runTest( main,
                            test_idx=1,
                            topology='2x2',
                            onosNodes=1,
                            description="TBD" )
