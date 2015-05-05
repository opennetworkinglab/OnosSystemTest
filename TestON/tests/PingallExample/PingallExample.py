"""
Description: This test is an example of a simple single node ONOS test

List of test cases:
CASE1: Compile ONOS and push it to the test machine
CASE2: Assign mastership to controller
CASE3: Pingall
"""
class PingallExample:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        """
           CASE1 is to compile ONOS and push it to the test machines

           Startup sequence:
           git pull
           mvn clean install
           onos-package
           cell <name>
           onos-verify-cell
           onos-install -f
           onos-wait-for-start
        """
        desc = "ONOS Single node cluster restart HA test - initialization"
        main.log.report( desc )
        main.case( "Setting up test environment" )

        # load some vairables from the params file
        PULLCODE = False
        if main.params[ 'Git' ] == 'True':
            PULLCODE = True
        cellName = main.params[ 'ENV' ][ 'cellName' ]

        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]

        main.step( "Applying cell variable to environment" )
        cellResult = main.ONOSbench.setCell( cellName )
        verifyResult = main.ONOSbench.verifyCell()

        main.log.report( "Uninstalling ONOS" )
        main.ONOSbench.onosUninstall( ONOS1Ip )

        cleanInstallResult = main.TRUE
        gitPullResult = main.TRUE

        main.step( "Compiling the latest version of ONOS" )
        if PULLCODE:
            main.step( "Git checkout and pull master" )
            main.ONOSbench.gitCheckout( "master" )
            gitPullResult = main.ONOSbench.gitPull()

            main.step( "Using mvn clean & install" )
            cleanInstallResult = main.TRUE
            if gitPullResult == main.TRUE:
                cleanInstallResult = main.ONOSbench.cleanInstall()
            else:
                main.log.warn( "Did not pull new code so skipping mvn " +
                               "clean install" )
        main.ONOSbench.getVersion( report=True )

        cellResult = main.ONOSbench.setCell( cellName )
        verifyResult = main.ONOSbench.verifyCell()
        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.onosPackage()

        main.step( "Installing ONOS package" )
        onos1InstallResult = main.ONOSbench.onosInstall( options="-f",
                                                           node=ONOS1Ip )

        main.step( "Checking if ONOS is up yet" )
        for i in range( 2 ):
            onos1Isup = main.ONOSbench.isup( ONOS1Ip )
            if onos1Isup:
                break
        if not onos1Isup:
            main.log.report( "ONOS1 didn't start!" )

        # TODO: if it becomes an issue, we can retry this step  a few times

        cliResult = main.ONOScli1.startOnosCli( ONOS1Ip )

        case1Result = ( cleanInstallResult and packageResult and
                        cellResult and verifyResult and
                        onos1InstallResult and
                        onos1Isup and cliResult )

        utilities.assert_equals( expect=main.TRUE, actual=case1Result,
                                 onpass="Test startup successful",
                                 onfail="Test startup NOT successful" )

        if case1Result == main.FALSE:
            main.cleanup()
            main.exit()

        # Starting the mininet using the old way
        main.step( "Starting Mininet ..." )
        netIsUp = main.Mininet1.startNet()
        if netIsUp:
            main.log.info("Mininet CLI is up")
        else:
            main.log.info("Mininet CLI is down")

    def CASE2( self, main ):
        """
           Assign mastership to controller
        """
        import re

        main.log.report( "Assigning switches to controller" )
        main.case( "Assigning Controller" )
        main.step( "Assign switches to controller" )

        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]
        ONOS1Port = main.params[ 'CTRL' ][ 'port1' ]

        for i in range( 1, 14 ):
            main.Mininet1.assignSwController(
                sw=str( i ),
                ip1=ONOS1Ip,
                port1=ONOS1Port )

        mastershipCheck = main.TRUE
        for i in range( 1, 14 ):
            response = main.Mininet1.getSwController( "s" + str( i ) )
            try:
                main.log.info( str( response ) )
            except Exception:
                main.log.info( repr( response ) )
            if re.search( "tcp:" + ONOS1Ip, response ):
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

    def CASE3( self, main ):
        """
           Install forwarding app, Pingall and unistall the app
        """
        import time

        main.log.report( "Run Pingall" )
        main.case( "Run Pingall" )

        # install onos-app-fwd
        main.step( "Activate reactive forwarding app" )
        main.ONOScli1.activateApp( "org.onosproject.fwd" )

        # REACTIVE FWD test
        main.step( "Run the pingall command in Mininet" )
        pingResult = main.FALSE
        time1 = time.time()
        pingResult = main.Mininet1.pingall()
        time2 = time.time()
        main.log.info( "Time for pingall: %2f seconds" % ( time2 - time1 ) )

        # uninstall onos-app-fwd
        # main.step( "Deactivate reactive forwarding app" )
        #main.ONOScli1.deactivateApp( "org.onosproject.fwd" )

        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="All hosts are reachable",
                                 onfail="Some pings failed" )

    def CASE25( self, main ):
        """
           Activate fwd app
           Ping selected hosts
           Assign selected hosts vlans
           Ping to test vlans 
           Deactivate fwd app
        """
        import time

        main.log.report( "This testcase creates different vlan hosts " +
                         " and verifies that only hosts that belong " + 
                         " to the same vlan can ping each others")
        main.log.report( "___________________________________________________" )
        main.case( "Creating vlans and performing ping between hosts" )

        main.step( "Activate reactive forwarding app" )
        main.ONOScli1.activateApp( "org.onosproject.fwd" )

        main.step( "Activate reactive forwarding app" )
        main.ONOScli1.activateApp( "org.onosproject.fwd" )

        main.step( "Verify host pinging in Mininet before creating vlans" )
        source1V1 = main.params[ 'VPING' ][ 'source1V1' ]['vhost']
        source1V2 = main.params[ 'VPING' ][ 'source1V2' ]['vhost']
        source1Vnone = main.params[ 'VPING' ][ 'source1Vnone' ]['vhost']
        target1V1 = main.params[ 'VPING' ][ 'target1V1' ]['vhost']
        target2V1 = main.params[ 'VPING' ][ 'target2V1' ]['vhost']
        target1V2 = main.params[ 'VPING' ][ 'target1V2' ]['vhost']
        target1Vnone = main.params[ 'VPING' ][ 'target1Vnone' ]['vhost']

        targetIP1V1 = main.Mininet1.getIPAddress(target1V1)
        targetIP2V1 = main.Mininet1.getIPAddress(target2V1)
        targetIP1V2 =  main.Mininet1.getIPAddress(target1V2)
        targetIP1Vnone =  main.Mininet1.getIPAddress(target1Vnone)
        
        for i in range(0,2):
            ping1V1 = main.Mininet1.pingHost( src = source1V1, target = targetIP1V1)
            ping2V1 = main.Mininet1.pingHost( src = source1V1, target = targetIP2V1)
            ping1V2 = main.Mininet1.pingHost( src = source1V2, target = targetIP1V2)
            pingV1V2 = main.Mininet1.pingHost( src = source1V1, target = targetIP1V2)
            pingV2V1 = main.Mininet1.pingHost( src = source1V2, target = targetIP1V1)
            pingV1Vnone = main.Mininet1.pingHost ( src = source1V1, target = targetIP1Vnone)
            pingVnoneV2 =  main.Mininet1.pingHost ( src = source1Vnone, target = targetIP1V2)

        pingResultBeforeVlan = ping1V1 and ping2V1 and ping1V2 and pingV1V2 \
                             and pingV2V1 and pingV1Vnone and pingVnoneV2

        
        if pingResultBeforeVlan == main.TRUE:
            main.log.report("Ping succeeded before vlans are created")

            main.step( "Create vlan hosts in mininet" )
            v1Tag = main.params[ 'VTAGS' ][ 'tag1' ]
            v2Tag = main.params[ 'VTAGS' ][ 'tag2' ]        
            intfSource1V1 = source1V1 + "-" + main.params[ 'VPING' ][ 'source1V1' ][ 'vintf' ]
            intfSource1V2 = source1V2 + "-" + main.params[ 'VPING' ][ 'source1V2' ][ 'vintf' ]
            intfTarget1V1 = target1V1 + "-" + main.params[ 'VPING' ][ 'target1V1' ][ 'vintf' ]
            intfTarget2V1 = target2V1 + "-" + main.params[ 'VPING' ][ 'target2V1' ][ 'vintf' ]
            intfTarget1V2 = target1V2 + "-" + main.params[ 'VPING' ][ 'target1V2' ][ 'vintf' ]
        
            main.Mininet1.assignVLAN(source1V1, intfSource1V1, v1Tag)
            main.Mininet1.assignVLAN(target1V1, intfTarget1V1, v1Tag)
            main.Mininet1.assignVLAN(target2V1, intfTarget2V1, v1Tag)
            main.Mininet1.assignVLAN(source1V2, intfSource1V2, v2Tag)
            main.Mininet1.assignVLAN(target1V2, intfTarget1V2, v2Tag)
        
            main.step( "Verify host pinging in Mininet after creating vlans" )
        
            ping1V1 = main.Mininet1.pingHost( src = source1V1, target = targetIP1V1)
            ping2V1 = main.Mininet1.pingHost( src = source1V1, target = targetIP2V1)
            ping1V2 = main.Mininet1.pingHost( src = source1V2, target = targetIP1V2)
            pingV1V2 = main.Mininet1.pingHost( src = source1V1, target = targetIP1V2)
            pingV2V1 = main.Mininet1.pingHost( src = source1V2, target = targetIP1V1)
            pingV1Vnone = main.Mininet1.pingHost ( src = source1V1, target = targetIP1Vnone)
            pingVnoneV2 =  main.Mininet1.pingHost ( src = source1Vnone, target = targetIP1V2)


            pingExpectedTrue = ping1V1 and ping2V1 and ping1V2
            pingResultAfterVlan = pingExpectedTrue and not pingV1V2 \
                   and not pingV2V1 and not pingV1Vnone and not pingVnoneV2

            if pingResultAfterVlan == main.TRUE:
                main.log.report("Ping results are as expected after vlans are created")
                testCaseResult = main.TRUE
            if pingResultAfterVlan == main.FALSE:
                main.log.report("Ping results are not expected after vlans are created")
                testCaseResult = main.FALSE

            case25Result = testCaseResult
            utilities.assert_equals( expect=main.TRUE, actual=case25Result,
                                 onpass="Vlan verification is successfull",
                                 onfail="Vlan verification failed" )
        if pingResultBeforeVlan == main.FALSE:
            main.log.report("Ping failed before vlans are created")
            case25Result = main.FALSE
            utilities.assert_equals( expect=main.TRUE, actual=case25Result,
                                 onpass="Test case 25 can be verified",
                                 onfail="Test case 25 cannot be verified because " + 
                                   "there are ping failures before assigning host vlans" )
        
        main.step( "Deactivate reactive forwarding app" )
        main.ONOScli1.deactivateApp( "org.onosproject.fwd" )
            
    def CASE26( self, main ):
        """
           This test case verifies that hosts belonging to the same vlan,
           can ping each other with proactive forwarding (after adding host intent):
              - Deactivate app fwd
              - Assign vlan tag to selected hosts
              - Add host intent between the selected hosts
              - Ping the selected hosts to verify proactive forwarding with vlan hosts
        """
        import time

        main.log.report( "This testcase creates vlan hosts, " +
                         " add host intent, " + 
                         " then ping the hosts")
        main.log.report( "___________________________________________________" )
        main.case( "Creating vlans and performing ping between hosts" )

        main.step( "Deactivate reactive forwarding app" )
        main.ONOScli1.deactivateApp( "org.onosproject.fwd" )
        
        main.step( "Assign vlan hosts in mininet" )
        
        source1V1 = main.params[ 'VPING' ][ 'source1V1Int' ]['vhost']
        target1V1 = main.params[ 'VPING' ][ 'target1V1Int' ]['vhost']
 
        intfSource1V1 = source1V1 + "-" + main.params[ 'VPING' ][ 'source1V1Int' ][ 'vintf' ]
        intfTarget1V1 = target1V1 + "-" + main.params[ 'VPING' ][ 'target1V1Int' ][ 'vintf' ]
        
        vTag = main.params[ 'VTAGS' ][ 'tag3' ]        

        main.Mininet1.assignVLAN(source1V1, intfSource1V1, vTag)
        main.Mininet1.assignVLAN(target1V1, intfTarget1V1, vTag)
        
        main.step( "Add host intent" )
        mac1 = main.Mininet1.getMacAddress(source1V1)
        mac2 = main.Mininet1.getMacAddress(target1V1)
        id1 = mac1 + "/" + vTag
        id2 = mac2 + "/" + vTag
        hthIntentResult = main.ONOScli1.addHostIntent( id1 , id2 )
        if hthIntentResult:       
            main.step( "Ping hosts after installing host intent" )
            #time.sleep(10)
            targetIPV1 = main.Mininet1.getIPAddress(target1V1)
            for i in range(0,3):
                ping1V1 = main.Mininet1.pingHost( src = source1V1, target = targetIPV1)
            
            if ping1V1 == main.TRUE:
                main.log.report(" Vlan hosts can ping each other successfully "+
                                  " after add host intent.")
            
            if ping1V1 == main.FALSE:
                main.log.report("Vlan hosts failed to ping each other "+ 
                                 " after add host intent. ")
              
        else:
            main.log.report(" add host intent failed between vlan hosts ")

        case26Result = hthIntentResult and ping1V1
        utilities.assert_equals( expect=main.TRUE, actual=case26Result,
                                 onpass="Test case 26 is successfull",
                                 onfail="Test case 26 has failed" )

