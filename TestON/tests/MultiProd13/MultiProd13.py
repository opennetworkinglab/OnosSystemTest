
# Testing the basic functionality of ONOS Next
# For sanity and driver functionality excercises only.

import time
import sys
import os
import re
import time
import json

time.sleep( 1 )

class MultiProd13:

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
        gitPull = main.params[ 'GIT' ][ 'pull' ]

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

        main.step( "Git checkout and get version" )
        main.ONOSbench.gitCheckout( "master" )
        if gitPull == 'True':
            gitPullResult = main.ONOSbench.gitPull()
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
            main.log.info( "git_pull_result = " + str( gitPullResult ))
        else:
            main.log.info( "Skipping git pull" )
        main.ONOSbench.getVersion( report=True )
        packageResult = main.TRUE

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

        # Starting the mininet using the old way
        main.step( "Starting Mininet ..." )
        netIsUp = main.Mininet1.startNet()
        if netIsUp:
            main.log.info("Mininet CLI is up")

        case1Result = ( packageResult and
                        cellResult and verifyResult and onosInstallResult and
                        onosIsup and startResult )
        utilities.assertEquals( expect=main.TRUE, actual=case1Result,
                                onpass="Test startup successful",
                                onfail="Test startup NOT successful" )

    def CASE11( self, main ):
        """
        Cleanup sequence:
        onos-service <nodeIp> stop
        onos-uninstall

        TODO: Define rest of cleanup

        """
        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]
        ONOS2Ip = main.params[ 'CTRL' ][ 'ip2' ]
        ONOS3Ip = main.params[ 'CTRL' ][ 'ip3' ]

        main.case( "Cleaning up test environment" )

        main.step( "Testing ONOS kill function" )
        killResult1 = main.ONOSbench.onosKill( ONOS1Ip )
        killResult2 = main.ONOSbench.onosKill( ONOS2Ip )
        killResult3 = main.ONOSbench.onosKill( ONOS3Ip )

        main.step( "Stopping ONOS service" )
        stopResult1 = main.ONOSbench.onosStop( ONOS1Ip )
        stopResult2 = main.ONOSbench.onosStop( ONOS2Ip )
        stopResult3 = main.ONOSbench.onosStop( ONOS3Ip )

        main.step( "Uninstalling ONOS service" )
        uninstallResult = main.ONOSbench.onosUninstall()

    def CASE3( self, main ):
        """
        Test 'onos' command and its functionality in driver
        """
        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]
        ONOS2Ip = main.params[ 'CTRL' ][ 'ip2' ]
        ONOS3Ip = main.params[ 'CTRL' ][ 'ip3' ]

        main.case( "Testing 'onos' command" )

        main.step( "Sending command 'onos -w <onos-ip> system:name'" )
        cmdstr1 = "system:name"
        cmdResult1 = main.ONOSbench.onosCli( ONOS1Ip, cmdstr1 )
        main.log.info( "onos command returned: " + cmdResult1 )
        cmdResult2 = main.ONOSbench.onosCli( ONOS2Ip, cmdstr1 )
        main.log.info( "onos command returned: " + cmdResult2 )
        cmdResult3 = main.ONOSbench.onosCli( ONOS3Ip, cmdstr1 )
        main.log.info( "onos command returned: " + cmdResult3 )

        main.step( "Sending command 'onos -w <onos-ip> onos:topology'" )
        cmdstr2 = "onos:topology"
        cmdResult4 = main.ONOSbench.onosCli( ONOS1Ip, cmdstr2 )
        main.log.info( "onos command returned: " + cmdResult4 )
        cmdResult5 = main.ONOSbench.onosCli( ONOS2Ip, cmdstr2 )
        main.log.info( "onos command returned: " + cmdResult5 )
        cmdResult6 = main.ONOSbench.onosCli( ONOS6Ip, cmdstr2 )
        main.log.info( "onos command returned: " + cmdResult6 )

    def CASE4( self, main ):
        import re
        import time
        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]
        ONOS2Ip = main.params[ 'CTRL' ][ 'ip2' ]
        ONOS3Ip = main.params[ 'CTRL' ][ 'ip3' ]
        ONOS1Port = main.params[ 'CTRL' ][ 'port1' ]
        ONOS2Port = main.params[ 'CTRL' ][ 'port2' ]
        ONOS3Port = main.params[ 'CTRL' ][ 'port3' ]

        main.log.report(
            "This testcase is testing the assignment of all the switches" +
            " to all controllers and discovering the hosts in reactive mode" )
        main.log.report( "__________________________________" )
        main.case( "Pingall Test(No intents are added)" )
        main.step( "Assigning switches to controllers" )
        for i in range( 1, 29 ):  # 1 to ( num of switches +1 )
            main.Mininet1.assignSwController(
                sw=str( i ),
                count=3,
                ip1=ONOS1Ip,
                port1=ONOS1Port,
                ip2=ONOS2Ip,
                port2=ONOS2Port,
                ip3=ONOS3Ip,
                port3=ONOS3Port )

        switchMastership = main.TRUE
        for i in range( 1, 29 ):
            response = main.Mininet1.getSwController( "s" + str( i ) )
            print( "Response is " + str( response ) )
            if re.search( "tcp:" + ONOS1Ip, response ):
                switchMastership = switchMastership and main.TRUE
            else:
                switchMastership = main.FALSE

        if switchMastership == main.TRUE:
            main.log.report( "Controller assignment successfull" )
        else:
            main.log.report( "Controller assignment failed" )
        appInstallResult = main.TRUE
        main.log.info( "Activating reactive forwarding app" )
        appInstallResult = main.ONOScli1.activateApp( "org.onosproject.fwd" )
        appCheck = main.ONOScli1.appToIDCheck()
        if appCheck != main.TRUE:
            main.log.warn( main.ONOScli1.apps() )
            main.log.warn( main.ONOScli1.appIDs() )
        time.sleep( 30 )
        # REACTIVE FWD test
        main.step( "Pingall" )
        pingResult = main.FALSE
        time1 = time.time()
        pingResult = main.Mininet1.pingall()
        time2 = time.time()
        print "Time for pingall: %2f seconds" % ( time2 - time1 )

        case4Result = switchMastership and pingResult
        if pingResult == main.TRUE:
            main.log.report(
                "Pingall Test in reactive mode to" +
                " discover the hosts successful" )
        else:
            main.log.report(
                "Pingall Test in reactive mode to discover the hosts failed" )

        utilities.assertEquals(
            expect=main.TRUE,
            actual=case4Result,
            onpass="Controller assignment and Pingall Test successful",
            onfail="Controller assignment and Pingall Test NOT successful" )

    def CASE5( self, main ):
        import json
        from subprocess import Popen, PIPE
        # assumes that sts is already in you PYTHONPATH
        from sts.topology.teston_topology import TestONTopology
        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]
        ONOS2Ip = main.params[ 'CTRL' ][ 'ip2' ]
        ONOS3Ip = main.params[ 'CTRL' ][ 'ip3' ]

        main.log.report(
            "This testcase is testing if all ONOS nodes are in topology" +
            " sync with mininet and its peer ONOS nodes" )
        main.log.report( "__________________________________" )
        main.case(
            "Testing Mininet topology with the" +
            " topology of multi instances ONOS" )
        main.step( "Collecting topology information from ONOS" )
        devices1 = main.ONOScli1.devices()
        devices2 = main.ONOScli2.devices()
        devices3 = main.ONOScli3.devices()
        # print "devices1 = ", devices1
        # print "devices2 = ", devices2
        # print "devices3 = ", devices3
        hosts1 = main.ONOScli1.hosts()
        hosts2 = main.ONOScli2.hosts()
        hosts3 = main.ONOScli3.hosts()
        # print "hosts1 = ", hosts1
        # print "hosts2 = ", hosts2
        # print "hosts3 = ", hosts3
        ports1 = main.ONOScli1.ports()
        ports2 = main.ONOScli2.ports()
        ports3 = main.ONOScli3.ports()
        # print "ports1 = ", ports1
        # print "ports2 = ", ports2
        # print "ports3 = ", ports3
        links1 = main.ONOScli1.links()
        links2 = main.ONOScli2.links()
        links3 = main.ONOScli3.links()
        # print "links1 = ", links1
        # print "links2 = ", links2
        # print "links3 = ", links3

        print "**************"

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

        switchesResults1 = main.Mininet1.compareSwitches(
            MNTopo,
            json.loads( devices1 ) )
        print "switches_Result1 = ", switchesResults1
        utilities.assertEquals( expect=main.TRUE, actual=switchesResults1,
                                onpass="ONOS1 Switches view is correct",
                                onfail="ONOS1 Switches view is incorrect" )

        switchesResults2 = main.Mininet1.compareSwitches(
            MNTopo,
            json.loads( devices2 ) )
        utilities.assertEquals( expect=main.TRUE, actual=switchesResults2,
                                onpass="ONOS2 Switches view is correct",
                                onfail="ONOS2 Switches view is incorrect" )

        switchesResults3 = main.Mininet1.compareSwitches(
            MNTopo,
            json.loads( devices3 ) )
        utilities.assertEquals( expect=main.TRUE, actual=switchesResults3,
                                onpass="ONOS3 Switches view is correct",
                                onfail="ONOS3 Switches view is incorrect" )

        portsResults1 =  main.Mininet1.comparePorts( MNTopo,
        json.loads( ports1 ) )
        utilities.assertEquals( expect=main.TRUE, actual=portsResults1,
                onpass="ONOS1 Ports view is correct",
                onfail="ONOS1 Ports view is incorrect" )

        portsResults2 =  main.Mininet1.comparePorts( MNTopo,
        json.loads( ports2 ) )
        utilities.assertEquals( expect=main.TRUE, actual=portsResults2,
                onpass="ONOS2 Ports view is correct",
                onfail="ONOS2 Ports view is incorrect" )

        portsResults3 =  main.Mininet1.comparePorts( MNTopo,
        json.loads( ports3 ) )
        utilities.assertEquals( expect=main.TRUE, actual=portsResults3,
                onpass="ONOS3 Ports view is correct",
                onfail="ONOS3 Ports view is incorrect" )

        linksResults1 = main.Mininet1.compareLinks(
            MNTopo,
            json.loads( links1 ) )
        utilities.assertEquals( expect=main.TRUE, actual=linksResults1,
                                onpass="ONOS1 Links view is correct",
                                onfail="ONOS1 Links view is incorrect" )

        linksResults2 = main.Mininet1.compareLinks(
            MNTopo,
            json.loads( links2 ) )
        utilities.assertEquals( expect=main.TRUE, actual=linksResults2,
                                onpass="ONOS2 Links view is correct",
                                onfail="ONOS2 Links view is incorrect" )

        linksResults3 = main.Mininet1.compareLinks(
            MNTopo,
            json.loads( links3 ) )
        utilities.assertEquals( expect=main.TRUE, actual=linksResults3,
                                onpass="ONOS2 Links view is correct",
                                onfail="ONOS2 Links view is incorrect" )

        # topoResult = switchesResults1 and switchesResults2
        # and switchesResults3\
        # and portsResults1 and portsResults2 and portsResults3\
        # and linksResults1 and linksResults2 and linksResults3

        topoResult = switchesResults1 and switchesResults2 and\
                     switchesResults3 and linksResults1 and linksResults2 and\
                     linksResults3

        if topoResult == main.TRUE:
            main.log.report(
                "Topology Check Test with mininet" +
                "and ONOS instances successful" )
        else:
            main.log.report(
                "Topology Check Test with mininet and ONOS instances failed" )

        utilities.assertEquals( expect=main.TRUE, actual=topoResult,
                                onpass="Topology Check Test successful",
                                onfail="Topology Check Test NOT successful" )

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

    def CASE6( self ):
        main.log.report(
            "This testcase is testing the addition of" +
            " host intents and then doing pingall" )
        main.log.report( "__________________________________" )
        main.case( "Obtaining hostsfor adding host intents" )
        main.step( "Get hosts" )
        hosts = main.ONOScli1.hosts()
        main.log.info( hosts )

        main.step( "Get all devices id" )
        devicesIdList = main.ONOScli1.getAllDevicesId()
        main.log.info( devicesIdList )

        # ONOS displays the hosts in hex format
        # unlike mininet which does in decimal format
        # So take care while adding intents

        """
        main.step( "Add host intents for mn hosts(h8-h18,h9-h19,h10-h20,
        h11-h21,h12-h22,h13-h23,h14-h24,h15-h25,h16-h26,h17-h27)" )
        hthIntentResult = main.ONOScli1.addHostIntent( "00:00:00:00:00:08/-1",
        "00:00:00:00:00:12/-1" )
        hthIntentResult = main.ONOScli1.addHostIntent( "00:00:00:00:00:09/-1",
        "00:00:00:00:00:13/-1" )
        hthIntentResult = main.ONOScli1.addHostIntent( "00:00:00:00:00:0A/-1",
        "00:00:00:00:00:14/-1" )
        hthIntentResult = main.ONOScli1.addHostIntent( "00:00:00:00:00:0B/-1",
        "00:00:00:00:00:15/-1" )
        hthIntentResult = main.ONOScli1.addHostIntent( "00:00:00:00:00:0C/-1",
        "00:00:00:00:00:16/-1" )
        hthIntentResult = main.ONOScli1.addHostIntent( "00:00:00:00:00:0D/-1",
        "00:00:00:00:00:17/-1" )
        hthIntentResult = main.ONOScli1.addHostIntent( "00:00:00:00:00:0E/-1",
        "00:00:00:00:00:18/-1" )
        hthIntentResult = main.ONOScli1.addHostIntent( "00:00:00:00:00:0F/-1",
        "00:00:00:00:00:19/-1" )
        hthIntentResult = main.ONOScli1.addHostIntent( "00:00:00:00:00:10/-1",
        "00:00:00:00:00:1A/-1" )
        hthIntentResult = main.ONOScli1.addHostIntent( "00:00:00:00:00:11/-1",
        "00:00:00:00:00:1B/-1" )
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
            # TODO: handle this
            host1Id = main.ONOScli1.getHost( host1 )[ 'id' ]
            host2Id = main.ONOScli1.getHost( host2 )[ 'id' ]
            tmpResult = main.ONOScli1.addHostIntent( host1Id, host2Id )
            intentsId.append( tmpResult )

        checkIntent1 = main.ONOScli1.checkIntentState( intentsId )
        checkIntent2 = main.ONOScli2.checkIntentState( intentsId )
        checkIntent3 = main.ONOScli3.checkIntentState( intentsId )

        flowHandle = main.ONOScli1.flows()

        main.log.info( "flows:" + flowHandle )

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
                "Host intents have not ben installed correctly. Cleaning up" )
            # main.cleanup()
            # main.exit()
        if PingResult == main.TRUE:
            main.log.report( "Host intents have been installed correctly" )

        checkIntent1 = main.ONOScli1.checkIntentState( intentsId )
        checkIntent2 = main.ONOScli2.checkIntentState( intentsId )
        checkIntent3 = main.ONOScli3.checkIntentState( intentsId )

        case6Result = PingResult
        utilities.assertEquals(
            expect=main.TRUE,
            actual=case6Result,
            onpass="Host intent addition and Pingall Test successful",
            onfail="Host intent addition and Pingall Test NOT successful" )

    def CASE7( self, main ):

        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]

        linkSleep = int( main.params[ 'timers' ][ 'LinkDiscovery' ] )

        main.log.report(
            "This testscase is killing a link to" +
            " ensure that link discovery is consistent" )
        main.log.report( "__________________________________" )
        main.case(
            "Killing a link to Ensure that Link" +
            " Discovery is Working Properly" )
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

        main.step( "Determine the current number of switches and links" )
        topologyOutput = main.ONOScli1.topology()
        topologyResult = main.ONOSbench.getTopology( topologyOutput )
        activeSwitches = topologyResult[ 'devices' ]
        links = topologyResult[ 'links' ]
        main.log.info(
            "Currently there are %s switches and %s links" %
            ( str( activeSwitches ), str( links ) ) )

        main.step( "Kill Link between s3 and s28" )
        main.Mininet1.link( END1="s3", END2="s28", OPTION="down" )
        time.sleep( linkSleep )
        topologyOutput = main.ONOScli2.topology()
        LinkDown = main.ONOSbench.checkStatus(
            topologyOutput, activeSwitches, str(
                int( links ) - 2 ) )
        if LinkDown == main.TRUE:
            main.log.report( "Link Down discovered properly" )
        utilities.assertEquals(
            expect=main.TRUE,
            actual=LinkDown,
            onpass="Link Down discovered properly",
            onfail="Link down was not discovered in " +
            str( linkSleep ) +
            " seconds" )

        main.step( "Bring link between s3 and s28 back up" )
        LinkUp = main.Mininet1.link( END1="s3", END2="s28", OPTION="up" )
        time.sleep( linkSleep )
        topologyOutput = main.ONOScli2.topology()
        LinkUp = main.ONOSbench.checkStatus(
            topologyOutput,
            activeSwitches,
            str( links ) )
        if LinkUp == main.TRUE:
            main.log.report( "Link up discovered properly" )
        utilities.assertEquals(
            expect=main.TRUE,
            actual=LinkUp,
            onpass="Link up discovered properly",
            onfail="Link up was not discovered in " +
            str( linkSleep ) +
            " seconds" )

        main.step( "Compare ONOS Topology to MN Topology" )
        main.case(
            "Testing Mininet topology with the" +
            " topology of multi instances ONOS" )
        main.step( "Collecting topology information from ONOS" )
        devices1 = main.ONOScli1.devices()
        devices2 = main.ONOScli2.devices()
        devices3 = main.ONOScli3.devices()
        print "devices1 = ", devices1
        print "devices2 = ", devices2
        print "devices3 = ", devices3
        hosts1 = main.ONOScli1.hosts()
        hosts2 = main.ONOScli2.hosts()
        hosts3 = main.ONOScli3.hosts()
        # print "hosts1 = ", hosts1
        # print "hosts2 = ", hosts2
        # print "hosts3 = ", hosts3
        ports1 = main.ONOScli1.ports()
        ports2 = main.ONOScli2.ports()
        ports3 = main.ONOScli3.ports()
        # print "ports1 = ", ports1
        # print "ports2 = ", ports2
        # print "ports3 = ", ports3
        links1 = main.ONOScli1.links()
        links2 = main.ONOScli2.links()
        links3 = main.ONOScli3.links()
        # print "links1 = ", links1
        # print "links2 = ", links2
        # print "links3 = ", links3

        print "**************"

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

        switchesResults1 = main.Mininet1.compareSwitches(
            MNTopo,
            json.loads( devices1 ) )
        print "switches_Result1 = ", switchesResults1
        utilities.assertEquals( expect=main.TRUE, actual=switchesResults1,
                                onpass="ONOS1 Switches view is correct",
                                onfail="ONOS1 Switches view is incorrect" )

        switchesResults2 = main.Mininet1.compareSwitches(
            MNTopo,
            json.loads( devices2 ) )
        utilities.assertEquals( expect=main.TRUE, actual=switchesResults2,
                                onpass="ONOS2 Switches view is correct",
                                onfail="ONOS2 Switches view is incorrect" )

        switchesResults3 = main.Mininet1.compareSwitches(
            MNTopo,
            json.loads( devices3 ) )
        utilities.assertEquals( expect=main.TRUE, actual=switchesResults3,
                                onpass="ONOS3 Switches view is correct",
                                onfail="ONOS3 Switches view is incorrect" )

        """
        portsResults1 =  main.Mininet1.comparePorts( MNTopo,
        json.loads( ports1 ) )
        utilities.assertEquals( expect=main.TRUE, actual=portsResults1,
                onpass="ONOS1 Ports view is correct",
                onfail="ONOS1 Ports view is incorrect" )

        portsResults2 =  main.Mininet1.comparePorts( MNTopo,
        json.loads( ports2 ) )
        utilities.assertEquals( expect=main.TRUE, actual=portsResults2,
                onpass="ONOS2 Ports view is correct",
                onfail="ONOS2 Ports view is incorrect" )

        portsResults3 =  main.Mininet1.comparePorts( MNTopo,
        json.loads( ports3 ) )
        utilities.assertEquals( expect=main.TRUE, actual=portsResults3,
                onpass="ONOS3 Ports view is correct",
                onfail="ONOS3 Ports view is incorrect" )
        """
        linksResults1 = main.Mininet1.compareLinks(
            MNTopo,
            json.loads( links1 ) )
        utilities.assertEquals( expect=main.TRUE, actual=linksResults1,
                                onpass="ONOS1 Links view is correct",
                                onfail="ONOS1 Links view is incorrect" )

        linksResults2 = main.Mininet1.compareLinks(
            MNTopo,
            json.loads( links2 ) )
        utilities.assertEquals( expect=main.TRUE, actual=linksResults2,
                                onpass="ONOS2 Links view is correct",
                                onfail="ONOS2 Links view is incorrect" )

        linksResults3 = main.Mininet1.compareLinks(
            MNTopo,
            json.loads( links3 ) )
        utilities.assertEquals( expect=main.TRUE, actual=linksResults3,
                                onpass="ONOS2 Links view is correct",
                                onfail="ONOS2 Links view is incorrect" )

        # topoResult = switchesResults1 and switchesResults2
        # and switchesResults3\
        # and portsResults1 and portsResults2 and portsResults3\
        # and linksResults1 and linksResults2 and linksResults3

        topoResult = switchesResults1 and switchesResults2\
                and switchesResults3 and linksResults1 and\
                linksResults2 and linksResults3

        utilities.assertEquals(
            expect=main.TRUE,
            actual=topoResult and LinkUp and LinkDown,
            onpass="Topology Check Test successful",
            onfail="Topology Check Test NOT successful" )

    def CASE8( self ):
        """
        Intent removal
        """
        main.log.report(
            "This testcase removes any previously added intents" )
        main.log.report( "__________________________________" )
        main.log.info( "Removing any previously installed intents" )
        main.case( "Removing intents" )
        main.step( "Obtain the intent id's" )
        intentResult = main.ONOScli1.intents( jsonFormat=False )

        intentLinewise = intentResult.split( "\n" )
        intentList = []
        for line in intentLinewise:
            if line.startswith( "id=" ):
                intentList.append( line )

        intentids = []
        for line in intentList:
            intentids.append( line.split( "," )[ 0 ].split( "=" )[ 1 ] )
        for id in intentids:
            main.log.info( "id = " + id )

        main.step(
            "Iterate through the intentids list and remove each intent" )
        for id in intentids:
            main.ONOScli1.removeIntent( intentId=id ,purge=True )

        remainingIntent = main.ONOScli1.intents( jsonFormat=False )
        main.log.info( "Remaining intents  " + remainingIntent )

        case8Result = main.TRUE
        intentResult = main.TRUE
        if remainingIntent:
            main.log.error( "There are still remaining intent" )
            intentResult = main.FALSE
        i = 8

        PingResult = main.TRUE
        """
        while i < 18:
            main.log.info(
                "\n\nh" + str( i ) + " is Pinging h" + str( i + 10 ) )
            ping = main.Mininet1.pingHost(
                src="h" + str( i ), target="h" + str( i + 10 ) )
            if ping == main.TRUE:
                i = 19
                PingResult = main.TRUE
            elif ping == main.FALSE:
                i += 1
                PingResult = main.FALSE
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
        """
        case8Result = intentResult

        if case8Result == main.TRUE:
            main.log.report( "Intent removal successful" )
        else:
            main.log.report( "Intent removal failed" )

        utilities.assertEquals( expect=main.TRUE, actual=case8Result,
                                onpass="Intent removal test successful",
                                onfail="Intent removal test failed" )

    def CASE9( self ):
        """
        This test case adds point intents. Make sure you run test case 8
        which is host intent removal before executing this test case.
        Else the host intent's flows will persist on switches and the pings
        would work even if there is some issue with the point intent's flows
        """
        main.log.report(
            "This testcase adds point intents and then does pingall" )
        main.log.report( "__________________________________" )
        main.log.info( "Adding point intents" )
        main.case(
            "Adding bidirectional point for mn hosts(h8-h18,h9-h19,h10-h20," +
            "h11-h21,h12-h22,h13-h23,h14-h24,h15-h25,h16-h26,h17-h27)" )
        main.step(
            "Add point-to-point intents for mininet hosts" +
            " h8 and h18 or ONOS hosts h8 and h12" )
        macsDict = {}
        for i in range( 1,29 ):
            macsDict[ 'h' + str( i ) ]= main.Mininet1.getMacAddress( host='h'+ str( i ) )
        print macsDict
        # main.step(var1)
        ptpIntentResult = main.ONOScli1.addPointIntent(
            ingressDevice="of:0000000000003008/1",
            egressDevice="of:0000000000006018/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h8' ))
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOScli1.addPointIntent(
            ingressDevice="of:0000000000006018/1",
            egressDevice="of:0000000000003008/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h18' ))
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        var2 = "Add point intents for mn hosts h9&h19 or ONOS hosts h9&h13"
        main.step(var2)
        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000003009/1",
            "of:0000000000006019/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h9' ))
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000006019/1",
            "of:0000000000003009/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h19' ))
        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        var3 = "Add point intents for MN hosts h10&h20 or ONOS hosts hA&h14"
        main.step(var3)
        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000003010/1",
            "of:0000000000006020/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h10' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000006020/1",
            "of:0000000000003010/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h20' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        var4 = "Add point intents for mininet hosts h11 and h21 or" +\
               " ONOS hosts hB and h15"
        main.case(var4)
        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000003011/1",
            "of:0000000000006021/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h11' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000006021/1",
            "of:0000000000003011/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h21' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        var5 = "Add point intents for mininet hosts h12 and h22 " +\
               "ONOS hosts hC and h16"
        main.case(var5)
        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000003012/1",
            "of:0000000000006022/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h12' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000006022/1",
            "of:0000000000003012/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h22' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        var6 = "Add point intents for mininet hosts h13 and h23 or" +\
               " ONOS hosts hD and h17"
        main.case(var6)
        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000003013/1",
            "of:0000000000006023/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h13' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000006023/1",
            "of:0000000000003013/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h23' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        var7 = "Add point intents for mininet hosts h14 and h24 or" +\
               " ONOS hosts hE and h18"
        main.case(var7)
        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000003014/1",
            "of:0000000000006024/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h14' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000006024/1",
            "of:0000000000003014/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h24' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        var8 = "Add point intents for mininet hosts h15 and h25 or" +\
               " ONOS hosts hF and h19"
        main.case(var8)
        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000003015/1",
            "of:0000000000006025/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h15' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000006025/1",
            "of:0000000000003015/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h25' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        var9 = "Add intents for mininet hosts h16 and h26 or" +\
               " ONOS hosts h10 and h1A"
        main.case(var9)
        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000003016/1",
            "of:0000000000006026/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h16' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000006026/1",
            "of:0000000000003016/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h26' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            # main.log.info( getIntentResult )

        var10 = "Add point intents for mininet hosts h17 and h27 or" +\
                " ONOS hosts h11 and h1B"
        main.case(var10)
        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000003017/1",
            "of:0000000000006027/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h17' ))

        if ptpIntentResult == main.TRUE:
            getIntentResult = main.ONOScli1.intents()
            main.log.info( "Point to point intent install successful" )
            #main.log.info( getIntentResult )

        ptpIntentResult = main.ONOScli1.addPointIntent(
            "of:0000000000006027/1",
            "of:0000000000003017/1",
            ethType='IPV4',
            ethSrc=macsDict.get( 'h27' ))

        print(
            "_______________________________________________________" +
            "________________________________" )

        flowHandle = main.ONOScli1.flows()
        print "flowHandle = ", flowHandle
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
                "Ping all test after Point intents" +
                " addition failed. Cleaning up" )
            # main.cleanup()
            # main.exit()
        if PingResult == main.TRUE:
            main.log.report(
                "Ping all test after Point intents addition successful" )

        case8Result = PingResult
        utilities.assertEquals(
            expect=main.TRUE,
            actual=case8Result,
            onpass="Ping all test after Point intents addition successful",
            onfail="Ping all test after Point intents addition failed" )

    def CASE31( self ):
        """
            This test case adds point intent related to
            SDN-IP matching on ICMP ( ethertype=IPV4, ipProto=1 )
        """
        import json

        main.log.report(
            "This test case adds point intent " +
            "related to SDN-IP matching on ICMP" )
        main.case(
            "Adding bidirectional point intent related" +
            " to SDN-IP matching on ICMP" )
        main.step( "Adding bidirectional point intent" )
        # add-point-intent --ipSrc=10.0.0.8/32 --ipDst=10.0.0.18/32
        # --ethType=IPV4 --ipProto=1  of:0000000000003008/1
        # of:0000000000006018/1

        hostsJson = json.loads( main.ONOScli1.hosts() )
        for i in range( 8, 11 ):
            main.log.info(
                "Adding point intent between h" + str( i ) +
                " and h" + str( i + 10 ) )
            host1 = "00:00:00:00:00:" + \
                str( hex( i )[ 2: ] ).zfill( 2 ).upper()
            host2 = "00:00:00:00:00:" + \
                str( hex( i + 10 )[ 2: ] ).zfill( 2 ).upper()
            host1Id = main.ONOScli1.getHost( host1 )[ 'id' ]
            host2Id = main.ONOScli1.getHost( host2 )[ 'id' ]
            for host in hostsJson:
                if host[ 'id' ] == host1Id:
                    ip1 = host[ 'ipAddresses' ][ 0 ]
                    ip1 = str( ip1 + "/32" )
                    device1 = host[ 'location' ][ 'elementId' ]
                    device1 = str( device1 + "/1" )
                elif host[ 'id' ] == host2Id:
                    ip2 = str( host[ 'ipAddresses' ][ 0 ] ) + "/32"
                    device2 = host[ 'location' ][ 'elementId' ]
                    device2 = str( device2 + "/1" )

            pIntentResult1 = main.ONOScli1.addPointIntent(
                ingressDevice=device1,
                egressDevice=device2,
                ipSrc=ip1,
                ipDst=ip2,
                ethType=main.params[ 'SDNIP' ][ 'ethType' ],
                ipProto=main.params[ 'SDNIP' ][ 'icmpProto' ], )

            getIntentResult = main.ONOScli1.intents( jsonFormat=False )
            main.log.info( getIntentResult )

            pIntentResult2 = main.ONOScli1.addPointIntent(
                ingressDevice=device2,
                egressDevice=device1,
                ipSrc=ip2,
                ipDst=ip1,
                ethType=main.params[ 'SDNIP' ][ 'ethType' ],
                ipProto=main.params[ 'SDNIP' ][ 'icmpProto' ] )

            getIntentResult = main.ONOScli1.intents( jsonFormat=False )
            main.log.info( getIntentResult )
            if ( pIntentResult1 and pIntentResult2 ) :
                # getIntentResult = main.ONOScli1.intents()
                # main.log.info( getIntentResult )
                main.log.info(
                    "Point intent related to SDN-IP matching" +
                    " on ICMP install successful" )

        time.sleep( 15 )
        getIntentResult = main.ONOScli1.intents( jsonFormat=False )
        main.log.info( "intents = " + getIntentResult )
        getFlowsResult = main.ONOScli1.flows()
        main.log.info( "flows = " + getFlowsResult )

        count = 1
        i = 8
        PingResult = main.TRUE
        while i < 11:
            main.log.info(
                "\n\nh" + str( i ) + " is Pinging h" + str( i + 10 ) )
            ping = main.Mininet1.pingHost(
                src="h" + str( i ), target="h" + str( i + 10 ) )
            if ping == main.FALSE and count < 3:
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
                "Ping test after Point intents related to" +
                " SDN-IP matching on ICMP failed." )
            # main.cleanup()
            # main.exit()
        if PingResult == main.TRUE:
            main.log.report(
                "Ping all test after Point intents related to" +
                " SDN-IP matching on ICMP successful" )

        case31Result = PingResult
        utilities.assertEquals(
            expect=main.TRUE,
            actual=case31Result,
            onpass="Point intent related to SDN-IP " +
            "matching on ICMP and ping test successful",
            onfail="Point intent related to SDN-IP" +
            " matching on ICMP and ping test failed" )

    def CASE32( self ):
        """
            This test case adds point intent related to SDN-IP matching on TCP
            ( ethertype=IPV4, ipProto=6, DefaultPort for iperf=5001 )
            Note: Although BGP port is 179, we are using 5001 because iperf
            is used for verifying and iperf's default port is 5001
        """
        import json

        main.log.report(
            "This test case adds point intent" +
            " related to SDN-IP matching on TCP" )
        main.case(
            "Adding bidirectional point intent related" +
            " to SDN-IP matching on TCP" )
        main.step( "Adding bidirectional point intent" )
        """
        add-point-intent --ipSrc=10.0.0.8/32 --ipDst=10.0.0.18/32
        --ethType=IPV4 --ipProto=6 --tcpDst=5001  of:0000000000003008/1
        of:0000000000006018/1

        add-point-intent --ipSrc=10.0.0.18/32 --ipDst=10.0.0.8/32
        --ethType=IPV4 --ipProto=6 --tcpDst=5001  of:0000000000006018/1
        of:0000000000003008/1

        add-point-intent --ipSrc=10.0.0.8/32 --ipDst=10.0.0.18/32
        --ethType=IPV4 --ipProto=6 --tcpSrc=5001  of:0000000000003008/1
        of:0000000000006018/1

        add-point-intent --ipSrc=10.0.0.18/32 --ipDst=10.0.0.8/32
        --ethType=IPV4 --ipProto=6 --tcpSrc=5001  of:0000000000006018/1
        of:0000000000003008/1

        """
        hostsJson = json.loads( main.ONOScli1.hosts() )
        for i in range( 8, 9 ):
            main.log.info(
                "Adding point intent between h" + str( i ) +
                " and h" + str( i + 10 ) )
            host1 = "00:00:00:00:00:" + \
                str( hex( i )[ 2: ] ).zfill( 2 ).upper()
            host2 = "00:00:00:00:00:" + \
                str( hex( i + 10 )[ 2: ] ).zfill( 2 ).upper()
            host1Id = main.ONOScli1.getHost( host1 )[ 'id' ]
            host2Id = main.ONOScli1.getHost( host2 )[ 'id' ]
            for host in hostsJson:
                if host[ 'id' ] == host1Id:
                    ip1 = host[ 'ipAddresses' ][ 0 ]
                    ip1 = str( ip1 + "/32" )
                    device1 = host[ 'location' ][ 'elementId' ]
                    device1 = str( device1 + "/1" )
                elif host[ 'id' ] == host2Id:
                    ip2 = str( host[ 'ipAddresses' ][ 0 ] ) + "/32"
                    device2 = host[ 'location' ][ 'elementId' ]
                    device2 = str( device2 + "/1" )

            pIntentResult1 = main.ONOScli1.addPointIntent(
                ingressDevice=device1,
                egressDevice=device2,
                ipSrc=ip1,
                ipDst=ip2,
                ethType=main.params[ 'SDNIP' ][ 'ethType' ],
                ipProto=main.params[ 'SDNIP' ][ 'tcpProto' ],
                tcpDst=main.params[ 'SDNIP' ][ 'dstPort' ] )
            pIntentResult2 = main.ONOScli1.addPointIntent(
                ingressDevice=device2,
                egressDevice=device1,
                ipSrc=ip2,
                ipDst=ip1,
                ethType=main.params[ 'SDNIP' ][ 'ethType' ],
                ipProto=main.params[ 'SDNIP' ][ 'tcpProto' ],
                tcpDst=main.params[ 'SDNIP' ][ 'dstPort' ] )

            pIntentResult3 = main.ONOScli1.addPointIntent(
                ingressDevice=device1,
                egressDevice=device2,
                ipSrc=ip1,
                ipDst=ip2,
                ethType=main.params[ 'SDNIP' ][ 'ethType' ],
                ipProto=main.params[ 'SDNIP' ][ 'tcpProto' ],
                tcpSrc=main.params[ 'SDNIP' ][ 'srcPort' ] )
            pIntentResult4 = main.ONOScli1.addPointIntent(
                ingressDevice=device2,
                egressDevice=device1,
                ipSrc=ip2,
                ipDst=ip1,
                ethType=main.params[ 'SDNIP' ][ 'ethType' ],
                ipProto=main.params[ 'SDNIP' ][ 'tcpProto' ],
                tcpSrc=main.params[ 'SDNIP' ][ 'srcPort' ] )

            getIntentResult = main.ONOScli1.intents( jsonFormat=False )
            main.log.info( getIntentResult )
            pIntentResult = main.TRUE
            if getIntentResult:
                main.log.report(
                    "Point intent related to SDN-IP matching" +
                    " on TCP install successful" )
            else:
                main.log.report(
                    "Point intent related to SDN-IP matching" +
                    " on TCP install failed" )
                pIntentResult = main.FALSE

        iperfResult = main.Mininet1.iperf( 'h8', 'h18' )
        if iperfResult == main.TRUE:
            main.log.report( "iperf test successful" )
        else:
            main.log.report( "iperf test failed" )

        case32Result = pIntentResult and iperfResult
        utilities.assertEquals(
            expect=main.TRUE,
            actual=case32Result,
            onpass="Ping all test after Point intents addition related " +
            "to SDN-IP on TCP match successful",
            onfail="Ping all test after Point intents addition related " +
            "to SDN-IP on TCP match failed" )

    def CASE33( self ):
        """
            This test case adds multipoint to singlepoint  intent related to
            SDN-IP matching on destination ip and the action is to rewrite
            the mac address
            Here the mac address to be rewritten is the mac address of the
            egress device
        """
        import json
        import time

        main.log.report(
            "This test case adds multipoint to singlepoint intent related to" +
            " SDN-IP matching on destination ip and " +
            "rewrite mac address action" )
        main.case(
            "Adding multipoint to singlepoint intent related to SDN-IP" +
            " matching on destination ip" )
        main.step( "Adding bidirectional multipoint to singlepoint intent" )
        """
        add-multi-to-single-intent --ipDst=10.0.3.0/24
        --setEthDst=00:00:00:00:00:12 of:0000000000003008/1 0000000000003009/1
        of:0000000000006018/1

        add-multi-to-single-intent --ipDst=10.0.1.0/24
        --setEthDst=00:00:00:00:00:08 of:0000000000006018/1 0000000000003009/1
        of:0000000000003008/1
        """
        main.case(
            "Installing multipoint to single point " +
            "intent with rewrite mac address" )
        main.step( "Uninstalling proxy arp app" )
        # deactivating proxyarp app
        appInstallResult = main.ONOScli1.deactivateApp( "org.onosproject.proxyarp" )
        appCheck = main.ONOScli1.appToIDCheck()
        if appCheck != main.TRUE:
            main.log.warn( main.ONOScli1.apps() )
            main.log.warn( main.ONOScli1.appIDs() )
        time.sleep( 30 )
        main.log.info( "onos-app-proxyarp deactivated" )

        main.step( "Changing ipaddress of hosts h8,h9 and h18" )
        main.Mininet1.changeIP(
            host='h8',
            intf='h8-eth0',
            newIP='10.0.1.1',
            newNetmask='255.255.255.0' )
        main.Mininet1.changeIP(
            host='h9',
            intf='h9-eth0',
            newIP='10.0.2.1',
            newNetmask='255.255.255.0' )
        main.Mininet1.changeIP(
            host='h10',
            intf='h10-eth0',
            newIP='10.0.3.1',
            newNetmask='255.255.255.0' )

        main.step( "Changing default gateway of hosts h8,h9 and h18" )
        main.Mininet1.changeDefaultGateway( host='h8', newGW='10.0.1.254' )
        main.Mininet1.changeDefaultGateway( host='h9', newGW='10.0.2.254' )
        main.Mininet1.changeDefaultGateway( host='h10', newGW='10.0.3.254' )

        main.step(
            "Assigning random mac address to the default gateways " +
            "since proxyarp app is uninstalled" )
        main.Mininet1.addStaticMACAddress(
            host='h8',
            GW='10.0.1.254',
            macaddr='00:00:00:00:11:11' )
        main.Mininet1.addStaticMACAddress(
            host='h9',
            GW='10.0.2.254',
            macaddr='00:00:00:00:22:22' )
        main.Mininet1.addStaticMACAddress(
            host='h10',
            GW='10.0.3.254',
            macaddr='00:00:00:00:33:33' )

        main.step( "Verify static gateway and MAC address assignment" )
        main.Mininet1.verifyStaticGWandMAC( host='h8' )
        main.Mininet1.verifyStaticGWandMAC( host='h9' )
        main.Mininet1.verifyStaticGWandMAC( host='h10' )

        ingressDevice1=main.params[ 'MULTIPOINT_INTENT' ][ 'device1' ]
        ingressDevice2=main.params[ 'MULTIPOINT_INTENT' ][ 'device2' ]
        ingressDeviceList = []
        ingressDeviceList.append( ingressDevice1 )
        ingressDeviceList.append( ingressDevice2 )

        main.step( "Adding multipoint to singlepoint intent" )
        pIntentResult1 = main.ONOScli1.addMultipointToSinglepointIntent(
            ingressDeviceList,
            egressDevice=main.params[ 'MULTIPOINT_INTENT' ][ 'device3' ],
            ipDst=main.params[ 'MULTIPOINT_INTENT' ][ 'ip1' ],
            setEthDst=main.params[ 'MULTIPOINT_INTENT' ][ 'mac1' ] )

        ingressDevice1=main.params[ 'MULTIPOINT_INTENT' ][ 'device3' ]
        ingressDevice2=main.params[ 'MULTIPOINT_INTENT' ][ 'device2' ]
        ingressDeviceList = [ingressDevice1, ingressDevice2]

        pIntentResult2 = main.ONOScli1.addMultipointToSinglepointIntent(
            ingressDeviceList,
            egressDevice=main.params[ 'MULTIPOINT_INTENT' ][ 'device1' ],
            ipDst=main.params[ 'MULTIPOINT_INTENT' ][ 'ip2' ],
            setEthDst=main.params[ 'MULTIPOINT_INTENT' ][ 'mac2' ] )

        pIntentResult = pIntentResult1 and pIntentResult2
        if pIntentResult == main.FALSE:
            main.log.info(
                "Multi point to single point intent " +
                "installation failed" )
        else:
            pIntentResult = main.TRUE 
            getIntentResult = main.ONOScli1.intents( jsonFormat=False )
            main.log.info( "intents = " + getIntentResult )

            time.sleep( 10 )
            getFlowsResult = main.ONOScli1.flows( jsonFormat=False )
            main.log.info( "flows = " + getFlowsResult )

            count = 1
            i = 8
            PingResult = main.TRUE

            main.log.info( "\n\nh" + str( i ) + " is Pinging h" + str( i + 2 ) )
            ping = main.Mininet1.pingHost(
            src="h" + str( i ), target="h" + str( i + 2 ) )
            if ping == main.FALSE and count < 3:
                count += 1
                PingResult = main.FALSE
                main.log.report( "Ping between h" +
                             str( i ) +
                             " and h" +
                             str( i +
                                  2 ) +
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
                PingResult = main.FALSE
            elif ping == main.TRUE:
                main.log.info( "Ping test between h" +
                           str( i ) +
                           " and h" +
                           str( i +
                                2 ) +
                           " passed!" )
                PingResult = main.TRUE
            else:
                main.log.info( "Unknown error" )
                PingResult = main.ERROR

            if PingResult == main.FALSE:
                main.log.report( "Ping test failed." )
                # main.cleanup()
                # main.exit()
            if PingResult == main.TRUE:
                main.log.report( "Ping all successful" )

        if pIntentResult == main.TRUE:
            main.log.info(
                "Multi point intent with rewrite mac " +
                "address installation and ping successful" )

        case33Result = pIntentResult and PingResult
        utilities.assertEquals(
            expect=main.TRUE,
            actual=case33Result,
            onpass="Ping all test after multipoint to single point" +
            " intent addition with rewrite mac address successful",
            onfail="Ping all test after multipoint to single point intent" +
            " addition with rewrite mac address failed" )

    def CASE20( self ):
        """
            Exit from mininet cli
            reinstall ONOS
        """
        import time
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

        time.sleep( 5 )
        main.step( "Uninstalling ONOS package" )
        onos1UninstallResult = main.ONOSbench.onosUninstall( nodeIp = ONOS1Ip)
        onos2UninstallResult = main.ONOSbench.onosUninstall( nodeIp = ONOS2Ip)
        onos3UninstallResult = main.ONOSbench.onosUninstall( nodeIp = ONOS3Ip)
        onosUninstallResult = onos1UninstallResult and onos2UninstallResult \
                              and onos3UninstallResult
        time.sleep( 15 )
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

        time.sleep( 10 )
        onos1Isup = main.ONOSbench.isup( ONOS1Ip )
        onos2Isup = main.ONOSbench.isup( ONOS2Ip )
        onos3Isup = main.ONOSbench.isup( ONOS3Ip )
        onosIsup = onos1Isup and onos2Isup and onos3Isup
        if onosIsup == main.TRUE:
            main.log.report( "ONOS instances are up and ready" )
        else:
            main.log.report( "ONOS instances may not be up" )

        main.step( "Starting ONOS service" )
        time.sleep( 10 )
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
            links=46.
            All this is hardcoded in the testcase. If the topology changes,
            these hardcoded values need to be changed
        """
        import time
        main.log.report(
            "This testcase compares the optical+packet topology against what" +
            " is expected" )
        main.case( "Topology comparision" )
        main.step( "Topology comparision" )
        devicesResult = main.ONOScli3.devices( jsonFormat=False )
        time.sleep( 15 )
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
        if linkActiveCount == 46:
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
        #flowHandle = main.ONOScli1.flows()
        #main.log.info( "flows :" + flowHandle )

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
        #flowHandle = main.ONOScli3.flows()
        #main.log.info( "flows :" + flowHandle )

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
