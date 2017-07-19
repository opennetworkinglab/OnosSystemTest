"""
Testing various connectivity failures for VPLS.

CASE1: Startup.
CASE2: Load VPLS topology and configurations from demo script.
CASE50: Initial connectivity test.
CASE100: Bring down 1 host at a time and test connectivity.
CASE200: Bring down 1 switch at a time and test connectivity.
CASE300: Stop 1 ONOS node at a time and test connectivity.
CASE310: Kill 1 ONOS node at a time and test connectivity.
CASE400: Bring down 1 link at a time and test connectivity.
"""

class VPLSfailsafe:

    def __init__( self ):
        self.default = ''


    def CASE1( self, main ):
        """
        CASE1 is to compile ONOS and push it to the test machines

        Startup sequence:
        cell <name>
        onos-verify-cell
        NOTE: temporary - onos-remove-raft-logs
        onos-uninstall
        start mininet
        git pull
        mvn clean install
        onos-package
        onos-install -f
        onos-wait-for-start
        start cli sessions
        start tcpdump
        """
        import imp
        import time
        import json

        main.case( "Setting up test environment" )
        main.caseExplanation = "Setup the test environment including " +\
                                "installing ONOS, starting Mininet and ONOS" +\
                                "cli sessions."

        # load some variables from the params file
        cellName = main.params[ 'ENV' ][ 'cellName' ]

        main.numCtrls = int( main.params[ 'num_controllers' ] )

        ofPort = main.params[ 'CTRL' ][ 'port' ]

        main.timeSleep = int( main.params[ 'RETRY' ][ 'sleep' ] )
        main.numAttempts = int( main.params[ 'RETRY' ][ 'attempts' ] )

        main.CLIs = []
        main.RESTs = []
        main.nodes = []
        ipList = []
        for i in range( 1, main.numCtrls + 1 ):
            try:
                main.CLIs.append( getattr( main, 'ONOScli' + str( i ) ) )
                main.RESTs.append( getattr( main, 'ONOSrest' + str( i ) ) )
                main.nodes.append( getattr( main, 'ONOS' + str( i ) ) )
                ipList.append( main.nodes[ -1 ].ip_address )
            except AttributeError:
                break

        main.step( "Create cell file" )
        cellAppString = main.params[ 'ENV' ][ 'cellApps' ]
        main.ONOSbench.createCellFile( main.ONOSbench.ip_address, cellName,
                                       main.Mininet1.ip_address,
                                       cellAppString, ipList, main.ONOScli1.karafUser )
        main.step( "Applying cell variable to environment" )
        main.cellResult = main.ONOSbench.setCell( cellName )
        verifyResult = main.ONOSbench.verifyCell()

        main.log.info( "Uninstalling ONOS" )
        for node in main.nodes:
            main.ONOSbench.onosUninstall( node.ip_address )

        # Make sure ONOS is DEAD
        main.log.info( "Killing any ONOS processes" )
        killResults = main.TRUE
        for node in main.nodes:
            killed = main.ONOSbench.onosKill( node.ip_address )
            killResults = killResults and killed

        main.step( "Starting Mininet" )

        # scp topo file to mininet
        # TODO: move to params?
        topoName = "vpls"
        topoFile = "vpls.py"
        filePath = main.ONOSbench.home + "/tools/test/topos/"
        main.ONOSbench.scp( main.Mininet1,
                            filePath + topoFile,
                            main.Mininet1.home,
                            direction="to" )
        topo = " --custom " + main.Mininet1.home + topoFile + " --topo " + topoName
        args = " --switch ovs,protocols=OpenFlow13"
        for node in main.nodes:
            args += " --controller=remote,ip=" + node.ip_address
        mnCmd = "sudo mn" + topo + args
        mnResult = main.Mininet1.startNet( mnCmd=mnCmd )
        utilities.assert_equals( expect=main.TRUE, actual=mnResult,
                                 onpass="Mininet Started",
                                 onfail="Error starting Mininet" )

        main.ONOSbench.getVersion( report=True )

        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.buckBuild()
        utilities.assert_equals( expect=main.TRUE, actual=packageResult,
                                 onpass="ONOS package successful",
                                 onfail="ONOS package failed" )

        main.step( "Installing ONOS package" )
        onosInstallResult = main.TRUE
        for node in main.nodes:
            tmpResult = main.ONOSbench.onosInstall( options="-f",
                                                    node=node.ip_address )
            onosInstallResult = onosInstallResult and tmpResult
        utilities.assert_equals( expect=main.TRUE, actual=onosInstallResult,
                                 onpass="ONOS install successful",
                                 onfail="ONOS install failed" )

        main.step( "Set up ONOS secure SSH" )
        secureSshResult = main.TRUE
        for node in main.nodes:
            secureSshResult = secureSshResult and main.ONOSbench.onosSecureSSH( node=node.ip_address )
        utilities.assert_equals( expect=main.TRUE, actual=secureSshResult,
                                 onpass="Test step PASS",
                                 onfail="Test step FAIL" )

        main.step( "Checking if ONOS is up yet" )
        for i in range( 2 ):
            onosIsupResult = main.TRUE
            for node in main.nodes:
                started = main.ONOSbench.isup( node.ip_address )
                if not started:
                    main.log.error( node.name + " hasn't started" )
                onosIsupResult = onosIsupResult and started
            if onosIsupResult == main.TRUE:
                break
        utilities.assert_equals( expect=main.TRUE, actual=onosIsupResult,
                                 onpass="ONOS startup successful",
                                 onfail="ONOS startup failed" )

        main.step( "Starting ONOS CLI sessions" )
        cliResults = main.TRUE
        threads = []
        for i in range( main.numCtrls ):
            t = main.Thread( target=main.CLIs[ i ].startOnosCli,
                             name="startOnosCli-" + str( i ),
                             args=[ main.nodes[ i ].ip_address ] )
            threads.append( t )
            t.start()

        for t in threads:
            t.join()
            cliResults = cliResults and t.result
        utilities.assert_equals( expect=main.TRUE, actual=cliResults,
                                 onpass="ONOS cli startup successful",
                                 onfail="ONOS cli startup failed" )

        main.activeNodes = [ i for i in range( 0, len( main.CLIs ) ) ]

        main.step( "Activate apps defined in the params file" )
        # get data from the params
        apps = main.params.get( 'apps' )
        if apps:
            apps = apps.split( ',' )
            main.log.warn( apps )
            activateResult = True
            for app in apps:
                main.CLIs[ 0 ].app( app, "Activate" )
            # TODO: check this worked
            time.sleep( SLEEP )  # wait for apps to activate
            for app in apps:
                state = main.CLIs[ 0 ].appStatus( app )
                if state == "ACTIVE":
                    activateResult = activateResult and True
                else:
                    main.log.error( "{} is in {} state".format( app, state ) )
                    activateResult = False
            utilities.assert_equals( expect=True,
                                     actual=activateResult,
                                     onpass="Successfully activated apps",
                                     onfail="Failed to activate apps" )
        else:
            main.log.warn( "No apps were specified to be loaded after startup" )

        main.step( "Set ONOS configurations" )
        config = main.params.get( 'ONOS_Configuration' )
        if config:
            main.log.debug( config )
            checkResult = main.TRUE
            for component in config:
                for setting in config[ component ]:
                    value = config[ component ][ setting ]
                    check = main.CLIs[ 0 ].setCfg( component, setting, value )
                    main.log.info( "Value was changed? {}".format( main.TRUE == check ) )
                    checkResult = check and checkResult
            utilities.assert_equals( expect=main.TRUE,
                                     actual=checkResult,
                                     onpass="Successfully set config",
                                     onfail="Failed to set config" )
        else:
            main.log.warn( "No configurations were specified to be changed after startup" )

        main.step( "App Ids check" )
        appCheck = main.TRUE
        threads = []
        for i in main.activeNodes:
            t = main.Thread( target=main.CLIs[ i ].appToIDCheck,
                             name="appToIDCheck-" + str( i ),
                             args=[] )
            threads.append( t )
            t.start()

        for t in threads:
            t.join()
            appCheck = appCheck and t.result
        if appCheck != main.TRUE:
            main.log.warn( main.CLIs[ 0 ].apps() )
            main.log.warn( main.CLIs[ 0 ].appIDs() )
        utilities.assert_equals( expect=main.TRUE, actual=appCheck,
                                 onpass="App Ids seem to be correct",
                                 onfail="Something is wrong with app Ids" )

    def CASE2( self, main ):
        """
        Load and test vpls configurations from json configuration file
        """
        import os.path
        from tests.USECASE.VPLS.dependencies import vpls

        main.vpls = vpls
        pprint = main.ONOSrest1.pprint
        hosts = int( main.params[ 'vpls' ][ 'hosts' ] )
        SLEEP = int( main.params[ 'SLEEP' ][ 'netcfg' ] )

        main.step( "Discover hosts using pings" )
        for i in range( 1, hosts + 1 ):
            src = "h" + str( i )
            for j in range( 1, hosts + 1 ):
                if j == i:
                    continue
                dst = "h" + str( j )
            pingResult = main.Mininet1.pingHost( SRC=src, TARGET=dst )

        main.step( "Load VPLS configurations" )
        fileName = main.params[ 'DEPENDENCY' ][ 'topology' ]
        app = main.params[ 'vpls' ][ 'name' ]

        loadVPLSResult = main.ONOSbench.onosNetCfg( main.nodes[ 0 ].ip_address, "", fileName )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=loadVPLSResult,
                                 onpass="Loaded vpls configuration.",
                                 onfail="Failed to load vpls configuration.")

        # Time for netcfg to load data
        time.sleep( SLEEP )

        main.step( "Check VPLS configurations" )
        # 'Master' copy of test configuration
        try:
            with open( os.path.expanduser( fileName ) ) as dataFile:
                originalCfg = json.load( dataFile )
                main.vplsConfig = originalCfg[ 'apps' ].get( app ).get( 'vpls' ).get( 'vplsList' )
        except Exception as e:
            main.log.error( "Error loading config file: {}".format( e ) )
        if main.vplsConfig:
            result = True
        else:
            result = False
        utilities.assert_equals( expect=True,
                                 actual=result,
                                 onpass="Check vpls configuration succeeded.",
                                 onfail="Check vpls configuration failed." )

        main.step( "Check interface configurations" )
        result = False
        getPorts = utilities.retry( f=main.ONOSrest1.getNetCfg,
                                    retValue=False,
                                    kwargs={"subjectClass":"ports"},
                                    sleep=SLEEP )
        onosCfg = pprint( getPorts )
        sentCfg = pprint( originalCfg.get( "ports" ) )

        if onosCfg == sentCfg:
            main.log.info( "ONOS interfaces NetCfg matches what was sent" )
            result = True
        else:
            main.log.error( "ONOS interfaces NetCfg doesn't match what was sent" )
            main.log.debug( "ONOS config: {}".format( onosCfg ) )
            main.log.debug( "Sent config: {}".format( sentCfg ) )
        utilities.assert_equals( expect=True,
                                 actual=result,
                                 onpass="Net Cfg added for interfaces",
                                 onfail="Net Cfg not added for interfaces" )

        # Run a bunch of checks to verify functionality based on configs
        vpls.verify( main )

        # This is to avoid a race condition in pushing netcfg's.
        main.step( "Loading vpls configuration in case any configuration was missed." )
        loadVPLSResult = main.ONOSbench.onosNetCfg( main.nodes[ 0 ].ip_address, "", fileName )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=loadVPLSResult,
                                 onpass="Loaded vpls configuration.",
                                 onfail="Failed to load vpls configuration." )



    def CASE50( self, main ):
        """
        Initial connectivity check
        """
        main.case( "Check connectivity before running all other tests." )

        # Check connectivity before running all other tests
        connectCheckResult = main.vpls.testConnectivityVpls( main )
        utilities.assert_equals( expect=main.TRUE, actual=connectCheckResult,
                                 onpass="Connectivity is as expected.",
                                 onfail="Connectivity is NOT as expected." )


    def CASE100( self, main ):
        """
        Bring down 1 host at a time and test connectivity
        """
        assert vpls, "vpls not defined"

        main.case( "Bring down one host at a time and test connectivity." )
        result = main.TRUE

        for i in range( 1, hosts + 1 ):

            stri = str( i )

            # Bring host down
            main.step( "Kill link between s" + stri + " and h" + stri + "." )
            linkDownResult = main.Mininet1.link( END1="s" + stri, END2="h" + stri, OPTION="down" )

            # Check if link was successfully down'd
            utilities.assert_equals( expect=main.TRUE, actual=linkDownResult,
                                     onpass="Link down successful.",
                                     onfail="Failed to bring link down." )
            result = result and linkDownResult

            # Check connectivity
            connectivityResult = vpls.testConnectivityVpls( main, blacklist=[ "h" + stri ] )
            result = result and connectivityResult

            # Bring host up
            main.step( "Re-adding link between s" + stri + " and h" + stri + "." )
            linkUpResult = main.Mininet1.link( END1="s" + stri, END2="h" + stri, OPTION="up" )

            # Check if link was successfully re-added
            utilities.assert_equals( expect=main.TRUE, actual=linkUpResult,
                                     onpass="Link up successful.",
                                     onfail="Failed to bring link up." )
            result = result and linkUpResult

            # Discover host using ping
            main.step( "Discover h" + stri + " using ping." )
            main.Mininet1.pingHost( SRC="h" + stri, TARGET="h" + str( ( i % hosts ) + 1 ) )

            # Check connectivity
            connectivityResult = vpls.testConnectivityVpls( main )
            result = result and connectivityResult

        utilities.assert_equals( expect=main.TRUE, actual=result,
                                 onpass="Connectivity is as expected.",
                                 onfail="Connectivity is NOT as expected.")

    def CASE200( self, main ):
        """
        Bring down 1 switch at a time and test connectivity
        """
        assert vpls, "vpls not defined"

        main.case( "Bring down one switch at a time and test connectivity." )
        links = main.Mininet1.getLinks( )  # Obtain links here
        result = main.TRUE

        for i in range( 5, hosts + 1 ):

            stri = str( i )

            # Bring switch down
            main.step( "Delete s" + stri + ".")
            delSwitchResult = main.Mininet1.delSwitch( sw="s" + stri )

            # Check if switch was deleted
            utilities.assert_equals( expect=main.TRUE, actual=delSwitchResult,
                                     onpass="Successfully deleted switch.",
                                     onfail="Failed to delete switch." )
            result = result and delSwitchResult

            # Check connectivity
            connectivityResult = vpls.testConnectivityVpls( main, blacklist=[ "h" + stri ] )
            result = result and connectivityResult

            # Bring switch up
            main.step( "Add s" + stri + ".")
            addSwitchResult = main.Mininet1.addSwitch( sw="s" + stri )

            # Check if switch was added
            utilities.assert_equals( expect=main.TRUE, actual=addSwitchResult,
                                     onpass="Successfully added switch.",
                                     onfail="Failed to add switch.")
            result = result and addSwitchResult

            # Reconnect links
            main.step( "Reconnecting links on s" + stri + ".")
            for j in links:
                if ( j[ 'node1' ] == "s" + stri and j[ 'node2' ][ 0 ] == "s" ) or \
                   ( j[ 'node2' ] == "s" + stri and j[ 'node1' ][ 0 ] == "s" ):
                    main.Mininet1.addLink( str( j[ 'node1' ] ), str( j[ 'node2' ] ) )

            # Discover host using ping
            main.Mininet1.pingHost( SRC="h" + stri, TARGET="h" + str( ( i % hosts ) + 1 ) )

            # Check connectivity
            connectivityResult = vpls.testConnectivityVpls( main )
            result = result and connectivityResult


        utilities.assert_equals( expect=main.TRUE,
                                 actual=result,
                                 onpass="Connectivity is as expected.",
                                 onfail="Connectivity is NOT as expected." )

    def CASE300( self, main ):
        """
        Stop 1 ONOS node at a time and test connectivity
        """
        from tests.USECASE.VPLS.dependencies import vpls
        from tests.HA.dependencies.HA import HA
        assert vpls, "vpls not defined"

        main.HA = HA()
        main.case( "Stop one ONOS node at a time and test connectivity." )

        result = main.TRUE

        for i in range( 0, len( main.nodes ) ):

            stri = str( i )

            ip_address = main.nodes[ i ].ip_address

            # Stop an ONOS node: i
            main.step( "Stop ONOS node " + stri + ".")
            stopResult = main.ONOSbench.onosStop( ip_address )
            main.activeNodes.remove( i )

            utilities.assert_equals( expect=main.TRUE, actual=stopResult,
                                     onpass="ONOS nodes stopped successfully.",
                                     onfail="ONOS nodes NOT successfully stopped." )

            # Check connectivity
            connectivityResult = vpls.testConnectivityVpls( main, isNodeUp=False )
            result = result and connectivityResult

            # Restart ONOS node
            main.step( "Restart ONOS node " + stri + " and checking status of restart.")
            startResult = main.ONOSbench.onosStart( ip_address )

            utilities.assert_equals( expect=main.TRUE, actual=startResult,
                                     onpass="ONOS nodes started successfully.",
                                     onfail="ONOS nodes NOT successfully started." )
            result = result and startResult

            # Check if ONOS is up yet
            main.log.info( "Checking if ONOS node " + stri + " is up." )
            upResult = main.ONOSbench.isup( ip_address )

            utilities.assert_equals( expect=main.TRUE, actual=upResult,
                                     onpass="ONOS successfully restarted.",
                                     onfail="ONOS did NOT successfully restart." )

            # Restart CLI
            main.log.info( "Restarting ONOS node " + stri + "'s main.CLI." )
            cliResult = main.CLIs[ i ].startOnosCli( ip_address )
            main.activeNodes.append( i )

            utilities.assert_equals( expect=main.TRUE, actual=cliResults,
                                     onpass="ONOS CLI successfully restarted.",
                                     onfail="ONOS CLI did NOT successfully restart." )

            # Run some basic checks to see if ONOS node truly has succesfully restarted:

            # Checking if all nodes appear with status READY using 'nodes' command
            main.step( "Checking ONOS nodes." )
            nodeResults = utilities.retry( main.HA.nodesCheck,
                                           False,
                                           args=[ main.activeNodes ],
                                           sleep=main.timeSleep,
                                           attempts=main.numAttempts )

            utilities.assert_equals( expect=True, actual=nodeResults,
                                     onpass="Nodes check successful.",
                                     onfail="Nodes check NOT successful." )

            # All apps that are present are active
            main.log.info( "Checking if apps are active." )
            compareAppsResult = vpls.compareApps( main )
            utilities.assert_equals( expect=main.TRUE,
                                     actual=compareAppsResult,
                                     onpass="Apps are the same across all nodes.",
                                     onfail="Apps are NOT the same across all nodes." )
            result = result and compareAppsResult

            # Check connectivity
            connectivityResult = vpls.testConnectivityVpls( main )
            result = result and connectivityResult

        utilities.assert_equals( expect=main.TRUE,
                                 actual=result,
                                 onpass="Connectivity is as expected.",
                                 onfail="Connectivity is NOT as expected." )


    def CASE310( self, main ):
        """
        Kill 1 ONOS node at a time and test connectivity
        """
        assert vpls, "vpls not defined"

        main.case( "Kill one ONOS node at a time and test connectivity." )
        killSleep = int( main.params[ 'SLEEP' ][ 'killnode' ] )
        result = main.TRUE

        for i in range( 0, len( main.nodes ) ):

            # Kill an ONOS node
            main.step( "Killing ONOS node " + str( i + 1 ) + "." )
            killresult = main.ONOSbench.onosKill( main.nodes[ i ].ip_address )

            # Check if ONOS node has been successfully killed
            utilities.assert_equals( expect=main.TRUE, actual=killresult,
                                     onpass="ONOS node killed successfully.",
                                     onfail="ONOS node NOT successfully killed." )

            main.step( "Waiting for ONOS to restart." )
            main.log.info( "Sleeping for " + str( killSleep ) + " seconds..." )
            time.sleep( killSleep )

            # Check connectivity
            connectivityResult = vpls.testConnectivityVpls( main )
            result = result and connectivityResult

        utilities.assert_equals( expect=main.TRUE,
                                 actual=result,
                                 onpass="Connectivity is as expected.",
                                 onfail="Connectivity is NOT as expected.")


    def CASE400( self, main ):
        """
        Bring down 1 link at a time and test connectivity
        """
        assert vpls, "vpls not defined"


        main.case( "Bring down one link at a time and test connectivity." )

        result = main.TRUE

        for link in main.Mininet1.getLinks():
            nodes = [ link[ 'node1' ], link[ 'node2' ] ]

            # Bring down a link
            main.step( "Bring down link: " + nodes[ 0 ] + " to " + nodes[ 1 ] )
            delLinkResult = main.Mininet1.link( END1=nodes[ 0 ], END2=nodes[ 1 ], OPTION="down" )

            # Check if the link has successfully been brought down
            utilities.assert_equals( expect=main.TRUE, actual=delLinkResult,
                                     onpass="Successfully deleted link.",
                                     onfail="Failed to delete link." )
            result = result and delLinkResult

            # Add removed host to blacklist if necessary
            blacklist = []
            for l in nodes:
                if l[ 0 ] == 'h':
                    blacklist.append( l )

            # Check intent states, then connectivity
            connectivityResult = vpls.testConnectivityVpls( main, blacklist )
            result = result and connectivityResult

            # Re-add the link
            main.step( "Adding link: " + nodes[ 0 ] + " to " + nodes[ 1 ] + "." )
            addLinkResult = main.Mininet1.link( END1=nodes[ 0 ], END2=nodes[ 1 ], OPTION="up" )

            # Check if the link has successfully been added
            utilities.assert_equals( expect=main.TRUE, actual=addLinkResult,
                                     onpass="Successfully added link.",
                                     onfail="Failed to delete link." )
            result = result and addLinkResult

            main.log.debug( main.timeSleep )
            time.sleep( main.timeSleep )

            # Check intent states, then connectivity
            connectivityResult = vpls.testConnectivityVpls( main )
            result = result and connectivityResult

        utilities.assert_equals( expect=main.TRUE,
                                 actual=result,
                                 onpass="Connectivity is as expected.",
                                 onfail="Connectivity is NOT as expected." )
