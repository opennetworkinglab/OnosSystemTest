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
import os
import time
import json
import urllib
import re
from core import utilities


class Testcaselib:

    useSSH = True

    @staticmethod
    def initTest( main ):
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
        from tests.dependencies.Network import Network
        main.Network = Network()
        main.testSetUp.envSetupDescription( False )
        stepResult = main.FALSE
        try:
            # Test variables
            main.cellName = main.params[ 'ENV' ][ 'cellName' ]
            main.apps = main.params[ 'ENV' ][ 'cellApps' ]
            main.path = os.path.dirname( main.testFile )
            main.useCommonTopo = main.params[ 'DEPENDENCY' ][ 'useCommonTopo' ] == 'True'
            main.topoPath = main.path + ( "/.." if main.useCommonTopo else "" ) + "/dependencies/"
            main.useCommonConf = main.params[ 'DEPENDENCY' ][ 'useCommonConf' ] == 'True'
            main.useBmv2 = main.params[ 'DEPENDENCY' ][ 'useBmv2' ] == 'True'
            main.configPath = main.path + ( "/.." if main.useCommonConf else "" ) + "/dependencies/"
            main.bmv2Path = main.path + "/../dependencies/"
            main.forJson = "json/"
            main.forChart = "chart/"
            main.forConfig = "conf/"
            main.forHost = "host/"
            main.forSwitchFailure = "switchFailure/"
            main.forLinkFailure = "linkFailure/"
            main.forMulticast = "multicast/"
            main.topology = main.params[ 'DEPENDENCY' ][ 'topology' ]
            main.topologyLib = main.params[ 'DEPENDENCY' ][ 'lib' ] if 'lib' in main.params[ 'DEPENDENCY' ] else None
            main.topologyConf = main.params[ 'DEPENDENCY' ][ 'conf' ] if 'conf' in main.params[ 'DEPENDENCY' ] else None
            main.bmv2 = "bmv2.py"
            main.scale = ( main.params[ 'SCALE' ][ 'size' ] ).split( "," )
            main.maxNodes = int( main.params[ 'SCALE' ][ 'max' ] )

            stepResult = main.testSetUp.envSetup( False )
        except Exception as e:
            main.testSetUp.envSetupException( e )

        main.testSetUp.evnSetupConclusion( stepResult )

    @staticmethod
    def installOnos( main, vlanCfg=True, skipPackage=False, cliSleep=10,
                     parallel=True ):
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
        # main.scale[ 0 ] determines the current number of ONOS controller
        if not main.apps:
            main.log.error( "App list is empty" )
        main.log.info( "Cluster size: " + str( main.Cluster.numCtrls ) )
        main.log.info( "Cluster ips: " + ', '.join( main.Cluster.getIps() ) )
        main.dynamicHosts = [ 'in1', 'out1' ]
        main.testSetUp.ONOSSetUp( main.Cluster, newCell=True, cellName=main.cellName,
                                  skipPack=skipPackage,
                                  useSSH=Testcaselib.useSSH,
                                  installParallel=parallel, includeCaseDesc=False )
        ready = utilities.retry( main.Cluster.active( 0 ).CLI.summary,
                                 main.FALSE,
                                 sleep=cliSleep,
                                 attempts=10 )
        if ready:
            ready = main.TRUE
        utilities.assert_equals( expect=main.TRUE, actual=ready,
                                 onpass="ONOS summary command succeded",
                                 onfail="ONOS summary command failed" )
        if not ready:
            main.log.error( "ONOS startup failed!" )
            main.cleanAndExit()

        for ctrl in main.Cluster.active():
            ctrl.CLI.logSet( "DEBUG", "org.onosproject.segmentrouting" )
            ctrl.CLI.logSet( "DEBUG", "org.onosproject.driver" )
            ctrl.CLI.logSet( "DEBUG", "org.onosproject.net.flowobjective.impl" )
            ctrl.CLI.logSet( "DEBUG", "org.onosproject.routeservice.impl" )
            ctrl.CLI.logSet( "DEBUG", "org.onosproject.routeservice.store" )
            ctrl.CLI.logSet( "DEBUG", "org.onosproject.routing.fpm" )
            ctrl.CLI.logSet( "TRACE", "org.onosproject.events" )
            ctrl.CLI.logSet( "DEBUG", "org.onosproject.mcast" )

    @staticmethod
    def loadCount( main ):
        with open("%s/count/%s.count" % (main.configPath, main.cfgName)) as count:
                main.count = json.load(count)

    @staticmethod
    def loadJson( main ):
        with open( "%s%s.json" % ( main.configPath + main.forJson,
                                   main.cfgName ) ) as cfg:
            main.Cluster.active( 0 ).REST.setNetCfg( json.load( cfg ) )

    @staticmethod
    def loadChart( main ):
        try:
            with open( "%s%s.chart" % ( main.configPath + main.forChart,
                                        main.cfgName ) ) as chart:
                main.pingChart = json.load(chart)
        except IOError:
            main.log.warn( "No chart file found." )

    @staticmethod
    def loadHost( main ):
        with open( "%s%s.host" % ( main.configPath + main.forHost,
                                   main.cfgName ) ) as host:
            main.expectedHosts = json.load( host )

    @staticmethod
    def loadSwitchFailureChart( main ):
        with open( "%s%s.switchFailureChart" % ( main.configPath + main.forSwitchFailure,
                                                 main.cfgName ) ) as sfc:
            main.switchFailureChart = json.load( sfc )

    @staticmethod
    def loadLinkFailureChart( main ):
        with open( "%s%s.linkFailureChart" % ( main.configPath + main.forLinkFailure,
                                                 main.cfgName ) ) as lfc:
            main.linkFailureChart = json.load( lfc )

    @staticmethod
    def loadMulticastConfig( main ):
        with open( "%s%s.multicastConfig" % ( main.configPath + main.forMulticast,
                                                 main.cfgName ) ) as cfg:
            main.multicastConfig = json.load( cfg )

    @staticmethod
    def startMininet( main, topology, args="" ):
        copyResult = main.ONOSbench.scp( main.Mininet1,
                                         main.topoPath + main.topology,
                                         main.Mininet1.home + "custom",
                                         direction="to" )
        if main.topologyLib:
            for lib in main.topologyLib.split(","):
                copyResult = copyResult and main.ONOSbench.scp( main.Mininet1,
                                                                main.topoPath + lib,
                                                                main.Mininet1.home + "custom",
                                                                direction="to" )
        if main.topologyConf:
            import re
            controllerIPs = [ ctrl.ipAddress for ctrl in main.Cluster.runningNodes ]
            index = 0
            for conf in main.topologyConf.split(","):
                # Update zebra configurations with correct ONOS instance IP
                if conf in [ "zebradbgp1.conf", "zebradbgp2.conf" ]:
                    ip = controllerIPs[ index ]
                    index = ( index + 1 ) % len( controllerIPs )
                    with open( main.configPath + main.forConfig + conf ) as f:
                        s = f.read()
                    s = re.sub( r"(fpm connection ip).*(port 2620)", r"\1 " + ip + r" \2", s )
                    with open( main.configPath + main.forConfig + conf, "w" ) as f:
                        f.write( s )
                copyResult = copyResult and main.ONOSbench.scp( main.Mininet1,
                                                                main.configPath + main.forConfig + conf,
                                                                "~/",
                                                                direction="to" )
        copyResult = copyResult and main.ONOSbench.scp( main.Mininet1,
                                                        main.bmv2Path + main.bmv2,
                                                        main.Mininet1.home + "custom",
                                                        direction="to" )
        stepResult = copyResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully copied topo files",
                                 onfail="Failed to copy topo files" )
        main.step( "Starting Mininet Topology" )
        arg = "--onos-ip=%s %s" % (",".join([ctrl.ipAddress for ctrl in main.Cluster.runningNodes]), args)
        main.topology = topology
        topoResult = main.Mininet1.startNet(
                topoFile=main.Mininet1.home + "custom/" + main.topology, args=arg )
        stepResult = topoResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully loaded topology",
                                 onfail="Failed to load topology" )
        # Exit if topology did not load properly
        if not topoResult:
            main.cleanAndExit()

    @staticmethod
    def connectToPhysicalNetwork( main ):
        main.step( "Connecting to physical netowrk" )
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
        switches = main.NetworkBench.getSwitches()
        pool = []
        for name in switches.keys():
            thread = main.Thread( target=main.NetworkBench.assignSwController,
                                  name="assignSwitchToController",
                                  args=[ name, main.Cluster.getIps(), '6653' ] )
            pool.append( thread )
            thread.start()
        for thread in pool:
            thread.join( 300 )
            if not thread.result:
                stepResult = main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully assign switches to controllers",
                                 onfail="Failed to assign switches to controllers" )

        # Check devices
        Testcaselib.checkDevices( main, switches=int( main.params[ 'TOPO' ][ 'switchNum' ] ) )
        time.sleep( float( main.params[ "timers" ][ "connectToNetSleep" ] ) )
        # Connecting to hosts that only have data plane connectivity
        main.step( "Connecting inband hosts" )
        stepResult = main.Network.connectInbandHosts()
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully connected inband hosts",
                                 onfail="Failed to connect inband hosts" )

    @staticmethod
    def saveOnosDiagnostics( main ):
        """
        Get onos-diags.tar.gz and save it to the log directory.
        suffix: suffix string of the file name. E.g. onos-diags-case1.tar.gz
        """
        main.log.info( "Collecting onos-diags..." )
        main.ONOSbench.onosDiagnostics( [ctrl.ipAddress for ctrl in main.Cluster.runningNodes],
                                        main.logdir,
                                        "-CASE%d" % main.CurrentTestCaseNumber )

    @staticmethod
    def config( main, cfgName ):
        main.spines = []

        main.failures = int( main.params[ 'failures' ] )
        main.cfgName = cfgName

        if main.cfgName == '2x2':
            spine = {}
            spine[ 'name' ] = main.params[ 'switches' ][ 'spine1' ]
            spine[ 'dpid' ] = main.params[ 'switches' ][ 'spinedpid1' ]
            main.spines.append( spine )

            spine = {}
            spine[ 'name' ] = main.params[ 'switches' ][ 'spine2' ]
            spine[ 'dpid' ] = main.params[ 'switches' ][ 'spinedpid2' ]
            main.spines.append( spine )

        elif main.cfgName == '4x4':
            spine = {}
            spine[ 'name' ] = main.params[ 'switches' ][ 'spine1' ]
            spine[ 'dpid' ] = main.params[ 'switches' ][ 'spinedpid1' ]
            main.spines.append( spine )

            spine = {}
            spine[ 'name' ] = main.params[ 'switches' ][ 'spine2' ]
            spine[ 'dpid' ] = main.params[ 'switches' ][ 'spinedpid2' ]
            main.spines.append( spine )

            spine = {}
            spine[ 'name' ] = main.params[ 'switches' ][ 'spine3' ]
            spine[ 'dpid' ] = main.params[ 'switches' ][ 'spinedpid3' ]
            main.spines.append( spine )

            spine = {}
            spine[ 'name' ] = main.params[ 'switches' ][ 'spine4' ]
            spine[ 'dpid' ] = main.params[ 'switches' ][ 'spinedpid4' ]
            main.spines.append( spine )

        else:
            main.log.error( "Configuration failed!" )
            main.cleanAndExit()

    @staticmethod
    def addStaticOnosRoute( main, subnet, intf):
        """
        Adds an ONOS static route with the use route-add command.
        """
        main.step("Add static route for subnet {0} towards router interface {1}".format(subnet, intf))
        routeResult = main.Cluster.active( 0 ).addStaticRoute(subnet, intf)

        utilities.assert_equals( expect=True, actual=( not routeResult ),
                                 onpass="route-add command succeeded",
                                 onfail="route-add command failed")

    @staticmethod
    def checkGroupsForBuckets( main, deviceId, subnetDict, routingTable=30 ):
        """
        Check number of groups for each subnet on device deviceId and matches
        it with an expected value. subnetDict is a dictionarty containing values
        of the type "10.0.1.0/24" : 5.
        """
        main.step( "Checking if number of groups for subnets in device {0} is as expected.".format( deviceId ) )
        groups = main.Cluster.active( 0 ).CLI.getGroups( deviceId, groupType="select" )
        flows = main.Cluster.active( 0 ).CLI.flows( jsonFormat=False, device=deviceId )

        result = main.TRUE
        for subnet, numberInSelect in subnetDict.iteritems():
            for flow in flows.splitlines():
                if "tableId={0}".format( routingTable ) in flow and subnet in flow:
                    # this will match the group id that this flow entry points to, for example :
                    # 0x70000041 in flow entry which contains "deferred=[GROUP:0x70000041], transition=TABLE:60,"
                    groupId = re.search( r".*GROUP:(0x.*)], transition.*", flow ).groups()[0]
                    count = 0
                    for group in groups.splitlines():
                        if 'id={0}'.format( groupId ) in group:
                            count += 1
                    if count - 1 != numberInSelect:
                        result = main.FALSE
                        main.log.warn( "Mismatch in number of buckets of select group, found {0}, expected {1} for subnet {2} on device {3}".format( count - 1, numberInSelect, subnet, deviceId ) )
        utilities.assert_equals( expect=main.TRUE, actual=result,
                                 onpass="All bucket numbers are as expected",
                                 onfail="Some bucket numbers are not as expected" )

    @staticmethod
    def checkFlows( main, minFlowCount, tag="", dumpflows=True, sleep=10 ):
        main.step(
                "Check whether the flow count is bigger than %s" % minFlowCount )
        if tag == "":
            tag = 'CASE%d' % main.CurrentTestCaseNumber
        count = utilities.retry( main.Cluster.active( 0 ).CLI.checkFlowCount,
                                 main.FALSE,
                                 kwargs={ 'min': minFlowCount },
                                 attempts=10,
                                 sleep=sleep )
        if count == main.FALSE:
            count = main.Cluster.active( 0 ).CLI.checkFlowCount()
        utilities.assertEquals(
                expect=True,
                actual=( count > minFlowCount ),
                onpass="Flow count looks correct: " + str( count ),
                onfail="Flow count looks wrong: " + str( count ) )

        main.step( "Check whether all flow status are ADDED" )
        flowCheck = utilities.retry( main.Cluster.active( 0 ).CLI.checkFlowsState,
                                     main.FALSE,
                                     kwargs={ 'isPENDING': False },
                                     attempts=5,
                                     sleep=sleep )
        utilities.assertEquals(
                expect=main.TRUE,
                actual=flowCheck,
                onpass="Flow status is correct!",
                onfail="Flow status is wrong!" )
        if dumpflows:
            main.ONOSbench.dumpONOSCmd( main.Cluster.active( 0 ).ipAddress,
                                        "flows",
                                        main.logdir,
                                        tag + "_FlowsBefore" )
            main.ONOSbench.dumpONOSCmd( main.Cluster.active( 0 ).ipAddress,
                                        "groups",
                                        main.logdir,
                                        tag + "_GroupsBefore" )

    @staticmethod
    def checkDevices( main, switches, tag="", sleep=10 ):
        main.step(
                "Check whether the switches count is equal to %s" % switches )
        if tag == "":
            tag = 'CASE%d' % main.CurrentTestCaseNumber
        result = utilities.retry( main.Cluster.active( 0 ).CLI.checkStatus,
                                    main.FALSE,
                                    kwargs={ 'numoswitch': switches},
                                    attempts=10,
                                    sleep=sleep )
        utilities.assert_equals( expect=main.TRUE, actual=result,
                                 onpass="Device up successful",
                                 onfail="Failed to boot up devices?" )

    @staticmethod
    def checkFlowsByDpid( main, dpid, minFlowCount, sleep=10 ):
        main.step(
            " Check whether the flow count of device %s is bigger than %s" % ( dpid, minFlowCount ) )
        count = utilities.retry( main.Cluster.active( 0 ).CLI.checkFlowAddedCount,
                                 main.FALSE,
                                 args=( dpid, minFlowCount ),
                                 attempts=5,
                                 sleep=sleep )
        if count == main.FALSE:
            count = main.Cluster.active( 0 ).CLI.checkFlowAddedCount( dpid )
        utilities.assertEquals(
            expect=True,
            actual=( count > minFlowCount ),
            onpass="Flow count looks correct: " + str( count ),
            onfail="Flow count looks wrong: " + str( count ) )

    @staticmethod
    def checkFlowEqualityByDpid( main, dpid, flowCount, sleep=10 ):
        main.step(
                " Check whether the flow count of device %s is equal to %s" % ( dpid, flowCount ) )
        count = utilities.retry( main.Cluster.active( 0 ).CLI.checkFlowAddedCount,
                                 main.FALSE,
                                 args=( dpid, flowCount, False, 1 ),
                                 attempts=5,
                                 sleep=sleep )
        if count == main.FALSE:
            count = main.Cluster.active( 0 ).CLI.checkFlowAddedCount( dpid )
        utilities.assertEquals(
                expect=True,
                actual=( count == flowCount ),
                onpass="Flow count looks correct: " + str( count ) ,
                onfail="Flow count looks wrong. found {},  should be {}.".format( count, flowCount ) )

    @staticmethod
    def checkGroupEqualityByDpid( main, dpid, groupCount, sleep=10):
        main.step(
                " Check whether the group count of device %s is equal to %s" % ( dpid, groupCount ) )
        count = utilities.retry( main.Cluster.active( 0 ).CLI.checkGroupAddedCount,
                                 main.FALSE,
                                 args=( dpid, groupCount, False, 1),
                                 attempts=5,
                                 sleep=sleep )
        if count == main.FALSE:
            count = main.Cluster.active( 0 ).CLI.checkGroupAddedCount( dpid )
        utilities.assertEquals(
                expect=True,
                actual=( count == groupCount ),
                onpass="Group count looks correct: " + str( count ) ,
                onfail="Group count looks wrong. found {},  should be {}.".format( count, groupCount ) )

    @staticmethod
    def checkFlowsGroupsFromFile( main ):

        for dpid, values in main.count.items():
            flowCount = values["flows"]
            groupCount = values["groups"]
            main.log.report( "Check flow count for dpid " + str( dpid ) +
                             ", should be " + str( flowCount ) )
            Testcaselib.checkFlowEqualityByDpid( main, dpid, flowCount )

            main.log.report( "Check group count for dpid " + str( dpid ) +
                             ", should be " + str( groupCount ) )
            Testcaselib.checkGroupEqualityByDpid( main, dpid, groupCount )

        return

    @staticmethod
    def pingAll( main, tag="", dumpflows=True, acceptableFailed=0, basedOnIp=False,
                 sleep=10, retryAttempts=1, skipOnFail=False ):
        '''
        Verify connectivity between hosts according to the ping chart
        acceptableFailed: max number of acceptable failed pings.
        basedOnIp: if True, run ping or ping6 based on suffix of host names
        retryAttempts: the number of retry ping. Only works for IPv4 hosts.
        '''
        main.log.report( "Check host connectivity" )
        main.log.debug( "Ping chart: %s" % main.pingChart )
        if tag == "":
            tag = 'CASE%d' % main.CurrentTestCaseNumber
        for entry in main.pingChart.itervalues():
            main.log.debug( "Entry in ping chart: %s" % entry )
            expect = entry[ 'expect' ]
            if expect == "Unidirectional":
                # Verify ping from each src host to each dst host
                src = entry[ 'src' ]
                dst = entry[ 'dst' ]
                expect = main.TRUE
                main.step( "Verify unidirectional connectivity from %s to %s with tag %s" % ( str( src ), str( dst ), tag ) )
                if basedOnIp:
                    if ("v4" in src[0]):
                        pa = main.Network.pingallHostsUnidirectional( src, dst, acceptableFailed=acceptableFailed )
                        utilities.assert_equals( expect=expect, actual=pa,
                                                 onpass="IPv4 connectivity successfully tested",
                                                 onfail="IPv4 connectivity failed" )
                    if ("v6" in src[0]):
                        pa = main.Network.pingallHostsUnidirectional( src, dst, ipv6=True, acceptableFailed=acceptableFailed )
                        utilities.assert_equals( expect=expect, actual=pa,
                                                 onpass="IPv6 connectivity successfully tested",
                                                 onfail="IPv6 connectivity failed" )
                else:
                    pa = main.Network.pingallHostsUnidirectional( src, dst, acceptableFailed=acceptableFailed )
                    utilities.assert_equals( expect=expect, actual=pa,
                                             onpass="IP connectivity successfully tested",
                                             onfail="IP connectivity failed" )
            else:
                # Verify ping between each host pair
                hosts = entry[ 'hosts' ]
                try:
                    expect = main.TRUE if str(expect).lower() == 'true' else main.FALSE
                except:
                    expect = main.FALSE
                main.step( "Verify full connectivity for %s with tag %s" % ( str( hosts ), tag ) )
                if basedOnIp:
                    if ("v4" in hosts[0]):
                        pa = utilities.retry( main.Network.pingallHosts,
                                              main.FALSE if expect else main.TRUE,
                                              args=(hosts,),
                                              attempts=retryAttempts,
                                              sleep=sleep )
                        utilities.assert_equals( expect=expect, actual=pa,
                                                 onpass="IPv4 connectivity successfully tested",
                                                 onfail="IPv4 connectivity failed" )
                    if ("v6" in hosts[0]):
                        pa = main.Network.pingIpv6Hosts( hosts, acceptableFailed=acceptableFailed )
                        utilities.assert_equals( expect=expect, actual=pa,
                                                 onpass="IPv6 connectivity successfully tested",
                                                 onfail="IPv6 connectivity failed" )
                else:
                    pa = main.Network.pingallHosts( hosts )
                    utilities.assert_equals( expect=expect, actual=pa,
                                             onpass="IP connectivity successfully tested",
                                             onfail="IP connectivity failed" )
            if skipOnFail and pa != expect:
                Testcaselib.saveOnosDiagnostics( main )
                Testcaselib.cleanup( main, copyKarafLog=False )
                main.skipCase()

        if dumpflows:
            main.ONOSbench.dumpONOSCmd( main.Cluster.active( 0 ).ipAddress,
                                        "flows",
                                        main.logdir,
                                        tag + "_FlowsOn" )
            main.ONOSbench.dumpONOSCmd( main.Cluster.active( 0 ).ipAddress,
                                        "groups",
                                        main.logdir,
                                        tag + "_GroupsOn" )

    @staticmethod
    def killLink( main, end1, end2, switches, links, sleep=None ):
        """
        end1,end2: identify the switches, ex.: 'leaf1', 'spine1'
        switches, links: number of expected switches and links after linkDown, ex.: '4', '6'
        Kill a link and verify ONOS can see the proper link change
        """
        if sleep is None:
            sleep = float( main.params[ 'timers' ][ 'LinkDiscovery' ] )
        else:
            sleep = float( sleep )
        main.step( "Kill link between %s and %s" % ( end1, end2 ) )
        linkDown = main.Network.link( END1=end1, END2=end2, OPTION="down" )
        linkDown = linkDown and main.Network.link( END2=end1, END1=end2, OPTION="down" )
        # TODO: Can remove this, since in the retry we will wait anyways if topology is incorrect
        main.log.info(
                "Waiting %s seconds for link down to be discovered" % sleep )
        time.sleep( sleep )
        topology = utilities.retry( main.Cluster.active( 0 ).CLI.checkStatus,
                                    main.FALSE,
                                    kwargs={ 'numoswitch': switches,
                                             'numolink': links },
                                    attempts=10,
                                    sleep=sleep )
        result = topology and linkDown
        utilities.assert_equals( expect=main.TRUE, actual=result,
                                 onpass="Link down successful",
                                 onfail="Failed to turn off link?" )

    @staticmethod
    def killLinkBatch( main, links, linksAfter, switches, sleep=None ):
        """
        links = list of links (src, dst) to bring down.
        """

        main.step("Killing a batch of links {0}".format(links))
        if sleep is None:
            sleep = float( main.params[ 'timers' ][ 'LinkDiscovery' ] )
        else:
            sleep = float( sleep )

        for end1, end2 in links:
            main.Network.link( END1=end1, END2=end2, OPTION="down")
            main.Network.link( END1=end2, END2=end1, OPTION="down")

        # TODO: Can remove this, since in the retry we will wait anyways if topology is incorrect
        main.log.info(
                "Waiting %s seconds for links down to be discovered" % sleep )
        time.sleep( sleep )

        topology = utilities.retry( main.Cluster.active( 0 ).CLI.checkStatus,
                                    main.FALSE,
                                    kwargs={ 'numoswitch': switches,
                                             'numolink': linksAfter },
                                    attempts=10,
                                    sleep=sleep )

        utilities.assert_equals( expect=main.TRUE, actual=topology,
                                 onpass="Link batch down successful",
                                 onfail="Link batch down failed" )

    @staticmethod
    def restoreLinkBatch( main, links, linksAfter, switches, sleep=None ):
        """
        links = list of link (src, dst) to bring up again.
        """

        main.step("Restoring a batch of links {0}".format(links))
        if sleep is None:
            sleep = float( main.params[ 'timers' ][ 'LinkDiscovery' ] )
        else:
            sleep = float( sleep )

        for end1, end2 in links:
            main.Network.link( END1=end1, END2=end2, OPTION="up")
            main.Network.link( END1=end2, END2=end1, OPTION="up")

        main.log.info(
                "Waiting %s seconds for links up to be discovered" % sleep )
        time.sleep( sleep )

        topology = utilities.retry( main.Cluster.active( 0 ).CLI.checkStatus,
                                    main.FALSE,
                                    kwargs={ 'numoswitch': switches,
                                             'numolink': linksAfter },
                                    attempts=10,
                                    sleep=sleep )

        utilities.assert_equals( expect=main.TRUE, actual=topology,
                                 onpass="Link batch up successful",
                                 onfail="Link batch up failed" )

    @staticmethod
    def disablePortBatch( main, ports, switches=None, links=None, sleep=None ):
        """
        Disable a list of switch ports using 'portstate' and verify ONOS can see the proper link change
        ports: a list of ports to disable ex. [ [ "of:0000000000000001", 1 ] ]
        switches, links: number of expected switches and links after link change, ex.: '4', '6'
        """
        if sleep is None:
            sleep = float( main.params[ 'timers' ][ 'LinkDiscovery' ] )
        else:
            sleep = float( sleep )
        main.step( "Disable a batch of ports" )
        for dpid, port in ports:
            main.Cluster.active( 0 ).CLI.portstate( dpid=dpid, port=port, state="disable" )
        main.log.info( "Waiting {} seconds for port down to be discovered".format( sleep ) )
        time.sleep( sleep )
        if switches and links:
            result = main.Cluster.active( 0 ).CLI.checkStatus( numoswitch=switches,
                                                               numolink=links )
            utilities.assert_equals( expect=main.TRUE, actual=result,
                                     onpass="Port down successful",
                                     onfail="Port down failed" )

    @staticmethod
    def enablePortBatch( main, ports, switches, links, sleep=None ):
        """
        Enable a list of switch ports using 'portstate' and verify ONOS can see the proper link change
        ports: a list of ports to enable ex. [ [ "of:0000000000000001", 1 ] ]
        switches, links: number of expected switches and links after link change, ex.: '4', '6'
        """
        if sleep is None:
            sleep = float( main.params[ 'timers' ][ 'LinkDiscovery' ] )
        else:
            sleep = float( sleep )
        main.step( "Enable a batch of ports" )
        for dpid, port in ports:
            main.Cluster.active( 0 ).CLI.portstate( dpid=dpid, port=port, state="enable" )
        main.log.info( "Waiting {} seconds for port up to be discovered".format( sleep ) )
        time.sleep( sleep )
        if switches and links:
            result = main.Cluster.active( 0 ).CLI.checkStatus( numoswitch=switches,
                                                               numolink=links )
            utilities.assert_equals( expect=main.TRUE, actual=result,
                                     onpass="Port up successful",
                                     onfail="Port up failed" )

    @staticmethod
    def restoreLink( main, end1, end2, switches, links,
                     portUp=False, dpid1='', dpid2='', port1='', port2='', sleep=None ):
        """
        Params:
            end1,end2: identify the end switches, ex.: 'leaf1', 'spine1'
            portUp: enable portstate after restoring link
            dpid1, dpid2: dpid of the end switches respectively, ex.: 'of:0000000000000002'
            port1, port2: respective port of the end switches that connects to the link, ex.:'1'
            switches, links: number of expected switches and links after linkDown, ex.: '4', '6'
        Kill a link and verify ONOS can see the proper link change
        """
        main.step( "Restore link between %s and %s" % ( end1, end2 ) )
        if sleep is None:
            sleep = float( main.params[ 'timers' ][ 'LinkDiscovery' ] )
        else:
            sleep = float( sleep )
        result = False
        count = 0
        while True:
            count += 1
            ctrl = main.Cluster.next()
            main.Network.link( END1=end1, END2=end2, OPTION="up" )
            main.Network.link( END2=end1, END1=end2, OPTION="up" )
            main.log.info(
                    "Waiting %s seconds for link up to be discovered" % sleep )
            time.sleep( sleep )

            if portUp:
                ctrl.CLI.portstate( dpid=dpid1, port=port1, state='Enable' )
                ctrl.CLI.portstate( dpid=dpid2, port=port2, state='Enable' )
                time.sleep( sleep )

            result = ctrl.CLI.checkStatus( numoswitch=switches,
                                           numolink=links )
            if count > 5 or result:
                break
        utilities.assert_equals( expect=main.TRUE, actual=result,
                                 onpass="Link up successful",
                                 onfail="Failed to bring link up" )

    @staticmethod
    def killSwitch( main, switch, switches, links, sleep=None ):
        """
        Params: switches, links: number of expected switches and links after SwitchDown, ex.: '4', '6'
        Completely kill a switch and verify ONOS can see the proper change
        """
        if sleep is None:
            sleep = float( main.params[ 'timers' ][ 'SwitchDiscovery' ] )
        else:
            sleep = float( sleep )
        switch = switch if isinstance( switch, list ) else [ switch ]
        main.step( "Kill " + str( switch ) )
        for s in switch:
            main.log.info( "Stopping " + s )
            main.Network.switch( SW=s, OPTION="stop" )
        # todo make this repeatable

        # TODO: Can remove this, since in the retry we will wait anyways if topology is incorrect
        main.log.info( "Waiting %s seconds for switch down to be discovered" % (
            sleep ) )
        time.sleep( sleep )
        topology = utilities.retry( main.Cluster.active( 0 ).CLI.checkStatus,
                                    main.FALSE,
                                    kwargs={ 'numoswitch': switches,
                                             'numolink': links },
                                    attempts=10,
                                    sleep=sleep )
        utilities.assert_equals( expect=main.TRUE, actual=topology,
                                 onpass="Kill switch successful",
                                 onfail="Failed to kill switch?" )

    @staticmethod
    def recoverSwitch( main, switch, switches, links, rediscoverHosts=False, hostsToDiscover=[], sleep=None ):
        """
        Params: switches, links: number of expected switches and links after SwitchUp, ex.: '4', '6'
        Recover a switch and verify ONOS can see the proper change
        """
        if sleep is None:
            sleep = float( main.params[ 'timers' ][ 'SwitchDiscovery' ] )
        else:
            sleep = float( sleep )
        # TODO make this repeatable
        switch = switch if isinstance( switch, list ) else [ switch ]
        main.step( "Recovering " + str( switch ) )
        for s in switch:
            main.log.info( "Starting " + s )
            main.Network.switch( SW=s, OPTION="start" )
        main.log.info( "Waiting %s seconds for switch up to be discovered" % (
            sleep ) )
        time.sleep( sleep )
        if rediscoverHosts:
            main.Network.discoverHosts( hostList=hostsToDiscover )
            main.log.info( "Waiting %s seconds for hosts to get re-discovered" % (
                           sleep ) )
            time.sleep( sleep )

        topology = utilities.retry( main.Cluster.active( 0 ).CLI.checkStatus,
                                    main.FALSE,
                                    kwargs={ 'numoswitch': switches,
                                             'numolink': links },
                                    attempts=10,
                                    sleep=sleep )
        utilities.assert_equals( expect=main.TRUE, actual=topology,
                                 onpass="Switch recovery successful",
                                 onfail="Failed to recover switch?" )

    @staticmethod
    def killRouter( main, router, sleep=None ):
        """
        Kill bgpd process on a quagga router
        router: name of the router to be killed. E.g. "bgp1"
        """
        sleep = float( sleep )
        main.step( "Kill " + str( router ) )
        if hasattr( main, 'Mininet1' ):
            main.Mininet1.handle.sendline( "px {}.stopProtocols()".format( router ) )
            main.Mininet1.handle.expect( "mininet>" )
        else:
            # TODO: support killing router in physical network
            pass
        main.log.info( "Waiting %s seconds for router down to be discovered" % ( sleep ) )
        time.sleep( sleep )

    @staticmethod
    def recoverRouter( main, router, sleep=None ):
        """
        Restart bgpd process on a quagga router
        router: name of the router to be recovered. E.g. "bgp1"
        """
        sleep = float( sleep )
        main.step( "Recovering " + str( router ) )
        if hasattr( main, 'Mininet1' ):
            main.Mininet1.handle.sendline( "px {}.startProtocols()".format( router ) )
            main.Mininet1.handle.expect( "mininet>" )
        else:
            # TODO: support recovering router in physical network
            pass
        main.log.info( "Waiting %s seconds for router up to be discovered" % ( sleep ) )
        time.sleep( sleep )

    @staticmethod
    def cleanup( main, copyKarafLog=True, removeHostComponent=False ):
        """
        Stop Onos-cluster.
        Stops Mininet
        Copies ONOS log
        """
        from tests.dependencies.utils import Utils
        main.utils = Utils()
        # Clean up scapy hosts
        if hasattr( main, "scapyHosts" ):
            scapyResult = main.TRUE
            for host in main.scapyHosts:
                scapyResult = host.stopScapy() and scapyResult
                main.log.info( "Stopped Scapy Host: {0}".format( host.name ) )
            for host in main.scapyHosts:
                if hasattr( main, 'Mininet1' ):
                    scapyResult = main.Scapy.removeHostComponent( host.name ) and scapyResult
                else:
                    scapyResult = main.Network.removeHostComponent( host.name ) and scapyResult
                main.log.info( "Removed Scapy Host Component: {0}".format( host.name ) )
            main.scapyHosts = []

        if removeHostComponent:
            for host in main.internalIpv4Hosts + main.internalIpv6Hosts + main.externalIpv4Hosts + main.externalIpv6Hosts:
                if hasattr( main, host ):
                    if hasattr( main, 'Mininet1' ):
                        pass
                    else:
                        getattr( main, host ).disconnectInband()
                    main.Network.removeHostComponent( host )

        if hasattr( main, 'Mininet1' ):
            main.utils.mininetCleanup( main.Mininet1 )
        else:
            main.Network.disconnectInbandHosts()
            main.Network.disconnectFromNet()

        if copyKarafLog:
            main.utils.copyKarafLog( "CASE%d" % main.CurrentTestCaseNumber, before=True, includeCaseDesc=False )

        for ctrl in main.Cluster.active():
            main.ONOSbench.onosStop( ctrl.ipAddress )

    @staticmethod
    def verifyNodes( main ):
        """
        Verifies Each active node in the cluster has an accurate view of other node's and their status

        Params:
        nodes, integer array with position of the ONOS nodes in the CLIs array
        """
        nodeResults = utilities.retry( main.Cluster.nodesCheck,
                                       False,
                                       attempts=10,
                                       sleep=10 )
        utilities.assert_equals( expect=True, actual=nodeResults,
                                 onpass="Nodes check successful",
                                 onfail="Nodes check NOT successful" )

        if not nodeResults:
            for ctrl in main.Cluster.runningNodes:
                main.log.debug( "{} components not ACTIVE: \n{}".format(
                    ctrl.name,
                    ctrl.CLI.sendline( "scr:list | grep -v ACTIVE" ) ) )
            main.log.error( "Failed to kill ONOS, stopping test" )
            main.cleanAndExit()

    @staticmethod
    def verifyTopology( main, switches, links, expNodes ):
        """
        Verifies that the ONOS cluster has an acuurate view of the topology

        Params:
        switches, links, expNodes: number of expected switches, links, and nodes at this point in the test ex.: '4', '6', '2'
        """
        main.step( "Check number of topology elements" )
        topology = utilities.retry( main.Cluster.active( 0 ).CLI.checkStatus,
                                    main.FALSE,
                                    kwargs={ 'numoswitch': switches,
                                             'numolink': links,
                                             'numoctrl': expNodes },
                                    attempts=10,
                                    sleep=12 )
        utilities.assert_equals( expect=main.TRUE, actual=topology,
                                 onpass="Number of topology elements are correct",
                                 onfail="Unexpected number of links, switches, and/or controllers" )

    @staticmethod
    def killOnos( main, nodes, switches, links, expNodes, sleep=None ):
        """
        Params: nodes, integer array with position of the ONOS nodes in the CLIs array
        switches, links, nodes: number of expected switches, links and nodes after KillOnos, ex.: '4', '6'
        Completely Kill an ONOS instance and verify the ONOS cluster can see the proper change
        """
        # TODO: We have enough information in the Cluster instance to remove expNodes from here and verifyTopology
        main.step( "Killing ONOS instances with index(es): {}".format( nodes ) )
        if sleep is None:
            sleep = float( main.params[ 'timers' ][ 'OnosDiscovery' ] )
        else:
            sleep = float( sleep )

        for i in nodes:
            killResult = main.ONOSbench.onosDie( main.Cluster.runningNodes[ i ].ipAddress )
            utilities.assert_equals( expect=main.TRUE, actual=killResult,
                                     onpass="ONOS instance Killed",
                                     onfail="Error killing ONOS instance" )
            main.Cluster.runningNodes[ i ].active = False
        main.Cluster.reset()
        time.sleep( sleep )

        if len( nodes ) < main.Cluster.numCtrls:
            Testcaselib.verifyNodes( main )
            Testcaselib.verifyTopology( main, switches, links, expNodes )

    @staticmethod
    def recoverOnos( main, nodes, switches, links, expNodes, sleep=None ):
        """
        Params: nodes, integer array with position of the ONOS nodes in the CLIs array
        switches, links, nodes: number of expected switches, links and nodes after recoverOnos, ex.: '4', '6'
        Recover an ONOS instance and verify the ONOS cluster can see the proper change
        """
        main.step( "Recovering ONOS instances with index(es): {}".format( nodes ) )
        if sleep is None:
            sleep = float( main.params[ 'timers' ][ 'OnosDiscovery' ] )
        else:
            sleep = float( sleep )
        [ main.ONOSbench.onosStart( main.Cluster.runningNodes[ i ].ipAddress ) for i in nodes ]
        time.sleep( sleep )
        for i in nodes:
            isUp = main.ONOSbench.isup( main.Cluster.runningNodes[ i ].ipAddress )
            utilities.assert_equals( expect=main.TRUE, actual=isUp,
                                     onpass="ONOS service is ready",
                                     onfail="ONOS service did not start properly" )
        for i in nodes:
            main.step( "Checking if ONOS CLI is ready" )
            ctrl = main.Cluster.runningNodes[ i ]
            # ctrl.CLI.startCellCli()
            cliResult = ctrl.CLI.startOnosCli( ctrl.ipAddress,
                                               commandlineTimeout=60,
                                               onosStartTimeout=100 )
            ctrl.active = True
            utilities.assert_equals( expect=main.TRUE,
                                     actual=cliResult,
                                     onpass="ONOS CLI is ready",
                                     onfail="ONOS CLI is not ready" )

        main.Cluster.reset()
        main.step( "Checking ONOS nodes" )
        Testcaselib.verifyNodes( main )
        Testcaselib.verifyTopology( main, switches, links, expNodes )

        ready = utilities.retry( main.Cluster.active( 0 ).CLI.summary,
                                 main.FALSE,
                                 attempts=10,
                                 sleep=12 )
        if ready:
            ready = main.TRUE
        utilities.assert_equals( expect=main.TRUE, actual=ready,
                                 onpass="ONOS summary command succeded",
                                 onfail="ONOS summary command failed" )
        if not ready:
            main.log.error( "ONOS startup failed!" )
            main.cleanAndExit()

    @staticmethod
    def addHostCfg( main ):
        """
        Adds Host Configuration to ONOS
        Updates expected state of the network ( pingChart )
        """
        import json
        hostCfg = {}
        with open( main.configPath + main.forJson + "extra.json" ) as template:
            hostCfg = json.load( template )
        main.pingChart[ 'ip' ][ 'hosts' ] += [ 'in1' ]
        main.step( "Pushing new configuration" )
        mac, cfg = hostCfg[ 'hosts' ].popitem()
        main.Cluster.active( 0 ).REST.setNetCfg( cfg[ 'basic' ],
                                                 subjectClass="hosts",
                                                 subjectKey=urllib.quote( mac,
                                                                          safe='' ),
                                                 configKey="basic" )
        main.pingChart[ 'ip' ][ 'hosts' ] += [ 'out1' ]
        main.step( "Pushing new configuration" )
        mac, cfg = hostCfg[ 'hosts' ].popitem()
        main.Cluster.active( 0 ).REST.setNetCfg( cfg[ 'basic' ],
                                                 subjectClass="hosts",
                                                 subjectKey=urllib.quote( mac,
                                                                          safe='' ),
                                                 configKey="basic" )
        main.pingChart.update( { 'vlan1': { "expect": "True",
                                            "hosts": [ "olt1", "vsg1" ] } } )
        main.pingChart[ 'vlan5' ][ 'expect' ] = 0
        main.pingChart[ 'vlan10' ][ 'expect' ] = 0
        ports = "[%s,%s]" % ( 5, 6 )
        cfg = '{"of:0000000000000001":[{"vlan":1,"ports":%s,"name":"OLT 1"}]}' % ports
        main.Cluster.active( 0 ).REST.setNetCfg( json.loads( cfg ),
                                                 subjectClass="apps",
                                                 subjectKey="org.onosproject.segmentrouting",
                                                 configKey="xconnect" )

    @staticmethod
    def delHostCfg( main ):
        """
        Removest Host Configuration from ONOS
        Updates expected state of the network ( pingChart )
        """
        import json
        hostCfg = {}
        with open( main.configPath + main.forJson + "extra.json" ) as template:
            hostCfg = json.load( template )
        main.step( "Removing host configuration" )
        main.pingChart[ 'ip' ][ 'expect' ] = 0
        mac, cfg = hostCfg[ 'hosts' ].popitem()
        main.Cluster.active( 0 ).REST.removeNetCfg( subjectClass="hosts",
                                                    subjectKey=urllib.quote(
                                                            mac,
                                                            safe='' ),
                                                    configKey="basic" )
        main.step( "Removing configuration" )
        main.pingChart[ 'ip' ][ 'expect' ] = 0
        mac, cfg = hostCfg[ 'hosts' ].popitem()
        main.Cluster.active( 0 ).REST.removeNetCfg( subjectClass="hosts",
                                                    subjectKey=urllib.quote(
                                                            mac,
                                                            safe='' ),
                                                    configKey="basic" )
        main.step( "Removing vlan configuration" )
        main.pingChart[ 'vlan1' ][ 'expect' ] = 0
        main.Cluster.active( 0 ).REST.removeNetCfg( subjectClass="apps",
                                                    subjectKey="org.onosproject.segmentrouting",
                                                    configKey="xconnect" )

    @staticmethod
    def verifyNetworkHostIp( main, attempts=10, sleep=10 ):
        """
        Verifies IP address assignment from the hosts
        """
        main.step( "Verify IP address assignment from hosts" )
        ipResult = main.TRUE
        main.Network.update()
        # Find out names of disconnected hosts
        disconnectedHosts = []
        if hasattr( main, "disconnectedIpv4Hosts" ):
            for host in main.disconnectedIpv4Hosts:
                disconnectedHosts.append( host )
        if hasattr( main, "disconnectedIpv6Hosts" ):
            for host in main.disconnectedIpv6Hosts:
                disconnectedHosts.append( host )
        for hostName, ip in main.expectedHosts[ "network" ].items():
            # Exclude disconnected hosts
            if hostName in disconnectedHosts:
                main.log.debug( "Skip verifying IP for {} as it's disconnected".format( hostName ) )
                continue
            ipResult = ipResult and utilities.retry( main.Network.verifyHostIp,
                                                     main.FALSE,
                                                     kwargs={ 'hostList': [ hostName ],
                                                              'prefix': ip,
                                                              'update': False },
                                                     attempts=attempts,
                                                     sleep=sleep )
        utilities.assert_equals( expect=main.TRUE, actual=ipResult,
                                 onpass="Verify network host IP succeded",
                                 onfail="Verify network host IP failed" )

    @staticmethod
    def verifyOnosHostIp( main, attempts=10, sleep=10, skipOnFail=True ):
        """
        Verifies host IP address assignment from ONOS
        """
        main.step( "Verify host IP address assignment in ONOS" )
        ipResult = main.TRUE
        # Find out IPs of disconnected hosts
        disconnectedIps = []
        if hasattr( main, "disconnectedIpv4Hosts" ):
            for host in main.disconnectedIpv4Hosts:
                disconnectedIps.append( main.expectedHosts[ "network" ][ host ] )
        if hasattr( main, "disconnectedIpv6Hosts" ):
            for host in main.disconnectedIpv6Hosts:
                disconnectedIps.append( main.expectedHosts[ "network" ][ host ] )
        for hostName, ip in main.expectedHosts[ "onos" ].items():
            # Exclude disconnected hosts
            if ip in disconnectedIps:
                main.log.debug( "Skip verifying IP for {} as it's disconnected".format( ip ) )
                continue
            ipResult = ipResult and utilities.retry( main.Cluster.active( 0 ).verifyHostIp,
                                                     main.FALSE,
                                                     kwargs={ 'hostList': [ hostName ],
                                                              'prefix': ip },
                                                     attempts=attempts,
                                                     sleep=sleep )
        utilities.assert_equals( expect=main.TRUE, actual=ipResult,
                                 onpass="Verify ONOS host IP succeded",
                                 onfail="Verify ONOS host IP failed" )
        if not ipResult and skipOnFail:
            Testcaselib.saveOnosDiagnostics( main )
            Testcaselib.cleanup( main, copyKarafLog=False )
            main.skipCase()

    @staticmethod
    def updateIntfCfg( main, connectPoint, ips=[], untagged=0, tagged=[], native=0 ):
        """
        Description:
            Updates interface configuration in ONOS, with given IP and vlan parameters
        Required:
            * connectPoint: connect point to update configuration
        Optional:
            * ips: list of IP addresses, combined with '/xx' subnet representation,
                   corresponding to 'ips' field in the configuration
            * untagged: vlan ID as an integer, corresponding to 'vlan-untagged' field in the configuration
            * tagged: integer list of vlan IDs, corresponding to 'vlan-tagged' field in the configuration
            * native: vlan ID as an integer, corresponding to 'vlan-native' field in the configuration
        """
        cfg = dict()
        cfg[ "ports" ] = dict()
        cfg[ "ports" ][ connectPoint ] = dict()
        cfg[ "ports" ][ connectPoint ][ "interfaces" ] = [ dict() ]
        cfg[ "ports" ][ connectPoint ][ "interfaces" ][ 0 ][ "ips" ] = ips
        if untagged > 0:
            cfg[ "ports" ][ connectPoint ][ "interfaces" ][ 0 ][ "vlan-untagged" ] = untagged
        else:
            cfg[ "ports" ][ connectPoint ][ "interfaces" ][ 0 ][ "vlan-tagged" ] = tagged
            if native > 0:
                cfg[ "ports" ][ connectPoint ][ "interfaces" ][ 0 ][ "vlan-native" ] = native

        main.Cluster.active( 0 ).REST.setNetCfg( json.loads( json.dumps( cfg ) ) )

    @staticmethod
    def startScapyHosts( main, scapyNames=[], mininetNames=[] ):
        """
        Create host components and start Scapy CLIs
        scapyNames: list of names that will be used as component names for scapy hosts
        mininetNames: used when scapy host names are different from the host names
        in Mininet. E.g. when scapyNames=['h1Scapy'], it's required to specify the
        name of the corresponding Mininet host by mininetNames=['h1']
        """
        main.step( "Start Scapy CLIs" )
        main.scapyNames = scapyNames if scapyNames else main.params[ 'SCAPY' ][ 'HOSTNAMES' ].split( ',' )
        main.scapyHosts = [] if not hasattr( main, "scapyHosts" ) else main.scapyHosts
        for scapyName in main.scapyNames:
            if hasattr( main, 'Mininet1' ):
                main.Scapy.createHostComponent( scapyName )
                scapyHandle = getattr( main, scapyName )
                if mininetNames:
                    mininetName = mininetNames[ scapyNames.index( scapyName ) ]
                else:
                    mininetName = None
                scapyHandle.startHostCli( mininetName )
            else:
                main.Network.createHostComponent( scapyName )
                scapyHandle = getattr( main, scapyName )
                scapyHandle.connectInband()
            main.scapyHosts.append( scapyHandle )
            scapyHandle.startScapy()
            scapyHandle.updateSelf()
            main.log.debug( scapyHandle.name )
            main.log.debug( scapyHandle.hostIp )
            main.log.debug( scapyHandle.hostMac )

    @staticmethod
    def verifyTraffic( main, srcHosts, dstIp, dstHost, dstIntf, ipv6=False, expect=True, skipOnFail=True, maxRetry=2 ):
        """
        Verify unicast traffic by pinging from source hosts to the destination IP
        and capturing the packets at the destination host using Scapy.
        srcHosts: List of host names to send the ping packets
        dstIp: destination IP of the ping packets
        dstHost: host that runs Scapy to capture the packets
        dstIntf: name of the interface on the destination host
        expect: use True if the ping is expected to be captured at destination;
                Otherwise False
        skipOnFail: skip the rest of this test case if result is not expected
        maxRetry: number of retries allowed
        """
        from tests.dependencies.topology import Topology
        try:
            main.topo
        except ( NameError, AttributeError ):
            main.topo = Topology()
        main.step( "Verify traffic to {} by capturing packets on {}".format( dstIp, dstHost ) )
        result = main.TRUE
        for srcHost in srcHosts:
            trafficResult = main.topo.pingAndCapture( srcHost, dstIp, dstHost, dstIntf, ipv6,
                                                      expect, maxRetry, True )
            if not trafficResult:
                result = main.FALSE
                main.log.warn( "Scapy result from {} to {} is not as expected".format( srcHost, dstIp ) )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=result,
                                 onpass="Verify traffic to {}: Pass".format( dstIp ),
                                 onfail="Verify traffic to {}: Fail".format( dstIp ) )
        if skipOnFail and result != main.TRUE:
            Testcaselib.saveOnosDiagnostics( main )
            Testcaselib.cleanup( main, copyKarafLog=False )
            main.skipCase()

    @staticmethod
    def verifyMulticastTraffic( main, routeName, expect, skipOnFail=True, maxRetry=1 ):
        """
        Verify multicast traffic using scapy
        """
        from tests.dependencies.topology import Topology
        try:
            main.topo
        except ( NameError, AttributeError ):
            main.topo = Topology()
        main.step( "Verify {} multicast traffic".format( routeName ) )
        routeData = main.multicastConfig[ routeName ]
        srcs = main.mcastRoutes[ routeName ][ "src" ]
        dsts = main.mcastRoutes[ routeName ][ "dst" ]
        main.log.info( "Sending multicast traffic from {} to {}".format( [ routeData[ "src" ][ i ][ "host" ] for i in srcs ],
                                                                         [ routeData[ "dst" ][ i ][ "host" ] for i in dsts ] ) )
        result = main.TRUE
        for src in srcs:
            srcEntry = routeData[ "src" ][ src ]
            for dst in dsts:
                dstEntry = routeData[ "dst" ][ dst ]
                sender = getattr( main, srcEntry[ "host" ] )
                receiver = getattr( main, dstEntry[ "host" ] )
                main.Network.addRoute( str( srcEntry[ "host" ] ),
                                       str( routeData[ "group" ] ),
                                       str( srcEntry[ "interface" ] ),
                                       True if routeData[ "ipVersion" ] == 6 else False )
                # Build the packet
                sender.buildEther( dst=str( srcEntry[ "Ether" ] ) )
                if routeData[ "ipVersion" ] == 4:
                    sender.buildIP( dst=str( routeData[ "group" ] ) )
                elif routeData[ "ipVersion" ] == 6:
                    sender.buildIPv6( dst=str( routeData[ "group" ] ) )
                sender.buildUDP( ipVersion=routeData[ "ipVersion" ], dport=srcEntry[ "UDP" ] )
                sIface = srcEntry[ "interface" ]
                dIface = dstEntry[ "interface" ] if "interface" in dstEntry.keys() else None
                pktFilter = srcEntry[ "filter" ]
                pkt = srcEntry[ "packet" ]
                # Send packet and check received packet
                expectedResult = expect.pop( 0 ) if isinstance( expect, list ) else expect
                t3Cmd = "t3-troubleshoot -vv -sp {} -et ipv{} -d {} -dm {}".format( srcEntry[ "port" ], routeData[ "ipVersion" ],
                                                                                    routeData[ "group" ], srcEntry[ "Ether" ] )
                trafficResult = main.topo.sendScapyPackets( sender, receiver, pktFilter, pkt, sIface, dIface,
                                                            expectedResult, maxRetry, True, t3Cmd )
                if not trafficResult:
                    result = main.FALSE
                    main.log.warn( "Scapy result from {} to {} is not as expected".format( srcEntry[ "host" ],
                                                                                           dstEntry[ "host" ] ) )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=result,
                                 onpass="Verify {} multicast traffic: Pass".format( routeName ),
                                 onfail="Verify {} multicast traffic: Fail".format( routeName ) )
        if skipOnFail and result != main.TRUE:
            Testcaselib.saveOnosDiagnostics( main )
            Testcaselib.cleanup( main, copyKarafLog=False )
            main.skipCase()

    @staticmethod
    def verifyPing( main, srcList, dstList, ipv6=False, expect=True, wait=1,
                    acceptableFailed=0, skipOnFail=True, stepMsg="Verify Ping",
                    t3Simple=True ):
        """
        Verify reachability from each host in srcList to each host in dstList
        """
        from tests.dependencies.topology import Topology
        try:
            main.topo
        except ( NameError, AttributeError ):
            main.topo = Topology()
        main.step( stepMsg )
        pingResult = main.topo.ping( srcList, dstList, ipv6, expect, wait, acceptableFailed, skipOnFail, t3Simple )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=pingResult,
                                 onpass="{}: Pass".format( stepMsg ),
                                 onfail="{}: Fail".format( stepMsg ) )
        if not pingResult and skipOnFail:
            Testcaselib.saveOnosDiagnostics( main )
            Testcaselib.cleanup( main, copyKarafLog=False, removeHostComponent=True )
            main.skipCase()

    @staticmethod
    def verifyHostLocations( main, locationDict, retry=2 ):
        """
        Verify if the specified host is discovered by ONOS on the given locations
        Required:
            locationDict: a dictionary that maps host names to expected locations.
                          locations could be a string or a list.
                          ex. { "h1v4": ["of:0000000000000005/8"] }
        Returns:
            main.TRUE if host is discovered on all locations provided, otherwise main.FALSE
        """
        main.step( "Verify locations of hosts {}".format( locationDict.keys() ) )
        result = main.TRUE
        for hostName, locations in locationDict.items():
            main.log.info( "Verify host {} is discovered at {}".format( hostName, locations ) )
            hostIp = main.Network.getIPAddress( hostName, proto='IPV4' )
            if not hostIp:
                hostIp = main.Network.getIPAddress( hostName, proto='IPV6' )
            if not hostIp:
                main.log.warn( "Failed to find IP address for host {}, skipping location verification".format( hostName ) )
                result = main.FALSE
                continue
            locationResult = utilities.retry( main.Cluster.active( 0 ).CLI.verifyHostLocation,
                                              main.FALSE,
                                              args=( hostIp, locations ),
                                              attempts=retry + 1,
                                              sleep=10 )
            if not locationResult:
                result = main.FALSE
                main.log.warn( "location verification for host {} failed".format( hostName ) )
        utilities.assert_equals( expect=main.TRUE, actual=result,
                                 onpass="Location verification passed",
                                 onfail="Location verification failed" )

    @staticmethod
    def moveHost( main, hostName, srcSw, dstSw, gw, macAddr=None, prefixLen=None, cfg='', ipv6=False, vlan=None ):
        """
        Move specified host from srcSw to dstSw.
        If srcSw and dstSw are same, the host will be moved from current port to
        next available port.
        Required:
            hostName: name of the host. e.g., "h1"
            srcSw: name of the switch that the host is attached to. e.g., "leaf1"
            dstSw: name of the switch that the host will be moved to. e.g., "leaf2"
            gw: ip address of the gateway of the new location
        Optional:
            macAddr: if specified, change MAC address of the host to the specified MAC address.
            prefixLen: prefix length
            cfg: port configuration as JSON string
            ipv6: Use True to move IPv6 host
            vlan: vlan number of the host
        """
        if not hasattr( main, 'Mininet1' ):
            main.log.warn( "moveHost is supposed to be used only in Mininet." )
            return

        main.step( "Moving {} host {} from {} to {}".format( 'tagged' if vlan else 'untagged', hostName, srcSw, dstSw ) )
        main.Mininet1.moveHost( hostName, srcSw, dstSw, macAddr, prefixLen, ipv6, vlan=vlan )
        if not ipv6:
            main.Mininet1.changeDefaultGateway( hostName, gw )
        if cfg:
            main.Cluster.active( 0 ).REST.setNetCfg( json.loads( cfg ),
                                                     subjectClass="ports" )
            # Wait for the host to get RA for setting up default gateway
            time.sleep( 5 )

        main.Mininet1.discoverHosts( [ hostName, ] )

        # Update expectedHost when MAC address is changed.
        if macAddr is not None:
            ipAddr = main.expectedHosts[ "network" ][ hostName ]
            if ipAddr is not None:
                for hostName, ip in main.expectedHosts[ "onos" ].items():
                    if ip == ipAddr:
                        vlan = hostName.split( "/" )[ -1 ]
                        del main.expectedHosts[ "onos" ][ hostName ]
                        main.expectedHosts[ "onos" ][ "{}/{}".format( macAddr.upper(), vlan ) ] = ip
                        break

    @staticmethod
    def moveDualHomedHost( main, hostName, srcSw, srcPairSw, dstSw, dstPairSw, gw,
                           macAddr=None, prefixLen=24, cfg='', ipv6=False, vlan=None ):
        """
        Move specified dual-homed host from srcSw-srcPairSw to dstSw-dstPairSw.
        If srcSw-srcPairSw and dstSw-dstPairSw are same, the host will be moved from current port
        to next available port.
        Required:
            hostName: name of the host. e.g., "h1"
            srcSw: name of the switch that the host is attached to. e.g., "leaf1"
            srcPairSw: name of the paired-switch that the host is attached to. e.g., "leaf2"
            dstSw: name of the switch that the host will be moved to. e.g., "leaf1"
            dstPairSw: name of the paired-switch that the host will be moved to. e.g., "leaf2"
            gw: ip address of the gateway of the new location
        Optional:
            macAddr: if specified, change MAC address of the host to the specified MAC address.
            prefixLen: prefix length
            cfg: port configurations as JSON string
            ipv6: Use True to move IPv6 host
            vlan: vlan number of the host
        """
        if not hasattr( main, 'Mininet1' ):
            main.log.warn( "moveDualHomedHost is supposed to be used only in Mininet." )
            return

        main.step( "Moving {} host {} from {} and {} to {} and {}".format( 'tagged' if vlan else 'untagged', hostName,
                                                                           srcSw, srcPairSw, dstSw, dstPairSw ) )
        main.Mininet1.moveDualHomedHost( hostName, srcSw, srcPairSw, dstSw, dstPairSw,
                                         macAddr=macAddr, prefixLen=prefixLen, ipv6=ipv6, vlan=vlan )
        if not ipv6:
            main.Mininet1.changeDefaultGateway( hostName, gw )
        if cfg:
            main.Cluster.active( 0 ).REST.setNetCfg( json.loads( cfg ),
                                                     subjectClass="ports" )
            # Wait for the host to get RA for setting up default gateway
            time.sleep( 5 )

        main.Mininet1.discoverHosts( [ hostName, ] )

        # Update expectedHost when MAC address is changed.
        if macAddr is not None:
            ipAddr = main.expectedHosts[ "network" ][ hostName ]
            if ipAddr is not None:
                for hostName, ip in main.expectedHosts[ "onos" ].items():
                    if ip == ipAddr:
                        vlan = hostName.split( "/" )[ -1 ]
                        del main.expectedHosts[ "onos" ][ hostName ]
                        main.expectedHosts[ "onos" ][ "{}/{}".format( macAddr.upper(), vlan ) ] = ip
