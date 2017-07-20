"""
Copyright 2015 Open Networking Foundation (ONF)

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

import json
import time


class HA():

    def __init__( self ):
        self.default = ''

    def customizeOnosGenPartitions( self ):
        # copy gen-partions file to ONOS
        # NOTE: this assumes TestON and ONOS are on the same machine
        srcFile = main.testDir + "/HA/dependencies/onos-gen-partitions"
        dstDir = main.ONOSbench.home + "/tools/test/bin/onos-gen-partitions"
        cpResult = main.ONOSbench.secureCopy( main.ONOSbench.user_name,
                                              main.ONOSbench.ip_address,
                                              srcFile,
                                              dstDir,
                                              pwd=main.ONOSbench.pwd,
                                              direction="from" )

    def cleanUpGenPartition( self ):
        # clean up gen-partitions file
        try:
            main.ONOSbench.handle.sendline( "cd " + main.ONOSbench.home )
            main.ONOSbench.handle.expect( main.ONOSbench.home + "\$" )
            main.ONOSbench.handle.sendline( "git checkout -- tools/test/bin/onos-gen-partitions" )
            main.ONOSbench.handle.expect( main.ONOSbench.home + "\$" )
            main.log.info( " Cleaning custom gen partitions file, response was: \n" +
                           str( main.ONOSbench.handle.before ) )
        except ( pexpect.TIMEOUT, pexpect.EOF ):
            main.log.exception( "ONOSbench: pexpect exception found:" +
                                main.ONOSbench.handle.before )
            main.cleanup()
            main.exit()

    def startingMininet( self ):
        main.step( "Starting Mininet" )
        # scp topo file to mininet
        # TODO: move to params?
        topoName = "obelisk.py"
        filePath = main.ONOSbench.home + "/tools/test/topos/"
        main.ONOSbench.scp( main.Mininet1,
                            filePath + topoName,
                            main.Mininet1.home,
                            direction="to" )
        mnResult = main.Mininet1.startNet()
        utilities.assert_equals( expect=main.TRUE, actual=mnResult,
                                 onpass="Mininet Started",
                                 onfail="Error starting Mininet" )

    def scalingMetadata( self ):
        import re
        main.step( "Generate initial metadata file" )
        main.scaling = main.params[ 'scaling' ].split( "," )
        main.log.debug( main.scaling )
        scale = main.scaling.pop( 0 )
        main.log.debug( scale )
        if "e" in scale:
            equal = True
        else:
            equal = False
        main.log.debug( equal )
        main.Cluster.setRunningNode( int( re.search( "\d+", scale ).group( 0 ) ) )
        genResult = main.Server.generateFile( main.Cluster.numCtrls, equal=equal )
        utilities.assert_equals( expect=main.TRUE, actual=genResult,
                                 onpass="New cluster metadata file generated",
                                 onfail="Failled to generate new metadata file" )

    def swapNodeMetadata( self ):
        main.step( "Generate initial metadata file" )
        if main.Cluster.numCtrls >= 5:
            main.Cluster.setRunningNode( main.Cluster.numCtrls - 2 )
        else:
            main.log.error( "Not enough ONOS nodes to run this test. Requires 5 or more" )
        genResult = main.Server.generateFile( main.Cluster.numCtrls )
        utilities.assert_equals( expect=main.TRUE, actual=genResult,
                                 onpass="New cluster metadata file generated",
                                 onfail="Failled to generate new metadata file" )

    def setServerForCluster( self ):
        import os
        main.step( "Setup server for cluster metadata file" )
        main.serverPort = main.params[ 'server' ][ 'port' ]
        rootDir = os.path.dirname( main.testFile ) + "/dependencies"
        main.log.debug( "Root dir: {}".format( rootDir ) )
        status = main.Server.start( main.ONOSbench,
                                    rootDir,
                                    port=main.serverPort,
                                    logDir=main.logdir + "/server.log" )
        utilities.assert_equals( expect=main.TRUE, actual=status,
                                 onpass="Server started",
                                 onfail="Failled to start SimpleHTTPServer" )

    def copyingBackupConfig( self ):
        main.step( "Copying backup config files" )
        main.onosServicepath = main.ONOSbench.home + "/tools/package/bin/onos-service"
        cp = main.ONOSbench.scp( main.ONOSbench,
                                 main.onosServicepath,
                                 main.onosServicepath + ".backup",
                                 direction="to" )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=cp,
                                 onpass="Copy backup config file succeeded",
                                 onfail="Copy backup config file failed" )
        # we need to modify the onos-service file to use remote metadata file
        # url for cluster metadata file
        iface = main.params[ 'server' ].get( 'interface' )
        ip = main.ONOSbench.getIpAddr( iface=iface )
        metaFile = "cluster.json"
        javaArgs = r"-Donos.cluster.metadata.uri=http:\/\/{}:{}\/{}".format( ip, main.serverPort, metaFile )
        main.log.warn( javaArgs )
        main.log.warn( repr( javaArgs ) )
        handle = main.ONOSbench.handle
        sed = r"sed -i 's/bash/bash\nexport JAVA_OPTS=${{JAVA_OPTS:-{}}}\n/' {}".format( javaArgs, main.onosServicepath )
        main.log.warn( sed )
        main.log.warn( repr( sed ) )
        handle.sendline( sed )
        handle.expect( metaFile )
        output = handle.before
        handle.expect( "\$" )
        output += handle.before
        main.log.debug( repr( output ) )

    def cleanUpOnosService( self ):
        # Cleanup custom onos-service file
        main.ONOSbench.scp( main.ONOSbench,
                            main.onosServicepath + ".backup",
                            main.onosServicepath,
                            direction="to" )

    def consistentCheck( self ):
        """
        Checks that TestON counters are consistent across all nodes.

        Returns the tuple ( onosCounters, consistent )
        - onosCounters is the parsed json output of the counters command on
          all nodes
        - consistent is main.TRUE if all "TestON" counters are consitent across
          all nodes or main.FALSE
        """
        try:
            # Get onos counters results
            onosCountersRaw = []
            threads = []
            for ctrl in main.Cluster.active():
                t = main.Thread( target=utilities.retry,
                                 name="counters-" + str( ctrl ),
                                 args=[ ctrl.counters, [ None ] ],
                                 kwargs={ 'sleep': 5, 'attempts': 5,
                                           'randomTime': True } )
                threads.append( t )
                t.start()
            for t in threads:
                t.join()
                onosCountersRaw.append( t.result )
            onosCounters = []
            for i in range( len( onosCountersRaw ) ):
                try:
                    onosCounters.append( json.loads( onosCountersRaw[ i ] ) )
                except ( ValueError, TypeError ):
                    main.log.error( "Could not parse counters response from " +
                                    str( main.Cluster.active( i ) ) )
                    main.log.warn( repr( onosCountersRaw[ i ] ) )
                    onosCounters.append( [] )

            testCounters = {}
            # make a list of all the "TestON-*" counters in ONOS
            # lookes like a dict whose keys are the name of the ONOS node and
            # values are a list of the counters. I.E.
            # { "ONOS1": [ { "name":"TestON-Partitions","value":56 } ]
            # }
            # NOTE: There is an assumtion that all nodes are active
            #        based on the above for loops
            for controller in enumerate( onosCounters ):
                for key, value in controller[ 1 ].iteritems():
                    if 'TestON' in key:
                        node = str( main.Cluster.active( controller[ 0 ] ) )
                        try:
                            testCounters[ node ].append( { key: value } )
                        except KeyError:
                            testCounters[ node ] = [ { key: value } ]
            # compare the counters on each node
            firstV = testCounters.values()[ 0 ]
            tmp = [ v == firstV for k, v in testCounters.iteritems() ]
            if all( tmp ):
                consistent = main.TRUE
            else:
                consistent = main.FALSE
                main.log.error( "ONOS nodes have different values for counters:\n" +
                                testCounters )
            return ( onosCounters, consistent )
        except Exception:
            main.log.exception( "" )
            main.cleanup()
            main.exit()

    def counterCheck( self, counterName, counterValue ):
        """
        Checks that TestON counters are consistent across all nodes and that
        specified counter is in ONOS with the given value
        """
        try:
            correctResults = main.TRUE
            # Get onos counters results and consistentCheck
            onosCounters, consistent = self.consistentCheck()
            # Check for correct values
            for i in range( len( main.Cluster.active() ) ):
                current = onosCounters[ i ]
                onosValue = None
                try:
                    onosValue = current.get( counterName )
                except AttributeError:
                    node = str( main.Cluster.active( i ) )
                    main.log.exception( node + " counters result " +
                                        "is not as expected" )
                    correctResults = main.FALSE
                if onosValue == counterValue:
                    main.log.info( counterName + " counter value is correct" )
                else:
                    main.log.error( counterName +
                                    " counter value is incorrect," +
                                    " expected value: " + str( counterValue ) +
                                    " current value: " + str( onosValue ) )
                    correctResults = main.FALSE
            return consistent and correctResults
        except Exception:
            main.log.exception( "" )
            main.cleanup()
            main.exit()

    def consistentLeaderboards( self, nodes ):
        TOPIC = 'org.onosproject.election'
        # FIXME: use threads
        # FIXME: should we retry outside the function?
        for n in range( 5 ):  # Retry in case election is still happening
            leaderList = []
            # Get all leaderboards
            for cli in nodes:
                leaderList.append( cli.specificLeaderCandidate( TOPIC ) )
            # Compare leaderboards
            result = all( i == leaderList[ 0 ] for i in leaderList ) and\
                     leaderList is not None
            main.log.debug( leaderList )
            main.log.warn( result )
            if result:
                return ( result, leaderList )
            time.sleep( 5 )  # TODO: paramerterize
        main.log.error( "Inconsistent leaderboards:" + str( leaderList ) )
        return ( result, leaderList )

    def nodesCheck( self, nodes ):
        nodesOutput = []
        results = True
        threads = []
        for node in nodes:
            t = main.Thread( target=node.nodes,
                             name="nodes-" + str( node ),
                             args=[] )
            threads.append( t )
            t.start()

        for t in threads:
            t.join()
            nodesOutput.append( t.result )
        ips = sorted( main.Cluster.getIps( activeOnly=True ) )
        for i in nodesOutput:
            try:
                current = json.loads( i )
                activeIps = []
                currentResult = False
                for node in current:
                    if node[ 'state' ] == 'READY':
                        activeIps.append( node[ 'ip' ] )
                activeIps.sort()
                if ips == activeIps:
                    currentResult = True
            except ( ValueError, TypeError ):
                main.log.error( "Error parsing nodes output" )
                main.log.warn( repr( i ) )
                currentResult = False
            results = results and currentResult
        return results

    def generateGraph( self, testName, plotName="Plot-HA", index=2 ):
        # GRAPHS
        # NOTE: important params here:
        #       job = name of Jenkins job
        #       Plot Name = Plot-HA, only can be used if multiple plots
        #       index = The number of the graph under plot name
        job = testName
        graphs = '<ac:structured-macro ac:name="html">\n'
        graphs += '<ac:plain-text-body><![CDATA[\n'
        graphs += '<iframe src="https://onos-jenkins.onlab.us/job/' + job +\
                  '/plot/' + plotName + '/getPlot?index=' + str( index ) +\
                  '&width=500&height=300"' +\
                  'noborder="0" width="500" height="300" scrolling="yes" ' +\
                  'seamless="seamless"></iframe>\n'
        graphs += ']]></ac:plain-text-body>\n'
        graphs += '</ac:structured-macro>\n'
        main.log.wiki( graphs )

    def initialSetUp( self, serviceClean=False ):
        """
        rest of initialSetup
        """


        if main.params[ 'tcpdump' ].lower() == "true":
            main.step( "Start Packet Capture MN" )
            main.Mininet2.startTcpdump(
                str( main.params[ 'MNtcpdump' ][ 'folder' ] ) + str( main.TEST )
                + "-MN.pcap",
                intf=main.params[ 'MNtcpdump' ][ 'intf' ],
                port=main.params[ 'MNtcpdump' ][ 'port' ] )

        if serviceClean:
            main.step( "Clean up ONOS service changes" )
            main.ONOSbench.handle.sendline( "git checkout -- tools/package/init/onos.conf" )
            main.ONOSbench.handle.expect( "\$" )
            main.ONOSbench.handle.sendline( "git checkout -- tools/package/init/onos.service" )
            main.ONOSbench.handle.expect( "\$" )

        main.step( "Checking ONOS nodes" )
        nodeResults = utilities.retry( self.nodesCheck,
                                       False,
                                       args=[ main.Cluster.active() ],
                                       attempts=5 )

        utilities.assert_equals( expect=True, actual=nodeResults,
                                 onpass="Nodes check successful",
                                 onfail="Nodes check NOT successful" )

        if not nodeResults:
            for ctrl in main.Cluster.active():
                main.log.debug( "{} components not ACTIVE: \n{}".format(
                    ctrl.name,
                    ctrl.CLI.sendline( "scr:list | grep -v ACTIVE" ) ) )
            main.log.error( "Failed to start ONOS, stopping test" )
            main.cleanup()
            main.exit()

        main.step( "Activate apps defined in the params file" )
        # get data from the params
        apps = main.params.get( 'apps' )
        if apps:
            apps = apps.split( ',' )
            main.log.debug( "Apps: " + str( apps ) )
            activateResult = True
            for app in apps:
                main.Cluster.active( 0 ).app( app, "Activate" )
            # TODO: check this worked
            time.sleep( 10 )  # wait for apps to activate
            for app in apps:
                state = main.Cluster.active( 0 ).appStatus( app )
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
        # FIXME: This shoudl be part of the general startup sequence
        config = main.params.get( 'ONOS_Configuration' )
        if config:
            main.log.debug( config )
            checkResult = main.TRUE
            for component in config:
                for setting in config[ component ]:
                    value = config[ component ][ setting ]
                    check = main.Cluster.next().setCfg( component, setting, value )
                    main.log.info( "Value was changed? {}".format( main.TRUE == check ) )
                    checkResult = check and checkResult
            utilities.assert_equals( expect=main.TRUE,
                                     actual=checkResult,
                                     onpass="Successfully set config",
                                     onfail="Failed to set config" )
        else:
            main.log.warn( "No configurations were specified to be changed after startup" )

        main.step( "Check app ids" )
        appCheck = self.appCheck()
        utilities.assert_equals( expect=True, actual=appCheck,
                                 onpass="App Ids seem to be correct",
                                 onfail="Something is wrong with app Ids" )

    def commonChecks( self ):
        # TODO: make this assertable or assert in here?
        self.topicsCheck()
        self.partitionsCheck()
        self.pendingMapCheck()
        self.appCheck()

    def topicsCheck( self, extraTopics=[] ):
        """
        Check for work partition topics in leaders output
        """
        leaders = main.Cluster.next().leaders()
        missing = False
        try:
            if leaders:
                parsedLeaders = json.loads( leaders )
                output = json.dumps( parsedLeaders,
                                     sort_keys=True,
                                     indent=4,
                                     separators=( ',', ': ' ) )
                main.log.debug( "Leaders: " + output )
                # check for all intent partitions
                topics = []
                for i in range( 14 ):
                    topics.append( "work-partition-" + str( i ) )
                topics += extraTopics
                main.log.debug( topics )
                ONOStopics = [ j[ 'topic' ] for j in parsedLeaders ]
                for topic in topics:
                    if topic not in ONOStopics:
                        main.log.error( "Error: " + topic +
                                        " not in leaders" )
                        missing = True
            else:
                main.log.error( "leaders() returned None" )
        except ( ValueError, TypeError ):
            main.log.exception( "Error parsing leaders" )
            main.log.error( repr( leaders ) )
        if missing:
            #NOTE Can we refactor this into the Cluster class? Maybe an option to print the output of a command from each node?
            for ctrl in main.Cluster.active():
                response = ctrl.CLI.leaders( jsonFormat=False )
                main.log.debug( str( ctrl.name ) + " leaders output: \n" +
                                str( response ) )
        return missing

    def partitionsCheck( self ):
        # TODO: return something assertable
        partitions = main.Cluster.next().partitions()
        try:
            if partitions:
                parsedPartitions = json.loads( partitions )
                output = json.dumps( parsedPartitions,
                                     sort_keys=True,
                                     indent=4,
                                     separators=( ',', ': ' ) )
                main.log.debug( "Partitions: " + output )
                # TODO check for a leader in all paritions
                # TODO check for consistency among nodes
            else:
                main.log.error( "partitions() returned None" )
        except ( ValueError, TypeError ):
            main.log.exception( "Error parsing partitions" )
            main.log.error( repr( partitions ) )

    def pendingMapCheck( self ):
        pendingMap = main.Cluster.next().pendingMap()
        try:
            if pendingMap:
                parsedPending = json.loads( pendingMap )
                output = json.dumps( parsedPending,
                                     sort_keys=True,
                                     indent=4,
                                     separators=( ',', ': ' ) )
                main.log.debug( "Pending map: " + output )
                # TODO check something here?
            else:
                main.log.error( "pendingMap() returned None" )
        except ( ValueError, TypeError ):
            main.log.exception( "Error parsing pending map" )
            main.log.error( repr( pendingMap ) )

    def appCheck( self ):
        """
        Check App IDs on all nodes
        """
        # FIXME: Rename this to appIDCheck? or add a check for isntalled apps
        appResults = main.Cluster.command( "appToIDCheck" )
        appCheck = all( i == main.TRUE for i in appResults )
        if not appCheck:
            ctrl = main.Cluster.active( 0 )
            main.log.debug( "%s apps: %s" % ( ctrl.name, ctrl.apps() ) )
            main.log.debug( "%s appIDs: %s" % ( ctrl.name, ctrl.appIDs() ) )
        return appCheck

    def workQueueStatsCheck( self, workQueueName, completed, inProgress, pending ):
        # Completed
        completedValues = main.Cluster.command( "workQueueTotalCompleted",
                                                args=[ workQueueName ] )
        # Check the results
        completedResults = [ int( x ) == completed for x in completedValues ]
        completedResult = all( completedResults )
        if not completedResult:
            main.log.warn( "Expected Work Queue {} to have {} completed, found {}".format(
                workQueueName, completed, completedValues ) )

        # In Progress
        inProgressValues = main.Cluster.command( "workQueueTotalInProgress",
                                                 args=[ workQueueName ] )
        # Check the results
        inProgressResults = [ int( x ) == inProgress for x in inProgressValues ]
        inProgressResult = all( inProgressResults )
        if not inProgressResult:
            main.log.warn( "Expected Work Queue {} to have {} inProgress, found {}".format(
                workQueueName, inProgress, inProgressValues ) )

        # Pending
        pendingValues = main.Cluster.command( "workQueueTotalPending",
                                              args=[ workQueueName ] )
        # Check the results
        pendingResults = [ int( x ) == pending for x in pendingValues ]
        pendingResult = all( pendingResults )
        if not pendingResult:
            main.log.warn( "Expected Work Queue {} to have {} pending, found {}".format(
                workQueueName, pending, pendingValues ) )
        return completedResult and inProgressResult and pendingResult

    def assignDevices( self, main ):
        """
        Assign devices to controllers
        """
        import re
        assert main, "main not defined"
        assert utilities.assert_equals, "utilities.assert_equals not defined"

        main.case( "Assigning devices to controllers" )
        main.caseExplanation = "Assign switches to ONOS using 'ovs-vsctl' " + \
                               "and check that an ONOS node becomes the " + \
                               "master of the device."
        main.step( "Assign switches to controllers" )

        ipList = main.Cluster.getIps()
        swList = []
        for i in range( 1, 29 ):
            swList.append( "s" + str( i ) )
        main.Mininet1.assignSwController( sw=swList, ip=ipList )

        mastershipCheck = main.TRUE
        for i in range( 1, 29 ):
            response = main.Mininet1.getSwController( "s" + str( i ) )
            try:
                main.log.info( str( response ) )
            except Exception:
                main.log.info( repr( response ) )
            for ctrl in main.Cluster.runningNodes:
                if re.search( "tcp:" + ctrl.ipAddress, response ):
                    mastershipCheck = mastershipCheck and main.TRUE
                else:
                    main.log.error( "Error, node " + repr( ctrl )+ " is " +
                                    "not in the list of controllers s" +
                                    str( i ) + " is connecting to." )
                    mastershipCheck = main.FALSE
        utilities.assert_equals(
            expect=main.TRUE,
            actual=mastershipCheck,
            onpass="Switch mastership assigned correctly",
            onfail="Switches not assigned correctly to controllers" )

    def assignIntents( self, main ):
        """
        Assign intents
        """
        import time
        import json
        assert main, "main not defined"
        assert utilities.assert_equals, "utilities.assert_equals not defined"
        try:
            main.HAlabels
        except ( NameError, AttributeError ):
            main.log.error( "main.HAlabels not defined, setting to []" )
            main.HAlabels = []
        try:
            main.HAdata
        except ( NameError, AttributeError ):
            main.log.error( "data not defined, setting to []" )
            main.HAdata = []
        main.case( "Adding host Intents" )
        main.caseExplanation = "Discover hosts by using pingall then " +\
                                "assign predetermined host-to-host intents." +\
                                " After installation, check that the intent" +\
                                " is distributed to all nodes and the state" +\
                                " is INSTALLED"

        # install onos-app-fwd
        main.step( "Install reactive forwarding app" )
        onosCli = main.Cluster.next()
        installResults = onosCli.activateApp( "org.onosproject.fwd" )
        utilities.assert_equals( expect=main.TRUE, actual=installResults,
                                 onpass="Install fwd successful",
                                 onfail="Install fwd failed" )

        main.step( "Check app ids" )
        appCheck = self.appCheck()
        utilities.assert_equals( expect=True, actual=appCheck,
                                 onpass="App Ids seem to be correct",
                                 onfail="Something is wrong with app Ids" )

        main.step( "Discovering Hosts( Via pingall for now )" )
        # FIXME: Once we have a host discovery mechanism, use that instead
        # REACTIVE FWD test
        pingResult = main.FALSE
        passMsg = "Reactive Pingall test passed"
        time1 = time.time()
        pingResult = main.Mininet1.pingall()
        time2 = time.time()
        if not pingResult:
            main.log.warn( "First pingall failed. Trying again..." )
            pingResult = main.Mininet1.pingall()
            passMsg += " on the second try"
        utilities.assert_equals(
            expect=main.TRUE,
            actual=pingResult,
            onpass=passMsg,
            onfail="Reactive Pingall failed, " +
                   "one or more ping pairs failed" )
        main.log.info( "Time for pingall: %2f seconds" %
                       ( time2 - time1 ) )
        if not pingResult:
            main.cleanup()
            main.exit()
        # timeout for fwd flows
        time.sleep( 11 )
        # uninstall onos-app-fwd
        main.step( "Uninstall reactive forwarding app" )
        uninstallResult = onosCli.deactivateApp( "org.onosproject.fwd" )
        utilities.assert_equals( expect=main.TRUE, actual=uninstallResult,
                                 onpass="Uninstall fwd successful",
                                 onfail="Uninstall fwd failed" )

        main.step( "Check app ids" )
        appCheck2 = self.appCheck()
        utilities.assert_equals( expect=True, actual=appCheck2,
                                 onpass="App Ids seem to be correct",
                                 onfail="Something is wrong with app Ids" )

        main.step( "Add host intents via cli" )
        intentIds = []
        # TODO: move the host numbers to params
        #       Maybe look at all the paths we ping?
        intentAddResult = True
        hostResult = main.TRUE
        for i in range( 8, 18 ):
            main.log.info( "Adding host intent between h" + str( i ) +
                           " and h" + str( i + 10 ) )
            host1 = "00:00:00:00:00:" + \
                str( hex( i )[ 2: ] ).zfill( 2 ).upper()
            host2 = "00:00:00:00:00:" + \
                str( hex( i + 10 )[ 2: ] ).zfill( 2 ).upper()
            # NOTE: getHost can return None
            host1Dict = onosCli.CLI.getHost( host1 )
            host2Dict = onosCli.CLI.getHost( host2 )
            host1Id = None
            host2Id = None
            if host1Dict and host2Dict:
                host1Id = host1Dict.get( 'id', None )
                host2Id = host2Dict.get( 'id', None )
            if host1Id and host2Id:
                nodeNum = len( main.Cluster.active() )
                ctrl = main.Cluster.active( i % nodeNum )
                tmpId = ctrl.CLI.addHostIntent( host1Id, host2Id )
                if tmpId:
                    main.log.info( "Added intent with id: " + tmpId )
                    intentIds.append( tmpId )
                else:
                    main.log.error( "addHostIntent returned: " +
                                     repr( tmpId ) )
            else:
                main.log.error( "Error, getHost() failed for h" + str( i ) +
                                " and/or h" + str( i + 10 ) )
                hosts = main.Cluster.next().hosts()
                try:
                    output = json.dumps( json.loads( hosts ),
                                         sort_keys=True,
                                         indent=4,
                                         separators=( ',', ': ' ) )
                except ( ValueError, TypeError ):
                    output = repr( hosts )
                main.log.debug( "Hosts output: %s" % output )
                hostResult = main.FALSE
        utilities.assert_equals( expect=main.TRUE, actual=hostResult,
                                 onpass="Found a host id for each host",
                                 onfail="Error looking up host ids" )

        intentStart = time.time()
        onosIds = onosCli.getAllIntentsId()
        main.log.info( "Submitted intents: " + str( intentIds ) )
        main.log.info( "Intents in ONOS: " + str( onosIds ) )
        for intent in intentIds:
            if intent in onosIds:
                pass  # intent submitted is in onos
            else:
                intentAddResult = False
        if intentAddResult:
            intentStop = time.time()
        else:
            intentStop = None
        # Print the intent states
        intents = onosCli.intents()
        intentStates = []
        installedCheck = True
        main.log.info( "%-6s%-15s%-15s" % ( 'Count', 'ID', 'State' ) )
        count = 0
        try:
            for intent in json.loads( intents ):
                state = intent.get( 'state', None )
                if "INSTALLED" not in state:
                    installedCheck = False
                intentId = intent.get( 'id', None )
                intentStates.append( ( intentId, state ) )
        except ( ValueError, TypeError ):
            main.log.exception( "Error parsing intents" )
        # add submitted intents not in the store
        tmplist = [ i for i, s in intentStates ]
        missingIntents = False
        for i in intentIds:
            if i not in tmplist:
                intentStates.append( ( i, " - " ) )
                missingIntents = True
        intentStates.sort()
        for i, s in intentStates:
            count += 1
            main.log.info( "%-6s%-15s%-15s" %
                           ( str( count ), str( i ), str( s ) ) )
        self.commonChecks()

        intentAddResult = bool( intentAddResult and not missingIntents and
                                installedCheck )
        if not intentAddResult:
            main.log.error( "Error in pushing host intents to ONOS" )

        main.step( "Intent Anti-Entropy dispersion" )
        for j in range( 100 ):
            correct = True
            main.log.info( "Submitted intents: " + str( sorted( intentIds ) ) )
            for ctrl in main.Cluster.active():
                onosIds = []
                ids = ctrl.getAllIntentsId()
                onosIds.append( ids )
                main.log.debug( "Intents in " + ctrl.name + ": " +
                                str( sorted( onosIds ) ) )
                if sorted( ids ) != sorted( intentIds ):
                    main.log.warn( "Set of intent IDs doesn't match" )
                    correct = False
                    break
                else:
                    intents = json.loads( ctrl.intents() )
                    for intent in intents:
                        if intent[ 'state' ] != "INSTALLED":
                            main.log.warn( "Intent " + intent[ 'id' ] +
                                           " is " + intent[ 'state' ] )
                            correct = False
                            break
            if correct:
                break
            else:
                time.sleep( 1 )
        if not intentStop:
            intentStop = time.time()
        global gossipTime
        gossipTime = intentStop - intentStart
        main.log.info( "It took about " + str( gossipTime ) +
                        " seconds for all intents to appear in each node" )
        append = False
        title = "Gossip Intents"
        count = 1
        while append is False:
            curTitle = title + str( count )
            if curTitle not in main.HAlabels:
                main.HAlabels.append( curTitle )
                main.HAdata.append( str( gossipTime ) )
                append = True
            else:
                count += 1
        gossipPeriod = int( main.params[ 'timers' ][ 'gossip' ] )
        maxGossipTime = gossipPeriod * len( main.Cluster.runningNodes )
        utilities.assert_greater_equals(
                expect=maxGossipTime, actual=gossipTime,
                onpass="ECM anti-entropy for intents worked within " +
                       "expected time",
                onfail="Intent ECM anti-entropy took too long. " +
                       "Expected time:{}, Actual time:{}".format( maxGossipTime,
                                                                  gossipTime ) )
        if gossipTime <= maxGossipTime:
            intentAddResult = True

        pendingMap = main.Cluster.next().pendingMap()
        if not intentAddResult or "key" in pendingMap:
            import time
            installedCheck = True
            main.log.info( "Sleeping 60 seconds to see if intents are found" )
            time.sleep( 60 )
            onosIds = onosCli.getAllIntentsId()
            main.log.info( "Submitted intents: " + str( intentIds ) )
            main.log.info( "Intents in ONOS: " + str( onosIds ) )
            # Print the intent states
            intents = onosCli.intents()
            intentStates = []
            main.log.info( "%-6s%-15s%-15s" % ( 'Count', 'ID', 'State' ) )
            count = 0
            try:
                for intent in json.loads( intents ):
                    # Iter through intents of a node
                    state = intent.get( 'state', None )
                    if "INSTALLED" not in state:
                        installedCheck = False
                    intentId = intent.get( 'id', None )
                    intentStates.append( ( intentId, state ) )
            except ( ValueError, TypeError ):
                main.log.exception( "Error parsing intents" )
            # add submitted intents not in the store
            tmplist = [ i for i, s in intentStates ]
            for i in intentIds:
                if i not in tmplist:
                    intentStates.append( ( i, " - " ) )
            intentStates.sort()
            for i, s in intentStates:
                count += 1
                main.log.info( "%-6s%-15s%-15s" %
                               ( str( count ), str( i ), str( s ) ) )
            self.topicsCheck( [ "org.onosproject.election" ] )
            self.partitionsCheck()
            self.pendingMapCheck()

    def pingAcrossHostIntent( self, main ):
        """
        Ping across added host intents
        """
        import json
        import time
        assert main, "main not defined"
        assert utilities.assert_equals, "utilities.assert_equals not defined"
        main.case( "Verify connectivity by sending traffic across Intents" )
        main.caseExplanation = "Ping across added host intents to check " +\
                                "functionality and check the state of " +\
                                "the intent"

        onosCli = main.Cluster.next()
        main.step( "Check Intent state" )
        installedCheck = False
        loopCount = 0
        while not installedCheck and loopCount < 40:
            installedCheck = True
            # Print the intent states
            intents = onosCli.intents()
            intentStates = []
            main.log.info( "%-6s%-15s%-15s" % ( 'Count', 'ID', 'State' ) )
            count = 0
            # Iter through intents of a node
            try:
                for intent in json.loads( intents ):
                    state = intent.get( 'state', None )
                    if "INSTALLED" not in state:
                        installedCheck = False
                    intentId = intent.get( 'id', None )
                    intentStates.append( ( intentId, state ) )
            except ( ValueError, TypeError ):
                main.log.exception( "Error parsing intents." )
            # Print states
            intentStates.sort()
            for i, s in intentStates:
                count += 1
                main.log.info( "%-6s%-15s%-15s" %
                               ( str( count ), str( i ), str( s ) ) )
            if not installedCheck:
                time.sleep( 1 )
                loopCount += 1
        utilities.assert_equals( expect=True, actual=installedCheck,
                                 onpass="Intents are all INSTALLED",
                                 onfail="Intents are not all in " +
                                        "INSTALLED state" )

        main.step( "Ping across added host intents" )
        PingResult = main.TRUE
        for i in range( 8, 18 ):
            ping = main.Mininet1.pingHost( src="h" + str( i ),
                                           target="h" + str( i + 10 ) )
            PingResult = PingResult and ping
            if ping == main.FALSE:
                main.log.warn( "Ping failed between h" + str( i ) +
                               " and h" + str( i + 10 ) )
            elif ping == main.TRUE:
                main.log.info( "Ping test passed!" )
                # Don't set PingResult or you'd override failures
        if PingResult == main.FALSE:
            main.log.error(
                "Intents have not been installed correctly, pings failed." )
            # TODO: pretty print
            try:
                tmpIntents = onosCli.intents()
                output = json.dumps( json.loads( tmpIntents ),
                                     sort_keys=True,
                                     indent=4,
                                     separators=( ',', ': ' ) )
            except ( ValueError, TypeError ):
               output = repr( tmpIntents )
            main.log.debug( "ONOS1 intents: " + output )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=PingResult,
            onpass="Intents have been installed correctly and pings work",
            onfail="Intents have not been installed correctly, pings failed." )

        main.step( "Check leadership of topics" )
        topicsCheck = self.topicsCheck()
        utilities.assert_equals( expect=False, actual=topicsCheck,
                                 onpass="intent Partitions is in leaders",
                                 onfail="Some topics were lost" )
        self.partitionsCheck()
        self.pendingMapCheck()

        if not installedCheck:
            main.log.info( "Waiting 60 seconds to see if the state of " +
                           "intents change" )
            time.sleep( 60 )
            # Print the intent states
            intents = onosCli.intents()
            intentStates = []
            main.log.info( "%-6s%-15s%-15s" % ( 'Count', 'ID', 'State' ) )
            count = 0
            # Iter through intents of a node
            try:
                for intent in json.loads( intents ):
                    state = intent.get( 'state', None )
                    if "INSTALLED" not in state:
                        installedCheck = False
                    intentId = intent.get( 'id', None )
                    intentStates.append( ( intentId, state ) )
            except ( ValueError, TypeError ):
                main.log.exception( "Error parsing intents." )
            intentStates.sort()
            for i, s in intentStates:
                count += 1
                main.log.info( "%-6s%-15s%-15s" %
                               ( str( count ), str( i ), str( s ) ) )
        self.commonChecks()

        # Print flowrules
        main.log.debug( onosCli.flows() )
        main.step( "Wait a minute then ping again" )
        # the wait is above
        PingResult = main.TRUE
        for i in range( 8, 18 ):
            ping = main.Mininet1.pingHost( src="h" + str( i ),
                                           target="h" + str( i + 10 ) )
            PingResult = PingResult and ping
            if ping == main.FALSE:
                main.log.warn( "Ping failed between h" + str( i ) +
                               " and h" + str( i + 10 ) )
            elif ping == main.TRUE:
                main.log.info( "Ping test passed!" )
                # Don't set PingResult or you'd override failures
        if PingResult == main.FALSE:
            main.log.error(
                "Intents have not been installed correctly, pings failed." )
            # TODO: pretty print
            main.log.warn( str( onosCli.name ) + " intents: " )
            try:
                tmpIntents = onosCli.intents()
                main.log.warn( json.dumps( json.loads( tmpIntents ),
                                           sort_keys=True,
                                           indent=4,
                                           separators=( ',', ': ' ) ) )
            except ( ValueError, TypeError ):
                main.log.warn( repr( tmpIntents ) )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=PingResult,
            onpass="Intents have been installed correctly and pings work",
            onfail="Intents have not been installed correctly, pings failed." )

    def checkRoleNotNull( self ):
        main.step( "Check that each switch has a master" )
        # Assert that each device has a master
        rolesNotNull = main.Cluster.command( "rolesNotNull", returnBool=True )
        utilities.assert_equals(
            expect=True,
            actual=rolesNotNull,
            onpass="Each device has a master",
            onfail="Some devices don't have a master assigned" )

    def checkTheRole( self ):
        main.step( "Read device roles from ONOS" )
        ONOSMastership = main.Cluster.command( "roles" )
        consistentMastership = True
        rolesResults = True
        for i in range( len( ONOSMastership ) ):
            node = str( main.Cluster.active( i ) )
            if not ONOSMastership[ i ] or "Error" in ONOSMastership[ i ]:
                main.log.error( "Error in getting " + node + " roles" )
                main.log.warn( node + " mastership response: " +
                               repr( ONOSMastership[ i ] ) )
                rolesResults = False
        utilities.assert_equals(
            expect=True,
            actual=rolesResults,
            onpass="No error in reading roles output",
            onfail="Error in reading roles from ONOS" )

        main.step( "Check for consistency in roles from each controller" )
        if all( [ i == ONOSMastership[ 0 ] for i in ONOSMastership ] ):
            main.log.info(
                "Switch roles are consistent across all ONOS nodes" )
        else:
            consistentMastership = False
        utilities.assert_equals(
            expect=True,
            actual=consistentMastership,
            onpass="Switch roles are consistent across all ONOS nodes",
            onfail="ONOS nodes have different views of switch roles" )
        return ONOSMastership, rolesResults, consistentMastership

    def checkingIntents( self ):
        main.step( "Get the intents from each controller" )
        ONOSIntents = main.Cluster.command( "intents", specificDriver=2 )
        intentsResults = True
        for i in range( len( ONOSIntents ) ):
            node = str( main.Cluster.active( i ) )
            if not ONOSIntents[ i ] or "Error" in ONOSIntents[ i ]:
                main.log.error( "Error in getting " + node + " intents" )
                main.log.warn( node + " intents response: " +
                               repr( ONOSIntents[ i ] ) )
                intentsResults = False
        utilities.assert_equals(
            expect=True,
            actual=intentsResults,
            onpass="No error in reading intents output",
            onfail="Error in reading intents from ONOS" )
        return ONOSIntents, intentsResults

    def readingState( self, main ):
        """
        Reading state of ONOS
        """
        import json
        import time
        assert main, "main not defined"
        assert utilities.assert_equals, "utilities.assert_equals not defined"
        try:
            from tests.dependencies.topology import Topology
        except ImportError:
            main.log.error( "Topology not found exiting the test" )
            main.cleanup()
            main.exit()
        try:
            main.topoRelated
        except ( NameError, AttributeError ):
            main.topoRelated = Topology()
        main.case( "Setting up and gathering data for current state" )
        # The general idea for this test case is to pull the state of
        # ( intents,flows, topology,... ) from each ONOS node
        # We can then compare them with each other and also with past states

        global mastershipState
        mastershipState = '[]'

        self.checkRoleNotNull()

        main.step( "Get the Mastership of each switch from each controller" )
        mastershipCheck = main.FALSE

        ONOSMastership, consistentMastership, rolesResults = self.checkTheRole()

        if rolesResults and not consistentMastership:
            for i in range( len( main.Cluster.active() ) ):
                node = str( main.Cluster.active( i ) )
                try:
                    main.log.warn(
                        node + " roles: ",
                        json.dumps(
                            json.loads( ONOSMastership[ i ] ),
                            sort_keys=True,
                            indent=4,
                            separators=( ',', ': ' ) ) )
                except ( ValueError, TypeError ):
                    main.log.warn( repr( ONOSMastership[ i ] ) )
        elif rolesResults and consistentMastership:
            mastershipCheck = main.TRUE
            mastershipState = ONOSMastership[ 0 ]


        global intentState
        intentState = []
        ONOSIntents, intentsResults = self.checkingIntents()
        intentCheck = main.FALSE
        consistentIntents = True


        main.step( "Check for consistency in Intents from each controller" )
        if all( [ sorted( i ) == sorted( ONOSIntents[ 0 ] ) for i in ONOSIntents ] ):
            main.log.info( "Intents are consistent across all ONOS " +
                             "nodes" )
        else:
            consistentIntents = False
            main.log.error( "Intents not consistent" )
        utilities.assert_equals(
            expect=True,
            actual=consistentIntents,
            onpass="Intents are consistent across all ONOS nodes",
            onfail="ONOS nodes have different views of intents" )

        if intentsResults:
            # Try to make it easy to figure out what is happening
            #
            # Intent      ONOS1      ONOS2    ...
            #  0x01     INSTALLED  INSTALLING
            #  ...        ...         ...
            #  ...        ...         ...
            title = "   Id"
            for ctrl in main.Cluster.active():
                title += " " * 10 + ctrl.name
            main.log.warn( title )
            # get all intent keys in the cluster
            keys = []
            try:
                # Get the set of all intent keys
                for nodeStr in ONOSIntents:
                    node = json.loads( nodeStr )
                    for intent in node:
                        keys.append( intent.get( 'id' ) )
                keys = set( keys )
                # For each intent key, print the state on each node
                for key in keys:
                    row = "%-13s" % key
                    for nodeStr in ONOSIntents:
                        node = json.loads( nodeStr )
                        for intent in node:
                            if intent.get( 'id', "Error" ) == key:
                                row += "%-15s" % intent.get( 'state' )
                    main.log.warn( row )
                # End of intent state table
            except ValueError as e:
                main.log.exception( e )
                main.log.debug( "nodeStr was: " + repr( nodeStr ) )

        if intentsResults and not consistentIntents:
            # print the json objects
            main.log.debug( ctrl.name + " intents: " )
            main.log.debug( json.dumps( json.loads( ONOSIntents[ -1 ] ),
                                        sort_keys=True,
                                        indent=4,
                                        separators=( ',', ': ' ) ) )
            for i in range( len( ONOSIntents ) ):
                node = str( main.Cluster.active( i ) )
                if ONOSIntents[ i ] != ONOSIntents[ -1 ]:
                    main.log.debug( node + " intents: " )
                    main.log.debug( json.dumps( json.loads( ONOSIntents[ i ] ),
                                                sort_keys=True,
                                                indent=4,
                                                separators=( ',', ': ' ) ) )
                else:
                    main.log.debug( node + " intents match " + ctrl.name + " intents" )
        elif intentsResults and consistentIntents:
            intentCheck = main.TRUE
            intentState = ONOSIntents[ 0 ]

        main.step( "Get the flows from each controller" )
        global flowState
        flowState = []
        ONOSFlows = main.Cluster.command( "flows", specificDriver=2 ) # TODO: Possible arg: sleep = 30
        ONOSFlowsJson = []
        flowCheck = main.FALSE
        consistentFlows = True
        flowsResults = True
        for i in range( len( ONOSFlows ) ):
            node = str( main.Cluster.active( i ) )
            if not ONOSFlows[ i ] or "Error" in ONOSFlows[ i ]:
                main.log.error( "Error in getting " + node + " flows" )
                main.log.warn( node + " flows response: " +
                               repr( ONOSFlows[ i ] ) )
                flowsResults = False
                ONOSFlowsJson.append( None )
            else:
                try:
                    ONOSFlowsJson.append( json.loads( ONOSFlows[ i ] ) )
                except ( ValueError, TypeError ):
                    # FIXME: change this to log.error?
                    main.log.exception( "Error in parsing " + node +
                                        " response as json." )
                    main.log.error( repr( ONOSFlows[ i ] ) )
                    ONOSFlowsJson.append( None )
                    flowsResults = False
        utilities.assert_equals(
            expect=True,
            actual=flowsResults,
            onpass="No error in reading flows output",
            onfail="Error in reading flows from ONOS" )

        main.step( "Check for consistency in Flows from each controller" )
        tmp = [ len( i ) == len( ONOSFlowsJson[ 0 ] ) for i in ONOSFlowsJson ]
        if all( tmp ):
            main.log.info( "Flow count is consistent across all ONOS nodes" )
        else:
            consistentFlows = False
        utilities.assert_equals(
            expect=True,
            actual=consistentFlows,
            onpass="The flow count is consistent across all ONOS nodes",
            onfail="ONOS nodes have different flow counts" )

        if flowsResults and not consistentFlows:
            for i in range( len( ONOSFlows ) ):
                node = str( main.Cluster.active( i ) )
                try:
                    main.log.warn(
                        node + " flows: " +
                        json.dumps( json.loads( ONOSFlows[ i ] ), sort_keys=True,
                                    indent=4, separators=( ',', ': ' ) ) )
                except ( ValueError, TypeError ):
                    main.log.warn( node + " flows: " +
                                   repr( ONOSFlows[ i ] ) )
        elif flowsResults and consistentFlows:
            flowCheck = main.TRUE
            flowState = ONOSFlows[ 0 ]

        main.step( "Get the OF Table entries" )
        global flows
        flows = []
        for i in range( 1, 29 ):
            flows.append( main.Mininet1.getFlowTable( "s" + str( i ), version="1.3", debug=False ) )
        if flowCheck == main.FALSE:
            for table in flows:
                main.log.warn( table )
        # TODO: Compare switch flow tables with ONOS flow tables

        main.step( "Start continuous pings" )
        main.Mininet2.pingLong(
            src=main.params[ 'PING' ][ 'source1' ],
            target=main.params[ 'PING' ][ 'target1' ],
            pingTime=500 )
        main.Mininet2.pingLong(
            src=main.params[ 'PING' ][ 'source2' ],
            target=main.params[ 'PING' ][ 'target2' ],
            pingTime=500 )
        main.Mininet2.pingLong(
            src=main.params[ 'PING' ][ 'source3' ],
            target=main.params[ 'PING' ][ 'target3' ],
            pingTime=500 )
        main.Mininet2.pingLong(
            src=main.params[ 'PING' ][ 'source4' ],
            target=main.params[ 'PING' ][ 'target4' ],
            pingTime=500 )
        main.Mininet2.pingLong(
            src=main.params[ 'PING' ][ 'source5' ],
            target=main.params[ 'PING' ][ 'target5' ],
            pingTime=500 )
        main.Mininet2.pingLong(
            src=main.params[ 'PING' ][ 'source6' ],
            target=main.params[ 'PING' ][ 'target6' ],
            pingTime=500 )
        main.Mininet2.pingLong(
            src=main.params[ 'PING' ][ 'source7' ],
            target=main.params[ 'PING' ][ 'target7' ],
            pingTime=500 )
        main.Mininet2.pingLong(
            src=main.params[ 'PING' ][ 'source8' ],
            target=main.params[ 'PING' ][ 'target8' ],
            pingTime=500 )
        main.Mininet2.pingLong(
            src=main.params[ 'PING' ][ 'source9' ],
            target=main.params[ 'PING' ][ 'target9' ],
            pingTime=500 )
        main.Mininet2.pingLong(
            src=main.params[ 'PING' ][ 'source10' ],
            target=main.params[ 'PING' ][ 'target10' ],
            pingTime=500 )

        main.step( "Collecting topology information from ONOS" )
        devices = main.topoRelated.getAll( "devices" )
        hosts = main.topoRelated.getAll( "hosts", inJson=True )
        ports = main.topoRelated.getAll( "ports" )
        links = main.topoRelated.getAll( "links" )
        clusters = main.topoRelated.getAll( "clusters" )
        # Compare json objects for hosts and dataplane clusters

        # hosts
        main.step( "Host view is consistent across ONOS nodes" )
        consistentHostsResult = main.TRUE
        for controller in range( len( hosts ) ):
            controllerStr = str( main.Cluster.active( controller ) )
            if hosts[ controller ] and "Error" not in hosts[ controller ]:
                if hosts[ controller ] == hosts[ 0 ]:
                    continue
                else:  # hosts not consistent
                    main.log.error( "hosts from " +
                                     controllerStr +
                                     " is inconsistent with ONOS1" )
                    main.log.warn( repr( hosts[ controller ] ) )
                    consistentHostsResult = main.FALSE

            else:
                main.log.error( "Error in getting ONOS hosts from " +
                                 controllerStr )
                consistentHostsResult = main.FALSE
                main.log.warn( controllerStr +
                               " hosts response: " +
                               repr( hosts[ controller ] ) )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=consistentHostsResult,
            onpass="Hosts view is consistent across all ONOS nodes",
            onfail="ONOS nodes have different views of hosts" )

        main.step( "Each host has an IP address" )
        ipResult = main.TRUE
        for controller in range( 0, len( hosts ) ):
            controllerStr = str( main.Cluster.active( controller ) )
            if hosts[ controller ]:
                for host in hosts[ controller ]:
                    if not host.get( 'ipAddresses', [] ):
                        main.log.error( "Error with host ips on " +
                                        controllerStr + ": " + str( host ) )
                        ipResult = main.FALSE
        utilities.assert_equals(
            expect=main.TRUE,
            actual=ipResult,
            onpass="The ips of the hosts aren't empty",
            onfail="The ip of at least one host is missing" )

        # Strongly connected clusters of devices
        main.step( "Cluster view is consistent across ONOS nodes" )
        consistentClustersResult = main.TRUE
        for controller in range( len( clusters ) ):
            controllerStr = str( main.Cluster.active( controller ) )
            if "Error" not in clusters[ controller ]:
                if clusters[ controller ] == clusters[ 0 ]:
                    continue
                else:  # clusters not consistent
                    main.log.error( "clusters from " + controllerStr +
                                     " is inconsistent with ONOS1" )
                    consistentClustersResult = main.FALSE

            else:
                main.log.error( "Error in getting dataplane clusters " +
                                 "from " + controllerStr )
                consistentClustersResult = main.FALSE
                main.log.warn( controllerStr +
                               " clusters response: " +
                               repr( clusters[ controller ] ) )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=consistentClustersResult,
            onpass="Clusters view is consistent across all ONOS nodes",
            onfail="ONOS nodes have different views of clusters" )
        if not consistentClustersResult:
            main.log.debug( clusters )

        # there should always only be one cluster
        main.step( "Cluster view correct across ONOS nodes" )
        try:
            numClusters = len( json.loads( clusters[ 0 ] ) )
        except ( ValueError, TypeError ):
            main.log.exception( "Error parsing clusters[0]: " +
                                repr( clusters[ 0 ] ) )
            numClusters = "ERROR"
        utilities.assert_equals(
            expect=1,
            actual=numClusters,
            onpass="ONOS shows 1 SCC",
            onfail="ONOS shows " + str( numClusters ) + " SCCs" )

        main.step( "Comparing ONOS topology to MN" )
        devicesResults = main.TRUE
        linksResults = main.TRUE
        hostsResults = main.TRUE
        mnSwitches = main.Mininet1.getSwitches()
        mnLinks = main.Mininet1.getLinks()
        mnHosts = main.Mininet1.getHosts()
        for controller in range( len( main.Cluster.active() ) ):
            controllerStr = str( main.Cluster.active( controller ) )
            currentDevicesResult = main.topoRelated.compareDevicePort(
                                                main.Mininet1, controller,
                                                mnSwitches, devices, ports )
            utilities.assert_equals( expect=main.TRUE,
                                     actual=currentDevicesResult,
                                     onpass=controllerStr +
                                     " Switches view is correct",
                                     onfail=controllerStr +
                                     " Switches view is incorrect" )

            currentLinksResult = main.topoRelated.compareBase( links, controller,
                                                                   main.Mininet1.compareLinks,
                                                                   [ mnSwitches, mnLinks ] )
            utilities.assert_equals( expect=main.TRUE,
                                     actual=currentLinksResult,
                                     onpass=controllerStr +
                                     " links view is correct",
                                     onfail=controllerStr +
                                     " links view is incorrect" )

            if hosts[ controller ] and "Error" not in hosts[ controller ]:
                currentHostsResult = main.Mininet1.compareHosts(
                        mnHosts,
                        hosts[ controller ] )
            else:
                currentHostsResult = main.FALSE
            utilities.assert_equals( expect=main.TRUE,
                                     actual=currentHostsResult,
                                     onpass=controllerStr +
                                     " hosts exist in Mininet",
                                     onfail=controllerStr +
                                     " hosts don't match Mininet" )

            devicesResults = devicesResults and currentDevicesResult
            linksResults = linksResults and currentLinksResult
            hostsResults = hostsResults and currentHostsResult

        main.step( "Device information is correct" )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=devicesResults,
            onpass="Device information is correct",
            onfail="Device information is incorrect" )

        main.step( "Links are correct" )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=linksResults,
            onpass="Link are correct",
            onfail="Links are incorrect" )

        main.step( "Hosts are correct" )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=hostsResults,
            onpass="Hosts are correct",
            onfail="Hosts are incorrect" )

    def checkDistPrimitivesFunc( self, main ):
        """
        Check for basic functionality with distributed primitives
        """
        # TODO: Clean this up so it's not just a cut/paste from the test
        try:
            # Make sure variables are defined/set
            assert utilities.assert_equals, "utilities.assert_equals not defined"
            assert main.pCounterName, "main.pCounterName not defined"
            assert main.onosSetName, "main.onosSetName not defined"
            # NOTE: assert fails if value is 0/None/Empty/False
            try:
                main.pCounterValue
            except ( NameError, AttributeError ):
                main.log.error( "main.pCounterValue not defined, setting to 0" )
                main.pCounterValue = 0
            try:
                main.onosSet
            except ( NameError, AttributeError ):
                main.log.error( "main.onosSet not defined, setting to empty Set" )
                main.onosSet = set( [] )
            # Variables for the distributed primitives tests. These are local only
            addValue = "a"
            addAllValue = "a b c d e f"
            retainValue = "c d e f"
            valueName = "TestON-Value"
            valueValue = None
            workQueueName = "TestON-Queue"
            workQueueCompleted = 0
            workQueueInProgress = 0
            workQueuePending = 0

            description = "Check for basic functionality with distributed " +\
                          "primitives"
            main.case( description )
            main.caseExplanation = "Test the methods of the distributed " +\
                                    "primitives (counters and sets) throught the cli"
            # DISTRIBUTED ATOMIC COUNTERS
            # Partitioned counters
            main.step( "Increment then get a default counter on each node" )
            pCounters = main.Cluster.command( "counterTestAddAndGet",
                                              args=[ main.pCounterName ] )
            addedPValues = []
            for i in main.Cluster.active():
                main.pCounterValue += 1
                addedPValues.append( main.pCounterValue )
            # Check that counter incremented once per controller
            pCounterResults = True
            for i in addedPValues:
                tmpResult = i in pCounters
                pCounterResults = pCounterResults and tmpResult
                if not tmpResult:
                    main.log.error( str( i ) + " is not in partitioned "
                                    "counter incremented results" )
            utilities.assert_equals( expect=True,
                                     actual=pCounterResults,
                                     onpass="Default counter incremented",
                                     onfail="Error incrementing default" +
                                            " counter" )

            main.step( "Get then Increment a default counter on each node" )
            pCounters = main.Cluster.command( "counterTestGetAndAdd",
                                              args=[ main.pCounterName ] )
            addedPValues = []
            for i in main.Cluster.active():
                addedPValues.append( main.pCounterValue )
                main.pCounterValue += 1
            # Check that counter incremented numController times
            pCounterResults = True
            for i in addedPValues:
                tmpResult = i in pCounters
                pCounterResults = pCounterResults and tmpResult
                if not tmpResult:
                    main.log.error( str( i ) + " is not in partitioned "
                                    "counter incremented results" )
            utilities.assert_equals( expect=True,
                                     actual=pCounterResults,
                                     onpass="Default counter incremented",
                                     onfail="Error incrementing default" +
                                            " counter" )

            main.step( "Counters we added have the correct values" )
            incrementCheck = self.counterCheck( main.pCounterName, main.pCounterValue )
            utilities.assert_equals( expect=main.TRUE,
                                     actual=incrementCheck,
                                     onpass="Added counters are correct",
                                     onfail="Added counters are incorrect" )

            main.step( "Add -8 to then get a default counter on each node" )
            pCounters = main.Cluster.command( "counterTestAddAndGet",
                                              args=[ main.pCounterName ],
                                              kwargs={ "delta": -8 } )
            addedPValues = []
            for ctrl in main.Cluster.active():
                main.pCounterValue += -8
                addedPValues.append( main.pCounterValue )
            # Check that counter incremented numController times
            pCounterResults = True
            for i in addedPValues:
                tmpResult = i in pCounters
                pCounterResults = pCounterResults and tmpResult
                if not tmpResult:
                    main.log.error( str( i ) + " is not in partitioned "
                                    "counter incremented results" )
            utilities.assert_equals( expect=True,
                                     actual=pCounterResults,
                                     onpass="Default counter incremented",
                                     onfail="Error incrementing default" +
                                            " counter" )

            main.step( "Add 5 to then get a default counter on each node" )
            pCounters = main.Cluster.command( "counterTestAddAndGet",
                                              args=[ main.pCounterName ],
                                              kwargs={ "delta": 5 } )
            addedPValues = []
            for ctrl in main.Cluster.active():
                main.pCounterValue += 5
                addedPValues.append( main.pCounterValue )

            # Check that counter incremented numController times
            pCounterResults = True
            for i in addedPValues:
                tmpResult = i in pCounters
                pCounterResults = pCounterResults and tmpResult
                if not tmpResult:
                    main.log.error( str( i ) + " is not in partitioned "
                                    "counter incremented results" )
            utilities.assert_equals( expect=True,
                                     actual=pCounterResults,
                                     onpass="Default counter incremented",
                                     onfail="Error incrementing default" +
                                            " counter" )

            main.step( "Get then add 5 to a default counter on each node" )
            pCounters = main.Cluster.command( "counterTestGetAndAdd",
                                              args=[ main.pCounterName ],
                                              kwargs={ "delta": 5 } )
            addedPValues = []
            for ctrl in main.Cluster.active():
                addedPValues.append( main.pCounterValue )
                main.pCounterValue += 5
            # Check that counter incremented numController times
            pCounterResults = True
            for i in addedPValues:
                tmpResult = i in pCounters
                pCounterResults = pCounterResults and tmpResult
                if not tmpResult:
                    main.log.error( str( i ) + " is not in partitioned "
                                    "counter incremented results" )
            utilities.assert_equals( expect=True,
                                     actual=pCounterResults,
                                     onpass="Default counter incremented",
                                     onfail="Error incrementing default" +
                                            " counter" )

            main.step( "Counters we added have the correct values" )
            incrementCheck = self.counterCheck( main.pCounterName, main.pCounterValue )
            utilities.assert_equals( expect=main.TRUE,
                                     actual=incrementCheck,
                                     onpass="Added counters are correct",
                                     onfail="Added counters are incorrect" )

            # DISTRIBUTED SETS
            main.step( "Distributed Set get" )
            size = len( main.onosSet )
            getResponses = main.Cluster.command( "setTestGet",
                                                 args=[ main.onosSetName ] )
            getResults = main.TRUE
            for i in range( len( main.Cluster.active() ) ):
                node = main.Cluster.active( i )
                if isinstance( getResponses[ i ], list ):
                    current = set( getResponses[ i ] )
                    if len( current ) == len( getResponses[ i ] ):
                        # no repeats
                        if main.onosSet != current:
                            main.log.error( node +
                                            " has incorrect view" +
                                            " of set " + main.onosSetName + ":\n" +
                                            str( getResponses[ i ] ) )
                            main.log.debug( "Expected: " + str( main.onosSet ) )
                            main.log.debug( "Actual: " + str( current ) )
                            getResults = main.FALSE
                    else:
                        # error, set is not a set
                        main.log.error( node +
                                        " has repeat elements in" +
                                        " set " + main.onosSetName + ":\n" +
                                        str( getResponses[ i ] ) )
                        getResults = main.FALSE
                elif getResponses[ i ] == main.ERROR:
                    getResults = main.FALSE
            utilities.assert_equals( expect=main.TRUE,
                                     actual=getResults,
                                     onpass="Set elements are correct",
                                     onfail="Set elements are incorrect" )

            main.step( "Distributed Set size" )
            sizeResponses = main.Cluster.command( "setTestSize",
                                                  args=[ main.onosSetName ] )
            sizeResults = main.TRUE
            for i in range( len( main.Cluster.active() ) ):
                node = main.Cluster.active( i )
                if size != sizeResponses[ i ]:
                    sizeResults = main.FALSE
                    main.log.error( node +
                                    " expected a size of " + str( size ) +
                                    " for set " + main.onosSetName +
                                    " but got " + str( sizeResponses[ i ] ) )
            utilities.assert_equals( expect=main.TRUE,
                                     actual=sizeResults,
                                     onpass="Set sizes are correct",
                                     onfail="Set sizes are incorrect" )

            main.step( "Distributed Set add()" )
            main.onosSet.add( addValue )
            addResponses = main.Cluster.command( "setTestAdd",
                                                 args=[ main.onosSetName, addValue ] )
            # main.TRUE = successfully changed the set
            # main.FALSE = action resulted in no change in set
            # main.ERROR - Some error in executing the function
            addResults = main.TRUE
            for i in range( len( main.Cluster.active() ) ):
                if addResponses[ i ] == main.TRUE:
                    # All is well
                    pass
                elif addResponses[ i ] == main.FALSE:
                    # Already in set, probably fine
                    pass
                elif addResponses[ i ] == main.ERROR:
                    # Error in execution
                    addResults = main.FALSE
                else:
                    # unexpected result
                    addResults = main.FALSE
            if addResults != main.TRUE:
                main.log.error( "Error executing set add" )

            # Check if set is still correct
            size = len( main.onosSet )
            getResponses = main.Cluster.command( "setTestGet",
                                                 args=[ main.onosSetName ] )
            getResults = main.TRUE
            for i in range( len( main.Cluster.active() ) ):
                node = main.Cluster.active( i )
                if isinstance( getResponses[ i ], list ):
                    current = set( getResponses[ i ] )
                    if len( current ) == len( getResponses[ i ] ):
                        # no repeats
                        if main.onosSet != current:
                            main.log.error( node + " has incorrect view" +
                                            " of set " + main.onosSetName + ":\n" +
                                            str( getResponses[ i ] ) )
                            main.log.debug( "Expected: " + str( main.onosSet ) )
                            main.log.debug( "Actual: " + str( current ) )
                            getResults = main.FALSE
                    else:
                        # error, set is not a set
                        main.log.error( node + " has repeat elements in" +
                                        " set " + main.onosSetName + ":\n" +
                                        str( getResponses[ i ] ) )
                        getResults = main.FALSE
                elif getResponses[ i ] == main.ERROR:
                    getResults = main.FALSE
            sizeResponses = main.Cluster.command( "setTestSize",
                                                  args=[ main.onosSetName ] )
            sizeResults = main.TRUE
            for i in range( len( main.Cluster.active() ) ):
                node = main.Cluster.active( i )
                if size != sizeResponses[ i ]:
                    sizeResults = main.FALSE
                    main.log.error( node + " expected a size of " +
                                    str( size ) + " for set " + main.onosSetName +
                                    " but got " + str( sizeResponses[ i ] ) )
            addResults = addResults and getResults and sizeResults
            utilities.assert_equals( expect=main.TRUE,
                                     actual=addResults,
                                     onpass="Set add correct",
                                     onfail="Set add was incorrect" )

            main.step( "Distributed Set addAll()" )
            main.onosSet.update( addAllValue.split() )
            addResponses = main.Cluster.command( "setTestAdd",
                                                 args=[ main.onosSetName, addAllValue ] )
            # main.TRUE = successfully changed the set
            # main.FALSE = action resulted in no change in set
            # main.ERROR - Some error in executing the function
            addAllResults = main.TRUE
            for i in range( len( main.Cluster.active() ) ):
                if addResponses[ i ] == main.TRUE:
                    # All is well
                    pass
                elif addResponses[ i ] == main.FALSE:
                    # Already in set, probably fine
                    pass
                elif addResponses[ i ] == main.ERROR:
                    # Error in execution
                    addAllResults = main.FALSE
                else:
                    # unexpected result
                    addAllResults = main.FALSE
            if addAllResults != main.TRUE:
                main.log.error( "Error executing set addAll" )

            # Check if set is still correct
            size = len( main.onosSet )
            getResponses = main.Cluster.command( "setTestGet",
                                                 args=[ main.onosSetName ] )
            getResults = main.TRUE
            for i in range( len( main.Cluster.active() ) ):
                node = main.Cluster.active( i )
                if isinstance( getResponses[ i ], list ):
                    current = set( getResponses[ i ] )
                    if len( current ) == len( getResponses[ i ] ):
                        # no repeats
                        if main.onosSet != current:
                            main.log.error( node + " has incorrect view" +
                                            " of set " + main.onosSetName + ":\n" +
                                            str( getResponses[ i ] ) )
                            main.log.debug( "Expected: " + str( main.onosSet ) )
                            main.log.debug( "Actual: " + str( current ) )
                            getResults = main.FALSE
                    else:
                        # error, set is not a set
                        main.log.error( node + " has repeat elements in" +
                                        " set " + main.onosSetName + ":\n" +
                                        str( getResponses[ i ] ) )
                        getResults = main.FALSE
                elif getResponses[ i ] == main.ERROR:
                    getResults = main.FALSE
            sizeResponses = main.Cluster.command( "setTestSize",
                                                  args=[ main.onosSetName ] )
            sizeResults = main.TRUE
            for i in range( len( main.Cluster.active() ) ):
                node = main.Cluster.active( i )
                if size != sizeResponses[ i ]:
                    sizeResults = main.FALSE
                    main.log.error( node + " expected a size of " + str( size ) +
                                    " for set " + main.onosSetName +
                                    " but got " + str( sizeResponses[ i ] ) )
            addAllResults = addAllResults and getResults and sizeResults
            utilities.assert_equals( expect=main.TRUE,
                                     actual=addAllResults,
                                     onpass="Set addAll correct",
                                     onfail="Set addAll was incorrect" )

            main.step( "Distributed Set contains()" )
            containsResponses = main.Cluster.command( "setTestGet",
                                                      args=[ main.onosSetName ],
                                                      kwargs={ "values": addValue } )
            containsResults = main.TRUE
            for i in range( len( main.Cluster.active() ) ):
                if containsResponses[ i ] == main.ERROR:
                    containsResults = main.FALSE
                else:
                    containsResults = containsResults and\
                                      containsResponses[ i ][ 1 ]
            utilities.assert_equals( expect=main.TRUE,
                                     actual=containsResults,
                                     onpass="Set contains is functional",
                                     onfail="Set contains failed" )

            main.step( "Distributed Set containsAll()" )
            containsAllResponses = main.Cluster.command( "setTestGet",
                                                         args=[ main.onosSetName ],
                                                         kwargs={ "values": addAllValue } )
            containsAllResults = main.TRUE
            for i in range( len( main.Cluster.active() ) ):
                if containsResponses[ i ] == main.ERROR:
                    containsResults = main.FALSE
                else:
                    containsResults = containsResults and\
                                      containsResponses[ i ][ 1 ]
            utilities.assert_equals( expect=main.TRUE,
                                     actual=containsAllResults,
                                     onpass="Set containsAll is functional",
                                     onfail="Set containsAll failed" )

            main.step( "Distributed Set remove()" )
            main.onosSet.remove( addValue )
            removeResponses = main.Cluster.command( "setTestRemove",
                                                    args=[ main.onosSetName, addValue ] )
            # main.TRUE = successfully changed the set
            # main.FALSE = action resulted in no change in set
            # main.ERROR - Some error in executing the function
            removeResults = main.TRUE
            for i in range( len( main.Cluster.active() ) ):
                if removeResponses[ i ] == main.TRUE:
                    # All is well
                    pass
                elif removeResponses[ i ] == main.FALSE:
                    # not in set, probably fine
                    pass
                elif removeResponses[ i ] == main.ERROR:
                    # Error in execution
                    removeResults = main.FALSE
                else:
                    # unexpected result
                    removeResults = main.FALSE
            if removeResults != main.TRUE:
                main.log.error( "Error executing set remove" )

            # Check if set is still correct
            size = len( main.onosSet )
            getResponses = main.Cluster.command( "setTestGet",
                                                 args=[ main.onosSetName ] )
            getResults = main.TRUE
            for i in range( len( main.Cluster.active() ) ):
                node = main.Cluster.active( i )
                if isinstance( getResponses[ i ], list ):
                    current = set( getResponses[ i ] )
                    if len( current ) == len( getResponses[ i ] ):
                        # no repeats
                        if main.onosSet != current:
                            main.log.error( node + " has incorrect view" +
                                            " of set " + main.onosSetName + ":\n" +
                                            str( getResponses[ i ] ) )
                            main.log.debug( "Expected: " + str( main.onosSet ) )
                            main.log.debug( "Actual: " + str( current ) )
                            getResults = main.FALSE
                    else:
                        # error, set is not a set
                        main.log.error( node + " has repeat elements in" +
                                        " set " + main.onosSetName + ":\n" +
                                        str( getResponses[ i ] ) )
                        getResults = main.FALSE
                elif getResponses[ i ] == main.ERROR:
                    getResults = main.FALSE
            sizeResponses = main.Cluster.command( "setTestSize",
                                                  args=[ main.onosSetName ] )
            sizeResults = main.TRUE
            for i in range( len( main.Cluster.active() ) ):
                node = main.Cluster.active( i )
                if size != sizeResponses[ i ]:
                    sizeResults = main.FALSE
                    main.log.error( node + " expected a size of " + str( size ) +
                                    " for set " + main.onosSetName +
                                    " but got " + str( sizeResponses[ i ] ) )
            removeResults = removeResults and getResults and sizeResults
            utilities.assert_equals( expect=main.TRUE,
                                     actual=removeResults,
                                     onpass="Set remove correct",
                                     onfail="Set remove was incorrect" )

            main.step( "Distributed Set removeAll()" )
            main.onosSet.difference_update( addAllValue.split() )
            removeAllResponses = main.Cluster.command( "setTestRemove",
                                                       args=[ main.onosSetName, addAllValue ] )
            # main.TRUE = successfully changed the set
            # main.FALSE = action resulted in no change in set
            # main.ERROR - Some error in executing the function
            removeAllResults = main.TRUE
            for i in range( len( main.Cluster.active() ) ):
                if removeAllResponses[ i ] == main.TRUE:
                    # All is well
                    pass
                elif removeAllResponses[ i ] == main.FALSE:
                    # not in set, probably fine
                    pass
                elif removeAllResponses[ i ] == main.ERROR:
                    # Error in execution
                    removeAllResults = main.FALSE
                else:
                    # unexpected result
                    removeAllResults = main.FALSE
            if removeAllResults != main.TRUE:
                main.log.error( "Error executing set removeAll" )

            # Check if set is still correct
            size = len( main.onosSet )
            getResponses = main.Cluster.command( "setTestGet",
                                                 args=[ main.onosSetName ] )
            getResults = main.TRUE
            for i in range( len( main.Cluster.active() ) ):
                node = main.Cluster.active( i )
                if isinstance( getResponses[ i ], list ):
                    current = set( getResponses[ i ] )
                    if len( current ) == len( getResponses[ i ] ):
                        # no repeats
                        if main.onosSet != current:
                            main.log.error( node + " has incorrect view" +
                                            " of set " + main.onosSetName + ":\n" +
                                            str( getResponses[ i ] ) )
                            main.log.debug( "Expected: " + str( main.onosSet ) )
                            main.log.debug( "Actual: " + str( current ) )
                            getResults = main.FALSE
                    else:
                        # error, set is not a set
                        main.log.error( node + " has repeat elements in" +
                                        " set " + main.onosSetName + ":\n" +
                                        str( getResponses[ i ] ) )
                        getResults = main.FALSE
                elif getResponses[ i ] == main.ERROR:
                    getResults = main.FALSE
            sizeResponses = main.Cluster.command( "setTestSize",
                                                  args=[ main.onosSetName ] )
            sizeResults = main.TRUE
            for i in range( len( main.Cluster.active() ) ):
                node = main.Cluster.active( i )
                if size != sizeResponses[ i ]:
                    sizeResults = main.FALSE
                    main.log.error( node + " expected a size of " + str( size ) +
                                    " for set " + main.onosSetName +
                                    " but got " + str( sizeResponses[ i ] ) )
            removeAllResults = removeAllResults and getResults and sizeResults
            utilities.assert_equals( expect=main.TRUE,
                                     actual=removeAllResults,
                                     onpass="Set removeAll correct",
                                     onfail="Set removeAll was incorrect" )

            main.step( "Distributed Set addAll()" )
            main.onosSet.update( addAllValue.split() )
            addResponses = main.Cluster.command( "setTestAdd",
                                                 args=[ main.onosSetName, addAllValue ] )
            # main.TRUE = successfully changed the set
            # main.FALSE = action resulted in no change in set
            # main.ERROR - Some error in executing the function
            addAllResults = main.TRUE
            for i in range( len( main.Cluster.active() ) ):
                if addResponses[ i ] == main.TRUE:
                    # All is well
                    pass
                elif addResponses[ i ] == main.FALSE:
                    # Already in set, probably fine
                    pass
                elif addResponses[ i ] == main.ERROR:
                    # Error in execution
                    addAllResults = main.FALSE
                else:
                    # unexpected result
                    addAllResults = main.FALSE
            if addAllResults != main.TRUE:
                main.log.error( "Error executing set addAll" )

            # Check if set is still correct
            size = len( main.onosSet )
            getResponses = main.Cluster.command( "setTestGet",
                                                 args=[ main.onosSetName ] )
            getResults = main.TRUE
            for i in range( len( main.Cluster.active() ) ):
                node = main.Cluster.active( i )
                if isinstance( getResponses[ i ], list ):
                    current = set( getResponses[ i ] )
                    if len( current ) == len( getResponses[ i ] ):
                        # no repeats
                        if main.onosSet != current:
                            main.log.error( node + " has incorrect view" +
                                            " of set " + main.onosSetName + ":\n" +
                                            str( getResponses[ i ] ) )
                            main.log.debug( "Expected: " + str( main.onosSet ) )
                            main.log.debug( "Actual: " + str( current ) )
                            getResults = main.FALSE
                    else:
                        # error, set is not a set
                        main.log.error( node + " has repeat elements in" +
                                        " set " + main.onosSetName + ":\n" +
                                        str( getResponses[ i ] ) )
                        getResults = main.FALSE
                elif getResponses[ i ] == main.ERROR:
                    getResults = main.FALSE
            sizeResponses = main.Cluster.command( "setTestSize",
                                                  args=[ main.onosSetName ] )
            sizeResults = main.TRUE
            for i in range( len( main.Cluster.active() ) ):
                node = main.Cluster.active( i )
                if size != sizeResponses[ i ]:
                    sizeResults = main.FALSE
                    main.log.error( node + " expected a size of " + str( size ) +
                                    " for set " + main.onosSetName +
                                    " but got " + str( sizeResponses[ i ] ) )
            addAllResults = addAllResults and getResults and sizeResults
            utilities.assert_equals( expect=main.TRUE,
                                     actual=addAllResults,
                                     onpass="Set addAll correct",
                                     onfail="Set addAll was incorrect" )

            main.step( "Distributed Set clear()" )
            main.onosSet.clear()
            clearResponses = main.Cluster.command( "setTestRemove",
                    args=[ main.onosSetName, " " ],  # Values doesn't matter
                    kwargs={ "clear": True } )
            # main.TRUE = successfully changed the set
            # main.FALSE = action resulted in no change in set
            # main.ERROR - Some error in executing the function
            clearResults = main.TRUE
            for i in range( len( main.Cluster.active() ) ):
                if clearResponses[ i ] == main.TRUE:
                    # All is well
                    pass
                elif clearResponses[ i ] == main.FALSE:
                    # Nothing set, probably fine
                    pass
                elif clearResponses[ i ] == main.ERROR:
                    # Error in execution
                    clearResults = main.FALSE
                else:
                    # unexpected result
                    clearResults = main.FALSE
            if clearResults != main.TRUE:
                main.log.error( "Error executing set clear" )

            # Check if set is still correct
            size = len( main.onosSet )
            getResponses = main.Cluster.command( "setTestGet",
                                                 args=[ main.onosSetName ] )
            getResults = main.TRUE
            for i in range( len( main.Cluster.active() ) ):
                node = main.Cluster.active( i )
                if isinstance( getResponses[ i ], list ):
                    current = set( getResponses[ i ] )
                    if len( current ) == len( getResponses[ i ] ):
                        # no repeats
                        if main.onosSet != current:
                            main.log.error( node + " has incorrect view" +
                                            " of set " + main.onosSetName + ":\n" +
                                            str( getResponses[ i ] ) )
                            main.log.debug( "Expected: " + str( main.onosSet ) )
                            main.log.debug( "Actual: " + str( current ) )
                            getResults = main.FALSE
                    else:
                        # error, set is not a set
                        main.log.error( node + " has repeat elements in" +
                                        " set " + main.onosSetName + ":\n" +
                                        str( getResponses[ i ] ) )
                        getResults = main.FALSE
                elif getResponses[ i ] == main.ERROR:
                    getResults = main.FALSE
            sizeResponses = main.Cluster.command( "setTestSize",
                                                  args=[ main.onosSetName ] )
            sizeResults = main.TRUE
            for i in range( len( main.Cluster.active() ) ):
                node = main.Cluster.active( i )
                if size != sizeResponses[ i ]:
                    sizeResults = main.FALSE
                    main.log.error( node + " expected a size of " + str( size ) +
                                    " for set " + main.onosSetName +
                                    " but got " + str( sizeResponses[ i ] ) )
            clearResults = clearResults and getResults and sizeResults
            utilities.assert_equals( expect=main.TRUE,
                                     actual=clearResults,
                                     onpass="Set clear correct",
                                     onfail="Set clear was incorrect" )

            main.step( "Distributed Set addAll()" )
            main.onosSet.update( addAllValue.split() )
            addResponses = main.Cluster.command( "setTestAdd",
                                                 args=[ main.onosSetName, addAllValue ] )
            # main.TRUE = successfully changed the set
            # main.FALSE = action resulted in no change in set
            # main.ERROR - Some error in executing the function
            addAllResults = main.TRUE
            for i in range( len( main.Cluster.active() ) ):
                if addResponses[ i ] == main.TRUE:
                    # All is well
                    pass
                elif addResponses[ i ] == main.FALSE:
                    # Already in set, probably fine
                    pass
                elif addResponses[ i ] == main.ERROR:
                    # Error in execution
                    addAllResults = main.FALSE
                else:
                    # unexpected result
                    addAllResults = main.FALSE
            if addAllResults != main.TRUE:
                main.log.error( "Error executing set addAll" )

            # Check if set is still correct
            size = len( main.onosSet )
            getResponses = main.Cluster.command( "setTestGet",
                                                 args=[ main.onosSetName ] )
            getResults = main.TRUE
            for i in range( len( main.Cluster.active() ) ):
                node = main.Cluster.active( i )
                if isinstance( getResponses[ i ], list ):
                    current = set( getResponses[ i ] )
                    if len( current ) == len( getResponses[ i ] ):
                        # no repeats
                        if main.onosSet != current:
                            main.log.error( node + " has incorrect view" +
                                            " of set " + main.onosSetName + ":\n" +
                                            str( getResponses[ i ] ) )
                            main.log.debug( "Expected: " + str( main.onosSet ) )
                            main.log.debug( "Actual: " + str( current ) )
                            getResults = main.FALSE
                    else:
                        # error, set is not a set
                        main.log.error( node + " has repeat elements in" +
                                        " set " + main.onosSetName + ":\n" +
                                        str( getResponses[ i ] ) )
                        getResults = main.FALSE
                elif getResponses[ i ] == main.ERROR:
                    getResults = main.FALSE
            sizeResponses = main.Cluster.command( "setTestSize",
                                                  args=[ main.onosSetName ] )
            sizeResults = main.TRUE
            for i in range( len( main.Cluster.active() ) ):
                node = main.Cluster.active( i )
                if size != sizeResponses[ i ]:
                    sizeResults = main.FALSE
                    main.log.error( node + " expected a size of " + str( size ) +
                                    " for set " + main.onosSetName +
                                    " but got " + str( sizeResponses[ i ] ) )
            addAllResults = addAllResults and getResults and sizeResults
            utilities.assert_equals( expect=main.TRUE,
                                     actual=addAllResults,
                                     onpass="Set addAll correct",
                                     onfail="Set addAll was incorrect" )

            main.step( "Distributed Set retain()" )
            main.onosSet.intersection_update( retainValue.split() )
            retainResponses = main.Cluster.command( "setTestRemove",
                                                    args=[ main.onosSetName, retainValue ],
                                                    kwargs={ "retain": True } )
            # main.TRUE = successfully changed the set
            # main.FALSE = action resulted in no change in set
            # main.ERROR - Some error in executing the function
            retainResults = main.TRUE
            for i in range( len( main.Cluster.active() ) ):
                if retainResponses[ i ] == main.TRUE:
                    # All is well
                    pass
                elif retainResponses[ i ] == main.FALSE:
                    # Already in set, probably fine
                    pass
                elif retainResponses[ i ] == main.ERROR:
                    # Error in execution
                    retainResults = main.FALSE
                else:
                    # unexpected result
                    retainResults = main.FALSE
            if retainResults != main.TRUE:
                main.log.error( "Error executing set retain" )

            # Check if set is still correct
            size = len( main.onosSet )
            getResponses = main.Cluster.command( "setTestGet",
                                                 args=[ main.onosSetName ] )
            getResults = main.TRUE
            for i in range( len( main.Cluster.active() ) ):
                node = main.Cluster.active( i )
                if isinstance( getResponses[ i ], list ):
                    current = set( getResponses[ i ] )
                    if len( current ) == len( getResponses[ i ] ):
                        # no repeats
                        if main.onosSet != current:
                            main.log.error( node + " has incorrect view" +
                                            " of set " + main.onosSetName + ":\n" +
                                            str( getResponses[ i ] ) )
                            main.log.debug( "Expected: " + str( main.onosSet ) )
                            main.log.debug( "Actual: " + str( current ) )
                            getResults = main.FALSE
                    else:
                        # error, set is not a set
                        main.log.error( node + " has repeat elements in" +
                                        " set " + main.onosSetName + ":\n" +
                                        str( getResponses[ i ] ) )
                        getResults = main.FALSE
                elif getResponses[ i ] == main.ERROR:
                    getResults = main.FALSE
            sizeResponses = main.Cluster.command( "setTestSize",
                                                  args=[ main.onosSetName ] )
            sizeResults = main.TRUE
            for i in range( len( main.Cluster.active() ) ):
                node = main.Cluster.active( i )
                if size != sizeResponses[ i ]:
                    sizeResults = main.FALSE
                    main.log.error( node + " expected a size of " +
                                    str( size ) + " for set " + main.onosSetName +
                                    " but got " + str( sizeResponses[ i ] ) )
            retainResults = retainResults and getResults and sizeResults
            utilities.assert_equals( expect=main.TRUE,
                                     actual=retainResults,
                                     onpass="Set retain correct",
                                     onfail="Set retain was incorrect" )

            # Transactional maps
            main.step( "Partitioned Transactional maps put" )
            tMapValue = "Testing"
            numKeys = 100
            putResult = True
            ctrl = main.Cluster.next()
            putResponses = ctrl.transactionalMapPut( numKeys, tMapValue )
            if putResponses and len( putResponses ) == 100:
                for i in putResponses:
                    if putResponses[ i ][ 'value' ] != tMapValue:
                        putResult = False
            else:
                putResult = False
            if not putResult:
                main.log.debug( "Put response values: " + str( putResponses ) )
            utilities.assert_equals( expect=True,
                                     actual=putResult,
                                     onpass="Partitioned Transactional Map put successful",
                                     onfail="Partitioned Transactional Map put values are incorrect" )

            main.step( "Partitioned Transactional maps get" )
            # FIXME: is this sleep needed?
            time.sleep( 5 )

            getCheck = True
            for n in range( 1, numKeys + 1 ):
                getResponses = main.Cluster.command( "transactionalMapGet",
                                                     args=[ "Key" + str( n ) ] )
                valueCheck = True
                for node in getResponses:
                    if node != tMapValue:
                        valueCheck = False
                if not valueCheck:
                    main.log.warn( "Values for key 'Key" + str(n) + "' do not match:" )
                    main.log.warn( getResponses )
                getCheck = getCheck and valueCheck
            utilities.assert_equals( expect=True,
                                     actual=getCheck,
                                     onpass="Partitioned Transactional Map get values were correct",
                                     onfail="Partitioned Transactional Map values incorrect" )

            # DISTRIBUTED ATOMIC VALUE
            main.step( "Get the value of a new value" )
            getValues = main.Cluster.command( "valueTestGet",
                                              args=[ valueName ] )
            main.log.debug( getValues )
            # Check the results
            atomicValueGetResult = True
            expected = valueValue if valueValue is not None else "null"
            main.log.debug( "Checking for value of " + expected )
            for i in getValues:
                if i != expected:
                    atomicValueGetResult = False
            utilities.assert_equals( expect=True,
                                     actual=atomicValueGetResult,
                                     onpass="Atomic Value get successful",
                                     onfail="Error getting atomic Value " +
                                            str( valueValue ) + ", found: " +
                                            str( getValues ) )

            main.step( "Atomic Value set()" )
            valueValue = "foo"
            setValues = main.Cluster.command( "valueTestSet",
                                              args=[ valueName, valueValue ] )
            main.log.debug( setValues )
            # Check the results
            atomicValueSetResults = True
            for i in setValues:
                if i != main.TRUE:
                    atomicValueSetResults = False
            utilities.assert_equals( expect=True,
                                     actual=atomicValueSetResults,
                                     onpass="Atomic Value set successful",
                                     onfail="Error setting atomic Value" +
                                            str( setValues ) )

            main.step( "Get the value after set()" )
            getValues = main.Cluster.command( "valueTestGet",
                                              args=[ valueName ] )
            main.log.debug( getValues )
            # Check the results
            atomicValueGetResult = True
            expected = valueValue if valueValue is not None else "null"
            main.log.debug( "Checking for value of " + expected )
            for i in getValues:
                if i != expected:
                    atomicValueGetResult = False
            utilities.assert_equals( expect=True,
                                     actual=atomicValueGetResult,
                                     onpass="Atomic Value get successful",
                                     onfail="Error getting atomic Value " +
                                            str( valueValue ) + ", found: " +
                                            str( getValues ) )

            main.step( "Atomic Value compareAndSet()" )
            oldValue = valueValue
            valueValue = "bar"
            ctrl = main.Cluster.next()
            CASValue = ctrl.valueTestCompareAndSet( valueName, oldValue, valueValue )
            main.log.debug( CASValue )
            utilities.assert_equals( expect=main.TRUE,
                                     actual=CASValue,
                                     onpass="Atomic Value comapreAndSet successful",
                                     onfail="Error setting atomic Value:" +
                                            str( CASValue ) )

            main.step( "Get the value after compareAndSet()" )
            getValues = main.Cluster.command( "valueTestGet",
                                              args=[ valueName ] )
            main.log.debug( getValues )
            # Check the results
            atomicValueGetResult = True
            expected = valueValue if valueValue is not None else "null"
            main.log.debug( "Checking for value of " + expected )
            for i in getValues:
                if i != expected:
                    atomicValueGetResult = False
            utilities.assert_equals( expect=True,
                                     actual=atomicValueGetResult,
                                     onpass="Atomic Value get successful",
                                     onfail="Error getting atomic Value " +
                                            str( valueValue ) + ", found: " +
                                            str( getValues ) )

            main.step( "Atomic Value getAndSet()" )
            oldValue = valueValue
            valueValue = "baz"
            ctrl = main.Cluster.next()
            GASValue = ctrl.valueTestGetAndSet( valueName, valueValue )
            main.log.debug( GASValue )
            expected = oldValue if oldValue is not None else "null"
            utilities.assert_equals( expect=expected,
                                     actual=GASValue,
                                     onpass="Atomic Value GAS successful",
                                     onfail="Error with GetAndSet atomic Value: expected " +
                                            str( expected ) + ", found: " +
                                            str( GASValue ) )

            main.step( "Get the value after getAndSet()" )
            getValues = main.Cluster.command( "valueTestGet",
                                              args=[ valueName ] )
            main.log.debug( getValues )
            # Check the results
            atomicValueGetResult = True
            expected = valueValue if valueValue is not None else "null"
            main.log.debug( "Checking for value of " + expected )
            for i in getValues:
                if i != expected:
                    atomicValueGetResult = False
            utilities.assert_equals( expect=True,
                                     actual=atomicValueGetResult,
                                     onpass="Atomic Value get successful",
                                     onfail="Error getting atomic Value: expected " +
                                            str( valueValue ) + ", found: " +
                                            str( getValues ) )

            main.step( "Atomic Value destory()" )
            valueValue = None
            ctrl = main.Cluster.next()
            destroyResult = ctrl.valueTestDestroy( valueName )
            main.log.debug( destroyResult )
            # Check the results
            utilities.assert_equals( expect=main.TRUE,
                                     actual=destroyResult,
                                     onpass="Atomic Value destroy successful",
                                     onfail="Error destroying atomic Value" )

            main.step( "Get the value after destroy()" )
            getValues = main.Cluster.command( "valueTestGet",
                                              args=[ valueName ] )
            main.log.debug( getValues )
            # Check the results
            atomicValueGetResult = True
            expected = valueValue if valueValue is not None else "null"
            main.log.debug( "Checking for value of " + expected )
            for i in getValues:
                if i != expected:
                    atomicValueGetResult = False
            utilities.assert_equals( expect=True,
                                     actual=atomicValueGetResult,
                                     onpass="Atomic Value get successful",
                                     onfail="Error getting atomic Value " +
                                            str( valueValue ) + ", found: " +
                                            str( getValues ) )

            # WORK QUEUES
            main.step( "Work Queue add()" )
            ctrl = main.Cluster.next()
            addResult = ctrl.workQueueAdd( workQueueName, 'foo' )
            workQueuePending += 1
            main.log.debug( addResult )
            # Check the results
            utilities.assert_equals( expect=main.TRUE,
                                     actual=addResult,
                                     onpass="Work Queue add successful",
                                     onfail="Error adding to Work Queue" )

            main.step( "Check the work queue stats" )
            statsResults = self.workQueueStatsCheck( workQueueName,
                                                     workQueueCompleted,
                                                     workQueueInProgress,
                                                     workQueuePending )
            utilities.assert_equals( expect=True,
                                     actual=statsResults,
                                     onpass="Work Queue stats correct",
                                     onfail="Work Queue stats incorrect " )

            main.step( "Work Queue addMultiple()" )
            ctrl = main.Cluster.next()
            addMultipleResult = ctrl.workQueueAddMultiple( workQueueName, 'bar', 'baz' )
            workQueuePending += 2
            main.log.debug( addMultipleResult )
            # Check the results
            utilities.assert_equals( expect=main.TRUE,
                                     actual=addMultipleResult,
                                     onpass="Work Queue add multiple successful",
                                     onfail="Error adding multiple items to Work Queue" )

            main.step( "Check the work queue stats" )
            statsResults = self.workQueueStatsCheck( workQueueName,
                                                     workQueueCompleted,
                                                     workQueueInProgress,
                                                     workQueuePending )
            utilities.assert_equals( expect=True,
                                     actual=statsResults,
                                     onpass="Work Queue stats correct",
                                     onfail="Work Queue stats incorrect " )

            main.step( "Work Queue takeAndComplete() 1" )
            ctrl = main.Cluster.next()
            number = 1
            take1Result = ctrl.workQueueTakeAndComplete( workQueueName, number )
            workQueuePending -= number
            workQueueCompleted += number
            main.log.debug( take1Result )
            # Check the results
            utilities.assert_equals( expect=main.TRUE,
                                     actual=take1Result,
                                     onpass="Work Queue takeAndComplete 1 successful",
                                     onfail="Error taking 1 from Work Queue" )

            main.step( "Check the work queue stats" )
            statsResults = self.workQueueStatsCheck( workQueueName,
                                                     workQueueCompleted,
                                                     workQueueInProgress,
                                                     workQueuePending )
            utilities.assert_equals( expect=True,
                                     actual=statsResults,
                                     onpass="Work Queue stats correct",
                                     onfail="Work Queue stats incorrect " )

            main.step( "Work Queue takeAndComplete() 2" )
            ctrl = main.Cluster.next()
            number = 2
            take2Result = ctrl.workQueueTakeAndComplete( workQueueName, number )
            workQueuePending -= number
            workQueueCompleted += number
            main.log.debug( take2Result )
            # Check the results
            utilities.assert_equals( expect=main.TRUE,
                                     actual=take2Result,
                                     onpass="Work Queue takeAndComplete 2 successful",
                                     onfail="Error taking 2 from Work Queue" )

            main.step( "Check the work queue stats" )
            statsResults = self.workQueueStatsCheck( workQueueName,
                                                     workQueueCompleted,
                                                     workQueueInProgress,
                                                     workQueuePending )
            utilities.assert_equals( expect=True,
                                     actual=statsResults,
                                     onpass="Work Queue stats correct",
                                     onfail="Work Queue stats incorrect " )

            main.step( "Work Queue destroy()" )
            valueValue = None
            threads = []
            ctrl = main.Cluster.next()
            destroyResult = ctrl.workQueueDestroy( workQueueName )
            workQueueCompleted = 0
            workQueueInProgress = 0
            workQueuePending = 0
            main.log.debug( destroyResult )
            # Check the results
            utilities.assert_equals( expect=main.TRUE,
                                     actual=destroyResult,
                                     onpass="Work Queue destroy successful",
                                     onfail="Error destroying Work Queue" )

            main.step( "Check the work queue stats" )
            statsResults = self.workQueueStatsCheck( workQueueName,
                                                     workQueueCompleted,
                                                     workQueueInProgress,
                                                     workQueuePending )
            utilities.assert_equals( expect=True,
                                     actual=statsResults,
                                     onpass="Work Queue stats correct",
                                     onfail="Work Queue stats incorrect " )
        except Exception as e:
            main.log.error( "Exception: " + str( e ) )

    def cleanUp( self, main ):
        """
        Clean up
        """
        import os
        import time
        assert main, "main not defined"
        assert utilities.assert_equals, "utilities.assert_equals not defined"

        # printing colors to terminal
        colors = { 'cyan': '\033[96m', 'purple': '\033[95m',
                   'blue': '\033[94m', 'green': '\033[92m',
                   'yellow': '\033[93m', 'red': '\033[91m', 'end': '\033[0m' }
        main.case( "Test Cleanup" )
        main.step( "Killing tcpdumps" )
        main.Mininet2.stopTcpdump()

        testname = main.TEST
        if main.params[ 'BACKUP' ][ 'ENABLED' ] == "True":
            main.step( "Copying MN pcap and ONOS log files to test station" )
            teststationUser = main.params[ 'BACKUP' ][ 'TESTONUSER' ]
            teststationIP = main.params[ 'BACKUP' ][ 'TESTONIP' ]
            # NOTE: MN Pcap file is being saved to logdir.
            #       We scp this file as MN and TestON aren't necessarily the same vm

            # FIXME: To be replaced with a Jenkin's post script
            # TODO: Load these from params
            # NOTE: must end in /
            logFolder = "/opt/onos/log/"
            logFiles = [ "karaf.log", "karaf.log.1" ]
            # NOTE: must end in /
            for f in logFiles:
                for ctrl in main.Cluster.runningNodes:
                    dstName = main.logdir + "/" + ctrl.name + "-" + f
                    main.ONOSbench.secureCopy( ctrl.user_name, ctrl.ipAddress,
                                               logFolder + f, dstName )
            # std*.log's
            # NOTE: must end in /
            logFolder = "/opt/onos/var/"
            logFiles = [ "stderr.log", "stdout.log" ]
            # NOTE: must end in /
            for f in logFiles:
                for ctrl in main.Cluster.runningNodes:
                    dstName = main.logdir + "/" + ctrl.name + "-" + f
                    main.ONOSbench.secureCopy( ctrl.user_name, ctrl.ipAddress,
                                               logFolder + f, dstName )
        else:
            main.log.debug( "skipping saving log files" )

        main.step( "Stopping Mininet" )
        mnResult = main.Mininet1.stopNet()
        utilities.assert_equals( expect=main.TRUE, actual=mnResult,
                                 onpass="Mininet stopped",
                                 onfail="MN cleanup NOT successful" )

        main.step( "Checking ONOS Logs for errors" )
        for ctrl in main.Cluster.runningNodes:
            main.log.debug( "Checking logs for errors on " + ctrl.name + ":" )
            main.log.warn( main.ONOSbench.checkLogs( ctrl.ipAddress ) )

        try:
            timerLog = open( main.logdir + "/Timers.csv", 'w' )
            main.log.debug( ", ".join( main.HAlabels ) + "\n" + ", ".join( main.HAdata ) )
            timerLog.write( ", ".join( main.HAlabels ) + "\n" + ", ".join( main.HAdata ) )
            timerLog.close()
        except NameError as e:
            main.log.exception( e )

    def assignMastership( self, main ):
        """
        Assign mastership to controllers
        """
        import time
        assert main, "main not defined"
        assert utilities.assert_equals, "utilities.assert_equals not defined"

        main.case( "Assigning Controller roles for switches" )
        main.caseExplanation = "Check that ONOS is connected to each " +\
                                "device. Then manually assign" +\
                                " mastership to specific ONOS nodes using" +\
                                " 'device-role'"
        main.step( "Assign mastership of switches to specific controllers" )
        # Manually assign mastership to the controller we want
        roleCall = main.TRUE

        ipList = []
        deviceList = []
        onosCli = main.Cluster.next()
        try:
            # Assign mastership to specific controllers. This assignment was
            # determined for a 7 node cluser, but will work with any sized
            # cluster
            for i in range( 1, 29 ):  # switches 1 through 28
                # set up correct variables:
                if i == 1:
                    c = 0
                    ip = main.Cluster.active( c ).ip_address  # ONOS1
                    deviceId = onosCli.getDevice( "1000" ).get( 'id' )
                elif i == 2:
                    c = 1 % main.Cluster.numCtrls
                    ip = main.Cluster.active( c ).ip_address  # ONOS2
                    deviceId = onosCli.getDevice( "2000" ).get( 'id' )
                elif i == 3:
                    c = 1 % main.Cluster.numCtrls
                    ip = main.Cluster.active( c ).ip_address  # ONOS2
                    deviceId = onosCli.getDevice( "3000" ).get( 'id' )
                elif i == 4:
                    c = 3 % main.Cluster.numCtrls
                    ip = main.Cluster.active( c ).ip_address  # ONOS4
                    deviceId = onosCli.getDevice( "3004" ).get( 'id' )
                elif i == 5:
                    c = 2 % main.Cluster.numCtrls
                    ip = main.Cluster.active( c ).ip_address  # ONOS3
                    deviceId = onosCli.getDevice( "5000" ).get( 'id' )
                elif i == 6:
                    c = 2 % main.Cluster.numCtrls
                    ip = main.Cluster.active( c ).ip_address  # ONOS3
                    deviceId = onosCli.getDevice( "6000" ).get( 'id' )
                elif i == 7:
                    c = 5 % main.Cluster.numCtrls
                    ip = main.Cluster.active( c ).ip_address  # ONOS6
                    deviceId = onosCli.getDevice( "6007" ).get( 'id' )
                elif i >= 8 and i <= 17:
                    c = 4 % main.Cluster.numCtrls
                    ip = main.Cluster.active( c ).ip_address  # ONOS5
                    dpid = '3' + str( i ).zfill( 3 )
                    deviceId = onosCli.getDevice( dpid ).get( 'id' )
                elif i >= 18 and i <= 27:
                    c = 6 % main.Cluster.numCtrls
                    ip = main.Cluster.active( c ).ip_address  # ONOS7
                    dpid = '6' + str( i ).zfill( 3 )
                    deviceId = onosCli.getDevice( dpid ).get( 'id' )
                elif i == 28:
                    c = 0
                    ip = main.Cluster.active( c ).ip_address  # ONOS1
                    deviceId = onosCli.getDevice( "2800" ).get( 'id' )
                else:
                    main.log.error( "You didn't write an else statement for " +
                                    "switch s" + str( i ) )
                    roleCall = main.FALSE
                # Assign switch
                assert deviceId, "No device id for s" + str( i ) + " in ONOS"
                # TODO: make this controller dynamic
                roleCall = roleCall and onosCli.deviceRole( deviceId, ip )
                ipList.append( ip )
                deviceList.append( deviceId )
        except ( AttributeError, AssertionError ):
            main.log.exception( "Something is wrong with ONOS device view" )
            main.log.info( onosCli.devices() )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=roleCall,
            onpass="Re-assigned switch mastership to designated controller",
            onfail="Something wrong with deviceRole calls" )

        main.step( "Check mastership was correctly assigned" )
        roleCheck = main.TRUE
        # NOTE: This is due to the fact that device mastership change is not
        #       atomic and is actually a multi step process
        time.sleep( 5 )
        for i in range( len( ipList ) ):
            ip = ipList[ i ]
            deviceId = deviceList[ i ]
            # Check assignment
            master = onosCli.getRole( deviceId ).get( 'master' )
            if ip in master:
                roleCheck = roleCheck and main.TRUE
            else:
                roleCheck = roleCheck and main.FALSE
                main.log.error( "Error, controller " + ip + " is not" +
                                " master " + "of device " +
                                str( deviceId ) + ". Master is " +
                                repr( master ) + "." )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=roleCheck,
            onpass="Switches were successfully reassigned to designated " +
                   "controller",
            onfail="Switches were not successfully reassigned" )

    def bringUpStoppedNode( self, main ):
        """
        The bring up stopped nodes
        """
        import time
        assert main, "main not defined"
        assert utilities.assert_equals, "utilities.assert_equals not defined"
        assert main.kill, "main.kill not defined"
        main.case( "Restart minority of ONOS nodes" )

        main.step( "Restarting " + str( len( main.kill ) ) + " ONOS nodes" )
        startResults = main.TRUE
        restartTime = time.time()
        for ctrl in main.kill:
            startResults = startResults and\
                           ctrl.onosStart( ctrl.ipAddress )
        utilities.assert_equals( expect=main.TRUE, actual=startResults,
                                 onpass="ONOS nodes started successfully",
                                 onfail="ONOS nodes NOT successfully started" )

        main.step( "Checking if ONOS is up yet" )
        count = 0
        onosIsupResult = main.FALSE
        while onosIsupResult == main.FALSE and count < 10:
            onosIsupResult = main.TRUE
            for ctrl in main.kill:
                onosIsupResult = onosIsupResult and\
                                 ctrl.isup( ctrl.ipAddress )
            count = count + 1
        utilities.assert_equals( expect=main.TRUE, actual=onosIsupResult,
                                 onpass="ONOS restarted successfully",
                                 onfail="ONOS restart NOT successful" )

        main.step( "Restarting ONOS nodes" )
        cliResults = main.TRUE
        for ctrl in main.kill:
            cliResults = cliResults and\
                         ctrl.startOnosCli( ctrl.ipAddress )
            ctrl.active = True
        utilities.assert_equals( expect=main.TRUE, actual=cliResults,
                                 onpass="ONOS node(s) restarted",
                                 onfail="ONOS node(s) did not restart" )

        # Grab the time of restart so we chan check how long the gossip
        # protocol has had time to work
        main.restartTime = time.time() - restartTime
        main.log.debug( "Restart time: " + str( main.restartTime ) )
        # TODO: MAke this configurable. Also, we are breaking the above timer
        main.step( "Checking ONOS nodes" )
        nodeResults = utilities.retry( self.nodesCheck,
                                       False,
                                       args=[ main.Cluster.active() ],
                                       sleep=15,
                                       attempts=5 )

        utilities.assert_equals( expect=True, actual=nodeResults,
                                 onpass="Nodes check successful",
                                 onfail="Nodes check NOT successful" )

        if not nodeResults:
            for ctrl in main.Cluster.active():
                main.log.debug( "{} components not ACTIVE: \n{}".format(
                    ctrl.name,
                    ctrl.CLI.sendline( "scr:list | grep -v ACTIVE" ) ) )
            main.log.error( "Failed to start ONOS, stopping test" )
            main.cleanup()
            main.exit()

        self.commonChecks()

        main.step( "Rerun for election on the node(s) that were killed" )
        runResults = main.TRUE
        for ctrl in main.kill:
            runResults = runResults and\
                         ctrl.electionTestRun()
        utilities.assert_equals( expect=main.TRUE, actual=runResults,
                                 onpass="ONOS nodes reran for election topic",
                                 onfail="Errror rerunning for election" )
    def tempCell( self, cellName, ipList ):
        main.step( "Create cell file" )
        cellAppString = main.params[ 'ENV' ][ 'appString' ]


        main.ONOSbench.createCellFile( main.ONOSbench.ip_address, cellName,
                                       main.Mininet1.ip_address,
                                       cellAppString, ipList , main.ONOScli1.karafUser )
        main.step( "Applying cell variable to environment" )
        cellResult = main.ONOSbench.setCell( cellName )
        verifyResult = main.ONOSbench.verifyCell()


    def checkStateAfterEvent( self, main, afterWhich, compareSwitch=False, isRestart=False ):
        """
        afterWhich :
            0: failure
            1: scaling
        """
        """
        Check state after ONOS failure/scaling
        """
        import json
        assert main, "main not defined"
        assert utilities.assert_equals, "utilities.assert_equals not defined"
        main.case( "Running ONOS Constant State Tests" )

        OnosAfterWhich = [ "failure" , "scaliing" ]

        # Assert that each device has a master
        self.checkRoleNotNull()

        ONOSMastership, rolesResults, consistentMastership = self.checkTheRole()
        mastershipCheck = main.FALSE

        if rolesResults and not consistentMastership:
            for i in range( len( ONOSMastership ) ):
                node = str( main.Cluster.active( i ) )
                main.log.warn( node + " roles: ",
                               json.dumps( json.loads( ONOSMastership[ i ] ),
                                           sort_keys=True,
                                           indent=4,
                                           separators=( ',', ': ' ) ) )

        if compareSwitch:
            description2 = "Compare switch roles from before failure"
            main.step( description2 )
            try:
                currentJson = json.loads( ONOSMastership[ 0 ] )
                oldJson = json.loads( mastershipState )
            except ( ValueError, TypeError ):
                main.log.exception( "Something is wrong with parsing " +
                                    "ONOSMastership[0] or mastershipState" )
                main.log.debug( "ONOSMastership[0]: " + repr( ONOSMastership[ 0 ] ) )
                main.log.debug( "mastershipState" + repr( mastershipState ) )
                main.cleanup()
                main.exit()
            mastershipCheck = main.TRUE
            for i in range( 1, 29 ):
                switchDPID = str(
                    main.Mininet1.getSwitchDPID( switch="s" + str( i ) ) )
                current = [ switch[ 'master' ] for switch in currentJson
                            if switchDPID in switch[ 'id' ] ]
                old = [ switch[ 'master' ] for switch in oldJson
                        if switchDPID in switch[ 'id' ] ]
                if current == old:
                    mastershipCheck = mastershipCheck and main.TRUE
                else:
                    main.log.warn( "Mastership of switch %s changed" % switchDPID )
                    mastershipCheck = main.FALSE
            utilities.assert_equals(
                expect=main.TRUE,
                actual=mastershipCheck,
                onpass="Mastership of Switches was not changed",
                onfail="Mastership of some switches changed" )

        # NOTE: we expect mastership to change on controller failure/scaling down
        ONOSIntents, intentsResults = self.checkingIntents()
        intentCheck = main.FALSE
        consistentIntents = True

        main.step( "Check for consistency in Intents from each controller" )
        if all( [ sorted( i ) == sorted( ONOSIntents[ 0 ] ) for i in ONOSIntents ] ):
            main.log.info( "Intents are consistent across all ONOS " +
                             "nodes" )
        else:
            consistentIntents = False

        # Try to make it easy to figure out what is happening
        #
        # Intent      ONOS1      ONOS2    ...
        #  0x01     INSTALLED  INSTALLING
        #  ...        ...         ...
        #  ...        ...         ...
        title = "   ID"
        for ctrl in main.Cluster.active():
            title += " " * 10 + ctrl.name
        main.log.warn( title )
        # get all intent keys in the cluster
        keys = []
        for nodeStr in ONOSIntents:
            node = json.loads( nodeStr )
            for intent in node:
                keys.append( intent.get( 'id' ) )
        keys = set( keys )
        for key in keys:
            row = "%-13s" % key
            for nodeStr in ONOSIntents:
                node = json.loads( nodeStr )
                for intent in node:
                    if intent.get( 'id' ) == key:
                        row += "%-15s" % intent.get( 'state' )
            main.log.warn( row )
        # End table view

        utilities.assert_equals(
            expect=True,
            actual=consistentIntents,
            onpass="Intents are consistent across all ONOS nodes",
            onfail="ONOS nodes have different views of intents" )
        intentStates = []
        for node in ONOSIntents:  # Iter through ONOS nodes
            nodeStates = []
            # Iter through intents of a node
            try:
                for intent in json.loads( node ):
                    nodeStates.append( intent[ 'state' ] )
            except ( ValueError, TypeError ):
                main.log.exception( "Error in parsing intents" )
                main.log.error( repr( node ) )
            intentStates.append( nodeStates )
            out = [ ( i, nodeStates.count( i ) ) for i in set( nodeStates ) ]
            main.log.info( dict( out ) )

        if intentsResults and not consistentIntents:
            for i in range( len( main.Cluster.active() ) ):
                ctrl = main.Cluster.contoller[ i ]
                main.log.warn( ctrl.name + " intents: " )
                main.log.warn( json.dumps(
                    json.loads( ONOSIntents[ i ] ),
                    sort_keys=True,
                    indent=4,
                    separators=( ',', ': ' ) ) )
        elif intentsResults and consistentIntents:
            intentCheck = main.TRUE

        # NOTE: Store has no durability, so intents are lost across system
        #       restarts
        if not isRestart:
            main.step( "Compare current intents with intents before the " + OnosAfterWhich[ afterWhich ] )
            # NOTE: this requires case 5 to pass for intentState to be set.
            #      maybe we should stop the test if that fails?
            sameIntents = main.FALSE
            try:
                intentState
            except NameError:
                main.log.warn( "No previous intent state was saved" )
            else:
                if intentState and intentState == ONOSIntents[ 0 ]:
                    sameIntents = main.TRUE
                    main.log.info( "Intents are consistent with before " + OnosAfterWhich[ afterWhich ] )
                # TODO: possibly the states have changed? we may need to figure out
                #       what the acceptable states are
                elif len( intentState ) == len( ONOSIntents[ 0 ] ):
                    sameIntents = main.TRUE
                    try:
                        before = json.loads( intentState )
                        after = json.loads( ONOSIntents[ 0 ] )
                        for intent in before:
                            if intent not in after:
                                sameIntents = main.FALSE
                                main.log.debug( "Intent is not currently in ONOS " +
                                                "(at least in the same form):" )
                                main.log.debug( json.dumps( intent ) )
                    except ( ValueError, TypeError ):
                        main.log.exception( "Exception printing intents" )
                        main.log.debug( repr( ONOSIntents[ 0 ] ) )
                        main.log.debug( repr( intentState ) )
                if sameIntents == main.FALSE:
                    try:
                        main.log.debug( "ONOS intents before: " )
                        main.log.debug( json.dumps( json.loads( intentState ),
                                                    sort_keys=True, indent=4,
                                                    separators=( ',', ': ' ) ) )
                        main.log.debug( "Current ONOS intents: " )
                        main.log.debug( json.dumps( json.loads( ONOSIntents[ 0 ] ),
                                                    sort_keys=True, indent=4,
                                                    separators=( ',', ': ' ) ) )
                    except ( ValueError, TypeError ):
                        main.log.exception( "Exception printing intents" )
                        main.log.debug( repr( ONOSIntents[ 0 ] ) )
                        main.log.debug( repr( intentState ) )
                utilities.assert_equals(
                    expect=main.TRUE,
                    actual=sameIntents,
                    onpass="Intents are consistent with before " + OnosAfterWhich[ afterWhich ] ,
                    onfail="The Intents changed during " + OnosAfterWhich[ afterWhich ] )
            intentCheck = intentCheck and sameIntents

            main.step( "Get the OF Table entries and compare to before " +
                       "component " + OnosAfterWhich[ afterWhich ] )
            FlowTables = main.TRUE
            for i in range( 28 ):
                main.log.info( "Checking flow table on s" + str( i + 1 ) )
                tmpFlows = main.Mininet1.getFlowTable( "s" + str( i + 1 ), version="1.3", debug=False )
                curSwitch = main.Mininet1.flowTableComp( flows[ i ], tmpFlows )
                FlowTables = FlowTables and curSwitch
                if curSwitch == main.FALSE:
                    main.log.warn( "Differences in flow table for switch: s{}".format( i + 1 ) )
            utilities.assert_equals(
                expect=main.TRUE,
                actual=FlowTables,
                onpass="No changes were found in the flow tables",
                onfail="Changes were found in the flow tables" )

        main.Mininet2.pingLongKill()
        """
        main.step( "Check the continuous pings to ensure that no packets " +
                   "were dropped during component failure" )
        main.Mininet2.pingKill( main.params[ 'TESTONUSER' ],
                                main.params[ 'TESTONIP' ] )
        LossInPings = main.FALSE
        # NOTE: checkForLoss returns main.FALSE with 0% packet loss
        for i in range( 8, 18 ):
            main.log.info(
                "Checking for a loss in pings along flow from s" +
                str( i ) )
            LossInPings = main.Mininet2.checkForLoss(
                "/tmp/ping.h" +
                str( i ) ) or LossInPings
        if LossInPings == main.TRUE:
            main.log.info( "Loss in ping detected" )
        elif LossInPings == main.ERROR:
            main.log.info( "There are multiple mininet process running" )
        elif LossInPings == main.FALSE:
            main.log.info( "No Loss in the pings" )
            main.log.info( "No loss of dataplane connectivity" )
        utilities.assert_equals(
            expect=main.FALSE,
            actual=LossInPings,
            onpass="No Loss of connectivity",
            onfail="Loss of dataplane connectivity detected" )
        # NOTE: Since intents are not persisted with IntnentStore,
        #       we expect loss in dataplane connectivity
        LossInPings = main.FALSE
        """

    def compareTopo( self, main ):
        """
        Compare topo
        """
        import json
        import time
        assert main, "main not defined"
        assert utilities.assert_equals, "utilities.assert_equals not defined"
        try:
            from tests.dependencies.topology import Topology
        except ImportError:
            main.log.error( "Topology not found exiting the test" )
            main.cleanup()
            main.exit()
        try:
            main.topoRelated
        except ( NameError, AttributeError ):
            main.topoRelated = Topology()
        main.case( "Compare ONOS Topology view to Mininet topology" )
        main.caseExplanation = "Compare topology objects between Mininet" +\
                                " and ONOS"
        topoResult = main.FALSE
        topoFailMsg = "ONOS topology don't match Mininet"
        elapsed = 0
        count = 0
        main.step( "Comparing ONOS topology to MN topology" )
        startTime = time.time()
        # Give time for Gossip to work
        while topoResult == main.FALSE and ( elapsed < 60 or count < 3 ):
            devicesResults = main.TRUE
            linksResults = main.TRUE
            hostsResults = main.TRUE
            hostAttachmentResults = True
            count += 1
            cliStart = time.time()
            devices = main.topoRelated.getAll( "devices", True,
                                                      kwargs={ 'sleep': 5, 'attempts': 5,
                                                               'randomTime': True } )
            ipResult = main.TRUE

            hosts = main.topoRelated.getAll( "hosts", True,
                                                  kwargs={ 'sleep': 5, 'attempts': 5,
                                                           'randomTime': True },
                                                  inJson=True )

            for controller in range( 0, len( hosts ) ):
                controllerStr = str( main.Cluster.active( controller ) )
                if hosts[ controller ]:
                    for host in hosts[ controller ]:
                        if host is None or host.get( 'ipAddresses', [] ) == []:
                            main.log.error(
                                "Error with host ipAddresses on controller" +
                                controllerStr + ": " + str( host ) )
                            ipResult = main.FALSE
            ports = main.topoRelated.getAll( "ports" , True,
                                                  kwargs={ 'sleep': 5, 'attempts': 5,
                                                           'randomTime': True } )
            links = main.topoRelated.getAll( "links", True,
                                                  kwargs={ 'sleep': 5, 'attempts': 5,
                                                           'randomTime': True } )
            clusters = main.topoRelated.getAll( "clusters", True,
                                                        kwargs={ 'sleep': 5, 'attempts': 5,
                                                                 'randomTime': True } )

            elapsed = time.time() - startTime
            cliTime = time.time() - cliStart
            print "Elapsed time: " + str( elapsed )
            print "CLI time: " + str( cliTime )

            if all( e is None for e in devices ) and\
               all( e is None for e in hosts ) and\
               all( e is None for e in ports ) and\
               all( e is None for e in links ) and\
               all( e is None for e in clusters ):
                topoFailMsg = "Could not get topology from ONOS"
                main.log.error( topoFailMsg )
                continue  # Try again, No use trying to compare

            mnSwitches = main.Mininet1.getSwitches()
            mnLinks = main.Mininet1.getLinks()
            mnHosts = main.Mininet1.getHosts()
            for controller in range( len( main.Cluster.active() ) ):
                controllerStr = str( main.Cluster.active( controller ) )
                currentDevicesResult = main.topoRelated.compareDevicePort( main.Mininet1, controller,
                                                          mnSwitches,
                                                          devices, ports )
                utilities.assert_equals( expect=main.TRUE,
                                         actual=currentDevicesResult,
                                         onpass=controllerStr +
                                         " Switches view is correct",
                                         onfail=controllerStr +
                                         " Switches view is incorrect" )


                currentLinksResult = main.topoRelated.compareBase( links, controller,
                                                        main.Mininet1.compareLinks,
                                                        [mnSwitches, mnLinks] )
                utilities.assert_equals( expect=main.TRUE,
                                         actual=currentLinksResult,
                                         onpass=controllerStr +
                                         " links view is correct",
                                         onfail=controllerStr +
                                         " links view is incorrect" )
                if hosts[ controller ] and "Error" not in hosts[ controller ]:
                    currentHostsResult = main.Mininet1.compareHosts(
                            mnHosts,
                            hosts[ controller ] )
                elif hosts[ controller ] == []:
                    currentHostsResult = main.TRUE
                else:
                    currentHostsResult = main.FALSE
                utilities.assert_equals( expect=main.TRUE,
                                         actual=currentHostsResult,
                                         onpass=controllerStr +
                                         " hosts exist in Mininet",
                                         onfail=controllerStr +
                                         " hosts don't match Mininet" )
                # CHECKING HOST ATTACHMENT POINTS
                hostAttachment = True
                zeroHosts = False
                # FIXME: topo-HA/obelisk specific mappings:
                # key is mac and value is dpid
                mappings = {}
                for i in range( 1, 29 ):  # hosts 1 through 28
                    # set up correct variables:
                    macId = "00:" * 5 + hex( i ).split( "0x" )[ 1 ].upper().zfill( 2 )
                    if i == 1:
                        deviceId = "1000".zfill( 16 )
                    elif i == 2:
                        deviceId = "2000".zfill( 16 )
                    elif i == 3:
                        deviceId = "3000".zfill( 16 )
                    elif i == 4:
                        deviceId = "3004".zfill( 16 )
                    elif i == 5:
                        deviceId = "5000".zfill( 16 )
                    elif i == 6:
                        deviceId = "6000".zfill( 16 )
                    elif i == 7:
                        deviceId = "6007".zfill( 16 )
                    elif i >= 8 and i <= 17:
                        dpid = '3' + str( i ).zfill( 3 )
                        deviceId = dpid.zfill( 16 )
                    elif i >= 18 and i <= 27:
                        dpid = '6' + str( i ).zfill( 3 )
                        deviceId = dpid.zfill( 16 )
                    elif i == 28:
                        deviceId = "2800".zfill( 16 )
                    mappings[ macId ] = deviceId
                if hosts[ controller ] is not None and "Error" not in hosts[ controller ]:
                    if hosts[ controller ] == []:
                        main.log.warn( "There are no hosts discovered" )
                        zeroHosts = True
                    else:
                        for host in hosts[ controller ]:
                            mac = None
                            location = None
                            device = None
                            port = None
                            try:
                                mac = host.get( 'mac' )
                                assert mac, "mac field could not be found for this host object"

                                location = host.get( 'locations' )[ 0 ]
                                assert location, "location field could not be found for this host object"

                                # Trim the protocol identifier off deviceId
                                device = str( location.get( 'elementId' ) ).split( ':' )[ 1 ]
                                assert device, "elementId field could not be found for this host location object"

                                port = location.get( 'port' )
                                assert port, "port field could not be found for this host location object"

                                # Now check if this matches where they should be
                                if mac and device and port:
                                    if str( port ) != "1":
                                        main.log.error( "The attachment port is incorrect for " +
                                                        "host " + str( mac ) +
                                                        ". Expected: 1 Actual: " + str( port ) )
                                        hostAttachment = False
                                    if device != mappings[ str( mac ) ]:
                                        main.log.error( "The attachment device is incorrect for " +
                                                        "host " + str( mac ) +
                                                        ". Expected: " + mappings[ str( mac ) ] +
                                                        " Actual: " + device )
                                        hostAttachment = False
                                else:
                                    hostAttachment = False
                            except AssertionError:
                                main.log.exception( "Json object not as expected" )
                                main.log.error( repr( host ) )
                                hostAttachment = False
                else:
                    main.log.error( "No hosts json output or \"Error\"" +
                                    " in output. hosts = " +
                                    repr( hosts[ controller ] ) )
                if zeroHosts is False:
                    # TODO: Find a way to know if there should be hosts in a
                    #       given point of the test
                    hostAttachment = True

                # END CHECKING HOST ATTACHMENT POINTS
                devicesResults = devicesResults and currentDevicesResult
                linksResults = linksResults and currentLinksResult
                hostsResults = hostsResults and currentHostsResult
                hostAttachmentResults = hostAttachmentResults and\
                                        hostAttachment
                topoResult = ( devicesResults and linksResults
                               and hostsResults and ipResult and
                               hostAttachmentResults )
        utilities.assert_equals( expect=True,
                                 actual=topoResult,
                                 onpass="ONOS topology matches Mininet",
                                 onfail=topoFailMsg )
        # End of While loop to pull ONOS state

        # Compare json objects for hosts and dataplane clusters

        # hosts
        main.step( "Hosts view is consistent across all ONOS nodes" )
        consistentHostsResult = main.TRUE
        for controller in range( len( hosts ) ):
            controllerStr = str( main.Cluster.active( controller ) )
            if hosts[ controller ] is not None and "Error" not in hosts[ controller ]:
                if hosts[ controller ] == hosts[ 0 ]:
                    continue
                else:  # hosts not consistent
                    main.log.error( "hosts from " + controllerStr +
                                     " is inconsistent with ONOS1" )
                    main.log.debug( repr( hosts[ controller ] ) )
                    consistentHostsResult = main.FALSE

            else:
                main.log.error( "Error in getting ONOS hosts from " +
                                 controllerStr )
                consistentHostsResult = main.FALSE
                main.log.debug( controllerStr +
                                " hosts response: " +
                                repr( hosts[ controller ] ) )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=consistentHostsResult,
            onpass="Hosts view is consistent across all ONOS nodes",
            onfail="ONOS nodes have different views of hosts" )

        main.step( "Hosts information is correct" )
        hostsResults = hostsResults and ipResult
        utilities.assert_equals(
            expect=main.TRUE,
            actual=hostsResults,
            onpass="Host information is correct",
            onfail="Host information is incorrect" )

        main.step( "Host attachment points to the network" )
        utilities.assert_equals(
            expect=True,
            actual=hostAttachmentResults,
            onpass="Hosts are correctly attached to the network",
            onfail="ONOS did not correctly attach hosts to the network" )

        # Strongly connected clusters of devices
        main.step( "Clusters view is consistent across all ONOS nodes" )
        consistentClustersResult = main.TRUE
        for controller in range( len( clusters ) ):
            controllerStr = str( main.Cluster.active( controller ) )
            if "Error" not in clusters[ controller ]:
                if clusters[ controller ] == clusters[ 0 ]:
                    continue
                else:  # clusters not consistent
                    main.log.error( "clusters from " +
                                     controllerStr +
                                     " is inconsistent with ONOS1" )
                    consistentClustersResult = main.FALSE
            else:
                main.log.error( "Error in getting dataplane clusters " +
                                 "from " + controllerStr )
                consistentClustersResult = main.FALSE
                main.log.debug( controllerStr +
                                " clusters response: " +
                                repr( clusters[ controller ] ) )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=consistentClustersResult,
            onpass="Clusters view is consistent across all ONOS nodes",
            onfail="ONOS nodes have different views of clusters" )
        if not consistentClustersResult:
            main.log.debug( clusters )
            for x in links:
                main.log.debug( "{}: {}".format( len( x ), x ) )

        main.step( "There is only one SCC" )
        # there should always only be one cluster
        try:
            numClusters = len( json.loads( clusters[ 0 ] ) )
        except ( ValueError, TypeError ):
            main.log.exception( "Error parsing clusters[0]: " +
                                repr( clusters[ 0 ] ) )
            numClusters = "ERROR"
        clusterResults = main.FALSE
        if numClusters == 1:
            clusterResults = main.TRUE
        utilities.assert_equals(
            expect=1,
            actual=numClusters,
            onpass="ONOS shows 1 SCC",
            onfail="ONOS shows " + str( numClusters ) + " SCCs" )

        topoResult = ( devicesResults and linksResults
                       and hostsResults and consistentHostsResult
                       and consistentClustersResult and clusterResults
                       and ipResult and hostAttachmentResults )

        topoResult = topoResult and int( count <= 2 )
        note = "note it takes about " + str( int( cliTime ) ) + \
            " seconds for the test to make all the cli calls to fetch " +\
            "the topology from each ONOS instance"
        main.log.info(
            "Very crass estimate for topology discovery/convergence( " +
            str( note ) + " ): " + str( elapsed ) + " seconds, " +
            str( count ) + " tries" )

        main.step( "Device information is correct" )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=devicesResults,
            onpass="Device information is correct",
            onfail="Device information is incorrect" )

        main.step( "Links are correct" )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=linksResults,
            onpass="Link are correct",
            onfail="Links are incorrect" )

        main.step( "Hosts are correct" )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=hostsResults,
            onpass="Hosts are correct",
            onfail="Hosts are incorrect" )

        # FIXME: move this to an ONOS state case
        main.step( "Checking ONOS nodes" )
        nodeResults = utilities.retry( self.nodesCheck,
                                       False,
                                       args=[ main.Cluster.active() ],
                                       attempts=5 )
        utilities.assert_equals( expect=True, actual=nodeResults,
                                 onpass="Nodes check successful",
                                 onfail="Nodes check NOT successful" )
        if not nodeResults:
            for ctrl in main.Cluster.active():
                main.log.debug( "{} components not ACTIVE: \n{}".format(
                    ctrl.name,
                    ctrl.CLI.sendline( "scr:list | grep -v ACTIVE" ) ) )

        if not topoResult:
            main.cleanup()
            main.exit()

    def linkDown( self, main, fromS="s3", toS="s28" ):
        """
        Link fromS-toS down
        """
        import time
        assert main, "main not defined"
        assert utilities.assert_equals, "utilities.assert_equals not defined"
        # NOTE: You should probably run a topology check after this

        linkSleep = float( main.params[ 'timers' ][ 'LinkDiscovery' ] )

        description = "Turn off a link to ensure that Link Discovery " +\
                      "is working properly"
        main.case( description )

        main.step( "Kill Link between " + fromS + " and " + toS )
        LinkDown = main.Mininet1.link( END1=fromS, END2=toS, OPTION="down" )
        main.log.info( "Waiting " + str( linkSleep ) +
                       " seconds for link down to be discovered" )
        time.sleep( linkSleep )
        utilities.assert_equals( expect=main.TRUE, actual=LinkDown,
                                 onpass="Link down successful",
                                 onfail="Failed to bring link down" )
        # TODO do some sort of check here

    def linkUp( self, main, fromS="s3", toS="s28" ):
        """
        Link fromS-toS up
        """
        import time
        assert main, "main not defined"
        assert utilities.assert_equals, "utilities.assert_equals not defined"
        # NOTE: You should probably run a topology check after this

        linkSleep = float( main.params[ 'timers' ][ 'LinkDiscovery' ] )

        description = "Restore a link to ensure that Link Discovery is " + \
                      "working properly"
        main.case( description )

        main.step( "Bring link between " + fromS + " and " + toS +" back up" )
        LinkUp = main.Mininet1.link( END1=fromS, END2=toS, OPTION="up" )
        main.log.info( "Waiting " + str( linkSleep ) +
                       " seconds for link up to be discovered" )
        time.sleep( linkSleep )
        utilities.assert_equals( expect=main.TRUE, actual=LinkUp,
                                 onpass="Link up successful",
                                 onfail="Failed to bring link up" )

    def switchDown( self, main ):
        """
        Switch Down
        """
        # NOTE: You should probably run a topology check after this
        import time
        assert main, "main not defined"
        assert utilities.assert_equals, "utilities.assert_equals not defined"

        switchSleep = float( main.params[ 'timers' ][ 'SwitchDiscovery' ] )

        description = "Killing a switch to ensure it is discovered correctly"
        onosCli = main.Cluster.next()
        main.case( description )
        switch = main.params[ 'kill' ][ 'switch' ]
        switchDPID = main.params[ 'kill' ][ 'dpid' ]

        # TODO: Make this switch parameterizable
        main.step( "Kill " + switch )
        main.log.info( "Deleting " + switch )
        main.Mininet1.delSwitch( switch )
        main.log.info( "Waiting " + str( switchSleep ) +
                       " seconds for switch down to be discovered" )
        time.sleep( switchSleep )
        device = onosCli.getDevice( dpid=switchDPID )
        # Peek at the deleted switch
        main.log.warn( "Bringing down switch " + str( device ) )
        result = main.FALSE
        if device and device[ 'available' ] is False:
            result = main.TRUE
        utilities.assert_equals( expect=main.TRUE, actual=result,
                                 onpass="Kill switch successful",
                                 onfail="Failed to kill switch?" )

    def switchUp( self, main ):
        """
        Switch Up
        """
        # NOTE: You should probably run a topology check after this
        import time
        assert main, "main not defined"
        assert utilities.assert_equals, "utilities.assert_equals not defined"

        switchSleep = float( main.params[ 'timers' ][ 'SwitchDiscovery' ] )
        switch = main.params[ 'kill' ][ 'switch' ]
        switchDPID = main.params[ 'kill' ][ 'dpid' ]
        links = main.params[ 'kill' ][ 'links' ].split()
        onosCli = main.Cluster.next()
        description = "Adding a switch to ensure it is discovered correctly"
        main.case( description )

        main.step( "Add back " + switch )
        main.Mininet1.addSwitch( switch, dpid=switchDPID )
        for peer in links:
            main.Mininet1.addLink( switch, peer )
        ipList = main.Cluster.getIps()
        main.Mininet1.assignSwController( sw=switch, ip=ipList )
        main.log.info( "Waiting " + str( switchSleep ) +
                       " seconds for switch up to be discovered" )
        time.sleep( switchSleep )
        device = onosCli.getDevice( dpid=switchDPID )
        # Peek at the deleted switch
        main.log.debug( "Added device: " + str( device ) )
        result = main.FALSE
        if device and device[ 'available' ]:
            result = main.TRUE
        utilities.assert_equals( expect=main.TRUE, actual=result,
                                 onpass="add switch successful",
                                 onfail="Failed to add switch?" )

    def startElectionApp( self, main ):
        """
        start election app on all onos nodes
        """
        assert main, "main not defined"
        assert utilities.assert_equals, "utilities.assert_equals not defined"

        main.case( "Start Leadership Election app" )
        main.step( "Install leadership election app" )
        onosCli = main.Cluster.next()
        appResult = onosCli.activateApp( "org.onosproject.election" )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=appResult,
            onpass="Election app installed",
            onfail="Something went wrong with installing Leadership election" )

        main.step( "Run for election on each node" )
        onosCli.electionTestRun()
        main.Cluster.command( "electionTestRun" )
        time.sleep( 5 )
        sameResult, leaders = main.HA.consistentLeaderboards( main.Cluster.active() )
        utilities.assert_equals(
            expect=True,
            actual=sameResult,
            onpass="All nodes see the same leaderboards",
            onfail="Inconsistent leaderboards" )

        if sameResult:
            leader = leaders[ 0 ][ 0 ]
            if onosCli.ipAddress in leader:
                correctLeader = True
            else:
                correctLeader = False
            main.step( "First node was elected leader" )
            utilities.assert_equals(
                expect=True,
                actual=correctLeader,
                onpass="Correct leader was elected",
                onfail="Incorrect leader" )
            main.Cluster.testLeader = leader

    def isElectionFunctional( self, main ):
        """
        Check that Leadership Election is still functional
            15.1 Run election on each node
            15.2 Check that each node has the same leaders and candidates
            15.3 Find current leader and withdraw
            15.4 Check that a new node was elected leader
            15.5 Check that that new leader was the candidate of old leader
            15.6 Run for election on old leader
            15.7 Check that oldLeader is a candidate, and leader if only 1 node
            15.8 Make sure that the old leader was added to the candidate list

            old and new variable prefixes refer to data from before vs after
                withdrawl and later before withdrawl vs after re-election
        """
        import time
        assert main, "main not defined"
        assert utilities.assert_equals, "utilities.assert_equals not defined"

        description = "Check that Leadership Election is still functional"
        main.case( description )
        # NOTE: Need to re-run after restarts since being a canidate is not persistant

        oldLeaders = []  # list of lists of each nodes' candidates before
        newLeaders = []  # list of lists of each nodes' candidates after
        oldLeader = ''  # the old leader from oldLeaders, None if not same
        newLeader = ''  # the new leaders fron newLoeaders, None if not same
        oldLeaderCLI = None  # the CLI of the old leader used for re-electing
        expectNoLeader = False  # True when there is only one leader
        if len( main.Cluster.runningNodes ) == 1:
            expectNoLeader = True

        main.step( "Run for election on each node" )
        electionResult = main.Cluster.command( "electionTestRun", returnBool=True )
        utilities.assert_equals(
            expect=True,
            actual=electionResult,
            onpass="All nodes successfully ran for leadership",
            onfail="At least one node failed to run for leadership" )

        if electionResult == main.FALSE:
            main.log.error(
                "Skipping Test Case because Election Test App isn't loaded" )
            main.skipCase()

        main.step( "Check that each node shows the same leader and candidates" )
        failMessage = "Nodes have different leaderboards"
        activeCLIs = main.Cluster.active()
        sameResult, oldLeaders = main.HA.consistentLeaderboards( activeCLIs )
        if sameResult:
            oldLeader = oldLeaders[ 0 ][ 0 ]
            main.log.info( "Old leader: " + oldLeader )
        else:
            oldLeader = None
        utilities.assert_equals(
            expect=True,
            actual=sameResult,
            onpass="Leaderboards are consistent for the election topic",
            onfail=failMessage )

        main.step( "Find current leader and withdraw" )
        withdrawResult = main.TRUE
        # do some sanity checking on leader before using it
        if oldLeader is None:
            main.log.error( "Leadership isn't consistent." )
            withdrawResult = main.FALSE
        # Get the CLI of the oldLeader
        for ctrl in main.Cluster.active():
            if oldLeader == ctrl.ipAddress:
                oldLeaderCLI = ctrl
                break
        else:  # FOR/ELSE statement
            main.log.error( "Leader election, could not find current leader" )
        if oldLeader:
            withdrawResult = oldLeaderCLI.electionTestWithdraw()
        utilities.assert_equals(
            expect=main.TRUE,
            actual=withdrawResult,
            onpass="Node was withdrawn from election",
            onfail="Node was not withdrawn from election" )

        main.step( "Check that a new node was elected leader" )
        failMessage = "Nodes have different leaders"
        # Get new leaders and candidates
        newLeaderResult, newLeaders = self.consistentLeaderboards( activeCLIs )
        newLeader = None
        if newLeaderResult:
            if newLeaders[ 0 ][ 0 ] == 'none':
                main.log.error( "No leader was elected on at least 1 node" )
                if not expectNoLeader:
                    newLeaderResult = False
            newLeader = newLeaders[ 0 ][ 0 ]

        # Check that the new leader is not the older leader, which was withdrawn
        if newLeader == oldLeader:
            newLeaderResult = False
            main.log.error( "All nodes still see old leader: " + str( oldLeader ) +
                            " as the current leader" )
        utilities.assert_equals(
            expect=True,
            actual=newLeaderResult,
            onpass="Leadership election passed",
            onfail="Something went wrong with Leadership election" )

        main.step( "Check that that new leader was the candidate of old leader" )
        # candidates[ 2 ] should become the top candidate after withdrawl
        correctCandidateResult = main.TRUE
        if expectNoLeader:
            if newLeader == 'none':
                main.log.info( "No leader expected. None found. Pass" )
                correctCandidateResult = main.TRUE
            else:
                main.log.info( "Expected no leader, got: " + str( newLeader ) )
                correctCandidateResult = main.FALSE
        elif len( oldLeaders[ 0 ] ) >= 3:
            if newLeader == oldLeaders[ 0 ][ 2 ]:
                # correct leader was elected
                correctCandidateResult = main.TRUE
            else:
                correctCandidateResult = main.FALSE
                main.log.error( "Candidate {} was elected. {} should have had priority.".format(
                                    newLeader, oldLeaders[ 0 ][ 2 ] ) )
        else:
            main.log.warn( "Could not determine who should be the correct leader" )
            main.log.debug( oldLeaders[ 0 ] )
            correctCandidateResult = main.FALSE
        utilities.assert_equals(
            expect=main.TRUE,
            actual=correctCandidateResult,
            onpass="Correct Candidate Elected",
            onfail="Incorrect Candidate Elected" )

        main.step( "Run for election on old leader( just so everyone " +
                   "is in the hat )" )
        if oldLeaderCLI is not None:
            runResult = oldLeaderCLI.electionTestRun()
        else:
            main.log.error( "No old leader to re-elect" )
            runResult = main.FALSE
        utilities.assert_equals(
            expect=main.TRUE,
            actual=runResult,
            onpass="App re-ran for election",
            onfail="App failed to run for election" )

        main.step(
            "Check that oldLeader is a candidate, and leader if only 1 node" )
        # verify leader didn't just change
        # Get new leaders and candidates
        reRunLeaders = []
        time.sleep( 5 )  # Paremterize
        positionResult, reRunLeaders = self.consistentLeaderboards( activeCLIs )

        # Check that the re-elected node is last on the candidate List
        if not reRunLeaders[ 0 ]:
            positionResult = main.FALSE
        elif oldLeader != reRunLeaders[ 0 ][ -1 ]:
            main.log.error( "Old Leader ({}) not in the proper position: {} ".format( str( oldLeader ),
                                                                                      str( reRunLeaders[ 0 ] ) ) )
            positionResult = main.FALSE
        utilities.assert_equals(
            expect=True,
            actual=positionResult,
            onpass="Old leader successfully re-ran for election",
            onfail="Something went wrong with Leadership election after " +
                   "the old leader re-ran for election" )

    def installDistributedPrimitiveApp( self, main ):
        """
        Install Distributed Primitives app
        """
        import time
        assert main, "main not defined"
        assert utilities.assert_equals, "utilities.assert_equals not defined"

        # Variables for the distributed primitives tests
        main.pCounterName = "TestON-Partitions"
        main.pCounterValue = 0
        main.onosSet = set( [] )
        main.onosSetName = "TestON-set"

        description = "Install Primitives app"
        main.case( description )
        main.step( "Install Primitives app" )
        appName = "org.onosproject.distributedprimitives"
        appResults = main.Cluster.next().activateApp( appName )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=appResults,
                                 onpass="Primitives app activated",
                                 onfail="Primitives app not activated" )
        # TODO check on all nodes instead of sleeping
        time.sleep( 5 )  # To allow all nodes to activate
