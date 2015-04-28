
# Testing the basic functionality of ONOS Next
# For sanity and driver functionality excercises only.

import time
# import sys
# import os
# import re
import json

time.sleep( 1 )

class IpOptical:

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

        main.step( "Removing raft logs before a clen installation of ONOS" )
        main.ONOSbench.onosRemoveRaftLogs()

        main.step( "Git checkout and get version" )
        #main.ONOSbench.gitCheckout( "master" )
        gitPullResult = main.ONOSbench.gitPull()
        main.log.info( "git_pull_result = " + str( gitPullResult ))
        main.ONOSbench.getVersion( report=True )

        if gitPullResult == 1:
            main.step( "Using mvn clean & install" )
            main.ONOSbench.cleanInstall()
        elif gitPullResult == 0:
            main.log.report(
                "Git Pull Failed, look into logs for detailed reason" )
            main.cleanup()
            main.exit()

        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.onosPackage()

        main.step( "Uninstalling ONOS package" )
        ONOSip1 = main.params[ 'CTRL' ][ 'ip1' ]
        onosUninstallResult = main.ONOSbench.onosUninstall( nodeIp = ONOSip1)
        if onosUninstallResult:
            main.log.report( "Uninstalling ONOS package successful" )
        else:
            main.log.report( "Uninstalled ONOS package unsucessful" )
        time.sleep( 5 )
        main.step( "Installing ONOS package" )
        onosInstallResult = main.ONOSbench.onosInstall( node = ONOSip1 )
        if onosInstallResult == main.TRUE:
            main.log.report( "Installing ONOS package successful" )
        else:
            main.log.report( "Installing ONOS package failed" )

        onos1Isup = main.ONOSbench.isup()
        if onos1Isup == main.TRUE:
            main.log.report( "ONOS instance is up and ready" )
        else:
            main.log.report( "ONOS instance may not be up" )

        main.step( "Starting ONOS service" )
        startResult = main.ONOSbench.onosStart( ONOS1Ip )

        main.ONOS2.startOnosCli( ONOSIp=main.params[ 'CTRL' ][ 'ip1' ] )
        main.step( "Starting Mininet CLI..." )
        
        case1Result = ( packageResult and
                        cellResult and verifyResult
                        and onosInstallResult and
                        onos1Isup and startResult )
        utilities.assert_equals( expect=main.TRUE, actual=case1Result,
                                 onpass="Test startup successful",
                                 onfail="Test startup NOT successful" )

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

        case20Result = step1Result and step3Result and\
                       step4Result and step5Result and step6Result and\
                       step7Result
        utilities.assert_equals(
            expect=main.TRUE,
            actual=case20Result,
            onpass= "Exiting functionality mininet topology and reinstalling" +
                    " ONOS successful",
            onfail= "Exiting functionality mininet topology and reinstalling" +
                    " ONOS failed" )

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

        case21Result = step1Result and step2Result
        utilities.assert_equals(
            expect=main.TRUE,
            actual=case21Result,
            onpass="Packet optical topology spawned successsfully",
            onfail="Packet optical topology spawning failed" )

    def CASE22( self, main ):
        """
            Curretly we use, 10 optical switches(ROADM's) and
            6 packet layer mininet switches each with one host.
            Therefore, the roadmCount variable = 10,
            packetLayerSWCount variable = 6, hostCount=6 and
            links=42.
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
        if linkActiveCount == 42:
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

        case22Result = step1Result and step2Result

        utilities.assert_equals(
            expect=main.TRUE,
            actual=case22Result,
            onpass="Packet optical topology discovery successful",
            onfail="Packet optical topology discovery failed" )

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
        step1Result = main.TRUE
        intentsId = []
        pIntent1 = main.ONOS3.addPointIntent(
            "of:0000ffffffff0001/1",
            "of:0000ffffffff0005/1" )
        pIntent2 = main.ONOS3.addPointIntent(
            "of:0000ffffffff0005/1",
            "of:0000ffffffff0001/1" )
        intentsId.append( pIntent1 )
        intentsId.append( pIntent2 )
        main.log.info( "Checking intents state")
        checkStateResult = main.ONOS3.checkIntentState( intentsId = intentsId )
        time.sleep( 30 )
        main.log.info( "Checking flows state")
        checkFlowResult = main.ONOS3.checkFlowsState()
        # Sleep for 30 seconds to provide time for the intent state to change
        time.sleep( 30 )
        main.log.info( "Checking intents state one more time")
        checkStateResult = main.ONOS3.checkIntentState( intentsId = intentsId )
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

        case23Result = step1Result and step2Result
        utilities.assert_equals(
            expect=main.TRUE,
            actual=case23Result,
            onpass="Point intents are installed properly",
            onfail="Failed to install point intents" )

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

        case24Result = step1Result and step2Result and step3Result \
                       and step4Result
        utilities.assert_equals( expect=main.TRUE,
                                 actual=case24Result,
                                 onpass="Packet optical rerouting successful",
                                 onfail="Packet optical rerouting failed" )

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

        case10Result = step1Result
        utilities.assert_equals(
            expect=main.TRUE,
            actual=case10Result,
            onpass="Reactive forwarding app uninstallation successful",
            onfail="Reactive forwarding app uninstallation failed" )

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
        case25Result = step1Result and step2Result and step3Result and \
                       step4Result
        utilities.assert_equals( expect=main.TRUE,
                                 actual=case25Result,
                                 onpass="Add host intent successful",
                                 onfail="Add host intent failed" )
