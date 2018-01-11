"""
Copyright 2015 Open Networking Foundation ( ONF )

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
# Testing the basic intent functionality of ONOS


class FUNCnetCfg:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        import imp
        import re
        """
        - Construct tests variables
        - GIT ( optional )
            - Checkout ONOS master branch
            - Pull latest ONOS code
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
            wrapperFile1 = main.params[ 'DEPENDENCY' ][ 'wrapper1' ]
            wrapperFile2 = main.params[ 'DEPENDENCY' ][ 'wrapper2' ]
            wrapperFile3 = main.params[ 'DEPENDENCY' ][ 'wrapper3' ]
            main.startUpSleep = int( main.params[ 'SLEEP' ][ 'startup' ] )
            main.gossipTime = int( main.params[ 'SLEEP' ][ 'cfgGossip' ] )
            main.SetNetCfgSleep = int( main.params[ 'SLEEP' ][ 'SetNetCfgSleep' ] )
            main.hostsData = {}
            main.retrytimes = int( main.params[ 'RETRY' ] )
            main.retrysleep = int( main.params[ 'RetrySleep' ] )

            # -- INIT SECTION, SHOULD ONLY BE RUN ONCE -- #
            main.netCfg = imp.load_source( wrapperFile2,
                                           main.dependencyPath +
                                           wrapperFile2 +
                                           ".py" )

            stepResult = main.testSetUp.envSetup()
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
        - Install ONOS cluster
        - Verify ONOS start up
        - Connect to cli
        """
        import time
        main.testSetUp.ONOSSetUp( main.Cluster )

    def CASE8( self, main ):
        """
        Compare Topo
        """
        try:
            from tests.dependencies.topology import Topology
        except ImportError:
            main.log.error( "Topology not found exiting the test" )
            main.cleanAndExit()
        try:
            main.topoRelated
        except ( NameError, AttributeError ):
            main.topoRelated = Topology()
        main.topoRelated.compareTopos( main.Mininet1 )

    def CASE9( self, main ):
        """
            Report errors/warnings/exceptions
        """
        main.log.info( "Error report: \n" )
        main.ONOSbench.logReport(
                main.Cluster.active( 0 ).ipAddress,
                [ "INFO", "WARN", "ERROR", "Except" ],
                "s" )
        # main.ONOSbench.logReport( globalONOSip[ 1 ], [ "INFO" ], "d" )

    def CASE10( self, main ):
        """
            Start Mininet topology with OF 1.0 switches
        """
        main.OFProtocol = "1.0"
        main.log.report( "Start Mininet topology with OF 1.0 switches" )
        main.case( "Start Mininet topology with OF 1.0 switches" )
        main.caseExplanation = "Start mininet topology with OF 1.0 " +\
                                "switches to test intents, exits out if " +\
                                "topology did not start correctly"

        main.step( "Starting Mininet topology with OF 1.0 switches" )
        args = "--controller none --switch ovs,protocols=OpenFlow10"
        switches = int( main.params[ 'MININET' ][ 'switch' ] )
        cmd = "mn --topo linear,{} {}".format( switches, args )
        topoResult = main.Mininet1.startNet( mnCmd=cmd )
        stepResult = topoResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully loaded topology",
                                 onfail="Failed to load topology" )
        # Exit if topology did not load properly
        if not topoResult:
            main.cleanAndExit()

    def CASE11( self, main ):
        """
            Start Mininet topology with OF 1.3 switches
        """
        import re
        main.OFProtocol = "1.3"
        main.log.report( "Start Mininet topology with OF 1.3 switches" )
        main.case( "Start Mininet topology with OF 1.3 switches" )
        main.caseExplanation = "Start mininet topology with OF 1.3 " +\
                                "switches to test intents, exits out if " +\
                                "topology did not start correctly"

        main.step( "Starting Mininet topology with OF 1.3 switches" )
        args = "--controller none --switch ovs,protocols=OpenFlow13"
        switches = int( main.params[ 'MININET' ][ 'switch' ] )
        cmd = "mn --topo linear,{} {}".format( switches, args )
        topoResult = main.Mininet1.startNet( mnCmd=cmd )
        stepResult = topoResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully loaded topology",
                                 onfail="Failed to load topology" )
        # Exit if topology did not load properly
        if not topoResult:
            main.cleanAndExit()

        tempONOSip = main.Cluster.getIps()

        swList = [ "s" + str( i ) for i in range( 1, switches + 1 ) ]
        assignResult = main.Mininet1.assignSwController( sw=swList,
                                                         ip=tempONOSip,
                                                         port='6653' )
        if not assignResult:
            main.cleanAndExit()

        assignResult = main.TRUE
        for sw in swList:
            response = main.Mininet1.getSwController( "s" + str( i ) )
            main.log.info( "Response is " + str( response ) )
            for ip in tempONOSip:
                if re.search( "tcp:" + ip, response ):
                    assignResult = assignResult and main.TRUE
                else:
                    assignResult = assignResult and main.FALSE
        stepResult = assignResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully assigned switches" +
                                        "to controller",
                                 onfail="Failed to assign switches to " +
                                        "controller" )

    def CASE14( self, main ):
        """
            Stop mininet
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
        main.Utils.mininetCleanIntro()
        topoResult = main.Utils.mininetCleanup( main.Mininet1 )
        # Exit if topology did not load properly
        if not topoResult:
            main.cleanAndExit()

    def CASE20( self, main ):
        """
        Add some device configurations and then check they are distributed
        to all nodes
        """
        import time
        import json
        import os
        main.case( "Add Network configurations to the cluster" )
        main.caseExplanation = "Add Network Configurations for devices" +\
                               " not discovered yet. One device is allowed" +\
                               ", the other disallowed."

        pprint = main.Cluster.active( 0 ).REST.pprint

        main.step( "Add Net Cfg for switch1" )

        try:
            with open( os.path.dirname( main.testFile ) + '/dependencies/s1Json', 'r' ) as s1Jsondata:
                s1Json = json.load( s1Jsondata )
        except IOError:
            main.log.exception( "s1Json File not found." )
            main.cleanAndExit()
        main.log.info( "s1Json:" + str( s1Json ) )

        main.s1Json = s1Json
        setS1Allow = main.Cluster.active( 0 ).REST.setNetCfg( s1Json,
                                                              subjectClass="devices",
                                                              subjectKey="of:0000000000000001",
                                                              configKey="basic" )
        s1Result = False
        # Wait 5 secs after set up netCfg
        time.sleep( main.SetNetCfgSleep )
        if setS1Allow:
            getS1 = utilities.retry( f=main.Cluster.active( 0 ).REST.getNetCfg,
                                     retValue=False,
                                     kwargs={ "subjectClass": "devices",
                                              "subjectKey": "of:0000000000000001",
                                              "configKey": "basic" },
                                     attempts=main.retrytimes,
                                     sleep=main.retrysleep )
            onosCfg = pprint( getS1 )
            sentCfg = pprint( s1Json )
            if onosCfg == sentCfg:
                main.log.info( "ONOS NetCfg match what was sent" )
                s1Result = True
            else:
                main.log.error( "ONOS NetCfg doesn't match what was sent" )
                main.log.debug( "ONOS config: {}".format( onosCfg ) )
                main.log.debug( "Sent config: {}".format( sentCfg ) )
                utilities.retry( f=main.Cluster.active( 0 ).REST.getNetCfg,
                                 retValue=False,
                                 attempts=main.retrytimes,
                                 sleep=main.retrysleep )
        utilities.assert_equals( expect=True,
                                 actual=s1Result,
                                 onpass="Net Cfg added for device s1",
                                 onfail="Net Cfg for device s1 not correctly set" )

        main.step( "Add Net Cfg for switch3" )

        try:
            with open( os.path.dirname( main.testFile ) + '/dependencies/s3Json', 'r' ) as s3Jsondata:
                s3Json = json.load( s3Jsondata )
        except IOError:
            main.log.exception( "s3Json File not found" )
            main.cleanAndExit()
        main.log.info( "s3Json:" + str( s3Json ) )

        main.s3Json = s3Json
        setS3Disallow = main.Cluster.active( 0 ).REST.setNetCfg( s3Json,
                                                                 subjectClass="devices",
                                                                 subjectKey="of:0000000000000003",
                                                                 configKey="basic" )
        s3Result = False
        time.sleep( main.SetNetCfgSleep )
        if setS3Disallow:
            # Check what we set is what is in ONOS
            getS3 = utilities.retry( f=main.Cluster.active( 0 ).REST.getNetCfg,
                                     retValue=False,
                                     kwargs={ "subjectClass": "devices",
                                              "subjectKey": "of:0000000000000003",
                                              "configKey": "basic" },
                                     attempts=main.retrytimes,
                                     sleep=main.retrysleep )
            onosCfg = pprint( getS3 )
            sentCfg = pprint( s3Json )
            if onosCfg == sentCfg:
                main.log.info( "ONOS NetCfg match what was sent" )
                s3Result = True
            else:
                main.log.error( "ONOS NetCfg doesn't match what was sent" )
                main.log.debug( "ONOS config: {}".format( onosCfg ) )
                main.log.debug( "Sent config: {}".format( sentCfg ) )
                utilities.retry( f=main.Cluster.active( 0 ).REST.getNetCfg,
                                 retValue=False,
                                 attempts=main.retrytimes,
                                 sleep=main.retrysleep )
        utilities.assert_equals( expect=True,
                                 actual=s3Result,
                                 onpass="Net Cfg added for device s3",
                                 onfail="Net Cfg for device s3 not correctly set" )
        main.netCfg.compareCfg( main, main.gossipTime )

    def CASE21( self, main ):
        """
        Initial check of devices
        """
        import json
        try:
            assert main.s1Json, "s1Json not defined"
        except AssertionError:
            main.log.exception( "Case Prerequisites not set: " )
            main.cleanAndExit()
        main.case( "Check Devices After they initially connect to ONOS" )

        main.netCfg.compareCfg( main )

        main.step( "ONOS should only show devices S1, S2, and S4" )
        devices = main.Cluster.active( 0 ).REST.devices()
        main.log.debug( main.Cluster.active( 0 ).REST.pprint( devices ) )
        allowedDevices = [ "of:{}".format( str( i ).zfill( 16 ) ) for i in [ 1, 2, 4 ] ]
        main.log.debug( allowedDevices )
        onosDevices = []
        try:
            for sw in json.loads( devices ):
                onosDevices.append( str( sw[ 'id' ] ) )
            onosDevices.sort()
            main.log.debug( onosDevices )
        except( TypeError, ValueError ):
            main.log.error( "Problem loading devices" )
        utilities.assert_equals( expect=allowedDevices,
                                 actual=onosDevices,
                                 onpass="Only allowed devices are in ONOS",
                                 onfail="ONOS devices doesn't match the list" +
                                        " of allowed devices" )
        main.step( "Check device annotations" )
        keys = [ 'name', 'owner', 'rackAddress' ]
        try:
            for sw in json.loads( devices ):
                if "of:0000000000000001" in sw[ 'id' ]:
                    s1Correct = True
                    for k in keys:
                        if str( sw.get( 'annotations', {} ).get( k ) ) != str( main.s1Json[ k ] ):
                            s1Correct = False
                            main.log.debug( "{} is wrong on s1".format( k ) )
                    if not s1Correct:
                        main.log.error( "Annotations for s1 are incorrect: {}".format( sw ) )
        except( TypeError, ValueError ):
            main.log.error( "Problem loading devices" )
            s1Correct = False
        try:
            stepResult = s1Correct
        except NameError:
            stepResult = False
            main.log.error( "s1 not found in devices" )
        utilities.assert_equals( expect=True,
                                 actual=stepResult,
                                 onpass="Configured device's annotations are correct",
                                 onfail="Incorrect annotations for configured devices." )

    def CASE22( self, main ):
        """
        Add some device configurations for connected devices and then check
        they are distributed to all nodes
        """
        main.case( "Add Network configurations for connected devices to the cluster" )
        main.caseExplanation = "Add Network Configurations for discovered " +\
                               "devices. One device is allowed" +\
                               ", the other disallowed."
        pprint = main.Cluster.active( 0 ).REST.pprint

        main.step( "Add Net Cfg for switch2" )
        try:
            with open( os.path.dirname( main.testFile ) + '/dependencies/s2Json', 'r' ) as s2Jsondata:
                s2Json = json.load( s2Jsondata )
        except IOError:
            main.log.exception( "s2Json File not found" )
            main.cleanAndExit()
        main.log.info( "s2Json:" + str( s2Json ) )
        main.s2Json = s2Json
        setS2Allow = main.Cluster.active( 1 ).REST.setNetCfg( s2Json,
                                                              subjectClass="devices",
                                                              subjectKey="of:0000000000000002",
                                                              configKey="basic" )
        s2Result = False
        if setS2Allow:
            # Check what we set is what is in ONOS
            getS2 = utilities.retry( f=main.Cluster.active( 1 ).REST.getNetCfg,
                                     retValue=False,
                                     kwargs={ "subjectClass": "devices",
                                              "subjectKey": "of:0000000000000002",
                                              "configKey": "basic" },
                                     attempts=main.retrytimes,
                                     sleep=main.retrysleep )
            onosCfg = pprint( getS2 )
            sentCfg = pprint( s2Json )
            if onosCfg == sentCfg:
                s2Result = True
            else:
                main.log.error( "ONOS NetCfg doesn't match what was sent" )
                main.log.debug( "ONOS config: {}".format( onosCfg ) )
                main.log.debug( "Sent config: {}".format( sentCfg ) )
                utilities.retry( f=main.Cluster.active( 1 ).REST.getNetCfg,
                                 retValue=False,
                                 attempts=main.retrytimes,
                                 sleep=main.retrysleep )
        utilities.assert_equals( expect=True,
                                 actual=s2Result,
                                 onpass="Net Cfg added for device s2",
                                 onfail="Net Cfg for device s2 not correctly set" )
        main.step( "Add Net Cfg for switch4" )

        try:
            with open( os.path.dirname( main.testFile ) + '/dependencies/s4Json', 'r' ) as s4Jsondata:
                s4Json = json.load( s4Jsondata )
        except IOError:
            main.log.exception( "s4Json File not found" )
            main.cleanAndExit()
        main.log.info( "s4Json:" + str( s4Json ) )
        main.s4Json = s4Json
        setS4Disallow = main.Cluster.active( 2 ).REST.setNetCfg( s4Json,
                                                                 subjectClass="devices",
                                                                 subjectKey="of:0000000000000004",
                                                                 configKey="basic" )
        s4Result = False
        if setS4Disallow:
            # Check what we set is what is in ONOS
            getS4 = utilities.retry( f=main.Cluster.active( 2 ).REST.getNetCfg,
                                     retValue=False,
                                     kwargs={ "subjectClass": "devices",
                                              "subjectKey": "of:0000000000000004",
                                              "configKey": "basic" },
                                     attempts=main.retrytimes,
                                     sleep=main.retrysleep )

            onosCfg = pprint( getS4 )
            sentCfg = pprint( s4Json )
            if onosCfg == sentCfg:
                s4Result = True
            else:
                main.log.error( "ONOS NetCfg doesn't match what was sent" )
                main.log.debug( "ONOS config: {}".format( onosCfg ) )
                main.log.debug( "Sent config: {}".format( sentCfg ) )
                main.step( "Retrying main.Cluster.active( 2 ).REST.getNetCfg" )
                utilities.retry( f=main.Cluster.active( 2 ).REST.getNetCfg,
                                 retValue=False,
                                 attempts=main.retrytimes,
                                 sleep=main.retrysleep )
        utilities.assert_equals( expect=True,
                                 actual=s4Result,
                                 onpass="Net Cfg added for device s4",
                                 onfail="Net Cfg for device s4 not correctly set" )

        main.netCfg.compareCfg( main, main.gossipTime )

    def CASE23( self, main ):
        """
        Check of devices after all Network Configurations are set
        """
        import json
        try:
            assert main.s1Json, "s1Json not defined"
            assert main.s2Json, "s2Json not defined"
        except AssertionError:
            main.log.exception( "Case Prerequisites not set: " )
            main.cleanAndExit()
        main.case( "Check Devices after all configurations are set" )

        main.netCfg.compareCfg( main )

        main.step( "ONOS should only show devices S1 and S2" )
        devices = main.Cluster.active( 0 ).REST.devices()
        main.log.debug( main.Cluster.active( 0 ).REST.pprint( devices ) )
        allowedDevices = [ "of:{}".format( str( i ).zfill( 16 ) ) for i in [ 1, 2 ] ]
        onosDevices = []
        try:
            for sw in json.loads( devices ):
                onosDevices.append( str( sw.get( 'id' ) ) )
            onosDevices.sort()
            failMsg = "ONOS devices doesn't match the list of allowed devices.\n"
            failMsg += "Expected devices: {}\nActual devices: {}".format( allowedDevices,
                                                                          onosDevices )
        except( TypeError, ValueError ):
            main.log.error( "Problem loading devices" )
        utilities.assert_equals( expect=allowedDevices,
                                 actual=onosDevices,
                                 onpass="Only allowed devices are in ONOS",
                                 onfail=failMsg )

        main.step( "Check device annotations" )
        stepResult = utilities.retry( f=main.netCfg.checkAllDeviceAnnotations,
                                      args=( main, json ),
                                      retValue=False,
                                      attempts=main.retrytimes,
                                      sleep=main.retrysleep )
        utilities.assert_equals( expect=True,
                                 actual=stepResult,
                                 onpass="Configured devices' annotations are correct",
                                 onfail="Incorrect annotations for configured devices." )

    def CASE24( self, main ):
        """
        Testing removal of configurations
        """
        import time
        try:
            assert main.s1Json, "s1Json not defined"
            assert main.s2Json, "s2Json not defined"
            assert main.s3Json, "s3Json not defined"
            assert main.s4Json, "s4Json not defined"
        except AssertionError:
            main.log.exception( "Case Prerequisites not set: " )
            main.cleanAndExit()
        main.case( "Testing removal of configurations" )
        main.step( "Remove 'allowed' configuration from all devices" )

        s1Json = main.s1Json  # NOTE: This is a reference
        try:
            del s1Json[ 'allowed' ]
        except KeyError:
            main.log.exception( "Key not found" )
        setS1 = main.Cluster.active( 0 ).REST.setNetCfg( s1Json,
                                                         subjectClass="devices",
                                                         subjectKey="of:0000000000000001",
                                                         configKey="basic" )

        s2Json = main.s2Json  # NOTE: This is a reference
        try:
            time.sleep( main.gossipTime )
            del s2Json[ 'allowed' ]
        except KeyError:
            main.log.exception( "Key not found" )
        setS2 = main.Cluster.active( 1 ).REST.setNetCfg( s2Json,
                                                         subjectClass="devices",
                                                         subjectKey="of:0000000000000002",
                                                         configKey="basic" )

        s3Json = main.s3Json  # NOTE: This is a reference
        try:
            time.sleep( main.gossipTime )
            del s3Json[ 'allowed' ]
        except KeyError:
            main.log.exception( "Key not found" )
        setS3 = main.Cluster.active( 2 ).REST.setNetCfg( s3Json,
                                                         subjectClass="devices",
                                                         subjectKey="of:0000000000000003",
                                                         configKey="basic" )

        s4Json = main.s4Json  # NOTE: This is a reference
        try:
            time.sleep( main.gossipTime )
            del s4Json[ 'allowed' ]
        except KeyError:
            main.log.exception( "Key not found" )
        setS4 = main.Cluster.active( 2 ).REST.setNetCfg( s4Json,
                                                         subjectClass="devices",
                                                         subjectKey="of:0000000000000004",
                                                         configKey="basic" )
        removeAllowed = setS1 and setS2 and setS3 and setS4
        utilities.assert_equals( expect=main.TRUE,
                                 actual=removeAllowed,
                                 onpass="Successfully removed 'allowed' config from devices",
                                 onfail="Failed to remove the 'allowed' config key." )

        main.netCfg.compareCfg( main, main.gossipTime )

        main.step( "Delete basic config for s1 and s2" )
        removeS1 = main.Cluster.active( 0 ).REST.removeNetCfg( subjectClass="devices",
                                                               subjectKey="of:0000000000000001",
                                                               configKey="basic" )
        removeS2 = main.Cluster.active( 1 ).REST.removeNetCfg( subjectClass="devices",
                                                               subjectKey="of:0000000000000002",
                                                               configKey="basic" )
        removeSingles = removeS1 and removeS2
        utilities.assert_equals( expect=main.TRUE,
                                 actual=removeSingles,
                                 onpass="Successfully removed S1 and S2 basic config",
                                 onfail="Failed to removed S1 and S2 basic config" )

        main.netCfg.compareCfg( main, main.gossipTime )

        main.step( "Delete the net config for S3" )
        removeS3 = main.Cluster.active( 2 ).REST.removeNetCfg( subjectClass="devices",
                                                               subjectKey="of:0000000000000003" )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=removeS3,
                                 onpass="Successfully removed S3's config",
                                 onfail="Failed to removed S3's config" )

        main.netCfg.compareCfg( main, main.gossipTime )

        main.step( "Delete the net config for all devices" )
        remove = main.Cluster.active( 2 ).REST.removeNetCfg( subjectClass="devices" )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=remove,
                                 onpass="Successfully removed device config",
                                 onfail="Failed to remove device config" )

        main.netCfg.compareCfg( main, main.gossipTime )

        main.step( "Assert the net config for devices is empty" )

        get = utilities.retry( f=main.Cluster.active( 2 ).REST.getNetCfg,
                               retValue=False,
                               kwargs={ "subjectClass": "devices" },
                               sleep=main.retrysleep,
                               attempts=main.retrytimes )

        utilities.assert_equals( expect='{}',
                                 actual=get,
                                 onpass="Successfully removed device config",
                                 onfail="Failed to remove device config" )

    def CASE25( self, main ):
        """
            Use network-cfg.json to configure devices during ONOS startup
        """
        main.case( "Preparing network-cfg.json to load configurations" )
        main.step( "Moving network-cfg.json to $ONOS_ROOT/tools/package/config/" )
        prestartResult = main.TRUE
        srcPath = "~/OnosSystemTest/TestON/tests/FUNC/FUNCnetCfg/dependencies/network-cfg.json"
        dstPath = "~/onos/tools/package/config/network-cfg.json"
        prestartResult = main.ONOSbench.scp( main.ONOSbench, srcPath, dstPath, direction="to" )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=prestartResult,
                                 onpass="Successfully copied network-cfg.json to target directory",
                                 onfail="Failed to copy network-cfg.json to target directory" )

    def CASE26( self, main ):
        """
            Check to see that pre-startup configurations were set correctly
        """
        import json
        main.case( "Check to see if the pre-startup configurations were set, then remove their allowed status" )
        main.step( "Checking configurations for Switches 5 and 6" )
        main.step( "ONOS should only show devices S1, S2, S4, and S5" )  # and S6
        devices = main.Cluster.active( 0 ).REST.devices()
        main.log.debug( main.Cluster.active( 0 ).REST.pprint( devices ) )
        allowedDevices = [ "of:{}".format( str( i ).zfill( 16 ) ) for i in [ 1, 2, 4, 5 ] ]  # 6
        main.log.debug( allowedDevices )
        onosDevices = []
        try:
            for sw in json.loads( devices ):
                onosDevices.append( str( sw[ 'id' ] ) )
            onosDevices.sort()
            main.log.debug( onosDevices )
        except( TypeError, ValueError ):
            main.log.error( "Problem loading devices" )
        utilities.assert_equals( expect=allowedDevices,
                                 actual=onosDevices,
                                 onpass="Only allowed devices are in ONOS",
                                 onfail="ONOS devices doesn't match the list" +
                                        " of allowed devices" )

        main.step( "Removing allowed status from Switches 5 and 6" )
        try:
            with open( os.path.dirname( main.testFile ) + '/dependencies/s5Json', 'r' ) as s5Jsondata:
                main.s5Json = json.load( s5Jsondata )
        except IOError:
            main.log.exception( "s5Json File not found" )
            main.cleanAndExit()
        main.log.info( "s5Json:" + str( main.s5Json ) )

        try:
            with open( os.path.dirname( main.testFile ) + '/dependencies/s6Json', 'r' ) as s6Jsondata:
                main.s6Json = json.load( s6Jsondata )
        except IOError:
            main.log.exception( "s6Json File not found" )
            main.cleanAndExit()
        main.log.info( "s6Json:" + str( main.s6Json ) )

        s5Json = main.s5Json
        setS1 = main.Cluster.active( 0 ).REST.setNetCfg( s5Json,
                                                         subjectClass="devices",
                                                         subjectKey="of:0000000000000005",
                                                         configKey="basic" )

        # Wait 5 secs after set up netCfg
        time.sleep( main.SetNetCfgSleep )

        s6Json = main.s6Json
        setS1 = main.Cluster.active( 0 ).REST.setNetCfg( s6Json,
                                                         subjectClass="devices",
                                                         subjectKey="of:0000000000000006",
                                                         configKey="basic" )

        # Wait 5 secs after set up netCfg
        time.sleep( main.SetNetCfgSleep )

    def CASE27( self, main ):
        """
        1 ) A = get /network/configuration
        2 ) Post A
        3 ) Compare A with ONOS
        4 ) Modify A so S6 is disallowed
        5 ) Check

        """
        import json
        pprint = main.Cluster.active( 0 ).REST.pprint
        main.case( "Posting network configurations to the top level web resource" )
        main.step( "Get json object from Net Cfg" )
        getinfo = utilities.retry( f=main.Cluster.active( 0 ).REST.getNetCfg,
                                   retValue=False,
                                   sleep=main.retrysleep,
                                   attempts=main.retrytimes )

        main.log.debug( getinfo )
        main.step( "Posting json object to Net Cfg" )
        postinfo = main.Cluster.active( 0 ).REST.setNetCfg( json.loads( getinfo ) )
        main.step( "Compare device with ONOS" )
        main.netCfg.compareCfg( main )
        main.step( "ONOS should only show devices S1, S2, S4, S5 and S6" )
        devices = main.Cluster.active( 0 ).REST.devices()
        main.log.debug( main.Cluster.active( 0 ).REST.pprint( devices ) )
        allowedDevices = [ "of:{}".format( str( i ).zfill( 16 ) ) for i in [ 1, 2, 4, 5, 6 ] ]
        onosDevices = []
        try:
            for sw in json.loads( devices ):
                onosDevices.append( str( sw.get( 'id' ) ) )
            onosDevices.sort()
            failMsg = "ONOS devices doesn't match the list of allowed devices. \n"
            failMsg += "Expected devices: {}\nActual devices: {}".format( allowedDevices, onosDevices )
        except( TypeError, ValueError ):
            main.log.error( "Problem loading devices" )
        utilities.assert_equals( expect=allowedDevices, actual=onosDevices,
                                 onpass="Only allowed devices are in ONOS", onfail=failMsg )

        main.step( "Modify json object so S6 is disallowed" )
        main.s6Json = { "allowed": False }
        s6Json = main.s6Json
        setS6Disallow = main.Cluster.active( 0 ).REST.setNetCfg( s6Json,
                                                                 subjectClass="devices",
                                                                 subjectKey="of:0000000000000006",
                                                                 configKey="basic" )
        s6Result = False
        if setS6Disallow:
            getS6 = utilities.retry( f=main.Cluster.active( 0 ).REST.getNetCfg,
                                     retValue=False,
                                     kwargs={ "subjectClass": "devices",
                                              "subjectKey": "of:0000000000000006",
                                              "configKey": "basic" },
                                     sleep=main.retrysleep,
                                     attempts=main.retrytimes )
            onosCfg = pprint( getS6 )
            sentCfg = pprint( s6Json )
            if onosCfg == sentCfg:
                s6Result = True
            else:
                main.log.error( "ONOS NetCfg doesn't match what was sent" )
                main.log.debug( "ONOS config: {}".format( onosCfg ) )
                main.log.debug( "Sent config: {}".format( sentCfg ) )
                utilities.retry( f=main.Cluster.active( 0 ).REST.getNetCfg,
                                 retValue=False,
                                 attempts=main.retrytimes,
                                 sleep=main.retrysleep )
        utilities.assert_equals( expect=True, actual=s6Result,
                                 onpass="Net Cfg added for devices s6",
                                 onfail="Net Cfg for device s6 not correctly set" )
