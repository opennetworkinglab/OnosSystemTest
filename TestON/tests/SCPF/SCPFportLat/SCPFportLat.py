"""
Copyright 2015 Open Networking Foundation (ONF)

Please refer questions to either the onos test mailing list at <onos-test@onosproject.org>,
the System Testing Plans and Results wiki page at <https://wiki.onosproject.org/x/voMg>,
or the System Testing Guide page at <https://wiki.onosproject.org/x/WYQg>

    TestON is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    TestON is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with TestON.  If not, see <http://www.gnu.org/licenses/>.
"""

'''
    SCPFportLat test
    Test latency for port status change
    Up & Down:
    PortStatus --- Device --- Link --- Graph

    yunpeng@onlab.us
'''
class SCPFportLat:
    def __init__( self ):
        self.default = ''

    def CASE0( self, main ):
        import os
        import imp
        '''
        - GIT
        - BUILDING ONOS
            Pull specific ONOS branch, then Build ONOS ono ONOS Bench.
            This step is usually skipped. Because in a Jenkins driven automated
            test env. We want Jenkins jobs to pull&build for flexibility to handle
            different versions of ONOS.
        - Construct tests variables
        '''
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
            main.dependencyPath = main.testOnDirectory + \
                                  main.params[ 'DEPENDENCY' ][ 'path' ]
            main.dependencyFunc = main.params[ 'DEPENDENCY' ][ 'function' ]
            main.topoName = main.params[ 'DEPENDENCY' ][ 'topology' ]
            main.cellName = main.params[ 'ENV' ][ 'cellName' ]
            main.apps = main.params[ 'ENV' ][ 'cellApps' ]
            main.scale = ( main.params[ 'SCALE' ] ).split( "," )
            main.ofportStatus = main.params[ 'TSHARK' ][ 'ofpPortStatus' ]
            main.tsharkResultPath = main.params[ 'TSHARK' ][ 'tsharkReusltPath' ]
            main.sampleSize = int( main.params[ 'TEST' ][ 'sampleSize' ] )
            main.warmUp = int( main.params[ 'TEST' ][ 'warmUp' ] )
            main.maxProcessTime = int( main.params[ 'TEST' ][ 'maxProcessTime' ] )
            main.dbFileName = main.params[ 'DATABASE' ][ 'dbName' ]
            main.startUpSleep = int( main.params[ 'SLEEP' ][ 'startup' ] )
            main.measurementSleep = int( main.params[ 'SLEEP' ][ 'measure' ] )
            main.maxScale = int( main.params[ 'max' ] )
            main.defaultTopoCfg = main.params[ 'CFG' ][ 'defaultTopo' ]
            main.interface = main.params[ 'TEST' ][ 'interface' ]
            main.timeout = int( main.params[ 'TIMEOUT' ][ 'timeout' ] )
            main.MNSleep = int( main.params[ 'SLEEP' ][ 'mininet' ] )
            main.device = main.params[ 'TEST' ][ 'device' ]
            main.debug = main.params[ 'TEST' ][ 'debug' ]

            if main.debug == "True":
                main.debug = True
            else:
                main.debug = False

            stepResult = main.testSetUp.envSetup()
            main.log.info( "Create Database file " + main.dbFileName )
            resultsDB = open( main.dbFileName, "w+" )
            resultsDB.close()

            main.portFunc = imp.load_source( main.dependencyFunc,
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
        main.testSetUp.ONOSSetUp( main.Mininet1, main.Cluster, True,
                                  cellName=main.cellName, killRemoveMax=False )

        main.log.info( "Configure apps" )
        main.Cluster.active( 0 ).CLI.setCfg( main.defaultTopoCfg,
                                                  "maxEvents 1" )
        main.Cluster.active( 0 ).CLI.setCfg( main.defaultTopoCfg,
                                                  "maxBatchMs 0" )
        main.Cluster.active( 0 ).CLI.setCfg( main.defaultTopoCfg,
                                                  "maxIdleMs 0" )
        time.sleep( 1 )
        main.log.info( "Copy topology file to Mininet" )
        main.ONOSbench.copyMininetFile( main.topoName,
                                       main.dependencyPath,
                                       main.Mininet1.user_name,
                                       main.Mininet1.ip_address )
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
        time.sleep( main.MNSleep )
        main.log.info( "Start new mininet topology" )
        main.Mininet1.startNet()
        main.log.info( "Assign switch to controller to ONOS node 1" )
        time.sleep( 1 )
        main.Mininet1.assignSwController( sw='s1',
                                          ip=main.Cluster.active( 0 ).ipAddress )
        main.Mininet1.assignSwController( sw='s2',
                                          ip=main.Cluster.active( 0 ).ipAddress )

        time.sleep( 2 )

    def CASE2( self, main ):
        import time
        import numpy
        # dictionary for each node and each timestamps
        resultDict = { 'up' : {}, 'down' : {} }
        for d in resultDict:
            for i in range( 1, main.Cluster.numCtrls + 1 ):
                resultDict[ d ][ 'node' + str( i ) ] = {}
                resultDict[ d ][ 'node' + str( i ) ][ 'Ave' ] = {}
                resultDict[ d ][ 'node' + str( i ) ][ 'Std' ] = {}
                resultDict[ d ][ 'node' + str( i ) ][ 'EtoE' ] = []
                resultDict[ d ][ 'node' + str( i ) ][ 'PtoD' ] = []
                resultDict[ d ][ 'node' + str( i ) ][ 'DtoL' ] = []
                resultDict[ d ][ 'node' + str( i ) ][ 'LtoG' ] = []
        for i in range( 0, main.sampleSize + main.warmUp ):
            main.log.info( "==========================================" )
            main.log.info( "================iteration:{}==============".format( str ( i + 1 ) ) )
            if i >= main.warmUp:
                # Portdown iteration
                main.portFunc.capturePortStatusPack( main,
                                                     main.device,
                                                     main.interface,
                                                     "down",
                                                     resultDict,
                                                     False )
                time.sleep( 2 )
                # PortUp iteration
                main.portFunc.capturePortStatusPack( main,
                                                     main.device,
                                                     main.interface,
                                                     "up",
                                                     resultDict,
                                                     False )
            else:
                # if warm up, keep old result dictionary
                main.portFunc.capturePortStatusPack( main,
                                                     main.device,
                                                     main.interface,
                                                     "down",
                                                     resultDict,
                                                     True )
                main.portFunc.capturePortStatusPack( main,
                                                     main.device,
                                                     main.interface,
                                                     "up",
                                                     resultDict,
                                                     True )

        # Dictionary for result
        maxDict  = {}
        maxDict[ 'down' ] = {}
        maxDict[ 'up' ] = {}
        maxDict[ 'down' ][ 'max' ] = 0
        maxDict[ 'up' ][ 'max' ] = 0
        maxDict[ 'down' ][ 'node' ] = 0
        maxDict[ 'up' ][ 'node' ] = 0
        EtoEtemp = 0
        for d in resultDict:
            for i in range( 1, main.Cluster.numCtrls + 1 ):
                # calculate average and std for result, and grep the max End to End data
                EtoEtemp = numpy.average( resultDict[ d ][ 'node' + str( i ) ][ 'EtoE' ] )
                resultDict[ d ][ 'node' + str( i ) ][ 'Ave' ][ 'EtoE' ] = EtoEtemp
                if maxDict[ d ][ 'max' ] < EtoEtemp:
                    # get max End to End latency
                    maxDict[ d ][ 'max' ] = EtoEtemp
                    maxDict[ d ][ 'node' ] = i
                resultDict[ d ][ 'node' + str( i ) ][ 'Ave' ][ 'PtoD' ] = numpy.average( resultDict[ d ][ 'node' + str( i ) ][ 'PtoD' ] )
                resultDict[ d ][ 'node' + str( i ) ][ 'Ave' ][ 'DtoL' ] = numpy.average( resultDict[ d ][ 'node' + str( i ) ][ 'DtoL' ] )
                resultDict[ d ][ 'node' + str( i ) ][ 'Ave' ][ 'LtoG' ] = numpy.average( resultDict[ d ][ 'node' + str( i ) ][ 'LtoG' ] )

                resultDict[ d ][ 'node' + str( i ) ][ 'Std' ][ 'EtoE' ] = numpy.std( resultDict[ d ][ 'node' + str( i ) ][ 'EtoE' ] )
                resultDict[ d ][ 'node' + str( i ) ][ 'Std' ][ 'PtoD' ] = numpy.std( resultDict[ d ][ 'node' + str( i ) ][ 'PtoD' ] )
                resultDict[ d ][ 'node' + str( i ) ][ 'Std' ][ 'DtoL' ] = numpy.std( resultDict[ d ][ 'node' + str( i ) ][ 'DtoL' ] )
                resultDict[ d ][ 'node' + str( i ) ][ 'Std' ][ 'LtoG' ] = numpy.std( resultDict[ d ][ 'node' + str( i ) ][ 'LtoG' ] )

                main.log.report( "=====node{} Summary:=====".format( str( i ) ) )
                main.log.report( "=============Port {}=======".format( str( d ) ) )
                main.log.report(
                    "End to End average: {}".format( str( resultDict[ d ][ 'node' + str( i ) ][ 'Ave' ][ 'EtoE' ] ) ) )
                main.log.report(
                    "End to End Std: {}".format( str( resultDict[ d ][ 'node' + str( i ) ][ 'Std' ][ 'EtoE' ] ) ) )
                main.log.report(
                    "Package to Device average: {}".format( str( resultDict[ d ][ 'node' + str( i ) ][ 'Ave' ][ 'PtoD' ] ) ) )
                main.log.report(
                    "Package to Device Std: {}".format( str( resultDict[ d ][ 'node' + str( i ) ][ 'Std' ][ 'PtoD' ] ) ) )
                main.log.report(
                    "Device to Link average: {}".format( str( resultDict[ d ][ 'node' + str( i ) ][ 'Ave' ][ 'DtoL' ] ) ) )
                main.log.report(
                    "Device to Link Std: {}".format( str( resultDict[ d ][ 'node' + str( i ) ][ 'Std' ][ 'DtoL' ] ) ) )
                main.log.report(
                    "Link to Grapg average: {}".format( str( resultDict[ d ][ 'node' + str( i ) ][ 'Ave' ][ 'LtoG' ] ) ) )
                main.log.report(
                    "Link to Grapg Std: {}".format( str( resultDict[ d ][ 'node' + str( i ) ][ 'Std' ][ 'LtoG' ] ) ) )

        with open( main.dbFileName, "a" ) as dbFile:
            # Scale number
            temp = str( main.Cluster.numCtrls )
            temp += ",'baremetal1'"
            # put result
            temp += "," + str( resultDict[ 'up' ][ 'node' + str( maxDict[ 'up' ][ 'node' ] ) ][ 'Ave' ][ 'EtoE' ] )
            temp += "," + str( resultDict[ 'up' ][ 'node' + str( maxDict[ 'up' ][ 'node' ] ) ][ 'Ave' ][ 'PtoD' ] )
            temp += "," + str( resultDict[ 'up' ][ 'node' + str( maxDict[ 'up' ][ 'node' ] ) ][ 'Ave' ][ 'DtoL' ] )
            temp += "," + str( resultDict[ 'up' ][ 'node' + str( maxDict[ 'up' ][ 'node' ] ) ][ 'Ave' ][ 'LtoG' ] )
            temp += "," + str( resultDict[ 'down' ][ 'node' + str( maxDict[ 'down' ][ 'node' ] ) ][ 'Ave' ][ 'EtoE' ] )
            temp += "," + str( resultDict[ 'down' ][ 'node' + str( maxDict[ 'down' ][ 'node' ] ) ][ 'Ave' ][ 'PtoD' ] )
            temp += "," + str( resultDict[ 'down' ][ 'node' + str( maxDict[ 'down' ][ 'node' ] ) ][ 'Ave' ][ 'DtoL' ] )
            temp += "," + str( resultDict[ 'down' ][ 'node' + str( maxDict[ 'down' ][ 'node' ] ) ][ 'Ave' ][ 'LtoG' ] )

            temp += "," + str( resultDict[ 'up' ][ 'node' + str( maxDict[ 'up' ][ 'node' ] ) ][ 'Std' ][ 'EtoE' ] )
            temp += "," + str( resultDict[ 'down' ][ 'node' + str( maxDict[ 'down' ][ 'node' ] ) ][ 'Std' ][ 'EtoE' ] )

            temp += "\n"
            dbFile.write( temp )
            dbFile.close()
