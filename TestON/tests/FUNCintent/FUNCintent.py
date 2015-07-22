
# Testing the basic intent functionality of ONOS

import time
import json

class FUNCintent:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        import time
        import os
        import imp

        """
        - Construct tests variables
        - GIT ( optional )
            - Checkout ONOS master branch
            - Pull latest ONOS code
        - Building ONOS ( optional )
            - Install ONOS package
            - Build ONOS package
        """

        main.case( "Constructing test variables and building ONOS package" )
        main.step( "Constructing test variables" )
        stepResult = main.FALSE

        # Test variables
        main.testOnDirectory = os.path.dirname( os.getcwd ( ) )
        main.apps = main.params[ 'ENV' ][ 'cellApps' ]
        gitBranch = main.params[ 'GIT' ][ 'branch' ]
        main.dependencyPath = main.testOnDirectory + \
                              main.params[ 'DEPENDENCY' ][ 'path' ]
        main.topology = main.params[ 'DEPENDENCY' ][ 'topology' ]
        main.scale = ( main.params[ 'SCALE' ][ 'size' ] ).split( "," )
        main.maxNodes = int( main.ONOSbench.maxNodes )
        wrapperFile1 = main.params[ 'DEPENDENCY' ][ 'wrapper1' ]
        wrapperFile2 = main.params[ 'DEPENDENCY' ][ 'wrapper2' ]
        main.startUpSleep = int( main.params[ 'SLEEP' ][ 'startup' ] )
        main.checkIntentSleep = int( main.params[ 'SLEEP' ][ 'checkintent' ] )
        main.rerouteSleep = int( main.params[ 'SLEEP' ][ 'reroute' ] )
        gitPull = main.params[ 'GIT' ][ 'pull' ]
        main.numSwitch = int( main.params[ 'MININET' ][ 'switch' ] )
        main.numLinks = int( main.params[ 'MININET' ][ 'links' ] )
        main.cellData = {} # for creating cell file
        main.hostsData = {}
        main.CLIs = []
        main.ONOSip = []

        main.ONOSip = main.ONOSbench.getOnosIps()
        print main.ONOSip

        # Assigning ONOS cli handles to a list
        for i in range( 1,  main.maxNodes + 1 ):
            main.CLIs.append( getattr( main, 'ONOScli' + str( i ) ) )

        # -- INIT SECTION, ONLY RUNS ONCE -- #
        main.startUp = imp.load_source( wrapperFile1,
                                        main.dependencyPath +
                                        wrapperFile1 +
                                        ".py" )

        main.intentFunction = imp.load_source( wrapperFile2,
                                        main.dependencyPath +
                                        wrapperFile2 +
                                        ".py" )

        copyResult = main.ONOSbench.copyMininetFile( main.topology,
                                                     main.dependencyPath,
                                                     main.Mininet1.user_name,
                                                     main.Mininet1.ip_address )
        if main.CLIs:
            stepResult = main.TRUE
        else:
            main.log.error( "Did not properly created list of ONOS CLI handle" )
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
        main.ONOSbench.getVersion( report=True )

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

        # main.scale[ 0 ] determines the current number of ONOS controller
        main.numCtrls = int( main.scale[ 0 ] )

        main.case( "Starting up " + str( main.numCtrls ) +
                   " node(s) ONOS cluster" )

        #kill off all onos processes
        main.log.info( "Safety check, killing all ONOS processes" +
                       " before initiating enviornment setup" )

        for i in range( main.maxNodes ):
            main.ONOSbench.onosDie( main.ONOSip[ i ] )

        print "NODE COUNT = ", main.numCtrls

        tempOnosIp = []
        for i in range( main.numCtrls ):
            tempOnosIp.append( main.ONOSip[i] )

        main.ONOSbench.createCellFile( main.ONOSbench.ip_address, "temp", main.Mininet1.ip_address, main.apps, tempOnosIp )

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
        for i in range( main.numCtrls ):
            onosUninstallResult = onosUninstallResult and \
                    main.ONOSbench.onosUninstall( nodeIp=main.ONOSip[ i ] )
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
        stepResult = cliResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully start ONOS cli",
                                 onfail="Failed to start ONOS cli" )

        # Remove the first element in main.scale list
        main.scale.remove( main.scale[ 0 ] )

    def CASE9( self, main ):
        '''
            Report errors/warnings/exceptions
        '''
        main.log.info( "Error report: \n" )
        main.ONOSbench.logReport( globalONOSip[0],
                [ "INFO", "FOLLOWER", "WARN", "flow", "ERROR" , "Except" ],
                "s" )
        #main.ONOSbench.logReport( globalONOSip[1], [ "INFO" ], "d" )

    def CASE10( self, main ):
        """
            Start mininet
        """
        main.log.report( "Start Mininet topology" )
        main.log.case( "Start Mininet topology" )

        main.step( "Starting Mininet Topology" )
        topoResult = main.Mininet1.startNet( topoFile=main.dependencyPath +
                                                      main.topology )
        stepResult = topoResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully loaded topology",
                                 onfail="Failed to load topology" )
        # Exit if topology did not load properly
        if not topoResult:
            main.cleanup()
            main.exit()

    def CASE11( self, main ):
        """
            Start mininet
        """
        main.log.report( "Start Mininet topology with OF 1.3 switches" )
        main.log.case( "Start Mininet topology with OF 1.3 switches" )

        main.step( "Start Mininet topology with OF 1.3 switches" )
        args = "--switch ovs,protocols=OpenFlow13"
        topoResult = main.Mininet1.startNet( topoFile=main.dependencyPath +
                                                      main.topology,
                                             args=args )
        stepResult = topoResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully loaded topology",
                                 onfail="Failed to load topology" )
        # Exit if topology did not load properly
        if not topoResult:
            main.cleanup()
            main.exit()

    def CASE12( self, main ):
        """
            Assign mastership to controllers
        """
        import re

        main.case( "Assign switches to controllers" )
        main.step( "Assigning switches to controllers" )
        assignResult = main.TRUE
        switchList = []

        # Creates a list switch name, use getSwitch() function later...
        for i in range( 1, ( main.numSwitch + 1 ) ):
            switchList.append( 's' + str( i ) )

        tempONOSip = []
        for i in range( main.numCtrls ):
            tempONOSip.append( main.ONOSip[ i ] )

        assignResult = main.Mininet1.assignSwController( sw=switchList,
                                                         ip=tempONOSip,
                                                         port='6633' )
        if not assignResult:
            main.cleanup()
            main.exit()

        for i in range( 1, ( main.numSwitch + 1 ) ):
            response = main.Mininet1.getSwController( "s" + str( i ) )
            print( "Response is " + str( response ) )
            if re.search( "tcp:" + main.ONOSip[ 0 ], response ):
                assignResult = assignResult and main.TRUE
            else:
                assignResult = main.FALSE
        stepResult = assignResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully assigned switches" +
                                        "to controller",
                                 onfail="Failed to assign switches to " +
                                        "controller" )
    def CASE13( self, main ):
        """
            Discover all hosts and store its data to a dictionary
        """
        main.case( "Discover all hosts" )

        stepResult = main.TRUE
        main.step( "Discover all hosts using pingall " )
        stepResult = main.intentFunction.getHostsData( main )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully discovered hosts",
                                 onfail="Failed to discover hosts" )

    def CASE14( self, main ):
        """
            Stop mininet
        """
        main.log.report( "Stop Mininet topology" )
        main.log.case( "Stop Mininet topology" )

        main.step( "Stopping Mininet Topology" )
        topoResult = main.Mininet1.stopNet( )
        stepResult = topoResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully stop mininet",
                                 onfail="Failed to stop mininet" )
        # Exit if topology did not load properly
        if not topoResult:
            main.cleanup()
            main.exit()

    def CASE1000( self, main ):
        """
            Add host intents between 2 host:
                - Discover hosts
                - Add host intents
                - Check intents
                - Verify flows
                - Ping hosts
                - Reroute
                    - Link down
                    - Verify flows
                    - Check topology
                    - Ping hosts
                    - Link up
                    - Verify flows
                    - Check topology
                    - Ping hosts
                - Remove intents
        """
        import time
        import json
        import re

        # Assert variables - These variable's name|format must be followed
        # if you want to use the wrapper function
        assert main, "There is no main"
        assert main.CLIs, "There is no main.CLIs"
        assert main.Mininet1, "Mininet handle should be named Mininet1"
        assert main.numSwitch, "Placed the total number of switch topology in \
                                main.numSwitch"

        intentLeadersOld = main.CLIs[ 0 ].leaderCandidates()

        main.case( "Add host intents between 2 host" )

        main.step( "IPV4: Add host intents between h1 and h9" )
        stepResult = main.TRUE
        stepResult = main.intentFunction.hostIntent( main,
                                              onosNode='0',
                                              name='IPV4',
                                              host1='h1',
                                              host2='h9',
                                              host1Id='00:00:00:00:00:01/-1',
                                              host2Id='00:00:00:00:00:09/-1',
                                              sw1='s5',
                                              sw2='s2',
                                              expectedLink=18 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="IPV4: Add host intent successful",
                                 onfail="IPV4: Add host intent failed" )

        main.step( "DUALSTACK1: Add host intents between h3 and h11" )
        stepResult = main.TRUE
        stepResult = main.intentFunction.hostIntent( main,
                                              name='DUALSTACK',
                                              host1='h3',
                                              host2='h11',
                                              host1Id='00:00:00:00:00:03/-1',
                                              host2Id='00:00:00:00:00:0B/-1',
                                              sw1='s5',
                                              sw2='s2',
                                              expectedLink=18 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="DUALSTACK1: Add host intent" +
                                        " successful",
                                 onfail="DUALSTACK1: Add host intent failed" )

        main.step( "DUALSTACK2: Add host intents between h1 and h11" )
        stepResult = main.TRUE
        stepResult = main.intentFunction.hostIntent( main,
                                              name='DUALSTACK2',
                                              host1='h1',
                                              host2='h11',
                                              sw1='s5',
                                              sw2='s2',
                                              expectedLink=18 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="DUALSTACK2: Add host intent" +
                                        " successful",
                                 onfail="DUALSTACK2: Add host intent failed" )

        main.step( "1HOP: Add host intents between h1 and h3" )
        stepResult = main.TRUE
        stepResult = main.intentFunction.hostIntent( main,
                                              name='1HOP',
                                              host1='h1',
                                              host2='h3' )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="1HOP: Add host intent" +
                                        " successful",
                                 onfail="1HOP: Add host intent failed" )

        main.step( "VLAN1: Add vlan host intents between h4 and h12" )
        stepResult = main.TRUE
        stepResult = main.intentFunction.hostIntent( main,
                                              name='VLAN1',
                                              host1='h4',
                                              host2='h12',
                                              host1Id='00:00:00:00:00:04/100',
                                              host2Id='00:00:00:00:00:0C/100',
                                              sw1='s5',
                                              sw2='s2',
                                              expectedLink=18 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="VLAN1: Add vlan host" +
                                        " intent successful",
                                 onfail="VLAN1: Add vlan host intent failed" )

        main.step( "VLAN2: Add inter vlan host intents between h13 and h20" )
        stepResult = main.TRUE
        stepResult = main.intentFunction.hostIntent( main,
                                              name='VLAN2',
                                              host1='h13',
                                              host2='h20' )

        utilities.assert_equals( expect=main.FALSE,
                                 actual=stepResult,
                                 onpass="VLAN2: Add inter vlan host" +
                                        " intent successful",
                                 onfail="VLAN2: Add inter vlan host" +
                                        " intent failed" )


        intentLeadersNew = main.CLIs[ 0 ].leaderCandidates()
        main.intentFunction.checkLeaderChange( intentLeadersOld,
                                                intentLeadersNew )

    def CASE2000( self, main ):
        """
            Add point intents between 2 hosts:
                - Get device ids | ports
                - Add point intents
                - Check intents
                - Verify flows
                - Ping hosts
                - Reroute
                    - Link down
                    - Verify flows
                    - Check topology
                    - Ping hosts
                    - Link up
                    - Verify flows
                    - Check topology
                    - Ping hosts
                - Remove intents
        """
        import time
        import json
        import re

        # Assert variables - These variable's name|format must be followed
        # if you want to use the wrapper function
        assert main, "There is no main"
        assert main.CLIs, "There is no main.CLIs"
        assert main.Mininet1, "Mininet handle should be named Mininet1"
        assert main.numSwitch, "Placed the total number of switch topology in \
                                main.numSwitch"

        main.case( "Add point intents between 2 devices" )

        # No option point intents
        main.step( "NOOPTION: Add point intents between h1 and h9" )
        stepResult = main.TRUE
        stepResult = main.intentFunction.pointIntent(
                                       main,
                                       name="NOOPTION",
                                       host1="h1",
                                       host2="h9",
                                       deviceId1="of:0000000000000005/1",
                                       deviceId2="of:0000000000000006/1",
                                       sw1="s5",
                                       sw2="s2",
                                       expectedLink=18 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="NOOPTION: Add point intent successful",
                                 onfail="NOOPTION: Add point intent failed" )

        stepResult = main.TRUE
        main.step( "IPV4: Add point intents between h1 and h9" )
        stepResult = main.intentFunction.pointIntent(
                                       main,
                                       name="IPV4",
                                       host1="h1",
                                       host2="h9",
                                       deviceId1="of:0000000000000005/1",
                                       deviceId2="of:0000000000000006/1",
                                       port1="",
                                       port2="",
                                       ethType="IPV4",
                                       mac1="00:00:00:00:00:01",
                                       mac2="00:00:00:00:00:09",
                                       bandwidth="",
                                       lambdaAlloc=False,
                                       ipProto="",
                                       ip1="",
                                       ip2="",
                                       tcp1="",
                                       tcp2="",
                                       sw1="s5",
                                       sw2="s2",
                                       expectedLink=18 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="IPV4: Add point intent successful",
                                 onfail="IPV4: Add point intent failed" )

        main.step( "IPV4_2: Add point intents between h1 and h9" )
        stepResult = main.TRUE
        stepResult = main.intentFunction.pointIntent(
                                       main,
                                       name="IPV4_2",
                                       host1="h1",
                                       host2="h9",
                                       deviceId1="of:0000000000000005/1",
                                       deviceId2="of:0000000000000006/1",
                                       ipProto="",
                                       ip1="",
                                       ip2="",
                                       tcp1="",
                                       tcp2="",
                                       sw1="s5",
                                       sw2="s2",
                                       expectedLink=18 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="IPV4_2: Add point intent successful",
                                 onfail="IPV4_2: Add point intent failed" )

        main.step( "SDNIP-TCP: Add point intents between h1 and h9" )
        stepResult = main.TRUE
        mac1 = main.hostsData[ 'h1' ][ 'mac' ]
        mac2 = main.hostsData[ 'h9' ][ 'mac' ]
        ip1 = str( main.hostsData[ 'h1' ][ 'ipAddresses' ][ 0 ] ) + "/24"
        ip2 = str( main.hostsData[ 'h9' ][ 'ipAddresses' ][ 0 ] ) + "/24"
        ipProto = main.params[ 'SDNIP' ][ 'icmpProto' ]
        tcp1 = main.params[ 'SDNIP' ][ 'srcPort' ]
        tcp2 = main.params[ 'SDNIP' ][ 'dstPort' ]

        stepResult = main.intentFunction.pointIntent(
                                           main,
                                           name="SDNIP-TCP",
                                           host1="h1",
                                           host2="h9",
                                           deviceId1="of:0000000000000005/1",
                                           deviceId2="of:0000000000000006/1",
                                           mac1=mac1,
                                           mac2=mac2,
                                           ethType="IPV4",
                                           ipProto=ipProto,
                                           ip1=ip1,
                                           ip2=ip2,
                                           tcp1=tcp1,
                                           tcp2=tcp2 )

        utilities.assert_equals( expect=main.TRUE,
                             actual=stepResult,
                             onpass="SDNIP-TCP: Add point intent successful",
                             onfail="SDNIP-TCP: Add point intent failed" )

        main.step( "SDNIP-ICMP: Add point intents between h1 and h9" )
        stepResult = main.TRUE
        mac1 = main.hostsData[ 'h1' ][ 'mac' ]
        mac2 = main.hostsData[ 'h9' ][ 'mac' ]
        ip1 = str( main.hostsData[ 'h1' ][ 'ipAddresses' ][ 0 ] ) + "/24"
        ip2 = str( main.hostsData[ 'h9' ][ 'ipAddresses' ][ 0 ] ) + "/24"
        ipProto = main.params[ 'SDNIP' ][ 'tcpProto' ]
        tcp1 = main.params[ 'SDNIP' ][ 'srcPort' ]
        tcp2 = main.params[ 'SDNIP' ][ 'dstPort' ]

        stepResult = main.intentFunction.pointIntent(
                                           main,
                                           name="SDNIP-ICMP",
                                           host1="h1",
                                           host2="h9",
                                           deviceId1="of:0000000000000005/1",
                                           deviceId2="of:0000000000000006/1",
                                           mac1=mac1,
                                           mac2=mac2,
                                           ethType="IPV4",
                                           ipProto=ipProto )

        utilities.assert_equals( expect=main.TRUE,
                             actual=stepResult,
                             onpass="SDNIP-ICMP: Add point intent successful",
                             onfail="SDNIP-ICMP: Add point intent failed" )

        main.step( "DUALSTACK1: Add point intents between h1 and h9" )
        stepResult = main.TRUE
        stepResult = main.intentFunction.pointIntent(
                                       main,
                                       name="DUALSTACK1",
                                       host1="h3",
                                       host2="h11",
                                       deviceId1="of:0000000000000005",
                                       deviceId2="of:0000000000000006",
                                       port1="3",
                                       port2="3",
                                       ethType="IPV4",
                                       mac1="00:00:00:00:00:03",
                                       mac2="00:00:00:00:00:0B",
                                       bandwidth="",
                                       lambdaAlloc=False,
                                       ipProto="",
                                       ip1="",
                                       ip2="",
                                       tcp1="",
                                       tcp2="",
                                       sw1="s5",
                                       sw2="s2",
                                       expectedLink=18 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="DUALSTACK1: Add point intent" +
                                        " successful",
                                 onfail="DUALSTACK1: Add point intent failed" )

        main.step( "VLAN: Add point intents between h5 and h21" )
        stepResult = main.TRUE
        stepResult = main.intentFunction.pointIntent(
                                       main,
                                       name="VLAN",
                                       host1="h5",
                                       host2="h21",
                                       deviceId1="of:0000000000000005/5",
                                       deviceId2="of:0000000000000007/5",
                                       port1="",
                                       port2="",
                                       ethType="IPV4",
                                       mac1="00:00:00:00:00:05",
                                       mac2="00:00:00:00:00:15",
                                       bandwidth="",
                                       lambdaAlloc=False,
                                       ipProto="",
                                       ip1="",
                                       ip2="",
                                       tcp1="",
                                       tcp2="",
                                       sw1="s5",
                                       sw2="s2",
                                       expectedLink=18 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="VLAN: Add point intent successful",
                                 onfail="VLAN: Add point intent failed" )

        main.step( "1HOP: Add point intents between h1 and h3" )
        stepResult = main.TRUE
        stepResult = main.intentFunction.hostIntent( main,
                                              name='1HOP',
                                              host1='h1',
                                              host2='h3' )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="1HOP: Add point intent" +
                                        " successful",
                                 onfail="1HOP: Add point intent failed" )

    def CASE3000( self, main ):
        """
            Add single point to multi point intents
                - Get device ids
                - Add single point to multi point intents
                - Check intents
                - Verify flows
                - Ping hosts
                - Reroute
                    - Link down
                    - Verify flows
                    - Check topology
                    - Ping hosts
                    - Link up
                    - Verify flows
                    - Check topology
                    - Ping hosts
                - Remove intents
        """
        assert main, "There is no main"
        assert main.CLIs, "There is no main.CLIs"
        assert main.Mininet1, "Mininet handle should be named Mininet1"
        assert main.numSwitch, "Placed the total number of switch topology in \
                                main.numSwitch"

        main.case( "Add single point to multi point intents between devices" )

        main.step( "NOOPTION: Add single point to multi point intents" )
        stepResult = main.TRUE
        hostNames = [ 'h8', 'h16', 'h24' ]
        devices = [ 'of:0000000000000005/8', 'of:0000000000000006/8', \
                    'of:0000000000000007/8' ]
        macs = [ '00:00:00:00:00:08', '00:00:00:00:00:10', '00:00:00:00:00:18' ]
        stepResult = main.intentFunction.singleToMultiIntent(
                                         main,
                                         name="NOOPTION",
                                         hostNames=hostNames,
                                         devices=devices,
                                         sw1="s5",
                                         sw2="s2",
                                         expectedLink=18 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="NOOPTION: Successfully added single "
                                        + " point to multi point intents",
                                 onfail="NOOPTION: Failed to add single point" +
                                        " to multi point intents" )

        main.step( "IPV4: Add single point to multi point intents" )
        stepResult = main.TRUE
        stepResult = main.intentFunction.singleToMultiIntent(
                                         main,
                                         name="IPV4",
                                         hostNames=hostNames,
                                         devices=devices,
                                         ports=None,
                                         ethType="IPV4",
                                         macs=macs,
                                         bandwidth="",
                                         lambdaAlloc=False,
                                         ipProto="",
                                         ipAddresses="",
                                         tcp="",
                                         sw1="s5",
                                         sw2="s2",
                                         expectedLink=18 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="IPV4: Successfully added single point"
                                        + " to multi point intents",
                                 onfail="IPV4: Failed to add single point" +
                                        " to multi point intents" )

        main.step( "IPV4_2: Add single point to multi point intents" )
        stepResult = main.TRUE
        hostNames = [ 'h8', 'h16', 'h24' ]
        stepResult = main.intentFunction.singleToMultiIntent(
                                         main,
                                         name="IPV4",
                                         hostNames=hostNames,
                                         ethType="IPV4",
                                         lambdaAlloc=False )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="IPV4_2: Successfully added single "
                                        + " point to multi point intents",
                                 onfail="IPV4_2: Failed to add single point" +
                                        " to multi point intents" )

        main.step( "VLAN: Add single point to multi point intents" )
        stepResult = main.TRUE
        hostNames = [ 'h4', 'h12', 'h20' ]
        devices = [ 'of:0000000000000005/4', 'of:0000000000000006/4', \
                    'of:0000000000000007/4' ]
        macs = [ '00:00:00:00:00:04', '00:00:00:00:00:0C', '00:00:00:00:00:14' ]
        stepResult = main.intentFunction.singleToMultiIntent(
                                         main,
                                         name="VLAN",
                                         hostNames=hostNames,
                                         devices=devices,
                                         ports=None,
                                         ethType="IPV4",
                                         macs=macs,
                                         bandwidth="",
                                         lambdaAlloc=False,
                                         ipProto="",
                                         ipAddresses="",
                                         tcp="",
                                         sw1="s5",
                                         sw2="s2",
                                         expectedLink=18 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="VLAN: Successfully added single point"
                                        + " to multi point intents",
                                 onfail="VLAN: Failed to add single point" +
                                        " to multi point intents" )

    def CASE4000( self, main ):
        """
            Add multi point to single point intents
                - Get device ids
                - Add multi point to single point intents
                - Check intents
                - Verify flows
                - Ping hosts
                - Reroute
                    - Link down
                    - Verify flows
                    - Check topology
                    - Ping hosts
                    - Link up
                    - Verify flows
                    - Check topology
                    - Ping hosts
             - Remove intents
        """
        assert main, "There is no main"
        assert main.CLIs, "There is no main.CLIs"
        assert main.Mininet1, "Mininet handle should be named Mininet1"
        assert main.numSwitch, "Placed the total number of switch topology in \
                                main.numSwitch"

        main.case( "Add multi point to single point intents between devices" )

        main.step( "NOOPTION: Add multi point to single point intents" )
        stepResult = main.TRUE
        hostNames = [ 'h8', 'h16', 'h24' ]
        devices = [ 'of:0000000000000005/8', 'of:0000000000000006/8', \
                    'of:0000000000000007/8' ]
        macs = [ '00:00:00:00:00:08', '00:00:00:00:00:10', '00:00:00:00:00:18' ]
        stepResult = main.intentFunction.multiToSingleIntent(
                                         main,
                                         name="NOOPTION",
                                         hostNames=hostNames,
                                         devices=devices,
                                         sw1="s5",
                                         sw2="s2",
                                         expectedLink=18 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="NOOPTION: Successfully added multi "
                                        + " point to single point intents",
                                 onfail="NOOPTION: Failed to add multi point" +
                                        " to single point intents" )

        main.step( "IPV4: Add multi point to single point intents" )
        stepResult = main.TRUE
        stepResult = main.intentFunction.multiToSingleIntent(
                                         main,
                                         name="IPV4",
                                         hostNames=hostNames,
                                         devices=devices,
                                         ports=None,
                                         ethType="IPV4",
                                         macs=macs,
                                         bandwidth="",
                                         lambdaAlloc=False,
                                         ipProto="",
                                         ipAddresses="",
                                         tcp="",
                                         sw1="s5",
                                         sw2="s2",
                                         expectedLink=18 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="IPV4: Successfully added multi point"
                                        + " to single point intents",
                                 onfail="IPV4: Failed to add multi point" +
                                        " to single point intents" )

        main.step( "IPV4_2: Add multi point to single point intents" )
        stepResult = main.TRUE
        hostNames = [ 'h8', 'h16', 'h24' ]
        stepResult = main.intentFunction.multiToSingleIntent(
                                         main,
                                         name="IPV4",
                                         hostNames=hostNames,
                                         ethType="IPV4",
                                         lambdaAlloc=False )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="IPV4_2: Successfully added multi point"
                                        + " to single point intents",
                                 onfail="IPV4_2: Failed to add multi point" +
                                        " to single point intents" )

        main.step( "VLAN: Add multi point to single point intents" )
        stepResult = main.TRUE
        hostNames = [ 'h5', 'h13', 'h21' ]
        devices = [ 'of:0000000000000005/5', 'of:0000000000000006/5', \
                    'of:0000000000000007/5' ]
        macs = [ '00:00:00:00:00:05', '00:00:00:00:00:0D', '00:00:00:00:00:15' ]
        stepResult = main.intentFunction.multiToSingleIntent(
                                         main,
                                         name="VLAN",
                                         hostNames=hostNames,
                                         devices=devices,
                                         ports=None,
                                         ethType="IPV4",
                                         macs=macs,
                                         bandwidth="",
                                         lambdaAlloc=False,
                                         ipProto="",
                                         ipAddresses="",
                                         tcp="",
                                         sw1="s5",
                                         sw2="s2",
                                         expectedLink=18 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="VLAN: Successfully added multi point"
                                        + " to single point intents",
                                 onfail="VLAN: Failed to add multi point" +
                                        " to single point intents" )
