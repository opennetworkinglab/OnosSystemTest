"""
Description: This test is to determine if ONOS can handle
    a minority of it's nodes restarting

List of test cases:
CASE1: Compile ONOS and push it to the test machines
CASE2: Assign mastership to controllers
CASE3: Assign intents
CASE4: Ping across added host intents
CASE5: Reading state of ONOS
CASE6: The Failure case.
CASE7: Check state after control plane failure
CASE8: Compare topo
CASE9: Link s3-s28 down
CASE10: Link s3-s28 up
CASE11: Switch down
CASE12: Switch up
CASE13: Clean up
CASE14: start election app on all onos nodes
CASE15: Check that Leadership Election is still functional
"""


class HATestMinorityRestart:

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
        main.log.report(
            "ONOS HA test: Restart minority of ONOS nodes - initialization" )
        main.case( "Setting up test environment" )
        # TODO: save all the timers and output them for plotting

        # load some vairables from the params file
        PULLCODE = False
        if main.params[ 'Git' ] == 'True':
            PULLCODE = True
        gitBranch = main.params[ 'branch' ]
        cellName = main.params[ 'ENV' ][ 'cellName' ]

        # set global variables
        global ONOS1Ip
        global ONOS1Port
        global ONOS2Ip
        global ONOS2Port
        global ONOS3Ip
        global ONOS3Port
        global ONOS4Ip
        global ONOS4Port
        global ONOS5Ip
        global ONOS5Port
        global ONOS6Ip
        global ONOS6Port
        global ONOS7Ip
        global ONOS7Port
        global numControllers

        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]
        ONOS1Port = main.params[ 'CTRL' ][ 'port1' ]
        ONOS2Ip = main.params[ 'CTRL' ][ 'ip2' ]
        ONOS2Port = main.params[ 'CTRL' ][ 'port2' ]
        ONOS3Ip = main.params[ 'CTRL' ][ 'ip3' ]
        ONOS3Port = main.params[ 'CTRL' ][ 'port3' ]
        ONOS4Ip = main.params[ 'CTRL' ][ 'ip4' ]
        ONOS4Port = main.params[ 'CTRL' ][ 'port4' ]
        ONOS5Ip = main.params[ 'CTRL' ][ 'ip5' ]
        ONOS5Port = main.params[ 'CTRL' ][ 'port5' ]
        ONOS6Ip = main.params[ 'CTRL' ][ 'ip6' ]
        ONOS6Port = main.params[ 'CTRL' ][ 'port6' ]
        ONOS7Ip = main.params[ 'CTRL' ][ 'ip7' ]
        ONOS7Port = main.params[ 'CTRL' ][ 'port7' ]
        numControllers = int( main.params[ 'num_controllers' ] )

        main.step( "Applying cell variable to environment" )
        cellResult = main.ONOSbench.setCell( cellName )
        verifyResult = main.ONOSbench.verifyCell()

        # FIXME:this is short term fix
        main.log.report( "Removing raft logs" )
        main.ONOSbench.onosRemoveRaftLogs()
        main.log.report( "Uninstalling ONOS" )
        main.ONOSbench.onosUninstall( ONOS1Ip )
        main.ONOSbench.onosUninstall( ONOS2Ip )
        main.ONOSbench.onosUninstall( ONOS3Ip )
        main.ONOSbench.onosUninstall( ONOS4Ip )
        main.ONOSbench.onosUninstall( ONOS5Ip )
        main.ONOSbench.onosUninstall( ONOS6Ip )
        main.ONOSbench.onosUninstall( ONOS7Ip )

        cleanInstallResult = main.TRUE
        gitPullResult = main.TRUE

        main.step( "Starting Mininet" )
        main.Mininet1.startNet( )

        main.step( "Compiling the latest version of ONOS" )
        if PULLCODE:
            main.step( "Git checkout and pull " + gitBranch )
            main.ONOSbench.gitCheckout( gitBranch )
            gitPullResult = main.ONOSbench.gitPull()

            main.step( "Using mvn clean & install" )
            cleanInstallResult = main.ONOSbench.cleanInstall()
        else:
            main.log.warn( "Did not pull new code so skipping mvn " +
                           "clean install" )
        main.ONOSbench.getVersion( report=True )

        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.onosPackage()

        main.step( "Installing ONOS package" )
        onos1InstallResult = main.ONOSbench.onosInstall( options="-f",
                                                           node=ONOS1Ip )
        onos2InstallResult = main.ONOSbench.onosInstall( options="-f",
                                                           node=ONOS2Ip )
        onos3InstallResult = main.ONOSbench.onosInstall( options="-f",
                                                           node=ONOS3Ip )
        onos4InstallResult = main.ONOSbench.onosInstall( options="-f",
                                                           node=ONOS4Ip )
        onos5InstallResult = main.ONOSbench.onosInstall( options="-f",
                                                           node=ONOS5Ip )
        onos6InstallResult = main.ONOSbench.onosInstall( options="-f",
                                                           node=ONOS6Ip )
        onos7InstallResult = main.ONOSbench.onosInstall( options="-f",
                                                           node=ONOS7Ip )
        onosInstallResult = onos1InstallResult and onos2InstallResult\
            and onos3InstallResult and onos4InstallResult\
            and onos5InstallResult and onos6InstallResult\
            and onos7InstallResult

        main.step( "Checking if ONOS is up yet" )
        for i in range( 2 ):
            onos1Isup = main.ONOSbench.isup( ONOS1Ip )
            if not onos1Isup:
                main.log.report( "ONOS1 didn't start!" )
                main.ONOSbench.onosStop( ONOS1Ip )
                main.ONOSbench.onosStart( ONOS1Ip )
            onos2Isup = main.ONOSbench.isup( ONOS2Ip )
            if not onos2Isup:
                main.log.report( "ONOS2 didn't start!" )
                main.ONOSbench.onosStop( ONOS2Ip )
                main.ONOSbench.onosStart( ONOS2Ip )
            onos3Isup = main.ONOSbench.isup( ONOS3Ip )
            if not onos3Isup:
                main.log.report( "ONOS3 didn't start!" )
                main.ONOSbench.onosStop( ONOS3Ip )
                main.ONOSbench.onosStart( ONOS3Ip )
            onos4Isup = main.ONOSbench.isup( ONOS4Ip )
            if not onos4Isup:
                main.log.report( "ONOS4 didn't start!" )
                main.ONOSbench.onosStop( ONOS4Ip )
                main.ONOSbench.onosStart( ONOS4Ip )
            onos5Isup = main.ONOSbench.isup( ONOS5Ip )
            if not onos5Isup:
                main.log.report( "ONOS5 didn't start!" )
                main.ONOSbench.onosStop( ONOS5Ip )
                main.ONOSbench.onosStart( ONOS5Ip )
            onos6Isup = main.ONOSbench.isup( ONOS6Ip )
            if not onos6Isup:
                main.log.report( "ONOS6 didn't start!" )
                main.ONOSbench.onosStop( ONOS6Ip )
                main.ONOSbench.onosStart( ONOS6Ip )
            onos7Isup = main.ONOSbench.isup( ONOS7Ip )
            if not onos7Isup:
                main.log.report( "ONOS7 didn't start!" )
                main.ONOSbench.onosStop( ONOS7Ip )
                main.ONOSbench.onosStart( ONOS7Ip )
            onosIsupResult = onos1Isup and onos2Isup and onos3Isup\
                and onos4Isup and onos5Isup and onos6Isup and onos7Isup
            if onosIsupResult == main.TRUE:
                break

        cliResult1 = main.ONOScli1.startOnosCli( ONOS1Ip )
        cliResult2 = main.ONOScli2.startOnosCli( ONOS2Ip )
        cliResult3 = main.ONOScli3.startOnosCli( ONOS3Ip )
        cliResult4 = main.ONOScli4.startOnosCli( ONOS4Ip )
        cliResult5 = main.ONOScli5.startOnosCli( ONOS5Ip )
        cliResult6 = main.ONOScli6.startOnosCli( ONOS6Ip )
        cliResult7 = main.ONOScli7.startOnosCli( ONOS7Ip )
        cliResults = cliResult1 and cliResult2 and cliResult3 and\
            cliResult4 and cliResult5 and cliResult6 and cliResult7

        main.step( "Start Packet Capture MN" )
        main.Mininet2.startTcpdump(
            str( main.params[ 'MNtcpdump' ][ 'folder' ] ) + str( main.TEST )
            + "-MN.pcap",
            intf=main.params[ 'MNtcpdump' ][ 'intf' ],
            port=main.params[ 'MNtcpdump' ][ 'port' ] )

        case1Result = ( cleanInstallResult and packageResult and
                        cellResult and verifyResult and onosInstallResult
                        and onosIsupResult and cliResults )

        utilities.assert_equals( expect=main.TRUE, actual=case1Result,
                                 onpass="Test startup successful",
                                 onfail="Test startup NOT successful" )

        if case1Result == main.FALSE:
            main.cleanup()
            main.exit()

    def CASE2( self, main ):
        """
        Assign mastership to controllers
        """
        import re

        main.log.report( "Assigning switches to controllers" )
        main.case( "Assigning Controllers" )
        main.step( "Assign switches to controllers" )

        for i in range( 1, 29 ):
            main.Mininet1.assignSwController(
                sw=str( i ),
                count=numControllers,
                ip1=ONOS1Ip, port1=ONOS1Port,
                ip2=ONOS2Ip, port2=ONOS2Port,
                ip3=ONOS3Ip, port3=ONOS3Port,
                ip4=ONOS4Ip, port4=ONOS4Port,
                ip5=ONOS5Ip, port5=ONOS5Port,
                ip6=ONOS6Ip, port6=ONOS6Port,
                ip7=ONOS7Ip, port7=ONOS7Port )

        mastershipCheck = main.TRUE
        for i in range( 1, 29 ):
            response = main.Mininet1.getSwController( "s" + str( i ) )
            try:
                main.log.info( str( response ) )
            except:
                main.log.info( repr( response ) )
            if re.search( "tcp:" + ONOS1Ip, response )\
                    and re.search( "tcp:" + ONOS2Ip, response )\
                    and re.search( "tcp:" + ONOS3Ip, response )\
                    and re.search( "tcp:" + ONOS4Ip, response )\
                    and re.search( "tcp:" + ONOS5Ip, response )\
                    and re.search( "tcp:" + ONOS6Ip, response )\
                    and re.search( "tcp:" + ONOS7Ip, response ):
                mastershipCheck = mastershipCheck and main.TRUE
            else:
                mastershipCheck = main.FALSE
        if mastershipCheck == main.TRUE:
            main.log.report( "Switch mastership assigned correctly" )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=mastershipCheck,
            onpass="Switch mastership assigned correctly",
            onfail="Switches not assigned correctly to controllers" )

        # Manually assign mastership to the controller we want
        roleCall = main.TRUE
        roleCheck = main.TRUE
        try:
            # Assign switch
            deviceId = main.ONOScli1.getDevice( "1000" ).get( 'id' )
            assert deviceId, "No device id for s1 in ONOS"
            roleCall = roleCall and main.ONOScli1.deviceRole(
                deviceId,
                ONOS1Ip )
            # Check assignment
            if ONOS1Ip in main.ONOScli1.getRole( deviceId ).get( 'master' ):
                roleCheck = roleCheck and main.TRUE
            else:
                roleCheck = roleCheck and main.FALSE

            # Assign switch
            deviceId = main.ONOScli1.getDevice( "2800" ).get( 'id' )
            assert deviceId, "No device id for s28 in ONOS"
            roleCall = roleCall and main.ONOScli1.deviceRole(
                deviceId,
                ONOS1Ip )
            # Check assignment
            if ONOS1Ip in main.ONOScli1.getRole( deviceId ).get( 'master' ):
                roleCheck = roleCheck and main.TRUE
            else:
                roleCheck = roleCheck and main.FALSE

            # Assign switch
            deviceId = main.ONOScli1.getDevice( "2000" ).get( 'id' )
            assert deviceId, "No device id for s2 in ONOS"
            roleCall = roleCall and main.ONOScli1.deviceRole(
                deviceId,
                ONOS2Ip )
            # Check assignment
            if ONOS2Ip in main.ONOScli1.getRole( deviceId ).get( 'master' ):
                roleCheck = roleCheck and main.TRUE
            else:
                roleCheck = roleCheck and main.FALSE

            # Assign switch
            deviceId = main.ONOScli1.getDevice( "3000" ).get( 'id' )
            assert deviceId, "No device id for s3 in ONOS"
            roleCall = roleCall and main.ONOScli1.deviceRole(
                deviceId,
                ONOS2Ip )
            # Check assignment
            if ONOS2Ip in main.ONOScli1.getRole( deviceId ).get( 'master' ):
                roleCheck = roleCheck and main.TRUE
            else:
                roleCheck = roleCheck and main.FALSE

            # Assign switch
            deviceId = main.ONOScli1.getDevice( "5000" ).get( 'id' )
            assert deviceId, "No device id for s5 in ONOS"
            roleCall = roleCall and main.ONOScli1.deviceRole(
                deviceId,
                ONOS3Ip )
            # Check assignment
            if ONOS3Ip in main.ONOScli1.getRole( deviceId ).get( 'master' ):
                roleCheck = roleCheck and main.TRUE
            else:
                roleCheck = roleCheck and main.FALSE

            # Assign switch
            deviceId = main.ONOScli1.getDevice( "6000" ).get( 'id' )
            assert deviceId, "No device id for s6 in ONOS"
            roleCall = roleCall and main.ONOScli1.deviceRole(
                deviceId,
                ONOS3Ip )
            # Check assignment
            if ONOS3Ip in main.ONOScli1.getRole( deviceId ).get( 'master' ):
                roleCheck = roleCheck and main.TRUE
            else:
                roleCheck = roleCheck and main.FALSE

            # Assign switch
            deviceId = main.ONOScli1.getDevice( "3004" ).get( 'id' )
            assert deviceId, "No device id for s4 in ONOS"
            roleCall = roleCall and main.ONOScli1.deviceRole(
                deviceId,
                ONOS4Ip )
            # Check assignment
            if ONOS4Ip in main.ONOScli1.getRole( deviceId ).get( 'master' ):
                roleCheck = roleCheck and main.TRUE
            else:
                roleCheck = roleCheck and main.FALSE

            for i in range( 8, 18 ):
                dpid = '3' + str( i ).zfill( 3 )
                deviceId = main.ONOScli1.getDevice( dpid ).get( 'id' )
                assert deviceId, "No device id for s%i in ONOS" % i
                roleCall = roleCall and main.ONOScli1.deviceRole(
                    deviceId,
                    ONOS5Ip )
                # Check assignment
                if ONOS5Ip in main.ONOScli1.getRole( deviceId ).get( 'master' ):
                    roleCheck = roleCheck and main.TRUE
                else:
                    roleCheck = roleCheck and main.FALSE

            deviceId = main.ONOScli1.getDevice( "6007" ).get( 'id' )
            assert deviceId, "No device id for s7 in ONOS"
            roleCall = roleCall and main.ONOScli1.deviceRole(
                deviceId,
                ONOS6Ip )
            # Check assignment
            if ONOS6Ip in main.ONOScli1.getRole( deviceId ).get( 'master' ):
                roleCheck = roleCheck and main.TRUE
            else:
                roleCheck = roleCheck and main.FALSE

            for i in range( 18, 28 ):
                dpid = '6' + str( i ).zfill( 3 )
                deviceId = main.ONOScli1.getDevice( dpid ).get( 'id' )
                assert deviceId, "No device id for s%i in ONOS" % i
                roleCall = roleCall and main.ONOScli1.deviceRole(
                    deviceId,
                    ONOS7Ip )
                # Check assignment
                if ONOS7Ip in main.ONOScli1.getRole( deviceId ).get( 'master' ):
                    roleCheck = roleCheck and main.TRUE
                else:
                    roleCheck = roleCheck and main.FALSE
        except ( AttributeError, AssertionError ):
            main.log.exception( "Something is wrong with ONOS device view" )
            main.log.info( main.ONOScli1.devices() )

        utilities.assert_equals(
            expect=main.TRUE,
            actual=roleCall,
            onpass="Re-assigned switch mastership to designated controller",
            onfail="Something wrong with deviceRole calls" )

        utilities.assert_equals(
            expect=main.TRUE,
            actual=roleCheck,
            onpass="Switches were successfully reassigned to designated " +
                   "controller",
            onfail="Switches were not successfully reassigned" )
        mastershipCheck = mastershipCheck and roleCall and roleCheck
        utilities.assert_equals( expect=main.TRUE, actual=mastershipCheck,
                                 onpass="Switch mastership correctly assigned",
                                 onfail="Error in (re)assigning switch" +
                                 " mastership" )

    def CASE3( self, main ):
        """
        Assign intents
        """
        import time
        import json
        main.log.report( "Adding host intents" )
        main.case( "Adding host Intents" )

        main.step( "Discovering  Hosts( Via pingall for now )" )
        # FIXME: Once we have a host discovery mechanism, use that instead

        # install onos-app-fwd
        main.log.info( "Install reactive forwarding app" )
        main.ONOScli1.featureInstall( "onos-app-fwd" )
        main.ONOScli2.featureInstall( "onos-app-fwd" )
        main.ONOScli3.featureInstall( "onos-app-fwd" )
        main.ONOScli4.featureInstall( "onos-app-fwd" )
        main.ONOScli5.featureInstall( "onos-app-fwd" )
        main.ONOScli6.featureInstall( "onos-app-fwd" )
        main.ONOScli7.featureInstall( "onos-app-fwd" )

        # REACTIVE FWD test
        pingResult = main.FALSE
        time1 = time.time()
        pingResult = main.Mininet1.pingall()
        utilities.assert_equals(
            expect=main.TRUE,
            actual=pingResult,
            onpass="Reactive Pingall test passed",
            onfail="Reactive Pingall failed, one or more ping pairs failed" )
        time2 = time.time()
        main.log.info( "Time for pingall: %2f seconds" % ( time2 - time1 ) )

        # uninstall onos-app-fwd
        main.log.info( "Uninstall reactive forwarding app" )
        main.ONOScli1.featureUninstall( "onos-app-fwd" )
        main.ONOScli2.featureUninstall( "onos-app-fwd" )
        main.ONOScli3.featureUninstall( "onos-app-fwd" )
        main.ONOScli4.featureUninstall( "onos-app-fwd" )
        main.ONOScli5.featureUninstall( "onos-app-fwd" )
        main.ONOScli6.featureUninstall( "onos-app-fwd" )
        main.ONOScli7.featureUninstall( "onos-app-fwd" )
        # timeout for fwd flows
        time.sleep( 10 )

        main.step( "Add  host intents" )
        intentIds = []
        # TODO:  move the host numbers to params
        #        Maybe look at all the paths we ping?
        intentAddResult = True
        hostResult = main.TRUE
        for i in range( 8, 18 ):
            main.log.info( "Adding host intent between h" + str( i ) +
                           " and h" + str( i + 10 ) )
            host1 = "00:00:00:00:00:" + \
                str( hex( i )[ 2: ] ).zfill( 2 ).upper()
            host2 = "00:00:00:00:00:" + \
                str( hex( i + 10 )[ 2: ] ).zfill( 2 ).upper()
            # NOTE: getHost can return None
            host1Dict = main.ONOScli1.getHost( host1 )
            host2Dict = main.ONOScli1.getHost( host2 )
            host1Id = None
            host2Id = None
            if host1Dict and host2Dict:
                host1Id = host1Dict.get( 'id', None )
                host2Id = host2Dict.get( 'id', None )
            if host1Id and host2Id:
                # Changed onos node to test something
                tmpId = main.ONOScli4.addHostIntent(
                    host1Id,
                    host2Id )
                if tmpId:
                    main.log.info( "Added intent with id: " + tmpId )
                    intentIds.append( tmpId )
                else:
                    main.log.error( "addHostIntent reutrned None" )
            else:
                main.log.error( "Error, getHost() failed" )
                main.log.warn( json.dumps( json.loads( main.ONOScli1.hosts() ),
                                           sort_keys=True,
                                           indent=4,
                                           separators=( ',', ': ' ) ) )
                hostResult = main.FALSE
        onosIds = main.ONOScli1.getAllIntentsId()
        main.log.info( "Submitted intents: " + str( intentIds ) )
        main.log.info( "Intents in ONOS: " + str( onosIds ) )
        for intent in intentIds:
            if intent in onosIds:
                pass  # intent submitted is still in onos
            else:
                intentAddResult = False
        # Print the intent states
        intents = main.ONOScli1.intents()
        intentStates = []
        installedCheck = True 
        main.log.info( "%-6s%-15s%-15s" % ( 'Count', 'ID', 'State' ) )
        count = 0
        for intent in json.loads( intents ):  # Iter through intents of a node
            state = intent.get( 'state', None )
            if "INSTALLED" not in state:
                installedCheck = False
            intentId = intent.get( 'id', None )
            intentStates.append( ( intentId, state ) )
        # add submitted intents not in the store
        tmplist = [ i for i, s in intentStates ]
        missingIntents = False
        for i in intentIds:
            if i not in tmplist:
                intentStates.append( ( i, " - " ) )
                missingIntents = True
        intentStates.sort()
        for i, s in intentStates:
            count += 1
            main.log.info( "%-6s%-15s%-15s" %
                           ( str( count ), str( i ), str( s ) ) )
        main.ONOScli1.leaders()
        main.ONOScli1.partitions()
        # for node in nodes:
        #     node.pendingMap()
        pendingMap = main.ONOScli1.pendingMap()
        main.ONOScli2.pendingMap()
        main.ONOScli3.pendingMap()
        main.ONOScli4.pendingMap()
        main.ONOScli5.pendingMap()
        main.ONOScli6.pendingMap()
        main.ONOScli7.pendingMap()
        intentAddResult = bool( pingResult and hostResult and intentAddResult
                                and not missingIntents and installedCheck )
        utilities.assert_equals(
            expect=True,
            actual=intentAddResult,
            onpass="Pushed host intents to ONOS",
            onfail="Error in pushing host intents to ONOS" )

        if not intentAddResult or "key" in pendingMap:
            import time
            installedCheck = True
            main.log.info( "Sleeping 60 seconds to see if intents are found" )
            time.sleep( 60 )
            onosIds = main.ONOScli1.getAllIntentsId()
            main.log.info( "Submitted intents: " + str( intentIds ) )
            main.log.info( "Intents in ONOS: " + str( onosIds ) )
            # Print the intent states
            intents = main.ONOScli1.intents()
            intentStates = []
            main.log.info( "%-6s%-15s%-15s" % ( 'Count', 'ID', 'State' ) )
            count = 0
            for intent in json.loads( intents ):
                # Iter through intents of a node
                state = intent.get( 'state', None )
                if "INSTALLED" not in state:
                    installedCheck = False
                intentId = intent.get( 'id', None )
                intentStates.append( ( intentId, state ) )
            # add submitted intents not in the store
            tmplist = [ i for i, s in intentStates ]
            for i in intentIds:
                if i not in tmplist:
                    intentStates.append( ( i, " - " ) )
            intentStates.sort()
            for i, s in intentStates:
                count += 1
                main.log.info( "%-6s%-15s%-15s" %
                               ( str( count ), str( i ), str( s ) ) )
            main.ONOScli1.leaders()
            main.ONOScli1.pendingMap()
            main.ONOScli2.pendingMap()
            main.ONOScli3.pendingMap()
            main.ONOScli4.pendingMap()
            main.ONOScli5.pendingMap()
            main.ONOScli6.pendingMap()
            main.ONOScli7.pendingMap()

    def CASE4( self, main ):
        """
        Ping across added host intents
        """
        import json
        description = " Ping across added host intents"
        main.log.report( description )
        main.case( description )
        PingResult = main.TRUE
        for i in range( 8, 18 ):
            ping = main.Mininet1.pingHost( src="h" + str( i ),
                                           target="h" + str( i + 10 ) )
            PingResult = PingResult and ping
            if ping == main.FALSE:
                main.log.warn( "Ping failed between h" + str( i ) +
                               " and h" + str( i + 10 ) )
            elif ping == main.TRUE:
                main.log.info( "Ping test passed!" )
                # Don't set PingResult or you'd override failures
        if PingResult == main.FALSE:
            main.log.report(
                "Intents have not been installed correctly, pings failed." )
            # TODO: pretty print
            main.log.warn( "ONSO1 intents: " )
            main.log.warn( json.dumps( json.loads( main.ONOScli1.intents() ),
                                       sort_keys=True,
                                       indent=4,
                                       separators=( ',', ': ' ) ) )
        if PingResult == main.TRUE:
            main.log.report(
                "Intents have been installed correctly and verified by pings" )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=PingResult,
            onpass="Intents have been installed correctly and pings work",
            onfail="Intents have not been installed correctly, pings failed." )

        installedCheck = True
        if PingResult is not main.TRUE:
            # Print the intent states
            intents = main.ONOScli1.intents()
            intentStates = []
            main.log.info( "%-6s%-15s%-15s" % ( 'Count', 'ID', 'State' ) )
            count = 0
            # Iter through intents of a node
            for intent in json.loads( intents ):
                state = intent.get( 'state', None )
                if "INSTALLED" not in state:
                    installedCheck = False
                intentId = intent.get( 'id', None )
                intentStates.append( ( intentId, state ) )
            intentStates.sort()
            for i, s in intentStates:
                count += 1
                main.log.info( "%-6s%-15s%-15s" %
                               ( str( count ), str( i ), str( s ) ) )
            main.ONOScli1.leaders()
            main.ONOScli1.partitions()
            main.ONOScli1.pendingMap()
            main.ONOScli2.pendingMap()
            main.ONOScli3.pendingMap()
            main.ONOScli4.pendingMap()
            main.ONOScli5.pendingMap()
            main.ONOScli6.pendingMap()
            main.ONOScli7.pendingMap()
        if not installedCheck:
            main.log.info( "Waiting 60 seconds to see if intent states change" )
            time.sleep( 60 )
            # Print the intent states
            intents = main.ONOScli1.intents()
            intentStates = []
            main.log.info( "%-6s%-15s%-15s" % ( 'Count', 'ID', 'State' ) )
            count = 0
            # Iter through intents of a node
            for intent in json.loads( intents ):
                state = intent.get( 'state', None )
                if "INSTALLED" not in state:
                    installedCheck = False
                intentId = intent.get( 'id', None )
                intentStates.append( ( intentId, state ) )
            intentStates.sort()
            for i, s in intentStates:
                count += 1
                main.log.info( "%-6s%-15s%-15s" %
                               ( str( count ), str( i ), str( s ) ) )
            main.ONOScli1.leaders()
            main.ONOScli1.partitions()
            main.ONOScli1.pendingMap()
            main.ONOScli2.pendingMap()
            main.ONOScli3.pendingMap()
            main.ONOScli4.pendingMap()
            main.ONOScli5.pendingMap()
            main.ONOScli6.pendingMap()
            main.ONOScli7.pendingMap()

    def CASE5( self, main ):
        """
        Reading state of ONOS
        """
        import json
        # assumes that sts is already in you PYTHONPATH
        from sts.topology.teston_topology import TestONTopology

        main.log.report( "Setting up and gathering data for current state" )
        main.case( "Setting up and gathering data for current state" )
        # The general idea for this test case is to pull the state of
        # ( intents,flows, topology,... ) from each ONOS node
        # We can then compare them with eachother and also with past states

        main.step( "Get the Mastership of each switch from each controller" )
        global mastershipState
        mastershipState = []

        # Assert that each device has a master
        ONOS1MasterNotNull = main.ONOScli1.rolesNotNull()
        ONOS2MasterNotNull = main.ONOScli2.rolesNotNull()
        ONOS3MasterNotNull = main.ONOScli3.rolesNotNull()
        ONOS4MasterNotNull = main.ONOScli4.rolesNotNull()
        ONOS5MasterNotNull = main.ONOScli5.rolesNotNull()
        ONOS6MasterNotNull = main.ONOScli6.rolesNotNull()
        ONOS7MasterNotNull = main.ONOScli7.rolesNotNull()
        rolesNotNull = ONOS1MasterNotNull and ONOS2MasterNotNull and\
            ONOS3MasterNotNull and ONOS4MasterNotNull and\
            ONOS5MasterNotNull and ONOS6MasterNotNull and\
            ONOS7MasterNotNull
        utilities.assert_equals(
            expect=main.TRUE,
            actual=rolesNotNull,
            onpass="Each device has a master",
            onfail="Some devices don't have a master assigned" )

        ONOS1Mastership = main.ONOScli1.roles()
        ONOS2Mastership = main.ONOScli2.roles()
        ONOS3Mastership = main.ONOScli3.roles()
        ONOS4Mastership = main.ONOScli4.roles()
        ONOS5Mastership = main.ONOScli5.roles()
        ONOS6Mastership = main.ONOScli6.roles()
        ONOS7Mastership = main.ONOScli7.roles()
        if "Error" in ONOS1Mastership or not ONOS1Mastership\
                or "Error" in ONOS2Mastership or not ONOS2Mastership\
                or "Error" in ONOS3Mastership or not ONOS3Mastership\
                or "Error" in ONOS4Mastership or not ONOS4Mastership\
                or "Error" in ONOS5Mastership or not ONOS5Mastership\
                or "Error" in ONOS6Mastership or not ONOS6Mastership\
                or "Error" in ONOS7Mastership or not ONOS7Mastership:
            main.log.report( "Error in getting ONOS roles" )
            main.log.warn(
                "ONOS1 mastership response: " +
                repr( ONOS1Mastership ) )
            main.log.warn(
                "ONOS2 mastership response: " +
                repr( ONOS2Mastership ) )
            main.log.warn(
                "ONOS3 mastership response: " +
                repr( ONOS3Mastership ) )
            main.log.warn(
                "ONOS4 mastership response: " +
                repr( ONOS4Mastership ) )
            main.log.warn(
                "ONOS5 mastership response: " +
                repr( ONOS5Mastership ) )
            main.log.warn(
                "ONOS6 mastership response: " +
                repr( ONOS6Mastership ) )
            main.log.warn(
                "ONOS7 mastership response: " +
                repr( ONOS7Mastership ) )
            consistentMastership = main.FALSE
        elif ONOS1Mastership == ONOS2Mastership\
                and ONOS1Mastership == ONOS3Mastership\
                and ONOS1Mastership == ONOS4Mastership\
                and ONOS1Mastership == ONOS5Mastership\
                and ONOS1Mastership == ONOS6Mastership\
                and ONOS1Mastership == ONOS7Mastership:
            mastershipState = ONOS1Mastership
            consistentMastership = main.TRUE
            main.log.report(
                "Switch roles are consistent across all ONOS nodes" )
        else:
            main.log.warn(
                "ONOS1 roles: ",
                json.dumps(
                    json.loads( ONOS1Mastership ),
                    sort_keys=True,
                    indent=4,
                    separators=(
                        ',',
                        ': ' ) ) )
            main.log.warn(
                "ONOS2 roles: ",
                json.dumps(
                    json.loads( ONOS2Mastership ),
                    sort_keys=True,
                    indent=4,
                    separators=(
                        ',',
                        ': ' ) ) )
            main.log.warn(
                "ONOS3 roles: ",
                json.dumps(
                    json.loads( ONOS3Mastership ),
                    sort_keys=True,
                    indent=4,
                    separators=(
                        ',',
                        ': ' ) ) )
            main.log.warn(
                "ONOS4 roles: ",
                json.dumps(
                    json.loads( ONOS4Mastership ),
                    sort_keys=True,
                    indent=4,
                    separators=(
                        ',',
                        ': ' ) ) )
            main.log.warn(
                "ONOS5 roles: ",
                json.dumps(
                    json.loads( ONOS5Mastership ),
                    sort_keys=True,
                    indent=4,
                    separators=(
                        ',',
                        ': ' ) ) )
            main.log.warn(
                "ONOS6 roles: ",
                json.dumps(
                    json.loads( ONOS6Mastership ),
                    sort_keys=True,
                    indent=4,
                    separators=(
                        ',',
                        ': ' ) ) )
            main.log.warn(
                "ONOS7 roles: ",
                json.dumps(
                    json.loads( ONOS7Mastership ),
                    sort_keys=True,
                    indent=4,
                    separators=(
                        ',',
                        ': ' ) ) )
            consistentMastership = main.FALSE
        utilities.assert_equals(
            expect=main.TRUE,
            actual=consistentMastership,
            onpass="Switch roles are consistent across all ONOS nodes",
            onfail="ONOS nodes have different views of switch roles" )

        main.step( "Get the intents from each controller" )
        global intentState
        intentState = []
        ONOS1Intents = main.ONOScli1.intents( jsonFormat=True )
        ONOS2Intents = main.ONOScli2.intents( jsonFormat=True )
        ONOS3Intents = main.ONOScli3.intents( jsonFormat=True )
        ONOS4Intents = main.ONOScli4.intents( jsonFormat=True )
        ONOS5Intents = main.ONOScli5.intents( jsonFormat=True )
        ONOS6Intents = main.ONOScli6.intents( jsonFormat=True )
        ONOS7Intents = main.ONOScli7.intents( jsonFormat=True )
        intentCheck = main.FALSE
        if "Error" in ONOS1Intents or not ONOS1Intents\
                or "Error" in ONOS2Intents or not ONOS2Intents\
                or "Error" in ONOS3Intents or not ONOS3Intents\
                or "Error" in ONOS4Intents or not ONOS4Intents\
                or "Error" in ONOS5Intents or not ONOS5Intents\
                or "Error" in ONOS6Intents or not ONOS6Intents\
                or "Error" in ONOS7Intents or not ONOS7Intents:
            main.log.report( "Error in getting ONOS intents" )
            main.log.warn( "ONOS1 intents response: " + repr( ONOS1Intents ) )
            main.log.warn( "ONOS2 intents response: " + repr( ONOS2Intents ) )
            main.log.warn( "ONOS3 intents response: " + repr( ONOS3Intents ) )
            main.log.warn( "ONOS4 intents response: " + repr( ONOS4Intents ) )
            main.log.warn( "ONOS5 intents response: " + repr( ONOS5Intents ) )
            main.log.warn( "ONOS6 intents response: " + repr( ONOS6Intents ) )
            main.log.warn( "ONOS7 intents response: " + repr( ONOS7Intents ) )
        elif ONOS1Intents == ONOS2Intents\
                and ONOS1Intents == ONOS3Intents\
                and ONOS1Intents == ONOS4Intents\
                and ONOS1Intents == ONOS5Intents\
                and ONOS1Intents == ONOS6Intents\
                and ONOS1Intents == ONOS7Intents:
            intentState = ONOS1Intents
            intentCheck = main.TRUE
            main.log.report( "Intents are consistent across all ONOS nodes" )
        else:
            main.log.warn(
                "ONOS1 intents: ",
                json.dumps(
                    json.loads( ONOS1Intents ),
                    sort_keys=True,
                    indent=4,
                    separators=(
                        ',',
                        ': ' ) ) )
            main.log.warn(
                "ONOS2 intents: ",
                json.dumps(
                    json.loads( ONOS2Intents ),
                    sort_keys=True,
                    indent=4,
                    separators=(
                        ',',
                        ': ' ) ) )
            main.log.warn(
                "ONOS3 intents: ",
                json.dumps(
                    json.loads( ONOS3Intents ),
                    sort_keys=True,
                    indent=4,
                    separators=(
                        ',',
                        ': ' ) ) )
            main.log.warn(
                "ONOS4 intents: ",
                json.dumps(
                    json.loads( ONOS4Intents ),
                    sort_keys=True,
                    indent=4,
                    separators=(
                        ',',
                        ': ' ) ) )
            main.log.warn(
                "ONOS5 intents: ",
                json.dumps(
                    json.loads( ONOS5Intents ),
                    sort_keys=True,
                    indent=4,
                    separators=(
                        ',',
                        ': ' ) ) )
            main.log.warn(
                "ONOS6 intents: ",
                json.dumps(
                    json.loads( ONOS6Intents ),
                    sort_keys=True,
                    indent=4,
                    separators=(
                        ',',
                        ': ' ) ) )
            main.log.warn(
                "ONOS7 intents: ",
                json.dumps(
                    json.loads( ONOS7Intents ),
                    sort_keys=True,
                    indent=4,
                    separators=(
                        ',',
                        ': ' ) ) )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=intentCheck,
            onpass="Intents are consistent across all ONOS nodes",
            onfail="ONOS nodes have different views of intents" )

        main.step( "Get the flows from each controller" )
        global flowState
        flowState = []
        flowCheck = main.FALSE
        try:
            ONOS1Flows = main.ONOScli1.flows( jsonFormat=True )
            ONOS2Flows = main.ONOScli2.flows( jsonFormat=True )
            ONOS3Flows = main.ONOScli3.flows( jsonFormat=True )
            ONOS4Flows = main.ONOScli4.flows( jsonFormat=True )
            ONOS5Flows = main.ONOScli5.flows( jsonFormat=True )
            ONOS6Flows = main.ONOScli6.flows( jsonFormat=True )
            ONOS7Flows = main.ONOScli7.flows( jsonFormat=True )
            assert ONOS1Flows, "ONOS1 Flows should not be empty"
            assert ONOS2Flows, "ONOS2 Flows should not be empty"
            assert ONOS3Flows, "ONOS3 Flows should not be empty"
            assert ONOS4Flows, "ONOS4 Flows should not be empty"
            assert ONOS5Flows, "ONOS5 Flows should not be empty"
            assert ONOS6Flows, "ONOS6 Flows should not be empty"
            assert ONOS7Flows, "ONOS7 Flows should not be empty"
            assert "Error" not in ONOS1Flows, "ONOS1 Flows contains 'Error'"
            assert "Error" not in ONOS2Flows, "ONOS2 Flows contains 'Error'"
            assert "Error" not in ONOS3Flows, "ONOS3 Flows contains 'Error'"
            assert "Error" not in ONOS4Flows, "ONOS4 Flows contains 'Error'"
            assert "Error" not in ONOS5Flows, "ONOS5 Flows contains 'Error'"
            assert "Error" not in ONOS6Flows, "ONOS6 Flows contains 'Error'"
            assert "Error" not in ONOS7Flows, "ONOS7 Flows contains 'Error'"
            ONOS1FlowsJson = json.loads( ONOS1Flows )
            ONOS2FlowsJson = json.loads( ONOS2Flows )
            ONOS3FlowsJson = json.loads( ONOS3Flows )
            ONOS4FlowsJson = json.loads( ONOS4Flows )
            ONOS5FlowsJson = json.loads( ONOS5Flows )
            ONOS6FlowsJson = json.loads( ONOS6Flows )
            ONOS7FlowsJson = json.loads( ONOS7Flows )
        except ( ValueError, AssertionError ):  # From json.loads, or asserts
            main.log.exception( "One or more 'flows' responses from " +
                                "ONOS couldn't be decoded." )
            main.log.warn( "ONOS1 flows repsponse: " + ONOS1Flows )
            main.log.warn( "ONOS2 flows repsponse: " + ONOS2Flows )
            main.log.warn( "ONOS3 flows repsponse: " + ONOS3Flows )
            main.log.warn( "ONOS4 flows repsponse: " + ONOS4Flows )
            main.log.warn( "ONOS5 flows repsponse: " + ONOS5Flows )
            main.log.warn( "ONOS6 flows repsponse: " + ONOS6Flows )
            main.log.warn( "ONOS7 flows repsponse: " + ONOS7Flows )
        else:  # No exceptions
            if len( ONOS1FlowsJson ) == len( ONOS2FlowsJson )\
                    and len( ONOS1FlowsJson ) == len( ONOS3FlowsJson )\
                    and len( ONOS1FlowsJson ) == len( ONOS4FlowsJson )\
                    and len( ONOS1FlowsJson ) == len( ONOS5FlowsJson )\
                    and len( ONOS1FlowsJson ) == len( ONOS6FlowsJson )\
                    and len( ONOS1FlowsJson ) == len( ONOS7FlowsJson ):
                # TODO: Do a better check, maybe compare flows on switches?
                # NOTE Possible issue with this not always being set?
                flowState = ONOS1Flows
                flowCheck = main.TRUE
                main.log.report( "Flow count is consistent across all" +
                                 " ONOS nodes" )
            else:
                main.log.warn( "ONOS1 flows: " +
                               json.dumps( ONOS1FlowsJson, sort_keys=True,
                                           indent=4,
                                           separators=( ',', ': ' ) ) )
                main.log.warn( "ONOS2 flows: " +
                               json.dumps( ONOS2FlowsJson, sort_keys=True,
                                           indent=4,
                                           separators=( ',', ': ' ) ) )
                main.log.warn( "ONOS3 flows: " +
                               json.dumps( ONOS3FlowsJson, sort_keys=True,
                                           indent=4,
                                           separators=( ',', ': ' ) ) )
                main.log.warn( "ONOS4 flows: " +
                               json.dumps( ONOS4FlowsJson, sort_keys=True,
                                           indent=4,
                                           separators=( ',', ': ' ) ) )
                main.log.warn( "ONOS5 flows: " +
                               json.dumps( ONOS5FlowsJson, sort_keys=True,
                                           indent=4,
                                           separators=( ',', ': ' ) ) )
                main.log.warn( "ONOS6 flows: " +
                               json.dumps( ONOS6FlowsJson, sort_keys=True,
                                           indent=4,
                                           separators=( ',', ': ' ) ) )
                main.log.warn( "ONOS7 flows: " +
                               json.dumps( ONOS7FlowsJson, sort_keys=True,
                                           indent=4,
                                           separators=( ',', ': ' ) ) )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=flowCheck,
            onpass="The flow count is consistent across all ONOS nodes",
            onfail="ONOS nodes have different flow counts" )

        main.step( "Get the OF Table entries" )
        global flows
        flows = []
        for i in range( 1, 29 ):
            flows.append( main.Mininet2.getFlowTable( 1.3, "s" + str( i ) ) )
        if flowCheck == main.FALSE:
            for table in flows:
                main.log.warn( table )
        # TODO: Compare switch flow tables with ONOS flow tables

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
        MNTopo = TestONTopology(
            main.Mininet1,
            ctrls )  # can also add Intent API info for intent operations

        main.step( "Collecting topology information from ONOS" )
        devices = []
        devices.append( main.ONOScli1.devices() )
        devices.append( main.ONOScli2.devices() )
        devices.append( main.ONOScli3.devices() )
        devices.append( main.ONOScli4.devices() )
        devices.append( main.ONOScli5.devices() )
        devices.append( main.ONOScli6.devices() )
        devices.append( main.ONOScli7.devices() )
        hosts = []
        hosts.append( json.loads( main.ONOScli1.hosts() ) )
        hosts.append( json.loads( main.ONOScli2.hosts() ) )
        hosts.append( json.loads( main.ONOScli3.hosts() ) )
        hosts.append( json.loads( main.ONOScli4.hosts() ) )
        hosts.append( json.loads( main.ONOScli5.hosts() ) )
        hosts.append( json.loads( main.ONOScli6.hosts() ) )
        hosts.append( json.loads( main.ONOScli7.hosts() ) )
        ports = []
        ports.append( main.ONOScli1.ports() )
        ports.append( main.ONOScli2.ports() )
        ports.append( main.ONOScli3.ports() )
        ports.append( main.ONOScli4.ports() )
        ports.append( main.ONOScli5.ports() )
        ports.append( main.ONOScli6.ports() )
        ports.append( main.ONOScli7.ports() )
        links = []
        links.append( main.ONOScli1.links() )
        links.append( main.ONOScli2.links() )
        links.append( main.ONOScli3.links() )
        links.append( main.ONOScli4.links() )
        links.append( main.ONOScli5.links() )
        links.append( main.ONOScli6.links() )
        links.append( main.ONOScli7.links() )
        clusters = []
        clusters.append( main.ONOScli1.clusters() )
        clusters.append( main.ONOScli2.clusters() )
        clusters.append( main.ONOScli3.clusters() )
        clusters.append( main.ONOScli4.clusters() )
        clusters.append( main.ONOScli5.clusters() )
        clusters.append( main.ONOScli6.clusters() )
        clusters.append( main.ONOScli7.clusters() )
        # Compare json objects for hosts and dataplane clusters

        # hosts
        consistentHostsResult = main.TRUE
        for controller in range( len( hosts ) ):
            controllerStr = str( controller + 1 )
            if "Error" not in hosts[ controller ]:
                if hosts[ controller ] == hosts[ 0 ]:
                    continue
                else:  # hosts not consistent
                    main.log.report( "hosts from ONOS" +
                                     controllerStr +
                                     " is inconsistent with ONOS1" )
                    main.log.warn( repr( hosts[ controller ] ) )
                    consistentHostsResult = main.FALSE

            else:
                main.log.report( "Error in getting ONOS hosts from ONOS" +
                                 controllerStr )
                consistentHostsResult = main.FALSE
                main.log.warn( "ONOS" + controllerStr +
                               " hosts response: " +
                               repr( hosts[ controller ] ) )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=consistentHostsResult,
            onpass="Hosts view is consistent across all ONOS nodes",
            onfail="ONOS nodes have different views of hosts" )

        ipResult = main.TRUE
        for controller in range( 0, len( hosts ) ):
            controllerStr = str( controller + 1 )
            for host in hosts[ controller ]:
                if host.get( 'ips', [] ) == []:
                    main.log.error(
                        "DEBUG:Error with host ips on controller" +
                        controllerStr + ": " + str( host ) )
                    ipResult = main.FALSE
        utilities.assert_equals(
            expect=main.TRUE,
            actual=ipResult,
            onpass="The ips of the hosts aren't empty",
            onfail="The ip of at least one host is missing" )

        # Strongly connected clusters of devices
        consistentClustersResult = main.TRUE
        for controller in range( len( clusters ) ):
            if "Error" not in clusters[ controller ]:
                if clusters[ controller ] == clusters[ 0 ]:
                    continue
                else:  # clusters not consistent
                    main.log.report( "clusters from ONOS" +
                                     controllerStr +
                                     " is inconsistent with ONOS1" )
                    consistentClustersResult = main.FALSE

            else:
                main.log.report( "Error in getting dataplane clusters " +
                                 "from ONOS" + controllerStr )
                consistentClustersResult = main.FALSE
                main.log.warn( "ONOS" + controllerStr +
                               " clusters response: " +
                               repr( clusters[ controller ] ) )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=consistentClustersResult,
            onpass="Clusters view is consistent across all ONOS nodes",
            onfail="ONOS nodes have different views of clusters" )
        # there should always only be one cluster
        numClusters = len( json.loads( clusters[ 0 ] ) )
        clusterResults = main.FALSE
        if numClusters == 1:
            clusterResults = main.TRUE
        utilities.assert_equals(
            expect=1,
            actual=numClusters,
            onpass="ONOS shows 1 SCC",
            onfail="ONOS shows " + str( numClusters ) + " SCCs" )

        main.step( "Comparing ONOS topology to MN" )
        devicesResults = main.TRUE
        portsResults = main.TRUE
        linksResults = main.TRUE
        for controller in range( numControllers ):
            controllerStr = str( controller + 1 )
            if devices[ controller ] or "Error" not in devices[ controller ]:
                currentDevicesResult = main.Mininet1.compareSwitches(
                    MNTopo,
                    json.loads(
                        devices[ controller ] ) )
            else:
                currentDevicesResult = main.FALSE
            utilities.assert_equals( expect=main.TRUE,
                                     actual=currentDevicesResult,
                                     onpass="ONOS" + controllerStr +
                                     " Switches view is correct",
                                     onfail="ONOS" + controllerStr +
                                     " Switches view is incorrect" )

            if ports[ controller ] or "Error" not in ports[ controller ]:
                currentPortsResult = main.Mininet1.comparePorts(
                    MNTopo,
                    json.loads(
                        ports[ controller ] ) )
            else:
                currentPortsResult = main.FALSE
            utilities.assert_equals( expect=main.TRUE,
                                     actual=currentPortsResult,
                                     onpass="ONOS" + controllerStr +
                                     " ports view is correct",
                                     onfail="ONOS" + controllerStr +
                                     " ports view is incorrect" )

            if links[ controller ] or "Error" not in links[ controller ]:
                currentLinksResult = main.Mininet1.compareLinks(
                    MNTopo,
                    json.loads(
                        links[ controller ] ) )
            else:
                currentLinksResult = main.FALSE
            utilities.assert_equals( expect=main.TRUE,
                                     actual=currentLinksResult,
                                     onpass="ONOS" + controllerStr +
                                     " links view is correct",
                                     onfail="ONOS" + controllerStr +
                                     " links view is incorrect" )

            devicesResults = devicesResults and currentDevicesResult
            portsResults = portsResults and currentPortsResult
            linksResults = linksResults and currentLinksResult

        topoResult = devicesResults and portsResults and linksResults\
                     and consistentHostsResult and consistentClustersResult\
                     and clusterResults and ipResult
        utilities.assert_equals( expect=main.TRUE, actual=topoResult,
                                 onpass="Topology Check Test successful",
                                 onfail="Topology Check Test NOT successful" )

        finalAssert = main.TRUE
        finalAssert = finalAssert and topoResult and flowCheck \
                      and intentCheck and consistentMastership and rolesNotNull
        utilities.assert_equals( expect=main.TRUE, actual=finalAssert,
                                 onpass="State check successful",
                                 onfail="State check NOT successful" )

    def CASE6( self, main ):
        """
        The Failure case.
        """
        import time
        main.log.report( "Killing 3 ONOS nodes" )
        main.log.case( "Restart minority of ONOS nodes" )
        # TODO: Randomize these nodes
        main.ONOSbench.onosKill( ONOS1Ip )
        time.sleep( 10 )
        main.ONOSbench.onosKill( ONOS2Ip )
        time.sleep( 10 )
        main.ONOSbench.onosKill( ONOS3Ip )

        main.step( "Checking if ONOS is up yet" )
        count = 0
        onosIsupResult = main.FALSE
        while onosIsupResult == main.FALSE and count < 10:
            onos1Isup = main.ONOSbench.isup( ONOS1Ip )
            onos2Isup = main.ONOSbench.isup( ONOS2Ip )
            onos3Isup = main.ONOSbench.isup( ONOS3Ip )
            onosIsupResult = onos1Isup and onos2Isup and onos3Isup
            count = count + 1
        # TODO: if it becomes an issue, we can retry this step  a few times

        cliResult1 = main.ONOScli1.startOnosCli( ONOS1Ip )
        cliResult2 = main.ONOScli2.startOnosCli( ONOS2Ip )
        cliResult3 = main.ONOScli3.startOnosCli( ONOS3Ip )
        cliResults = cliResult1 and cliResult2 and cliResult3

        # Grab the time of restart so we chan check how long the gossip
        # protocol has had time to work
        main.restartTime = time.time()
        caseResults = main.TRUE and onosIsupResult and cliResults
        utilities.assert_equals( expect=main.TRUE, actual=caseResults,
                                 onpass="ONOS restart successful",
                                 onfail="ONOS restart NOT successful" )

    def CASE7( self, main ):
        """
        Check state after ONOS failure
        """
        import json
        main.case( "Running ONOS Constant State Tests" )

        # Assert that each device has a master
        ONOS1MasterNotNull = main.ONOScli1.rolesNotNull()
        ONOS2MasterNotNull = main.ONOScli2.rolesNotNull()
        ONOS3MasterNotNull = main.ONOScli3.rolesNotNull()
        ONOS4MasterNotNull = main.ONOScli4.rolesNotNull()
        ONOS5MasterNotNull = main.ONOScli5.rolesNotNull()
        ONOS6MasterNotNull = main.ONOScli6.rolesNotNull()
        ONOS7MasterNotNull = main.ONOScli7.rolesNotNull()
        rolesNotNull = ONOS1MasterNotNull and ONOS2MasterNotNull and\
            ONOS3MasterNotNull and ONOS4MasterNotNull and\
            ONOS5MasterNotNull and ONOS6MasterNotNull and\
            ONOS7MasterNotNull
        utilities.assert_equals(
            expect=main.TRUE,
            actual=rolesNotNull,
            onpass="Each device has a master",
            onfail="Some devices don't have a master assigned" )

        main.step( "Check if switch roles are consistent across all nodes" )
        ONOS1Mastership = main.ONOScli1.roles()
        ONOS2Mastership = main.ONOScli2.roles()
        ONOS3Mastership = main.ONOScli3.roles()
        ONOS4Mastership = main.ONOScli4.roles()
        ONOS5Mastership = main.ONOScli5.roles()
        ONOS6Mastership = main.ONOScli6.roles()
        ONOS7Mastership = main.ONOScli7.roles()
        if "Error" in ONOS1Mastership or not ONOS1Mastership\
                or "Error" in ONOS2Mastership or not ONOS2Mastership\
                or "Error" in ONOS3Mastership or not ONOS3Mastership\
                or "Error" in ONOS4Mastership or not ONOS4Mastership\
                or "Error" in ONOS5Mastership or not ONOS5Mastership\
                or "Error" in ONOS6Mastership or not ONOS6Mastership\
                or "Error" in ONOS7Mastership or not ONOS7Mastership:
            main.log.error( "Error in getting ONOS mastership" )
            main.log.warn( "ONOS1 mastership response: " +
                           repr( ONOS1Mastership ) )
            main.log.warn( "ONOS2 mastership response: " +
                           repr( ONOS2Mastership ) )
            main.log.warn( "ONOS3 mastership response: " +
                           repr( ONOS3Mastership ) )
            main.log.warn( "ONOS4 mastership response: " +
                           repr( ONOS4Mastership ) )
            main.log.warn( "ONOS5 mastership response: " +
                           repr( ONOS5Mastership ) )
            main.log.warn( "ONOS6 mastership response: " +
                           repr( ONOS6Mastership ) )
            main.log.warn( "ONOS7 mastership response: " +
                           repr( ONOS7Mastership ) )
            consistentMastership = main.FALSE
        elif ONOS1Mastership == ONOS2Mastership\
                and ONOS1Mastership == ONOS3Mastership\
                and ONOS1Mastership == ONOS4Mastership\
                and ONOS1Mastership == ONOS5Mastership\
                and ONOS1Mastership == ONOS6Mastership\
                and ONOS1Mastership == ONOS7Mastership:
            consistentMastership = main.TRUE
            main.log.report(
                "Switch roles are consistent across all ONOS nodes" )
        else:
            main.log.warn( "ONOS1 roles: ", json.dumps(
                json.loads( ONOS1Mastership ), sort_keys=True, indent=4,
                separators=( ',', ': ' ) ) )
            main.log.warn( "ONOS2 roles: ", json.dumps(
                json.loads( ONOS2Mastership ), sort_keys=True, indent=4,
                separators=( ',', ': ' ) ) )
            main.log.warn( "ONOS3 roles: ", json.dumps(
                json.loads( ONOS3Mastership ), sort_keys=True, indent=4,
                separators=( ',', ': ' ) ) )
            main.log.warn( "ONOS4 roles: ", json.dumps(
                json.loads( ONOS4Mastership ), sort_keys=True, indent=4,
                separators=( ',', ': ' ) ) )
            main.log.warn( "ONOS5 roles: ", json.dumps(
                json.loads( ONOS5Mastership ), sort_keys=True, indent=4,
                separators=( ',', ': ' ) ) )
            main.log.warn( "ONOS6 roles: ", json.dumps(
                json.loads( ONOS6Mastership ), sort_keys=True, indent=4,
                separators=( ',', ': ' ) ) )
            main.log.warn( "ONOS7 roles: ", json.dumps(
                json.loads( ONOS7Mastership ), sort_keys=True, indent=4,
                separators=( ',', ': ' ) ) )
            consistentMastership = main.FALSE
        utilities.assert_equals(
            expect=main.TRUE,
            actual=consistentMastership,
            onpass="Switch roles are consistent across all ONOS nodes",
            onfail="ONOS nodes have different views of switch roles" )

        description2 = "Compare switch roles from before failure"
        main.step( description2 )

        currentJson = json.loads( ONOS1Mastership )
        oldJson = json.loads( mastershipState )
        mastershipCheck = main.TRUE
        for i in range( 1, 29 ):
            switchDPID = str(
                main.Mininet1.getSwitchDPID(
                    switch="s" +
                    str( i ) ) )

            current = [ switch[ 'master' ] for switch in currentJson
                        if switchDPID in switch[ 'id' ] ]
            old = [ switch[ 'master' ] for switch in oldJson
                    if switchDPID in switch[ 'id' ] ]
            if current == old:
                mastershipCheck = mastershipCheck and main.TRUE
            else:
                main.log.warn( "Mastership of switch %s changed" % switchDPID )
                mastershipCheck = main.FALSE
        if mastershipCheck == main.TRUE:
            main.log.report( "Mastership of Switches was not changed" )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=mastershipCheck,
            onpass="Mastership of Switches was not changed",
            onfail="Mastership of some switches changed" )
        # NOTE: we expect mastership to change on controller failure
        mastershipCheck = consistentMastership

        main.step( "Get the intents and compare across all nodes" )
        ONOS1Intents = main.ONOScli1.intents( jsonFormat=True )
        ONOS2Intents = main.ONOScli2.intents( jsonFormat=True )
        ONOS3Intents = main.ONOScli3.intents( jsonFormat=True )
        ONOS4Intents = main.ONOScli4.intents( jsonFormat=True )
        ONOS5Intents = main.ONOScli5.intents( jsonFormat=True )
        ONOS6Intents = main.ONOScli6.intents( jsonFormat=True )
        ONOS7Intents = main.ONOScli7.intents( jsonFormat=True )
        intentCheck = main.FALSE
        if "Error" in ONOS1Intents or not ONOS1Intents\
                or "Error" in ONOS2Intents or not ONOS2Intents\
                or "Error" in ONOS3Intents or not ONOS3Intents\
                or "Error" in ONOS4Intents or not ONOS4Intents\
                or "Error" in ONOS5Intents or not ONOS5Intents\
                or "Error" in ONOS6Intents or not ONOS6Intents\
                or "Error" in ONOS7Intents or not ONOS7Intents:
            main.log.report( "Error in getting ONOS intents" )
            main.log.warn( "ONOS1 intents response: " + repr( ONOS1Intents ) )
            main.log.warn( "ONOS2 intents response: " + repr( ONOS2Intents ) )
            main.log.warn( "ONOS3 intents response: " + repr( ONOS3Intents ) )
            main.log.warn( "ONOS4 intents response: " + repr( ONOS4Intents ) )
            main.log.warn( "ONOS5 intents response: " + repr( ONOS5Intents ) )
            main.log.warn( "ONOS6 intents response: " + repr( ONOS6Intents ) )
            main.log.warn( "ONOS7 intents response: " + repr( ONOS7Intents ) )
        elif ONOS1Intents == ONOS2Intents\
                and ONOS1Intents == ONOS3Intents\
                and ONOS1Intents == ONOS4Intents\
                and ONOS1Intents == ONOS5Intents\
                and ONOS1Intents == ONOS6Intents\
                and ONOS1Intents == ONOS7Intents:
            intentCheck = main.TRUE
            main.log.report( "Intents are consistent across all ONOS nodes" )
        else:
            main.log.warn( "ONOS1 intents: " )
            print json.dumps( json.loads( ONOS1Intents ), sort_keys=True,
                              indent=4, separators=( ',', ': ' ) )
            main.log.warn( "ONOS2 intents: " )
            print json.dumps( json.loads( ONOS2Intents ), sort_keys=True,
                              indent=4, separators=( ',', ': ' ) )
            main.log.warn( "ONOS3 intents: " )
            print json.dumps( json.loads( ONOS3Intents ), sort_keys=True,
                              indent=4, separators=( ',', ': ' ) )
            main.log.warn( "ONOS4 intents: " )
            print json.dumps( json.loads( ONOS4Intents ), sort_keys=True,
                              indent=4, separators=( ',', ': ' ) )
            main.log.warn( "ONOS5 intents: " )
            print json.dumps( json.loads( ONOS5Intents ), sort_keys=True,
                              indent=4, separators=( ',', ': ' ) )
            main.log.warn( "ONOS6 intents: " )
            print json.dumps( json.loads( ONOS6Intents ), sort_keys=True,
                              indent=4, separators=( ',', ': ' ) )
            main.log.warn( "ONOS7 intents: " )
            print json.dumps( json.loads( ONOS7Intents ), sort_keys=True,
                              indent=4, separators=( ',', ': ' ) )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=intentCheck,
            onpass="Intents are consistent across all ONOS nodes",
            onfail="ONOS nodes have different views of intents" )
        # Print the intent states
        intents = []
        intents.append( ONOS1Intents )
        intents.append( ONOS2Intents )
        intents.append( ONOS3Intents )
        intents.append( ONOS4Intents )
        intents.append( ONOS5Intents )
        intents.append( ONOS6Intents )
        intents.append( ONOS7Intents )
        intentStates = []
        for node in intents:  # Iter through ONOS nodes
            nodeStates = []
            # Iter through intents of a node
            for intent in json.loads( node ):
                nodeStates.append( intent[ 'state' ] )
            intentStates.append( nodeStates )
            out = [ (i, nodeStates.count( i ) ) for i in set( nodeStates ) ]
            main.log.info( dict( out ) )

        # NOTE: Store has no durability, so intents are lost across system
        #       restarts
        main.step( "Compare current intents with intents before the failure" )
        # NOTE: this requires case 5 to pass for intentState to be set.
        #      maybe we should stop the test if that fails?
        sameIntents = main.TRUE
        if intentState and intentState == ONOS1Intents:
            sameIntents = main.TRUE
            main.log.report( "Intents are consistent with before failure" )
        # TODO: possibly the states have changed? we may need to figure out
        # what the aceptable states are
        else:
            try:
                main.log.warn( "ONOS1 intents: " )
                print json.dumps( json.loads( ONOS1Intents ),
                                  sort_keys=True, indent=4,
                                  separators=( ',', ': ' ) )
            except:
                pass
            sameIntents = main.FALSE
        utilities.assert_equals(
            expect=main.TRUE,
            actual=sameIntents,
            onpass="Intents are consistent with before failure",
            onfail="The Intents changed during failure" )
        intentCheck = intentCheck and sameIntents

        main.step( "Get the OF Table entries and compare to before " +
                   "component failure" )
        FlowTables = main.TRUE
        flows2 = []
        for i in range( 28 ):
            main.log.info( "Checking flow table on s" + str( i + 1 ) )
            tmpFlows = main.Mininet2.getFlowTable( 1.3, "s" + str( i + 1 ) )
            flows2.append( tmpFlows )
            tempResult = main.Mininet2.flowComp(
                flow1=flows[ i ],
                flow2=tmpFlows )
            FlowTables = FlowTables and tempResult
            if FlowTables == main.FALSE:
                main.log.info( "Differences in flow table for switch: s" +
                               str( i + 1 ) )
        if FlowTables == main.TRUE:
            main.log.report( "No changes were found in the flow tables" )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=FlowTables,
            onpass="No changes were found in the flow tables",
            onfail="Changes were found in the flow tables" )

        main.step( "Check the continuous pings to ensure that no packets " +
                   "were dropped during component failure" )
        # FIXME: This check is always failing. Investigate cause
        # NOTE:  this may be something to do with file permsissions
        #       or slight change in format
        main.Mininet2.pingKill(
            main.params[ 'TESTONUSER' ],
            main.params[ 'TESTONIP' ] )
        LossInPings = main.FALSE
        # NOTE: checkForLoss returns main.FALSE with 0% packet loss
        for i in range( 8, 18 ):
            main.log.info(
                "Checking for a loss in pings along flow from s" +
                str( i ) )
            LossInPings = main.Mininet2.checkForLoss(
                "/tmp/ping.h" +
                str( i ) ) or LossInPings
        if LossInPings == main.TRUE:
            main.log.info( "Loss in ping detected" )
        elif LossInPings == main.ERROR:
            main.log.info( "There are multiple mininet process running" )
        elif LossInPings == main.FALSE:
            main.log.info( "No Loss in the pings" )
            main.log.report( "No loss of dataplane connectivity" )
        utilities.assert_equals(
            expect=main.FALSE,
            actual=LossInPings,
            onpass="No Loss of connectivity",
            onfail="Loss of dataplane connectivity detected" )

        # Test of LeadershipElection
        leaderList = []
        leaderResult = main.TRUE
        for controller in range( 1, numControllers + 1 ):
            # loop through ONOScli handlers
            node = getattr( main, ( 'ONOScli' + str( controller ) ) )
            leaderN = node.electionTestLeader()
            leaderList.append( leaderN )
            if leaderN == main.FALSE:
                # error in  response
                main.log.report( "Something is wrong with " +
                                 "electionTestLeader function, check the" +
                                 " error logs" )
                leaderResult = main.FALSE
            elif leaderN is None:
                main.log.report( "ONOS" + str( controller ) +
                                 " shows no leader for the election-app was" +
                                 " elected after the old one died" )
                leaderResult = main.FALSE
            elif leaderN == ONOS1Ip or leaderN == ONOS2Ip or\
                    leaderN == ONOS3Ip:
                main.log.report( "ONOS" + str( controller ) +
                                 " shows " + str( leaderN ) +
                                 " as leader for the election-app, but it " +
                                 "was restarted" )
                leaderResult = main.FALSE
        if len( set( leaderList ) ) != 1:
            leaderResult = main.FALSE
            main.log.error(
                "Inconsistent view of leader for the election test app" )
            # TODO: print the list
        if leaderResult:
            main.log.report( "Leadership election tests passed( consistent " +
                             "view of leader across listeners and a new " +
                             "leader was re-elected if applicable )" )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=leaderResult,
            onpass="Leadership election passed",
            onfail="Something went wrong with Leadership election" )

        result = ( mastershipCheck and intentCheck and FlowTables and
                   ( not LossInPings ) and rolesNotNull and leaderResult )
        result = int( result )
        if result == main.TRUE:
            main.log.report( "Constant State Tests Passed" )
        utilities.assert_equals( expect=main.TRUE, actual=result,
                                 onpass="Constant State Tests Passed",
                                 onfail="Constant state tests failed" )

    def CASE8( self, main ):
        """
        Compare topo
        """
        import sys
        # FIXME add this path to params
        sys.path.append( "/home/admin/sts" )
        # assumes that sts is already in you PYTHONPATH
        from sts.topology.teston_topology import TestONTopology
        import json
        import time

        description = "Compare ONOS Topology view to Mininet topology"
        main.case( description )
        main.log.report( description )
        main.step( "Create TestONTopology object" )
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
        MNTopo = TestONTopology(
            main.Mininet1,
            ctrls )  # can also add Intent API info for intent operations

        main.step( "Comparing ONOS topology to MN" )
        devicesResults = main.TRUE
        portsResults = main.TRUE
        linksResults = main.TRUE
        hostsResults = main.TRUE
        topoResult = main.FALSE
        elapsed = 0
        count = 0
        main.step( "Collecting topology information from ONOS" )
        startTime = time.time()
        # Give time for Gossip to work
        while topoResult == main.FALSE and elapsed < 60:
            count = count + 1
            if count > 1:
                # TODO: Depricate STS usage
                MNTopo = TestONTopology( main.Mininet1, ctrls )
            cliStart = time.time()
            devices = []
            devices.append( main.ONOScli1.devices() )
            devices.append( main.ONOScli2.devices() )
            devices.append( main.ONOScli3.devices() )
            devices.append( main.ONOScli4.devices() )
            devices.append( main.ONOScli5.devices() )
            devices.append( main.ONOScli6.devices() )
            devices.append( main.ONOScli7.devices() )
            hosts = []
            hosts.append( json.loads( main.ONOScli1.hosts() ) )
            hosts.append( json.loads( main.ONOScli2.hosts() ) )
            hosts.append( json.loads( main.ONOScli3.hosts() ) )
            hosts.append( json.loads( main.ONOScli4.hosts() ) )
            hosts.append( json.loads( main.ONOScli5.hosts() ) )
            hosts.append( json.loads( main.ONOScli6.hosts() ) )
            hosts.append( json.loads( main.ONOScli7.hosts() ) )
            ipResult = main.TRUE
            for controller in range( 0, len( hosts ) ):
                controllerStr = str( controller + 1 )
                for host in hosts[ controller ]:
                    if host is None or host.get( 'ips', [] ) == []:
                        main.log.error(
                            "DEBUG:Error with host ips on controller" +
                            controllerStr + ": " + str( host ) )
                        ipResult = main.FALSE
            ports = []
            ports.append( main.ONOScli1.ports() )
            ports.append( main.ONOScli2.ports() )
            ports.append( main.ONOScli3.ports() )
            ports.append( main.ONOScli4.ports() )
            ports.append( main.ONOScli5.ports() )
            ports.append( main.ONOScli6.ports() )
            ports.append( main.ONOScli7.ports() )
            links = []
            links.append( main.ONOScli1.links() )
            links.append( main.ONOScli2.links() )
            links.append( main.ONOScli3.links() )
            links.append( main.ONOScli4.links() )
            links.append( main.ONOScli5.links() )
            links.append( main.ONOScli6.links() )
            links.append( main.ONOScli7.links() )
            clusters = []
            clusters.append( main.ONOScli1.clusters() )
            clusters.append( main.ONOScli2.clusters() )
            clusters.append( main.ONOScli3.clusters() )
            clusters.append( main.ONOScli4.clusters() )
            clusters.append( main.ONOScli5.clusters() )
            clusters.append( main.ONOScli6.clusters() )
            clusters.append( main.ONOScli7.clusters() )

            elapsed = time.time() - startTime
            cliTime = time.time() - cliStart
            print "CLI time: " + str( cliTime )

            for controller in range( numControllers ):
                controllerStr = str( controller + 1 )
                if devices[ controller ] or "Error" not in devices[
                        controller ]:
                    currentDevicesResult = main.Mininet1.compareSwitches(
                        MNTopo,
                        json.loads( devices[ controller ] ) )
                else:
                    currentDevicesResult = main.FALSE
                utilities.assert_equals( expect=main.TRUE,
                                         actual=currentDevicesResult,
                                         onpass="ONOS" + controllerStr +
                                         " Switches view is correct",
                                         onfail="ONOS" + controllerStr +
                                         " Switches view is incorrect" )

                if ports[ controller ] or "Error" not in ports[ controller ]:
                    currentPortsResult = main.Mininet1.comparePorts(
                        MNTopo,
                        json.loads( ports[ controller ] ) )
                else:
                    currentPortsResult = main.FALSE
                utilities.assert_equals( expect=main.TRUE,
                                         actual=currentPortsResult,
                                         onpass="ONOS" + controllerStr +
                                         " ports view is correct",
                                         onfail="ONOS" + controllerStr +
                                         " ports view is incorrect" )

                if links[ controller ] or "Error" not in links[ controller ]:
                    currentLinksResult = main.Mininet1.compareLinks(
                        MNTopo,
                        json.loads( links[ controller ] ) )
                else:
                    currentLinksResult = main.FALSE
                utilities.assert_equals( expect=main.TRUE,
                                         actual=currentLinksResult,
                                         onpass="ONOS" + controllerStr +
                                         " links view is correct",
                                         onfail="ONOS" + controllerStr +
                                         " links view is incorrect" )

                if hosts[ controller ] or "Error" not in hosts[ controller ]:
                    currentHostsResult = main.Mininet1.compareHosts(
                        MNTopo, hosts[ controller ] )
                else:
                    currentHostsResult = main.FALSE
                utilities.assert_equals( expect=main.TRUE,
                                         actual=currentHostsResult,
                                         onpass="ONOS" + controllerStr +
                                         " hosts exist in Mininet",
                                         onfail="ONOS" + controllerStr +
                                         " hosts don't match Mininet" )

                devicesResults = devicesResults and currentDevicesResult
                portsResults = portsResults and currentPortsResult
                linksResults = linksResults and currentLinksResult
                hostsResults = hostsResults and currentHostsResult

            # Compare json objects for hosts and dataplane clusters

            # hosts
            consistentHostsResult = main.TRUE
            for controller in range( len( hosts ) ):
                controllerStr = str( controller + 1 )
                if "Error" not in hosts[ controller ]:
                    if hosts[ controller ] == hosts[ 0 ]:
                        continue
                    else:  # hosts not consistent
                        main.log.report( "hosts from ONOS" + controllerStr +
                                         " is inconsistent with ONOS1" )
                        main.log.warn( repr( hosts[ controller ] ) )
                        consistentHostsResult = main.FALSE

                else:
                    main.log.report( "Error in getting ONOS hosts from ONOS" +
                                     controllerStr )
                    consistentHostsResult = main.FALSE
                    main.log.warn( "ONOS" + controllerStr +
                                   " hosts response: " +
                                   repr( hosts[ controller ] ) )
            utilities.assert_equals(
                expect=main.TRUE,
                actual=consistentHostsResult,
                onpass="Hosts view is consistent across all ONOS nodes",
                onfail="ONOS nodes have different views of hosts" )

            # Strongly connected clusters of devices
            consistentClustersResult = main.TRUE
            for controller in range( len( clusters ) ):
                controllerStr = str( controller + 1 )
                if "Error" not in clusters[ controller ]:
                    if clusters[ controller ] == clusters[ 0 ]:
                        continue
                    else:  # clusters not consistent
                        main.log.report( "clusters from ONOS" +
                                         controllerStr +
                                         " is inconsistent with ONOS1" )
                        consistentClustersResult = main.FALSE

                else:
                    main.log.report( "Error in getting dataplane clusters " +
                                     "from ONOS" + controllerStr )
                    consistentClustersResult = main.FALSE
                    main.log.warn( "ONOS" + controllerStr +
                                   " clusters response: " +
                                   repr( clusters[ controller ] ) )
            utilities.assert_equals(
                expect=main.TRUE,
                actual=consistentClustersResult,
                onpass="Clusters view is consistent across all ONOS nodes",
                onfail="ONOS nodes have different views of clusters" )
            # there should always only be one cluster
            numClusters = len( json.loads( clusters[ 0 ] ) )
            clusterResults = main.FALSE
            if numClusters == 1:
                clusterResults = main.TRUE
            utilities.assert_equals(
                expect=1,
                actual=numClusters,
                onpass="ONOS shows 1 SCC",
                onfail="ONOS shows " + str( numClusters ) + " SCCs" )

            topoResult = ( devicesResults and portsResults and linksResults
                           and hostsResults and consistentHostsResult
                           and consistentClustersResult and clusterResults
                           and ipResult )

        topoResult = topoResult and int( count <= 2 )
        note = "note it takes about " + str( int( cliTime ) ) + \
            " seconds for the test to make all the cli calls to fetch " +\
            "the topology from each ONOS instance"
        main.log.info(
            "Very crass estimate for topology discovery/convergence( " +
            str( note ) + " ): " + str( elapsed ) + " seconds, " +
            str( count ) + " tries" )
        utilities.assert_equals( expect=main.TRUE, actual=topoResult,
                                 onpass="Topology Check Test successful",
                                 onfail="Topology Check Test NOT successful" )
        if topoResult == main.TRUE:
            main.log.report( "ONOS topology view matches Mininet topology" )

    def CASE9( self, main ):
        """
        Link s3-s28 down
        """
        import time
        # NOTE: You should probably run a topology check after this

        linkSleep = float( main.params[ 'timers' ][ 'LinkDiscovery' ] )

        description = "Turn off a link to ensure that Link Discovery " +\
                      "is working properly"
        main.log.report( description )
        main.case( description )

        main.step( "Kill Link between s3 and s28" )
        LinkDown = main.Mininet1.link( END1="s3", END2="s28", OPTION="down" )
        main.log.info( "Waiting " + str( linkSleep ) +
                       " seconds for link down to be discovered" )
        time.sleep( linkSleep )
        utilities.assert_equals( expect=main.TRUE, actual=LinkDown,
                                 onpass="Link down succesful",
                                 onfail="Failed to bring link down" )
        # TODO do some sort of check here

    def CASE10( self, main ):
        """
        Link s3-s28 up
        """
        import time
        # NOTE: You should probably run a topology check after this

        linkSleep = float( main.params[ 'timers' ][ 'LinkDiscovery' ] )

        description = "Restore a link to ensure that Link Discovery is " + \
                      "working properly"
        main.log.report( description )
        main.case( description )

        main.step( "Bring link between s3 and s28 back up" )
        LinkUp = main.Mininet1.link( END1="s3", END2="s28", OPTION="up" )
        main.log.info( "Waiting " + str( linkSleep ) +
                       " seconds for link up to be discovered" )
        time.sleep( linkSleep )
        utilities.assert_equals( expect=main.TRUE, actual=LinkUp,
                                 onpass="Link up succesful",
                                 onfail="Failed to bring link up" )
        # TODO do some sort of check here

    def CASE11( self, main ):
        """
        Switch Down
        """
        # NOTE: You should probably run a topology check after this
        import time

        switchSleep = float( main.params[ 'timers' ][ 'SwitchDiscovery' ] )

        description = "Killing a switch to ensure it is discovered correctly"
        main.log.report( description )
        main.case( description )
        switch = main.params[ 'kill' ][ 'switch' ]
        switchDPID = main.params[ 'kill' ][ 'dpid' ]

        # TODO: Make this switch parameterizable
        main.step( "Kill " + switch )
        main.log.report( "Deleting " + switch )
        main.Mininet1.delSwitch( switch )
        main.log.info( "Waiting " + str( switchSleep ) +
                       " seconds for switch down to be discovered" )
        time.sleep( switchSleep )
        device = main.ONOScli1.getDevice( dpid=switchDPID )
        # Peek at the deleted switch
        main.log.warn( str( device ) )
        result = main.FALSE
        if device and device[ 'available' ] is False:
            result = main.TRUE
        utilities.assert_equals( expect=main.TRUE, actual=result,
                                 onpass="Kill switch succesful",
                                 onfail="Failed to kill switch?" )

    def CASE12( self, main ):
        """
        Switch Up
        """
        # NOTE: You should probably run a topology check after this
        import time

        switchSleep = float( main.params[ 'timers' ][ 'SwitchDiscovery' ] )
        switch = main.params[ 'kill' ][ 'switch' ]
        switchDPID = main.params[ 'kill' ][ 'dpid' ]
        links = main.params[ 'kill' ][ 'links' ].split()
        description = "Adding a switch to ensure it is discovered correctly"
        main.log.report( description )
        main.case( description )

        main.step( "Add back " + switch )
        main.log.report( "Adding back " + switch )
        main.Mininet1.addSwitch( switch, dpid=switchDPID )
        # TODO: New dpid or same? Ask Thomas?
        for peer in links:
            main.Mininet1.addLink( switch, peer )
        main.Mininet1.assignSwController( sw=switch.split( 's' )[ 1 ],
                                          count=numControllers,
                                          ip1=ONOS1Ip,
                                          port1=ONOS1Port,
                                          ip2=ONOS2Ip,
                                          port2=ONOS2Port,
                                          ip3=ONOS3Ip,
                                          port3=ONOS3Port,
                                          ip4=ONOS4Ip,
                                          port4=ONOS4Port,
                                          ip5=ONOS5Ip,
                                          port5=ONOS5Port,
                                          ip6=ONOS6Ip,
                                          port6=ONOS6Port,
                                          ip7=ONOS7Ip,
                                          port7=ONOS7Port )
        main.log.info( "Waiting " + str( switchSleep ) +
                       " seconds for switch up to be discovered" )
        time.sleep( switchSleep )
        device = main.ONOScli1.getDevice( dpid=switchDPID )
        # Peek at the deleted switch
        main.log.warn( str( device ) )
        result = main.FALSE
        if device and device[ 'available' ]:
            result = main.TRUE
        utilities.assert_equals( expect=main.TRUE, actual=result,
                                 onpass="add switch succesful",
                                 onfail="Failed to add switch?" )

    def CASE13( self, main ):
        """
        Clean up
        """
        import os
        import time
        # TODO: make use of this elsewhere
        ips = []
        ips.append( ONOS1Ip )
        ips.append( ONOS2Ip )
        ips.append( ONOS3Ip )
        ips.append( ONOS4Ip )
        ips.append( ONOS5Ip )
        ips.append( ONOS6Ip )
        ips.append( ONOS7Ip )

        # printing colors to terminal
        colors = {}
        colors[ 'cyan' ] = '\033[96m'
        colors[ 'purple' ] = '\033[95m'
        colors[ 'blue' ] = '\033[94m'
        colors[ 'green' ] = '\033[92m'
        colors[ 'yellow' ] = '\033[93m'
        colors[ 'red' ] = '\033[91m'
        colors[ 'end' ] = '\033[0m'
        description = "Test Cleanup"
        main.log.report( description )
        main.case( description )
        main.step( "Killing tcpdumps" )
        main.Mininet2.stopTcpdump()

        main.step( "Checking ONOS Logs for errors" )
        for i in range( 7 ):
            print colors[ 'purple' ] + "Checking logs for errors on " + \
                "ONOS" + str( i + 1 ) + ":" + colors[ 'end' ]
            print main.ONOSbench.checkLogs( ips[ i ] )

        main.step( "Copying MN pcap and ONOS log files to test station" )
        testname = main.TEST
        teststationUser = main.params[ 'TESTONUSER' ]
        teststationIP = main.params[ 'TESTONIP' ]
        # NOTE: MN Pcap file is being saved to ~/packet_captures
        #       scp this file as MN and TestON aren't necessarily the same vm
        # FIXME: scp
        # mn files
        # TODO: Load these from params
        # NOTE: must end in /
        logFolder = "/opt/onos/log/"
        logFiles = [ "karaf.log", "karaf.log.1" ]
        # NOTE: must end in /
        dstDir = "~/packet_captures/"
        for f in logFiles:
            for i in range( 7 ):
                main.ONOSbench.handle.sendline( "scp sdn@" + ips[ i ] + ":" +
                                                logFolder + f + " " +
                                                teststationUser + "@" +
                                                teststationIP + ":" +
                                                dstDir + str( testname ) +
                                                "-ONOS" + str( i + 1 ) + "-" +
                                                f )
                main.ONOSbench.handle.expect( "\$" )

        # std*.log's
        # NOTE: must end in /
        logFolder = "/opt/onos/var/"
        logFiles = [ "stderr.log", "stdout.log" ]
        # NOTE: must end in /
        dstDir = "~/packet_captures/"
        for f in logFiles:
            for i in range( 7 ):
                main.ONOSbench.handle.sendline( "scp sdn@" + ips[ i ] + ":" +
                                                logFolder + f + " " +
                                                teststationUser + "@" +
                                                teststationIP + ":" +
                                                dstDir + str( testname ) +
                                                "-ONOS" + str( i + 1 ) + "-" +
                                                f )
                main.ONOSbench.handle.expect( "\$" )
        # sleep so scp can finish
        time.sleep( 10 )
        main.Mininet1.stopNet()
        main.step( "Packing and rotating pcap archives" )
        os.system( "~/TestON/dependencies/rotate.sh " + str( testname ) )

        # TODO: actually check something here
        utilities.assert_equals( expect=main.TRUE, actual=main.TRUE,
                                 onpass="Test cleanup successful",
                                 onfail="Test cleanup NOT successful" )

    def CASE14( self, main ):
        """
        start election app on all onos nodes
        """
        leaderResult = main.TRUE
        # install app on onos 1
        main.log.info( "Install leadership election app" )
        main.ONOScli1.featureInstall( "onos-app-election" )
        # wait for election
        # check for leader
        leader = main.ONOScli1.electionTestLeader()
        # verify leader is ONOS1
        if leader == ONOS1Ip:
            # all is well
            pass
        elif leader is None:
            # No leader elected
            main.log.report( "No leader was elected" )
            leaderResult = main.FALSE
        elif leader == main.FALSE:
            # error in  response
            # TODO: add check for "Command not found:" in the driver, this
            # means the app isn't loaded
            main.log.report( "Something is wrong with electionTestLeader" +
                             " function, check the error logs" )
            leaderResult = main.FALSE
        else:
            # error in  response
            main.log.report(
                "Unexpected response from electionTestLeader function:'" +
                str( leader ) +
                "'" )
            leaderResult = main.FALSE

        # install on other nodes and check for leader.
        # Should be onos1 and each app should show the same leader
        for controller in range( 2, numControllers + 1 ):
            # loop through ONOScli handlers
            node = getattr( main, ( 'ONOScli' + str( controller ) ) )
            node.featureInstall( "onos-app-election" )
            leaderN = node.electionTestLeader()
            # verify leader is ONOS1
            if leaderN == ONOS1Ip:
                # all is well
                pass
            elif leaderN == main.FALSE:
                # error in  response
                # TODO: add check for "Command not found:" in the driver, this
                # means the app isn't loaded
                main.log.report( "Something is wrong with " +
                                 "electionTestLeader function, check the" +
                                 " error logs" )
                leaderResult = main.FALSE
            elif leader != leaderN:
                leaderResult = main.FALSE
                main.log.report( "ONOS" + str( controller ) + " sees " +
                                 str( leaderN ) +
                                 " as the leader of the election app. Leader" +
                                 " should be " +
                                 str( leader ) )
        if leaderResult:
            main.log.report( "Leadership election tests passed( consistent " +
                             "view of leader across listeners and a leader " +
                             "was elected )" )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=leaderResult,
            onpass="Leadership election passed",
            onfail="Something went wrong with Leadership election" )

    def CASE15( self, main ):
        """
        Check that Leadership Election is still functional
        """
        leaderResult = main.TRUE
        description = "Check that Leadership Election is still functional"
        main.log.report( description )
        main.case( description )
        main.step( "Find current leader and withdraw" )
        leader = main.ONOScli1.electionTestLeader()
        # TODO: do some sanity checking on leader before using it
        withdrawResult = main.FALSE
        if leader == ONOS1Ip:
            oldLeader = getattr( main, "ONOScli1" )
        elif leader == ONOS2Ip:
            oldLeader = getattr( main, "ONOScli2" )
        elif leader == ONOS3Ip:
            oldLeader = getattr( main, "ONOScli3" )
        elif leader == ONOS4Ip:
            oldLeader = getattr( main, "ONOScli4" )
        elif leader == ONOS5Ip:
            oldLeader = getattr( main, "ONOScli5" )
        elif leader == ONOS6Ip:
            oldLeader = getattr( main, "ONOScli6" )
        elif leader == ONOS7Ip:
            oldLeader = getattr( main, "ONOScli7" )
        elif leader is None or leader == main.FALSE:
            main.log.report(
                "Leader for the election app should be an ONOS node," +
                "instead got '" + str( leader ) + "'" )
            leaderResult = main.FALSE
            oldLeader = None
        else:
            main.log.error( "Leader election --- why am I HERE?!?")
        if oldLeader:
            withdrawResult = oldLeader.electionTestWithdraw()
        utilities.assert_equals(
            expect=main.TRUE,
            actual=withdrawResult,
            onpass="App was withdrawn from election",
            onfail="App was not withdrawn from election" )

        main.step( "Make sure new leader is elected" )
        leaderList = []
        for controller in range( 1, numControllers + 1 ):
            # loop through ONOScli handlers
            node = getattr( main, ( 'ONOScli' + str( controller ) ) )
            leaderList.append( node.electionTestLeader() )
        for leaderN in leaderList:
            if leaderN == leader:
                main.log.report(
                    "ONOS" + str( controller ) +
                    " still sees " + str( leader ) +
                    " as leader after they withdrew" )
                leaderResult = main.FALSE
            elif leaderN == main.FALSE:
                # error in  response
                # TODO: add check for "Command not found:" in the driver, this
                # means the app isn't loaded
                main.log.report( "Something is wrong with " +
                                 "electionTestLeader function, " +
                                 "check the error logs" )
                leaderResult = main.FALSE
        consistentLeader = main.FALSE
        if len( set( leaderList ) ) == 1:
            main.log.info( "Each Election-app sees '" +
                           str( leaderList[ 0 ] ) +
                           "' as the leader" )
            consistentLeader = main.TRUE
        else:
            main.log.report(
                "Inconsistent responses for leader of Election-app:" )
            for n in range( len( leaderList ) ):
                main.log.report( "ONOS" + str( n + 1 ) + " response: " +
                                 str( leaderList[ n ] ) )
        if leaderResult:
            main.log.report( "Leadership election tests passed( consistent " +
                             "view of leader across listeners and a new " +
                             "leader was elected when the old leader " +
                             "resigned )" )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=leaderResult,
            onpass="Leadership election passed",
            onfail="Something went wrong with Leadership election" )

        main.step( "Run for election on old leader( just so everyone " +
                   "is in the hat )" )
        if oldLeader:
            runResult = oldLeader.electionTestRun()
        else:
            runResult = main.FALSE
        utilities.assert_equals(
            expect=main.TRUE,
            actual=runResult,
            onpass="App re-ran for election",
            onfail="App failed to run for election" )
        if consistentLeader == main.TRUE:
            afterRun = main.ONOScli1.electionTestLeader()
            # verify leader didn't just change
            if afterRun == leaderList[ 0 ]:
                leaderResult = main.TRUE
            else:
                leaderResult = main.FALSE
        # TODO: assert on  run and withdraw results?

        utilities.assert_equals(
            expect=main.TRUE,
            actual=leaderResult,
            onpass="Leadership election passed",
            onfail="Something went wrong with Leadership election after " +
                   "the old leader re-ran for election" )
