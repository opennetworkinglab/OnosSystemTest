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
# Testing the basic intent functionality of ONOS


class FUNCoptical:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        import imp
        import time
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
        try:
            from tests.dependencies.ONOSSetup import ONOSSetup
            main.testSetUp = ONOSSetup()
        except ImportError:
            main.log.error( "ONOSSetup not found. exiting the test" )
            main.cleanAndExit()
        main.testSetUp.envSetupDescription()
        stepResult = main.FALSE
        # Test variables
        try:
            main.apps = main.params[ 'ENV' ][ 'cellApps' ]
            main.dependencyPath = main.testOnDirectory + \
                                  main.params[ 'DEPENDENCY' ][ 'path' ]
            main.scale = ( main.params[ 'SCALE' ][ 'size' ] ).split( "," )
            wrapperFile1 = main.params[ 'DEPENDENCY' ][ 'wrapper1' ]
            main.startUpSleep = int( main.params[ 'SLEEP' ][ 'startup' ] )
            main.checkIntentSleep = int( main.params[ 'SLEEP' ][ 'checkintent' ] )
            main.checkTopoAttempts = int( main.params[ 'SLEEP' ][ 'topoAttempts' ] )
            main.switches = int( main.params[ 'MININET' ][ 'switch' ] )
            main.links = int( main.params[ 'MININET' ][ 'links' ] )
            main.hosts = int( main.params[ 'MININET' ][ 'hosts' ] )
            main.opticalTopo = main.params[ 'MININET' ][ 'toponame' ]
            main.hostsData = {}
            main.assertReturnString = ''  # Assembled assert return string
            main.cycle = 0  # How many times FUNCintent has run through its tests
            # -- INIT SECTION, ONLY RUNS ONCE -- #
            stepResult = main.testSetUp.envSetup()
        except Exception as e:
            main.testSetUp.envSetupException( e )
        main.testSetUp.evnSetupConclusion( stepResult )

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
        main.flowCompiler = "Flow Rules"
        main.testSetUp.ONOSSetUp( main.Cluster, True, mininetIp=main.LincOE )

    def CASE10( self, main ):
        """
            Start Mininet opticalTest Topology
        """
        main.case( "Mininet with Linc-OE startup" )
        main.step( "Push TopoDDriver.json to ONOS through onos-netcfg" )
        topoResult = True
        for ctrl in main.Cluster.active():
            topoResult = topoResult and \
                         main.ONOSbench.onosNetCfg( controllerIp=ctrl.ipAddress,
                                                    path=main.dependencyPath,
                                                    fileName="TopoDDriver.json" )
        # Exit if topology did not load properly
        if not topoResult:
            main.cleanAndExit()

        main.caseExplanation = "Start opticalTest.py topology included with ONOS"
        main.step( "Starting mininet and LINC-OE" )
        time.sleep( 10 )
        controllerIPs = ','.join( main.Cluster.getIps() )
        cIps = ""
        for i in range( 0, 4 ):
            cIps += controllerIPs + ' '
        opticalMnScript = main.LincOE.runOpticalMnScript( ctrllerIP=cIps, topology=main.opticalTopo )
        topoResult = opticalMnScript
        utilities.assert_equals(
            expect=main.TRUE,
            actual=topoResult,
            onpass="Started the topology successfully ",
            onfail="Failed to start the topology" )

    def CASE14( self, main ):
        """
            Stop mininet
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
        main.Utils.mininetCleanIntro()
        topoResult = main.Utils.mininetCleanup( main.LincOE, timeout=180 )
        # Exit if topology did not load properly
        if not topoResult:
            main.cleanAndExit()

    def CASE16( self, main ):
        """
            Balance Masters
        """
        main.case( "Balance mastership of switches" )
        main.step( "Balancing mastership of switches" )

        balanceResult = main.FALSE
        balanceResult = utilities.retry( f=main.Cluster.active( 0 ).CLI.balanceMasters, retValue=main.FALSE, args=[] )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=balanceResult,
                                 onpass="Successfully balanced mastership of switches",
                                 onfail="Failed to balance mastership of switches" )
        if not balanceResult:
            main.initialized = main.FALSE

    def CASE17( self, main ):
        """
            Use Flow Objectives
        """
        main.case( "Enable intent compilation using Flow Objectives" )
        main.step( "Enabling Flow Objectives" )

        main.flowCompiler = "Flow Objectives"

        cmd = "org.onosproject.net.intent.impl.compiler.IntentConfigurableRegistrator"

        stepResult = main.Cluster.active( 0 ).CLI.setCfg( component=cmd,
                                                          propName="useFlowObjectives", value="true" )
        stepResult &= main.Cluster.active( 0 ).CLI.setCfg( component=cmd,
                                                           propName="defaultFlowObjectiveCompiler",
                                                           value='org.onosproject.net.intent.impl.compiler.LinkCollectionIntentObjectiveCompiler' )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully activated Flow Objectives",
                                 onfail="Failed to activate Flow Objectives" )

    def CASE19( self, main ):
        """
            Copy the karaf.log files after each testcase cycle
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
        main.Utils.copyKarafLog( "cycle" + str( main.cycle ) )

    def CASE21( self, main ):
        """
            Run pingall to discover all hosts
        """
        main.case( "Running Pingall" )
        main.caseExplanation = "Use pingall to discover all hosts. Pingall is expected to fail."
        main.step( "Discover Hosts through Pingall" )
        pingResult = main.LincOE.pingall( timeout=120 )

        utilities.assert_equals( expect=main.FALSE,
                                 actual=pingResult,
                                 onpass="Pingall Completed",
                                 onfail="Pingall did not complete or did not return fales" )

    def CASE22( self, main ):
        """
            Send arpings to discover all hosts
        """
        main.case( "Discover Hosts with arping" )
        main.caseExplanation = "Send arpings between all the hosts to discover and verify them"

        main.step( "Send arping between all hosts" )

        hosts = []
        for i in range( main.hosts ):
            hosts.append( 'h{}'.format( i + 1 ) )

        arpingHostResults = main.TRUE
        for host in hosts:
            if main.LincOE.arping( host, ethDevice=host + "-eth0" ):
                main.log.info( "Successfully reached host {} with arping".format( host ) )
            else:
                main.log.error( "Could not reach host {} with arping".format( host ) )
                arpingHostResults = main.FALSE

        utilities.assert_equals( expect=main.TRUE,
                                 actual=arpingHostResults,
                                 onpass="Successfully discovered all hosts",
                                 onfail="Could not descover some hosts" )

    def CASE23( self, main ):
        """
        Compare ONOS Topology to Mininet Topology
        """
        import json
        try:
            from tests.dependencies.topology import Topology
        except ImportError:
            main.log.error( "Topology not found exiting the test" )
            main.cleanAndExit()
        try:
            main.topoRelated
        except ( NameError, AttributeError ):
            main.topoRelated = Topology()
        main.case( "Compare ONOS Topology view to Mininet topology" )
        main.caseExplanation = "Compare topology elements between Mininet" +\
                                " and ONOS"

        main.log.info( "Gathering topology information from Mininet" )
        devicesResults = main.FALSE  # Overall Boolean for device correctness
        linksResults = main.FALSE  # Overall Boolean for link correctness
        hostsResults = main.FALSE  # Overall Boolean for host correctness
        deviceFails = []  # Nodes where devices are incorrect
        linkFails = []  # Nodes where links are incorrect
        hostFails = []  # Nodes where hosts are incorrect
        attempts = main.checkTopoAttempts  # Remaining Attempts

        mnSwitches = main.switches
        mnLinks = main.links
        mnHosts = main.hosts

        main.step( "Comparing Mininet topology to ONOS topology" )

        while ( attempts >= 0 ) and\
                ( not devicesResults or not linksResults or not hostsResults ):
            time.sleep( 2 )
            if not devicesResults:
                devices = main.topoRelated.getAll( "devices", False )
                ports = main.topoRelated.getAll( "ports", False )
                devicesResults = main.TRUE
                deviceFails = []  # Reset for each attempt
            if not linksResults:
                links = main.topoRelated.getAll( "links", False )
                linksResults = main.TRUE
                linkFails = []  # Reset for each attempt
            if not hostsResults:
                hosts = main.topoRelated.getAll( "hosts", False )
                hostsResults = main.TRUE
                hostFails = []  # Reset for each attempt

            #  Check for matching topology on each node
            for controller in range( main.Cluster.numCtrls ):
                controllerStr = str( controller + 1 )  # ONOS node number
                # Compare Devices
                if devices[ controller ] and ports[ controller ] and\
                        "Error" not in devices[ controller ] and\
                        "Error" not in ports[ controller ]:

                    try:
                        deviceData = json.loads( devices[ controller ] )
                        portData = json.loads( ports[ controller ] )
                    except ( TypeError, ValueError ):
                        main.log.error( "Could not load json:" + str( devices[ controller ] ) + ' or ' + str( ports[ controller ] ) )
                        currentDevicesResult = main.FALSE
                    else:
                        if mnSwitches == len( deviceData ):
                            currentDevicesResult = main.TRUE
                        else:
                            currentDevicesResult = main.FALSE
                            main.log.error( "Node {} only sees {} device(s) but {} exist".format(
                                controllerStr, len( deviceData ), mnSwitches ) )
                else:
                    currentDevicesResult = main.FALSE
                if not currentDevicesResult:
                    deviceFails.append( controllerStr )
                devicesResults = devicesResults and currentDevicesResult
                # Compare Links
                if links[ controller ] and "Error" not in links[ controller ]:
                    try:
                        linkData = json.loads( links[ controller ] )
                    except ( TypeError, ValueError ):
                        main.log.error( "Could not load json:" + str( links[ controller ] ) )
                        currentLinksResult = main.FALSE
                    else:
                        if mnLinks == len( linkData ):
                            currentLinksResult = main.TRUE
                        else:
                            currentLinksResult = main.FALSE
                            main.log.error( "Node {} only sees {} link(s) but {} exist".format(
                                controllerStr, len( linkData ), mnLinks ) )
                else:
                    currentLinksResult = main.FALSE
                if not currentLinksResult:
                    linkFails.append( controllerStr )
                linksResults = linksResults and currentLinksResult
                # Compare Hosts
                if hosts[ controller ] and "Error" not in hosts[ controller ]:
                    try:
                        hostData = json.loads( hosts[ controller ] )
                    except ( TypeError, ValueError ):
                        main.log.error( "Could not load json:" + str( hosts[ controller ] ) )
                        currentHostsResult = main.FALSE
                    else:
                        if mnHosts == len( hostData ):
                            currentHostsResult = main.TRUE
                        else:
                            currentHostsResult = main.FALSE
                            main.log.error( "Node {} only sees {} host(s) but {} exist".format(
                                controllerStr, len( hostData ), mnHosts ) )
                else:
                    currentHostsResult = main.FALSE
                if not currentHostsResult:
                    hostFails.append( controllerStr )
                hostsResults = hostsResults and currentHostsResult
            # Decrement Attempts Remaining
            attempts -= 1

        utilities.assert_equals( expect=[],
                                 actual=deviceFails,
                                 onpass="ONOS correctly discovered all devices",
                                 onfail="ONOS incorrectly discovered devices on nodes: " +
                                 str( deviceFails ) )
        utilities.assert_equals( expect=[],
                                 actual=linkFails,
                                 onpass="ONOS correctly discovered all links",
                                 onfail="ONOS incorrectly discovered links on nodes: " +
                                 str( linkFails ) )
        utilities.assert_equals( expect=[],
                                 actual=hostFails,
                                 onpass="ONOS correctly discovered all hosts",
                                 onfail="ONOS incorrectly discovered hosts on nodes: " +
                                 str( hostFails ) )
        if hostsResults and linksResults and devicesResults:
            topoResults = main.TRUE
        else:
            topoResults = main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=topoResults,
                                 onpass="ONOS correctly discovered the topology",
                                 onfail="ONOS incorrectly discovered the topology" )

    def CASE31( self, main ):
        import time
        """
            Add bidirectional point intents between 2 packet layer( mininet )
            devices and ping mininet hosts
        """
        main.log.report(
            "This testcase adds bidirectional point intents between 2 " +
            "packet layer( mininet ) devices and ping mininet hosts" )
        main.case( "Install point intents between 2 packet layer device and " +
                   "ping the hosts" )
        main.caseExplanation = "This testcase adds bidirectional point intents between 2 " +\
            "packet layer( mininet ) devices and ping mininet hosts"

        main.step( "Adding point intents" )
        checkFlowResult = main.TRUE
        main.pIntentsId = []
        pIntent1 = main.Cluster.active( 0 ).CLI.addPointIntent(
            "of:0000000000000015/1",
            "of:000000000000000b/2" )
        time.sleep( 10 )
        pIntent2 = main.Cluster.active( 0 ).CLI.addPointIntent(
            "of:000000000000000b/2",
            "of:0000000000000015/1" )
        main.pIntentsId.append( pIntent1 )
        main.pIntentsId.append( pIntent2 )
        time.sleep( 10 )
        main.log.info( "Checking intents state" )
        checkStateResult = main.Cluster.active( 0 ).CLI.checkIntentState(
                                                         intentsId=main.pIntentsId )
        time.sleep( 10 )
        checkStateResult = utilities.retry( f=main.Cluster.active( 0 ).CLI.checkIntentState,
                                            retValue=main.FALSE, args=( main.pIntentsId, "INSTALLED" ),
                                            sleep=main.checkIntentSleep, attempts=10 )
        main.log.info( "Checking flows state" )
        checkFlowResult = main.Cluster.active( 0 ).CLI.checkFlowsState()
        # Sleep for 10 seconds to provide time for the intent state to change
        time.sleep( 10 )
        main.log.info( "Checking intents state one more time" )
        checkStateResult = main.Cluster.active( 0 ).CLI.checkIntentState(
                                                  intentsId=main.pIntentsId )

        if checkStateResult and checkFlowResult:
            addIntentsResult = main.TRUE
        else:
            addIntentsResult = main.FALSE
        utilities.assert_equals(
            expect=main.TRUE,
            actual=addIntentsResult,
            onpass="Successfully added point intents",
            onfail="Failed to add point intents" )

        pingResult = main.FALSE

        if not addIntentsResult:
            main.log.error( "Intents were not properly installed. Skipping ping." )

        else:
            main.step( "Ping h1 and h2" )
            pingResult = main.LincOE.pingHostOptical( src="h1", target="h2" )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=pingResult,
            onpass="Successfully pinged h1 and h2",
            onfail="Failed to ping between h1 and h2" )

        main.step( "Remove Point to Point intents" )
        removeResult = main.TRUE
        # Check remaining intents
        try:
            intentsJson = json.loads( main.Cluster.active( 0 ).CLI.intents() )
            main.log.debug( intentsJson )
            main.Cluster.active( 0 ).CLI.removeIntent( intentId=pIntent1, purge=True )
            main.Cluster.active( 0 ).CLI.removeIntent( intentId=pIntent2, purge=True )
            for intents in intentsJson:
                main.Cluster.active( 0 ).CLI.removeIntent( intentId=intents.get( 'id' ),
                                                           app='org.onosproject.cli',
                                                           purge=True )
                time.sleep( 15 )

            for ctrl in main.Cluster.active():
                if not any( intent.get( 'state' ) == 'WITHDRAWING' for intent
                            in json.loads( ctrl.CLI.intents() ) ):
                    main.log.debug( json.loads( ctrl.CLI.intents() ) )
                    removeResult = main.FALSE
                    break
                else:
                    removeResult = main.TRUE
        except ( TypeError, ValueError ):
            main.log.error( "Cannot see intents on " + main.Cluster.active( 0 ).name +
                            ".  Removing all intents." )
            main.Cluster.active( 0 ).CLI.removeAllIntents( purge=True )
            main.Cluster.active( 0 ).CLI.removeAllIntents( purge=True, app='org.onosproject.cli' )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=removeResult,
                                 onpass="Successfully removed host intents",
                                 onfail="Failed to remove host intents" )

    def CASE32( self ):
        """
            Add host intents between 2 packet layer host
        """
        import time
        import json
        main.log.report( "Adding host intents between 2 optical layer host" )
        main.case( "Test add host intents between optical layer host" )
        main.caseExplanation = "Test host intents between 2 optical layer host"

        main.step( "Creating list of hosts" )
        hostnum = 0
        try:
            hostData = json.loads( hosts[ controller ] )
        except( TypeError, ValueError ):
            main.log.error( "Could not load json:" + str( hosts[ controller ] ) )

        main.step( "Adding host intents to h1 and h2" )
        hostId = []
        # Listing host MAC addresses
        for host in hostData:
            hostId.append( host.get( "id" ) )
        host1 = hostId[ 0 ]
        host2 = hostId[ 1 ]
        main.log.debug( host1 )
        main.log.debug( host2 )

        intentsId = []
        intent1 = main.Cluster.active( 0 ).CLI.addHostIntent( hostIdOne=host1,
                                                              hostIdTwo=host2 )
        intentsId.append( intent1 )
        # Checking intents state before pinging
        main.log.info( "Checking intents state" )
        intentResult = utilities.retry( f=main.Cluster.active( 0 ).CLI.checkIntentState,
                                        retValue=main.FALSE, args=intentsId,
                                        sleep=main.checkIntentSleep, attempts=10 )

        # If intent state is still wrong, display intent states
        if not intentResult:
            main.log.error( main.Cluster.active( 0 ).CLI.intents() )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=intentResult,
                                 onpass="All intents are in INSTALLED state ",
                                 onfail="Some of the intents are not in " +
                                        "INSTALLED state " )

        if not intentResult:
            main.log.error( "Intents were not properly installed. Skipping Ping" )
        else:
            # Pinging h1 to h2 and then ping h2 to h1
            main.step( "Pinging h1 and h2" )
            pingResult = main.TRUE
            pingResult = main.LincOE.pingHostOptical( src="h1", target="h2" ) \
                and main.LincOE.pingHostOptical( src="h2", target="h1" )

            utilities.assert_equals( expect=main.TRUE,
                                     actual=pingResult,
                                     onpass="Pinged successfully between h1 and h2",
                                     onfail="Pinged failed between h1 and h2" )

        # Removed all added host intents
        main.step( "Removing host intents" )
        removeResult = main.TRUE
        # Check remaining intents
        try:
            intentsJson = json.loads( main.Cluster.active( 0 ).CLI.intents() )
            main.Cluster.active( 0 ).CLI.removeIntent( intentId=intent1, purge=True )
            main.log.debug( intentsJson )
            for intents in intentsJson:
                main.Cluster.active( 0 ).CLI.removeIntent( intentId=intents.get( 'id' ),
                                                           app='org.onosproject.optical',
                                                           purge=True )
            time.sleep( 15 )

            for ctrl in main.Cluster.active():
                if not any( intent.get( 'state' ) == 'WITHDRAWING' for intent
                            in json.loads( ctrl.CLI.intents() ) ):
                    main.log.debug( json.loads( ctrl.CLI.intents() ) )
                    removeResult = main.FALSE
                    break
                else:
                    removeResult = main.TRUE
        except ( TypeError, ValueError ):
            main.log.error( "Cannot see intents on " + main.Cluster.active( 0 ).name +
                            ".  Removing all intents." )
            main.Cluster.active( 0 ).CLI.removeAllIntents( purge=True )
            main.Cluster.active( 0 ).CLI.removeAllIntents( purge=True, app='org.onosproject.optical' )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=removeResult,
                                 onpass="Successfully removed host intents",
                                 onfail="Failed to remove host intents" )
