'''
    SCPFswitchLat
    Test Switch add/remove latency
    calculate package latency between switch and ONOS
    Switch UP:
    TCP -- Feature Reply -- Role Request -- Role Reply -- Device -- Graph
    Siwtch Down:
    Openflow FIN/ACK -- ACK -- Device -- Graph
'''

class SCPFswitchLat:

    def __init__(self):
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
        # The dictionary to record different type of wrongs
        main.wrong = { 'totalWrong': 0, 'skipDown' : 0, 'TsharkValueIncorrect': 0,
                'TypeError' : 0, 'decodeJasonError': 0,
                'checkResultIncorrect': 0}
        main.maxWrong = int( main.params['TEST'] ['MaxWrong'] )
        main.resultRange = main.params['TEST']['ResultRange']
        main.searchTerm = main.params['TEST']['SearchTerm']
        main.testOnDirectory = os.path.dirname( os.getcwd() )
        main.MN1Ip = main.params['MN']['ip1']
        main.dependencyPath = main.testOnDirectory + \
                              main.params['DEPENDENCY']['path']
        main.topoName = main.params['DEPENDENCY']['topology']
        main.dependencyFunc = main.params['DEPENDENCY']['function']
        main.cellName = main.params['ENV']['cellName']
        main.Apps = main.params['ENV']['cellApps']
        main.scale = (main.params['SCALE']).split(",")

        main.ofPackage = main.params['TSHARK']

        main.tsharkResultPath = main.params['TEST']['tsharkResultPath']
        main.sampleSize = int(main.params['TEST']['sampleSize'])
        main.warmUp = int(main.params['TEST']['warmUp'])
        main.dbFileName = main.params['DATABASE']['dbName']
        main.startUpSleep = int(main.params['SLEEP']['startup'])
        main.measurementSleep = int( main.params['SLEEP']['measure'] )
        main.deleteSwSleep = int( main.params['SLEEP']['deleteSW'] )
        main.maxScale = int( main.params['max'] )
        main.timeout = int( main.params['TIMEOUT']['timeout'] )
        main.MNSleep = int( main.params['SLEEP']['mininet'])
        main.device = main.params['TEST']['device']
        main.log.info("Create Database file " + main.dbFileName)
        resultsDB = open(main.dbFileName, "w+")
        resultsDB.close()

        main.switchFunc = imp.load_source(main.dependencyFunc,
                                       main.dependencyPath +
                                       main.dependencyFunc +
                                       ".py")

    def CASE1(self, main):
        # Clean up test environment and set up
        import time
        main.log.info("Get ONOS cluster IP")
        print(main.scale)
        main.numCtrls = int(main.scale.pop(0))
        main.ONOSip = []
        main.maxNumBatch = 0
        main.AllONOSip = main.ONOSbench.getOnosIps()
        for i in range(main.numCtrls):
            main.ONOSip.append(main.AllONOSip[i])
        main.log.info(main.ONOSip)
        main.CLIs = []
        main.log.info("Creating list of ONOS cli handles")
        for i in range(main.numCtrls):
            main.CLIs.append(getattr(main, 'ONOS%scli' % (i + 1)))

        if not main.CLIs:
            main.log.error("Failed to create the list of ONOS cli handles")
            main.cleanup()
            main.exit()

        main.commit = main.ONOSbench.getVersion(report=True)
        main.commit = main.commit.split(" ")[1]
        main.log.info("Starting up %s node(s) ONOS cluster" % main.numCtrls)
        main.log.info("Safety check, killing all ONOS processes" +
                      " before initiating environment setup")

        for i in range(main.numCtrls):
            main.ONOSbench.onosStop(main.ONOSip[i])
            main.ONOSbench.onosKill(main.ONOSip[i])

        main.log.info("NODE COUNT = %s" % main.numCtrls)
        main.ONOSbench.createCellFile(main.ONOSbench.ip_address,
                                      main.cellName,
                                      main.MN1Ip,
                                      main.Apps,
                                      main.ONOSip)
        main.step("Apply cell to environment")
        cellResult = main.ONOSbench.setCell(main.cellName)
        verifyResult = main.ONOSbench.verifyCell()
        stepResult = cellResult and verifyResult
        utilities.assert_equals(expect=main.TRUE,
                                actual=stepResult,
                                onpass="Successfully applied cell to " + \
                                       "environment",
                                onfail="Failed to apply cell to environment ")

        main.step("Creating ONOS package")
        packageResult = main.ONOSbench.buckBuild()
        stepResult = packageResult
        utilities.assert_equals(expect=main.TRUE,
                                actual=stepResult,
                                onpass="Successfully created ONOS package",
                                onfail="Failed to create ONOS package")

        main.step("Uninstall ONOS package on all Nodes")
        uninstallResult = main.TRUE
        for i in range(int(main.numCtrls)):
            main.log.info("Uninstalling package on ONOS Node IP: " + main.ONOSip[i])
            u_result = main.ONOSbench.onosUninstall(main.ONOSip[i])
            utilities.assert_equals(expect=main.TRUE, actual=u_result,
                                    onpass="Test step PASS",
                                    onfail="Test step FAIL")
            uninstallResult = (uninstallResult and u_result)

        main.step("Install ONOS package on all Nodes")
        installResult = main.TRUE
        for i in range(int(main.numCtrls)):
            main.log.info("Installing package on ONOS Node IP: " + main.ONOSip[i])
            i_result = main.ONOSbench.onosInstall(node=main.ONOSip[i])
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

        time.sleep(2)
        main.step("Start ONOS CLI on all nodes")
        cliResult = main.TRUE
        main.step(" Start ONOS cli using thread ")
        startCliResult = main.TRUE
        pool = []
        main.threadID = 0
        for i in range(int(main.numCtrls)):
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
        time.sleep(main.startUpSleep)

        main.log.info("Configure apps")
        main.CLIs[0].setCfg("org.onosproject.net.topology.impl.DefaultTopologyProvider",
                            "maxEvents 1")
        main.CLIs[0].setCfg("org.onosproject.net.topology.impl.DefaultTopologyProvider",
                            "maxBatchMs 0")
        main.CLIs[0].setCfg("org.onosproject.net.topology.impl.DefaultTopologyProvider",
                            "maxIdleMs 0")
        for i in range(main.numCtrls):
            main.CLIs[i].logSet( "DEBUG", "org.onosproject.metrics.topology")
        time.sleep(1)

        main.log.info("Copy topology file to Mininet")
        main.ONOSbench.copyMininetFile(main.topoName,
                                       main.dependencyPath,
                                       main.Mininet1.user_name,
                                       main.Mininet1.ip_address)
        main.log.info("Stop Mininet...")
        main.Mininet1.stopNet()
        time.sleep(main.MNSleep)
        main.log.info("Start new mininet topology")
        main.Mininet1.startNet()
        main.log.info("Assign switch to controller to ONOS node 1")

        time.sleep(2)

    def CASE2(self,main):
        import time
        import json
        import numpy

        resultDict = {'up' : {}, 'down' : {}}
        for i in range(1, main.numCtrls + 1):
            resultDict['up'][ 'node' + str(i) ] = {}
            resultDict['up'][ 'node' + str(i) ][ 'Ave' ] = {}
            resultDict['up'][ 'node' + str(i) ][ 'Std' ] = {}
            resultDict['up'][ 'node' + str(i) ][ 'T_F' ] = []#TCP to Feature
            resultDict['up'][ 'node' + str(i) ][ 'F_R' ] = []#Feature to Role
            resultDict['up'][ 'node' + str(i) ][ 'RQ_RR' ] = []#role request to role reply
            resultDict['up'][ 'node' + str(i) ][ 'RR_D' ] = []#role reply to Device
            resultDict['up'][ 'node' + str(i) ][ 'D_G' ] = []#Device to Graph
            resultDict['up'][ 'node' + str(i) ][ 'E_E' ] = []#TCP to Graph

        for i in range(1,main.numCtrls + 1):
            resultDict['down'][ 'node' + str(i) ] = {}
            resultDict['down'][ 'node' + str(i) ][ 'Ave' ] = {}
            resultDict['down'][ 'node' + str(i) ][ 'Std' ] = {}
            resultDict['down'][ 'node' + str(i) ][ 'FA_A' ] = []#Fin_ack to ACK
            resultDict['down'][ 'node' + str(i) ][ 'A_D' ] = []#Ack to Device
            resultDict['down'][ 'node' + str(i) ][ 'D_G' ] = []#Device to Graph
            resultDict['down'][ 'node' + str(i) ][ 'E_E' ] = []#fin_ack to Graph
        for i in range(1 , main.sampleSize + main.warmUp):
            main.log.info("************************************************************")
            main.log.info("************************ Iteration: {} **********************" .format(str( i )) )
            if i < main.warmUp:
                main.switchFunc.captureOfPack( main, main.device, main.ofPackage,
                                               "up", resultDict, True )
                main.switchFunc.captureOfPack( main, main.device, main.ofPackage,
                                               "down", resultDict, True )
                main.CLIs[0].removeDevice( "of:0000000000000001" )
            else:
                main.switchFunc.captureOfPack( main, main.device, main.ofPackage,
                                               "up", resultDict, False )
                main.switchFunc.captureOfPack (main, main.device, main.ofPackage,
                                               "down", resultDict, False )
                main.CLIs[0].removeDevice( "of:0000000000000001" )

        # Dictionary for result
        maxDict  = {}
        maxDict['down'] = {}
        maxDict['up'] = {}
        maxDict['down']['max'] = 0
        maxDict['up']['max'] = 0
        maxDict['down']['node'] = 0
        maxDict['up']['node'] = 0

        for i in range(1, main.numCtrls + 1):
            # calculate average and std for result, and grep the max End to End data
            EtoEtemp = numpy.average( resultDict['up'][ 'node' + str(i) ]['E_E'] )
            resultDict['up'][ 'node' + str(i) ][ 'Ave' ][ 'E_E' ] = EtoEtemp
            if maxDict['up']['max'] < EtoEtemp:
                # get max End to End latency
                maxDict['up']['max'] = EtoEtemp
                maxDict['up']['node'] = i
            resultDict['up']['node' + str(i)]['Ave']['T_F'] = numpy.average(resultDict['up']['node' + str(i)]['T_F'])
            resultDict['up']['node' + str(i)]['Ave']['F_R'] = numpy.average(resultDict['up']['node' + str(i)]['F_R'])
            resultDict['up']['node' + str(i)]['Ave']['RQ_RR'] = numpy.average(resultDict['up']['node' + str(i)]['RQ_RR'])
            resultDict['up']['node' + str(i)]['Ave']['RR_D'] = numpy.average(resultDict['up']['node' + str(i)]['RR_D'])
            resultDict['up']['node' + str(i)]['Ave']['D_G'] = numpy.average(resultDict['up']['node' + str(i)]['D_G'])

            resultDict['up'][ 'node' + str(i) ][ 'Std' ][ 'E_E' ] = numpy.std( resultDict['up'][ 'node' + str(i) ]['E_E'] )
            resultDict['up']['node' + str(i)]['Std']['T_F'] = numpy.std(resultDict['up']['node' + str(i)]['T_F'])
            resultDict['up']['node' + str(i)]['Std']['F_R'] = numpy.std(resultDict['up']['node' + str(i)]['F_R'])
            resultDict['up']['node' + str(i)]['Std']['RQ_RR'] = numpy.std(resultDict['up']['node' + str(i)]['RQ_RR'])
            resultDict['up']['node' + str(i)]['Std']['RR_D'] = numpy.std(resultDict['up']['node' + str(i)]['RR_D'])
            resultDict['up']['node' + str(i)]['Std']['D_G'] = numpy.std(resultDict['up']['node' + str(i)]['D_G'])

            # calculate average and std for result, and grep the max End to End data
            EtoEtemp = numpy.average( resultDict['down'][ 'node' + str(i) ]['E_E'] )
            resultDict['down'][ 'node' + str(i) ][ 'Ave' ][ 'E_E' ] = EtoEtemp
            if maxDict['down']['max'] < EtoEtemp:
                # get max End to End latency
                maxDict['down']['max'] = EtoEtemp
                maxDict['down']['node'] = i
            resultDict['down']['node' + str(i)]['Ave']['FA_A'] = numpy.average(resultDict['down']['node' + str(i)]['FA_A'])
            resultDict['down']['node' + str(i)]['Ave']['A_D'] = numpy.average(resultDict['down']['node' + str(i)]['A_D'])
            resultDict['down']['node' + str(i)]['Ave']['D_G'] = numpy.average(resultDict['down']['node' + str(i)]['D_G'])

            resultDict['down'][ 'node' + str(i) ][ 'Std' ][ 'E_E' ] = numpy.std( resultDict['down'][ 'node' + str(i) ]['E_E'] )
            resultDict['down']['node' + str(i)]['Std']['FA_A'] = numpy.std(resultDict['down']['node' + str(i)]['FA_A'])
            resultDict['down']['node' + str(i)]['Std']['A_D'] = numpy.std(resultDict['down']['node' + str(i)]['A_D'])
            resultDict['down']['node' + str(i)]['Std']['D_G'] = numpy.std(resultDict['down']['node' + str(i)]['D_G'])

            main.log.report( "=====node{} Summary:=====".format( str(i) ) )
            main.log.report( "=============Switch up=======" )

            main.log.report(
                            "End to End average: {}".format( str(resultDict["up"][ 'node' + str(i) ][ 'Ave' ][ 'E_E' ]) ) )
            main.log.report(
                            "End to End Std: {}".format( str(resultDict["up"][ 'node' + str(i) ][ 'Std' ][ 'E_E' ]) ) )

            main.log.report(
                            "TCP to Feature average: {}".format( str(resultDict["up"][ 'node' + str(i) ][ 'Ave' ][ 'T_F' ]) ) )
            main.log.report(
                            "TCP to Feature Std: {}".format( str(resultDict["up"][ 'node' + str(i) ][ 'Std' ][ 'T_F' ]) ) )

            main.log.report(
                            "Feature to Role average: {}".format( str(resultDict["up"][ 'node' + str(i) ][ 'Ave' ][ 'F_R' ]) ) )
            main.log.report(
                            "Feature to Role Std: {}".format( str(resultDict["up"][ 'node' + str(i) ][ 'Std' ][ 'F_R' ]) ) )

            main.log.report(
                            "Role request to Role reply average: {}".format( str(resultDict["up"][ 'node' + str(i) ][ 'Ave' ][ 'RQ_RR' ]) ) )
            main.log.report(
                            "Role request to Role reply Std: {}".format( str(resultDict["up"][ 'node' + str(i) ][ 'Std' ][ 'RQ_RR' ]) ) )

            main.log.report(
                            "Role reply to Device average: {}".format( str(resultDict["up"][ 'node' + str(i) ][ 'Ave' ][ 'RR_D' ]) ) )
            main.log.report(
                            "Role reply to Device Std: {}".format( str(resultDict["up"][ 'node' + str(i) ][ 'Std' ][ 'RR_D' ]) ) )

            main.log.report(
                            "Device to Graph average: {}".format( str(resultDict["up"][ 'node' + str(i) ][ 'Ave' ][ 'D_G' ]) ) )
            main.log.report(
                            "Device to Graph Std: {}".format( str(resultDict["up"][ 'node' + str(i) ][ 'Std' ][ 'D_G' ]) ) )

            main.log.report( "=============Switch down=======" )

            main.log.report(
                            "End to End average: {}".format( str(resultDict["down"][ 'node' + str(i) ][ 'Ave' ][ 'E_E' ]) ) )
            main.log.report(
                            "End to End Std: {}".format( str(resultDict["down"][ 'node' + str(i) ][ 'Std' ][ 'E_E' ]) ) )

            main.log.report(
                            "Fin_ACK to ACK average: {}".format( str(resultDict["down"][ 'node' + str(i) ][ 'Ave' ][ 'FA_A' ]) ) )
            main.log.report(
                            "Fin_ACK to ACK Std: {}".format( str(resultDict["down"][ 'node' + str(i) ][ 'Std' ][ 'FA_A' ]) ) )

            main.log.report(
                            "ACK to Device average: {}".format( str(resultDict["down"][ 'node' + str(i) ][ 'Ave' ][ 'A_D' ]) ) )
            main.log.report(
                            "ACK to Device Std: {}".format( str(resultDict["down"][ 'node' + str(i) ][ 'Std' ][ 'A_D' ]) ) )

            main.log.report(
                            "Device to Graph average: {}".format( str(resultDict["down"][ 'node' + str(i) ][ 'Ave' ][ 'D_G' ]) ) )
            main.log.report(
                            "Device to Graph Std: {}".format( str(resultDict["down"][ 'node' + str(i) ][ 'Std' ][ 'D_G' ]) ) )

        with open(main.dbFileName, "a") as dbFile:
            # TODO: Save STD to Database
            # Scale number
            temp = str(main.numCtrls)
            temp += ",'baremetal1'"
            # put result
            temp += "," + str( "%.2f" % resultDict['up'][ 'node' + str(maxDict['up']['node']) ][ 'Ave' ][ 'E_E' ] )
            temp += "," + str( "%.2f" % resultDict['up'][ 'node' + str(maxDict['up']['node']) ][ 'Ave' ][ 'T_F' ] )
            temp += "," + str( "%.2f" % resultDict['up'][ 'node' + str(maxDict['up']['node']) ][ 'Ave' ][ 'F_R' ] )
            temp += "," + str( "%.2f" % resultDict['up'][ 'node' + str(maxDict['up']['node']) ][ 'Ave' ][ 'RQ_RR' ] )
            temp += "," + str( "%.2f" % resultDict['up'][ 'node' + str(maxDict['up']['node']) ][ 'Ave' ][ 'RR_D' ] )
            temp += "," + str( "%.2f" % resultDict['up'][ 'node' + str(maxDict['up']['node']) ][ 'Ave' ][ 'D_G' ] )

            temp += "," + str( "%.2f" % resultDict['down'][ 'node' + str(maxDict['down']['node']) ][ 'Ave' ][ 'E_E' ] )
            temp += "," + str( "%.2f" % resultDict['down'][ 'node' + str(maxDict['down']['node']) ][ 'Ave' ][ 'FA_A' ] )
            temp += "," + str( "%.2f" % resultDict['down'][ 'node' + str(maxDict['down']['node']) ][ 'Ave' ][ 'A_D' ] )
            temp += "," + str( "%.2f" % resultDict['down'][ 'node' + str(maxDict['down']['node']) ][ 'Ave' ][ 'D_G' ] )

            temp += "," + str( "%.2f" % resultDict['up'][ 'node' + str(maxDict['up']['node']) ][ 'Std' ][ 'E_E' ] )
            temp += "," + str( "%.2f" % resultDict['down'][ 'node' + str(maxDict['down']['node']) ][ 'Std' ][ 'E_E' ] )

            temp += "\n"
            dbFile.write( temp )
            dbFile.close()
