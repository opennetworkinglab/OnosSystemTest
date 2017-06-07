# CASE1: Startup
# CASE2: Load vpls topology and configurations from demo script
# CASE3: Test CLI commands


class VPLSBasic:

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
        import imp
        import time
        import json
        main.case( "Setting up test environment" )
        main.caseExplanation = "Setup the test environment including " +\
                                "installing ONOS, starting Mininet and ONOS" +\
                                "cli sessions."

        # load some variables from the params file
        cellName = main.params[ 'ENV' ][ 'cellName' ]

        main.numCtrls = int( main.params[ 'num_controllers' ] )

        ofPort = main.params[ 'CTRL' ][ 'port' ]

        main.CLIs = []
        main.RESTs = []
        main.nodes = []
        ipList = []
        for i in range( 1, main.numCtrls + 1 ):
            try:
                main.CLIs.append( getattr( main, 'ONOScli' + str( i ) ) )
                main.RESTs.append( getattr( main, 'ONOSrest' + str( i ) ) )
                main.nodes.append( getattr( main, 'ONOS' + str( i ) ) )
                ipList.append( main.nodes[ -1 ].ip_address )
            except AttributeError:
                break

        main.step( "Create cell file" )
        cellAppString = main.params[ 'ENV' ][ 'cellApps' ]
        main.ONOSbench.createCellFile( main.ONOSbench.ip_address, cellName,
                                       main.Mininet1.ip_address,
                                       cellAppString, ipList, main.ONOScli1.user_name )
        main.step( "Applying cell variable to environment" )
        cellResult = main.ONOSbench.setCell( cellName )
        verifyResult = main.ONOSbench.verifyCell()

        main.log.info( "Uninstalling ONOS" )
        for node in main.nodes:
            main.ONOSbench.onosUninstall( node.ip_address )

        # Make sure ONOS is DEAD
        main.log.info( "Killing any ONOS processes" )
        killResults = main.TRUE
        for node in main.nodes:
            killed = main.ONOSbench.onosKill( node.ip_address )
            killResults = killResults and killed

        cleanInstallResult = main.TRUE

        main.step( "Starting Mininet" )
        # scp topo file to mininet
        # TODO: move to params?
        topoName = "vpls"
        topoFile = "vpls.py"
        filePath = main.ONOSbench.home + "/tools/test/topos/"
        main.ONOSbench.scp( main.Mininet1,
                            filePath + topoFile,
                            main.Mininet1.home,
                            direction="to" )
        topo = " --custom " + main.Mininet1.home + topoFile + " --topo " + topoName
        args = " --switch ovs,protocols=OpenFlow13 --controller=remote"
        for node in main.nodes:
            args += ",ip=" + node.ip_address
        mnCmd = "sudo mn" + topo + args
        mnResult = main.Mininet1.startNet( mnCmd=mnCmd )
        utilities.assert_equals( expect=main.TRUE, actual=mnResult,
                                 onpass="Mininet Started",
                                 onfail="Error starting Mininet" )

        main.ONOSbench.getVersion( report=True )

        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.buckBuild()
        utilities.assert_equals( expect=main.TRUE, actual=packageResult,
                                 onpass="ONOS package successful",
                                 onfail="ONOS package failed" )

        main.step( "Installing ONOS package" )
        onosInstallResult = main.TRUE
        for node in main.nodes:
            tmpResult = main.ONOSbench.onosInstall( options="-f",
                                                    node=node.ip_address )
            onosInstallResult = onosInstallResult and tmpResult
        utilities.assert_equals( expect=main.TRUE, actual=onosInstallResult,
                                 onpass="ONOS install successful",
                                 onfail="ONOS install failed" )

        main.step( "Set up ONOS secure SSH" )
        secureSshResult = main.TRUE
        for node in main.nodes:
            secureSshResult = secureSshResult and main.ONOSbench.onosSecureSSH( node=node.ip_address )
        utilities.assert_equals( expect=main.TRUE, actual=secureSshResult,
                                 onpass="Test step PASS",
                                 onfail="Test step FAIL" )

        main.step( "Checking if ONOS is up yet" )
        for i in range( 2 ):
            onosIsupResult = main.TRUE
            for node in main.nodes:
                started = main.ONOSbench.isup( node.ip_address )
                if not started:
                    main.log.error( node.name + " hasn't started" )
                onosIsupResult = onosIsupResult and started
            if onosIsupResult == main.TRUE:
                break
        utilities.assert_equals( expect=main.TRUE, actual=onosIsupResult,
                                 onpass="ONOS startup successful",
                                 onfail="ONOS startup failed" )

        main.step( "Starting ONOS CLI sessions" )
        cliResults = main.TRUE
        threads = []
        for i in range( main.numCtrls ):
            t = main.Thread( target=main.CLIs[ i ].startOnosCli,
                             name="startOnosCli-" + str( i ),
                             args=[ main.nodes[ i ].ip_address ] )
            threads.append( t )
            t.start()

        for t in threads:
            t.join()
            cliResults = cliResults and t.result
        utilities.assert_equals( expect=main.TRUE, actual=cliResults,
                                 onpass="ONOS cli startup successful",
                                 onfail="ONOS cli startup failed" )

        main.activeNodes = [ i for i in range( 0, len( main.CLIs ) ) ]

        main.step( "Activate apps defined in the params file" )
        # get data from the params
        apps = main.params.get( 'apps' )
        if apps:
            apps = apps.split( ',' )
            main.log.warn( apps )
            activateResult = True
            for app in apps:
                main.CLIs[ 0 ].app( app, "Activate" )
            # TODO: check this worked
            time.sleep( SLEEP )  # wait for apps to activate
            for app in apps:
                state = main.CLIs[ 0 ].appStatus( app )
                if state == "ACTIVE":
                    activateResult = activateResult and True
                else:
                    main.log.error( "{} is in {} state".format( app, state ) )
                    activateResult = False
            utilities.assert_equals( expect=True,
                                     actual=activateResult,
                                     onpass="Successfully activated apps",
                                     onfail="Failed to activate apps" )
        else:
            main.log.warn( "No apps were specified to be loaded after startup" )

        main.step( "Set ONOS configurations" )
        config = main.params.get( 'ONOS_Configuration' )
        if config:
            main.log.debug( config )
            checkResult = main.TRUE
            for component in config:
                for setting in config[ component ]:
                    value = config[ component ][ setting ]
                    check = main.CLIs[ 0 ].setCfg( component, setting, value )
                    main.log.info( "Value was changed? {}".format( main.TRUE == check ) )
                    checkResult = check and checkResult
            utilities.assert_equals( expect=main.TRUE,
                                     actual=checkResult,
                                     onpass="Successfully set config",
                                     onfail="Failed to set config" )
        else:
            main.log.warn( "No configurations were specified to be changed after startup" )

        main.step( "App Ids check" )
        appCheck = main.TRUE
        threads = []
        for i in main.activeNodes:
            t = main.Thread( target=main.CLIs[ i ].appToIDCheck,
                             name="appToIDCheck-" + str( i ),
                             args=[] )
            threads.append( t )
            t.start()

        for t in threads:
            t.join()
            appCheck = appCheck and t.result
        if appCheck != main.TRUE:
            main.log.warn( main.CLIs[ 0 ].apps() )
            main.log.warn( main.CLIs[ 0 ].appIDs() )
        utilities.assert_equals( expect=main.TRUE, actual=appCheck,
                                 onpass="App Ids seem to be correct",
                                 onfail="Something is wrong with app Ids" )

    def CASE2( self, main ):
        """
        Load and test vpls configurations from json configuration file
        """
        import os.path
        from tests.USECASE.VPLS.dependencies import vpls

        pprint = main.ONOSrest1.pprint
        hosts = int( main.params[ 'vpls' ][ 'hosts' ] )
        SLEEP = int( main.params[ 'SLEEP' ][ 'netcfg' ] )

        main.step( "Discover hosts using pings" )
        for i in range( 1, hosts + 1 ):
            src = "h" + str( i )
            for j in range( 1, hosts + 1 ):
                if j == i:
                    continue
                dst = "h" + str( j )
            pingResult = main.Mininet1.pingHost( SRC=src, TARGET=dst )

        main.step( "Load VPLS configurations" )
        # TODO: load from params
        fileName = main.params[ 'DEPENDENCY' ][ 'topology' ]
        app = main.params[ 'vpls' ][ 'name' ]
        # TODO make this a function?
        main.ONOSbench.handle.sendline( "onos-netcfg $OC1 " + fileName )
        # Time for netcfg to load data
        time.sleep( SLEEP )
        # 'Master' copy of test configuration
        try:
            with open( os.path.expanduser( fileName ) ) as dataFile:
                originalCfg = json.load( dataFile )
                main.vplsConfig = originalCfg[ 'apps' ].get( app ).get( 'vpls' ).get( 'vplsList' )
        except Exception as e:
            main.log.error( "Error loading config file: {}".format( e ) )
        if main.vplsConfig:
            result = True
        else:
            result = False
        utilities.assert_equals( expect=True,
                                 actual=result,
                                 onpass="Loaded vpls configuration",
                                 onfail="Failed to load vpls configuration" )

        main.step( "Check interface configurations" )
        result = False
        getPorts = utilities.retry( f=main.ONOSrest1.getNetCfg,
                                    retValue=False,
                                    kwargs={"subjectClass":"ports"},
                                    sleep=SLEEP )
        onosCfg = pprint( getPorts )
        sentCfg = pprint( originalCfg.get( "ports" ) )

        if onosCfg == sentCfg:
            main.log.info( "ONOS interfaces NetCfg matches what was sent" )
            result = True
        else:
            main.log.error( "ONOS interfaces NetCfg doesn't match what was sent" )
            main.log.debug( "ONOS config: {}".format( onosCfg ) )
            main.log.debug( "Sent config: {}".format( sentCfg ) )
        utilities.assert_equals( expect=True,
                                 actual=result,
                                 onpass="Net Cfg added for interfaces",
                                 onfail="Net Cfg not added for interfaces" )

        # Run a bunch of checks to verify functionality based on configs
        vpls.verify( main )

    def CASE3( self, main ):
        """
        Test VPLS cli commands
        High level steps:
            remove interface from a network
            Clean configs
            create vpls network
            add interfaces to a network
            add encap
            change encap
            remove encap
            list?
        """
        from tests.USECASE.VPLS.dependencies import vpls
        SLEEP = int( main.params[ 'SLEEP' ][ 'netcfg' ] )
        pprint = main.ONOSrest1.pprint

        main.step( "Remove an interface from a vpls network" )
        main.CLIs[ 0 ].vplsRemIface( 'VPLS1', 'h1' )
        time.sleep( SLEEP )
        #update master config json
        for network in main.vplsConfig:
            if network.get( 'name' ) == 'VPLS1':
                ifaces = network.get( 'interfaces' )
                ifaces.remove( 'h1' )
        vpls.verify( main )

        main.step( "Clean all vpls configurations" )
        main.CLIs[ 0 ].vplsClean()
        time.sleep( SLEEP )
        main.vplsConfig = []
        vpls.verify( main )

        main.step( "Create a new vpls network" )
        name = "Network1"
        main.CLIs[ 0 ].vplsCreate( name )
        time.sleep( SLEEP )
        network1 = { 'name': name, 'interfaces': [], 'encapsulation': 'NONE' }
        main.vplsConfig.append( network1 )
        vpls.verify( main )

        main.step( "Add interfaces to the network" )
        main.CLIs[ 0 ].vplsAddIface( name, "h1" )
        main.CLIs[ 0 ].vplsAddIface( name, "h5" )
        main.CLIs[ 0 ].vplsAddIface( name, "h4" )
        time.sleep( SLEEP )
        for network in main.vplsConfig:
            if network.get( 'name' ) == name:
                ifaces = network.get( 'interfaces' )
                ifaces.append( 'h1' )
                ifaces.append( 'h4' )
                ifaces.append( 'h5' )
                network[ 'interfaces' ] = ifaces
        vpls.verify( main )

        main.step( "Add MPLS encapsulation to a vpls network" )
        encapType = "MPLS"
        main.CLIs[ 0 ].vplsSetEncap( name, encapType )
        for network in main.vplsConfig:
            if network.get( 'name' ) == name:
                network[ 'encapsulation' ] = encapType
        time.sleep( SLEEP )
        vpls.verify( main )

        main.step( "Change an encapsulation type" )
        encapType = "VLAN"
        main.CLIs[ 0 ].vplsSetEncap( name, encapType )
        for network in main.vplsConfig:
            if network.get( 'name' ) == name:
                network[ 'encapsulation' ] = encapType
        time.sleep( SLEEP )
        vpls.verify( main )

        main.step( "Remove encapsulation" )
        encapType = "NONE"
        main.CLIs[ 0 ].vplsSetEncap( name, encapType )
        for network in main.vplsConfig:
            if network.get( 'name' ) == name:
                network[ 'encapsulation' ] = encapType
        time.sleep( SLEEP )
        vpls.verify( main )

        main.step( "Clean all vpls configurations" )
        main.CLIs[ 0 ].vplsClean()
        time.sleep( SLEEP )
        main.vplsConfig = []
        vpls.verify( main )
