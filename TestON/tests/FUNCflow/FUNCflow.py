class FUNCflow:

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
        main.maxNodes = int( main.params[ 'SCALE' ][ 'max' ] )
        main.startUpSleep = int( main.params[ 'SLEEP' ][ 'startup' ] )
        main.startMNSleep = int( main.params[ 'SLEEP' ][ 'startMN' ] )
        main.addFlowSleep = int( main.params[ 'SLEEP' ][ 'addFlow' ] )
        main.delFlowSleep = int( main.params[ 'SLEEP' ][ 'delFlow' ] )
        main.debug = main.params['DEBUG']
        main.swDPID = main.params[ 'TEST' ][ 'swDPID' ]
        main.cellData = {} # for creating cell file
        main.CLIs = []
        main.ONOSip = []

        main.debug = True if "on" in main.debug else False

        main.ONOSip = main.ONOSbench.getOnosIps()

        # Assigning ONOS cli handles to a list
        for i in range( 1,  main.maxNodes + 1 ):
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


        copyResult = main.ONOSbench.scp( main.Mininet1,
                                         main.dependencyPath+main.topology,
                                         main.Mininet1.home+'/custom/',
                                         direction="to" )

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

        main.numCtrls = int( main.maxNodes )

        main.case( "Starting up " + str( main.numCtrls ) +
                   " node(s) ONOS cluster" )

        #kill off all onos processes
        main.log.info( "Safety check, killing all ONOS processes" +
                       " before initiating environment setup" )

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

    def CASE10( self, main ):
        '''
            Start Mininet
        '''
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
        stepResult = main.Mininet1.assignSwController( "s1", main.ONOSip[0] )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully assigned switch to controller",
                                 onfail="Failed to assign switch to controller" )

        time.sleep( main.startMNSleep )

        main.step( "Comparing MN topology to ONOS topology" )
        main.log.info( "Gathering topology information" )
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
                                            " hosts don't match Mininet")


    def CASE66( self, main ):
        '''
        Testing scapy
        '''
        main.case( "Testing scapy" )
        main.step( "Creating Host1 component" )
        main.Mininet1.createHostComponent( "h1" )
        main.Mininet1.createHostComponent( "h2" )
        hosts = [main.h1, main.h2]
        for host in hosts:
            host.startHostCli()
            host.startScapy()
            host.updateSelf()
            main.log.debug( host.name )
            main.log.debug( host.hostIp )
            main.log.debug( host.hostMac )

        main.step( "Sending/Receiving Test packet - Filter doesn't match" )
        main.h2.startFilter()
        main.h1.buildEther( dst=main.h2.hostMac )
        main.h1.sendPacket( )
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

        main.step( "Sending/Receiving Test packet - Filter matches" )
        main.h2.startFilter()
        main.h1.buildEther( dst=main.h2.hostMac )
        main.h1.buildIP( dst=main.h2.hostIp )
        main.h1.sendPacket( )
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
        main.Mininet1.removeHostComponent("h1")
        main.Mininet1.removeHostComponent("h2")

    def CASE1000( self, main ):
        '''
            Add flows with MAC selectors and verify the flows
        '''
        import json
        import time

        main.case( "Verify flow MAC selectors are correctly compiled" )
        main.caseExplanation = "Install two flows with only MAC selectors " +\
                "specified, then verify flows are added in ONOS, finally "+\
                "send a packet that only specifies the MAC src and dst."

        main.step( "Add flows with MAC addresses as the only selectors" )

        main.log.info( "Creating host components" )
        main.Mininet1.createHostComponent( "h1" )
        main.Mininet1.createHostComponent( "h2" )
        hosts = [main.h1, main.h2]
        stepResult = main.TRUE
        for host in hosts:
            host.startHostCli()
            host.startScapy()
            host.updateSelf()

        # Add a flow that connects host1 on port1 to host2 on port2
        # send output on port2
        # recieve input on port1
        egress = 2
        ingress = 1

        # Add flows that sends packets from port1 to port2 with correct
        # MAC src and dst addresses
        main.log.info( "Adding flow with MAC selectors" )
        stepResult = main.ONOSrest.addFlow( deviceId=main.swDPID,
                                            egressPort=egress,
                                            ingressPort=ingress,
                                            ethSrc=main.h1.hostMac,
                                            ethDst=main.h2.hostMac,
                                            debug=main.debug )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully added flows",
                                 onfail="Failed add flows" )

        # Giving ONOS time to add the flows
        time.sleep( main.addFlowSleep )

        main.step( "Check flows are in the ADDED state" )

        main.log.info( "Get the flows from ONOS" )
        flows = json.loads( main.ONOSrest.flows() )

        stepResult = main.TRUE
        for f in flows:
            if "rest" in f.get("appId"):
                if "ADDED" not in f.get("state"):
                    stepResult = main.FALSE
                    main.log.error( "Flow: %s in state: %s" % (f.get("id"), f.get("state")) )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="All flows are in the ADDED state",
                                 onfail="All flows are NOT in the ADDED state" )

        main.step( "Check flows are in Mininet's flow table" )

        # get the flow IDs that were added through rest
        main.log.info( "Getting the flow IDs from ONOS" )
        flowIds = [ f.get("id") for f in flows if "rest" in f.get("appId") ]
        # convert the flowIDs to ints then hex and finally back to strings
        flowIds = [str(hex(int(x))) for x in flowIds]
        main.log.info( "ONOS flow IDs: {}".format(flowIds) )

        stepResult = main.Mininet1.checkFlowId( "s1", flowIds, debug=False )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="All flows are in mininet",
                                 onfail="All flows are NOT in mininet" )

        main.step( "Send a packet to verify the flows are correct" )

        # Specify the src and dst MAC addr
        main.log.info( "Constructing packet" )
        main.h1.buildEther( src=main.h1.hostMac, dst=main.h2.hostMac )

        # Filter for packets with the correct host name. Otherwise,
        # the filter we catch any packet that is sent to host2
        # NOTE: I believe it doesn't matter which host name it is,
        # as long as the src and dst are both specified
        main.log.info( "Starting filter on host2" )
        main.h2.startFilter( pktFilter="ether host %s" % main.h1.hostMac)

        main.log.info( "Sending packet to host2" )
        main.h1.sendPacket()

        main.log.info( "Checking filter for our packet" )
        stepResult = main.h2.checkFilter()
        if stepResult:
            main.log.info( "Packet: %s" % main.h2.readPackets() )
        else: main.h2.killFilter()

        main.log.info( "Clean up host components" )
        for host in hosts:
            host.stopScapy()
        main.Mininet1.removeHostComponent("h1")
        main.Mininet1.removeHostComponent("h2")

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully sent a packet",
                                 onfail="Failed to send a packet" )

    def CASE1100( self, main ):
        '''
            Add flows with IPv4 selectors and verify the flows
        '''
        import json
        import time

        main.case( "Verify flow IP selectors are correctly compiled" )
        main.caseExplanation = "Install two flows with only IP selectors " +\
                "specified, then verify flows are added in ONOS, finally "+\
                "send a packet that only specifies the IP src and dst."

        main.step( "Add flows with IPv4 addresses as the only selectors" )

        main.log.info( "Creating host components" )
        main.Mininet1.createHostComponent( "h1" )
        main.Mininet1.createHostComponent( "h2" )
        hosts = [main.h1, main.h2]
        stepResult = main.TRUE
        for host in hosts:
            host.startHostCli()
            host.startScapy()
            host.updateSelf()

        # Add a flow that connects host1 on port1 to host2 on port2
        # send output on port2
        # recieve input on port1
        egress = 2
        ingress = 1
        # IPv4 etherType = 0x800
        IPv4=2048

        # Add flows that connects host1 to host2
        main.log.info( "Add flow with port ingress 1 to port egress 2" )
        stepResult = main.ONOSrest.addFlow( deviceId=main.swDPID,
                                            egressPort=egress,
                                            ingressPort=ingress,
                                            ethType=IPv4,
                                            ipSrc=("IPV4_SRC", main.h1.hostIp+"/32"),
                                            ipDst=("IPV4_DST", main.h2.hostIp+"/32"),
                                            debug=main.debug )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully added flows",
                                 onfail="Failed add flows" )

        # Giving ONOS time to add the flow
        time.sleep( main.addFlowSleep )

        main.step( "Check flow is in the ADDED state" )

        main.log.info( "Get the flows from ONOS" )
        flows = json.loads( main.ONOSrest.flows() )

        stepResult = main.TRUE
        for f in flows:
            if "rest" in f.get("appId"):
                if "ADDED" not in f.get("state"):
                    stepResult = main.FALSE
                    main.log.error( "Flow: %s in state: %s" % (f.get("id"), f.get("state")) )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="All flows are in the ADDED state",
                                 onfail="All flows are NOT in the ADDED state" )

        main.step( "Check flows are in Mininet's flow table" )

        # get the flow IDs that were added through rest
        main.log.info( "Getting the flow IDs from ONOS" )
        flowIds = [ f.get("id") for f in flows if "rest" in f.get("appId") ]
        # convert the flowIDs to ints then hex and finally back to strings
        flowIds = [str(hex(int(x))) for x in flowIds]
        main.log.info( "ONOS flow IDs: {}".format(flowIds) )

        stepResult = main.Mininet1.checkFlowId( "s1", flowIds, debug=False )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="All flows are in mininet",
                                 onfail="All flows are NOT in mininet" )

        main.step( "Send a packet to verify the flow is correct" )

        main.log.info( "Constructing packet" )
        # No need for the MAC src dst
        main.h1.buildEther( dst=main.h2.hostMac )
        main.h1.buildIP( src=main.h1.hostIp, dst=main.h2.hostIp )

        main.log.info( "Starting filter on host2" )
        # Defaults to ip
        main.h2.startFilter()

        main.log.info( "Sending packet to host2" )
        main.h1.sendPacket()

        main.log.info( "Checking filter for our packet" )
        stepResult = main.h2.checkFilter()
        if stepResult:
            main.log.info( "Packet: %s" % main.h2.readPackets() )
        else: main.h2.killFilter()

        main.log.info( "Clean up host components" )
        for host in hosts:
            host.stopScapy()
        main.Mininet1.removeHostComponent("h1")
        main.Mininet1.removeHostComponent("h2")

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully sent a packet",
                                 onfail="Failed to send a packet" )

    def CASE1200( self, main ):
        '''
            Add flow with VLAN selector and verify the flow
        '''
        import json
        import time

        main.case( "Verify VLAN selector is correctly compiled" )
        main.caseExplanation = "Install one flow with only the VLAN selector " +\
                "specified, then verify the flow is added in ONOS, and finally "+\
                "broadcast a packet with the correct VLAN tag."

        # We do this here to utilize the hosts information
        main.log.info( "Creating host components" )
        main.Mininet1.createHostComponent( "h3" )
        main.Mininet1.createHostComponent( "h4" )
        hosts = [main.h3, main.h4]
        stepResult = main.TRUE
        for host in hosts:
            host.startHostCli()
            host.startScapy()
            host.updateSelf()


        main.step( "Add a flow with the VLAN tag as the only selector" )

        # Add flows that connects the two vlan hosts h3 and h4
        # Host 3 is on port 3 and host 4 is on port 4
        vlan = main.params[ 'TEST' ][ 'vlan' ]
        egress = 4
        ingress = 3
        # VLAN ethType = 0x8100
        ethType = 33024

        # Add only one flow because we don't need a response
        main.log.info( "Add flow with port ingress 1 to port egress 2" )
        stepResult = main.ONOSrest.addFlow( deviceId=main.swDPID,
                                            egressPort=egress,
                                            ingressPort=ingress,
                                            ethType=ethType,
                                            vlan=vlan,
                                            debug=main.debug )


        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully added flow",
                                 onfail="Failed add flows" )

        # Giving ONOS time to add the flows
        time.sleep( main.addFlowSleep )

        main.step( "Check flows  are in the ADDED state" )

        main.log.info( "Get the flows from ONOS" )
        flows = json.loads( main.ONOSrest.flows() )

        stepResult = main.TRUE
        for f in flows:
            if "rest" in f.get("appId"):
                if "ADDED" not in f.get("state"):
                    stepResult = main.FALSE
                    main.log.error( "Flow: %s in state: %s" % (f.get("id"), f.get("state")) )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="All flows are in the ADDED state",
                                 onfail="All flows are NOT in the ADDED state" )

        main.step( "Check flows are in Mininet's flow table" )

        # get the flow IDs that were added through rest
        main.log.info( "Getting the flow IDs from ONOS" )
        flowIds = [ f.get("id") for f in flows if "rest" in f.get("appId") ]
        # convert the flowIDs to ints then hex and finally back to strings
        flowIds = [str(hex(int(x))) for x in flowIds]
        main.log.info( "ONOS flow IDs: {}".format(flowIds) )

        stepResult = main.Mininet1.checkFlowId( "s1", flowIds, debug=False )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="All flows are in mininet",
                                 onfail="All flows are NOT in mininet" )

        main.step( "Send a packet to verify the flow are correct" )

        # The receiving interface
        recIface = "{}-eth0.{}".format(main.h4.name, vlan)
        main.log.info( "Starting filter on host2" )
        # Filter is setup to catch any packet on the vlan interface with the correct vlan tag
        main.h4.startFilter( ifaceName=recIface, pktFilter="" )

        # Broadcast the packet on the vlan interface. We only care if the flow forwards
        # the packet with the correct vlan tag, not if the mac addr is correct
        sendIface = "{}-eth0.{}".format(main.h3.name, vlan)
        main.log.info( "Broadcasting the packet with a vlan tag" )
        main.h3.sendPacket( iface=sendIface,
                            packet="Ether()/Dot1Q(vlan={})".format(vlan) )

        main.log.info( "Checking filter for our packet" )
        stepResult = main.h4.checkFilter()
        if stepResult:
            main.log.info( "Packet: %s" % main.h4.readPackets() )
        else: main.h4.killFilter()

        main.log.info( "Clean up host components" )
        for host in hosts:
            host.stopScapy()
        main.Mininet1.removeHostComponent("h3")
        main.Mininet1.removeHostComponent("h4")

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully sent a packet",
                                 onfail="Failed to send a packet" )

    def CASE1300( self, main ):
        '''
            Add flows with MPLS selector and verify the flows
        '''
        import json
        import time

        main.case( "Verify the MPLS selector is correctly compiled on the flow." )
        main.caseExplanation = "Install one flow with an MPLS selector, " +\
                               "verify the flow is added in ONOS, and finally "+\
                               "send a packet via scapy that has a MPLS label."

        main.step( "Add a flow with a MPLS selector" )

        main.log.info( "Creating host components" )
        main.Mininet1.createHostComponent( "h1" )
        main.Mininet1.createHostComponent( "h2" )
        hosts = [main.h1, main.h2]
        stepResult = main.TRUE
        for host in hosts:
            host.startHostCli()
            host.startScapy( main.dependencyPath )
            host.updateSelf()

        # ports
        egress = 2
        ingress = 1
        # MPLS etherType
        ethType = main.params[ 'TEST' ][ 'mplsType' ]
        # MPLS label
        mplsLabel = main.params[ 'TEST' ][ 'mpls' ]

        # Add a flow that connects host1 on port1 to host2 on port2
        main.log.info( "Adding flow with MPLS selector" )
        stepResult = main.ONOSrest.addFlow( deviceId=main.swDPID,
                                            egressPort=egress,
                                            ingressPort=ingress,
                                            ethType=ethType,
                                            mpls=mplsLabel,
                                            debug=main.debug )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully added flow",
                                 onfail="Failed add flow" )

        # Giving ONOS time to add the flow
        time.sleep( main.addFlowSleep )

        main.step( "Check flow is in the ADDED state" )

        main.log.info( "Get the flows from ONOS" )
        flows = json.loads( main.ONOSrest.flows() )

        stepResult = main.TRUE
        for f in flows:
            if "rest" in f.get("appId"):
                if "ADDED" not in f.get("state"):
                    stepResult = main.FALSE
                    main.log.error( "Flow: %s in state: %s" % (f.get("id"), f.get("state")) )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="All flows are in the ADDED state",
                                 onfail="All flows are NOT in the ADDED state" )

        main.step( "Check flows are in Mininet's flow table" )

        # get the flow IDs that were added through rest
        main.log.info( "Getting the flow IDs from ONOS" )
        flowIds = [ f.get("id") for f in flows if "rest" in f.get("appId") ]
        # convert the flowIDs to ints then hex and finally back to strings
        flowIds = [str(hex(int(x))) for x in flowIds]
        main.log.info( "ONOS flow IDs: {}".format(flowIds) )

        stepResult = main.Mininet1.checkFlowId( "s1", flowIds, debug=True )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="All flows are in mininet",
                                 onfail="All flows are NOT in mininet" )

        main.step( "Send a packet to verify the flow is correct" )

        main.log.info( "Starting filter on host2" )
        main.h2.startFilter( pktFilter="mpls" )

        main.log.info( "Constructing packet" )
        main.log.info( "Sending packet to host2" )
        main.h1.sendPacket( packet='Ether()/MPLS(label={})'.format(mplsLabel) )

        main.log.info( "Checking filter for our packet" )
        stepResult = main.h2.checkFilter()
        if stepResult:
            main.log.info( "Packet: %s" % main.h2.readPackets() )
        else: main.h2.killFilter()

        main.log.info( "Clean up host components" )
        for host in hosts:
            host.stopScapy()
        main.Mininet1.removeHostComponent("h1")
        main.Mininet1.removeHostComponent("h2")

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully sent a packet",
                                 onfail="Failed to send a packet" )

    def CASE1400( self, main ):
        '''
            Add flows with a TCP selector and verify the flow
        '''
        import json
        import time

        main.case( "Verify the TCP selector is correctly compiled on the flow" )
        main.caseExplanation = "Install a flow with only the TCP selector " +\
                "specified, verify the flow is added in ONOS, and finally "+\
                "send a TCP packet to verify the TCP selector is compiled correctly."

        main.step( "Add a flow with a TCP selector" )

        main.log.info( "Creating host components" )
        main.Mininet1.createHostComponent( "h1" )
        main.Mininet1.createHostComponent( "h2" )
        hosts = [main.h1, main.h2]
        stepResult = main.TRUE
        for host in hosts:
            host.startHostCli()
            host.startScapy()
            host.updateSelf()

        # Add a flow that connects host1 on port1 to host2 on port2
        egress = 2
        ingress = 1
        # IPv4 etherType
        ethType = main.params[ 'TEST' ][ 'ip4Type' ]
        # IP protocol
        ipProto = main.params[ 'TEST' ][ 'tcpProto' ]
        # TCP port destination
        tcpDst = main.params[ 'TEST' ][ 'tcpDst' ]

        main.log.info( "Add a flow that connects host1 on port1 to host2 on port2" )
        stepResult = main.ONOSrest.addFlow( deviceId=main.swDPID,
                                            egressPort=egress,
                                            ingressPort=ingress,
                                            ethType=ethType,
                                            ipProto=ipProto,
                                            tcpDst=tcpDst,
                                            debug=main.debug )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully added flows",
                                 onfail="Failed add flows" )

        # Giving ONOS time to add the flow
        time.sleep( main.addFlowSleep )

        main.step( "Check flow is in the ADDED state" )

        main.log.info( "Get the flows from ONOS" )
        flows = json.loads( main.ONOSrest.flows() )

        stepResult = main.TRUE
        for f in flows:
            if "rest" in f.get("appId"):
                if "ADDED" not in f.get("state"):
                    stepResult = main.FALSE
                    main.log.error( "Flow: %s in state: %s" % (f.get("id"), f.get("state")) )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="All flows are in the ADDED state",
                                 onfail="All flows are NOT in the ADDED state" )

        main.step( "Check flows are in Mininet's flow table" )

        # get the flow IDs that were added through rest
        main.log.info( "Getting the flow IDs from ONOS" )
        flowIds = [ f.get("id") for f in flows if "rest" in f.get("appId") ]
        # convert the flowIDs to ints then hex and finally back to strings
        flowIds = [str(hex(int(x))) for x in flowIds]
        main.log.info( "ONOS flow IDs: {}".format(flowIds) )

        stepResult = main.Mininet1.checkFlowId( "s1", flowIds, debug=False )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="All flows are in mininet",
                                 onfail="All flows are NOT in mininet" )

        main.step( "Send a packet to verify the flow is correct" )

        main.log.info( "Constructing packet" )
        # No need for the MAC src dst
        main.h1.buildEther( dst=main.h2.hostMac )
        main.h1.buildIP( dst=main.h2.hostIp )
        main.h1.buildTCP( dport=tcpDst )

        main.log.info( "Starting filter on host2" )
        # Defaults to ip
        main.h2.startFilter( pktFilter="tcp" )

        main.log.info( "Sending packet to host2" )
        main.h1.sendPacket()

        main.log.info( "Checking filter for our packet" )
        stepResult = main.h2.checkFilter()
        if stepResult:
            main.log.info( "Packet: %s" % main.h2.readPackets() )
        else: main.h2.killFilter()

        main.log.info( "Clean up host components" )
        for host in hosts:
            host.stopScapy()
        main.Mininet1.removeHostComponent("h1")
        main.Mininet1.removeHostComponent("h2")

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully sent a packet",
                                 onfail="Failed to send a packet" )

    def CASE1500( self, main ):
        '''
            Add flows with a UDP selector and verify the flow
        '''
        import json
        import time

        main.case( "Verify the UDP selector is correctly compiled on the flow" )
        main.caseExplanation = "Install a flow with only the UDP selector " +\
                "specified, verify the flow is added in ONOS, and finally "+\
                "send a UDP packet to verify the UDP selector is compiled correctly."

        main.step( "Add a flow with a UDP selector" )

        main.log.info( "Creating host components" )
        main.Mininet1.createHostComponent( "h1" )
        main.Mininet1.createHostComponent( "h2" )
        hosts = [main.h1, main.h2]
        stepResult = main.TRUE
        for host in hosts:
            host.startHostCli()
            host.startScapy()
            host.updateSelf()

        # Add a flow that connects host1 on port1 to host2 on port2
        egress = 2
        ingress = 1
        # IPv4 etherType
        ethType = main.params[ 'TEST' ][ 'ip4Type' ]
        # IP protocol
        ipProto = main.params[ 'TEST' ][ 'udpProto' ]
        # UDP port destination
        udpDst = main.params[ 'TEST' ][ 'udpDst' ]

        main.log.info( "Add a flow that connects host1 on port1 to host2 on port2" )
        stepResult = main.ONOSrest.addFlow( deviceId=main.swDPID,
                                            egressPort=egress,
                                            ingressPort=ingress,
                                            ethType=ethType,
                                            ipProto=ipProto,
                                            udpDst=udpDst,
                                            debug=main.debug )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully added flows",
                                 onfail="Failed add flows" )

        # Giving ONOS time to add the flow
        time.sleep( main.addFlowSleep )

        main.step( "Check flow is in the ADDED state" )

        main.log.info( "Get the flows from ONOS" )
        flows = json.loads( main.ONOSrest.flows() )

        stepResult = main.TRUE
        for f in flows:
            if "rest" in f.get("appId"):
                if "ADDED" not in f.get("state"):
                    stepResult = main.FALSE
                    main.log.error( "Flow: %s in state: %s" % (f.get("id"), f.get("state")) )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="All flows are in the ADDED state",
                                 onfail="All flows are NOT in the ADDED state" )

        main.step( "Check flows are in Mininet's flow table" )

        # get the flow IDs that were added through rest
        main.log.info( "Getting the flow IDs from ONOS" )
        flowIds = [ f.get("id") for f in flows if "rest" in f.get("appId") ]
        # convert the flowIDs to ints then hex and finally back to strings
        flowIds = [str(hex(int(x))) for x in flowIds]
        main.log.info( "ONOS flow IDs: {}".format(flowIds) )

        stepResult = main.Mininet1.checkFlowId( "s1", flowIds, debug=False )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="All flows are in mininet",
                                 onfail="All flows are NOT in mininet" )

        main.step( "Send a packet to verify the flow is correct" )

        main.log.info( "Constructing packet" )
        # No need for the MAC src dst
        main.h1.buildEther( dst=main.h2.hostMac )
        main.h1.buildIP( dst=main.h2.hostIp )
        main.h1.buildUDP( dport=udpDst )

        main.log.info( "Starting filter on host2" )
        # Defaults to ip
        main.h2.startFilter( pktFilter="udp" )

        main.log.info( "Sending packet to host2" )
        main.h1.sendPacket()

        main.log.info( "Checking filter for our packet" )
        stepResult = main.h2.checkFilter()
        if stepResult:
            main.log.info( "Packet: %s" % main.h2.readPackets() )
        else: main.h2.killFilter()

        main.log.info( "Clean up host components" )
        for host in hosts:
            host.stopScapy()
        main.Mininet1.removeHostComponent("h1")
        main.Mininet1.removeHostComponent("h2")

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully sent a packet",
                                 onfail="Failed to send a packet" )


    def CASE2000( self, main ):
        import json

        main.case( "Delete flows that were added through rest" )
        main.step("Deleting flows")

        main.log.info( "Getting flows" )
        flows = json.loads( main.ONOSrest.flows() )

        stepResult = main.TRUE
        for f in flows:
            if "rest" in f.get("appId"):
                if main.debug: main.log.debug( "Flow to be deleted:\n{}".format( main.ONOSrest.pprint(f) ) )
                stepResult = stepResult and main.ONOSrest.removeFlow( f.get("deviceId"), f.get("id") )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully deleting flows",
                                 onfail="Failed to delete flows" )

        time.sleep( main.delFlowSleep )

    def CASE100( self, main ):
        '''
            Report errors/warnings/exceptions
        '''
        main.log.info("Error report: \n" )
        main.ONOSbench.logReport( main.ONOSip[ 0 ],
                                  [ "INFO",
                                    "FOLLOWER",
                                    "WARN",
                                    "flow",
                                    "ERROR",
                                    "Except" ],
                                  "s" )
