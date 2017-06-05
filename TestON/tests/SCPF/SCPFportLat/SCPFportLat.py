'''
    SCPFportLat test
    Test latency for port status change
    Up & Down:
    PortStatus --- Device --- Link --- Graph

    yunpeng@onlab.us
'''
class SCPFportLat:
    def __init__( self ):
        self.default = ''

    def CASE0( self, main ):
        import os
        import imp
        '''
        - GIT
        - BUILDING ONOS
            Pull specific ONOS branch, then Build ONOS ono ONOS Bench.
            This step is usually skipped. Because in a Jenkins driven automated
            test env. We want Jenkins jobs to pull&build for flexibility to handle
            different versions of ONOS.
        - Construct tests variables
        '''
        gitPull = main.params['GIT']['gitPull']
        gitBranch = main.params['GIT']['gitBranch']

        main.case( "Pull onos branch and build onos on Teststation." )

        if gitPull == 'True':
            main.step( "Git Checkout ONOS branch: " + gitBranch )
            stepResult = main.ONOSbench.gitCheckout( branch=gitBranch )
            utilities.assert_equals(expect=main.TRUE,
                                    actual=stepResult,
                                    onpass="Successfully checkout onos branch.",
                                    onfail="Failed to checkout onos branch. Exiting test...")
            if not stepResult: main.exit()

            main.step( "Git Pull on ONOS branch:" + gitBranch )
            stepResult = main.ONOSbench.gitPull()
            utilities.assert_equals(expect=main.TRUE,
                                    actual=stepResult,
                                    onpass="Successfully pull onos. ",
                                    onfail="Failed to pull onos. Exiting test ...")
            if not stepResult: main.exit()

            main.step( "Building ONOS branch: " + gitBranch )
            stepResult = main.ONOSbench.cleanInstall( skipTest=True )
            utilities.assert_equals(expect=main.TRUE,
                                    actual=stepResult,
                                    onpass="Successfully build onos.",
                                    onfail="Failed to build onos. Exiting test...")
            if not stepResult: main.exit()

        else:
            main.log.warn( "Skipped pulling onos and Skipped building ONOS" )

        main.testOnDirectory = os.path.dirname( os.getcwd() )
        main.MN1Ip = main.params['MN']['ip1']
        main.dependencyPath = main.testOnDirectory + \
                              main.params['DEPENDENCY']['path']
        main.dependencyFunc = main.params['DEPENDENCY']['function']
        main.topoName = main.params['DEPENDENCY']['topology']
        main.cellName = main.params['ENV']['cellName']
        main.Apps = main.params['ENV']['cellApps']
        main.scale = (main.params['SCALE']).split(",")
        main.ofportStatus = main.params['TSHARK']['ofpPortStatus']
        main.tsharkResultPath = main.params['TSHARK']['tsharkReusltPath']
        main.sampleSize = int( main.params['TEST']['sampleSize'] )
        main.warmUp = int( main.params['TEST']['warmUp'] )
        main.maxProcessTime = int( main.params['TEST']['maxProcessTime'])
        main.dbFileName = main.params['DATABASE']['dbName']
        main.startUpSleep = int( main.params['SLEEP']['startup'] )
        main.measurementSleep = int( main.params['SLEEP']['measure'] )
        main.maxScale = int( main.params['max'] )
        main.interface = main.params['TEST']['interface']
        main.timeout = int( main.params['TIMEOUT']['timeout'] )
        main.MNSleep = int( main.params['SLEEP']['mininet'])
        main.device = main.params['TEST']['device']
        main.debug = main.params['TEST']['debug']

        if main.debug == "True":
            main.debug = True
        else:
            main.debug = False

        main.log.info( "Create Database file " + main.dbFileName )
        resultsDB = open( main.dbFileName, "w+" )
        resultsDB.close()

        main.portFunc = imp.load_source(main.dependencyFunc,
                                       main.dependencyPath +
                                       main.dependencyFunc +
                                       ".py")

    def CASE1( self, main ):
        # Clean up test environment and set up
        import time
        main.log.info( "Get ONOS cluster IP" )
        print( main.scale )
        main.numCtrls = int( main.scale.pop(0) )
        main.ONOSip = []
        main.maxNumBatch = 0
        main.AllONOSip = main.ONOSbench.getOnosIps()
        for i in range( main.numCtrls ):
            main.ONOSip.append( main.AllONOSip[i] )
        main.log.info( main.ONOSip )
        main.CLIs = []
        main.log.info( "Creating list of ONOS cli handles" )
        for i in range( main.numCtrls ):
            main.CLIs.append( getattr(main, 'ONOS%scli' % (i + 1)) )

        if not main.CLIs:
            main.log.error( "Failed to create the list of ONOS cli handles" )
            main.cleanup()
            main.exit()

        main.commit = main.ONOSbench.getVersion( report=True )
        main.commit = main.commit.split(" ")[1]
        main.log.info( "Starting up %s node(s) ONOS cluster" % main.numCtrls )
        main.log.info("Safety check, killing all ONOS processes" +
                      " before initiating environment setup")

        for i in range( main.numCtrls ):
            main.ONOSbench.onosStop( main.ONOSip[i] )
            main.ONOSbench.onosKill( main.ONOSip[i] )

        main.log.info( "NODE COUNT = %s" % main.numCtrls )
        main.ONOSbench.createCellFile(main.ONOSbench.ip_address,
                                      main.cellName,
                                      main.MN1Ip,
                                      main.Apps,
                                      main.ONOSip,
                                      main.ONOScli1.user_name)
        main.step( "Apply cell to environment" )
        cellResult = main.ONOSbench.setCell( main.cellName )
        verifyResult = main.ONOSbench.verifyCell()
        stepResult = cellResult and verifyResult
        utilities.assert_equals(expect=main.TRUE,
                                actual=stepResult,
                                onpass="Successfully applied cell to " + \
                                       "environment",
                                onfail="Failed to apply cell to environment ")

        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.buckBuild()
        stepResult = packageResult
        utilities.assert_equals(expect=main.TRUE,
                                actual=stepResult,
                                onpass="Successfully created ONOS package",
                                onfail="Failed to create ONOS package")

        main.step( "Uninstall ONOS package on all Nodes" )
        uninstallResult = main.TRUE
        for i in range( int( main.numCtrls ) ):
            main.log.info( "Uninstalling package on ONOS Node IP: " + main.ONOSip[i] )
            u_result = main.ONOSbench.onosUninstall( main.ONOSip[i] )
            utilities.assert_equals(expect=main.TRUE, actual=u_result,
                                    onpass="Test step PASS",
                                    onfail="Test step FAIL")
            uninstallResult = uninstallResult and u_result

        main.step( "Install ONOS package on all Nodes" )
        installResult = main.TRUE
        for i in range( int( main.numCtrls ) ):
            main.log.info( "Installing package on ONOS Node IP: " + main.ONOSip[i] )
            i_result = main.ONOSbench.onosInstall( node=main.ONOSip[i] )
            utilities.assert_equals(expect=main.TRUE, actual=i_result,
                                    onpass="Test step PASS",
                                    onfail="Test step FAIL")
            installResult = installResult and i_result

        main.step( "Set up ONOS secure SSH" )
        secureSshResult = main.TRUE
        for i in range( int( main.numCtrls ) ):
            secureSshResult = secureSshResult and main.ONOSbench.onosSecureSSH( node=main.ONOSip[i] )
        utilities.assert_equals( expect=main.TRUE, actual=secureSshResult,
                                 onpass="Test step PASS",
                                 onfail="Test step FAIL" )

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

        main.step( "Start ONOS CLI on all nodes" )
        cliResult = main.TRUE
        main.step( " Start ONOS cli using thread " )
        startCliResult = main.TRUE
        pool = []
        main.threadID = 0
        for i in range( int( main.numCtrls ) ):
            t = main.Thread(target=main.CLIs[i].startOnosCli,
                            threadID=main.threadID,
                            name="startOnosCli",
                            args=[main.ONOSip[i]],
                            kwargs={"onosStartTimeout": main.timeout})
            pool.append(t)
            t.start()
            main.threadID = main.threadID + 1
        for t in pool:
            t.join()
            startCliResult = startCliResult and t.result
        time.sleep( main.startUpSleep )

        main.log.info( "Configure apps" )
        main.CLIs[0].setCfg("org.onosproject.net.topology.impl.DefaultTopologyProvider",
                            "maxEvents 1")
        main.CLIs[0].setCfg("org.onosproject.net.topology.impl.DefaultTopologyProvider",
                            "maxBatchMs 0")
        main.CLIs[0].setCfg("org.onosproject.net.topology.impl.DefaultTopologyProvider",
                            "maxIdleMs 0")
        time.sleep(1)
        main.log.info( "Copy topology file to Mininet" )
        main.ONOSbench.copyMininetFile(main.topoName,
                                       main.dependencyPath,
                                       main.Mininet1.user_name,
                                       main.Mininet1.ip_address)
        main.log.info( "Stop Mininet..." )
        main.Mininet1.stopNet()
        time.sleep( main.MNSleep )
        main.log.info( "Start new mininet topology" )
        main.Mininet1.startNet()
        main.log.info( "Assign switch to controller to ONOS node 1" )
        time.sleep(1)
        main.Mininet1.assignSwController( sw='s1', ip=main.ONOSip[0] )
        main.Mininet1.assignSwController( sw='s2', ip=main.ONOSip[0] )

        time.sleep(2)

    def CASE2( self, main ):
        import time
        import numpy
        # dictionary for each node and each timestamps
        resultDict = {'up' : {}, 'down' : {}}
        for d in resultDict:
            for i in range( 1, main.numCtrls + 1 ):
                resultDict[d][ 'node' + str(i) ] = {}
                resultDict[d][ 'node' + str(i) ][ 'Ave' ] = {}
                resultDict[d][ 'node' + str(i) ][ 'Std' ] = {}
                resultDict[d][ 'node' + str(i) ][ 'EtoE' ] = []
                resultDict[d][ 'node' + str(i) ][ 'PtoD' ] = []
                resultDict[d][ 'node' + str(i) ][ 'DtoL' ] = []
                resultDict[d][ 'node' + str(i) ][ 'LtoG' ] = []
        for i in range( 1, main.sampleSize + main.warmUp ):
            main.log.info( "==========================================" )
            main.log.info( "================iteration:{}==============".format(str (i) ) )
            if i > main.warmUp:
                # Portdown iteration
                main.portFunc.capturePortStatusPack( main, main.device, main.interface, "down", resultDict, False )
                time.sleep(2)
                # PortUp iteration
                main.portFunc.capturePortStatusPack( main, main.device, main.interface, "up", resultDict, False )
            else:
                # if warm up, keep old result dictionary
                main.portFunc.capturePortStatusPack( main, main.device, main.interface, "down", resultDict, True)
                main.portFunc.capturePortStatusPack( main, main.device, main.interface, "up", resultDict, True)

        # Dictionary for result
        maxDict  = {}
        maxDict['down'] = {}
        maxDict['up'] = {}
        maxDict['down']['max'] = 0
        maxDict['up']['max'] = 0
        maxDict['down']['node'] = 0
        maxDict['up']['node'] = 0
        EtoEtemp = 0
        for d in resultDict:
            for i in range( 1, main.numCtrls + 1 ):
                # calculate average and std for result, and grep the max End to End data
                EtoEtemp = numpy.average( resultDict[d][ 'node' + str(i) ]['EtoE'] )
                resultDict[d][ 'node' + str(i) ][ 'Ave' ][ 'EtoE' ] = EtoEtemp
                if maxDict[d]['max'] < EtoEtemp:
                    # get max End to End latency
                    maxDict[d]['max'] = EtoEtemp
                    maxDict[d]['node'] = i
                resultDict[d]['node' + str(i)]['Ave']['PtoD'] = numpy.average(resultDict[d]['node' + str(i)]['PtoD'])
                resultDict[d]['node' + str(i)]['Ave']['DtoL'] = numpy.average(resultDict[d]['node' + str(i)]['DtoL'])
                resultDict[d]['node' + str(i)]['Ave']['LtoG'] = numpy.average(resultDict[d]['node' + str(i)]['LtoG'])

                resultDict[d]['node' + str(i)]['Std']['EtoE'] = numpy.std(resultDict[d]['node' + str(i)]['EtoE'])
                resultDict[d]['node' + str(i)]['Std']['PtoD'] = numpy.std(resultDict[d]['node' + str(i)]['PtoD'])
                resultDict[d]['node' + str(i)]['Std']['DtoL'] = numpy.std(resultDict[d]['node' + str(i)]['DtoL'])
                resultDict[d]['node' + str(i)]['Std']['LtoG'] = numpy.std(resultDict[d]['node' + str(i)]['LtoG'])

                main.log.report( "=====node{} Summary:=====".format( str(i) ) )
                main.log.report( "=============Port {}=======".format( str(d) ) )
                main.log.report(
                    "End to End average: {}".format( str(resultDict[d][ 'node' + str(i) ][ 'Ave' ][ 'EtoE' ]) ) )
                main.log.report(
                    "End to End Std: {}".format( str(resultDict[d][ 'node' + str(i) ][ 'Std' ][ 'EtoE' ]) ) )
                main.log.report(
                    "Package to Device average: {}".format( str(resultDict[d]['node' + str(i)]['Ave']['PtoD']) ) )
                main.log.report(
                    "Package to Device Std: {}".format( str( resultDict[d]['node' + str(i)]['Std']['PtoD'])))
                main.log.report(
                    "Device to Link average: {}".format( str( resultDict[d]['node' + str(i)]['Ave']['DtoL']) ) )
                main.log.report(
                    "Device to Link Std: {}".format( str( resultDict[d]['node' + str(i)]['Std']['DtoL'])))
                main.log.report(
                    "Link to Grapg average: {}".format( str( resultDict[d]['node' + str(i)]['Ave']['LtoG']) ) )
                main.log.report(
                    "Link to Grapg Std: {}".format( str( resultDict[d]['node' + str(i)]['Std']['LtoG'] ) ) )

        with open( main.dbFileName, "a" ) as dbFile:
            # Scale number
            temp = str( main.numCtrls )
            temp += ",'baremetal1'"
            # put result
            temp += "," + str( resultDict['up'][ 'node' + str(maxDict['up']['node']) ][ 'Ave' ][ 'EtoE' ] )
            temp += "," + str( resultDict['up'][ 'node' + str(maxDict['up']['node']) ][ 'Ave' ][ 'PtoD' ] )
            temp += "," + str( resultDict['up'][ 'node' + str(maxDict['up']['node']) ][ 'Ave' ][ 'DtoL' ] )
            temp += "," + str( resultDict['up'][ 'node' + str(maxDict['up']['node']) ][ 'Ave' ][ 'LtoG' ] )
            temp += "," + str( resultDict['down'][ 'node' + str(maxDict['down']['node']) ][ 'Ave' ][ 'EtoE' ] )
            temp += "," + str( resultDict['down'][ 'node' + str(maxDict['down']['node']) ][ 'Ave' ][ 'PtoD' ] )
            temp += "," + str( resultDict['down'][ 'node' + str(maxDict['down']['node']) ][ 'Ave' ][ 'DtoL' ] )
            temp += "," + str( resultDict['down'][ 'node' + str(maxDict['down']['node']) ][ 'Ave' ][ 'LtoG' ] )

            temp += "," + str( resultDict['up'][ 'node' + str(maxDict['up']['node']) ][ 'Std' ][ 'EtoE' ] )
            temp += "," + str( resultDict['down'][ 'node' + str(maxDict['down']['node']) ][ 'Std' ][ 'EtoE' ] )

            temp += "\n"
            dbFile.write( temp )
            dbFile.close()
