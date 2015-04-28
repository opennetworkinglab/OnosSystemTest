
# Testing the basic functionality of ONOS Next
# For sanity and driver functionality excercises only.

import time
import sys
import os
import re
import time
import json

time.sleep( 1 )

class IpOpticalMulti:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        """
        Startup sequence:
        cell <name>
        onos-verify-cell
        onos-remove-raft-logs
        git pull
        mvn clean install
        onos-package
        onos-install -f
        onos-wait-for-start
        """
        cellName = main.params[ 'ENV' ][ 'cellName' ]
        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]
        ONOS2Ip = main.params[ 'CTRL' ][ 'ip2' ]
        ONOS3Ip = main.params[ 'CTRL' ][ 'ip3' ]
        ONOS1Port = main.params[ 'CTRL' ][ 'port1' ]
        ONOS2Port = main.params[ 'CTRL' ][ 'port2' ]
        ONOS3Port = main.params[ 'CTRL' ][ 'port3' ]

        main.case( "Setting up test environment" )
        main.log.report(
            "This testcase is testing setting up test environment" )
        main.log.report( "__________________________________" )

        main.step( "Applying cell variable to environment" )
        cellResult1 = main.ONOSbench.setCell( cellName )
        # cellResult2 = main.ONOScli1.setCell( cellName )
        # cellResult3 = main.ONOScli2.setCell( cellName )
        # cellResult4 = main.ONOScli3.setCell( cellName )
        verifyResult = main.ONOSbench.verifyCell()
        cellResult = cellResult1

        main.step( "Removing raft logs before a clen installation of ONOS" )
        removeLogResult = main.ONOSbench.onosRemoveRaftLogs()

        main.step( "Git checkout, pull and get version" )
        #main.ONOSbench.gitCheckout( "master" )
        gitPullResult = main.ONOSbench.gitPull()
        main.log.info( "git_pull_result = " + str( gitPullResult ))
        versionResult = main.ONOSbench.getVersion( report=True )

        if gitPullResult == 1:
            main.step( "Using mvn clean & install" )
            cleanInstallResult = main.ONOSbench.cleanInstall()
            # cleanInstallResult = main.TRUE

        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.onosPackage()

        # main.step( "Creating a cell" )
        # cellCreateResult = main.ONOSbench.createCellFile( **************
        # )

        main.step( "Installing ONOS package" )
        onos1InstallResult = main.ONOSbench.onosInstall(
            options="-f",
            node=ONOS1Ip )
        onos2InstallResult = main.ONOSbench.onosInstall(
            options="-f",
            node=ONOS2Ip )
        onos3InstallResult = main.ONOSbench.onosInstall(
            options="-f",
            node=ONOS3Ip )
        onosInstallResult = onos1InstallResult and onos2InstallResult and\
                onos3InstallResult
        if onosInstallResult == main.TRUE:
            main.log.report( "Installing ONOS package successful" )
        else:
            main.log.report( "Installing ONOS package failed" )

        onos1Isup = main.ONOSbench.isup( ONOS1Ip )
        onos2Isup = main.ONOSbench.isup( ONOS2Ip )
        onos3Isup = main.ONOSbench.isup( ONOS3Ip )
        onosIsup = onos1Isup and onos2Isup and onos3Isup
        if onosIsup == main.TRUE:
            main.log.report( "ONOS instances are up and ready" )
        else:
            main.log.report( "ONOS instances may not be up" )

        main.step( "Starting ONOS service" )
        startResult = main.TRUE
        # startResult = main.ONOSbench.onosStart( ONOS1Ip )
        startcli1 = main.ONOScli1.startOnosCli( ONOSIp=ONOS1Ip )
        startcli2 = main.ONOScli2.startOnosCli( ONOSIp=ONOS2Ip )
        startcli3 = main.ONOScli3.startOnosCli( ONOSIp=ONOS3Ip )
        print startcli1
        print startcli2
        print startcli3

        case1Result = ( packageResult and
                        cellResult and verifyResult and onosInstallResult and
                        onosIsup and startResult )
        utilities.assertEquals( expect=main.TRUE, actual=case1Result,
                                onpass="Test startup successful",
                                onfail="Test startup NOT successful" )

    def CASE10( self ):
        import time
        main.log.report(
            "This testcase uninstalls the reactive forwarding app" )
        main.log.report( "__________________________________" )
        main.case( "Uninstalling reactive forwarding app" )
        # Unistall onos-app-fwd app to disable reactive forwarding
        appInstallResult = main.ONOScli1.deactivateApp( "org.onosproject.fwd" )
        appCheck = main.ONOScli1.appToIDCheck()
        if appCheck != main.TRUE:
            main.log.warn( main.ONOScli1.apps() )
            main.log.warn( main.ONOScli1.appIDs() )
        main.log.info( "onos-app-fwd uninstalled" )

        # After reactive forwarding is disabled,
        # the reactive flows on switches timeout in 10-15s
        # So sleep for 15s
        time.sleep( 15 )

        hosts = main.ONOScli1.hosts()
        main.log.info( hosts )
        case10Result = appInstallResult
        utilities.assertEquals(
            expect=main.TRUE,
            actual=case10Result,
            onpass="Reactive forwarding app uninstallation successful",
            onfail="Reactive forwarding app uninstallation failed" )

    def CASE20( self ):
        """
            Exit from mininet cli
            reinstall ONOS
        """
        cellName = main.params[ 'ENV' ][ 'cellName' ]
        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]
        ONOS2Ip = main.params[ 'CTRL' ][ 'ip2' ]
        ONOS3Ip = main.params[ 'CTRL' ][ 'ip3' ]
        ONOS1Port = main.params[ 'CTRL' ][ 'port1' ]
        ONOS2Port = main.params[ 'CTRL' ][ 'port2' ]
        ONOS3Port = main.params[ 'CTRL' ][ 'port3' ]

        main.log.report( "This testcase exits the mininet cli and reinstalls" +
                         "ONOS to switch over to Packet Optical topology" )
        main.log.report( "_____________________________________________" )
        main.case( "Disconnecting mininet and restarting ONOS" )
        main.step( "Disconnecting mininet and restarting ONOS" )
        mininetDisconnect = main.Mininet1.disconnect()
        print "mininetDisconnect = ", mininetDisconnect

        main.step( "Removing raft logs before a clen installation of ONOS" )
        main.ONOSbench.onosRemoveRaftLogs()

        main.step( "Applying cell variable to environment" )
        cellResult = main.ONOSbench.setCell( cellName )
        verifyResult = main.ONOSbench.verifyCell()


        main.step( "Installing ONOS package" )
        onos1InstallResult = main.ONOSbench.onosInstall(
            options="-f",
            node=ONOS1Ip )
        onos2InstallResult = main.ONOSbench.onosInstall(
            options="-f",
            node=ONOS2Ip )
        onos3InstallResult = main.ONOSbench.onosInstall(
            options="-f",
            node=ONOS3Ip )
        onosInstallResult = onos1InstallResult and onos2InstallResult and\
                onos3InstallResult
        if onosInstallResult == main.TRUE:
            main.log.report( "Installing ONOS package successful" )
        else:
            main.log.report( "Installing ONOS package failed" )

        onos1Isup = main.ONOSbench.isup( ONOS1Ip )
        onos2Isup = main.ONOSbench.isup( ONOS2Ip )
        onos3Isup = main.ONOSbench.isup( ONOS3Ip )
        onosIsup = onos1Isup and onos2Isup and onos3Isup
        if onosIsup == main.TRUE:
            main.log.report( "ONOS instances are up and ready" )
        else:
            main.log.report( "ONOS instances may not be up" )

        main.step( "Starting ONOS service" )
        startResult = main.TRUE
        # startResult = main.ONOSbench.onosStart( ONOS1Ip )
        startcli1 = main.ONOScli1.startOnosCli( ONOSIp=ONOS1Ip )
        startcli2 = main.ONOScli2.startOnosCli( ONOSIp=ONOS2Ip )
        startcli3 = main.ONOScli3.startOnosCli( ONOSIp=ONOS3Ip )
        startResult = startcli1 and startcli2 and startcli3
        if startResult == main.TRUE:
            main.log.report( "ONOS cli starts properly" )
        case20Result = mininetDisconnect and cellResult and verifyResult \
            and onosInstallResult and onosIsup and startResult

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
            sudo -E python ~/onos/tools/test/topos/opticalTest.py -OC1 <Ctrls>
            which spawns packet optical topology and copies the links
            json file to the onos instance.
            Note that in case of Packet Optical, the links are not learnt
            from the topology, instead the links are learnt
            from the json config file
        """
        main.log.report(
            "This testcase starts the packet layer topology and REST" )
        main.log.report( "_____________________________________________" )
        main.case( "Starting LINC-OE and other components" )
        main.step( "Starting LINC-OE and other components" )
        main.log.info( "Activate optical app" )
        appInstallResult = main.ONOScli1.activateApp( "org.onosproject.optical" )
        appCheck = main.ONOScli1.appToIDCheck()
        appCheck = appCheck and main.ONOScli2.appToIDCheck()
        appCheck = appCheck and main.ONOScli3.appToIDCheck()
        if appCheck != main.TRUE:
            main.log.warn( "Checking ONOS application unsuccesful" )

        ctrllerIP = []
        ctrllerIP.append( main.params[ 'CTRL' ][ 'ip1' ] )
        #ctrllerIP.append( main.params[ 'CTRL' ][ 'ip2' ] )
        #ctrllerIP.append( main.params[ 'CTRL' ][ 'ip3' ] )
        opticalMnScript = main.LincOE2.runOpticalMnScript( ctrllerIP = ctrllerIP )
        case21Result = opticalMnScript and appInstallResult
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
        main.log.report(
            "This testcase compares the optical+packet topology against what" +
            " is expected" )
        main.case( "Topology comparision" )
        main.step( "Topology comparision" )
        devicesResult = main.ONOScli3.devices( jsonFormat=False )

        print "devices_result = ", devicesResult
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
        print "_________________________________"

        linksResult = main.ONOScli3.links( jsonFormat=False )
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

        case22Result = opticalSWResult and packetSWResult and \
                        linkActiveResult
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
        main.case( "Topology comparision" )
        main.step( "Adding point intents" )
        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000ffffffff0001/1",
            "of:0000ffffffff0005/1" )
        if ptpIntentResult == main.TRUE:
            main.ONOScli1.intents( jsonFormat=False )
            main.log.info( "Point to point intent install successful" )

        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000ffffffff0005/1",
            "of:0000ffffffff0001/1" )
        if ptpIntentResult == main.TRUE:
            main.ONOScli1.intents( jsonFormat=False )
            main.log.info( "Point to point intent install successful" )

        time.sleep( 30 )
        flowHandle = main.ONOScli1.flows()
        main.log.info( "flows :" + flowHandle )

        # Sleep for 30 seconds to provide time for the intent state to change
        time.sleep( 60 )
        intentHandle = main.ONOScli1.intents( jsonFormat=False )
        main.log.info( "intents :" + intentHandle )

        PingResult = main.TRUE
        count = 1
        main.log.info( "\n\nh1 is Pinging h5" )
        ping = main.LincOE2.pingHostOptical( src="h1", target="h5" )
        # ping = main.LincOE2.pinghost()
        if ping == main.FALSE and count < 5:
            count += 1
            PingResult = main.FALSE
            main.log.info(
                "Ping between h1 and h5  failed. Making attempt number " +
                str( count ) +
                " in 2 seconds" )
            time.sleep( 2 )
        elif ping == main.FALSE:
            main.log.info( "All ping attempts between h1 and h5 have failed" )
            PingResult = main.FALSE
        elif ping == main.TRUE:
            main.log.info( "Ping test between h1 and h5 passed!" )
            PingResult = main.TRUE
        else:
            main.log.info( "Unknown error" )
            PingResult = main.ERROR

        if PingResult == main.FALSE:
            main.log.report(
                "Point intents for packet optical have not ben installed" +
                " correctly. Cleaning up" )
        if PingResult == main.TRUE:
            main.log.report(
                "Point Intents for packet optical have been " +
                "installed correctly" )

        case23Result = PingResult
        utilities.assert_equals(
            expect=main.TRUE,
            actual=case23Result,
            onpass= "Point intents addition for packet optical and" +
                    "Pingall Test successful",
            onfail= "Point intents addition for packet optical and" +
                    "Pingall Test NOT successful" )

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
        attachConsole = main.LincOE1.attachLincOESession()
        print "attachConsole = ", attachConsole

        main.step( "Bring a port down and verify the link state" )
        main.LincOE1.portDown( swId="9", ptId="20" )
        linksNonjson = main.ONOScli3.links( jsonFormat=False )
        main.log.info( "links = " + linksNonjson )

        linkInactiveCount = linksNonjson.count("state=INACTIVE")
        main.log.info( "linkInactiveCount = " + str( linkInactiveCount ))
        if linkInactiveCount == 2:
            main.log.info(
                "Number of links in INACTIVE state are correct")
        else:
            main.log.info(
                "Number of links in INACTIVE state are wrong")
        
        links = main.ONOScli3.links()
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

        print "links_state_result = ", linksStateResult
        time.sleep( 10 )
        flowHandle = main.ONOScli3.flows()
        main.log.info( "flows :" + flowHandle )

        main.step( "Verify Rerouting by a ping test" )
        PingResult = main.TRUE
        count = 1
        main.log.info( "\n\nh1 is Pinging h5" )
        ping = main.LincOE2.pingHostOptical( src="h1", target="h5" )
        # ping = main.LincOE2.pinghost()
        if ping == main.FALSE and count < 5:
            count += 1
            PingResult = main.FALSE
            main.log.info(
                "Ping between h1 and h5  failed. Making attempt number " +
                str( count ) +
                " in 2 seconds" )
            time.sleep( 2 )
        elif ping == main.FALSE:
            main.log.info( "All ping attempts between h1 and h5 have failed" )
            PingResult = main.FALSE
        elif ping == main.TRUE:
            main.log.info( "Ping test between h1 and h5 passed!" )
            PingResult = main.TRUE
        else:
            main.log.info( "Unknown error" )
            PingResult = main.ERROR

        if PingResult == main.TRUE:
            main.log.report( "Ping test successful " )
        if PingResult == main.FALSE:
            main.log.report( "Ping test failed" )

        case24Result = PingResult and linksStateResult
        utilities.assert_equals( expect=main.TRUE, actual=case24Result,
                                 onpass="Packet optical rerouting successful",
                                 onfail="Packet optical rerouting failed" )

    def CASE25( self ):
        """
            Add host intents between 2 packet layer host
        """
        import time
        import json
        main.log.report( "Adding host intents between 2 packet layer host" )
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
        intentsId = []
        # Use arping to discover the hosts
        main.LincOE2.arping( host = "h1" )
        main.LincOE2.arping( host = "h2" )
        # Adding host intent
        main.log.step( "Adding host intents to h1 and h2" )
        intent1 = main.ONOScli1.addHostIntent( hostIdOne = host1,
                                            hostIdTwo = host2 )
        intentsId.append( intent1 )
        time.sleep( 5 )
        intent2 = main.ONOScli1.addHostIntent( hostIdOne = host2,
                                            hostIdTwo = host1 )
        intentsId.append( intent2 )
        # Checking intents state before pinging
        main.log.step( "Checking intents state" )
        time.sleep( 10 )
        intentResult = main.ONOScli1.checkIntentState( intentsId = intentsId )
        utilities.assert_equals( expect=main.TRUE, actual=intentResult,
                                 onpass="All intents are in INSTALLED state ",
                                 onfail="Some of the intents are not in " +
                                        "INSTALLED state " )

        # pinging h1 to h2 and then ping h2 to h1
        main.log.step( "Pinging h1 and h2" )
        pingResult = main.TRUE
        pingResult = main.LincOE2.pingHostOptical( src="h1", target="h2" )
        pingResult = pingResult and main.LincOE2.pingHostOptical( src="h2",
                                                                  target="h1" )

        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="Pinged successfully between h1 and h2",
                                 onfail="Pinged failed between h1 and h2" )

        case25Result = pingResult
        utilities.assert_equals( expect=main.TRUE, actual=case25Result,
                                 onpass="Add host intent successful",
                                 onfail="Add host intent failed" )
