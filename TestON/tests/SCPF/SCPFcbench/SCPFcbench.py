# ScaleOutTemplate --> CbenchBM
#
# CASE1 starts number of nodes specified in param file
#
# cameron@onlab.us

import sys
import os
import os.path


class SCPFcbench:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):

        import time
        import os
        global init
        main.case( "pre-condition for cbench test." )

        try:
            if not isinstance( init, bool ):
                init = False
        except NameError:
            init = False

        # -- INIT SECTION, ONLY RUNS ONCE -- #
        if not init:
            init = True
            try:
                from tests.dependencies.ONOSSetup import ONOSSetup
                main.testSetUp = ONOSSetup()
            except ImportError:
                main.log.error( "ONOSSetup not found. exiting the test" )
                main.cleanAndExit()
            main.testSetUp.envSetupDescription()
            stepResult = main.FALSE
            try:
                # Load values from params file
                BENCHIp = main.params[ 'BENCH' ][ 'ip1' ]
                BENCHUser = main.params[ 'BENCH' ][ 'user' ]
                CBENCHuser = main.params[ 'CBENCH' ][ 'user' ]
                MN1Ip = os.environ[ main.params[ 'MN' ][ 'ip1' ] ]
                main.maxNodes = int( main.params[ 'availableNodes' ] )
                main.cellName = main.params[ 'ENV' ][ 'cellName' ]
                main.apps = main.params[ 'ENV' ][ 'cellApps' ]
                main.scale = ( main.params[ 'SCALE' ] ).split( "," )

                stepResult = main.testSetUp.envSetup()
            except Exception as e:
                main.testSetUp.envSetupException( e )
            main.testSetUp.evnSetupConclusion( stepResult )
            main.commit = ( main.commit.split( " " ) )[ 1 ]
        # -- END OF INIT SECTION --#

        main.testSetUp.ONOSSetUp( MN1Ip, main.Cluster, True,
                                  cellName=main.cellName )

        for i in range( 5 ):
            main.ONOSbench.onosCfgSet( main.Cluster.active( 0 ).ipAddress, "org.onosproject.fwd.ReactiveForwarding", "packetOutOnly true" )
            time.sleep( 5 )
            main.ONOSbench.handle.sendline( "onos $OC1 cfg get|grep packetOutOnly" )
            main.ONOSbench.handle.expect( ":~" )
            check = main.ONOSbench.handle.before
            if "value=true" in check:
                main.log.info( "cfg set successful" )
                stepResult = main.TRUE
                break
            if i == 4:
                main.log.info( "Cfg set failed" )
                stepResult = main.FALSE
            else:
                time.sleep( 5 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully configure onos for cbench test ",
                                 onfail="Failed to configure onos for cbench test" )

    def CASE2( self, main ):
        main.case( "Running Cbench" )
        main.step( "Issuing cbench commands and grab returned results" )
        validFlag = False
        cbenchCMD = main.params[ 'TEST' ][ 'cbenchCMD' ]
        mode = main.params[ 'TEST' ][ 'mode' ]
        if mode != "t":
            mode = " "

        runCbench = ( "ssh " + CBENCHuser + "@" + main.Cluster.active( 0 ).ipAddress + " " + cbenchCMD + mode )
        main.ONOSbench.handle.sendline( runCbench )
        time.sleep( 30 )
        main.ONOSbench.handle.expect( ":~" )
        output = main.ONOSbench.handle.before
        main.log.info( output )

        output = output.splitlines()
        for line in output:
            if "RESULT: " in line:
                validFlag = True
                print line
                resultLine = line.split( " " )
                for word in resultLine:
                    if word == "min/max/avg/stdev":
                        resultsIndex = resultLine.index( word )
                        print resultsIndex
                        break

                finalDataString = resultLine[ resultsIndex + 2 ]
                print finalDataString
                finalDataList = finalDataString.split( "/" )
                avg = finalDataList[ 2 ]
                stdev = finalDataList[ 3 ]

                main.log.info( "Average: \t\t\t" + avg )
                main.log.info( "Standard Deviation: \t" + stdev )

                try:
                    dbFileName = "/tmp/CbenchDB"
                    dbfile = open( dbFileName, "w+" )
                    temp = "'" + main.commit + "',"
                    temp += "'" + mode + "',"
                    temp += "'" + avg + "',"
                    temp += "'" + stdev + "'\n"
                    dbfile.write( temp )
                    dbfile.close()
                    main.ONOSbench.logReport( main.Cluster.active( 0 ).ipAddress, [ "ERROR", "WARNING", "EXCEPT" ], outputMode="d" )
                except IOError:
                    main.log.warn( "Error opening " + dbFileName + " to write results." )

                stepResult = main.TRUE
                break
        if not validFlag:
            main.log.warn( "Cbench Test produced no valid results!!!!" )
            stepResult = main.FALSE

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully tested onos for cbench. ",
                                 onfail="Failed to obtain valid onos cbench result!" )
