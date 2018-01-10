"""
Copyright 2016 Open Networking Foundation ( ONF )

Please refer questions to either the onos test mailing list at <onos-test@onosproject.org>,
the System Testing Plans and Results wiki page at <https://wiki.onosproject.org/x/voMg>,
or the System Testing Guide page at <https://wiki.onosproject.org/x/WYQg>

    TestON is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    ( at your option ) any later version.

    TestON is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with TestON.  If not, see <http://www.gnu.org/licenses/>.
"""
# This is a sample template that starts up ONOS cluster, this template
# can be use as a base script for ONOS System Testing.


class SAMPstartTemplate_3node:

    def __init__( self ):
        self.default = ''

    def CASE0( self, main ):
        """
            Pull specific ONOS branch, then Build ONOS on ONOS Bench.
            This step is usually skipped. Because in a Jenkins driven automated
            test env. We want Jenkins jobs to pull&build for flexibility to handle
            different versions of ONOS.
        """
        from tests.dependencies.ONOSSetup import ONOSSetup
        main.testSetUp = ONOSSetup()
        main.testSetUp.gitPulling()

    def CASE1( self, main ):
        """
            Set up global test variables;
            Uninstall all running cells in test env defined in .topo file

        """
        main.testSetUp.envSetupDescription()
        stepResult = main.FALSE
        try:
            main.onosStartupSleep = float( main.params[ 'CASE1' ][ 'SleepTimers' ][ 'onosStartup' ] )
            main.onosCfgSleep = float( main.params[ 'CASE1' ][ 'SleepTimers' ][ 'onosCfg' ] )
            main.mnStartupSleep = float( main.params[ 'CASE1' ][ 'SleepTimers' ][ 'mnStartup' ] )
            main.mnCfgSleep = float( main.params[ 'CASE1' ][ 'SleepTimers' ][ 'mnCfg' ] )
            stepResult = main.testSetUp.envSetup( includeGitPull=False )
        except Exception as e:
            main.testSetUp.envSetupException( e )
        main.testSetUp.evnSetupConclusion( stepResult )

    def CASE2( self, main ):
        """
            Report errors/warnings/exceptions
        """
        main.log.info( "Error report: \n" )
        main.ONOSbench.logReport( main.Cluster.runningNodes[ 0 ].ipAddress,
                                  [ "INFO",
                                    "FOLLOWER",
                                    "WARN",
                                    "flow",
                                    "ERROR",
                                    "Except" ],
                                  "s" )

    def CASE10( self, main ):
        """
        Start ONOS cluster ( 3 nodes in this example ) in three steps:
        1 ) start a basic cluster with drivers app via ONOSDriver;
        2 ) activate apps via ONOSCliDriver;
        3 ) configure onos via ONOSCliDriver;
        """
        import time

        main.case( "Start up " + str( main.Cluster.numCtrls ) + "-node onos cluster." )

        main.step( "Start ONOS cluster with basic (drivers) app." )
        stepResult = main.testSetUp.ONOSSetUp( main.Mininet1, main.Cluster )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully started basic ONOS cluster ",
                                 onfail="Failed to start basic ONOS Cluster " )

        main.testSetUp.startOnosClis( main.Cluster )

        main.step( "Activate onos apps." )
        main.apps = main.params[ 'CASE10' ].get( 'Apps' )
        if main.apps:
            main.log.info( "Apps to activate: " + main.apps )
            activateResult = main.TRUE
            for a in main.apps.split( "," ):
                activateResult = activateResult & main.Cluster.active( 0 ).CLI.activateApp( a )
            # TODO: check this worked
            time.sleep( main.onosCfgSleep )  # wait for apps to activate
        else:
            main.log.warn( "No configurations were specified to be changed after startup" )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=activateResult,
                                 onpass="Successfully set config",
                                 onfail="Failed to set config" )

        main.step( "Set ONOS configurations" )
        config = main.params[ 'CASE10' ].get( 'ONOS_Configuration' )
        if config:
            main.log.debug( config )
            checkResult = main.TRUE
            for component in config:
                for setting in config[ component ]:
                    value = config[ component ][ setting ]
                    check = main.Cluster.runningNodes[ 0 ].setCfg( component, setting, value )
                    main.log.info( "Value was changed? {}".format( main.TRUE == check ) )
                    checkResult = check and checkResult
            utilities.assert_equals( expect=main.TRUE,
                                     actual=checkResult,
                                     onpass="Successfully set config",
                                     onfail="Failed to set config" )
        else:
            main.log.warn( "No configurations were specified to be changed after startup" )

    def CASE11( self, main ):
        """
            Start mininet and assign controllers
        """
        import time

        topology = main.params[ 'CASE11' ][ 'topo' ]
        main.log.report( "Start Mininet topology" )
        main.case( "Start Mininet topology" )

        main.step( "Starting Mininet Topology" )
        topoResult = main.Mininet1.startNet( mnCmd=topology )
        stepResult = topoResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully loaded topology",
                                 onfail="Failed to load topology" )
        # Exit if topology did not load properly
        if not topoResult:
            main.cleanAndExit()

        main.step( "Assign switches to controllers." )
        assignResult = main.TRUE
        for i in range( 1, 8 ):
            assignResult = assignResult & main.Mininet1.assignSwController( sw="s" + str( i ),
                                                                            ip=main.Cluster.getIps(),
                                                                            port='6653' )
        time.sleep( main.mnCfgSleep )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully assign switches to controllers",
                                 onfail="Failed to assign switches to controllers" )

    def CASE12( self, main ):
        """
            Tests using through ONOS CLI handles
        """
        main.case( "Test some onos commands through CLI. " )
        main.log.debug( main.Cluster.active( 0 ).CLI.sendline( "summary" ) )
        main.log.debug( main.Cluster.active( 1 ).CLI.sendline( "devices" ) )

    def CASE22( self, main ):
        """
            Tests using ONOS REST API handles
        """
        main.case( " Sample tests using ONOS REST API handles. " )
        main.log.debug( main.Cluster.active( 0 ).REST.send( "/devices" ) )
        main.log.debug( main.Cluster.active( 2 ).REST.apps() )

    def CASE32( self, main ):
        """
            Configure fwd app from .params json string with parameter configured
            Check if configuration successful
            Run pingall to check connectivity
            Check ONOS log for warning/error/exceptions
        """
        main.case( "Configure onos-app-fwd and check if configuration successful. " )
        main.step( "Install reactive forwarding app." )
        installResults = main.Cluster.active( 0 ).CLI.activateApp( "org.onosproject.fwd" )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=installResults,
                                 onpass="Configure fwd successful",
                                 onfail="Configure fwd failed" )
        main.step( "Run pingall to check connectivity. " )
        pingResult = main.FALSE
        passMsg = "Reactive Pingall test passed"
        pingResult = main.Mininet1.pingall()
        if not pingResult:
            main.log.warn( "First pingall failed. Trying again..." )
            pingResult = main.Mininet1.pingall()
            passMsg += "on the second try"
        utilities.assert_equals( expect=main.TRUE,
                                 actual=pingResult,
                                 onpass=passMsg,
                                 onfail="Reactive Pingall failed, " + "one or more ping pairs failed" )
