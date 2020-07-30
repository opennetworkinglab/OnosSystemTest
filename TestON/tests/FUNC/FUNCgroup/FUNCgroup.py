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
        try:
            from tests.dependencies.ONOSSetup import ONOSSetup
            main.testSetUp = ONOSSetup()
        except ImportError:
            main.log.error( "ONOSSetup not found. exiting the test" )
            main.cleanAndExit()
        main.testSetUp.envSetupDescription()
        stepResult = main.FALSE

        try:
            # Test variables
            main.cellName = main.params[ 'ENV' ][ 'cellName' ]
            main.apps = main.params[ 'ENV' ][ 'cellApps' ]
            main.ONOSport = main.params[ 'CTRL' ][ 'port' ]
            main.dependencyPath = main.testOnDirectory + \
                                  main.params[ 'DEPENDENCY' ][ 'path' ]
            wrapperFile1 = main.params[ 'DEPENDENCY' ][ 'wrapper1' ]
            wrapperFile2 = main.params[ 'DEPENDENCY' ][ 'wrapper2' ]
            main.topology = main.params[ 'DEPENDENCY' ][ 'topology' ]
            bucket = main.params[ 'DEPENDENCY' ][ 'bucket' ]
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
            main.scapyHostNames = main.params[ 'SCAPY' ][ 'HOSTNAMES' ].split( ',' )
            main.scapyHosts = []  # List of scapy hosts for iterating

            main.debug = True if "on" in main.debug else False
            # -- INIT SECTION, ONLY RUNS ONCE -- #

            main.buckets = imp.load_source( bucket,
                                            main.dependencyPath +
                                            bucket +
                                            ".py" )

            stepResult = main.testSetUp.envSetup()

        except Exception as e:
            main.testSetUp.envSetupException( e )

        main.testSetUp.envSetupConclusion( stepResult )

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
        main.testSetUp.ONOSSetUp( main.Cluster )

    def CASE3( self, main ):
        """
            Start Mininet
        """
        import json
        import time
        try:
            from tests.dependencies.topology import Topology
        except ImportError:
            main.log.error( "Topology not found exiting the test" )
            main.cleanAndExit()
        try:
            main.topoRelated
        except ( NameError, AttributeError ):
            main.topoRelated = Topology()

        main.case( "Setup mininet and compare ONOS topology view to Mininet topology" )
        main.caseExplanation = "Start mininet with custom topology and compare topology " +\
                "elements between Mininet and ONOS"

        main.step( "Copy Mininet topology file" )
        copyResult = main.ONOSbench.scp( main.Mininet1,
                                         main.dependencyPath + main.topology,
                                         main.Mininet1.home + '/custom/',
                                         direction="to" )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=copyResult,
                                 onpass="Successfully copy mininet topo file",
                                 onfail="Failed to copy mininet topo file" )

        main.step( "Setup Mininet Topology" )
        topology = main.Mininet1.home + '/custom/' + main.topology
        stepResult = main.Mininet1.startNet( topoFile=topology )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully loaded topology",
                                 onfail="Failed to load topology" )

        main.step( "Assign switch to controller" )
        stepResult = main.Mininet1.assignSwController( "s1", main.Cluster.active( 0 ).ipAddress )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully assigned switch to controller",
                                 onfail="Failed to assign switch to controller" )

        time.sleep( main.startMNSleep )

        main.topoRelated.compareTopos( main.Mininet1 )

        main.step( "Create hosts and start scapy" )
        scapyResult = main.TRUE
        for hostName in main.scapyHostNames:
            main.Scapy.createHostComponent( hostName )
            main.scapyHosts.append( getattr( main, hostName ) )

        main.step( "Start scapy components" )
        for host in main.scapyHosts:
            host.startHostCli()
            host.startScapy()
            host.updateSelf()
            main.log.debug( host.name )
            main.log.debug( host.hostIp )
            main.log.debug( host.hostMac )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=scapyResult,
                                 onpass="Successfully created Scapy Components",
                                 onfail="Failed to discover Scapy Components" )

    def CASE11( self, main ):
        """
            Connect to a physical network, assign controllers and start scapy
        """
        import time
        main.case( "Connecting to physical network" )

        main.step( "Connecting to physical network" )
        topoResult = main.NetworkBench.connectToNet()
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
        for i in range( 1, 2 ):
            assignResult = assignResult & main.NetworkBench.assignSwController( sw="s" + str( i ),
                                                                                ip=main.Cluster.getIps(),
                                                                                port='6653' )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully assign switches to controllers",
                                 onfail="Failed to assign switches to controllers" )

        main.step( "Start scapy" )
        scapyResult = main.TRUE
        for hostName in main.scapyHostNames:
            main.scapyHosts.append( getattr( main, hostName ) )

        for host in main.scapyHosts:
            host.startScapy()
            host.updateSelf()
            main.log.debug( host.name )
            main.log.debug( host.hostIp )
            main.log.debug( host.hostMac )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=scapyResult,
                                 onpass="Successfully created Scapy Components",
                                 onfail="Failed to discover Scapy Components" )

    def CASE4( self, main ):
        """
        Testing scapy
        """
        main.case( "Testing scapy" )
        for host in main.scapyHosts:
            host.stopScapy()
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
        ctrl = main.Cluster.active( 0 )
        response = ctrl.REST.addGroup( deviceId=deviceId,
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

        response = ctrl.REST.getGroups( deviceId=deviceId,
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
        response = ctrl.REST.addFlow( deviceId=deviceId,
                                      priority=priority,
                                      ingressPort=ingressPort,
                                      groupId=groupId )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=response,
                                 onpass="Successfully Added Flows",
                                 onfail="Failed to Add flows" )

        # Giving ONOS time to add the flow
        time.sleep( main.addFlowSleep )

        response = ctrl.REST.getFlows( deviceId=deviceId )
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
        main.step( "Testing Group by sending packet using Scapy" )
        for host in main.scapyHosts:
            host.stopScapy()
            host.startScapy()
            host.updateSelf()
            main.log.debug( host.name )
            main.log.debug( host.hostIp )
            main.log.debug( host.hostMac )

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
        ctrl = main.Cluster.active( 0 )
        # Get Flow ID
        response = ctrl.REST.getFlows( deviceId=deviceId )
        responsejson = json.loads( response )
        for item in responsejson:
            if item[ "priority" ] == int( priority ):
                respFlowId = item[ "id" ]

        main.step( "Deleting the created flow by deviceId and flowId" )
        flowResponse = ctrl.REST.removeFlow( deviceId=deviceId,
                                             flowId=respFlowId )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=flowResponse,
                                 onpass="Deleting flow is successful!!!",
                                 onfail="Deleting flow is failure!!!" )

        # Giving ONOS time to delete the flow
        time.sleep( main.delFlowSleep )

        main.step( "Deleting the created group by deviceId and appCookie" )
        groupResponse = ctrl.REST.removeGroup( deviceId=deviceId,
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
        ctrl = main.Cluster.active( 0 )
        bucketList = []
        bucket = main.buckets.addBucket( main, egressPort=egressPort1 )
        bucketList.append( bucket )
        response = ctrl.REST.addGroup( deviceId=deviceId,
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

        response = ctrl.REST.getGroups( deviceId=deviceId,
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
        response = ctrl.REST.addFlow( deviceId=deviceId,
                                      priority=priority,
                                      ingressPort=ingressPort,
                                      groupId=groupId )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=response,
                                 onpass="Successfully Added Flows",
                                 onfail="Failed to Add flows" )

        # Giving ONOS time to add the flow
        time.sleep( main.addFlowSleep )

        response = ctrl.REST.getFlows( deviceId=deviceId )
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
        main.step( "Testing Group by sending packet using Scapy" )
        for host in main.scapyHosts:
            host.stopScapy()
            host.startScapy()
            host.updateSelf()
            main.log.debug( host.name )
            main.log.debug( host.hostIp )
            main.log.debug( host.hostMac )

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

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResultH2,
                                 onpass="Packet sent to port 1 is received at port 2 successfully!!!",
                                 onfail="Failure!!!Packet sent to port 1 is not received at port 2" )

    def CASE10( self, main ):
        """
            Stop mininet and remove scapy host
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
        main.log.report( "Stop Mininet and Scapy" )
        main.case( "Stop Mininet and Scapy" )
        main.caseExplanation = "Stopping the current mininet topology " +\
                                "to start up fresh"
        main.step( "Stopping and Removing Scapy Host Components" )
        scapyResult = main.TRUE
        for host in main.scapyHosts:
            scapyResult = scapyResult and host.stopScapy()
            main.log.info( "Stopped Scapy Host: {0}".format( host.name ) )

        for host in main.scapyHosts:
            scapyResult = scapyResult and main.Scapy.removeHostComponent( host.name )
            main.log.info( "Removed Scapy Host Component: {0}".format( host.name ) )

        main.scapyHosts = []

        utilities.assert_equals( expect=main.TRUE,
                                 actual=scapyResult,
                                 onpass="Successfully stopped scapy and removed host components",
                                 onfail="Failed to stop mininet and scapy" )

        mininetResult = main.Utils.mininetCleanup( main.Mininet1 )
        # Exit if topology did not load properly
        if not ( mininetResult and scapyResult ):
            main.cleanAndExit()

    def CASE12( self, main ):
        """
        Stop Scapy on physical hosts
        """
        main.case( "Stop Scapy" )
        main.step( "Stopping Scapy Hosts" )
        scapyResult = main.TRUE
        for host in main.scapyHosts:
            host.stopScapy()
        utilities.assert_equals( expect=main.TRUE,
                                 actual=scapyResult,
                                 onpass="Successfully stopped scapy",
                                 onfail="Failed to stop scapy" )

    def CASE100( self, main ):
        """
            Report errors/warnings/exceptions
        """
        main.log.info( "Error report: \n" )
        main.ONOSbench.logReport( main.Cluster.active( 0 ).ipAddress,
                                  [ "INFO",
                                    "FOLLOWER",
                                    "WARN",
                                    "flow",
                                    "group",
                                    "ERROR",
                                    "Except" ],
                                  "s" )
