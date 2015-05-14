
# Testing the basic functionality of ONOS Next
# For sanity and driver functionality excercises only.

import time
import json

time.sleep( 1 )

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
        try:
            if type(init) is not bool:
                init = False
        except NameError:
            init = False
        #Local variables
        cellName = main.params[ 'ENV' ][ 'cellName' ]
        apps = main.params[ 'ENV' ][ 'cellApps' ]
        gitBranch = main.params[ 'GIT' ][ 'branch' ]
        benchIp = main.params[ 'BENCH' ][ 'ip1' ]
        benchUser = main.params[ 'BENCH' ][ 'user' ]
        topology = main.params[ 'MININET' ][ 'topo' ]
        maxNodes = int( main.params[ 'availableNodes' ] )
        main.numSwitch = int( main.params[ 'MININET' ][ 'switch' ] )
        main.numLinks = int( main.params[ 'MININET' ][ 'links' ] )
        main.numCtrls = main.params[ 'CTRL' ][ 'num' ]
        main.wrapper = imp.load_source( 'FuncIntentFunction',
                                    '/home/admin/ONLabTest/TestON/tests/' +
                                    'FuncIntent/Dependency/' +
                                    'FuncIntentFunction.py' )
        PULLCODE = False
        if main.params[ 'GIT' ][ 'pull' ] == 'True':
            PULLCODE = True
        main.case( "Setting up test environment" )
        main.CLIs = []
        for i in range( 1, int( main.numCtrls ) + 1 ):
            main.CLIs.append( getattr( main, 'ONOScli' + str( i ) ) )

        # -- INIT SECTION, ONLY RUNS ONCE -- #
        if init == False:
            init = True
            main.MNisUp = main.FALSE

            main.ONOSip = []
            main.ONOSport = []
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
            # Populate main.ONOSip with ips from params
            for i in range( 1, maxNodes + 1):
                main.ONOSip.append( main.params[ 'CTRL' ][ 'ip' + str( i ) ] )
                main.ONOSport.append( main.params[ 'CTRL' ][ 'port' +
                                      str( i ) ])

        main.numCtrls = int( main.scale[ 0 ] )
        main.scale.remove( main.scale[ 0 ] )
        #kill off all onos processes
        main.log.info( "Safety check, killing all ONOS processes" +
                       " before initiating enviornment setup" )
        for i in range( maxNodes ):
            main.ONOSbench.onosDie( main.ONOSip[ i ] )
        """main.step( "Removing raft logs" )
        removeRaftResult = main.ONOSbench.onosRemoveRaftLogs()
        stepResult = removeRaftResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully removed raft logs",
                                 onfail="Failed to remove raft logs" )
        """
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
        for i in range( main.numCtrls):
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
        for i in range( main.numCtrls):
            onosInstallResult = onosInstallResult and \
                    main.ONOSbench.onosInstall( node=main.ONOSip[ i ] )
        stepResult = onosInstallResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully installed ONOS package",
                                 onfail="Failed to install ONOS package" )

        time.sleep( 5 )
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

    def CASE11( self, main ):
        """
            Start mininet
        """
        import time
        main.log.report( "Start Mininet topology" )
        main.case( "Start Mininet topology" )
        if not main.MNisUp:
            main.MNisUp = main.TRUE
        else:
            main.Mininet1.stopNet()
            time.sleep( 30 )
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
        """
            Create your item(s) here
            item = { 'name': '', 'host1':
                     { 'name': '', 'MAC': '00:00:00:00:00:0X',
                       'id':'00:00:00:00:00:0X/-X' } , 'host2':
                     { 'name': '', 'MAC': '00:00:00:00:00:0X',
                       'id':'00:00:00:00:00:0X/-X'}, 'link': { 'switch1': '',
                       'switch2': '', 'expect':'' } }
        """

        # Assert variables - These variable's name|format must be followed
        # if you want to use the wrapper function
        assert main, "There is no main"
        assert main.CLIs, "There is no main.CLIs"
        assert main.Mininet1, "Mininet handle should be named Mininet1"
        assert main.numSwitch, "Placed the total number of switch topology in \
                                main.numSwitch"

        # Local variables
        ipv4 = { 'name':'IPV4', 'host1':
                 { 'name': 'h1', 'MAC':'00:00:00:00:00:01',
                   'id':'00:00:00:00:00:01/-1' } , 'host2':
                 { 'name':'h9', 'MAC':'00:00:00:00:00:09',
                   'id':'00:00:00:00:00:09/-1'}, 'link': { 'switch1':'s5',
                   'switch2':'s2', 'expect':'18' } }
        dualStack1 = { 'name':'DUALSTACK1', 'host1':
                 { 'name':'h3', 'MAC':'00:00:00:00:00:03',
                   'id':'00:00:00:00:00:03/-1' } , 'host2':
                 { 'name':'h11', 'MAC':'00:00:00:00:00:0B',
                   'id':'00:00:00:00:00:0B/-1'}, 'link': { 'switch1':'s5',
                   'switch2':'s2', 'expect':'18' } }

        main.case( "Add host intents between 2 host" )

        stepResult = main.TRUE
        main.step( ipv4[ 'name' ] + ": Add host intents between " +
                   ipv4[ 'host1' ][ 'name' ] + " and " +
                   ipv4[ 'host2' ][ 'name' ]  )
        stepResult = main.wrapper.addHostIntent( main, ipv4 )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass=ipv4[ 'name' ] +
                                        ": Add host intent successful",
                                 onfail=ipv4[ 'name' ] +
                                        ": Add host intent failed" )

        stepResult = main.TRUE
        main.step( dualStack1[ 'name' ] + ": Add host intents between " +
                   dualStack1[ 'host1' ][ 'name' ] + " and " +
                   dualStack1[ 'host2' ][ 'name' ]  )
        stepResult = main.wrapper.addHostIntent( main, dualStack1 )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass=dualStack1[ 'name' ] +
                                        ": Add host intent successful",
                                 onfail=dualStack1[ 'name' ] +
                                        ": Add host intent failed" )

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
        """
            Create your item(s) here
            item = { 'name':'', 'host1': { 'name': '' },
                     'host2': { 'name': '' },
                     'ingressDevice':'' , 'egressDevice':'',
                     'ingressPort':'', 'egressPort':'',
                     'option':{ 'ethType':'', 'ethSrc':'', 'ethDst':'' } ,
                     'link': { 'switch1': '', 'switch2':'', 'expect':'' } }

        """

        # Assert variables - These variable's name|format must be followed
        # if you want to use the wrapper function
        assert main, "There is no main"
        assert main.CLIs, "There is no main.CLIs"
        assert main.Mininet1, "Mininet handle should be named Mininet1"
        assert main.numSwitch, "Placed the total number of switch topology in \
                                main.numSwitch"

        ipv4 = { 'name':'IPV4', 'ingressDevice':'of:0000000000000005/1' ,
                 'host1': { 'name': 'h1' }, 'host2': { 'name': 'h9' },
                 'egressDevice':'of:0000000000000006/1', 'option':
                 { 'ethType':'IPV4', 'ethSrc':'00:00:00:00:00:01',
                   'ethDst':'00:00:00:00:00:09' }, 'link': { 'switch1':'s5',
                   'switch2':'s2', 'expect':'18' } }

        """
        ipv4 = { 'name':'IPV4', 'ingressDevice':'of:0000000000000005/1' ,
                 'host1': { 'name': 'h1' }, 'host2': { 'name': 'h9' },
                 'egressDevice':'of:0000000000000006/1', 'option':
                 { 'ethType':'IPV4', 'ethSrc':'00:00:00:00:00:01' },
                 'link': { 'switch1':'s5', 'switch2':'s2', 'expect':'18' } }
        """ 
        dualStack1 = { 'name':'IPV4', 'ingressDevice':'0000000000000005/3' ,
                       'host1': { 'name': 'h3' }, 'host2': { 'name': 'h11' },
                       'egressDevice':'0000000000000006/3', 'option':
                       { 'ethType':'IPV4', 'ethSrc':'00:00:00:00:00:03',
                       'ethDst':'00:00:00:00:00:0B' }, 'link': { 'switch1':'s5',
                       'switch2':'s2', 'expect':'18' } }


        main.case( "Add point intents between 2 devices" )

        stepResult = main.TRUE
        main.step( ipv4[ 'name' ] + ": Add point intents between " +
                   ipv4[ 'host1' ][ 'name' ] + " and " +
                   ipv4[ 'host2' ][ 'name' ]  )
        stepResult = main.wrapper.addPointIntent( main, ipv4 )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass=ipv4[ 'name' ] +
                                        ": Point intent successful",
                                 onfail=ipv4[ 'name' ] +
                                        ": Point intent failed" )

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
