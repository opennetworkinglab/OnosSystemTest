class Utils:
    def __init__( self ):
        self.default = ''

    def mininetCleanIntro( self ):
        main.log.report( "Stop Mininet" )

        main.case( "Stop Mininet" )
        main.caseExplanation = "Stopping the current mininet to start up fresh"

    def mininetCleanup( self, Mininet, timeout=5 ):
        main.step( "Stopping Mininet" )
        topoResult = Mininet.stopNet( timeout=timeout )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=topoResult,
                                 onpass="Successfully stopped mininet",
                                 onfail="Failed to stopped mininet" )
        return topoResult

    def copyKarafLog( self ):
        """
            Copy the karaf.log files after each testcase cycle
        """
        main.log.report( "Copy karaf logs" )
        main.case( "Copy karaf logs" )
        main.caseExplanation = "Copying the karaf logs to preserve them through" +\
                               "reinstalling ONOS"
        main.step( "Copying karaf logs" )
        stepResult = main.TRUE
        scpResult = main.TRUE
        copyResult = main.TRUE
        for i in range( main.numCtrls ):
            main.node = main.CLIs[ i ]
            ip = main.ONOSip[ i ]
            main.node.ip_address = ip
            scpResult = scpResult and main.ONOSbench.scp( main.node,
                                                          "/opt/onos/log/karaf.log",
                                                          "/tmp/karaf.log",
                                                          direction="from" )
            copyResult = copyResult and main.ONOSbench.cpLogsToDir( "/tmp/karaf.log", main.logdir,
                                                                    copyFileName=( "karaf.log.node{0}.cycle{1}".format(
                                                                        str( i + 1 ), str( main.cycle ) ) ) )
            if scpResult and copyResult:
                stepResult = main.TRUE and stepResult
            else:
                stepResult = main.FALSE and stepResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully copied remote ONOS logs",
                                 onfail="Failed to copy remote ONOS logs" )