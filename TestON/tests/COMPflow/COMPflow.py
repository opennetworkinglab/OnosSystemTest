class COMPflow:

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
        main.maxNodes = int( main.params[ 'SCALE' ][ 'max' ] )
        main.startUpSleep = int( main.params[ 'SLEEP' ][ 'startup' ] )
        main.startMNSleep = int( main.params[ 'SLEEP' ][ 'startMN' ] )
        main.addFlowSleep = int( main.params[ 'SLEEP' ][ 'addFlow' ] )
        main.delFlowSleep = int( main.params[ 'SLEEP' ][ 'delFlow' ] )
        main.debug = main.params['DEBUG']
        #main.swDPID = main.params[ 'TEST' ][ 'swDPID' ]
        main.cellData = {} # for creating cell file
        main.CLIs = []
        main.ONOSip = []

        main.debug = True if "on" in main.debug else False

        main.ONOSip = main.ONOSbench.getOnosIps()

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
        packageResult = main.ONOSbench.onosPackage(opTimeout=30)
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
                        main.CLIs[ i ].startOnosCli( main.ONOSip[ i ], onosStartTimeout=30 )
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

        main.numSw = int(main.params['CASE10']['numSw'])
        main.case( "Setup mininet and compare ONOS topology view to Mininet topology" )
        main.caseExplanation = "Start mininet with custom topology and compare topology " +\
                "elements between Mininet and ONOS"

        main.step( "Setup Mininet Linear Topology with " + str(main.numSw) + " switches" )
        stepResult = main.Mininet1.startNet( args = main.params['CASE10']['mnArgs'] )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully loaded topology",
                                 onfail="Failed to load topology" )

        main.step( "Assign switches to controller" )
        for i in range(1, main.numSw + 1):
            main.Mininet1.assignSwController( "s" + str(i), main.ONOSip[0] )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully assigned switch to controller",
                                 onfail="Failed to assign switch to controller" )

        time.sleep( main.startMNSleep )




    def CASE1000( self, main ):
        '''
            create JSON object with batched flows
        '''
        import numpy
        import time

        main.case( "Create a json object for the batched flows" )

        main.step( "Parse batch information" )
        main.batchSize = int(main.params['CASE1000']['batchSize'])
        main.log.info("Number of flows in a batch is:" + str(main.batchSize))

        main.flowJsonBatchList = []
        postTimes = []
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
                                                           ingressPort = 2,
                                                           egressPort = 3)
            main.flowJsonBatchList.append(flowJsonBatch)

            startSw += 1



        main.step("Using REST API /flows/{} to post flow batch")
        tStartPost = time.time()
        for item in main.flowJsonBatchList:
            ts = time.time()
            resp = main.ONOSrest.sendFlowBatch(batch = item )
            teBatch = time.time() - ts
            postTimes.append(teBatch)
            main.log.info("Batch Rest Post Elapse time is: " + str(teBatch))

        tLastPostEnd = time.time()

        main.step("Check to ensure all flows are in added state.")
        resp = main.FALSE
        while resp != main.TRUE:
            resp = main.ONOSrest.checkFlowsState()
            time.sleep(0.5)
        tAllAdded = time.time()

        numFlows = int(main.params['CASE1000']['batches']) *\
                                                    int(main.params['CASE1000']['batchSize'])
        main.log.info("Total number of flows: " + str (numFlows) )
        main.log.info("Sum of each POST elapse time: " + str(numpy.sum(postTimes)) )
        main.log.info("Total POST elapse time: " + str(tLastPostEnd-tStartPost))

        duration = tAllAdded - tLastPostEnd
        main.log.info("Elapse time from end of last REST POST to Flows in ADDED state: " +\
                      str(duration))
        main.log.info("Rate of Batch Flow add is (flows/sec): " + str( numFlows / duration))

    def CASE2000(self, main):
        import time
        import numpy

        rmTimes = []

        main.case("Remove flow timing")

        tStartRemove = time.time()
        for item in main.flowJsonBatchList:
            ts = time.time()
            resp = main.ONOSrest.removeFlowBatch(batch = item )
            teBatch = time.time() - ts
            rmTimes.append(teBatch)
            main.log.info("Batch Rest Remove Elapse time is: " + str(teBatch))

        tLastRemoveEnd = time.time()

        main.step("Check to ensure all flows are in added state.")
        resp = main.FALSE
        while resp != main.TRUE:
            resp = main.ONOSrest.checkFlowsState()
            time.sleep(0.5)
        tAllRemoved = time.time()

        main.log.info("Total number of flows: " + str (int(main.params['CASE1000']['batches']) *\
                                                    int(main.params['CASE1000']['batchSize']) *\
                                                    int(main.params['CASE10']['numSw'])) )
        main.log.info("Sum of each DELETE elapse time: " + str(numpy.sum(rmTimes)) )
        main.log.info("Total POST elapse time: " + str(tLastRemoveEnd-tStartRemove))

        main.log.info("Elapse time from end of last REST POST to Flows in ADDED state: " +\
                      str(tAllRemoved - tLastRemoveEnd))

    def CASE100(self,main):
        from pprint import pprint

        main.case( "Check to ensure onos flows." )

        resp = main.ONOSrest.checkFlowsState()
        pprint(resp)


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
        main.stop()

