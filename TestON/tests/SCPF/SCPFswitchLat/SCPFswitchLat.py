"""
Copyright 2015 Open Networking Foundation ( ONF )

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
"""
    SCPFswitchLat
    Test Switch add/remove latency
    calculate package latency between switch and ONOS
    Switch UP:
    TCP -- Feature Reply -- Role Request -- Role Reply -- Device -- Graph
    Siwtch Down:
    Openflow FIN/ACK -- ACK -- Device -- Graph
"""
class SCPFswitchLat:

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
            main.cleanAndExit()
        main.testSetUp.envSetupDescription()
        stepResult = main.FALSE
        try:
            # The dictionary to record different type of wrongs
            main.wrong = { 'totalWrong': 0, 'skipDown': 0, 'TsharkValueIncorrect': 0,
                           'TypeError': 0, 'decodeJasonError': 0,
                           'checkResultIncorrect': 0 }
            main.maxWrong = int( main.params[ 'TEST' ][ 'MaxWrong' ] )
            main.resultRange = main.params[ 'TEST' ][ 'ResultRange' ]
            main.searchTerm = main.params[ 'TEST' ][ 'SearchTerm' ]
            main.MN1Ip = main.params[ 'MN' ][ 'ip1' ]
            main.dependencyPath = main.testOnDirectory + \
                                  main.params[ 'DEPENDENCY' ][ 'path' ]
            main.topoName = main.params[ 'DEPENDENCY' ][ 'topology' ]
            main.dependencyFunc = main.params[ 'DEPENDENCY' ][ 'function' ]
            main.cellName = main.params[ 'ENV' ][ 'cellName' ]
            main.apps = main.params[ 'ENV' ][ 'cellApps' ]
            main.scale = ( main.params[ 'SCALE' ] ).split( "," )

            main.ofPackage = main.params[ 'TSHARK' ]
            main.defaultTopoCfg = main.params[ 'CFG' ][ 'defaultTopo' ]
            main.tsharkResultPath = main.params[ 'TEST' ][ 'tsharkResultPath' ]
            main.sampleSize = int( main.params[ 'TEST' ][ 'sampleSize' ] )
            main.warmUp = int( main.params[ 'TEST' ][ 'warmUp' ] )
            main.dbFileName = main.params[ 'DATABASE' ][ 'dbName' ]
            main.startUpSleep = int( main.params[ 'SLEEP' ][ 'startup' ] )
            main.measurementSleep = int( main.params[ 'SLEEP' ][ 'measure' ] )
            main.deleteSwSleep = int( main.params[ 'SLEEP' ][ 'deleteSW' ] )
            main.maxScale = int( main.params[ 'max' ] )
            main.timeout = int( main.params[ 'TIMEOUT' ][ 'timeout' ] )
            main.MNSleep = int( main.params[ 'SLEEP' ][ 'mininet' ] )
            main.device = main.params[ 'TEST' ][ 'device' ]
            stepResult = main.testSetUp.envSetup()
            main.log.info( "Create Database file " + main.dbFileName )
            resultsDB = open( main.dbFileName, "w+" )
            resultsDB.close()

            main.switchFunc = imp.load_source( main.dependencyFunc,
                                               main.dependencyPath +
                                               main.dependencyFunc +
                                               ".py" )
        except Exception as e:
            main.testSetUp.envSetupException( e )
        main.testSetUp.evnSetupConclusion( stepResult )
        main.commit = main.commit.split( " " )[ 1 ]

    def CASE1( self, main ):
        # Clean up test environment and set up
        import time
        try:
            from tests.dependencies.utils import Utils
        except ImportError:
            main.log.error( "Utils not found exiting the test" )
            main.cleanAndExit()
        try:
            main.Utils
        except ( NameError, AttributeError ):
            main.Utils = Utils()
        main.maxNumBatch = 0
        main.testSetUp.ONOSSetUp( main.Cluster, True,
                                  cellName=main.cellName, killRemoveMax=False )

        main.log.info( "Configure apps" )
        main.Cluster.active( 0 ).CLI.setCfg( main.defaultTopoCfg,
                                             "maxEvents 1" )
        main.Cluster.active( 0 ).CLI.setCfg( main.defaultTopoCfg,
                                             "maxBatchMs 0" )
        main.Cluster.active( 0 ).CLI.setCfg( main.defaultTopoCfg,
                                             "maxIdleMs 0" )
        main.Cluster.command( "logSet",
                              args=[ "DEBUG", "org.onosproject.metrics.topology" ],
                              specificDriver=2 )
        time.sleep( 1 )

        main.log.info( "Copy topology file to Mininet" )
        main.ONOSbench.copyMininetFile( main.topoName,
                                        main.dependencyPath,
                                        main.Mininet1.user_name,
                                        main.Mininet1.ip_address )
        main.Utils.mininetCleanup( main.Mininet1 )
        time.sleep( main.MNSleep )
        main.log.info( "Start new mininet topology" )
        main.Mininet1.startNet()
        main.log.info( "Assign switch to controller to ONOS node 1" )

        time.sleep( 2 )

    def CASE2( self, main ):
        import time
        import json
        import numpy

        resultDict = { 'up': {}, 'down': {} }
        for i in range( 1, main.Cluster.numCtrls + 1 ):
            resultDict[ 'up' ][ 'node' + str( i ) ] = {}
            resultDict[ 'up' ][ 'node' + str( i ) ][ 'Ave' ] = {}
            resultDict[ 'up' ][ 'node' + str( i ) ][ 'Std' ] = {}
            resultDict[ 'up' ][ 'node' + str( i ) ][ 'T_F' ] = []  # TCP to Feature
            resultDict[ 'up' ][ 'node' + str( i ) ][ 'F_D' ] = []  # Feature to Device
            resultDict[ 'up' ][ 'node' + str( i ) ][ 'D_G' ] = []  # Device to Graph
            resultDict[ 'up' ][ 'node' + str( i ) ][ 'E_E' ] = []  # TCP to Graph

        for i in range( 1, main.Cluster.numCtrls + 1 ):
            resultDict[ 'down' ][ 'node' + str( i ) ] = {}
            resultDict[ 'down' ][ 'node' + str( i ) ][ 'Ave' ] = {}
            resultDict[ 'down' ][ 'node' + str( i ) ][ 'Std' ] = {}
            resultDict[ 'down' ][ 'node' + str( i ) ][ 'FA_A' ] = []  # Fin_ack to ACK
            resultDict[ 'down' ][ 'node' + str( i ) ][ 'A_D' ] = []  # Ack to Device
            resultDict[ 'down' ][ 'node' + str( i ) ][ 'D_G' ] = []  # Device to Graph
            resultDict[ 'down' ][ 'node' + str( i ) ][ 'E_E' ] = []  # fin_ack to Graph
        for i in range( 0, main.sampleSize + main.warmUp ):
            main.log.info( "************************************************************" )
            main.log.info( "************************ Iteration: {} **********************" .format( str( i + 1 ) ) )
            if i < main.warmUp:
                main.switchFunc.captureOfPack( main, main.device, main.ofPackage,
                                               "up", resultDict, True )
                main.switchFunc.captureOfPack( main, main.device, main.ofPackage,
                                               "down", resultDict, True )
                main.log.debug( "Before devices : " + str( main.Cluster.active( 0 ).CLI.devices() ) )
                main.Cluster.active( 0 ).CLI.removeDevice( "of:0000000000000001" )
                main.log.debug( "After devices : " + str( main.Cluster.active( 0 ).CLI.devices() ) )
                while main.Cluster.active( 0 ).CLI.devices() != "[]":
                    main.log.error( "DEVICE NOT REMOVED !!!!!")
                    main.Cluster.active( 0 ).CLI.removeDevice( "of:0000000000000001" )
            else:
                main.switchFunc.captureOfPack( main, main.device, main.ofPackage,
                                               "up", resultDict, False )
                main.switchFunc.captureOfPack( main, main.device, main.ofPackage,
                                                "down", resultDict, False )
                main.log.debug( "Before devices : " + str( main.Cluster.active( 0 ).CLI.devices() ) )
                main.Cluster.active( 0 ).CLI.removeDevice( "of:0000000000000001" )
                main.log.debug("After devices : " + str(main.Cluster.active(0).CLI.devices()))
                while main.Cluster.active( 0 ).CLI.devices() != "[]":
                    main.log.error( "DEVICE NOT REMOVED !!!!!")
                    main.Cluster.active( 0 ).CLI.removeDevice( "of:0000000000000001" )

        # Dictionary for result
        maxDict = {}
        maxDict[ 'down' ] = {}
        maxDict[ 'up' ] = {}
        maxDict[ 'down' ][ 'max' ] = 0
        maxDict[ 'up' ][ 'max' ] = 0
        maxDict[ 'down' ][ 'node' ] = 0
        maxDict[ 'up' ][ 'node' ] = 0

        for i in range( 1, main.Cluster.numCtrls + 1 ):
            # calculate average and std for result, and grep the max End to End data
            EtoEtemp = numpy.average( resultDict[ 'up' ][ 'node' + str( i ) ][ 'E_E' ] )
            resultDict[ 'up' ][ 'node' + str( i ) ][ 'Ave' ][ 'E_E' ] = EtoEtemp
            if maxDict[ 'up' ][ 'max' ] < EtoEtemp:
                # get max End to End latency
                maxDict[ 'up' ][ 'max' ] = EtoEtemp
                maxDict[ 'up' ][ 'node' ] = i
            resultDict[ 'up' ][ 'node' + str( i ) ][ 'Ave' ][ 'T_F' ] = numpy.average( resultDict[ 'up' ][ 'node' + str( i ) ][ 'T_F' ] )
            resultDict[ 'up' ][ 'node' + str( i ) ][ 'Ave' ][ 'F_D' ] = numpy.average( resultDict[ 'up' ][ 'node' + str( i ) ][ 'F_D' ] )
            resultDict[ 'up' ][ 'node' + str( i ) ][ 'Ave' ][ 'D_G' ] = numpy.average( resultDict[ 'up' ][ 'node' + str( i ) ][ 'D_G' ] )

            resultDict[ 'up' ][ 'node' + str( i ) ][ 'Std' ][ 'E_E' ] = numpy.std( resultDict[ 'up' ][ 'node' + str( i ) ][ 'E_E' ] )
            resultDict[ 'up' ][ 'node' + str( i ) ][ 'Std' ][ 'T_F' ] = numpy.std( resultDict[ 'up' ][ 'node' + str( i ) ][ 'T_F' ] )
            resultDict[ 'up' ][ 'node' + str( i ) ][ 'Std' ][ 'F_D' ] = numpy.std( resultDict[ 'up' ][ 'node' + str( i ) ][ 'F_D' ] )
            resultDict[ 'up' ][ 'node' + str( i ) ][ 'Std' ][ 'D_G' ] = numpy.std( resultDict[ 'up' ][ 'node' + str( i ) ][ 'D_G' ] )

            # calculate average and std for result, and grep the max End to End data
            EtoEtemp = numpy.average( resultDict[ 'down' ][ 'node' + str( i ) ][ 'E_E' ] )
            resultDict[ 'down' ][ 'node' + str( i ) ][ 'Ave' ][ 'E_E' ] = EtoEtemp
            if maxDict[ 'down' ][ 'max' ] < EtoEtemp:
                # get max End to End latency
                maxDict[ 'down' ][ 'max' ] = EtoEtemp
                maxDict[ 'down' ][ 'node' ] = i
            resultDict[ 'down' ][ 'node' + str( i ) ][ 'Ave' ][ 'FA_A' ] = numpy.average( resultDict[ 'down' ][ 'node' + str( i ) ][ 'FA_A' ] )
            resultDict[ 'down' ][ 'node' + str( i ) ][ 'Ave' ][ 'A_D' ] = numpy.average( resultDict[ 'down' ][ 'node' + str( i ) ][ 'A_D' ] )
            resultDict[ 'down' ][ 'node' + str( i ) ][ 'Ave' ][ 'D_G' ] = numpy.average( resultDict[ 'down' ][ 'node' + str( i ) ][ 'D_G' ] )

            resultDict[ 'down' ][ 'node' + str( i ) ][ 'Std' ][ 'E_E' ] = numpy.std( resultDict[ 'down' ][ 'node' + str( i ) ][ 'E_E' ] )
            resultDict[ 'down' ][ 'node' + str( i ) ][ 'Std' ][ 'FA_A' ] = numpy.std( resultDict[ 'down' ][ 'node' + str( i ) ][ 'FA_A' ] )
            resultDict[ 'down' ][ 'node' + str( i ) ][ 'Std' ][ 'A_D' ] = numpy.std( resultDict[ 'down' ][ 'node' + str( i ) ][ 'A_D' ] )
            resultDict[ 'down' ][ 'node' + str( i ) ][ 'Std' ][ 'D_G' ] = numpy.std( resultDict[ 'down' ][ 'node' + str( i ) ][ 'D_G' ] )

            main.log.report( "=====node{} Summary:=====".format( str( i ) ) )
            main.log.report( "=============Switch up=======" )
            main.log.report( "End to End average: {}".format( str( resultDict[ "up" ][ 'node' + str( i ) ][ 'Ave' ][ 'E_E' ] ) ) )
            main.log.report( "End to End Std: {}".format( str( resultDict[ "up" ][ 'node' + str( i ) ][ 'Std' ][ 'E_E' ] ) ) )
            main.log.report( "TCP to Feature average: {}".format( str( resultDict[ "up" ][ 'node' + str( i ) ][ 'Ave' ][ 'T_F' ] ) ) )
            main.log.report( "TCP to Feature Std: {}".format( str( resultDict[ "up" ][ 'node' + str( i ) ][ 'Std' ][ 'T_F' ] ) ) )
            main.log.report( "Feature to Device average: {}".format( str( resultDict[ "up" ][ 'node' + str( i ) ][ 'Ave' ][ 'F_D' ] ) ) )
            main.log.report( "Feature to Device Std: {}".format( str( resultDict[ "up" ][ 'node' + str( i ) ][ 'Std' ][ 'F_D' ] ) ) )
            main.log.report( "Device to Graph average: {}".format( str( resultDict[ "up" ][ 'node' + str( i ) ][ 'Ave' ][ 'D_G' ] ) ) )
            main.log.report( "Device to Graph Std: {}".format( str( resultDict[ "up" ][ 'node' + str( i ) ][ 'Std' ][ 'D_G' ] ) ) )

            main.log.report( "=============Switch down=======" )
            main.log.report( "End to End average: {}".format( str( resultDict[ "down" ][ 'node' + str( i ) ][ 'Ave' ][ 'E_E' ] ) ) )
            main.log.report( "End to End Std: {}".format( str( resultDict[ "down" ][ 'node' + str( i ) ][ 'Std' ][ 'E_E' ] ) ) )
            main.log.report( "Fin_ACK to ACK average: {}".format( str( resultDict[ "down" ][ 'node' + str( i ) ][ 'Ave' ][ 'FA_A' ] ) ) )
            main.log.report( "Fin_ACK to ACK Std: {}".format( str( resultDict[ "down" ][ 'node' + str( i ) ][ 'Std' ][ 'FA_A' ] ) ) )
            main.log.report( "ACK to Device average: {}".format( str( resultDict[ "down" ][ 'node' + str( i ) ][ 'Ave' ][ 'A_D' ] ) ) )
            main.log.report( "ACK to Device Std: {}".format( str( resultDict[ "down" ][ 'node' + str( i ) ][ 'Std' ][ 'A_D' ] ) ) )
            main.log.report( "Device to Graph average: {}".format( str( resultDict[ "down" ][ 'node' + str( i ) ][ 'Ave' ][ 'D_G' ] ) ) )
            main.log.report( "Device to Graph Std: {}".format( str( resultDict[ "down" ][ 'node' + str( i ) ][ 'Std' ][ 'D_G' ] ) ) )

        # Check if any result is abnormal
        # Switch-up
        result = resultDict[ 'up' ][ 'node' + str( maxDict[ 'up' ][ 'node' ] ) ][ 'Ave' ][ 'E_E' ]
        threshold = float( main.params[ 'ALARM' ][ 'maxSwitchUpAvg' ].split( ',' )[ main.cycle - 1 ] )
        if result > threshold:
            main.log.alarm( "{}-node switch-up avg: {} ms > {} ms".format( main.Cluster.numCtrls, result, threshold ) )
        result = resultDict[ 'up' ][ 'node' + str( maxDict[ 'up' ][ 'node' ] ) ][ 'Std' ][ 'E_E' ]
        threshold = float( main.params[ 'ALARM' ][ 'maxSwitchUpStd' ].split( ',' )[ main.cycle - 1 ] )
        if result > threshold:
            main.log.alarm( "{}-node switch-up std: {} ms > {} ms".format( main.Cluster.numCtrls, result, threshold ) )
        # Switch-down
        result = resultDict[ 'down' ][ 'node' + str( maxDict[ 'down' ][ 'node' ] ) ][ 'Ave' ][ 'E_E' ]
        threshold = float( main.params[ 'ALARM' ][ 'maxSwitchDownAvg' ].split( ',' )[ main.cycle - 1 ] )
        if result > threshold:
            main.log.alarm( "{}-node switch-down avg: {} ms > {} ms".format( main.Cluster.numCtrls, result, threshold ) )
        result = resultDict[ 'down' ][ 'node' + str( maxDict[ 'down' ][ 'node' ] ) ][ 'Std' ][ 'E_E' ]
        threshold = float( main.params[ 'ALARM' ][ 'maxSwitchDownStd' ].split( ',' )[ main.cycle - 1 ] )
        if result > threshold:
            main.log.alarm( "{}-node switch-down std: {} ms > {} ms".format( main.Cluster.numCtrls, result, threshold ) )

        with open( main.dbFileName, "a" ) as dbFile:
            # Scale number
            temp = str( main.Cluster.numCtrls )
            temp += ",'baremetal1'"
            # put result
            temp += "," + str( "%.2f" % resultDict[ 'up' ][ 'node' + str( maxDict[ 'up' ][ 'node' ] ) ][ 'Ave' ][ 'E_E' ] )
            temp += "," + str( "%.2f" % resultDict[ 'up' ][ 'node' + str( maxDict[ 'up' ][ 'node' ] ) ][ 'Ave' ][ 'T_F' ] )
            temp += "," + str( "%.2f" % resultDict[ 'up' ][ 'node' + str( maxDict[ 'up' ][ 'node' ] ) ][ 'Ave' ][ 'F_D' ] )
            temp += "," + str( "%.2f" % resultDict[ 'up' ][ 'node' + str( maxDict[ 'up' ][ 'node' ] ) ][ 'Ave' ][ 'D_G' ] )

            temp += "," + str( "%.2f" % resultDict[ 'down' ][ 'node' + str( maxDict[ 'down' ][ 'node' ] ) ][ 'Ave' ][ 'E_E' ] )
            temp += "," + str( "%.2f" % resultDict[ 'down' ][ 'node' + str( maxDict[ 'down' ][ 'node' ] ) ][ 'Ave' ][ 'FA_A' ] )
            temp += "," + str( "%.2f" % resultDict[ 'down' ][ 'node' + str( maxDict[ 'down' ][ 'node' ] ) ][ 'Ave' ][ 'A_D' ] )
            temp += "," + str( "%.2f" % resultDict[ 'down' ][ 'node' + str( maxDict[ 'down' ][ 'node' ] ) ][ 'Ave' ][ 'D_G' ] )

            temp += "," + str( "%.2f" % resultDict[ 'up' ][ 'node' + str( maxDict[ 'up' ][ 'node' ] ) ][ 'Std' ][ 'E_E' ] )
            temp += "," + str( "%.2f" % resultDict[ 'down' ][ 'node' + str( maxDict[ 'down' ][ 'node' ] ) ][ 'Std' ][ 'E_E' ] )

            temp += "\n"
            dbFile.write( temp )
            dbFile.close()
