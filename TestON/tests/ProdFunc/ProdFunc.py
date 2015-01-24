
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

        main.step( "Git checkout and pull master and get version" )
        main.ONOSbench.gitCheckout( "master" )
        gitPullResult = main.ONOSbench.gitPull()
        main.log.info( "git_pull_result = " + gitPullResult )
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

        main.step( "Installing ONOS package" )
        onosInstallResult = main.ONOSbench.onosInstall()
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

    def CASE11( self, main ):
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
        cellName = main.params[ 'ENV' ][ 'cellName' ]
        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]

        main.log.report( "This testcase exits the mininet cli and reinstalls" +
                         "ONOS to switch over to Packet Optical topology" )
        main.log.report( "_____________________________________________" )
        main.case( "Disconnecting mininet and restarting ONOS" )
        main.step( "Disconnecting mininet and restarting ONOS" )
        mininetDisconnect = main.Mininet1.disconnect()

        main.step( "Removing raft logs before a clen installation of ONOS" )
        main.ONOSbench.onosRemoveRaftLogs()

        main.step( "Applying cell variable to environment" )
        cellResult = main.ONOSbench.setCell( cellName )
        verifyResult = main.ONOSbench.verifyCell()

        onosInstallResult = main.ONOSbench.onosInstall()
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
        case20Result = mininetDisconnect and cellResult and verifyResult \
            and onosInstallResult and onos1Isup and \
            startResult
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
             ./~/ONOS/tools/test/bin/onos-topo-cfg
            which starts the rest and copies the links
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
        startConsoleResult = main.LincOE1.startConsole()
        opticalMnScript = main.LincOE2.runOpticalMnScript()
        onosTopoCfgResult = main.ONOSbench.runOnosTopoCfg(
            instanceName=main.params[ 'CTRL' ][ 'ip1' ],
            jsonFile=main.params[ 'OPTICAL' ][ 'jsonfile' ] )

        print "start_console_result =", startConsoleResult
        print "optical_mn_script = ", opticalMnScript
        print "onos_topo_cfg_result =", onosTopoCfgResult

        case21Result = startConsoleResult and opticalMnScript and \
            onosTopoCfgResult
        utilities.assert_equals(
            expect=main.TRUE,
            actual=case21Result,
            onpass="Packet optical topology spawned successsfully",
            onfail="Packet optical topology spawning failed" )

    def CASE22( self, main ):
        """
            Curretly we use, 4 linear switch optical topology and
            2 packet layer mininet switches each with one host.
            Therefore, the roadmCount variable = 4,
            packetLayerSWCount variable = 2 and hostCount = 2
            and this is hardcoded in the testcase. If the topology changes,
            these hardcoded values need to be changed
        """
        main.log.report(
            "This testcase compares the optical+packet topology against what" +
            " is expected" )
        main.case( "Topology comparision" )
        main.step( "Topology comparision" )
        main.ONOS3.startOnosCli( ONOSIp=main.params[ 'CTRL' ][ 'ip1' ] )
        devicesResult = main.ONOS3.devices( jsonFormat=False )

        print "devices_result = ", devicesResult
        devicesLinewise = devicesResult.split( "\n" )
        devicesLinewise = devicesLinewise[ 1:-1 ]
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
        if roadmCount == 4:
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

        if packetLayerSWCount == 2:
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

        linksResult = main.ONOS3.links( jsonFormat=False )
        print "links_result = ", linksResult
        print "_________________________________"

        # NOTE:Since only point intents are added, there is no
        # requirement to discover the hosts
        # Therfore, the below portion of the code is commented.
        """
        #Discover hosts using pingall
        pingallResult = main.LincOE2.pingall()

        hostsResult = main.ONOS3.hosts( jsonFormat=False )
        main.log.info( "hosts_result = "+hostsResult )
        main.log.info( "_________________________________" )
        hostsLinewise = hostsResult.split( "\n" )
        hostsLinewise = hostsLinewise[ 1:-1 ]
        hostCount = 0
        for line in hostsLinewise:
            hostid = line.split( "," )[ 0 ].split( "=" )[ 1 ]
            hostCount +=1
        if hostCount ==2:
            print "Number of hosts = %d and is correctly detected" %hostCount
            main.log.info( "Number of hosts = " + str( hostCount ) +" and \
                            is correctly detected" )
            hostDiscovery = main.TRUE
        else:
            print "Number of hosts = %d and is wrong" %hostCount
            main.log.info( "Number of hosts = " + str( hostCount ) +" and \
                            is wrong" )
            hostDiscovery = main.FALSE
        """
        case22Result = opticalSWResult and packetSWResult
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
        ptpIntentResult = main.ONOS3.addPointIntent(
            "of:0000ffffffff0001/1",
            "of:0000ffffffff0002/1" )
        if ptpIntentResult == main.TRUE:
            main.ONOS3.intents( jsonFormat=False )
            main.log.info( "Point to point intent install successful" )

        ptpIntentResult = main.ONOS3.addPointIntent(
            "of:0000ffffffff0002/1",
            "of:0000ffffffff0001/1" )
        if ptpIntentResult == main.TRUE:
            main.ONOS3.intents( jsonFormat=False )
            main.log.info( "Point to point intent install successful" )

        time.sleep( 10 )
        flowHandle = main.ONOS3.flows()
        main.log.info( "flows :" + flowHandle )

        # Sleep for 30 seconds to provide time for the intent state to change
        time.sleep( 30 )
        intentHandle = main.ONOS3.intents( jsonFormat=False )
        main.log.info( "intents :" + intentHandle )

        PingResult = main.TRUE
        count = 1
        main.log.info( "\n\nh1 is Pinging h2" )
        ping = main.LincOE2.pingHostOptical( src="h1", target="h2" )
        # ping = main.LincOE2.pinghost()
        if ping == main.FALSE and count < 5:
            count += 1
            PingResult = main.FALSE
            main.log.info(
                "Ping between h1 and h2  failed. Making attempt number " +
                str( count ) +
                " in 2 seconds" )
            time.sleep( 2 )
        elif ping == main.FALSE:
            main.log.info( "All ping attempts between h1 and h2 have failed" )
            PingResult = main.FALSE
        elif ping == main.TRUE:
            main.log.info( "Ping test between h1 and h2 passed!" )
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
            Test Rerouting of Packet Optical by bringing a port down
            ( port 22 ) of a switch( switchID=1 ), so that link
            ( between switch1 port22 - switch4-port30 ) is inactive
            and do a ping test. If rerouting is successful,
            ping should pass. also check the flows
        """
        main.log.report(
            "This testcase tests rerouting and pings mininet hosts" )
        main.case( "Test rerouting and pings mininet hosts" )
        main.step( "Bring a port down and verify the link state" )
        main.LincOE1.portDown( swId="1", ptId="22" )
        linksNonjson = main.ONOS3.links( jsonFormat=False )
        main.log.info( "links = " + linksNonjson )

        links = main.ONOS3.links()
        main.log.info( "links = " + links )

        linksResult = json.loads( links )
        linksStateResult = main.FALSE
        for item in linksResult:
            if item[ 'src' ][ 'device' ] == "of:0000ffffffffff01" and item[
                    'src' ][ 'port' ] == "22":
                if item[ 'dst' ][ 'device' ] == "of:0000ffffffffff04" and item[
                        'dst' ][ 'port' ] == "30":
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
        flowHandle = main.ONOS3.flows()
        main.log.info( "flows :" + flowHandle )

        main.step( "Verify Rerouting by a ping test" )
        PingResult = main.TRUE
        count = 1
        main.log.info( "\n\nh1 is Pinging h2" )
        ping = main.LincOE2.pingHostOptical( src="h1", target="h2" )
        # ping = main.LincOE2.pinghost()
        if ping == main.FALSE and count < 5:
            count += 1
            PingResult = main.FALSE
            main.log.info(
                "Ping between h1 and h2  failed. Making attempt number " +
                str( count ) +
                " in 2 seconds" )
            time.sleep( 2 )
        elif ping == main.FALSE:
            main.log.info( "All ping attempts between h1 and h2 have failed" )
            PingResult = main.FALSE
        elif ping == main.TRUE:
            main.log.info( "Ping test between h1 and h2 passed!" )
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

    def CASE4( self, main ):
        import re
        import time
        main.log.report( "This testcase is testing the assignment of" +
                         " all the switches to all the controllers and" +
                         " discovering the hists in reactive mode" )
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

        main.step( "Get list of hosts from Mininet" )
        hostList = main.Mininet1.getHosts()
        main.log.info( hostList )

        main.step( "Get host list in ONOS format" )
        hostOnosList = main.ONOS2.getHostsId( hostList )
        main.log.info( hostOnosList )
        # time.sleep( 5 )

        main.step( "Pingall" )
        pingResult = main.FALSE
        while pingResult == main.FALSE:
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

    def CASE10( self ):
        main.log.report(
            "This testcase uninstalls the reactive forwarding app" )
        main.log.report( "__________________________________" )
        main.case( "Uninstalling reactive forwarding app" )
        # Unistall onos-app-fwd app to disable reactive forwarding
        appUninstallResult = main.ONOS2.featureUninstall( "onos-app-fwd" )
        main.log.info( "onos-app-fwd uninstalled" )

        # After reactive forwarding is disabled, the reactive flows on
        # switches timeout in 10-15s
        # So sleep for 15s
        time.sleep( 15 )

        flows = main.ONOS2.flows()
        main.log.info( flows )

        case10Result = appUninstallResult
        utilities.assert_equals(
            expect=main.TRUE,
            actual=case10Result,
            onpass="Reactive forwarding app uninstallation successful",
            onfail="Reactive forwarding app uninstallation failed" )

    def CASE6( self ):
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
        for i in range( 8, 18 ):
            main.log.info(
                "Adding host intent between h" + str( i ) +
                " and h" + str( i + 10 ) )
            host1 = "00:00:00:00:00:" + \
                str( hex( i )[ 2: ] ).zfill( 2 ).upper()
            host2 = "00:00:00:00:00:" + \
                str( hex( i + 10 )[ 2: ] ).zfill( 2 ).upper()
            # NOTE: get host can return None
            # TODO: handle this
            host1Id = main.ONOS2.getHost( host1 )[ 'id' ]
            host2Id = main.ONOS2.getHost( host2 )[ 'id' ]
            main.ONOS2.addHostIntent( host1Id, host2Id )

        time.sleep( 10 )
        hIntents = main.ONOS2.intents( jsonFormat=False )
        main.log.info( "intents:" + hIntents )
        main.ONOS2.flows()

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

        case6Result = PingResult
        utilities.assert_equals(
            expect=main.TRUE,
            actual=case6Result,
            onpass="Pingall Test after Host intents addition successful",
            onfail="Pingall Test after Host intents addition failed" )

    def CASE5( self, main ):
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
        # portsJson = main.ONOS2.ports()

        result1 = main.Mininet1.compareSwitches(
            MNTopo,
            json.loads( devicesJson ) )
        result2 = main.Mininet1.compareLinks(
            MNTopo,
            json.loads( linksJson ) )
        # result3 = main.Mininet1.comparePorts(
        # MNTopo, json.loads( portsJson ) )

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
        # result3 = main.Mininet1.comparePorts(
        # MNTopo, json.loads( portsJson ) )

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
        Host intents removal
        """
        main.log.report( "This testcase removes any previously added intents" +
                         " before adding the same intents or point intents" )
        main.log.report( "__________________________________" )
        main.log.info( "Host intents removal" )
        main.case( "Removing host intents" )
        main.step( "Obtain the intent id's" )
        intentResult = main.ONOS2.intents( jsonFormat=False )
        main.log.info( "intent_result = " + intentResult )

        intentLinewise = intentResult.split( "\n" )
        intentList = []
        for line in intentLinewise:
            if line.startswith( "id=" ):
                intentList.append( line )

        intentids = []
        for line in intentList:
            intentids.append( line.split( "," )[ 0 ].split( "=" )[ 1 ] )
        for id in intentids:
            print "id = ", id

        main.step(
            "Iterate through the intentids list and remove each intent" )
        for id in intentids:
            main.ONOS2.removeIntent( intentId=id )

        intentResult = main.ONOS2.intents( jsonFormat=False )
        main.log.info( "intent_result = " + intentResult )

        case8Result = main.TRUE
        if case8Result == main.TRUE:
            main.log.report( "Intent removal successful" )
        else:
            main.log.report( "Intent removal failed" )

        PingResult = main.TRUE
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
            main.log.report( "Host intents have not been withdrawn correctly" )
            # main.cleanup()
            # main.exit()
        if PingResult == main.FALSE:
            main.log.report( "Host intents have been withdrawn correctly" )

        case8Result = case8Result and PingResult

        if case8Result == main.FALSE:
            main.log.report( "Intent removal successful" )
        else:
            main.log.report( "Intent removal failed" )

        utilities.assert_equals( expect=main.FALSE, actual=case8Result,
                                 onpass="Intent removal test passed",
                                 onfail="Intent removal test failed" )

    def CASE9( self ):
        main.log.report(
            "This testcase adds point intents and then does pingall" )
        main.log.report( "__________________________________" )
        main.log.info( "Adding point intents" )
        main.case(
            '''Adding bidirectional point for mn hosts
            ( h8-h18, h9-h19, h10-h20, h11-h21, h12-h22,
                h13-h23, h14-h24, h15-h25, h16-h26, h17-h27 )''' )

        main.step( "Add point intents for mn hosts h8 and h18 or" +
                   "ONOS hosts h8 and h12" )
        # main.step(var1)
        ptpIntentResult = main.ONOS2.addPointIntent(
            "of:0000000000003008/1",
            "of:0000000000006018/1" )
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOS2.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOS2.addPointIntent(
            "of:0000000000006018/1",
            "of:0000000000003008/1" )
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOS2.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        var2 = "Add point intents for mn hosts h9&h19 or ONOS hosts h9&h13"
        main.step(var2)
        ptpIntentResult = main.ONOS2.addPointIntent(
            "of:0000000000003009/1",
            "of:0000000000006019/1" )
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOS2.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOS2.addPointIntent(
            "of:0000000000006019/1",
            "of:0000000000003009/1" )
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOS2.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        var3 = "Add point intents for MN hosts h10&h20 or ONOS hosts hA&h14"
        main.step(var3)
        ptpIntentResult = main.ONOS2.addPointIntent(
            "of:0000000000003010/1",
            "of:0000000000006020/1" )
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOS2.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOS2.addPointIntent(
            "of:0000000000006020/1",
            "of:0000000000003010/1" )
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOS2.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        var4 = "Add point intents for mininet hosts h11 and h21 or" +\
               " ONOS hosts hB and h15"
        main.case(var4)
        ptpIntentResult = main.ONOS2.addPointIntent(
            "of:0000000000003011/1",
            "of:0000000000006021/1" )
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOS2.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOS2.addPointIntent(
            "of:0000000000006021/1",
            "of:0000000000003011/1" )
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOS2.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        var5 = "Add point intents for mininet hosts h12 and h22 " +\
               "ONOS hosts hC and h16"
        main.case(var5)
        ptpIntentResult = main.ONOS2.addPointIntent(
            "of:0000000000003012/1",
            "of:0000000000006022/1" )
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOS2.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOS2.addPointIntent(
            "of:0000000000006022/1",
            "of:0000000000003012/1" )
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOS2.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        var6 = "Add point intents for mininet hosts h13 and h23 or" +\
               " ONOS hosts hD and h17"
        main.case(var6)
        ptpIntentResult = main.ONOS2.addPointIntent(
            "of:0000000000003013/1",
            "of:0000000000006023/1" )
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOS2.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOS2.addPointIntent(
            "of:0000000000006023/1",
            "of:0000000000003013/1" )
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOS2.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        var7 = "Add point intents for mininet hosts h14 and h24 or" +\
               " ONOS hosts hE and h18"
        main.case(var7)
        ptpIntentResult = main.ONOS2.addPointIntent(
            "of:0000000000003014/1",
            "of:0000000000006024/1" )
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOS2.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOS2.addPointIntent(
            "of:0000000000006024/1",
            "of:0000000000003014/1" )
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOS2.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        var8 = "Add point intents for mininet hosts h15 and h25 or" +\
               " ONOS hosts hF and h19"
        main.case(var8)
        ptpIntentResult = main.ONOS2.addPointIntent(
            "of:0000000000003015/1",
            "of:0000000000006025/1" )
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOS2.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOS2.addPointIntent(
            "of:0000000000006025/1",
            "of:0000000000003015/1" )
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOS2.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        var9 = "Add intents for mininet hosts h16 and h26 or" +\
               " ONOS hosts h10 and h1A"
        main.case(var9)
        ptpIntentResult = main.ONOS2.addPointIntent(
            "of:0000000000003016/1",
            "of:0000000000006026/1" )
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOS2.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOS2.addPointIntent(
            "of:0000000000006026/1",
            "of:0000000000003016/1" )
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOS2.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        var10 = "Add point intents for mininet hosts h17 and h27 or" +\
                " ONOS hosts h11 and h1B"
        main.case(var10)
        ptpIntentResult = main.ONOS2.addPointIntent(
            "of:0000000000003017/1",
            "of:0000000000006027/1" )
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOS2.intents()
            main.log.info( "Point to point intent install successful" )
            main.log.info( getIntentResult )

        ptpIntentResult = main.ONOS2.addPointIntent(
            "of:0000000000006027/1",
            "of:0000000000003017/1" )
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOS2.intents()
            main.log.info( "Point to point intent install successful" )
            main.log.info( getIntentResult )

        print(
            "___________________________________________________________" )

        flowHandle = main.ONOS2.flows()
        # print "flowHandle = ", flowHandle
        main.log.info( "flows :" + flowHandle )

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
