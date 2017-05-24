class FUNCgroup:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
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

        # Test variables
        main.testOnDirectory = os.path.dirname( os.getcwd() )
        main.cellName = main.params[ 'ENV' ][ 'cellName' ]
        main.apps = main.params[ 'ENV' ][ 'cellApps' ]
        gitBranch = main.params[ 'GIT' ][ 'branch' ]
        gitPull = main.params[ 'GIT' ][ 'pull' ]
        main.ONOSport = main.params[ 'CTRL' ][ 'port' ]
        main.dependencyPath = main.testOnDirectory + \
                              main.params[ 'DEPENDENCY' ][ 'path' ]
        wrapperFile1 = main.params[ 'DEPENDENCY' ][ 'wrapper1' ]
        wrapperFile2 = main.params[ 'DEPENDENCY' ][ 'wrapper2' ]
        main.topology = main.params[ 'DEPENDENCY' ][ 'topology' ]
        bucket = main.params[ 'DEPENDENCY' ][ 'bucket' ]
        main.maxNodes = int( main.params[ 'SCALE' ][ 'max' ] )
        main.startUpSleep = int( main.params[ 'SLEEP' ][ 'startup' ] )
        main.startMNSleep = int( main.params[ 'SLEEP' ][ 'startMN' ] )
        main.addFlowSleep = int( main.params[ 'SLEEP' ][ 'addFlow' ] )
        main.delFlowSleep = int( main.params[ 'SLEEP' ][ 'delFlow' ] )
        main.addGroupSleep = int( main.params[ 'SLEEP' ][ 'addGroup' ] )
        main.delGroupSleep = int( main.params[ 'SLEEP' ][ 'delGroup' ] )
        main.debug = main.params[ 'DEBUG' ]
        main.swDPID = main.params[ 'TEST' ][ 'swDPID' ]
        egressPort1 = main.params[ 'TEST' ][ 'egressPort1' ]
        egressPort2 = main.params[ 'TEST' ][ 'egressPort2' ]
        egressPort3 = main.params[ 'TEST' ][ 'egressPort3' ]
        ingressPort = main.params[ 'TEST' ][ 'ingressPort' ]
        appCookie = main.params[ 'TEST' ][ 'appCookie' ]
        type1 = main.params[ 'TEST' ][ 'type1' ]
        type2 = main.params[ 'TEST' ][ 'type2' ]
        groupId = main.params[ 'TEST' ][ 'groupId' ]
        priority = main.params[ 'TEST' ][ 'priority' ]
        deviceId = main.params[ 'TEST' ][ 'swDPID' ]

        main.cellData = {}  # for creating cell file
        main.CLIs = []
        main.ONOSip = []

        main.debug = True if "on" in main.debug else False

        main.ONOSip = main.ONOSbench.getOnosIps()

        # Assigning ONOS cli handles to a list
        for i in range( 1, main.maxNodes + 1 ):
            main.CLIs.append( getattr( main, 'ONOScli' + str( i ) ) )

        # -- INIT SECTION, ONLY RUNS ONCE -- #
        main.startUp = imp.load_source( wrapperFile1,
                                        main.dependencyPath +
                                        wrapperFile1 +
                                        ".py" )

        main.topo = imp.load_source( wrapperFile2,
                                     main.dependencyPath +
                                     wrapperFile2 +
                                     ".py" )

        main.buckets = imp.load_source( bucket,
                                        main.dependencyPath +
                                        bucket +
                                        ".py" )

        copyResult = main.ONOSbench.scp( main.Mininet1,
                                         main.dependencyPath + main.topology,
                                         main.Mininet1.home + '/custom/',
                                         direction="to" )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=copyResult,
                                 onpass="Successfully copy " + "test variables ",
                                 onfail="Failed to copy test variables" )

        if main.CLIs:
            stepResult = main.TRUE
        else:
            main.log.error( "Did not properly created list of ONOS CLI handle" )
            stepResult = main.FALSE

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully construct " + "test variables ",
                                 onfail="Failed to construct test variables" )

        if gitPull == 'True':
            main.step( "Building ONOS in " + gitBranch + " branch" )
            onosBuildResult = main.startUp.onosBuild( main, gitBranch )
            stepResult = onosBuildResult
            utilities.assert_equals( expect=main.TRUE,
                                     actual=stepResult,
                                     onpass="Successfully compiled " + "latest ONOS",
                                     onfail="Failed to compile " + "latest ONOS" )
        else:
            main.log.warn( "Did not pull new code so skipping mvn " +
                           "clean install" )

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

        main.numCtrls = int( main.maxNodes )

        main.case( "Starting up " + str( main.numCtrls ) +
                   " node(s) ONOS cluster" )

        #kill off all onos processes
        main.log.info( "Safety check, killing all ONOS processes" +
                       " before initiating environment setup" )

        for i in range( main.maxNodes ):
            main.ONOSbench.onosDie( main.ONOSip[ i ] )

        main.log.info( "NODE COUNT = " + str( main.numCtrls ) )

        tempOnosIp = []
        for i in range( main.numCtrls ):
            tempOnosIp.append( main.ONOSip[ i ] )

        main.ONOSbench.createCellFile( main.ONOSbench.ip_address,
                                       "temp",
                                       main.Mininet1.ip_address,
                                       main.apps,
                                       tempOnosIp )

        main.step( "Apply cell to environment" )
        cellResult = main.ONOSbench.setCell( "temp" )
        verifyResult = main.ONOSbench.verifyCell()
        stepResult = cellResult and verifyResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully applied cell to " + "environment",
                                 onfail="Failed to apply cell to environment " )

        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.buckBuild()
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

        main.step( "Set up ONOS secure SSH" )
        secureSshResult = main.TRUE
        for i in range( int( main.numCtrls ) ):
            secureSshResult = secureSshResult and main.ONOSbench.onosSecureSSH( node=main.ONOSip[ i ] )
        utilities.assert_equals( expect=main.TRUE, actual=secureSshResult,
                                 onpass="Test step PASS",
                                 onfail="Test step FAIL" )

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

    def CASE3( self, main ):
        """
            Start Mininet
        """
        import json

        main.case( "Setup mininet and compare ONOS topology view to Mininet topology" )
        main.caseExplanation = "Start mininet with custom topology and compare topology " +\
                "elements between Mininet and ONOS"

        main.step( "Setup Mininet Topology" )
        topology = main.Mininet1.home + '/custom/' + main.topology
        stepResult = main.Mininet1.startNet( topoFile=topology )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully loaded topology",
                                 onfail="Failed to load topology" )

        main.step( "Assign switch to controller" )
        stepResult = main.Mininet1.assignSwController( "s1", main.ONOSip[ 0 ] )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully assigned switch to controller",
                                 onfail="Failed to assign switch to controller" )

        time.sleep( main.startMNSleep )

        main.step( "Comparing MN topology to ONOS topology" )
        main.log.info( "Gathering topology information" )
        devices = main.topo.getAllDevices( main )
        hosts = main.topo.getAllHosts( main )
        ports = main.topo.getAllPorts( main )
        links = main.topo.getAllLinks( main )

        mnSwitches = main.Mininet1.getSwitches()
        mnLinks = main.Mininet1.getLinks()
        mnHosts = main.Mininet1.getHosts()

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

    def CASE4( self, main ):
        """
        Testing scapy
        """
        main.case( "Testing scapy" )
        main.step( "Creating Host1 component" )
        main.Scapy.createHostComponent( "h1" )
        main.Scapy.createHostComponent( "h2" )
        hosts = [ main.h1, main.h2 ]
        for host in hosts:
            host.startHostCli()
            host.startScapy()
            host.updateSelf()
            main.log.debug( host.name )
            main.log.debug( host.hostIp )
            main.log.debug( host.hostMac )

        main.step( "Sending/Receiving Test packet - Filter doesn't match" )
        main.log.info( "Starting Filter..." )
        main.h2.startFilter()
        main.log.info( "Building Ether frame..." )
        main.h1.buildEther( dst=main.h2.hostMac )
        main.log.info( "Sending Packet..." )
        main.h1.sendPacket()
        main.log.info( "Checking Filter..." )
        finished = main.h2.checkFilter()
        main.log.debug( finished )
        i = ""
        if finished:
            a = main.h2.readPackets()
            for i in a.splitlines():
                main.log.info( i )
        else:
            kill = main.h2.killFilter()
            main.log.debug( kill )
            main.h2.handle.sendline( "" )
            main.h2.handle.expect( main.h2.scapyPrompt )
            main.log.debug( main.h2.handle.before )
        utilities.assert_equals( expect=True,
                                 actual="dst=00:00:00:00:00:02 src=00:00:00:00:00:01" in i,
                                 onpass="Pass",
                                 onfail="Fail" )

        main.step( "Sending/Receiving Test packet - Filter matches" )
        main.h2.startFilter()
        main.h1.buildEther( dst=main.h2.hostMac )
        main.h1.buildIP( dst=main.h2.hostIp )
        main.h1.sendPacket()
        finished = main.h2.checkFilter()
        i = ""
        if finished:
            a = main.h2.readPackets()
            for i in a.splitlines():
                main.log.info( i )
        else:
            kill = main.h2.killFilter()
            main.log.debug( kill )
            main.h2.handle.sendline( "" )
            main.h2.handle.expect( main.h2.scapyPrompt )
            main.log.debug( main.h2.handle.before )
        utilities.assert_equals( expect=True,
                                 actual="dst=00:00:00:00:00:02 src=00:00:00:00:00:01" in i,
                                 onpass="Pass",
                                 onfail="Fail" )

        main.step( "Clean up host components" )
        for host in hosts:
            host.stopScapy()
        main.Mininet1.removeHostComponent( "h1" )
        main.Mininet1.removeHostComponent( "h2" )

    def CASE5( self, main ):
        """
           Adding Group of type "ALL" using Rest api
        """
        import json
        import time
        isAdded = main.FALSE
        main.case( "Verify Group of type All are successfully Added" )
        main.caseExplanation = " Install a Group of type ALL " +\
                               " Verify the Group is Added " +\
                               " Add a flow using the group " +\
                               " Send a packet that verifies the action bucket of the group"

        main.step( "Add Group using Rest api" )
        bucketList = []
        bucket = main.buckets.addBucket( main, egressPort=egressPort1 )
        bucketList.append( bucket )
        bucket = main.buckets.addBucket( main, egressPort=egressPort2 )
        bucketList.append( bucket )
        bucket = main.buckets.addBucket( main, egressPort=egressPort3 )
        bucketList.append( bucket )
        response = main.ONOSrest.addGroup( deviceId=deviceId,
                                           groupType=type1,
                                           bucketList=bucketList,
                                           appCookie=appCookie,
                                           groupId=groupId )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=response,
                                 onpass="Successfully added Groups of type ALL",
                                 onfail="Failed to add Groups of type ALL" )

        # Giving ONOS time to add the group
        time.sleep( main.addGroupSleep )

        main.step( "Check groups are in ADDED state" )

        response = main.ONOSrest.getGroups( deviceId=deviceId,
                                            appCookie=appCookie )
        responsejson = json.loads( response )
        for item in responsejson:
            if item[ "state" ] == "ADDED":
                isAdded = main.TRUE

        utilities.assert_equals( expect=main.TRUE,
                                 actual=isAdded,
                                 onpass="All Group is in Added State",
                                 onfail="All Group is not in Added State" )

        """
           Adding flow using rest api
        """
        isAdded = main.FALSE

        main.step( "Adding flow with Group using rest api" )
        response = main.ONOSrest.addFlow( deviceId=deviceId,
                                          priority=priority,
                                          ingressPort=ingressPort,
                                          groupId=groupId )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=response,
                                 onpass="Successfully Added Flows",
                                 onfail="Failed to Add flows" )

        # Giving ONOS time to add the flow
        time.sleep( main.addFlowSleep )

        response = main.ONOSrest.getFlows( deviceId=deviceId )
        responsejson = json.loads( response )
        for item in responsejson:
            if item[ "priority" ] == int( priority ) and item[ "state" ] == "ADDED":
                isAdded = main.TRUE

        utilities.assert_equals( expect=main.TRUE,
                                 actual=isAdded,
                                 onpass="Flow is in Added State",
                                 onfail="Flow is not in Added State" )

        """
        Sends a packet using  scapy
        """
        main.step( "Testing Group by sending packet using  Scapy" )
        main.log.info( "Creating host components" )
        main.Scapy.createHostComponent( "h1" )
        main.Scapy.createHostComponent( "h2" )
        main.Scapy.createHostComponent( "h3" )
        main.Scapy.createHostComponent( "h4" )

        hosts = [ main.h1, main.h2, main.h3, main.h4 ]
        for host in hosts:
            host.startHostCli()
            host.startScapy()
            host.updateSelf()
        main.log.info( "Constructing Packet" )
        main.h1.buildEther( dst=main.h1.hostMac )
        main.h1.buildIP( dst=main.h1.hostIp )
        main.log.info( "Start Filter on host2,host3,host4" )
        main.h2.startFilter( pktFilter="ether host %s and ip host %s" % ( main.h1.hostMac, main.h1.hostIp ) )
        main.h3.startFilter( pktFilter="ether host %s and ip host %s" % ( main.h1.hostMac, main.h1.hostIp ) )
        main.h4.startFilter( pktFilter="ether host %s and ip host %s" % ( main.h1.hostMac, main.h1.hostIp ) )
        main.log.info( "sending packet to Host" )
        main.h1.sendPacket()
        main.log.info( "Checking filter for our packet" )
        stepResultH2 = main.h2.checkFilter()
        stepResultH3 = main.h3.checkFilter()
        stepResultH4 = main.h4.checkFilter()

        if stepResultH2:
            main.log.info( "Packet : %s" % main.h2.readPackets() )
        else:
            main.h2.killFilter()

        if stepResultH3:
            main.log.info( "Packet : %s" % main.h3.readPackets() )
        else:
            main.h2.killFilter()

        if stepResultH4:
            main.log.info( "Packet : %s" % main.h4.readPackets() )
        else:
            main.h4.killFilter()

        if stepResultH2 and stepResultH3 and stepResultH4:
            main.log.info( "Success!!!Packet sent to port 1 is received at port 2,3 and 4" )
            stepResult = main.TRUE
        else:
            main.log.info( "Failure!!!Packet sent to port 1 is not received at port 2,3 and 4" )
            stepResult = main.FALSE

        main.log.info( "Clean up host components" )
        for host in hosts:
            host.stopScapy()
        main.Mininet1.removeHostComponent( "h1" )
        main.Mininet1.removeHostComponent( "h2" )
        main.Mininet1.removeHostComponent( "h3" )
        main.Mininet1.removeHostComponent( "h4" )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Packet sent to port 1 is received at port 2,3,4 ",
                                 onfail="Packet sent to port 1 is not received at port 2,3,4 " )

    def CASE6( self, main ):
        """
         Deleting the Group and Flow
        """
        import json
        import time
        respFlowId = 1

        main.case( "Delete the Group and Flow added through Rest api " )
        main.step( "Deleting Group and Flows" )

        #Get Flow ID
        response = main.ONOSrest.getFlows( deviceId=deviceId )
        responsejson = json.loads( response )
        for item in responsejson:
            if item[ "priority" ] == int( priority ):
                respFlowId = item[ "id" ]

        main.step( "Deleting the created flow by deviceId and flowId" )
        flowResponse = main.ONOSrest.removeFlow( deviceId=deviceId,
                                                 flowId=respFlowId )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=flowResponse,
                                 onpass="Deleting flow is successful!!!",
                                 onfail="Deleting flow is failure!!!" )

        # Giving ONOS time to delete the flow
        time.sleep( main.delFlowSleep )

        main.step( "Deleting the created group by deviceId and appCookie" )
        groupResponse = main.ONOSrest.removeGroup( deviceId=deviceId,
                                                   appCookie=appCookie )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=groupResponse,
                                 onpass="Deleting Group is successful!!!",
                                 onfail="Deleting Group is failure!!!" )

        # Giving ONOS time to delete the group
        time.sleep( main.delGroupSleep )

    def CASE7( self, main ):
        """
           Adding Group of type "INDIRECT" using Rest api.
        """
        import json
        import time
        isAdded = main.FALSE

        main.case( "Verify Group of type INDIRECT are successfully Added" )
        main.caseExplanation = " Install a Group of type INDIRECT " +\
                               " Verify the Group is Added " +\
                               " Add a flow using the group " +\
                               " Send a packet that verifies the action bucket of the group"

        main.step( "Add Group using Rest api" )
        bucketList = []
        bucket = main.buckets.addBucket( main, egressPort=egressPort1 )
        bucketList.append( bucket )
        response = main.ONOSrest.addGroup( deviceId=deviceId,
                                           groupType=type2,
                                           bucketList=bucketList,
                                           appCookie=appCookie,
                                           groupId=groupId )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=response,
                                 onpass="Successfully added Groups of type INDIRECT",
                                 onfail="Failed to add Groups of type INDIRECT" )

        # Giving ONOS time to add the group
        time.sleep( main.addGroupSleep )

        main.step( "Check groups are in ADDED state" )

        response = main.ONOSrest.getGroups( deviceId=deviceId,
                                            appCookie=appCookie )
        responsejson = json.loads( response )
        for item in responsejson:
            if item[ "state" ] == "ADDED":
                isAdded = main.TRUE

        utilities.assert_equals( expect=main.TRUE,
                                 actual=isAdded,
                                 onpass="INDIRECT Group is in Added State",
                                 onfail="INDIRECT Group is not in Added State" )

        """
           Adding flows using rest api
        """
        isAdded = main.FALSE

        main.step( "Adding flow with Group using rest api" )
        response = main.ONOSrest.addFlow( deviceId=deviceId,
                                          priority=priority,
                                          ingressPort=ingressPort,
                                          groupId=groupId )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=response,
                                 onpass="Successfully Added Flows",
                                 onfail="Failed to Add flows" )

        # Giving ONOS time to add the flow
        time.sleep( main.addFlowSleep )

        response = main.ONOSrest.getFlows( deviceId=deviceId )
        responsejson = json.loads( response )
        for item in responsejson:
            if item[ "priority" ] == int( priority ) and item[ "state" ] == "ADDED":
                isAdded = main.TRUE

        utilities.assert_equals( expect=main.TRUE,
                                 actual=isAdded,
                                 onpass="Flow is in Added State",
                                 onfail="Flow is not in Added State" )

        """
        Sends a packet using scapy
        """
        main.step( "Testing Group by sending packet using  Scapy" )
        main.log.info( "Creating host components" )
        main.Scapy.createHostComponent( "h1" )
        main.Scapy.createHostComponent( "h2" )

        hosts = [ main.h1, main.h2 ]
        for host in hosts:
            host.startHostCli()
            host.startScapy()
            host.updateSelf()
        main.log.info( "Constructing Packet" )
        main.h1.buildEther( dst=main.h1.hostMac )
        main.h1.buildIP( dst=main.h1.hostIp )
        main.log.info( "Start Filter on host2" )
        main.h2.startFilter( pktFilter="ether host %s and ip host %s" % ( main.h1.hostMac, main.h1.hostIp ) )
        main.log.info( "sending packet to Host" )
        main.h1.sendPacket()
        main.log.info( "Checking filter for our packet" )
        stepResultH2 = main.h2.checkFilter()

        if stepResultH2:
            main.log.info( "Packet : %s" % main.h2.readPackets() )
        else:
            main.h2.killFilter()

        main.log.info( "Clean up host components" )
        for host in hosts:
            host.stopScapy()
        main.Mininet1.removeHostComponent( "h1" )
        main.Mininet1.removeHostComponent( "h2" )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResultH2,
                                 onpass="Packet sent to port 1 is received at port 2 successfully!!!",
                                 onfail="Failure!!!Packet sent to port 1 is not received at port 2" )

    def CASE8( self, main ):
        """
         Deleting the Group and Flow
        """
        import json
        import time
        respFlowId = 1

        main.case( "Delete the Group and Flow added through Rest api " )
        main.step( "Deleting Group and Flows" )

        #Getting Flow ID
        response = main.ONOSrest.getFlows( deviceId=deviceId )
        responsejson = json.loads( response )
        for item in responsejson:
            if item[ "priority" ] == int( priority ):
                respFlowId = item[ "id" ]

        main.step( "Deleting the created flow by deviceId and flowId" )
        flowResponse = main.ONOSrest.removeFlow( deviceId=deviceId,
                                                 flowId=respFlowId )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=flowResponse,
                                 onpass="Deleting flow is successful!!!",
                                 onfail="Deleting flow is failure!!!" )

        # Giving ONOS time to delete the flow
        time.sleep( main.delFlowSleep )

        groupResponse = main.ONOSrest.removeGroup( deviceId=deviceId,
                                                   appCookie=appCookie )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=groupResponse,
                                 onpass="Deleting Group is successful!!!",
                                 onfail="Deleting Group is failure!!!" )

        # Giving ONOS time to delete the group
        time.sleep( main.delGroupSleep )

    def CASE100( self, main ):
        """
            Report errors/warnings/exceptions
        """
        main.log.info( "Error report: \n" )
        main.ONOSbench.logReport( main.ONOSip[ 0 ],
                                  [ "INFO",
                                    "FOLLOWER",
                                    "WARN",
                                    "flow",
                                    "group",
                                    "ERROR",
                                    "Except" ],
                                  "s" )
