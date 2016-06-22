"""
    SCPFhostLat
    This test will test the host found latency.
    Host will arping a ip address, tshark will caputure the package time, then compare with the topology event timestamp.
    Test will run with 1 node from start, and scale up to 7 nodes.
    The event timestamp will only greb the latest one, then calculate average and standar dev.

    yunpeng@onlab.us
"""
class SCPFhostLat:

    def __init__( self ):
        self.default = ''

    def CASE0( self, main):
        import sys
        import json
        import time
        import os
        import imp

        main.case( "Constructing test variables and building ONOS package" )
        main.step( "Constructing test variables" )
        stepResult = main.FALSE

        # Test variables
        main.testOnDirectory = os.path.dirname( os.getcwd ( ) )
        main.cellName = main.params[ 'ENV' ][ 'cellName' ]
        main.apps = main.params[ 'ENV' ][ 'cellApps' ]
        main.scale = ( main.params[ 'SCALE' ] ).split( "," )
        main.ONOSport = main.params[ 'CTRL' ][ 'port' ]
        main.startUpSleep = int( main.params[ 'SLEEP' ][ 'startup' ] )
        main.installSleep = int( main.params[ 'SLEEP' ][ 'install' ] )
        main.measurementSleep = int( main.params['SLEEP']['measurement'])
        main.timeout = int( main.params['SLEEP']['timeout'] )
        main.dbFileName = main.params['DATABASE']['file']
        main.cellData = {} # for creating cell file

        # Tshark params
        main.tsharkResultPath = main.params['TSHARK']['tsharkPath']
        main.tsharkPacketIn = main.params['TSHARK']['tsharkPacketIn']

        main.numlter = main.params['TEST']['numIter']
        main.iterIgnore = int(main.params['TEST']['iterIgnore'])
        main.hostTimestampKey = main.params['TEST']['hostTimestamp']
        main.thresholdStr = main.params['TEST']['singleSwThreshold']
        main.thresholdObj = main.thresholdStr.split(',')
        main.thresholdMin = int(main.thresholdObj[0])
        main.thresholdMax = int(main.thresholdObj[1])
        main.threadID = 0

        main.CLIs = []
        main.ONOSip = []
        main.maxNumBatch = 0
        main.ONOSip = main.ONOSbench.getOnosIps()
        main.log.info(main.ONOSip)
        main.setupSkipped = False

        gitBranch = main.params[ 'GIT' ][ 'branch' ]
        gitPull = main.params[ 'GIT' ][ 'pull' ]
        nic = main.params['DATABASE']['nic']
        node = main.params['DATABASE']['node']
        nic = main.params['DATABASE']['nic']
        node = main.params['DATABASE']['node']
        stepResult = main.TRUE

        main.log.info("Cresting DB file")
        with open(main.dbFileName, "w+") as dbFile:
            dbFile.write("")

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="environment set up successfull",
                                 onfail="environment set up Failed" )

    def CASE1( self ):
        # main.scale[ 0 ] determines the current number of ONOS controller
        main.CLIs = []
        main.numCtrls = int( main.scale[ 0 ] )
        main.log.info( "Creating list of ONOS cli handles" )
        for i in range(main.numCtrls):
            main.CLIs.append( getattr( main, 'ONOScli%s' % (i+1) ) )

        main.log.info(main.CLIs)
        if not main.CLIs:
            main.log.error( "Failed to create the list of ONOS cli handles" )
            main.cleanup()
            main.exit()

        main.commit = main.ONOSbench.getVersion(report=True)
        main.commit = main.commit.split(" ")[1]

        if gitPull == 'True':
            if not main.startUp.onosBuild( main, gitBranch ):
                main.log.error( "Failed to build ONOS" )
                main.cleanup()
                main.exit()
        else:
            main.log.warn( "Did not pull new code so skipping mvn " +
                           "clean install" )
        with open(main.dbFileName, "a") as dbFile:
            temp = "'" + main.commit + "',"
            temp += "'" + nic + "',"
            dbFile.write(temp)
            dbFile.close()

    def CASE2( self, main ):
        """
        - Uninstall ONOS cluster
        - Verify ONOS start up
        - Install ONOS cluster
        - Connect to cli
        """
        main.log.info( "Starting up %s node(s) ONOS cluster" % main.numCtrls)
        main.log.info( "Safety check, killing all ONOS processes" +
                       " before initiating environment setup" )

        for i in range( main.numCtrls ):
            main.ONOSbench.onosDie( main.ONOSip[ i ] )

        main.log.info( "NODE COUNT = %s" % main.numCtrls)

        tempOnosIp = []
        for i in range( main.numCtrls ):
            tempOnosIp.append( main.ONOSip[i] )

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

        main.step( "Uninstall ONOS package on all Nodes" )
        uninstallResult = main.TRUE
        for i in range( int( main.numCtrls ) ):
            main.log.info( "Uninstalling package on ONOS Node IP: " + main.ONOSip[i] )
            u_result = main.ONOSbench.onosUninstall( main.ONOSip[i] )
            utilities.assert_equals( expect=main.TRUE, actual=u_result,
                                     onpass="Test step PASS",
                                     onfail="Test step FAIL" )
            uninstallResult = ( uninstallResult and u_result )

        main.step( "Install ONOS package on all Nodes" )
        installResult = main.TRUE
        for i in range( int( main.numCtrls ) ):
            main.log.info( "Installing package on ONOS Node IP: " + main.ONOSip[i] )
            i_result = main.ONOSbench.onosInstall( node=main.ONOSip[i] )
            utilities.assert_equals( expect=main.TRUE, actual=i_result,
                                     onpass="Test step PASS",
                                     onfail="Test step FAIL" )
            installResult = installResult and i_result
        time.sleep( main.startUpSleep )
        main.step( "Verify ONOS nodes UP status" )
        statusResult = main.TRUE
        for i in range( int( main.numCtrls ) ):
            main.log.info( "ONOS Node " + main.ONOSip[i] + " status:" )
            onos_status = main.ONOSbench.onosStatus( node=main.ONOSip[i] )
            utilities.assert_equals( expect=main.TRUE, actual=onos_status,
                                     onpass="Test step PASS",
                                     onfail="Test step FAIL" )
            statusResult = ( statusResult and onos_status )

        main.step( "Start ONOS CLI on all nodes" )
        cliResult = main.TRUE
        main.step(" Start ONOS cli using thread ")
        time.sleep( main.startUpSleep )
        startCliResult  = main.TRUE
        pool = []

        for i in range( int( main.numCtrls) ):
            t = main.Thread( target=main.CLIs[i].startOnosCli,
                             threadID=main.threadID,
                             name="startOnosCli",
                             args=[ main.ONOSip[i] ],
                             kwargs = {"onosStartTimeout":main.timeout} )
            pool.append(t)
            t.start()
            main.threadID = main.threadID + 1
        for t in pool:
            t.join()
            startCliResult = startCliResult and t.result
        time.sleep( main.startUpSleep )

    def CASE11( self, main ):
        main.log.info( "set and configure Application" )
        import json
        import time
        time.sleep(main.startUpSleep)
        main.step( "Activating org.onosproject.proxyarp" )
        appStatus = utilities.retry( main.ONOSrest1.activateApp,
                                     main.FALSE,
                                     ['org.onosproject.proxyarp'],
                                     sleep=3,
                                     attempts=3 )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=appStatus,
                                 onpass="Successfully activated proxyarp",
                                 onfail="Failed to activated proxyarp")

        main.step( "Set up Default Topology Provider" )
        appStatus = main.TRUE
        configName = 'org.onosproject.net.topology.impl.DefaultTopologyProvider'
        configParam = 'maxEvents'
        appStatus = appStatus and main.CLIs[0].setCfg(  configName, configParam,'1' )
        configParam = 'maxBatchMs'
        appStatus = appStatus and main.CLIs[0].setCfg( configName, configParam, '0')
        configParam = 'maxIdleMs'
        appStatus = appStatus and main.CLIs[0].setCfg( configName, configParam,'0' )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=appStatus,
                                 onpass="Successfully set DefaultTopologyProvider",
                                 onfail="Failed to set DefaultTopologyProvider" )

        time.sleep(main.startUpSleep)
        main.step('Starting mininet topology')
        mnStatus = main.Mininet1.startNet(args='--topo=linear,1')
        utilities.assert_equals( expect=main.TRUE,
                                 actual=mnStatus,
                                 onpass="Successfully started Mininet",
                                 onfail="Failed to activate Mininet" )
        main.step("Assinging masters to switches")
        switches = main.Mininet1.getSwitches()
        swStatus = main.Mininet1.assignSwController( sw=switches.keys(), ip=main.ONOSip[0] )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=swStatus,
                                 onpass="Successfully assigned switches to masters",
                                 onfail="Failed assign switches to masters" )

        time.sleep(main.startUpSleep)

    def CASE20(self, main):
        """
        host1 send arping package and measure latency

        There are only 1 levels of latency measurements to this test:
        1 ) ARPING-to-device measurement: Measurement the time from host1
        send apring package to onos processing the host event

        """
        import time
        import subprocess
        import json
        import requests
        import os
        import numpy

        # Host adding measurement
        assertion = main.TRUE

        main.log.report('Latency of adding one host to ONOS')
        main.log.report('First ' + str(main.iterIgnore) + ' iterations ignored' + ' for jvm warmup time')
        main.log.report('Total iterations of test: ' + str(main.numlter))

        addingHostTime = []
        metricsResultList = []
        for i in range(0, int(main.numlter)):
            main.log.info('Clean up data file')
            with open(main.tsharkResultPath, "w") as dbFile:
                dbFile.write("")

            main.log.info('Starting tshark capture')
            main.ONOSbench.tsharkGrep(main.tsharkPacketIn, main.tsharkResultPath)
            time.sleep(main.measurementSleep)

            main.log.info('host 1 arping...')
            main.Mininet1.arping(srcHost='h1', dstHost='10.0.0.2')

            time.sleep(main.measurementSleep)

            main.log.info('Stopping all Tshark processes')
            main.ONOSbench.tsharkStop()

            time.sleep(main.measurementSleep)

            # Get tshark output
            with open(main.tsharkResultPath, "r") as resultFile:
                resultText = resultFile.readline()
                main.log.info('Capture result:' + resultText)
                resultText = resultText.split(' ')
                if len(resultText) > 1:
                    tsharkResultTime = float(resultText[1]) * 1000.0
                else:
                    main.log.error('Tshark output file for packet_in' + ' returned unexpected results')
                    hostTime = 0
                    caseResult = main.FALSE
                resultFile.close()
            # Compare the timestemps, and get the lowest one.
            temp = 0;
            # Get host event timestamps from each nodes
            for node in range (0, main.numCtrls):
                metricsResult = json.loads(main.CLIs[node].topologyEventsMetrics())
                metricsResult = metricsResult.get(main.hostTimestampKey).get("value")
                main.log.info("ONOS topology event matrics timestemp: {}".format(str(metricsResult)) )

                if temp < metricsResult:
                    temp = metricsResult
                metricsResult = temp

            addingHostTime.append(float(metricsResult) - tsharkResultTime)
            main.log.info("Result of this iteration: {}".format( str( float(metricsResult) - tsharkResultTime) ))
            # gethost to remove
            gethost = main.ONOSrest1.hosts()
            HosttoRemove = []
            HosttoRemove.append( json.loads( gethost[1:len(gethost)-1] ).get('id') )
            main.CLIs[0].removeHost(HosttoRemove)

        main.log.info("Result List: {}".format(addingHostTime))

        # calculate average latency from each nodes
        averageResult = numpy.average(addingHostTime)
        main.log.info("Average Latency: {}".format(averageResult))

        # calculate std
        stdResult = numpy.std(addingHostTime)
        main.log.info("std: {}".format(stdResult))

        # write to DB file
        main.log.info("Writing results to DS file")
        with open(main.dbFileName, "a") as dbFile:
            # Scale number
            temp = str(main.numCtrls)
            temp += ",'" + "baremetal1" + "'"
            # average latency
            temp += "," + str( averageResult )
            # std of latency
            temp += "," + str(stdResult)
            temp += "\n"
            dbFile.write( temp )

        assertion = main.TRUE

        utilities.assert_equals(expect=main.TRUE, actual=assertion,
                onpass='Host latency test successful',
                onfail='Host latency test failed')

        main.Mininet1.stopNet()
        del main.scale[0]
