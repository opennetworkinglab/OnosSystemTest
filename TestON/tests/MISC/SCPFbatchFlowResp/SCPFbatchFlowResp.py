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

class SCPFbatchFlowResp:

    """
    Testing end-to-end ONOS response time from POST of batched flows to when ONOS returns
    response confirmation of all flows ADDED; subsequently testing the response time from when REST DELETE to
    ONOS confirmation of all flows REMOVED.
    """
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
        """
        try:
            from tests.dependencies.ONOSSetup import ONOSSetup
            main.testSetUp = ONOSSetup()
        except ImportError:
            main.log.error( "ONOSSetup not found. exiting the test" )
            main.exit()
        main.testSetUp.envSetupDescription()
        stepResult = main.FALSE
        try:
            # Test variables
            main.testOnDirectory = os.path.dirname( os.getcwd() )
            main.cellName = main.params[ 'CASE1' ][ 'cellName' ]
            main.apps = main.params[ 'CASE1' ][ 'cellApps' ]
            main.maxNodes = int( main.params[ 'GLOBAL' ][ 'maxNodes' ] )
            main.startUpSleep = float( main.params[ 'GLOBAL' ][ 'SLEEP' ][ 'startup' ] )
            main.startMNSleep = float( main.params[ 'GLOBAL' ][ 'SLEEP' ][ 'startMN' ] )
            main.addFlowSleep = float( main.params[ 'GLOBAL' ][ 'SLEEP' ][ 'addFlow' ] )
            main.delFlowSleep = float( main.params[ 'GLOBAL' ][ 'SLEEP' ][ 'delFlow' ] )
            main.chkFlowSleep = float( main.params[ 'GLOBAL' ][ 'SLEEP' ][ 'chkFlow' ] )
            main.skipPackaging = main.params[ 'CASE2' ][ 'skipPackaging' ]
            if main.skipPackaging.lower() == "true":
                main.skipPackaging = True
            else:
                main.skipPackaging = False
            main.cfgSleep = float( main.params[ 'GLOBAL' ][ 'SLEEP' ][ 'cfg' ] )
            main.numSw = int( main.params[ 'GLOBAL' ][ 'numSw' ] )
            main.numThreads = int( main.params[ 'GLOBAL' ][ 'numThreads' ] )
            main.cluster = main.params[ 'GLOBAL' ][ 'cluster' ]

            stepResult = main.testSetUp.envSetup()
        except Exception as e:
            main.testSetUp.envSetupException( e )
        main.testSetUp.evnSetupConclusion( stepResult )
        main.commit = main.commit.split( " " )[ 1 ]


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
        main.testSetUp.ONOSSetUp( main.Mininet1, main.Cluster,
                                  skipPack=main.skipPackaging )

    def CASE10( self, main ):
        """
            Start Mininet
        """
        import time

        main.case( "Enable openflow-base on onos and start Mininet." )

        main.step( "Activate openflow-base App" )
        app = main.params[ 'CASE10' ][ 'app' ]
        stepResult = main.Cluster.active( 0 ).CLI.activateApp( app )
        time.sleep( main.cfgSleep )
        main.log.info( stepResult )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully activate " + app,
                                 onfail="Failed to activate app " + app )

        time.sleep( main.cfgSleep )

        main.step( "Configure AdaptiveFlowSampling " )
        stepResult = main.Cluster.active( 0 ).CLI.setCfg( component=main.params[ 'CASE10' ][ 'cfg' ],
                                           propName="adaptiveFlowSampling ", value=main.params[ 'CASE10' ][ 'adaptiveFlowenabled' ] )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="App Configuration Succeeded! ",
                                 onfail="App Configuration Failed!" )
        time.sleep( main.cfgSleep )

        main.step( "Setup Mininet Linear Topology with " + str( main.numSw ) + " switches" )
        argStr = main.params[ 'CASE10' ][ 'mnArgs' ].format( main.numSw )
        stepResult = main.Mininet1.startNet( args=argStr )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully loaded topology",
                                 onfail="Failed to load topology" )

        time.sleep( main.startMNSleep )

        main.step( "Assign switches to controller" )
        for i in range( 1, main.numSw + 1 ):
            main.Mininet1.assignSwController( "s" + str( i ),
                                              main.Cluster.active( 0 ).ipAddress )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully assigned switch to controller",
                                 onfail="Failed to assign switch to controller" )

        main.deviceIdPrefix = "of:"

        time.sleep( main.startMNSleep )

    def CASE11( self, main ):
        """
            Start Null Provider
        """
        import time

        main.case( "Setup Null Provider for linear Topology" )

        main.step( "Activate Null Provider App" )
        stepResult = main.ONOSbench.onosCli( ONOSIp=main.Cluster.active( 0 ).ipAddress,
                                             cmdstr="app activate org.onosproject.null" )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully activated org.onosproject.null",
                                 onfail="Failed to activate org.onosproject.null" )
        time.sleep( main.cfgSleep )
        cfgs = main.params[ 'CASE11' ][ 'cfg' ]
        main.step( "Setup Null Provider Linear Topology with " + str( main.numSw ) + " devices." )
        r1 = main.ONOSbench.onosCfgSet( main.Cluster.active( 0 ).ipAddress,
                                        cfgs,
                                        "deviceCount " + str( main.numSw ) )
        r2 = main.ONOSbench.onosCfgSet( main.Cluster.active( 0 ).ipAddress,
                                        cfgs,
                                        "topoShape " + main.params[ 'CASE11' ][ 'nullTopo' ] )
        r3 = main.ONOSbench.onosCfgSet( main.Cluster.active( 0 ).ipAddress,
                                        cfgs,
                                        "enabled " + main.params[ 'CASE11' ][ 'nullStart' ] )
        stepResult = r1 & r2 & r3
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="App Configuration Succeeded! ",
                                 onfail="App Configuration Failed!" )
        time.sleep( main.cfgSleep )

        main.log.info( "Check to make sure null providers are configured correctly." )
        main.ONOSbench.handle.sendline( "onos $OC1 summary" )
        stepResult = main.ONOSbench.handle.expect( ":~" )
        main.log.info( "ONOS Summary: " + main.ONOSbench.handle.before )

        main.deviceIdPrefix = "null:"

        time.sleep( main.startMNSleep )

    def CASE1000( self, main ):
        """
            create JSON object with batched flows
        """
        import numpy
        import time
        from pprint import pprint

        main.case( "Create a json object for the batched flows" )

        main.step( "Parse batch creation information" )
        main.batchSize = int( main.params[ 'CASE1000' ][ 'batchSize' ] )
        main.log.info( "Number of flows in a batch is:" + str( main.batchSize ) )

        main.flowJsonBatchList = []
        startSw = 1

        main.step( "Creating a full list of batches" )
        for index in range( 1, int( main.params[ 'CASE1000' ][ 'batches' ] ) + 1 ):
            if startSw <= main.numSw:
                ind = startSw
            else:
                startSw = 1
                ind = startSw

            main.log.info( "Creating batch: " + str( index ) )
            flowJsonBatch = main.Cluster.active( 0 ).REST.createFlowBatch( numSw=main.numSw,
                                                           swIndex=ind,
                                                           batchSize=main.batchSize,
                                                           batchIndex=index,
                                                           deviceIdpreFix=main.deviceIdPrefix,
                                                           ingressPort=2,
                                                           egressPort=3 )
            main.flowJsonBatchList.append( flowJsonBatch )

            startSw += 1
        main.log.info( "Number of items created in the batch list is: " + str( len( main.flowJsonBatchList ) ) )

    def CASE2100( self, main ):
        """
            Posting flow batches using threads
        """
        main.case( "Using REST API /flows/{} to post flow batch - multi-threads" )
        main.step( "Using REST API /flows/{} to post flow batch - multi-threads" )

        from Queue import Queue
        from threading import Thread
        import time
        import json

        main.threadID = 0
        main.addedBatchList = []
        q = Queue()
        tAllAdded = 0
        main.postFailed = False

        def postWorker( id ):
            while True:
                item = q.get()
                #print json.dumps( item )
                status, response = main.Cluster.active( 0 ).REST.sendFlowBatch( batch=item )
                if status == main.TRUE:
                    main.log.info( "Thread {} is working on posting. ".format( id ) )
                    #print json.dumps( response )
                    main.addedBatchList.append( response[ 1 ] )
                else:
                    main.log.error( "Thread {} failed to post.".format( id ) )
                    main.postFailed = True
                q.task_done()

        for i in range( int( main.params[ 'CASE2100' ][ 'numThreads' ] ) ):
            threadID = "ThreadID-" + str( i )
            t = Thread( target=postWorker, name=threadID, args=( threadID, ) )
            t.daemon = True
            t.start()

        tStartPost = time.time()
        for item in main.flowJsonBatchList:
            q.put( item )

        q.join()
        tLastPostEnd = time.time()
        if main.postFailed:
            main.log.error( "Flow batch posting failed, exit test" )
            main.cleanup()
            main.exit()

        main.step( "Check to ensure all flows are in added state." )
        #pprint( main.addedBatchList )
        resp = main.FALSE
        while resp != main.TRUE and ( tAllAdded - tLastPostEnd < int( main.params[ 'CASE2100' ][ 'chkFlowTO' ] ) ):
            if main.params[ 'CASE2100' ][ 'RESTchkFlow' ] == 'main.TRUE':
                resp = main.Cluster.active( 0 ).REST.checkFlowsState()
            else:
                handle = main.Cluster.active( 0 ).CLI.flows( state=" |grep PEND|wc -l", jsonFormat=False )
                main.log.info( "handle returns PENDING flows: " + handle )
                if handle == "0":
                    resp = main.TRUE

            time.sleep( main.chkFlowSleep )
            tAllAdded = time.time()

        if tAllAdded - tLastPostEnd >= int( main.params[ 'CASE2100' ][ 'chkFlowTO' ] ):
            main.log.warn( "ONOS Flows still in pending state after: {} seconds.".format( tAllAdded - tLastPostEnd ) )

        main.numFlows = int( main.params[ 'CASE1000' ][ 'batches' ] ) *\
                                                    int( main.params[ 'CASE1000' ][ 'batchSize' ] )
        main.log.info( "Total number of flows: " + str( main.numFlows ) )
        main.elapsePOST = tLastPostEnd - tStartPost
        main.log.info( "Total POST elapse time: " + str( main.elapsePOST ) )
        main.log.info( "Rate of ADD Controller response: " + str( main.numFlows / ( main.elapsePOST ) ) )

        main.POSTtoCONFRM = tAllAdded - tLastPostEnd
        main.log.info( "Elapse time from end of last REST POST to Flows in ADDED state: " +
                       str( main.POSTtoCONFRM ) )
        main.log.info( "Rate of Confirmed Batch Flow ADD is ( flows/sec ): " +
                       str( main.numFlows / main.POSTtoCONFRM ) )
        main.log.info( "Number of flow Batches in the addedBatchList is: " +
                       str( len( main.addedBatchList ) ) )

    def CASE3100( self, main ):
        """
            DELETE flow batches using threads
        """
        main.case( "Using REST API /flows/{} to delete flow batch - multi-threads" )
        main.step( "Using REST API /flows/{} to delete flow batch - multi-threads" )

        from Queue import Queue
        from threading import Thread
        import time
        import json

        main.threadID = 0
        q = Queue()
        tAllRemoved = 0

        main.log.info( "Number of flow batches at start of remove: " + str( len( main.addedBatchList ) ) )

        def removeWorker( id ):
            while True:
                item = q.get()
                response = main.Cluster.active( 0 ).REST.removeFlowBatch( batch=json.loads( item ) )
                main.log.info( "Thread {} is working on deleting. ".format( id ) )
                q.task_done()

        for i in range( int( main.params[ 'CASE2100' ][ 'numThreads' ] ) ):
            threadID = "ThreadID-" + str( i )
            t = Thread( target=removeWorker, name=threadID, args=( threadID, ) )
            t.daemon = True
            t.start()

        tStartDelete = time.time()
        for item in main.addedBatchList:
            q.put( item )

        q.join()
        tLastDeleteEnd = time.time()
        main.log.info( "Number of flow batches at end of remove: " + str( len( main.addedBatchList ) ) )

        main.step( "Check to ensure all flows are in added state." )
        #pprint( main.addedBatchList )
        resp = main.FALSE
        while resp != main.TRUE and ( tAllRemoved - tLastDeleteEnd < int( main.params[ 'CASE3100' ][ 'chkFlowTO' ] ) ):
            if main.params[ 'CASE3100' ][ 'RESTchkFlow' ] == 'main.TRUE':
                resp = main.Cluster.active( 0 ).REST.checkFlowsState()
            else:
                handle = main.Cluster.active( 0 ).CLI.flows( state=" |grep PEND|wc -l", jsonFormat=False )
                main.log.info( "handle returns PENDING flows: " + handle )
                if handle == "0":
                    resp = main.TRUE
            time.sleep( main.chkFlowSleep )
            tAllRemoved = time.time()

        if tLastDeleteEnd - tLastDeleteEnd >= int( main.params[ 'CASE2100' ][ 'chkFlowTO' ] ):
            main.log.warn( "ONOS Flows still in pending state after: {} seconds.".format( tAllRemoved - tLastDeleteEnd ) )

        main.numFlows = int( main.params[ 'CASE1000' ][ 'batches' ] ) *\
                                                    int( main.params[ 'CASE1000' ][ 'batchSize' ] )
        main.log.info( "Total number of flows: " + str( main.numFlows ) )
        main.elapseDELETE = tLastDeleteEnd - tStartDelete
        main.log.info( "Total DELETE elapse time: " + str( main.elapseDELETE ) )
        main.log.info( "Rate of DELETE Controller response: " + str( main.numFlows / ( main.elapseDELETE ) ) )

        main.DELtoCONFRM = tAllRemoved - tLastDeleteEnd
        main.log.info( "Elapse time from end of last REST DELETE to Flows in REMOVED state: " +
                       str( main.DELtoCONFRM ) )
        main.log.info( "Rate of Confirmed Batch Flow REMOVED is ( flows/sec ): " + str( main.numFlows / main.DELtoCONFRM ) )

    def CASE100( self, main ):
        from pprint import pprint

        main.case( "Check to ensure onos flows." )

        resp = main.Cluster.active( 0 ).REST.checkFlowsState()
        #pprint( resp )

    def CASE210( self, main ):
        main.case( "Log test results to a data file" )
        main.step( "Write test resulted data to a data file" )
        main.scale = main.maxNodes

        try:
            dbFileName = "/tmp/SCPFbatchFlowRespData"
            dbfile = open( dbFileName, "w+" )
            temp = "'" + main.commit + "',"
            temp += "'1gig',"
            temp += "'" + str( main.scale ) + "',"
            temp += "'" + main.cluster + "',"
            temp += "'" + str( main.elapsePOST ) + "',"
            temp += "'" + str( main.POSTtoCONFRM ) + "',"
            temp += "'" + str( main.numFlows / main.POSTtoCONFRM ) + "',"
            temp += "'" + str( main.elapseDELETE ) + "',"
            temp += "'" + str( main.DELtoCONFRM ) + "',"
            temp += "'" + str( main.numFlows / main.DELtoCONFRM ) + "',"
            temp += "'" + str( main.numSw ) + "'\n"
            dbfile.write( temp )
            dbfile.close()
            stepResult = main.TRUE
        except IOError:
            main.log.warn( "Error opening " + dbFileName + " to write results." )
            stepResult = main.FALSE

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Succeeded to write results to datafile",
                                 onfail="Failed to write results to datafile " )

    def CASE110( self, main ):
        """
        Report errors/warnings/exceptions
        """
        main.log.info( "Error report: \n" )
        main.ONOSbench.logReport( main.Cluster.active( 0 ).ipAddress,
                                  [ "INFO",
                                    "FOLLOWER",
                                    "WARN",
                                    "flow",
                                    "ERROR",
                                    "Except" ],
                                  "s" )
        #main.stop()

