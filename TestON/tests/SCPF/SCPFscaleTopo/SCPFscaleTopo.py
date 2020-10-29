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
# Testing network scalability, this test suite scales up a network topology
# using mininet and verifies ONOS stability


class SCPFscaleTopo:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        import os
        import imp
        """
        - Construct tests variables
        - GIT ( optional )
            - Checkout ONOS master branch
            - Pull latest ONOS code
        - Building ONOS ( optional )
            - Install ONOS package
            - Build ONOS package
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
            # The variable to decide if the data should be written into data base.
            # 1 means Yes and -1 means No.
            main.writeData = 1
            main.searchTerm = main.params[ 'SearchTerm' ]
            main.apps = main.params[ 'ENV' ][ 'cellApps' ]
            main.dependencyPath = main.testOnDirectory + \
                                  main.params[ 'DEPENDENCY' ][ 'path' ]
            main.tsharkResultPath = main.params[ 'TsharkPath' ]
            main.roleRequest = main.params[ 'SearchTerm' ][ 'roleRequest' ]
            main.multiovs = main.params[ 'DEPENDENCY' ][ 'multiovs' ]
            main.topoName = main.params[ 'TOPOLOGY' ][ 'topology' ]
            main.topoScale = ( main.params[ 'TOPOLOGY' ][ 'scale' ] ).split( "," )
            main.topoScaleSize = len( main.topoScale )
            wrapperFile1 = main.params[ 'DEPENDENCY' ][ 'wrapper1' ]
            wrapperFile2 = main.params[ 'DEPENDENCY' ][ 'wrapper2' ]
            wrapperFile3 = main.params[ 'DEPENDENCY' ][ 'wrapper3' ]
            main.topoCmpAttempts = int( main.params[ 'ATTEMPTS' ][ 'topoCmp' ] )
            main.pingallAttempts = int( main.params[ 'ATTEMPTS' ][ 'pingall' ] )
            main.startUpSleep = int( main.params[ 'SLEEP' ][ 'startup' ] )
            main.balanceSleep = int( main.params[ 'SLEEP' ][ 'balance' ] )
            main.nodeSleep = int( main.params[ 'SLEEP' ][ 'nodeSleep' ] )
            main.pingallSleep = int( main.params[ 'SLEEP' ][ 'pingall' ] )
            main.MNSleep = int( main.params[ 'SLEEP' ][ 'MNsleep' ] )
            main.pingTimeout = float( main.params[ 'TIMEOUT' ][ 'pingall' ] )
            main.hostDiscover = main.params[ 'TOPOLOGY' ][ 'host' ]
            main.hostDiscoverSleep = float( main.params[ 'SLEEP' ][ 'host' ] )
            main.basicMNTime = int( main.params[ 'TIMEOUT' ][ 'basicMininet' ] )
            main.startNetTime = int( main.params[ 'TIMEOUT' ][ 'startNet' ] )
            main.stopNetTime = int( main.params[ 'TIMEOUT' ][ 'stopNet' ] )
            main.MNupdateTime = int( main.params[ 'TIMEOUT' ][ 'update' ] )
            main.MNLinksTime = int( main.params[ 'TIMEOUT' ][ 'links' ] )
            main.getTopoTime = int( main.params[ 'TIMEOUT' ][ 'getTopo' ] )
            main.tsharkInterface = main.params[ 'TSHARK' ][ 'tsharkInterface' ]
            main.currScale = None
            main.maxScale = 1
            main.threadID = 0
            if main.hostDiscover == 'True':
                main.hostDiscover = True
            else:
                main.hostDiscover = False
            main.homeDir = os.path.expanduser( '~' )
            main.hostsData = {}

            stepResult = main.testSetUp.envSetup()
            main.allinfo = {}  # The dictionary to record all the data from karaf.log

            for i in range( 2 ):
                main.allinfo[ i ] = {}
                for w in range( 3 ):
                    # Totaltime: the time from the new switchConnection to its end
                    # swConnection: the time from the first new switchConnection to the last new switchConnection
                    # lastSwToLastRr: the time from the last new switchConnection to the last role request
                    # lastRrToLastTopology: the time form the last role request to the last topology
                    # disconnectRate: the rate that shows how many switch disconnect after connection
                    main.allinfo[ i ][ 'info' + str( w ) ] = { 'totalTime': 0, 'swConnection': 0, 'lastSwToLastRr': 0, 'lastRrToLastTopology': 0, 'disconnectRate': 0 }

            main.dbFilePath = main.params[ 'DATABASE' ][ 'dbPath' ]
            main.log.info( "Create Database file " + main.dbFilePath )
            resultDB = open( main.dbFilePath, 'w+' )
            resultDB.close()

            main.scaleTopoFunction = imp.load_source( wrapperFile2,
                                                      main.dependencyPath +
                                                      wrapperFile2 +
                                                      ".py" )

            main.topo = imp.load_source( wrapperFile3,
                                         main.dependencyPath +
                                         wrapperFile3 +
                                         ".py" )

            main.ONOSbench.scp( main.Mininet1,
                                main.dependencyPath +
                                main.multiovs,
                                main.Mininet1.home,
                                direction="to" )
        except Exception as e:
            main.testSetUp.envSetupException( e )
        main.testSetUp.evnSetupConclusion( stepResult )
        main.commit = main.commit.split( " " )[ 1 ]

    def CASE2( self, main ):
        """
        - Set up cell
            - Create cell file
            - Set cell file
            - Verify cell file
        - Kill ONOS process
        - Uninstall ONOS cluster
        - Verify ONOS start up
        - Install ONOS cluster
        - Connect to cli
        """
        import time
        main.testSetUp.ONOSSetUp( main.Cluster )

    def CASE3( self, main ):
        """
            cleanup mininet.
        """
        try:
            from tests.dependencies.utils import Utils
        except ImportError:
            main.log.error( "Utils not found exiting the test" )
            main.cleanAndExit()
        try:
            main.Utils
        except ( NameError, AttributeError ):
            main.Utils = Utils()
        main.Utils.mininetCleanup( main.Mininet1, exitTimeout=main.basicMNTime + ( int( main.currScale ) if main.currScale is not None
                                   else 1 ) * main.stopNetTime )

    def CASE10( self, main ):
        """
            Starting up torus topology
        """
        main.case( "Starting up Mininet and verifying topology" )
        main.caseExplanation = "Starting Mininet with a scalling topology and " +\
                "comparing topology elements between Mininet and ONOS"
        if main.topoScale:
            main.currScale = main.topoScale.pop( 0 )
        else:
            main.log.error( "topology scale is empty" )
        main.step( "Starting up TORUS %sx%s topology" % ( main.currScale, main.currScale ) )

        main.log.info( "Constructing Mininet command" )
        mnCmd = " mn --custom " + main.Mininet1.home + main.multiovs + \
                " --switch ovsm --topo " + main.topoName + "," + main.currScale + "," + main.currScale
        for ctrl in main.Cluster.runningNodes:
            mnCmd += " --controller remote,ip=" + ctrl.ipAddress
        stepResult = main.Mininet1.startNet( mnCmd=mnCmd, timeout=( main.basicMNTime + int( main.currScale ) * main.startNetTime )  )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                  onpass=main.topoName +
                                    " topology started successfully",
                                 onfail=main.topoName +
                                    " topology failed to start" )

        time.sleep( main.MNSleep )
        main.log.info( "Clean up Tshark" )
        with open( main.tsharkResultPath, "w" ) as tshark:
            tshark.write( "" )
        main.log.info( "Starting Tshark capture" )
        main.ONOSbench.tsharkGrep( main.roleRequest, main.tsharkResultPath, interface=main.tsharkInterface, grepOptions='-E' )
        main.Cluster.active( 0 ).CLI.activateApp( "org.onosproject.openflow" )
        time.sleep( main.MNSleep )
        main.log.info( "Stop Tshark" )
        main.ONOSbench.tsharkStop()
        main.log.info( "Get role request time" )
        with open( main.tsharkResultPath, "r" ) as resultFile:
            resultText = resultFile.readlines()
            resultFile.close()

    def CASE11( self, main ):
        """
            Compare topo, and sending Arping package
            if the topology is same, then Pass.
        """
        import json
        import time
        try:
            from tests.dependencies.topology import Topology
        except ImportError:
            main.log.error( "Topology not found exiting the test" )
            main.cleanAndExit()
        try:
            main.topoRelated
        except ( NameError, AttributeError ):
            main.topoRelated = Topology()
        # First capture

        main.postResult = True
        main.step( "Grep information from the ONOS log" )
        for i in range( 3 ):
            # Calculate total time
            main.allinfo[ 0 ][ 'info' + str( i ) ][ 'totalTime' ] = main.scaleTopoFunction.getInfoFromLog( main, main.searchTerm[ 'start' ], 'first', main.searchTerm[ 'end' ], 'last', index=i, funcMode='TD' )
            # Calculate switch connection time
            main.allinfo[ 0 ][ 'info' + str( i ) ][ 'swConnection' ] = main.scaleTopoFunction.getInfoFromLog( main, main.searchTerm[ 'start' ], 'first', main.searchTerm[ 'start' ], 'last', index=i, funcMode='TD' )
            # Calculate the time from last switch connection to the last role request
            main.allinfo[ 0 ][ 'info' + str( i ) ][ 'lastSwToLastRr' ] = main.scaleTopoFunction.compareTimeDiffWithRoleRequest( main, main.searchTerm[ 'start' ], 'last', index=i )
            # Calculate the time from the last role request to the last topology
            main.allinfo[ 0 ][ 'info' + str( i ) ][ 'lastRrToLastTopology' ] = main.scaleTopoFunction.compareTimeDiffWithRoleRequest( main, main.searchTerm[ 'end' ], 'last', index=i )
            # Calculate the disconnecti rate
            main.allinfo[ 0 ][ 'info' + str( i ) ][ 'disconnectRate' ] = main.scaleTopoFunction.getInfoFromLog( main, main.searchTerm[ 'Disconnect' ], 'num', main.searchTerm[ 'start' ], 'num', index=i, funcMode='DR' )
        main.log.debug( "The data is " + str( main.allinfo[ 0 ] ) )
        if -1 in main.allinfo[ 0 ][ 'info0' ].values() or -1 in main.allinfo[ 0 ][ 'info1' ].values() or -1 in main.allinfo[ 0 ][ 'info2' ].values():
            utilities.assert_equals( expect=main.TRUE,
                                     actual=main.FALSE,
                                     onpass="Everything installed properly to the ONOS.",
                                     onfail="Something happened to ONOS. Skip the rest of the steps." )
            main.postResult = False
        else:
            main.case( "Verifying topology: TORUS %sx%s" % ( main.currScale, main.currScale ) )
            main.caseExplanation = "Pinging all hosts and comparing topology " +\
                    "elements between Mininet and ONOS"

            main.log.info( "Gathering topology information" )
            time.sleep( main.MNSleep )

            compareRetry = 0
            main.step( "Checking if ONOS is stable" )
            main.scaleTopoFunction.checkingONOSStablility( main )

            if main.postResult:
                main.step( "Comparing MN topology to ONOS topology" )

                compareRetry = 0
                while compareRetry < 2:
                    stepResult = main.TRUE
                    currentDevicesResult = main.TRUE
                    currentLinksResult = main.TRUE
                    # While loop for retry
                    devices = main.topoRelated.getAll( "devices", kwargs={ 'timeout': main.getTopoTime } )
                    ports = main.topoRelated.getAll( "ports", kwargs={ 'timeout': main.getTopoTime } )
                    links = main.topoRelated.getAll( "links", kwargs={ 'timeout': main.getTopoTime } )
                    if None in devices or None in ports or None in links:
                        main.log.warn( "Something went wrong. Retrying..." )
                        time.sleep( 20 )
                        stepResult = main.FALSE
                        compareRetry += 1
                        continue
                    mnSwitches = main.Mininet1.getSwitches( updateTimeout=main.basicMNTime + int( main.currScale ) * main.MNupdateTime )
                    main.log.info( "Comparing switches..." )
                    devicePool = []
                    for controller in range( len( main.Cluster.active() ) ):
                        t = main.Thread( target=main.topoRelated.compareDevicePort,
                                         threadID=main.threadID,
                                         name="Compare-Device-Port",
                                         args=[ main.Mininet1, controller,
                                                mnSwitches,
                                                devices, ports ] )
                        devicePool.append( t )
                        t.start()
                        main.threadID = main.threadID + 1

                    mnLinks = main.Mininet1.getLinks( timeout=main.basicMNTime + int( main.currScale ) * main.MNLinksTime,
                                                      updateTimeout=main.basicMNTime + int(main.currScale) * main.MNupdateTime )
                    main.log.info( "Comparing links..." )
                    linkPool = []
                    for controller in range( len( main.Cluster.active() ) ):
                        t = main.Thread( target=main.topoRelated.compareBase,
                                         threadID=main.threadID,
                                         name="Compare-Link-Result",
                                         args=[ links, controller,
                                                main.Mininet1.compareLinks,
                                                [ mnSwitches, mnLinks ] ] )
                        linkPool.append( t )
                        t.start()
                        main.threadID = main.threadID + 1

                    for t in devicePool:
                        t.join()
                        currentDevicesResult = currentDevicesResult and t.result
                    for t in linkPool:
                        t.join()
                        currentLinksResult = currentLinksResult and t.result
                    stepResult = stepResult and currentDevicesResult and currentLinksResult
                    if stepResult:
                        break
                    compareRetry += 1
                utilities.assert_equals( expect=main.TRUE,
                                         actual=stepResult,
                                         onpass=" Topology match Mininet",
                                         onfail="ONOS Topology doesn't match Mininet" )
                main.scaleTopoFunction.checkingONOSStablility( main )
                if stepResult and main.postResult:
                    if main.hostDiscover:
                        hostList = []
                        for i in range( 1, int( main.currScale ) + 1 ):
                            for j in range( 1, int( main.currScale ) + 1 ):
                                # Generate host list
                                hoststr = "h" + str( i ) + "x" + str( j )
                                hostList.append( hoststr )
                        for i in range( len( hostList ) ):
                            main.topo.sendArpPackage( main, hostList[ i ] )
                        time.sleep( 20 )
                        totalHost = main.topo.getHostNum( main )
                        if totalHost == int( main.currScale ) * int( main.currScale ):
                            main.log.info( "Discovered all hosts" )
                            stepResult = stepResult and main.TRUE
                        else:
                            main.log.warn( "Some hosts ware not discovered by ONOS... Topology doesn't match!" )
                            stepResult = main.FALSE
                        utilities.assert_equals( expect=main.TRUE,
                                                 actual=stepResult,
                                                 onpass=" Topology match Mininet",
                                                 onfail="ONOS Topology doesn't match Mininet" )
                    main.log.info( "Finished this iteration, continue to scale next topology." )
                else:
                    utilities.assert_equals( expect=main.TRUE,
                                             actual=main.FALSE,
                                             onpass="ONOS is stable.",
                                             onfail="Something happened to ONOS. Skip the rest of the steps." )
                    main.postResult = False

    def CASE100( self, main ):
        """
           Bring Down node 3
        """
        main.case( "Bring ONOS node 3 down: TORUS %sx%s" % ( main.currScale, main.currScale ) )
        main.caseExplanation = "Balance masters to make sure " +\
                        "each controller has some devices and " +\
                        "stop ONOS node 3 service. "

        stepResult = main.FALSE
        main.step( "Bringing down node 3" )
        # Always bring down the third node
        main.deadNode = 2
        # Printing purposes
        node = main.deadNode + 1
        main.log.info( "Stopping node %s" % node )
        stepResult = main.ONOSbench.onosStop( main.Cluster.active( main.deadNode ).ipAddress )
        main.log.info( "Removing dead node from list of active nodes" )
        main.Cluster.runningNodes[ main.deadNode ].active = False

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully bring down node 3",
                                 onfail="Failed to bring down node 3" )

    def CASE200( self, main ):
        """
            Bring up onos node
        """
        main.case( "Bring ONOS node 3 up: TORUS %sx%s" % ( main.currScale, main.currScale ) )
        main.caseExplanation = "Bring node 3 back up and balance the masters"
        ctrl = main.Cluster.runningNodes[ main.deadNode ]
        node = main.deadNode + 1
        main.log.info( "Starting node %s" % node )
        stepResult = main.ONOSbench.onosStart( ctrl.ipAddress )
        main.log.info( "Starting onos cli" )
        stepResult = stepResult and \
                     ctrl.CLI.startOnosCli( ctrl.ipAddress )
        main.log.info( "Adding previously dead node to list of active nodes" )
        ctrl.active = True

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully brought up onos node %s" % node,
                                 onfail="Failed to bring up onos node %s" % node )

        time.sleep( main.nodeSleep )

    def CASE300( self, main ):
        """
            Balancing Masters
        """
        time.sleep( main.balanceSleep )
        main.step( "Balancing Masters" )

        stepResult = main.FALSE
        if main.Cluster.active():
            stepResult = utilities.retry( main.Cluster.next().CLI.balanceMasters,
                                          main.FALSE,
                                          [],
                                          sleep=3,
                                          attempts=3 )
        else:
            main.log.error( "List of active nodes is empty" )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Balance masters was successfull",
                                 onfail="Failed to balance masters" )
        time.sleep( main.balanceSleep )

    def CASE1000( self, main ):
        """
            Report errors/warnings/exceptions
        """
        # Compare the slowest Node through total time of each node
        if main.postResult:
            slowestNode = 0
            slowestTotalTime = 0
            # Second capture
            for i in range( 3 ):
                # Calculate total time
                main.allinfo[ 1 ][ 'info' + str( i ) ][ 'totalTime' ] = main.scaleTopoFunction.getInfoFromLog( main,
                                                                                                               main.searchTerm[ 'start' ],
                                                                                                               'first',
                                                                                                               main.searchTerm[ 'end' ],
                                                                                                               'last',
                                                                                                               index=i,
                                                                                                               funcMode='TD' )
                # Compare the total time
                if main.allinfo[ 1 ][ 'info' + str( i ) ][ 'totalTime' ] > slowestTotalTime:
                    slowestTotalTime = main.allinfo[ 1 ][ 'info' + str( i ) ][ 'totalTime' ]
                    slowestNode = i
                # Calculate switch connection time
                main.allinfo[ 1 ][ 'info' + str( i ) ][ 'swConnection' ] = main.scaleTopoFunction.getInfoFromLog( main,
                                                                                                                  main.searchTerm[ 'start' ],
                                                                                                                  'first',
                                                                                                                  main.searchTerm[ 'start' ],
                                                                                                                  'last',
                                                                                                                  index=i,
                                                                                                                  funcMode='TD' )
                # Calculate the time from last switch connection to the last role request
                main.allinfo[ 1 ][ 'info' + str( i ) ][ 'lastSwToLastRr' ] = main.scaleTopoFunction.compareTimeDiffWithRoleRequest( main,
                                                                                                                                    main.searchTerm[ 'start' ],
                                                                                                                                    'last',
                                                                                                                                    index=i )
                # Calculate the time from the last role request to the last topology
                main.allinfo[ 1 ][ 'info' + str( i ) ][ 'lastRrToLastTopology' ] = main.scaleTopoFunction.compareTimeDiffWithRoleRequest( main,
                                                                                                                                          main.searchTerm[ 'end' ],
                                                                                                                                          'last',
                                                                                                                                          index=i )
                # Calculate the disconnecti rate
                main.allinfo[ 1 ][ 'info' + str( i ) ][ 'disconnectRate' ] = main.scaleTopoFunction.getInfoFromLog( main,
                                                                                                                    main.searchTerm[ 'Disconnect' ],
                                                                                                                    'num',
                                                                                                                    main.searchTerm[ 'start' ],
                                                                                                                    'num',
                                                                                                                    index=i,
                                                                                                                    funcMode='DR' )

            if ( main.allinfo[ 0 ] != main.allinfo[ 1 ] ):
                main.log.error( "The results of two capture are different!" )
            main.log.debug( "The data is " + str( main.allinfo ) )
            if main.writeData != -1:
                main.maxScale = main.currScale
                main.log.info( "Write the date into database" )
                # write the date into data base
                with open( main.dbFilePath, "a" ) as dbFile:
                    temp = str( main.currScale )
                    temp += ",'baremetal1'"
                    # put result from second capture into data base
                    temp += "," + str( "%.2f" % main.allinfo[ 1 ][ 'info' + str( slowestNode ) ][ 'totalTime' ] )
                    temp += "," + str( "%.2f" % main.allinfo[ 1 ][ 'info' + str( slowestNode ) ][ 'swConnection' ] )
                    temp += "," + str( "%.2f" % main.allinfo[ 1 ][ 'info' + str( slowestNode ) ][ 'lastSwToLastRr' ] )
                    temp += "," + str( "%.2f" % main.allinfo[ 1 ][ 'info' + str( slowestNode ) ][ 'lastRrToLastTopology' ] )
                    temp += "," + str( "%.2f" % main.allinfo[ 1 ][ 'info' + str( slowestNode ) ][ 'disconnectRate' ] )
                    temp += "\n"
                    dbFile.write( temp )
            else:
                main.log.error( "The data from log is wrong!" )
            main.writeData = 1
            main.case( "Checking logs for errors, warnings, and exceptions" )
            main.log.info( "Error report: \n" )
            main.ONOSbench.logReport( main.Cluster.active( 0 ).ipAddress,
                                                                [ "INFO",
                                                                  "FOLLOWER",
                                                                  "WARN",
                                                                  "flow",
                                                                  "ERROR",
                                                                  "Except" ],
                                                                  "s" )

    def CASE1001( self, main ):
        """
            Write abnormal test results to alarm log
        """
        threshold = int( main.params[ 'ALARM' ][ 'minMaxScale' ] )
        if int( main.maxScale ) < threshold:
            main.log.alarm( "Max scale: {}x{} < {}x{}".format( main.maxScale, main.maxScale,
                                                               threshold, threshold ) )
