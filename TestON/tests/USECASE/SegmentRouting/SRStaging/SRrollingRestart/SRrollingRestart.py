class SRrollingRestart:
    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        main.case("Testing connections")
        main.persistentSetup = True

    def CASE2( self, main ):
        """
        Connect to Pod
        Perform rolling ONOS failure/recovery test
        Collect logs and analyze results
        """
        pass
