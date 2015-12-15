
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
        - Building ONOS ( optional )
            - Install ONOS package
            - Build ONOS package
        """

        main.case( "Constructing test variables and building ONOS package" )
        main.step( "Constructing test variables" )
        main.caseExplanation = "This test case is mainly for loading " +\
                               "from params file, and pull and build the " +\
                               " latest ONOS package"
        stepResult = main.FALSE

        # Test variables
        try:
            main.testOnDirectory = re.sub( "(/tests)$", "", main.testDir )
            main.apps = main.params[ 'ENV' ][ 'cellApps' ]
            gitBranch = main.params[ 'GIT' ][ 'branch' ]
            main.dependencyPath = main.testOnDirectory + \
                                  main.params[ 'DEPENDENCY' ][ 'path' ]
            if main.ONOSbench.maxNodes:
                main.maxNodes = int( main.ONOSbench.maxNodes )
            else:
                main.maxNodes = 0
            wrapperFile1 = main.params[ 'DEPENDENCY' ][ 'wrapper1' ]
            wrapperFile2 = main.params[ 'DEPENDENCY' ][ 'wrapper2' ]
            wrapperFile3 = main.params[ 'DEPENDENCY' ][ 'wrapper3' ]
            main.startUpSleep = int( main.params[ 'SLEEP' ][ 'startup' ] )
            main.gossipTime = int( main.params[ 'SLEEP'][ 'cfgGossip' ] )
            gitPull = main.params[ 'GIT' ][ 'pull' ]
            main.cellData = {}  # for creating cell file
            main.hostsData = {}
            main.nodes = []
            main.ONOSip = []

            main.ONOSip = main.ONOSbench.getOnosIps()

            # Assigning ONOS cli handles to a list
            try:
                for i in range( 1, main.maxNodes + 1 ):
                    main.nodes.append( getattr( main, 'ONOSrest' + str( i ) ) )
            except AttributeError:
                main.log.warn( "A " + str( main.maxNodes ) + " node cluster " +
                               "was defined in env variables, but only " +
                               str( len( main.nodes ) ) +
                               " nodes were defined in the .topo file. " +
                               "Using " + str( len( main.nodes ) ) +
                               " nodes for the test." )

            main.numCtrls = len( main.nodes )

            # -- INIT SECTION, SHOULD ONLY BE RUN ONCE -- #
            main.startUp = imp.load_source( wrapperFile1,
                                            main.dependencyPath +
                                            wrapperFile1 +
                                            ".py" )

            main.netCfg = imp.load_source( wrapperFile2,
                                           main.dependencyPath +
                                           wrapperFile2 +
                                           ".py" )

            main.topo = imp.load_source( wrapperFile3,
                                         main.dependencyPath +
                                         wrapperFile3 +
                                         ".py" )

            if main.nodes:
                stepResult = main.TRUE
            else:
                main.log.error( "Did not properly created list of ONOS handle" )
                stepResult = main.FALSE
        except Exception as e:
            main.log.exception(e)
            main.cleanup()
            main.exit()

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
        import time
        main.case( "Starting up " + str( main.numCtrls ) +
                   " node(s) ONOS cluster" )
        main.caseExplanation = "Set up ONOS with " + str( main.numCtrls ) +\
                                " node(s) ONOS cluster"

        # kill off all onos processes
        main.log.info( "Safety check, killing all ONOS processes" +
                       " before initiating environment setup" )

        for i in range( main.maxNodes ):
            main.ONOSbench.onosStop( main.ONOSip[ i ] )
            main.ONOSbench.onosDie( main.ONOSip[ i ] )

        tempOnosIp = []
        for i in range( main.numCtrls ):
            tempOnosIp.append( main.ONOSip[i] )

        main.ONOSbench.createCellFile( main.ONOSbench.ip_address,
                                       "temp", main.Mininet1.ip_address,
                                       main.apps, tempOnosIp )

        main.step( "Apply cell to environment" )
        cellResult = main.ONOSbench.setCell( "temp" )
        verifyResult = main.ONOSbench.verifyCell()
        stepResult = cellResult and verifyResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully applied cell to environment",
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
        for ip in main.ONOSip:
            onosUninstallResult = onosUninstallResult and \
                    main.ONOSbench.onosUninstall( nodeIp=ip )
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

    def CASE8( self, main ):
        """
        Compare Topo
        """
        import json

        main.case( "Compare ONOS Topology view to Mininet topology" )
        main.caseExplanation = "Compare topology elements between Mininet" +\
                                " and ONOS"

        main.step( "Gathering topology information" )
        # TODO: add a parameterized sleep here
        devicesResults = main.TRUE
        linksResults = main.TRUE
        hostsResults = main.TRUE
        devices = main.topo.getAllDevices( main )
        hosts = main.topo.getAllHosts( main )
        ports = main.topo.getAllPorts( main )
        links = main.topo.getAllLinks( main )
        clusters = main.topo.getAllClusters( main )

        mnSwitches = main.Mininet1.getSwitches()
        mnLinks = main.Mininet1.getLinks()
        mnHosts = main.Mininet1.getHosts()

        main.step( "Comparing MN topology to ONOS topology" )
        for controller in range( main.numCtrls ):
            controllerStr = str( controller + 1 )
            if devices[ controller ] and ports[ controller ] and\
               "Error" not in devices[ controller ] and\
               "Error" not in ports[ controller ]:

                currentDevicesResult = main.Mininet1.compareSwitches(
                        mnSwitches,
                        json.loads( devices[ controller ] ),
                        json.loads( ports[ controller ] ) )
            else:
                currentDevicesResult = main.FALSE
            utilities.assert_equals( expect=main.TRUE,
                                     actual=currentDevicesResult,
                                     onpass="ONOS" + controllerStr +
                                     " Switches view is correct",
                                     onfail="ONOS" + controllerStr +
                                     " Switches view is incorrect" )

            if links[ controller ] and "Error" not in links[ controller ]:
                currentLinksResult = main.Mininet1.compareLinks(
                        mnSwitches, mnLinks,
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
                        mnHosts,
                        json.loads( hosts[ controller ] ) )
            else:
                currentHostsResult = main.FALSE
            utilities.assert_equals( expect=main.TRUE,
                                     actual=currentHostsResult,
                                     onpass="ONOS" + controllerStr +
                                     " hosts exist in Mininet",
                                     onfail="ONOS" + controllerStr +
                                     " hosts don't match Mininet" )

    def CASE9( self, main ):
        '''
            Report errors/warnings/exceptions
        '''
        main.log.info( "Error report: \n" )
        main.ONOSbench.logReport(
                globalONOSip[0],
                [ "INFO", "WARN", "ERROR" , "Except" ],
                "s" )
        # main.ONOSbench.logReport( globalONOSip[1], [ "INFO" ], "d" )

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
        args = "--switch ovs,protocols=OpenFlow10"
        switches = int( main.params['MININET']['switch'] )
        cmd = "mn --topo linear,{} {}".format( switches, args )
        topoResult = main.Mininet1.startNet( mnCmd = cmd )
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
        args = "--switch ovs,protocols=OpenFlow13"
        switches = int( main.params['MININET']['switch'] )
        cmd = "mn --topo linear,{} {}".format( switches, args )
        topoResult = main.Mininet1.startNet( mnCmd = cmd )
        stepResult = topoResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully loaded topology",
                                 onfail="Failed to load topology" )
        # Exit if topology did not load properly
        if not topoResult:
            main.cleanup()
            main.exit()

        tempONOSip = []
        for i in range( main.numCtrls ):
            tempONOSip.append( main.ONOSip[ i ] )

        swList = [ "s" + str( i ) for i in range( 1, switches + 1 ) ]
        assignResult = main.Mininet1.assignSwController( sw=swList,
                                                         ip=tempONOSip,
                                                         port='6653' )
        if not assignResult:
            main.cleanup()
            main.exit()

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
        main.log.report( "Stop Mininet topology" )
        main.case( "Stop Mininet topology" )
        main.caseExplanation = "Stopping the current mininet topology " +\
                                "to start up fresh"

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

    def CASE20( self, main ):
        """
        Add some device configurations and then check they are distributed
        to all nodes
        """
        main.case( "Add Network configurations to the cluster" )
        main.caseExplanation = "Add Network Configurations for devices" +\
                               " not discovered yet. One device is allowed" +\
                               ", the other disallowed."
        pprint = main.nodes[0].pprint

        main.step( "Add Net Cfg for switch1" )
        s1Json = { "rackAddress": 1,
                   "name": "Switch1",
                   "owner": "Jimmy",
                   "allowed": True }
        main.s1Json = s1Json
        setS1Allow = main.ONOSrest1.setNetCfg( s1Json,
                                               subjectClass="devices",
                                               subjectKey="of:0000000000000001",
                                               configKey="basic" )
        s1Result = False
        if setS1Allow:
            # Check what we set is what is in ONOS
            getS1 = main.ONOSrest1.getNetCfg( subjectClass="devices",
                                              subjectKey="of:0000000000000001",
                                              configKey="basic" )
            onosCfg = pprint( getS1 )
            sentCfg = pprint( s1Json )
            if onosCfg == sentCfg:
                s1Result = True
            else:
                main.log.error( "ONOS NetCfg doesn't match what was sent" )
                main.log.debug( "ONOS config: {}".format( onosCfg ) )
                main.log.debug( "Sent config: {}".format( sentCfg ) )
        utilities.assert_equals( expect=True,
                                 actual=s1Result,
                                 onpass="Net Cfg added for device s1",
                                 onfail="Net Cfg for device s1 not correctly set" )

        main.step( "Add Net Cfg for switch3" )
        s3Json = { "rackAddress": 3,
                   "name": "Switch3",
                   "owner": "Jane",
                   "allowed": False }
        main.s3Json = s3Json
        setS3Disallow = main.ONOSrest1.setNetCfg( s3Json,
                                                  subjectClass="devices",
                                                  subjectKey="of:0000000000000003",
                                                  configKey="basic" )
        s3Result = False
        if setS3Disallow:
            # Check what we set is what is in ONOS
            getS3 = main.ONOSrest1.getNetCfg( subjectClass="devices",
                                              subjectKey="of:0000000000000003",
                                              configKey="basic" )
            onosCfg = pprint( getS3 )
            sentCfg = pprint( s3Json )
            if onosCfg == sentCfg:
                s3Result = True
            else:
                main.log.error( "ONOS NetCfg doesn't match what was sent" )
                main.log.debug( "ONOS config: {}".format( onosCfg ) )
                main.log.debug( "Sent config: {}".format( sentCfg ) )
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
            main.cleanup()
            main.exit()
        main.case( "Check Devices After they initially connect to ONOS" )

        main.netCfg.compareCfg( main )

        main.step( "ONOS should only show devices S1, S2, and S4" )
        devices = main.ONOSrest1.devices()
        main.log.debug( main.ONOSrest1.pprint( devices ) )
        allowedDevices = [ "of:{}".format( str( i ).zfill( 16 ) ) for i in [ 1, 2, 4 ] ]
        print allowedDevices
        onosDevices = []
        for sw in json.loads( devices ):
            onosDevices.append( str( sw['id'] ) )
        onosDevices.sort()
        print onosDevices
        utilities.assert_equals( expect=allowedDevices,
                                 actual=onosDevices,
                                 onpass="Only allowed devices are in ONOS",
                                 onfail="ONOS devices doesn't match the list" +
                                        " of allowed devices" )

        main.step( "Check device annotations" )
        keys = [ 'name', 'owner', 'rackAddress' ]
        for sw in json.loads( devices ):
            if "of:0000000000000001" in sw['id']:
                s1Correct = True
                for k in keys:
                    if str( sw.get( 'annotations', {} ).get( k ) ) != str( main.s1Json[k] ):
                        s1Correct = False
                        main.log.debug( "{} is wrong on s1".format( k ) )
                if not s1Correct:
                    main.log.error( "Annotations for s1 are incorrect: {}".format( sw ) )
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
        pprint = main.nodes[0].pprint

        main.step( "Add Net Cfg for switch2" )
        s2Json = { "rackAddress": 2,
                   "name": "Switch2",
                   "owner": "Jenny",
                   "allowed": True }
        main.s2Json = s2Json
        setS2Allow = main.ONOSrest2.setNetCfg( s2Json,
                                               subjectClass="devices",
                                               subjectKey="of:0000000000000002",
                                               configKey="basic" )
        s2Result = False
        if setS2Allow:
            # Check what we set is what is in ONOS
            getS2 = main.ONOSrest2.getNetCfg( subjectClass="devices",
                                              subjectKey="of:0000000000000002",
                                              configKey="basic" )
            onosCfg = pprint( getS2 )
            sentCfg = pprint( s2Json )
            if onosCfg == sentCfg:
                s2Result = True
            else:
                main.log.error( "ONOS NetCfg doesn't match what was sent" )
                main.log.debug( "ONOS config: {}".format( onosCfg ) )
                main.log.debug( "Sent config: {}".format( sentCfg ) )
        utilities.assert_equals( expect=True,
                                 actual=s2Result,
                                 onpass="Net Cfg added for device s2",
                                 onfail="Net Cfg for device s2 not correctly set" )

        main.step( "Add Net Cfg for switch4" )
        s4Json = { "rackAddress": 4,
                   "name": "Switch4",
                   "owner": "John",
                   "allowed": False }
        main.s4Json = s4Json
        setS4Disallow = main.ONOSrest4.setNetCfg( s4Json,
                                                  subjectClass="devices",
                                                  subjectKey="of:0000000000000004",
                                                  configKey="basic" )
        s4Result = False
        if setS4Disallow:
            # Check what we set is what is in ONOS
            getS4 = main.ONOSrest4.getNetCfg( subjectClass="devices",
                                              subjectKey="of:0000000000000004",
                                              configKey="basic" )
            onosCfg = pprint( getS4 )
            sentCfg = pprint( s4Json )
            if onosCfg == sentCfg:
                s4Result = True
            else:
                main.log.error( "ONOS NetCfg doesn't match what was sent" )
                main.log.debug( "ONOS config: {}".format( onosCfg ) )
                main.log.debug( "Sent config: {}".format( sentCfg ) )
        utilities.assert_equals( expect=True,
                                 actual=s4Result,
                                 onpass="Net Cfg added for device s4",
                                 onfail="Net Cfg for device s3 not correctly set" )

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
            main.cleanup()
            main.exit()
        main.case( "Check Devices after all configurations are set" )

        main.netCfg.compareCfg( main )

        main.step( "ONOS should only show devices S1 and S2" )
        devices = main.ONOSrest1.devices()
        main.log.debug( main.ONOSrest1.pprint( devices ) )
        allowedDevices = [ "of:{}".format( str( i ).zfill( 16 ) ) for i in [ 1, 2 ] ]
        onosDevices = []
        for sw in json.loads( devices ):
            onosDevices.append( str( sw.get( 'id' ) ) )
        onosDevices.sort()
        failMsg = "ONOS devices doesn't match the list of allowed devices.\n"
        failMsg += "Expected devices: {}\nActual devices: {}".format( allowedDevices,
                                                                      onosDevices )
        utilities.assert_equals( expect=allowedDevices,
                                 actual=onosDevices,
                                 onpass="Only allowed devices are in ONOS",
                                 onfail=failMsg )

        main.step( "Check device annotations" )
        keys = [ 'name', 'owner', 'rackAddress' ]
        for sw in json.loads( devices ):
            if "of:0000000000000001" in sw.get( 'id' ):
                s1Correct = True
                for k in keys:
                    if str( sw.get( 'annotations', {} ).get( k ) ) != str( main.s1Json[k] ):
                        s1Correct = False
                        main.log.debug( "{} is wrong on s1".format( k ) )
                if not s1Correct:
                    main.log.error( "Annotations for s1 are incorrect: {}".format( sw ) )
            elif "of:0000000000000002" in sw['id']:
                s2Correct = True
                for k in keys:
                    if str( sw.get( 'annotations', {} ).get( k ) ) != str( main.s2Json[k] ):
                        s2Correct = False
                        main.log.debug( "{} is wrong on s2".format( k ) )
                if not s2Correct:
                    main.log.error( "Annotations for s2 are incorrect: {}".format( sw ) )
        try:
            stepResult = s1Correct and s2Correct
        except NameError:
            stepResult = False
            main.log.error( "s1 and/or s2 not found in devices" )
        utilities.assert_equals( expect=True,
                                 actual=stepResult,
                                 onpass="Configured device's annotations are correct",
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
            main.cleanup()
            main.exit()
        main.case( "Testing removal of configurations" )
        main.step( "Remove 'allowed' configuration from all devices" )

        s1Json = main.s1Json  # NOTE: This is a reference
        try:
            del s1Json['allowed']
        except KeyError:
            main.log.exception( "Key not found" )
        setS1 = main.ONOSrest1.setNetCfg( s1Json,
                                          subjectClass="devices",
                                          subjectKey="of:0000000000000001",
                                          configKey="basic" )

        s2Json = main.s2Json  # NOTE: This is a reference
        try:
            time.sleep( main.gossipTime )
            del s2Json['allowed']
        except KeyError:
            main.log.exception( "Key not found" )
        setS2 = main.ONOSrest2.setNetCfg( s2Json,
                                          subjectClass="devices",
                                          subjectKey="of:0000000000000002",
                                          configKey="basic" )

        s3Json = main.s3Json  # NOTE: This is a reference
        try:
            time.sleep( main.gossipTime )
            del s3Json['allowed']
        except KeyError:
            main.log.exception( "Key not found" )
        setS3 = main.ONOSrest3.setNetCfg( s3Json,
                                          subjectClass="devices",
                                          subjectKey="of:0000000000000003",
                                          configKey="basic" )

        s4Json = main.s4Json  # NOTE: This is a reference
        try:
            time.sleep( main.gossipTime )
            del s4Json['allowed']
        except KeyError:
            main.log.exception( "Key not found" )
        setS4 = main.ONOSrest4.setNetCfg( s4Json,
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
        removeS1 = main.ONOSrest1.removeNetCfg( subjectClass="devices",
                                                subjectKey="of:0000000000000001",
                                                configKey="basic" )
        removeS2 = main.ONOSrest2.removeNetCfg( subjectClass="devices",
                                                subjectKey="of:0000000000000002",
                                                configKey="basic" )
        removeSingles = removeS1 and removeS2
        utilities.assert_equals( expect=main.TRUE,
                                 actual=removeSingles,
                                 onpass="Successfully removed S1 and S2 basic config",
                                 onfail="Failed to removed S1 and S2 basic config" )

        main.netCfg.compareCfg( main, main.gossipTime )

        main.step( "Delete the net config for S3" )
        removeS3 = main.ONOSrest3.removeNetCfg( subjectClass="devices",
                                                subjectKey="of:0000000000000003" )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=removeS3,
                                 onpass="Successfully removed S3's config",
                                 onfail="Failed to removed S3's config" )

        main.netCfg.compareCfg( main, main.gossipTime )

        main.step( "Delete the net config for all devices" )
        remove = main.ONOSrest3.removeNetCfg( subjectClass="devices" )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=remove,
                                 onpass="Successfully removed device config",
                                 onfail="Failed to remove device config" )

        main.netCfg.compareCfg( main, main.gossipTime )

        main.step( "Assert the net config for devices is empty" )
        get = main.ONOSrest3.getNetCfg( subjectClass="devices" )
        utilities.assert_equals( expect='{}',
                                 actual=get,
                                 onpass="Successfully removed device config",
                                 onfail="Failed to remove device config" )
