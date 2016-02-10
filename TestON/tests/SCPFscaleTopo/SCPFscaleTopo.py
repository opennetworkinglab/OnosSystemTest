
# Testing network scalability, this test suite scales up a network topology
# using mininet and verifies ONOS stability

class SCPFscaleTopo:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        import time
        import os
        import imp
        import re

        """
        - Construct tests variables
        - GIT ( optional )
            - Checkout ONOS master branch
            - Pull latest ONOS code
        - Building ONOS ( optional )
            - Install ONOS package
            - Build ONOS package
        """

        main.case( "Constructing test variables" )
        main.step( "Constructing test variables" )
        stepResult = main.FALSE

        main.testOnDirectory = os.path.dirname( os.getcwd ( ) )
        main.apps = main.params[ 'ENV' ][ 'cellApps' ]
        gitBranch = main.params[ 'GIT' ][ 'branch' ]
        main.dependencyPath = main.testOnDirectory + \
                              main.params[ 'DEPENDENCY' ][ 'path' ]
        main.multiovs = main.params[ 'DEPENDENCY' ][ 'multiovs' ]
        main.topoName = main.params[ 'TOPOLOGY' ][ 'topology' ]
        main.numCtrls = int( main.params[ 'CTRL' ][ 'numCtrls' ] )
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
        gitPull = main.params[ 'GIT' ][ 'pull' ]
        main.homeDir = os.path.expanduser('~')
        main.cellData = {} # for creating cell file
        main.hostsData = {}
        main.CLIs = []
        main.ONOSip = []
        main.activeNodes = []
        main.ONOSip = main.ONOSbench.getOnosIps()

        for i in range(main.numCtrls):
                main.CLIs.append( getattr( main, 'ONOScli%s' % (i+1) ) )

        main.startUp = imp.load_source( wrapperFile1,
                                        main.dependencyPath +
                                        wrapperFile1 +
                                        ".py" )

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

        if main.CLIs:
                stepResult = main.TRUE
        else:
            main.log.error( "Did not properly created list of " +
                            "ONOS CLI handle" )
            stepResult = main.FALSE

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully construct " +
                                        "test variables ",
                                 onfail="Failed to construct test variables" )

        if gitPull == 'True':
            main.step( "Building ONOS in " + gitBranch + " branch" )
            onosBuildResult = main.startUp.onosBuild( main, gitBranch )
            stepResult = onosBuildResult
            utilities.assert_equals( expect=main.TRUE,
                                     actual=stepResult,
                                     onpass="Successfully compiled " +
                                            "latest ONOS",
                                     onfail="Failed to compile " +
                                            "latest ONOS" )
        else:
            main.log.warn( "Did not pull new code so skipping mvn " +
                           "clean install" )


    def CASE2( self, main):
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

        main.case( "Starting up " + str( main.numCtrls ) +
                   " node(s) ONOS cluster" )
        main.caseExplanation = "Set up ONOS with " + str( main.numCtrls ) +\
                                " node(s) ONOS cluster"



        #kill off all onos processes
        main.log.info( "Safety check, killing all ONOS processes" +
                       " before initiating environment setup" )

        for i in range( main.numCtrls ):
            main.ONOSbench.onosDie( main.ONOSip[ i ] )

        tempOnosIp = []
        for i in range( main.numCtrls ):
            tempOnosIp.append( main.ONOSip[i] )

        main.ONOSbench.createCellFile( main.ONOSbench.ip_address,
                                       "temp", main.Mininet1.ip_address,
                                       main.apps, tempOnosIp )

        main.step( "Apply cell to environment" )
        cellResult = main.ONOSbench.setCell( "temp" )
        verifyResult = main.ONOSbench.verifyCell()
        stepResult = cellResult and verifyResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully applied cell to " + \
                                        "environment",
                                 onfail="Failed to apply cell to environment " )

        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.onosPackage()
        stepResult = packageResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully created ONOS package",
                                 onfail="Failed to create ONOS package" )

        time.sleep( main.startUpSleep )
        main.step( "Uninstalling ONOS package" )
        onosUninstallResult = main.TRUE
        for ip in main.ONOSip:
            onosUninstallResult = onosUninstallResult and \
                    main.ONOSbench.onosUninstall( nodeIp=ip )
        stepResult = onosUninstallResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully uninstalled ONOS package",
                                 onfail="Failed to uninstall ONOS package" )

        time.sleep( main.startUpSleep )
        main.step( "Installing ONOS package" )
        onosInstallResult = main.TRUE
        for i in range( main.numCtrls ):
            onosInstallResult = onosInstallResult and \
                    main.ONOSbench.onosInstall( node=main.ONOSip[ i ] )
        stepResult = onosInstallResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully installed ONOS package",
                                 onfail="Failed to install ONOS package" )

        time.sleep( main.startUpSleep )
        main.step( "Starting ONOS service" )
        stopResult = main.TRUE
        startResult = main.TRUE
        onosIsUp = main.TRUE

        for i in range( main.numCtrls ):
            onosIsUp = onosIsUp and main.ONOSbench.isup( main.ONOSip[ i ] )
        if onosIsUp == main.TRUE:
            main.log.report( "ONOS instance is up and ready" )
        else:
            main.log.report( "ONOS instance may not be up, stop and " +
                             "start ONOS again " )

            for i in range( main.numCtrls ):
                stopResult = stopResult and \
                        main.ONOSbench.onosStop( main.ONOSip[ i ] )
            for i in range( main.numCtrls ):
                startResult = startResult and \
                        main.ONOSbench.onosStart( main.ONOSip[ i ] )
        stepResult = onosIsUp and stopResult and startResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="ONOS service is ready",
                                 onfail="ONOS service did not start properly" )

        main.step( "Start ONOS cli" )
        cliResult = main.TRUE
        for i in range( main.numCtrls ):
            cliResult = cliResult and \
                        main.CLIs[ i ].startOnosCli( main.ONOSip[ i ] )
            main.activeNodes.append( i )
        stepResult = cliResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully start ONOS cli",
                                 onfail="Failed to start ONOS cli" )


    def CASE10( self, main ):
        """
            Starting up torus topology
        """
        import json

        main.case( "Starting up Mininet and verifying topology" )
        main.caseExplanation = "Starting Mininet with a scalling topology and " +\
                "comparing topology elements between Mininet and ONOS"

        main.log.info( "Checking if mininet is already running" )
        if len( main.topoScale ) < main.topoScaleSize:
            main.log.info( "Mininet is already running. Stopping mininet." )
            main.Mininet1.stopNet()
            time.sleep(main.MNSleep)
        else:
            main.log.info( "Mininet was not running" )

        if main.topoScale:
            main.currScale = main.topoScale.pop(0)
        else: main.log.error( "topology scale is empty" )


        main.step( "Starting up TORUS %sx%s topology" % (main.currScale, main.currScale) )

        main.log.info( "Constructing Mininet command" )
        mnCmd = " mn --custom " + main.Mininet1.home + main.multiovs +\
                " --switch ovsm --topo " + main.topoName + ","+ main.currScale + "," + main.currScale

        for i in range( main.numCtrls ):
                mnCmd += " --controller remote,ip=" + main.ONOSip[ i ]

        stepResult = main.Mininet1.startNet(mnCmd=mnCmd)
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass=main.topoName +
                                    " topology started successfully",
                                 onfail=main.topoName +
                                    " topology failed to start" )

        time.sleep( main.MNSleep )

    def CASE11( self, main ):
        """
            Pingall, and compare topo
            We don't care the pingall result,
            if the topology is same, then Pass.
        """
        import json

        main.case( "Verifying topology: TORUS %sx%s" % (main.currScale, main.currScale) )
        main.caseExplanation = "Pinging all hosts and comparing topology " +\
                "elements between Mininet and ONOS"

        main.log.info( "Pinging all hosts" )

        # the pingall timeout is depend on the number of total host
        pingTimeout = int( main.pingTimeout * float( int(main.currScale) * int(main.currScale ) ) )
        pingResult = main.Mininet1.pingall( pingTimeout )

        main.log.info( "Gathering topology information" )

        time.sleep( main.MNSleep )

        devicesResults = main.TRUE
        linksResults = main.TRUE
        hostsResults = main.TRUE
        stepResult = main.TRUE
        devices = main.topo.getAllDevices( main )
        hosts = main.topo.getAllHosts( main )
        ports = main.topo.getAllPorts( main )
        links = main.topo.getAllLinks( main )
        clusters = main.topo.getAllClusters( main )
        mnSwitches = main.Mininet1.getSwitches()
        mnLinks = main.Mininet1.getLinks()
        mnHosts = main.Mininet1.getHosts()

        main.step( "Comparing MN topology to ONOS topology" )
        for controller in range(len(main.activeNodes)):
            controllerStr = str( main.activeNodes[controller] + 1 )
            if devices[ controller ] and ports[ controller ] and\
                "Error" not in devices[ controller ] and\
                "Error" not in ports[ controller ]:

                currentDevicesResult = main.Mininet1.compareSwitches(
                        mnSwitches,
                        json.loads( devices[ controller ] ),
                        json.loads( ports[ controller ] ) )
            else:
                currentDevicesResult = main.FALSE
 
            if links[ controller ] and "Error" not in links[ controller ]:
                currentLinksResult = main.Mininet1.compareLinks(
                        mnSwitches, mnLinks,
                        json.loads( links[ controller ] ) )
            else:
                currentLinksResult = main.FALSE

            if hosts[ controller ] or "Error" not in hosts[ controller ]:
                currentHostsResult = main.Mininet1.compareHosts(
                        mnHosts,
                        json.loads( hosts[ controller ] ) )
            else:
                currentHostsResult = main.FALSE

            stepResult = stepResult and currentDevicesResult and currentLinksResult and currentHostsResult

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass=" Topology match Mininet",
                                 onfail="ONOS" + controllerStr +
                                 " Topology doesn't match Mininet" )


    def CASE100( self, main ):
        '''
            Balance masters, ping and bring third ONOS node down
        '''

        main.case("Balancing Masters and bring ONOS node 3 down: TORUS %sx%s" % (main.currScale, main.currScale))
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
        stepResult = main.ONOSbench.onosStop( main.ONOSip[ main.deadNode ] )
        main.log.info( "Removing dead node from list of active nodes" )
        main.activeNodes.pop( main.deadNode )



    def CASE200( self, main ):
        '''
            Bring up onos node and balance masters
        '''

        main.case("Bring ONOS node 3 up and balance masters: TORUS %sx%s" % (main.currScale, main.currScale))
        main.caseExplanation = "Bring node 3 back up and balance the masters"

        node = main.deadNode + 1
        main.log.info( "Starting node %s" % node )
        stepResult = main.ONOSbench.onosStart( main.ONOSip[ main.deadNode ] )
        main.log.info( "Starting onos cli" )
        stepResult = stepResult and main.CLIs[ main.deadNode ].startOnosCli( main.ONOSip[ main.deadNode ] )

        main.log.info( "Adding previously dead node to list of active nodes" )
        main.activeNodes.append( main.deadNode )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully brought up onos node %s" % node,
                                 onfail="Failed to bring up onos node %s" % node )


        time.sleep(main.nodeSleep)

    def CASE300( self, main ):
        '''

            Balancing Masters
        '''
        time.sleep(main.balanceSleep)
        main.step( "Balancing Masters" )

        stepResult = main.FALSE
        if main.activeNodes:
            controller = main.activeNodes[0]
            stepResult = utilities.retry( main.CLIs[controller].balanceMasters,
                                          main.FALSE,
                                          [],
                                          sleep=3,
                                          attempts=3 )

        else:
            main.log.error( "List of active nodes is empty" )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Balance masters was successfull",
                                 onfail="Failed to balance masters")
        time.sleep(main.balanceSleep)

    def CASE1000( self, main ):
        '''
            Report errors/warnings/exceptions
        '''
        main.case( "Checking logs for errors, warnings, and exceptions" )
        main.log.info("Error report: \n" )
        main.ONOSbench.logReport( main.ONOSip[ 0 ],
                                                            [ "INFO",
                                                              "FOLLOWER",
                                                              "WARN",
                                                              "flow",
                                                              "ERROR",
                                                              "Except" ],
                                                            "s" )
