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

# Testing the NETCONF protocol within ONOS


class FUNCnetconf:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        import time
        import imp
        import re
        """
        - Construct tests variables
        - GIT ( optional )
            - Checkout ONOS master branch
            - Pull latest ONOS code
        - Building ONOS ( optional )
            - Install ONOS package
            - Build ONOS package
        """
        try:
            from tests.dependencies.ONOSSetup import ONOSSetup
            main.testSetUp = ONOSSetup()
        except ImportError:
            main.log.error( "ONOSSetup not found. exiting the test" )
            main.cleanAndExit()
        main.testSetUp.envSetupDescription()
        stepResult = main.FALSE

        # Test variables
        try:
            main.apps = main.params[ 'ENV' ][ 'cellApps' ]
            main.dependencyPath = main.testOnDirectory + \
                                  main.params[ 'DEPENDENCY' ][ 'path' ]
            # main.topology = main.params[ 'DEPENDENCY' ][ 'topology' ]
            main.scale = ( main.params[ 'SCALE' ][ 'size' ] ).split( "," )
            wrapperFile1 = main.params[ 'DEPENDENCY' ][ 'wrapper1' ]
            wrapperFile2 = main.params[ 'DEPENDENCY' ][ 'wrapper2' ]
            wrapperFile3 = main.params[ 'DEPENDENCY' ][ 'wrapper3' ]
            main.startUpSleep = int( main.params[ 'SLEEP' ][ 'startup' ] )
            main.switchSleep = int( main.params[ 'SLEEP' ][ 'upSwitch' ] )
            main.checkTopoAttempts = int( main.params[ 'SLEEP' ][ 'topoAttempts' ] )
            main.numSwitch = int( main.params[ 'MININET' ][ 'switch' ] )

            # Config file parameters
            main.configDevicePort = main.params[ 'CONFIGURE' ][ 'cfgDevicePort' ]
            main.configDriver = main.params[ 'CONFIGURE' ][ 'cfgDriver' ]
            main.configApps = main.params[ 'CONFIGURE' ][ 'cfgApps' ]
            main.configName = main.params[ 'CONFIGURE' ][ 'cfgName' ]
            main.configPass = main.params[ 'CONFIGURE' ][ 'cfgPass' ]
            main.configPort = main.params[ 'CONFIGURE' ][ 'cfgAppPort' ]
            main.cycle = 0  # How many times FUNCintent has run through its tests

            main.hostsData = {}
            main.assertReturnString = ''  # Assembled assert return string

            # -- INIT SECTION, ONLY RUNS ONCE -- #

            main.netconfFunction = imp.load_source( wrapperFile2,
                                                    main.dependencyPath +
                                                    wrapperFile2 +
                                                    ".py" )

            stepResult = main.testSetUp.envSetup()
            # Uncomment out the following if a mininet topology is added
            # copyResult1 = main.ONOSbench.scp( main.Mininet1,
            #                                   main.dependencyPath +
            #                                   main.topology,
            #                                   main.Mininet1.home + "custom/",
            #                                   direction="to" )
        except Exception as e:
            main.testSetUp.envSetupException( e )
        main.testSetUp.evnSetupConclusion( stepResult )


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
        main.testSetUp.ONOSSetUp( main.Mininet1, main.Cluster, True )

    def CASE19( self, main ):
        """
            Copy the karaf.log files after each testcase cycle
        """
        try:
            from tests.dependencies.utils import Utils
        except ImportError:
            main.log.error( "Utils not found exiting the test" )
            main.cleanAndExit()
        try:
            main.Utils
        except ( NameError, AttributeError ):
            main.Utils = Utils()
        main.Utils.copyKarafLog( "cycle" + str( main.cycle ) )
    def CASE100( self, main ):
        """
            Start NETCONF app and OFC-Server or make sure that they are already running
        """
        assert main, "There is no main"

        testResult = main.FALSE
        main.testName = "Start up NETCONF app in all nodes"
        main.case( main.testName + " Test - " + str( main.Cluster.numCtrls ) +
                   " NODE(S)" )
        main.step( "Starting NETCONF app" )
        main.assertReturnString = "Assertion result for starting NETCONF app"
        testResult = main.netconfFunction.startApp( main )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        main.step( "Starting OFC-Server" )
        main.assertReturnString = "Assertion result for starting OFC-Server"
        testResult = main.netconfFunction.startOFC( main )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )
        time.sleep( main.startUpSleep )

    def CASE200( self, main ):
        """
            Create or modify a Configuration file
                -The file is built from information loaded from the .params file
        """
        assert main, "There is no main"

        main.testName = "Assemble the configuration"
        main.case( main.testName + " Test - " + str( main.Cluster.numCtrls ) +
                   " NODES(S)" )
        main.step( "Assembling configuration file" )
        main.assertReturnString = "Assertion result for assembling configuration file"
        testResult = main.FALSE
        testResult = main.netconfFunction.createConfig( main )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )
        time.sleep( main.startUpSleep )

    def CASE300( self, main ):
        """
            Push a configuration and bring up a switch
        """
        assert main, "There is no main"

        main.testName = "Uploading the configuration"
        main.case( main.testName + " Test - " + str( main.Cluster.numCtrls ) +
                   " NODES(S)" )
        main.step( "Sending the configuration file" )
        main.assertReturnString = "Assertion result for sending the configuration file"
        testResult = main.FALSE

        testResult = main.netconfFunction.sendConfig( main )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        time.sleep( main.switchSleep )

        main.step( "Confirming the device was configured" )
        main.assertReturnString = "Assertion result for confirming a configuration."
        testResult = main.FALSE

        testResult = main.netconfFunction.devices( main )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

    def CASE400( self, main ):
        """
            Bring down a switch
            This test case is not yet possible, but the functionality needed to
            perform it is planned to be added
                There is a message that is sent "Device () has closed session"
                when the device disconnects from onos for some reason.
                    Because of the triggers for this message are not practical
                    to activate this will likely not be used to implement the test
                    case at this time
            Possible ways to do this may include bringing down mininet then checking
            ONOS to see if it was recongnized the device being disconnected
        """
