"""
Copyright 2016 Open Networking Foundation (ONF)

Please refer questions to either the onos test mailing list at <onos-test@onosproject.org>,
the System Testing Plans and Results wiki page at <https://wiki.onosproject.org/x/voMg>,
or the System Testing Guide page at <https://wiki.onosproject.org/x/WYQg>

    TestON is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    TestON is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with TestON.  If not, see <http://www.gnu.org/licenses/>.
"""

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

        try:
            from tests.dependencies.ONOSSetup import ONOSSetup
            main.testSetUp = ONOSSetup()
        except ImportError:
            main.log.error( "ONOSSetup not found. exiting the test" )
            main.exit()
        main.testSetUp.envSetupDescription()
        stepResult = main.FALSE
        try:
            # load some variables from the params file
            cellName = main.params[ 'ENV' ][ 'cellName' ]

            main.apps = main.params[ 'ENV' ][ 'cellApps' ]
            main.numCtrls = int( main.params[ 'num_controllers' ] )

            ofPort = main.params[ 'CTRL' ][ 'port' ]
            stepResult = main.testSetUp.envSetup( hasRest=True, hasNode=True )
        except Exception as e:
            main.testSetUp.envSetupException( e )
        main.testSetUp.evnSetupConclusion( stepResult )

        main.testSetUp.ONOSSetUp( main.Mininet1, cellName=cellName )

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
        args = " --switch ovs,protocols=OpenFlow13"
        for node in main.nodes:
            args += " --controller=remote,ip=" + node.ip_address
        mnCmd = "sudo mn" + topo + args
        mnResult = main.Mininet1.startNet( mnCmd=mnCmd )
        utilities.assert_equals( expect=main.TRUE, actual=mnResult,
                                 onpass="Mininet Started",
                                 onfail="Error starting Mininet" )

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

        main.vpls = vpls
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
        fileName = main.params[ 'DEPENDENCY' ][ 'topology' ]
        app = main.params[ 'vpls' ][ 'name' ]

        loadVPLSResult = main.ONOSbench.onosNetCfg( main.nodes[ 0 ].ip_address, "", fileName )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=loadVPLSResult,
                                 onpass="Loaded vpls configuration.",
                                 onfail="Failed to load vpls configuration." )

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

        main.step( "Loading vpls configuration in case any configuration was missed." )
        loadVPLSResult = main.ONOSbench.onosNetCfg( main.nodes[ 0 ].ip_address, "", fileName )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=loadVPLSResult,
                                 onpass="Loaded vpls configuration.",
                                 onfail="Failed to load vpls configuration." )

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
