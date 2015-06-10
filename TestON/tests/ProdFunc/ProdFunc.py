
# Testing the basic functionality of ONOS Next
# For sanity and driver functionality excercises only.

import time
# import sys
# import os
# import re
import json

time.sleep( 1 )


class ProdFunc:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        import time
        """
        Startup sequence:
        cell <name>
        onos-verify-cell
        onos-remove-raft-log
        git pull
        mvn clean install
        onos-package
        onos-install -f
        onos-wait-for-start
        """
        cellName = main.params[ 'ENV' ][ 'cellName' ]
        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]

        main.case( "Setting up test environment" )
        main.log.report(
            "This testcase is testing setting up test environment" )
        main.log.report( "__________________________________" )

        main.step( "Applying cell variable to environment" )
        cellResult = main.ONOSbench.setCell( cellName )
        verifyResult = main.ONOSbench.verifyCell()

        main.step( "Git checkout and get version" )
        main.ONOSbench.gitCheckout( "master" )
        gitPullResult = main.ONOSbench.gitPull()
        main.log.info( "git_pull_result = " + str( gitPullResult ))
        main.ONOSbench.getVersion( report=True )

        packageResult = main.TRUE
        if gitPullResult == 1:
            main.step( "Using mvn clean & install" )
            main.ONOSbench.cleanInstall()
            main.step( "Creating ONOS package" )
            packageResult = main.ONOSbench.onosPackage()
        elif gitPullResult == 0:
            main.log.report(
                "Git Pull Failed, look into logs for detailed reason" )
            main.cleanup()
            main.exit()


        main.step( "Uninstalling ONOS package" )
        onosInstallResult = main.ONOSbench.onosUninstall( ONOS1Ip )
        if onosInstallResult == main.TRUE:
            main.log.report( "Uninstalling ONOS package successful" )
        else:
            main.log.report( "Uninstalling ONOS package failed" )

        time.sleep( 20 )
        main.step( "Installing ONOS package" )
        onosInstallResult = main.ONOSbench.onosInstall( ONOS1Ip )
        print onosInstallResult
        if onosInstallResult == main.TRUE:
            main.log.report( "Installing ONOS package successful" )
        else:
            main.log.report( "Installing ONOS package failed" )

        time.sleep( 20 )
        onos1Isup = main.ONOSbench.isup()
        if onos1Isup == main.TRUE:
            main.log.report( "ONOS instance is up and ready" )
        else:
            main.log.report( "ONOS instance may not be up" )

        startResult = main.TRUE
        #main.step( "Starting ONOS service" )
        #startResult = main.ONOSbench.onosStart( ONOS1Ip )

        main.ONOS2.startOnosCli( ONOS1Ip )
        main.step( "Starting Mininet CLI..." )
        
        # Starting the mininet using the old way
        main.step( "Starting Mininet ..." )
        netIsUp = main.Mininet1.startNet()
        if netIsUp:
            main.log.info("Mininet CLI is up")
        
        case1Result = ( packageResult and
                        cellResult and verifyResult
                        and onosInstallResult and
                        onos1Isup and startResult )
        utilities.assert_equals( expect=main.TRUE, actual=case1Result,
                                 onpass="Test startup successful",
                                 onfail="Test startup NOT successful" )

    def CASE2( self, main ):
        """
        Switch Down
        """
        # NOTE: You should probably run a topology check after this
        import time

        main.case( "Switch down discovery" )
        main.log.report( "This testcase is testing a switch down discovery" )
        main.log.report( "__________________________________" )

        switchSleep = int( main.params[ 'timers' ][ 'SwitchDiscovery' ] )

        description = "Killing a switch to ensure it is discovered correctly"
        main.log.report( description )
        main.case( description )

        # TODO: Make this switch parameterizable
        main.step( "Kill s28 " )
        main.log.report( "Deleting s28" )
        # FIXME: use new dynamic topo functions
        main.Mininet1.delSwitch( "s28" )
        main.log.info(
            "Waiting " +
            str( switchSleep ) +
            " seconds for switch down to be discovered" )
        time.sleep( switchSleep )
        # Peek at the deleted switch
        device = main.ONOS2.getDevice( dpid="0028" )
        print "device = ", device
        if device[ u'available' ] == 'False':
            case2Result = main.FALSE
        else:
            case2Result = main.TRUE
        utilities.assert_equals( expect=main.TRUE, actual=case2Result,
                                 onpass="Switch down discovery successful",
                                 onfail="Switch down discovery failed" )

    def CASE101( self, main ):
        """
        Cleanup sequence:
        onos-service <nodeIp> stop
        onos-uninstall

        TODO: Define rest of cleanup

        """
        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]

        main.case( "Cleaning up test environment" )

        main.step( "Testing ONOS kill function" )
        killResult = main.ONOSbench.onosKill( ONOS1Ip )

        main.step( "Stopping ONOS service" )
        stopResult = main.ONOSbench.onosStop( ONOS1Ip )

        main.step( "Uninstalling ONOS service" )
        uninstallResult = main.ONOSbench.onosUninstall()

        case11Result = killResult and stopResult and uninstallResult
        utilities.assert_equals( expect=main.TRUE, actual=case11Result,
                                 onpass="Cleanup successful",
                                 onfail="Cleanup failed" )

    def CASE3( self, main ):
        """
        Test 'onos' command and its functionality in driver
        """
        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]

        main.case( "Testing 'onos' command" )

        main.step( "Sending command 'onos -w <onos-ip> system:name'" )
        cmdstr1 = "system:name"
        cmdResult1 = main.ONOSbench.onosCli( ONOS1Ip, cmdstr1 )
        main.log.info( "onos command returned: " + cmdResult1 )

        main.step( "Sending command 'onos -w <onos-ip> onos:topology'" )
        cmdstr2 = "onos:topology"
        cmdResult2 = main.ONOSbench.onosCli( ONOS1Ip, cmdstr2 )
        main.log.info( "onos command returned: " + cmdResult2 )

    def CASE20( self ):
        """
            Exit from mininet cli
            reinstall ONOS
        """
        import time
        cellName = main.params[ 'ENV' ][ 'cellName' ]
        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]

        main.log.report( "This testcase exits the mininet cli and reinstalls" +
                         "ONOS to switch over to Packet Optical topology" )
        main.log.report( "_____________________________________________" )
        main.case( "Disconnecting mininet and restarting ONOS" )

        main.step( "Disconnecting mininet and restarting ONOS" )
        step1Result = main.TRUE
        mininetDisconnect = main.Mininet1.disconnect()
        print "mininetDisconnect = ", mininetDisconnect
        step1Result = mininetDisconnect
        utilities.assert_equals(
            expect=main.TRUE,
            actual=step1Result,
            onpass="Mininet disconnect successfully",
            onfail="Mininet failed to disconnect")
        """
        main.step( "Removing raft logs before a clean installation of ONOS" )
        step2Result = main.TRUE
        removeRaftLogsResult = main.ONOSbench.onosRemoveRaftLogs()
        step2Result = removeRaftLogsResult
        utilities.assert_equals(
            expect=main.TRUE,
            actual=step2Result,
            onpass="Raft logs removed successfully",
            onfail="Failed to remove raft logs")
        """
        main.step( "Applying cell variable to environment" )
        step3Result = main.TRUE
        setCellResult = main.ONOSbench.setCell( cellName )
        verifyCellResult = main.ONOSbench.verifyCell()
        step3Result = setCellResult and verifyCellResult
        utilities.assert_equals(
            expect=main.TRUE,
            actual=step3Result,
            onpass="Cell applied successfully",
            onfail="Failed to apply cell")

        main.step( "Uninstalling ONOS package" )
        step4Result = main.TRUE
        ONOSip1 = main.params[ 'CTRL' ][ 'ip1' ]
        onosUninstallResult = main.ONOSbench.onosUninstall( nodeIp = ONOSip1)
        step4Result = onosUninstallResult
        utilities.assert_equals(
            expect=main.TRUE,
            actual=step4Result,
            onpass="Successfully uninstalled ONOS",
            onfail="Failed to uninstall ONOS")

        time.sleep( 5 )
        main.step( "Installing ONOS package" )
        step5Result = main.TRUE
        onosInstallResult = main.ONOSbench.onosInstall( node = ONOSip1 )
        step5Result = onosInstallResult
        utilities.assert_equals(
            expect=main.TRUE,
            actual=step5Result,
            onpass="Successfully installed ONOS",
            onfail="Failed to install ONOS")

        onos1Isup = main.ONOSbench.isup()
        if onos1Isup == main.TRUE:
            main.log.report( "ONOS instance is up and ready" )
        else:
            main.log.report( "ONOS instance may not be up" )

        main.step( "Starting ONOS service" )
        step6Result = main.TRUE
        startResult = main.ONOSbench.onosStart( ONOS1Ip )
        step6Result = startResult
        utilities.assert_equals(
            expect=main.TRUE,
            actual=step6Result,
            onpass="Successfully started ONOS",
            onfail="Failed to start ONOS")

        main.step( "Starting ONOS cli" )
        step7Result = main.TRUE
        cliResult = main.ONOS2.startOnosCli( ONOSIp=main.params[ 'CTRL' ][ 'ip1' ] )
        step7Result = cliResult
        utilities.assert_equals(
            expect=main.TRUE,
            actual=step7Result,
            onpass="Successfully started ONOS cli",
            onfail="Failed to start ONOS cli")

    def CASE21( self, main ):
        """
            On ONOS bench, run this command:
            sudo -E python ~/onos/tools/test/topos/opticalTest.py -OC1
            which spawns packet optical topology and copies the links
            json file to the onos instance.
            Note that in case of Packet Optical, the links are not learnt
            from the topology, instead the links are learnt
            from the json config file
        """
        import time
        main.log.report(
            "This testcase starts the packet layer topology and REST" )
        main.log.report( "_____________________________________________" )
        main.case( "Starting LINC-OE and other components" )

        main.step( "Activate optical app" )
        step1Result = main.TRUE
        activateOpticalResult = main.ONOS2.activateApp( "org.onosproject.optical" )
        step1Result = activateOpticalResult
        utilities.assert_equals(
            expect=main.TRUE,
            actual=step1Result,
            onpass="Successfully activated optical app",
            onfail="Failed to activate optical app")

        appCheck = main.ONOS2.appToIDCheck()
        if appCheck != main.TRUE:
            main.log.warn( main.ONOS2.apps() )
            main.log.warn( main.ONOS2.appIDs() )

        main.step( "Starting mininet and LINC-OE" )
        step2Result = main.TRUE
        time.sleep( 10 )
        opticalMnScript = main.LincOE2.runOpticalMnScript(ctrllerIP = main.params[ 'CTRL' ][ 'ip1' ])
        step2Result = opticalMnScript
        utilities.assert_equals(
            expect=main.TRUE,
            actual=step2Result,
            onpass="Started the topology successfully ",
            onfail="Failed to start the topology")

    def CASE22( self, main ):
        """
            Curretly we use, 10 optical switches(ROADM's) and
            6 packet layer mininet switches each with one host.
            Therefore, the roadmCount variable = 10,
            packetLayerSWCount variable = 6, hostCount=6 and
            links=46.
            All this is hardcoded in the testcase. If the topology changes,
            these hardcoded values need to be changed
        """
        import time
        main.log.report(
            "This testcase compares the optical+packet topology against what" +
            " is expected" )
        main.case( "Topology comparision" )

        main.step( "Starts new ONOS cli" )
        step1Result = main.TRUE
        cliResult = main.ONOS3.startOnosCli( ONOSIp=main.params[ 'CTRL' ]\
                                                               [ 'ip1' ] )
        step1Result = cliResult
        utilities.assert_equals(
            expect=main.TRUE,
            actual=step1Result,
            onpass="Successfully starts a new cli",
            onfail="Failed to start new cli" )

        main.step( "Compare topology" )
        step2Result = main.TRUE
        devicesResult = main.ONOS3.devices( jsonFormat=False )
        print "devices_result :\n", devicesResult
        devicesLinewise = devicesResult.split( "\n" )
        roadmCount = 0
        packetLayerSWCount = 0
        for line in devicesLinewise:
            components = line.split( "," )
            availability = components[ 1 ].split( "=" )[ 1 ]
            type = components[ 3 ].split( "=" )[ 1 ]
            if availability == 'true' and type == 'ROADM':
                roadmCount += 1
            elif availability == 'true' and type == 'SWITCH':
                packetLayerSWCount += 1
        if roadmCount == 10:
            print "Number of Optical Switches = %d and is" % roadmCount +\
                  " correctly detected"
            main.log.info(
                "Number of Optical Switches = " +
                str( roadmCount ) +
                " and is correctly detected" )
            opticalSWResult = main.TRUE
        else:
            print "Number of Optical Switches = %d and is wrong" % roadmCount
            main.log.info(
                "Number of Optical Switches = " +
                str( roadmCount ) +
                " and is wrong" )
            opticalSWResult = main.FALSE
        if packetLayerSWCount == 6:
            print "Number of Packet layer or mininet Switches = %d "\
                    % packetLayerSWCount + "and is correctly detected"
            main.log.info(
                "Number of Packet layer or mininet Switches = " +
                str( packetLayerSWCount ) +
                " and is correctly detected" )
            packetSWResult = main.TRUE
        else:
            print "Number of Packet layer or mininet Switches = %d and"\
                    % packetLayerSWCount + " is wrong"
            main.log.info(
                "Number of Packet layer or mininet Switches = " +
                str( packetLayerSWCount ) +
                " and is wrong" )
            packetSWResult = main.FALSE
        # sleeps for sometime so the state of the switches will be active
        time.sleep( 30 )
        print "_________________________________"
        linksResult = main.ONOS3.links( jsonFormat=False )
        print "links_result = ", linksResult
        print "_________________________________"
        linkActiveCount = linksResult.count("state=ACTIVE")
        main.log.info( "linkActiveCount = " + str( linkActiveCount ))
        if linkActiveCount == 46:
            linkActiveResult = main.TRUE
            main.log.info(
                "Number of links in ACTIVE state are correct")
        else:
            linkActiveResult = main.FALSE
            main.log.info(
                "Number of links in ACTIVE state are wrong")
        step2Result = opticalSWResult and packetSWResult and \
                        linkActiveResult
        utilities.assert_equals(
            expect=main.TRUE,
            actual=step2Result,
            onpass="Successfully loaded packet optical topology",
            onfail="Failed to load packet optical topology" )

    def CASE23( self, main ):
        import time
        """
            Add bidirectional point intents between 2 packet layer( mininet )
            devices and
            ping mininet hosts
        """
        main.log.report(
            "This testcase adds bidirectional point intents between 2 " +
            "packet layer( mininet ) devices and ping mininet hosts" )
        main.case( "Install point intents between 2 packet layer device and " +
                   "ping the hosts" )

        main.step( "Adding point intents" )
        checkFlowResult = main.TRUE
        step1Result = main.TRUE
        main.pIntentsId = []
        pIntent1 = main.ONOS3.addPointIntent(
            "of:0000ffffffff0001/1",
            "of:0000ffffffff0005/1" )
        pIntent2 = main.ONOS3.addPointIntent(
            "of:0000ffffffff0005/1",
            "of:0000ffffffff0001/1" )
        main.pIntentsId.append( pIntent1 )
        main.pIntentsId.append( pIntent2 )
        time.sleep( 10 )
        main.log.info( "Checking intents state")
        checkStateResult = main.ONOS3.checkIntentState(
                                                  intentsId = main.pIntentsId )
        time.sleep( 10 )
        main.log.info( "Checking flows state")
        checkFlowResult = main.ONOS3.checkFlowsState()
        # Sleep for 30 seconds to provide time for the intent state to change
        time.sleep( 10 )
        main.log.info( "Checking intents state one more time")
        checkStateResult = main.ONOS3.checkIntentState(
                                                  intentsId = main.pIntentsId )
        step1Result = checkStateResult and checkFlowResult
        utilities.assert_equals(
            expect=main.TRUE,
            actual=step1Result,
            onpass="Successfully added point intents",
            onfail="Failed to add point intents")

        main.step( "Ping h1 and h5" )
        step2Result = main.TRUE
        main.log.info( "\n\nh1 is Pinging h5" )
        pingResult = main.LincOE2.pingHostOptical( src="h1", target="h5" )
        step2Result = pingResult
        utilities.assert_equals(
            expect=main.TRUE,
            actual=step2Result,
            onpass="Successfully pinged h1 and h5",
            onfail="Failed to ping between h1 and h5")

    def CASE24( self, main ):
        import time
        import json
        """
            LINC uses its own switch IDs. You can use the following
            command on the LINC console to find the mapping between 
            DPIDs and LINC IDs.
            rp(application:get_all_key(linc)).
            
            Test Rerouting of Packet Optical by bringing a port down
            ( port 20 ) of a switch( switchID=1, or LincOE switchID =9 ), 
            so that link
            ( between switch1 port20 - switch5 port50 ) is inactive
            and do a ping test. If rerouting is successful,
            ping should pass. also check the flows
        """
        main.log.report(
            "This testcase tests rerouting and pings mininet hosts" )
        main.case( "Test rerouting and pings mininet hosts" )

        main.step( "Attach to the Linc-OE session" )
        step1Result = main.TRUE
        attachConsole = main.LincOE1.attachLincOESession()
        step1Result = attachConsole
        utilities.assert_equals(
            expect=main.TRUE,
            actual=step1Result,
            onpass="Successfully attached Linc-OE session",
            onfail="Failed to attached Linc-OE session")

        main.step( "Bring a port down and verify the link state" )
        step2Result = main.TRUE
        main.LincOE1.portDown( swId="9", ptId="20" )
        linksNonjson = main.ONOS3.links( jsonFormat=False )
        main.log.info( "links = " + linksNonjson )
        linkInactiveCount = linksNonjson.count( "state=INACTIVE" )
        main.log.info( "linkInactiveCount = " + str( linkInactiveCount ))
        if linkInactiveCount == 2:
            main.log.info(
                "Number of links in INACTIVE state are correct")
        else:
            main.log.info(
                "Number of links in INACTIVE state are wrong")
        links = main.ONOS3.links()
        main.log.info( "links = " + links )
        linksResult = json.loads( links )
        linksStateResult = main.FALSE
        for item in linksResult:
            if item[ 'src' ][ 'device' ] == "of:0000ffffffffff01" and item[
                    'src' ][ 'port' ] == "20":
                if item[ 'dst' ][ 'device' ] == "of:0000ffffffffff05" and item[
                        'dst' ][ 'port' ] == "50":
                    linksState = item[ 'state' ]
                    if linksState == "INACTIVE":
                        main.log.info(
                            "Links state is inactive as expected due to one" +
                            " of the ports being down" )
                        main.log.report(
                            "Links state is inactive as expected due to one" +
                            " of the ports being down" )
                        linksStateResult = main.TRUE
                        break
                    else:
                        main.log.info(
                            "Links state is not inactive as expected" )
                        main.log.report(
                            "Links state is not inactive as expected" )
                        linksStateResult = main.FALSE
        time.sleep( 10 )
        checkFlowsState = main.ONOS3.checkFlowsState()
        step2Result = linksStateResult
        utilities.assert_equals(
            expect=main.TRUE,
            actual=step2Result,
            onpass="Successfuly brought down a link",
            onfail="Failed to bring down a link")

        main.step( "Verify Rerouting by a ping test" )
        step3Result = main.TRUE
        main.log.info( "\n\nh1 is Pinging h5" )
        pingResult = main.LincOE2.pingHostOptical( src="h1", target="h5" )
        step3Result = pingResult
        utilities.assert_equals(
            expect=main.TRUE,
            actual=step3Result,
            onpass="Successfully pinged h1 and h5",
            onfail="Failed to ping between h1 and h5")

        main.step( "Bring the downed port up and verify the link state" )
        step4Result = main.TRUE
        main.LincOE1.portUp( swId="9", ptId="20" )
        linksNonjson = main.ONOS3.links( jsonFormat=False )
        main.log.info( "links = " + linksNonjson )
        linkInactiveCount = linksNonjson.count( "state=INACTIVE" )
        main.log.info( "linkInactiveCount = " + str( linkInactiveCount ))
        if linkInactiveCount == 0:
            main.log.info(
                "Number of links in INACTIVE state are correct")
        else:
            main.log.info(
                "Number of links in INACTIVE state are wrong")
            step4Result = main.FALSE
        utilities.assert_equals(
            expect=main.TRUE,
            actual=step4Result,
            onpass="Successfully brought the port up",
            onfail="Failed to bring the port up")
        """
        main.step( "Removing host intents" )
        step5Result = main.TRUE
        removeResult = main.TRUE
        # Check remaining intents
        intentsJson = json.loads( main.ONOS3.intents() )
        main.ONOS3.removeIntent( intentId=intent1, purge=True )
        main.ONOS3.removeIntent( intentId=intent2, purge=True )
        for intents in intentsJson:
            main.ONOS3.removeIntent( intentId=intents.get( 'id' ),
                                     app='org.onosproject.optical',
                                     purge=True )
        print json.loads( main.ONOS3.intents() )
        if len( json.loads( main.ONOS3.intents() ) ):
            removeResult = main.FALSE
        step5Result = removeResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=step5Result,
                                 onpass="Successfully removed host intents",
                                 onfail="Failed to remove host intents" )
        """
    def CASE10( self ):
        main.log.report(
            "This testcase uninstalls the reactive forwarding app" )
        main.log.report( "__________________________________" )
        main.case( "Uninstalling reactive forwarding app" )
        main.step( "Uninstalling reactive forwarding app" )
        step1Result = main.TRUE
        # Unistall onos-app-fwd app to disable reactive forwarding
        main.log.info( "deactivate reactive forwarding app" )
        appUninstallResult = main.ONOS2.deactivateApp( "org.onosproject.fwd" )
        appCheck = main.ONOS2.appToIDCheck()
        if appCheck != main.TRUE:
            main.log.warn( main.ONOS2.apps() )
            main.log.warn( main.ONOS2.appIDs() )
        step1Result = appUninstallResult
        utilities.assert_equals(
            expect=main.TRUE,
            actual=step1Result,
            onpass="Successfully deactivate reactive forwarding app",
            onfail="Failed to deactivate reactive forwarding app")
        # After reactive forwarding is disabled, the reactive flows on
        # switches timeout in 10-15s
        # So sleep for 15s
        time.sleep( 15 )
        flows = main.ONOS2.flows()
        main.log.info( flows )

    def CASE25( self ):
        """
            Add host intents between 2 packet layer host
        """
        import time
        import json
        main.log.report( "Adding host intents between 2 optical layer host" )
        main.case( "Test add host intents between optical layer host" )

        main.step( "Discover host using arping" )
        step1Result = main.TRUE
        main.hostMACs = []
        main.hostId = []
        #Listing host MAC addresses
        for i in range( 1 , 7 ):
            main.hostMACs.append( "00:00:00:00:00:" +
                                str( hex( i )[ 2: ] ).zfill( 2 ).upper() )
        for macs in main.hostMACs:
            main.hostId.append( macs + "/-1" )
        host1 = main.hostId[ 0 ]
        host2 = main.hostId[ 1 ]
        # Use arping to discover the hosts
        main.LincOE2.arping( host = "h1" )
        main.LincOE2.arping( host = "h2" )
        time.sleep( 5 )
        hostsDict = main.ONOS3.hosts()
        if not len( hostsDict ):
            step1Result = main.FALSE
        # Adding host intent
        utilities.assert_equals(
            expect=main.TRUE,
            actual=step1Result,
            onpass="Hosts discovered",
            onfail="Failed to discover hosts")

        main.step( "Adding host intents to h1 and h2" )
        step2Result = main.TRUE
        intentsId = []
        intent1 = main.ONOS3.addHostIntent( hostIdOne = host1,
                                            hostIdTwo = host2 )
        intentsId.append( intent1 )
        time.sleep( 5 )
        intent2 = main.ONOS3.addHostIntent( hostIdOne = host2,
                                            hostIdTwo = host1 )
        intentsId.append( intent2 )
        # Checking intents state before pinging
        main.log.info( "Checking intents state" )
        time.sleep( 15 )
        intentResult = main.ONOS3.checkIntentState( intentsId = intentsId )
        #check intent state again if intents are not in installed state
        if not intentResult:
           intentResult = main.ONOS3.checkIntentState( intentsId = intentsId )
        step2Result = intentResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=step2Result,
                                 onpass="All intents are in INSTALLED state ",
                                 onfail="Some of the intents are not in " +
                                        "INSTALLED state " )

        # pinging h1 to h2 and then ping h2 to h1
        main.step( "Pinging h1 and h2" )
        step3Result = main.TRUE
        pingResult = main.TRUE
        pingResult = main.LincOE2.pingHostOptical( src="h1", target="h2" )
        pingResult = pingResult and main.LincOE2.pingHostOptical( src="h2",
                                                                  target="h1" )
        step3Result = pingResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=step3Result,
                                 onpass="Pinged successfully between h1 and h2",
                                 onfail="Pinged failed between h1 and h2" )
        # Removed all added host intents
        main.step( "Removing host intents" )
        step4Result = main.TRUE
        removeResult = main.TRUE
        # Check remaining intents
        intentsJson = json.loads( main.ONOS3.intents() )
        main.ONOS3.removeIntent( intentId=intent1, purge=True )
        main.ONOS3.removeIntent( intentId=intent2, purge=True )
        for intents in intentsJson:
            main.ONOS3.removeIntent( intentId=intents.get( 'id' ),
                                     app='org.onosproject.optical',
                                     purge=True )
        print json.loads( main.ONOS3.intents() )
        if len( json.loads( main.ONOS3.intents() ) ):
            removeResult = main.FALSE
        step4Result = removeResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=step4Result,
                                 onpass="Successfully removed host intents",
                                 onfail="Failed to remove host intents" )

    def CASE4( self, main ):
        import re
        import time
        main.log.report( "This testcase is testing the assignment of" +
                         " all the switches to all the controllers and" +
                         " discovering the hosts in reactive mode" )
        main.log.report( "__________________________________" )

        main.case( "Pingall Test" )
        main.step( "Assigning switches to controllers" )
        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]
        ONOS1Port = main.params[ 'CTRL' ][ 'port1' ]
        for i in range( 1, 29 ):
            if i == 1:
                main.Mininet1.assignSwController(
                    sw=str( i ),
                    ip1=ONOS1Ip,
                    port1=ONOS1Port )
            elif i >= 2 and i < 5:
                main.Mininet1.assignSwController(
                    sw=str( i ),
                    ip1=ONOS1Ip,
                    port1=ONOS1Port )
            elif i >= 5 and i < 8:
                main.Mininet1.assignSwController(
                    sw=str( i ),
                    ip1=ONOS1Ip,
                    port1=ONOS1Port )
            elif i >= 8 and i < 18:
                main.Mininet1.assignSwController(
                    sw=str( i ),
                    ip1=ONOS1Ip,
                    port1=ONOS1Port )
            elif i >= 18 and i < 28:
                main.Mininet1.assignSwController(
                    sw=str( i ),
                    ip1=ONOS1Ip,
                    port1=ONOS1Port )
            else:
                main.Mininet1.assignSwController(
                    sw=str( i ),
                    ip1=ONOS1Ip,
                    port1=ONOS1Port )
        SwitchMastership = main.TRUE
        for i in range( 1, 29 ):
            if i == 1:
                response = main.Mininet1.getSwController( "s" + str( i ) )
                print( "Response is " + str( response ) )
                if re.search( "tcp:" + ONOS1Ip, response ):
                    SwitchMastership = SwitchMastership and main.TRUE
                else:
                    SwitchMastership = main.FALSE
            elif i >= 2 and i < 5:
                response = main.Mininet1.getSwController( "s" + str( i ) )
                print( "Response is " + str( response ) )
                if re.search( "tcp:" + ONOS1Ip, response ):
                    SwitchMastership = SwitchMastership and main.TRUE
                else:
                    SwitchMastership = main.FALSE
            elif i >= 5 and i < 8:
                response = main.Mininet1.getSwController( "s" + str( i ) )
                print( "Response is " + str( response ) )
                if re.search( "tcp:" + ONOS1Ip, response ):
                    SwitchMastership = SwitchMastership and main.TRUE
                else:
                    SwitchMastership = main.FALSE
            elif i >= 8 and i < 18:
                response = main.Mininet1.getSwController( "s" + str( i ) )
                print( "Response is " + str( response ) )
                if re.search( "tcp:" + ONOS1Ip, response ):
                    SwitchMastership = SwitchMastership and main.TRUE
                else:
                    SwitchMastership = main.FALSE
            elif i >= 18 and i < 28:
                response = main.Mininet1.getSwController( "s" + str( i ) )
                print( "Response is " + str( response ) )
                if re.search( "tcp:" + ONOS1Ip, response ):
                    SwitchMastership = SwitchMastership and main.TRUE
                else:
                    SwitchMastership = main.FALSE
            else:
                response = main.Mininet1.getSwController( "s" + str( i ) )
                print( "Response is" + str( response ) )
                if re.search( "tcp:" + ONOS1Ip, response ):
                    SwitchMastership = SwitchMastership and main.TRUE
                else:
                    SwitchMastership = main.FALSE

        if SwitchMastership == main.TRUE:
            main.log.report( "Controller assignmnet successful" )
        else:
            main.log.report( "Controller assignmnet failed" )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=SwitchMastership,
            onpass="MasterControllers assigned correctly" )
        """
        for i in range ( 1,29 ):
            main.Mininet1.assignSwController( sw=str( i ),count=5,
                    ip1=ONOS1Ip,port1=ONOS1Port,
                    ip2=ONOS2Ip,port2=ONOS2Port,
                    ip3=ONOS3Ip,port3=ONOS3Port,
                    ip4=ONOS4Ip,port4=ONOS4Port,
                    ip5=ONOS5Ip,port5=ONOS5Port )
        """
        # REACTIVE FWD test
        main.log.info( "Activate fwd app" )
        appInstallResult = main.ONOS2.activateApp( "org.onosproject.fwd" )
        appCheck = main.ONOS2.appToIDCheck()
        if appCheck != main.TRUE:
            main.log.warn( main.ONOS2.apps() )
            main.log.warn( main.ONOS2.appIDs() )
        time.sleep( 10 )

        main.step( "Get list of hosts from Mininet" )
        hostList = main.Mininet1.getHosts()
        main.log.info( hostList )

        main.step( "Get host list in ONOS format" )
        hostOnosList = main.ONOS2.getHostsId( hostList )
        main.log.info( hostOnosList )
        # time.sleep( 5 )

        main.step( "Pingall" )
        pingResult = main.FALSE
        time1 = time.time()
        pingResult = main.Mininet1.pingall()
        time2 = time.time()
        print "Time for pingall: %2f seconds" % ( time2 - time1 )

        # Start onos cli again because u might have dropped out of
        # onos prompt to the shell prompt
        # if there was no activity
        main.ONOS2.startOnosCli( ONOSIp=main.params[ 'CTRL' ][ 'ip1' ] )

        case4Result = SwitchMastership and pingResult
        if pingResult == main.TRUE:
            main.log.report( "Pingall Test in reactive mode to" +
                             " discover the hosts successful" )
        else:
            main.log.report( "Pingall Test in reactive mode to" +
                             " discover the hosts failed" )

        utilities.assert_equals(
            expect=main.TRUE,
            actual=case4Result,
            onpass="Controller assignment and Pingall Test successful",
            onfail="Controller assignment and Pingall Test NOT successful" )

    def CASE11( self ):
        # NOTE: This testcase require reactive forwarding mode enabled
        # NOTE: in the beginning and then uninstall it before adding 
        # NOTE: point intents. Again the app is installed so that 
        # NOTE: testcase 10 can be ran successively
        import time
        main.log.report(
            "This testcase moves a host from one switch to another to add" +
            "point intents between them and then perform ping" )
        main.log.report( "__________________________________" )
        main.log.info( "Moving host from one switch to another" )
        main.case( "Moving host from a device and attach it to another device" )
        main.step( "Moving host h9 from device s9 and attach it to s8" )
        main.Mininet1.moveHost(host = 'h9', oldSw = 's9', newSw = 's8')

        main.log.info( "Activate fwd app" )
        appInstallResult = main.ONOS2.activateApp( "org.onosproject.fwd" )
        appCheck = main.ONOS2.appToIDCheck()
        if appCheck != main.TRUE:
            main.log.warn( main.ONOS2.apps() )
            main.log.warn( main.ONOS2.appIDs() )

        time.sleep(25) #Time delay to have all the flows ready
        main.step( "Pingall" )
        pingResult = main.FALSE
        time1 = time.time()
        pingResult = main.Mininet1.pingall( timeout=120,
                                            shortCircuit=True,
                                            acceptableFailed=20 )
        time2 = time.time()
        print "Time for pingall: %2f seconds" % ( time2 - time1 )

        hosts = main.ONOS2.hosts( jsonFormat = False )
        main.log.info( hosts )
        
        main.log.info( "deactivate reactive forwarding app" )
        appUninstallResult = main.ONOS2.deactivateApp( "org.onosproject.fwd" )
        appCheck = main.ONOS2.appToIDCheck()
        if appCheck != main.TRUE:
            main.log.warn( main.ONOS2.apps() )
            main.log.warn( main.ONOS2.appIDs() )

        main.step( "Add point intents between hosts on the same device")
        ptpIntentResult = main.ONOS2.addPointIntent(
            "of:0000000000003008/1",
            "of:0000000000003008/3",
            ethType='IPV4',
            ethSrc='00:00:00:00:00:08',
            ethDst='00:00:00:00:00:09' )
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOS2.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOS2.addPointIntent(
            "of:0000000000003008/3",
            "of:0000000000003008/1",
            ethType='IPV4',
            ethSrc='00:00:00:00:00:09',
            ethDst='00:00:00:00:00:08' )
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOS2.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        main.case( "Ping hosts on the same devices" )
        ping = main.Mininet1.pingHost( src = 'h8', target = 'h9' )

        '''
        main.case( "Installing reactive forwarding app" )
        # Install onos-app-fwd app to enable reactive forwarding
        appUninstallResult = main.ONOS2.featureInstall( "onos-app-fwd" )
        main.log.info( "onos-app-fwd installed" )
        '''

        if ping == main.FALSE:
            main.log.report(
                "Point intents for hosts on same devices haven't" +
                " been installed correctly. Cleaning up" )
        if ping == main.TRUE:
            main.log.report(
                "Point intents for hosts on same devices" +
                "installed correctly. Cleaning up" )

        case11Result = ping
        utilities.assert_equals(
            expect = main.TRUE,
            actual = case11Result,
            onpass = "Point intents for hosts on same devices" +
                    "Ping Test successful",
            onfail = "Point intents for hosts on same devices" +
                    "Ping Test NOT successful" )

    def CASE12( self ):
        """
        Verify the default flows on each switch in proactive mode
        """
        main.log.report( "This testcase is verifying num of default" +
                         " flows on each switch" )
        main.log.report( "__________________________________" )
        main.case( "Verify num of default flows on each switch" )
        main.step( "Obtaining the device id's and flowrule count on them" )

        case12Result = main.TRUE
        idList = main.ONOS2.getAllDevicesId()
        for id in idList:
            count = main.ONOS2.FlowAddedCount( id )
            main.log.info("count = " +count)
            if int(count) != 3:
                case12Result = main.FALSE
                break
        utilities.assert_equals(
            expect=main.TRUE,
            actual=case12Result,
            onpass = "Expected default num of flows exist",
            onfail = "Expected default num of flows do not exist")

    def CASE6( self ):
        import time
        main.log.report( "This testcase is testing the addition of" +
                         " host intents and then does pingall" )
        main.log.report( "__________________________________" )
        main.case( "Obtaining host id's" )
        main.step( "Get hosts" )
        hosts = main.ONOS2.hosts()
        main.log.info( hosts )

        main.step( "Get all devices id" )
        devicesIdList = main.ONOS2.getAllDevicesId()
        main.log.info( devicesIdList )

        # ONOS displays the hosts in hex format unlike mininet which does
        # in decimal format
        # So take care while adding intents
        """
        main.step( "Add host-to-host intents for mininet hosts h8 and h18 or
                    ONOS hosts h8 and h12" )
        hthIntentResult = main.ONOS2.addHostIntent(
                            "00:00:00:00:00:08/-1", "00:00:00:00:00:12/-1" )
        hthIntentResult = main.ONOS2.addHostIntent(
                            "00:00:00:00:00:09/-1", "00:00:00:00:00:13/-1" )
        hthIntentResult = main.ONOS2.addHostIntent(
                            "00:00:00:00:00:0A/-1", "00:00:00:00:00:14/-1" )
        hthIntentResult = main.ONOS2.addHostIntent(
                            "00:00:00:00:00:0B/-1", "00:00:00:00:00:15/-1" )
        hthIntentResult = main.ONOS2.addHostIntent(
                            "00:00:00:00:00:0C/-1", "00:00:00:00:00:16/-1" )
        hthIntentResult = main.ONOS2.addHostIntent(
                            "00:00:00:00:00:0D/-1", "00:00:00:00:00:17/-1" )
        hthIntentResult = main.ONOS2.addHostIntent(
                            "00:00:00:00:00:0E/-1", "00:00:00:00:00:18/-1" )
        hthIntentResult = main.ONOS2.addHostIntent(
                            "00:00:00:00:00:0F/-1", "00:00:00:00:00:19/-1" )
        hthIntentResult = main.ONOS2.addHostIntent(
                            "00:00:00:00:00:10/-1", "00:00:00:00:00:1A/-1" )
        hthIntentResult = main.ONOS2.addHostIntent(
                            "00:00:00:00:00:11/-1", "00:00:00:00:00:1B/-1" )
        print "______________________________________________________"
        """
        intentsId = []
        for i in range( 8, 18 ):
            main.log.info(
                "Adding host intent between h" + str( i ) +
                " and h" + str( i + 10 ) )
            host1 = "00:00:00:00:00:" + \
                str( hex( i )[ 2: ] ).zfill( 2 ).upper()
            host2 = "00:00:00:00:00:" + \
                str( hex( i + 10 )[ 2: ] ).zfill( 2 ).upper()
            # NOTE: get host can return None
            if host1:
                host1Id = main.ONOS2.getHost( host1 )[ 'id' ]
            if host2:
                host2Id = main.ONOS2.getHost( host2 )[ 'id' ]
            if host1Id and host2Id:
                intentsId.append( main.ONOS2.addHostIntent( host1Id, host2Id ) )

        checkIntentResult = main.ONOS2.checkIntentState( intentsId )
        time.sleep( 10 )
        hIntents = main.ONOS2.intents( jsonFormat=False )
        main.log.info( "intents:" + hIntents )
        flows = main.ONOS2.flows()
        main.log.info( "flows:" + flows )     

        count = 1
        i = 8
        PingResult = main.TRUE
        # while i<10:
        while i < 18:
            main.log.info(
                "\n\nh" + str( i ) + " is Pinging h" + str( i + 10 ) )
            ping = main.Mininet1.pingHost(
                src="h" + str( i ), target="h" + str( i + 10 ) )
            if ping == main.FALSE and count < 5:
                count += 1
                # i = 8
                PingResult = main.FALSE
                main.log.report( "Ping between h" +
                                 str( i ) +
                                 " and h" +
                                 str( i +
                                      10 ) +
                                 " failed. Making attempt number " +
                                 str( count ) +
                                 " in 2 seconds" )
                time.sleep( 2 )
            elif ping == main.FALSE:
                main.log.report( "All ping attempts between h" +
                                 str( i ) +
                                 " and h" +
                                 str( i +
                                      10 ) +
                                 "have failed" )
                i = 19
                PingResult = main.FALSE
            elif ping == main.TRUE:
                main.log.info( "Ping test between h" +
                               str( i ) +
                               " and h" +
                               str( i +
                                    10 ) +
                               "passed!" )
                i += 1
                PingResult = main.TRUE
            else:
                main.log.info( "Unknown error" )
                PingResult = main.ERROR
        if PingResult == main.FALSE:
            main.log.report(
                "Ping all test after Host intent addition failed.Cleaning up" )
            # main.cleanup()
            # main.exit()
        if PingResult == main.TRUE:
            main.log.report(
                "Ping all test after Host intent addition successful" )

        checkIntentResult = main.ONOS2.checkIntentState( intentsId )

        case6Result = PingResult
        utilities.assert_equals(
            expect=main.TRUE,
            actual=case6Result,
            onpass="Pingall Test after Host intents addition successful",
            onfail="Pingall Test after Host intents addition failed" )

    def CASE5( self, main ):
        """
            Check ONOS topology matches with mininet
        """
        import json
        # assumes that sts is already in you PYTHONPATH
        from sts.topology.teston_topology import TestONTopology
        # main.ONOS2.startOnosCli( ONOSIp=main.params[ 'CTRL' ][ 'ip1' ] )
        main.log.report( "This testcase is testing if all ONOS nodes" +
                         " are in topology sync with mininet" )
        main.log.report( "__________________________________" )
        main.case( "Comparing Mininet topology with the topology of ONOS" )
        main.step( "Start continuous pings" )
        main.Mininet2.pingLong(
            src=main.params[ 'PING' ][ 'source1' ],
            target=main.params[ 'PING' ][ 'target1' ],
            pingTime=500 )
        main.Mininet2.pingLong(
            src=main.params[ 'PING' ][ 'source2' ],
            target=main.params[ 'PING' ][ 'target2' ],
            pingTime=500 )
        main.Mininet2.pingLong(
            src=main.params[ 'PING' ][ 'source3' ],
            target=main.params[ 'PING' ][ 'target3' ],
            pingTime=500 )
        main.Mininet2.pingLong(
            src=main.params[ 'PING' ][ 'source4' ],
            target=main.params[ 'PING' ][ 'target4' ],
            pingTime=500 )
        main.Mininet2.pingLong(
            src=main.params[ 'PING' ][ 'source5' ],
            target=main.params[ 'PING' ][ 'target5' ],
            pingTime=500 )
        main.Mininet2.pingLong(
            src=main.params[ 'PING' ][ 'source6' ],
            target=main.params[ 'PING' ][ 'target6' ],
            pingTime=500 )
        main.Mininet2.pingLong(
            src=main.params[ 'PING' ][ 'source7' ],
            target=main.params[ 'PING' ][ 'target7' ],
            pingTime=500 )
        main.Mininet2.pingLong(
            src=main.params[ 'PING' ][ 'source8' ],
            target=main.params[ 'PING' ][ 'target8' ],
            pingTime=500 )
        main.Mininet2.pingLong(
            src=main.params[ 'PING' ][ 'source9' ],
            target=main.params[ 'PING' ][ 'target9' ],
            pingTime=500 )
        main.Mininet2.pingLong(
            src=main.params[ 'PING' ][ 'source10' ],
            target=main.params[ 'PING' ][ 'target10' ],
            pingTime=500 )

        main.step( "Create TestONTopology object" )
        global ctrls
        ctrls = []
        count = 1
        while True:
            temp = ()
            if ( 'ip' + str( count ) ) in main.params[ 'CTRL' ]:
                temp = temp + ( getattr( main, ( 'ONOS' + str( count ) ) ), )
                temp = temp + ( "ONOS" + str( count ), )
                temp = temp + ( main.params[ 'CTRL' ][ 'ip' + str( count ) ], )
                temp = temp + \
                    ( eval( main.params[ 'CTRL' ][ 'port' + str( count ) ] ), )
                ctrls.append( temp )
                count = count + 1
            else:
                break
        global MNTopo
        Topo = TestONTopology(
            main.Mininet1,
            ctrls )  # can also add Intent API info for intent operations
        MNTopo = Topo

        TopologyCheck = main.TRUE
        main.step( "Compare ONOS Topology to MN Topology" )
        devicesJson = main.ONOS2.devices()
        linksJson = main.ONOS2.links()
        portsJson = main.ONOS2.ports()

        result1 = main.Mininet1.compareSwitches(
            MNTopo,
            json.loads( devicesJson ) )
        result2 = main.Mininet1.compareLinks(
            MNTopo,
            json.loads( linksJson ) )

        result3 = main.Mininet1.comparePorts( MNTopo, json.loads( portsJson ) )
        # result = result1 and result2 and result3
        result = result1 and result2

        print "***********************"
        if result == main.TRUE:
            main.log.report( "ONOS" + " Topology matches MN Topology" )
        else:
            main.log.report( "ONOS" + " Topology does not match MN Topology" )

        utilities.assert_equals(
            expect=main.TRUE,
            actual=result,
            onpass="ONOS" +
            " Topology matches MN Topology",
            onfail="ONOS" +
            " Topology does not match MN Topology" )

        TopologyCheck = TopologyCheck and result
        utilities.assert_equals(
            expect=main.TRUE,
            actual=TopologyCheck,
            onpass="Topology checks passed",
            onfail="Topology checks failed" )

    def CASE7( self, main ):
        """
            Link discovery test case. Checks if ONOS can discover a link
            down or up properly.
        """

        from sts.topology.teston_topology import TestONTopology

        linkSleep = int( main.params[ 'timers' ][ 'LinkDiscovery' ] )

        main.log.report( "This testscase is killing a link to ensure that" +
                         " link discovery is consistent" )
        main.log.report( "__________________________________" )
        main.log.report( "Killing a link to ensure that link discovery" +
                         " is consistent" )
        main.case( "Killing a link to Ensure that Link Discovery" +
                   "is Working Properly" )
        """
        main.step( "Start continuous pings" )

        main.Mininet2.pingLong( src=main.params[ 'PING' ][ 'source1' ],
                               target=main.params[ 'PING' ][ 'target1' ],
                               pingTime=500 )
        main.Mininet2.pingLong( src=main.params[ 'PING' ][ 'source2' ],
                               target=main.params[ 'PING' ][ 'target2' ],
                               pingTime=500 )
        main.Mininet2.pingLong( src=main.params[ 'PING' ][ 'source3' ],
                               target=main.params[ 'PING' ][ 'target3' ],
                               pingTime=500 )
        main.Mininet2.pingLong( src=main.params[ 'PING' ][ 'source4' ],
                               target=main.params[ 'PING' ][ 'target4' ],
                               pingTime=500 )
        main.Mininet2.pingLong( src=main.params[ 'PING' ][ 'source5' ],
                               target=main.params[ 'PING' ][ 'target5' ],
                               pingTime=500 )
        main.Mininet2.pingLong( src=main.params[ 'PING' ][ 'source6' ],
                               target=main.params[ 'PING' ][ 'target6' ],
                               pingTime=500 )
        main.Mininet2.pingLong( src=main.params[ 'PING' ][ 'source7' ],
                               target=main.params[ 'PING' ][ 'target7' ],
                               pingTime=500 )
        main.Mininet2.pingLong( src=main.params[ 'PING' ][ 'source8' ],
                               target=main.params[ 'PING' ][ 'target8' ],
                               pingTime=500 )
        main.Mininet2.pingLong( src=main.params[ 'PING' ][ 'source9' ],
                               target=main.params[ 'PING' ][ 'target9' ],
                               pingTime=500 )
        main.Mininet2.pingLong( src=main.params[ 'PING' ][ 'source10' ],
                               target=main.params[ 'PING' ][ 'target10' ],
                               pingTime=500 )
        """
        main.step( "Determine the current number of switches and links" )
        topologyOutput = main.ONOS2.topology()
        topologyResult = main.ONOS1.getTopology( topologyOutput )
        activeSwitches = topologyResult[ 'devices' ]
        links = topologyResult[ 'links' ]
        print "activeSwitches = ", type( activeSwitches )
        print "links = ", type( links )
        main.log.info(
            "Currently there are %s switches and %s links" %
            ( str( activeSwitches ), str( links ) ) )

        main.step( "Kill Link between s3 and s28" )
        main.Mininet1.link( END1="s3", END2="s28", OPTION="down" )
        time.sleep( linkSleep )
        topologyOutput = main.ONOS2.topology()
        LinkDown = main.ONOS1.checkStatus(
            topologyOutput, activeSwitches, str(
                int( links ) - 2 ) )
        if LinkDown == main.TRUE:
            main.log.report( "Link Down discovered properly" )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=LinkDown,
            onpass="Link Down discovered properly",
            onfail="Link down was not discovered in " +
            str( linkSleep ) +
            " seconds" )

        # Check ping result here..add code for it

        main.step( "Bring link between s3 and s28 back up" )
        LinkUp = main.Mininet1.link( END1="s3", END2="s28", OPTION="up" )
        time.sleep( linkSleep )
        topologyOutput = main.ONOS2.topology()
        LinkUp = main.ONOS1.checkStatus(
            topologyOutput,
            activeSwitches,
            str( links ) )
        if LinkUp == main.TRUE:
            main.log.report( "Link up discovered properly" )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=LinkUp,
            onpass="Link up discovered properly",
            onfail="Link up was not discovered in " +
            str( linkSleep ) +
            " seconds" )

        # NOTE Check ping result here..add code for it

        main.step( "Compare ONOS Topology to MN Topology" )
        Topo = TestONTopology(
            main.Mininet1,
            ctrls )  # can also add Intent API info for intent operations
        MNTopo = Topo
        TopologyCheck = main.TRUE

        devicesJson = main.ONOS2.devices()
        linksJson = main.ONOS2.links()
        portsJson = main.ONOS2.ports()

        result1 = main.Mininet1.compareSwitches(
            MNTopo,
            json.loads( devicesJson ) )
        result2 = main.Mininet1.compareLinks(
            MNTopo,
            json.loads( linksJson ) )
        result3 = main.Mininet1.comparePorts( MNTopo, json.loads( portsJson ) )

        # result = result1 and result2 and result3
        result = result1 and result2
        print "***********************"

        if result == main.TRUE:
            main.log.report( "ONOS" + " Topology matches MN Topology" )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=result,
            onpass="ONOS" +
            " Topology matches MN Topology",
            onfail="ONOS" +
            " Topology does not match MN Topology" )

        TopologyCheck = TopologyCheck and result
        utilities.assert_equals(
            expect=main.TRUE,
            actual=TopologyCheck,
            onpass="Topology checks passed",
            onfail="Topology checks failed" )

        result = LinkDown and LinkUp and TopologyCheck
        utilities.assert_equals( expect=main.TRUE, actual=result,
                                 onpass="Link failure is discovered correctly",
                                 onfail="Link Discovery failed" )

    def CASE8( self ):
        """
        Intent removal
        """
        import time
        main.log.report( "This testcase removes any previously added intents" +
                         " before adding any new set of intents" )
        main.log.report( "__________________________________" )
        main.log.info( "intent removal" )
        main.case( "Removing installed intents" )
        main.step( "Obtain the intent id's" )
        currentIntents = main.ONOS2.intents( jsonFormat=False )
        main.log.info( "intent_result = " + currentIntents )
        intentLinewise = currentIntents.split( "\n" )

        intentList = [line for line in intentLinewise \
            if line.startswith( "id=")]
        intentids = [line.split( "," )[ 0 ].split( "=" )[ 1 ] for line in \
            intentList]
        for id in intentids:
            print "id = ", id

        main.step(
            "Iterate through the intentids list and remove each intent" )
        for id in intentids:
            main.ONOS2.removeIntent( intentId=id ,purge=True)

        remainingIntents = main.ONOS2.intents( jsonFormat=False )
        main.log.info( "intent_result = " + remainingIntents )
        if remainingIntents:
            main.log.info( "There are still remaining intents " )
            intentResult = main.FALSE
        else:
            intentResult = main.TRUE

        intentList = [line for line in remainingIntents.split( "\n" ) \
            if line.startswith( "id=")]
        intentState = [line.split( "," )[ 1 ].split( "=" )[ 1 ] for line in \
            intentList]
        for state in intentState:
            print state
        
        case8Result = main.TRUE
        for state in intentState:
            if state != 'WITHDRAWN':
                case8Result = main.FALSE
                break

        PingResult = main.TRUE
        """
        if case8Result == main.TRUE:
            i = 8
            while i < 18:
                main.log.info(
                    "\n\nh" + str( i ) + " is Pinging h" + str( i + 10 ) )
                ping = main.Mininet1.pingHost(
                    src="h" + str( i ), target="h" + str( i + 10 ) )
                if ping == main.TRUE:
                    i = 19
                    PingResult = PingResult and main.TRUE
                elif ping == main.FALSE:
                    i += 1
                    PingResult = PingResult and main.FALSE
                else:
                    main.log.info( "Unknown error" )
                    PingResult = main.ERROR
        
            # Note: If the ping result failed, that means the intents have been
            # withdrawn correctly.
        if PingResult == main.TRUE:
            main.log.report( "Installed intents have not been withdrawn correctly" )
            # main.cleanup()
            # main.exit()
        if PingResult == main.FALSE:
            main.log.report( "Installed intents have been withdrawn correctly" )
        """

        if case8Result:
            main.log.report( "Intent removal successful" )
        else:
            main.log.report( "Intent removal failed" )

        utilities.assert_equals( expect=main.TRUE, actual=case8Result,
                                 onpass="Intent removal test passed",
                                 onfail="Intent removal test failed" )

    def CASE9( self ):
        """
            Testing Point intents
        """
        main.log.report(
            "This test case adds point intents and then does pingall" )
        main.log.report( "__________________________________" )
        main.log.info( "Adding point intents" )
        main.case(
            "Adding bidirectional point for mn hosts" +
            "( h8-h18, h9-h19, h10-h20, h11-h21, h12-h22, " +
            "h13-h23, h14-h24, h15-h25, h16-h26, h17-h27 )" )
        macsDict = {}
        for i in range( 1,29 ):
            macsDict[ 'h' + str( i ) ]= main.Mininet1.getMacAddress( host='h'+ str( i ) )
        print macsDict
        main.step( "Add point intents for mn hosts h8 and h18 or" +
                   "ONOS hosts h8 and h12" )
        # main.step(var1)
        ptpIntentResult = main.ONOS2.addPointIntent(
            ingressDevice="of:0000000000003008/1",
            egressDevice="of:0000000000006018/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h8' ))
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOS2.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOS2.addPointIntent(
            ingressDevice="of:0000000000006018/1",
            egressDevice="of:0000000000003008/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h18' ))
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOS2.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        var2 = "Add point intents for mn hosts h9&h19 or ONOS hosts h9&h13"
        main.step(var2)
        ptpIntentResult = main.ONOS2.addPointIntent(
            "of:0000000000003009/1",
            "of:0000000000006019/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h9' ))
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOS2.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOS2.addPointIntent(
            "of:0000000000006019/1",
            "of:0000000000003009/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h19' ))
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOS2.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        var3 = "Add point intents for MN hosts h10&h20 or ONOS hosts hA&h14"
        main.step(var3)
        ptpIntentResult = main.ONOS2.addPointIntent(
            "of:0000000000003010/1",
            "of:0000000000006020/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h10' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOS2.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOS2.addPointIntent(
            "of:0000000000006020/1",
            "of:0000000000003010/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h20' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOS2.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        var4 = "Add point intents for mininet hosts h11 and h21 or" +\
               " ONOS hosts hB and h15"
        main.case(var4)
        ptpIntentResult = main.ONOS2.addPointIntent(
            "of:0000000000003011/1",
            "of:0000000000006021/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h11' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOS2.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOS2.addPointIntent(
            "of:0000000000006021/1",
            "of:0000000000003011/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h21' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOS2.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        var5 = "Add point intents for mininet hosts h12 and h22 " +\
               "ONOS hosts hC and h16"
        main.case(var5)
        ptpIntentResult = main.ONOS2.addPointIntent(
            "of:0000000000003012/1",
            "of:0000000000006022/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h12' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOS2.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOS2.addPointIntent(
            "of:0000000000006022/1",
            "of:0000000000003012/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h22' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOS2.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        var6 = "Add point intents for mininet hosts h13 and h23 or" +\
               " ONOS hosts hD and h17"
        main.case(var6)
        ptpIntentResult = main.ONOS2.addPointIntent(
            "of:0000000000003013/1",
            "of:0000000000006023/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h13' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOS2.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOS2.addPointIntent(
            "of:0000000000006023/1",
            "of:0000000000003013/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h23' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOS2.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        var7 = "Add point intents for mininet hosts h14 and h24 or" +\
               " ONOS hosts hE and h18"
        main.case(var7)
        ptpIntentResult = main.ONOS2.addPointIntent(
            "of:0000000000003014/1",
            "of:0000000000006024/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h14' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOS2.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOS2.addPointIntent(
            "of:0000000000006024/1",
            "of:0000000000003014/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h24' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOS2.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        var8 = "Add point intents for mininet hosts h15 and h25 or" +\
               " ONOS hosts hF and h19"
        main.case(var8)
        ptpIntentResult = main.ONOS2.addPointIntent(
            "of:0000000000003015/1",
            "of:0000000000006025/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h15' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOS2.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOS2.addPointIntent(
            "of:0000000000006025/1",
            "of:0000000000003015/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h25' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOS2.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        var9 = "Add intents for mininet hosts h16 and h26 or" +\
               " ONOS hosts h10 and h1A"
        main.case(var9)
        ptpIntentResult = main.ONOS2.addPointIntent(
            "of:0000000000003016/1",
            "of:0000000000006026/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h16' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOS2.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOS2.addPointIntent(
            "of:0000000000006026/1",
            "of:0000000000003016/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h26' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOS2.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        var10 = "Add point intents for mininet hosts h17 and h27 or" +\
                " ONOS hosts h11 and h1B"
        main.case(var10)
        ptpIntentResult = main.ONOS2.addPointIntent(
            "of:0000000000003017/1",
            "of:0000000000006027/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h17' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOS2.intents()
            main.log.info( "Point to point intent install successful" )
            #main.log.info( getIntentResult )

        ptpIntentResult = main.ONOS2.addPointIntent(
            "of:0000000000006027/1",
            "of:0000000000003017/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h27' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOS2.intents()
            main.log.info( "Point to point intent install successful" )
            #main.log.info( getIntentResult )

        print(
            "___________________________________________________________" )

        flowHandle = main.ONOS2.flows()
        #main.log.info( "flows :" + flowHandle )

        count = 1
        i = 8
        PingResult = main.TRUE
        while i < 18:
            main.log.info(
                "\n\nh" + str( i ) + " is Pinging h" + str( i + 10 ) )
            ping = main.Mininet1.pingHost(
                src="h" + str( i ), target="h" + str( i + 10 ) )
            if ping == main.FALSE and count < 5:
                count += 1
                # i = 8
                PingResult = main.FALSE
                main.log.report( "Ping between h" +
                                 str( i ) +
                                 " and h" +
                                 str( i +
                                      10 ) +
                                 " failed. Making attempt number " +
                                 str( count ) +
                                 " in 2 seconds" )
                time.sleep( 2 )
            elif ping == main.FALSE:
                main.log.report( "All ping attempts between h" +
                                 str( i ) +
                                 " and h" +
                                 str( i +
                                      10 ) +
                                 "have failed" )
                i = 19
                PingResult = main.FALSE
            elif ping == main.TRUE:
                main.log.info( "Ping test between h" +
                               str( i ) +
                               " and h" +
                               str( i +
                                    10 ) +
                               "passed!" )
                i += 1
                PingResult = main.TRUE
            else:
                main.log.info( "Unknown error" )
                PingResult = main.ERROR

        if PingResult == main.FALSE:
            main.log.report(
                "Point intents have not ben installed correctly. Cleaning up" )
            # main.cleanup()
            # main.exit()
        if PingResult == main.TRUE:
            main.log.report( "Point Intents have been installed correctly" )

        case9Result = PingResult
        utilities.assert_equals(
            expect=main.TRUE,
            actual=case9Result,
            onpass="Point intents addition and Pingall Test successful",
            onfail="Point intents addition and Pingall Test NOT successful" )
