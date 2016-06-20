class SCPFbatchFlowResp:
    '''
    Testing end-to-end ONOS response time from POST of batched flows to when ONOS returns
    response confirmation of all flows ADDED; subsequently testing the response time from when REST DELETE to
    ONOS confirmation of all flows REMOVED.
    '''

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

        # Test variables
        main.testOnDirectory = os.path.dirname( os.getcwd ( ) )
        main.cellName = main.params[ 'CASE1' ][ 'cellName' ]
        main.apps = main.params[ 'CASE1' ][ 'cellApps' ]
        gitBranch = main.params[ 'CASE1' ][ 'gitBranch' ]
        gitPull = main.params[ 'CASE1' ][ 'gitPull' ]
        main.maxNodes = int( main.params['GLOBAL'][ 'maxNodes' ] )
        main.startUpSleep = float( main.params['GLOBAL'][ 'SLEEP' ][ 'startup' ] )
        main.startMNSleep = float( main.params['GLOBAL'][ 'SLEEP' ][ 'startMN' ] )
        main.addFlowSleep = float( main.params['GLOBAL'][ 'SLEEP' ][ 'addFlow' ] )
        main.delFlowSleep = float( main.params['GLOBAL'][ 'SLEEP' ][ 'delFlow' ] )
        main.chkFlowSleep = float( main.params['GLOBAL']['SLEEP']['chkFlow'])
        main.cfgSleep = float( main.params['GLOBAL']['SLEEP']['cfg'])
        main.numSw = int( main.params['GLOBAL']['numSw'])
        main.numThreads = int( main.params['GLOBAL']['numThreads'] )
        main.cellData = {} # for creating cell file
        main.CLIs = []
        main.ONOSip = []

        main.ONOSip = main.ONOSbench.getOnosIps()
        main.commit = main.ONOSbench.getVersion()
        main.commit = main.commit.split(" ")[1]

        main.cluster = main.params['GLOBAL']['cluster']

        # Assigning ONOS cli handles to a list
        for i in range( 1,  main.maxNodes + 1 ):
            main.CLIs.append( getattr( main, 'ONOScli' + str( i ) ) )


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

        main.log.info( "Safety check, killing all ONOS processes" +
                       " before initiating environment setup" )

        tempOnosIp = []
        for i in range( main.numCtrls ):
            tempOnosIp.append( main.ONOSip[i] )

        if main.params['CASE2']['incPackaging'] == "true":
            main.step("Create onos cell file with: " + main.apps)
            main.ONOSbench.createCellFile( main.ONOSbench.ip_address, "temp",
                                       main.Mininet1.ip_address, main.apps, tempOnosIp )

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
            packageResult = main.ONOSbench.onosPackage(opTimeout=240)
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

        else:
            main.log.info("onos Packaging Skipped!")

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
        for i in range( i, main.numCtrls ):
            cliResult = cliResult and \
                        main.ONOScli1.startCellCli( )
            main.log.info("ONOSip is: " + main.ONOScli1.ip_address)
        stepResult = cliResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully start ONOS cli",
                                 onfail="Failed to start ONOS cli" )



    def CASE10( self, main ):
        '''
            Start Mininet
        '''
        import time

        main.case( "Enable openflow-base on onos and start Mininet." )

        main.step("Activate openflow-base App")
        app = main.params['CASE10']['app']
        stepResult = main.ONOScli1.activateApp( app )
        time.sleep(main.cfgSleep)
        main.log.info(stepResult)
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully activate " + app,
                                 onfail="Failed to activate app " + app )

        time.sleep(main.cfgSleep)


        main.step( "Configure AdaptiveFlowSampling ")
        stepResult = main.ONOScli1.setCfg( component = "org.onosproject.provider.of.flow.impl.OpenFlowRuleProvider",
                                   propName = "adaptiveFlowSampling ",  value = main.params['CASE10']['adaptiveFlowenabled'])
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="App Configuration Succeeded! ",
                                 onfail="App Configuration Failed!" )
        time.sleep(main.cfgSleep)

        main.step( "Setup Mininet Linear Topology with " + str(main.numSw) + " switches" )
        argStr = main.params['CASE10']['mnArgs'].format(main.numSw)
        stepResult = main.Mininet1.startNet( args = argStr )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully loaded topology",
                                 onfail="Failed to load topology" )

        time.sleep( main.startMNSleep )

        main.step( "Assign switches to controller" )
        for i in range(1, main.numSw + 1):
            main.Mininet1.assignSwController( "s" + str(i), main.ONOSip[0] )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully assigned switch to controller",
                                 onfail="Failed to assign switch to controller" )

        main.deviceIdPrefix = "of:"

        time.sleep( main.startMNSleep )

    def CASE11( self, main ):
        '''
            Start Null Provider
        '''
        import time

        main.case( "Setup Null Provider for linear Topology" )

        main.step("Activate Null Provider App")
        stepResult = main.ONOSbench.onosCli( ONOSIp = main.ONOSip[0],
                                             cmdstr = "app activate org.onosproject.null" )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully activated org.onosproject.null",
                                 onfail="Failed to activate org.onosproject.null" )
        time.sleep( main.cfgSleep)

        main.step( "Setup Null Provider Linear Topology with " + str(main.numSw) + " devices." )
        r1 = main.ONOSbench.onosCfgSet( main.ONOSip[0], "org.onosproject.provider.nil.NullProviders", "deviceCount " + str(main.numSw))
        r2 = main.ONOSbench.onosCfgSet( main.ONOSip[0], "org.onosproject.provider.nil.NullProviders", "topoShape " + main.params['CASE11']['nullTopo'] )
        r3 = main.ONOSbench.onosCfgSet( main.ONOSip[0], "org.onosproject.provider.nil.NullProviders", "enabled " + main.params['CASE11']['nullStart'])
        stepResult = r1 & r2 & r3
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="App Configuration Succeeded! ",
                                 onfail="App Configuration Failed!" )
        time.sleep( main.cfgSleep )

        main.log.info("Check to make sure null providers are configured correctly.")
        main.ONOSbench.handle.sendline("onos $OC1 summary")
        stepResult = main.ONOSbench.handle.expect(":~")
        main.log.info("ONOS Summary: " + main.ONOSbench.handle.before)

        main.deviceIdPrefix = "null:"

        time.sleep( main.startMNSleep )



    def CASE1000( self, main ):
        '''
            create JSON object with batched flows
        '''
        import numpy
        import time
        from pprint import pprint

        main.case( "Create a json object for the batched flows" )

        main.step( "Parse batch creation information" )
        main.batchSize = int(main.params['CASE1000']['batchSize'])
        main.log.info("Number of flows in a batch is:" + str(main.batchSize))

        main.flowJsonBatchList = []
        startSw = 1

        main.step("Creating a full list of batches")
        for index in range(1, int(main.params['CASE1000']['batches']) + 1):
            if startSw <= main.numSw:
                ind = startSw
            else:
                startSw = 1
                ind = startSw

            main.log.info("Creating batch: " + str(index))
            flowJsonBatch = main.ONOSrest.createFlowBatch( numSw = main.numSw,
                                                           swIndex = ind,
                                                           batchSize = main.batchSize,
                                                           batchIndex = index,
                                                           deviceIdpreFix=main.deviceIdPrefix,
                                                           ingressPort = 2,
                                                           egressPort = 3)
            main.flowJsonBatchList.append(flowJsonBatch)

            startSw += 1
        main.log.info( "Number of items created in the batch list is: " + str(len(main.flowJsonBatchList)))

    def CASE2100(self, main):
        '''
            Posting flow batches using threads
        '''
        main.case("Using REST API /flows/{} to post flow batch - multi-threads")
        main.step("Using REST API /flows/{} to post flow batch - multi-threads")

        from Queue import Queue
        from threading import Thread
        import time
        import json

        main.threadID = 0
        main.addedBatchList = []
        q = Queue()
        tAllAdded = 0

        def postWorker(id):
            while True:
                item = q.get()
                #print json.dumps(item)
                status,response = main.ONOSrest.sendFlowBatch(batch = item)
                main.log.info("Thread {} is working on posting. ".format(id))
                #print json.dumps(response)
                main.addedBatchList.append(response[1])
                q.task_done()

        for i in range( int( main.params['CASE2100']['numThreads'])):
            threadID = "ThreadID-" + str(i)
            t = Thread(target = postWorker, name = threadID, args=(threadID,) )
            t.daemon = True
            t.start()

        tStartPost = time.time()
        for item in main.flowJsonBatchList:
            q.put(item)

        q.join()
        tLastPostEnd = time.time()

        main.step("Check to ensure all flows are in added state.")
        #pprint(main.addedBatchList)
        resp = main.FALSE
        while resp != main.TRUE and ( tAllAdded - tLastPostEnd < int (main.params['CASE2100']['chkFlowTO']) ):
            if main.params['CASE2100']['RESTchkFlow'] == main.TRUE:
                resp = main.ONOSrest.checkFlowsState()
            else:
                handle = main.CLIs[0].flows(state = " |grep PEND|wc -l", jsonFormat=False)
                main.log.info("handle returns PENDING flows: " + handle)
                if handle == "0":
                    resp = main.TRUE

            time.sleep( main.chkFlowSleep )
            tAllAdded = time.time()

        if tAllAdded - tLastPostEnd >= int (main.params['CASE2100']['chkFlowTO']):
            main.log.warn("ONOS Flows still in pending state after: {} seconds.".format(tAllAdded - tLastPostEnd))

        main.numFlows = int(main.params['CASE1000']['batches']) *\
                                                    int(main.params['CASE1000']['batchSize'])
        main.log.info("Total number of flows: " + str (main.numFlows) )
        main.elapsePOST = tLastPostEnd-tStartPost
        main.log.info("Total POST elapse time: " + str( main.elapsePOST ) )
        main.log.info("Rate of ADD Controller response: " + str(main.numFlows / ( main.elapsePOST )))

        main.POSTtoCONFRM = tAllAdded - tLastPostEnd
        main.log.info("Elapse time from end of last REST POST to Flows in ADDED state: " +\
                      str( main.POSTtoCONFRM ))
        main.log.info("Rate of Confirmed Batch Flow ADD is (flows/sec): " +
                      str( main.numFlows / main.POSTtoCONFRM ))
        main.log.info("Number of flow Batches in the addedBatchList is: " +
                      str( len(main.addedBatchList)))

    def CASE3100(self, main):
        '''
            DELETE flow batches using threads
        '''
        main.case("Using REST API /flows/{} to delete flow batch - multi-threads")
        main.step("Using REST API /flows/{} to delete flow batch - multi-threads")

        from Queue import Queue
        from threading import Thread
        import time
        import json

        main.threadID = 0
        q = Queue()
        tAllRemoved = 0

        main.log.info("Number of flow batches at start of remove: " + str( len( main.addedBatchList)))
        def removeWorker(id):
            while True:
                item = q.get()
                response = main.ONOSrest.removeFlowBatch(batch = json.loads(item) )
                main.log.info("Thread {} is working on deleting. ".format(id))
                q.task_done()

        for i in range( int( main.params['CASE2100']['numThreads'])):
            threadID = "ThreadID-" + str(i)
            t = Thread(target = removeWorker, name = threadID, args=(threadID,) )
            t.daemon = True
            t.start()

        tStartDelete = time.time()
        for item in main.addedBatchList:
            q.put(item)

        q.join()
        tLastDeleteEnd = time.time()
        main.log.info("Number of flow batches at end of remove: " + str( len( main.addedBatchList)))

        main.step("Check to ensure all flows are in added state.")
        #pprint(main.addedBatchList)
        resp = main.FALSE
        while resp != main.TRUE and ( tAllRemoved - tLastDeleteEnd < int (main.params['CASE3100']['chkFlowTO']) ):
            if main.params['CASE3100']['RESTchkFlow'] == main.TRUE:
                resp = main.ONOSrest.checkFlowsState()
            else:
                handle = main.CLIs[0].flows(state = " |grep PEND|wc -l", jsonFormat=False)
                main.log.info("handle returns PENDING flows: " + handle)
                if handle == "0":
                    resp = main.TRUE
            time.sleep( main.chkFlowSleep )
            tAllRemoved = time.time()

        if tLastDeleteEnd - tLastDeleteEnd >= int (main.params['CASE2100']['chkFlowTO']):
            main.log.warn("ONOS Flows still in pending state after: {} seconds.".format(tAllRemoved - tLastDeleteEnd))

        main.numFlows = int(main.params['CASE1000']['batches']) *\
                                                    int(main.params['CASE1000']['batchSize'])
        main.log.info("Total number of flows: " + str (main.numFlows) )
        main.elapseDELETE = tLastDeleteEnd-tStartDelete
        main.log.info("Total DELETE elapse time: " + str( main.elapseDELETE ))
        main.log.info("Rate of DELETE Controller response: " + str(main.numFlows / ( main.elapseDELETE )))

        main.DELtoCONFRM = tAllRemoved - tLastDeleteEnd
        main.log.info("Elapse time from end of last REST DELETE to Flows in REMOVED state: " +\
                      str( main.DELtoCONFRM ))
        main.log.info("Rate of Confirmed Batch Flow REMOVED is (flows/sec): " + str( main.numFlows / main.DELtoCONFRM))

    def CASE100(self,main):
        from pprint import pprint

        main.case( "Check to ensure onos flows." )

        resp = main.ONOSrest.checkFlowsState()
        #pprint(resp)

    def CASE210(self,main):
        main.case("Log test results to a data file")
        main.step("Write test resulted data to a data file")
        main.scale = main.maxNodes

        try:
            dbFileName="/tmp/SCPFbatchFlowRespData"
            dbfile = open(dbFileName, "w+")
            temp = "'" + main.commit + "',"
            temp += "'1gig',"
            temp += "'" + str( main.scale ) + "',"
            temp += "'" + main.cluster + "',"
            temp += "'" + str( main.elapsePOST ) + "',"
            temp += "'" + str( main.POSTtoCONFRM ) + "',"
            temp += "'" + str( main.numFlows / main.POSTtoCONFRM ) + "',"
            temp += "'" + str ( main.elapseDELETE ) + "',"
            temp += "'" + str ( main.DELtoCONFRM ) + "',"
            temp += "'" + str( main.numFlows / main.DELtoCONFRM ) + "',"
            temp += "'" + str( main.numSw ) + "'\n"
            dbfile.write( temp )
            dbfile.close()
            stepResult = main.TRUE
        except IOError:
            main.log.warn("Error opening " + dbFileName + " to write results.")
            stepResult = main.FALSE

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Succeeded to write results to datafile",
                                 onfail="Failed to write results to datafile " )
        
    def CASE110( self, main ):
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
        #main.stop()

