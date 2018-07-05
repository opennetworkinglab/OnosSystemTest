"""
Copyright 2017 Open Networking Foundation ( ONF )

Please refer questions to either the onos test mailing list at <onos-test@onosproject.org>,
the System Testing Plans and Results wiki page at <https://wiki.onosproject.org/x/voMg>,
or the System Testing Guide page at <https://wiki.onosproject.org/x/WYQg>

    TestON is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    ( at your option ) any later version.

    TestON is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with TestON.  If not, see <http://www.gnu.org/licenses/>.
"""
class SCPFmastershipFailoverLat:

    def __init__( self ):
        self.default = ''

    def CASE0( self, main ):
        import os
        import imp
        """
        - GIT
        - BUILDING ONOS
            Pull specific ONOS branch, then Build ONOS ono ONOS Bench.
            This step is usually skipped. Because in a Jenkins driven automated
            test env. We want Jenkins jobs to pull&build for flexibility to handle
            different versions of ONOS.
        - Construct tests variables
        """
        try:
            from tests.dependencies.ONOSSetup import ONOSSetup
            main.testSetUp = ONOSSetup()
        except ImportError:
            main.log.error( "ONOSSetup not found. exiting the test" )
            main.exit()
        main.testSetUp.envSetupDescription()
        stepResult = main.FALSE
        try:
            main.MN1Ip = main.params[ 'MN' ][ 'ip1' ]
            main.cellName = main.params[ 'ENV' ][ 'cellName' ]
            main.apps = main.params[ 'ENV' ][ 'cellApps' ]
            main.scale = ( main.params[ 'SCALE' ] ).split( "," )
            main.ofpRoleRequest = main.params[ 'TSHARK' ][ 'ofpRoleRequest' ]
            main.tsharkResultPath = main.params[ 'TSHARK' ][ 'tsharkResultPath' ]
            main.sampleSize = int( main.params[ 'TEST' ][ 'sampleSize' ] )
            main.warmUp = int( main.params[ 'TEST' ][ 'warmUp' ] )
            main.dbFileName = main.params[ 'DATABASE' ][ 'dbName' ]
            main.maxScale = int( main.params[ 'max' ] )
            main.timeout = int( main.params[ 'TIMEOUT' ][ 'timeout' ] )
            main.MNSleep = int( main.params[ 'SLEEP' ][ 'mininet' ] )
            main.recoverySleep = int( main.params[ 'SLEEP' ][ 'recovery' ] )
            main.debug = main.params[ 'TEST' ][ 'debug' ]
            main.failoverSleep = int( main.params[ 'SLEEP' ][ 'failover' ] )
            main.switchID = main.params[ 'SWITCH' ][ 'id' ]
            main.topologySwitchCount = main.params[ 'TOPOLOGY' ][ 'switchCount' ]
            main.topologyType = main.params[ 'TOPOLOGY' ][ 'type' ]
            main.nodeNumToKill = int( main.params[ 'KILL' ][ 'nodeNum' ] )
            main.failPercent = float( main.params[ 'TEST' ][ 'failPercent' ] )

            if main.debug == "True":
                main.debug = True
            else:
                main.debug = False

            stepResult = main.testSetUp.envSetup()
            main.log.info( "Create Database file " + main.dbFileName )
            resultsDB = open( main.dbFileName, "w+" )
            resultsDB.close()

        except Exception as e:
            main.testSetUp.envSetupException( e )
        main.testSetUp.evnSetupConclusion( stepResult )

    def CASE1( self, main ):
        # Clean up test environment and set up
        import time
        main.testSetUp.ONOSSetUp( main.Cluster, True,
                                  cellName=main.cellName, killRemoveMax=False )
        try:
            from tests.dependencies.utils import Utils
        except ImportError:
            main.log.error( "Utils not found exiting the test" )
            main.exit()
        try:
            main.Utils
        except ( NameError, AttributeError ):
            main.Utils = Utils()
        main.Utils.mininetCleanup( main.Mininet1 )

        main.step( "Starting up Mininet from command." )

        mnCmd = " mn " + " --topo " + main.topologyType + "," + main.topologySwitchCount
        for ctrl in main.Cluster.active():
            mnCmd += " --controller remote,ip=" + ctrl.ipAddress

        stepResult = main.Mininet1.startNet( mnCmd=mnCmd )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Mininet was set up correctly.",
                                 onfail="Mininet was NOT set up correctly." )

    def CASE2( self, main ):
        """
        Kill ONOS node, and measure the latency for INSTANCE_DEACTIVATED, MASTER_CHANGED, and role request
        ( tshark time ), then bring the node back up.
        """
        import time
        import datetime
        import numpy
        from tests.HA.dependencies.HA import HA

        main.HA = HA()

        main.latencyData = { 'kill_to_deactivation': [],
                             'deactivation_to_role_request': [] }

        main.failCounter = 0
        passingResult = True
        criticalError = False

        main.step( "Gathering data starting with "
                   + str( main.warmUp )
                   + " warm ups and a sample size of "
                   + str( main.sampleSize ) )

        for iteration in range( 0, main.sampleSize + main.warmUp ):

            main.log.info( "==========================================" )
            main.log.info( "================iteration:{}==============".format( str( iteration + 1 ) ) )

            ip_address = main.Cluster.active( 0 ).ipAddress
            strNodeNumToKill = str( main.nodeNumToKill )

            main.log.info( "Assigning mastership to ONOS node " + strNodeNumToKill )
            main.Cluster.active( 0 ).CLI.deviceRole( main.switchID, ip_address )

            main.log.info( "Sleeping for " + str( main.recoverySleep ) + " seconds..." )
            time.sleep( main.recoverySleep )
            mastershipCheck = main.Cluster.active( 0 ).CLI.getMaster( main.switchID ) == ip_address

            if not mastershipCheck:
                main.log.warn( "Mastership is NOT as expected." )

            with open( main.tsharkResultPath, "w" ) as tshark:
                tshark.write( "" )
            main.log.info( "Starting tshark capture." )
            main.ONOSbench.tsharkGrep( main.ofpRoleRequest, main.tsharkResultPath )
            time1 = time.time() * 1000.0

            # Kill an ONOS node
            main.log.info( "Killing ONOS node " + strNodeNumToKill + "." )
            killresult = main.ONOSbench.onosKill( ip_address )
            main.Cluster.runningNodes[ main.nodeNumToKill ].active = False

            # Stop an ONOS node
            main.log.info( "Stopping ONOS node " + strNodeNumToKill + "." )
            stopresult = main.ONOSbench.onosStop( ip_address )

            killStopResult = stopresult == killresult and True

            if not killStopResult:
                main.log.error( "ONOS node was NOT successfully stopped and killed." )
                criticalError = True

            time.sleep( main.failoverSleep )

            # Stop tshark and get times
            main.log.info( "Stopping tshark." )
            main.ONOSbench.tsharkStop()

            masterChangedLats = []
            instanceDeactivatedLats = []

            main.log.info( "Obtaining latencies from 'events' output." )
            for CLInum in range( 0, main.Cluster.numCtrls - 1 ):
                eventOutput = main.Cluster.active( CLInum ).CLI.events( args='-a' ).split( "\r\n" )
                for line in reversed( eventOutput ):
                    timestamp = line[ :23 ] if line[ 19 ] != '-' else line[ :19 ] + '.000'
                    if "INSTANCE_DEACTIVATED" in line and len( instanceDeactivatedLats ) == CLInum:
                        deactivateTime = float( datetime.datetime.strptime(
                                            timestamp, "%Y-%m-%dT%H:%M:%S.%f" ).strftime( '%s.%f' ) ) * 1000.0
                        instanceDeactivatedLats.append( deactivateTime - time1 )
                    elif "MASTER_CHANGED" in line and len( masterChangedLats ) == CLInum:
                        changedTime = float( datetime.datetime.strptime(
                                            timestamp, "%Y-%m-%dT%H:%M:%S.%f" ).strftime( '%s.%f' ) ) * 1000.0
                        masterChangedLats.append( changedTime - time1 )
                    if len( instanceDeactivatedLats ) > CLInum and len( masterChangedLats ) > CLInum:
                        break

            instanceDeactivatedLats.sort()
            instanceDeactivated = instanceDeactivatedLats[ 0 ]

            eventLatCheck = True if masterChangedLats and instanceDeactivated else False
            if not eventLatCheck:
                main.log.warn( "Latencies were NOT obtained from 'events' successfully." )

            main.log.info( "Obtain latency from tshark output." )
            tsharkLatCheck = True
            with open( main.tsharkResultPath, "r" ) as resultFile:
                resultText = resultFile.readline()
                main.log.info( "Capture result: " + resultText )
                resultText = resultText.split()
                if len( resultText ) > 1:
                    roleRequestLat = int( float( resultText[ 1 ] ) * 1000.0 ) - time1
                    resultFile.close()
                else:
                    main.log.error( "Tshark output file is NOT as expected." )
                    tsharkLatCheck = False
            if not tsharkLatCheck:
                main.log.warn( "Latency was NOT obtained from tshark successfully." )

            validDataCheck = False
            if tsharkLatCheck:
                main.log.info( "instanceDeactivated: " + str( instanceDeactivated ) )
                main.log.info( "roleRequestLat - instanceDeactivated: " + str( roleRequestLat - instanceDeactivated ) )
                if iteration >= main.warmUp:
                    main.log.info( "Verifying that the data are valid." )  # Don't record data during a warm-up
                    validDataCheck = roleRequestLat - instanceDeactivated >= 0 and \
                                     instanceDeactivated >= 0
                    if not validDataCheck:
                        main.log.warn( "Data are NOT valid." )

                    if eventLatCheck and tsharkLatCheck and validDataCheck:
                        main.log.info( "Saving data..." )
                        main.latencyData[ 'kill_to_deactivation' ]\
                            .append( instanceDeactivated )
                        main.latencyData[ 'deactivation_to_role_request' ]\
                            .append( roleRequestLat - instanceDeactivated )

            # Restart ONOS node
            main.log.info( "Restart ONOS node " + strNodeNumToKill + " and checking status of restart." )
            startResult = main.ONOSbench.onosStart( ip_address )

            if not startResult:
                main.log.error( "ONOS nodes NOT successfully started." )
                criticalError = True

            # Check if ONOS is up yet
            main.log.info( "Checking if ONOS node " + strNodeNumToKill + " is up." )
            upResult = main.ONOSbench.isup( ip_address )

            if not upResult:
                main.log.error( "ONOS did NOT successfully restart." )
                criticalError = True

            # Restart CLI
            main.log.info( "Restarting ONOS node " + strNodeNumToKill + "'s main.CLI." )
            cliResult = main.Cluster.active( main.nodeNumToKill ).CLI.startOnosCli( ip_address )
            main.Cluster.runningNodes[ main.nodeNumToKill ] .active = True

            if not cliResult:
                main.log.error( "ONOS CLI did NOT successfully restart." )
                criticalError = True

            main.log.info( "Checking ONOS nodes." )
            nodeResults = utilities.retry( main.Cluster.nodesCheck,
                                           False,
                                           sleep=1,
                                           attempts=3 )

            if not nodeResults:
                main.log.error( "Nodes check NOT successful." )
                criticalError = True

            main.log.info( "Sleeping for " + str( main.recoverySleep ) + " seconds..." )
            time.sleep( main.recoverySleep )

            if not ( mastershipCheck and
                     eventLatCheck and
                     tsharkLatCheck and
                     validDataCheck ) and \
                     iteration >= main.warmUp:
                main.failCounter += 1
                main.log.warn( "Iteration failed. Failure count: " + str( main.failCounter ) )
            if float( main.failCounter ) / float( main.sampleSize ) >= main.failPercent or criticalError:
                main.log.error( str( main.failPercent * 100 )
                                + "% or more of data is invalid, or a critical error has occurred." )
                passingResult = False
                break

        utilities.assert_equals( expect=True, actual=passingResult,
                                 onpass="Node scaling "
                                        + str( main.Cluster.numCtrls )
                                        + " data gathering was successful.",
                                 onfail="Node scaling "
                                        + str( main.Cluster.numCtrls )
                                        + " data gathering FAILED. Stopping test." )
        if not passingResult:
            main.cleanAndExit()

    def CASE3( self, main ):
        """
        Write results to database file.
        Omit this case if you don't want to write to database.
        """
        import numpy
        result = { 'avg': {}, 'stddev': {} }

        for i in main.latencyData:
            result[ 'avg' ][ i ] = numpy.average( main.latencyData[ i ] )
            result[ 'stddev' ][ i ] = numpy.std( main.latencyData[ i ] )

        main.log.info( "result: " + str( result ) )
        with open( main.dbFileName, "a" ) as dbFile:
            strToWrite = str( main.Cluster.numCtrls ) + ",'baremetal1'"
            strToWrite += ",'" + main.commit.split()[1] + "'"
            for i in result:
                for j in result[ i ]:
                    strToWrite += "," + str( result[ i ][ j ] )
            strToWrite += "\n"
            dbFile.write( strToWrite )
            dbFile.close()
