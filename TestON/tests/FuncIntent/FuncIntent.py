
# Testing the basic functionality of ONOS Next
# For sanity and driver functionality excercises only.

import time
import json

class FuncIntent:

    def __init__( self ):
        self.default = ''

    def CASE10( self, main ):
        import time
        import os
        import imp
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
        global init
        global globalONOSip
        try:
            if type(init) is not bool:
                init = False
        except NameError:
            init = False

        main.wrapper = imp.load_source( 'FuncIntentFunction',
                                    '/home/admin/ONLabTest/TestON/tests/' +
                                    'FuncIntent/Dependency/' +
                                    'FuncIntentFunction.py' )
        #Local variables
        cellName = main.params[ 'ENV' ][ 'cellName' ]
        apps = main.params[ 'ENV' ][ 'cellApps' ]
        gitBranch = main.params[ 'GIT' ][ 'branch' ]
        benchIp = os.environ[ 'OCN' ]
        benchUser = main.params[ 'BENCH' ][ 'user' ]
        topology = main.params[ 'MININET' ][ 'topo' ]
        main.numSwitch = int( main.params[ 'MININET' ][ 'switch' ] )
        main.numLinks = int( main.params[ 'MININET' ][ 'links' ] )
        main.numCtrls = main.params[ 'CTRL' ][ 'num' ]
        main.ONOSport = []
        main.hostsData = {}
        PULLCODE = False
        if main.params[ 'GIT' ][ 'pull' ] == 'True':
            PULLCODE = True
        main.case( "Setting up test environment" )
        main.CLIs = []
        for i in range( 1, int( main.numCtrls ) + 1 ):
            main.CLIs.append( getattr( main, 'ONOScli' + str( i ) ) )
            main.ONOSport.append( main.params[ 'CTRL' ][ 'port' + str( i ) ] )

        # -- INIT SECTION, ONLY RUNS ONCE -- #
        if init == False:
            init = True

            main.scale = ( main.params[ 'SCALE' ] ).split( "," )
            main.numCtrls = int( main.scale[ 0 ] )

            if PULLCODE:
                main.step( "Git checkout and pull " + gitBranch )
                main.ONOSbench.gitCheckout( gitBranch )
                gitPullResult = main.ONOSbench.gitPull()
                if gitPullResult == main.ERROR:
                    main.log.error( "Error pulling git branch" )
                main.step( "Using mvn clean & install" )
                cleanInstallResult = main.ONOSbench.cleanInstall()
                stepResult = cleanInstallResult
                utilities.assert_equals( expect=main.TRUE,
                                         actual=stepResult,
                                         onpass="Successfully compiled " +
                                                "latest ONOS",
                                         onfail="Failed to compile " +
                                                "latest ONOS" )
            else:
                main.log.warn( "Did not pull new code so skipping mvn " +
                               "clean install" )

            globalONOSip = main.ONOSbench.getOnosIps()

        maxNodes = ( len(globalONOSip) - 2 )

        main.numCtrls = int( main.scale[ 0 ] )
        main.scale.remove( main.scale[ 0 ] )

        main.ONOSip = []
        for i in range( maxNodes ):
            main.ONOSip.append( globalONOSip[i] )

        #kill off all onos processes
        main.log.info( "Safety check, killing all ONOS processes" +
                       " before initiating enviornment setup" )
        for i in range(maxNodes):
            main.ONOSbench.onosDie( globalONOSip[ i ] )

        print "NODE COUNT = ", main.numCtrls
        main.log.info( "Creating cell file" )
        cellIp = []
        for i in range( main.numCtrls ):
            cellIp.append( str( main.ONOSip[ i ] ) )
        print cellIp
        main.ONOSbench.createCellFile( benchIp, cellName, "",
                                       str( apps ), *cellIp )

        main.step( "Apply cell to environment" )
        cellResult = main.ONOSbench.setCell( cellName )
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
        time.sleep( 5 )
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

        time.sleep( 20 )
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
                        main.CLIs[i].startOnosCli( main.ONOSip[ i ] )
        stepResult = cliResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully start ONOS cli",
                                 onfail="Failed to start ONOS cli" )

    def CASE9( self, main ):
        '''
            Report errors/warnings/exceptions
        '''
        main.log.info( "Error report: \n" )
        main.ONOSbench.logReport( globalONOSip[0],
                [ "INFO", "FOLLOWER", "WARN", "flow", "ERROR" , "Except" ],
                "s" )
        #main.ONOSbench.logReport( globalONOSip[1], [ "INFO" ], "d" )

    def CASE11( self, main ):
        """
            Start mininet
        """
        main.log.report( "Start Mininet topology" )
        main.log.case( "Start Mininet topology" )

        main.step( "Starting Mininet Topology" )
        topoResult = main.Mininet1.startNet( topoFile=topology )
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
        for i in range( 1, ( main.numSwitch + 1 ) ):
            main.Mininet1.assignSwController( sw=str( i ),
                                              count=1,
                                              ip1=main.ONOSip[ 0 ],
                                              port1=main.ONOSport[ 0 ] )
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
        stepResult = main.wrapper.getHostsData( main )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully discovered hosts",
                                 onfail="Failed to discover hosts" )

    def CASE1001( self, main ):
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

        main.case( "Add host intents between 2 host" )

        stepResult = main.TRUE
        main.step( "IPV4: Add host intents between h1 and h9" )
        stepResult = main.wrapper.hostIntent( main,
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
        stepResult = main.TRUE

        main.step( "DUALSTACK1: Add host intents between h3 and h11" )
        stepResult = main.wrapper.hostIntent( main,
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

        stepResult = main.TRUE
        main.step( "DUALSTACK2: Add host intents between h1 and h11" )
        stepResult = main.wrapper.hostIntent( main,
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

        stepResult = main.TRUE
        main.step( "1HOP: Add host intents between h1 and h3" )
        stepResult = main.wrapper.hostIntent( main,
                                              name='1HOP',
                                              host1='h1',
                                              host2='h3' )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="1HOP: Add host intent" +
                                        " successful",
                                 onfail="1HOP: Add host intent failed" )

        main.step( "VLAN1: Add vlan host intents between h4 and h12" )
        stepResult = main.wrapper.hostIntent( main,
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
                                 onpass="VLAN1: Add vlan host intent successful",
                                 onfail="VLAN1: Add vlan host intent failed" )
        stepResult = main.TRUE
        main.step( "VLAN2: Add inter vlan host intents between h13 and h20" )
        stepResult = main.wrapper.hostIntent( main,
                                              name='VLAN2',
                                              host1='h13',
                                              host2='h20',
                                              host1Id='',
                                              host2Id='',
                                              sw1='s5',
                                              sw2='s2',
                                              expectedLink=18 )

        utilities.assert_equals( expect=main.FALSE,
                                 actual=stepResult,
                                 onpass="VLAN2: Add inter vlan host intent successful",
                                 onfail="VLAN2: Add inter vlan host intent failed" )

    def CASE1002( self, main ):
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

        stepResult = main.TRUE
        # No option point intents
        main.step( "NOOPTION: Add point intents between h1 and h9" )
        stepResult = main.wrapper.pointIntent(
                                       main,
                                       name="NOOPTION",
                                       host1="h1",
                                       host2="h9",
                                       deviceId1="of:0000000000000005/1",
                                       deviceId2="of:0000000000000006/1",
                                       sw1="s5",
                                       sw2="s2",
                                       expectedLink=18 )

        stepResult = main.TRUE
        main.step( "NOOPTION: Add point intents between h1 and h9" )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="NOOPTION: Add point intent successful",
                                 onfail="NOOPTION: Add point intent failed" )

        stepResult = main.wrapper.pointIntent(
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

        stepResult = main.TRUE
        main.step( "DUALSTACK1: Add point intents between h1 and h9" )
        stepResult = main.wrapper.pointIntent(
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

        stepResult = main.TRUE
        main.step( "1HOP: Add point intents between h1 and h3" )
        stepResult = main.wrapper.hostIntent( main,
                                              name='1HOP',
                                              host1='h1',
                                              host2='h3' )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="1HOP: Add point intent" +
                                        " successful",
                                 onfail="1HOP: Add point intent failed" )

    def CASE1003( self, main ):
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

        stepResult = main.TRUE
        hostNames = [ 'h8', 'h16', 'h24' ]
        devices = [ 'of:0000000000000005/8', 'of:0000000000000006/8', \
                    'of:0000000000000007/8' ]
        macs = [ '00:00:00:00:00:08', '00:00:00:00:00:10', '00:00:00:00:00:18' ]

        main.step( "NOOPTION: Add single point to multi point intents" )
        stepResult = main.wrapper.singleToMultiIntent(
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
        stepResult = main.wrapper.singleToMultiIntent(
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
        hostNames = [ 'h8', 'h16', 'h24' ]
        stepResult = main.wrapper.singleToMultiIntent(
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
    def CASE1004( self, main ):
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

        stepResult = main.TRUE
        hostNames = [ 'h8', 'h16', 'h24' ]
        devices = [ 'of:0000000000000005/8', 'of:0000000000000006/8', \
                    'of:0000000000000007/8' ]
        macs = [ '00:00:00:00:00:08', '00:00:00:00:00:10', '00:00:00:00:00:18' ]

        main.step( "NOOPTION: Add multi point to single point intents" )
        stepResult = main.wrapper.multiToSingleIntent(
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
        stepResult = main.wrapper.multiToSingleIntent(
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
        hostNames = [ 'h8', 'h16', 'h24' ]
        stepResult = main.wrapper.multiToSingleIntent(
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
