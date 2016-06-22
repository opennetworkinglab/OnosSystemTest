# SCPFintentRerouteLat
"""
SCPFintentRerouteLat
    - Test Intent Reroute Latency
    - Test Algorithm:
        1. Start Null Provider reroute Topology
        2. Using Push-test-intents to push batch size intents from switch 1 to switch 7
        3. Cut the link between switch 3 and switch 4 (the path will reroute to switch 8)
        4. Get the topology time stamp
        5. Get Intent reroute(Installed) time stamp from each nodes
        6. Use the latest intent time stamp subtract topology time stamp
    - This test will run 5 warm up by default, warm up iteration can be setup in Param file
    - The intent batch size will default set to 1, 100, and 1000, also can be set in Param file
    - The unit of the latency result is milliseconds
"""

class SCPFintentRerouteLat:
    def __init__(self):
        self.default = ''

    def CASE0( self, main ):
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

        main.case("Pull onos branch and build onos on Teststation.")

        if gitPull == 'True':
            main.step("Git Checkout ONOS branch: " + gitBranch)
            stepResult = main.ONOSbench.gitCheckout(branch=gitBranch)
            utilities.assert_equals(expect=main.TRUE,
                                    actual=stepResult,
                                    onpass="Successfully checkout onos branch.",
                                    onfail="Failed to checkout onos branch. Exiting test...")
            if not stepResult: main.exit()

            main.step("Git Pull on ONOS branch:" + gitBranch)
            stepResult = main.ONOSbench.gitPull()
            utilities.assert_equals(expect=main.TRUE,
                                    actual=stepResult,
                                    onpass="Successfully pull onos. ",
                                    onfail="Failed to pull onos. Exiting test ...")
            if not stepResult: main.exit()

            main.step("Building ONOS branch: " + gitBranch)
            stepResult = main.ONOSbench.cleanInstall(skipTest=True)
            utilities.assert_equals(expect=main.TRUE,
                                    actual=stepResult,
                                    onpass="Successfully build onos.",
                                    onfail="Failed to build onos. Exiting test...")
            if not stepResult: main.exit()

        else:
            main.log.warn("Skipped pulling onos and Skipped building ONOS")

        main.apps = main.params['ENV']['cellApps']
        main.BENCHUser = main.params['BENCH']['user']
        main.BENCHIp = main.params['BENCH']['ip1']
        main.MN1Ip = main.params['MN']['ip1']
        main.maxNodes = int(main.params['max'])
        main.skipMvn = main.params['TEST']['skipCleanInstall']
        main.cellName = main.params['ENV']['cellName']
        main.scale = (main.params['SCALE']).split(",")
        main.dbFileName = main.params['DATABASE']['file']
        main.timeout = int(main.params['SLEEP']['timeout'])
        main.startUpSleep = int(main.params['SLEEP']['startup'])
        main.installSleep = int(main.params['SLEEP']['install'])
        main.verifySleep = int(main.params['SLEEP']['verify'])
        main.setMasterSleep = int(main.params['SLEEP']['setmaster'])
        main.verifyAttempts = int(main.params['ATTEMPTS']['verify'])
        main.sampleSize = int(main.params['TEST']['sampleSize'])
        main.warmUp = int(main.params['TEST']['warmUp'])
        main.intentsList = (main.params['TEST']['intents']).split(",")
        main.ingress = main.params['TEST']['ingress']
        main.egress = main.params['TEST']['egress']
        main.debug = main.params['TEST']['debug']
        for i in range(0, len(main.intentsList)):
            main.intentsList[i] = int(main.intentsList[i])
            # Create DataBase file
        main.log.info("Create Database file " + main.dbFileName)
        resultsDB = open(main.dbFileName, "w+")
        resultsDB.close()

    def CASE1( self, main ):
        '''
            clean up test environment and set up
        '''
        import time

        main.log.info("Get ONOS cluster IP")
        print(main.scale)
        main.numCtrls = int(main.scale[0])
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
            main.ONOSbench.onosDie(main.ONOSip[i])

        main.log.info("NODE COUNT = %s" % main.numCtrls)
        main.ONOSbench.createCellFile(main.ONOSbench.ip_address,
                                      main.cellName,
                                      main.MN1Ip,
                                      main.apps,
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
        packageResult = main.ONOSbench.onosPackage()
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

        main.step("Verify ONOS nodes UP status")
        statusResult = main.TRUE
        for i in range(int(main.numCtrls)):
            main.log.info("ONOS Node " + main.ONOSip[i] + " status:")
            onos_status = main.ONOSbench.onosStatus(node=main.ONOSip[i])
            utilities.assert_equals(expect=main.TRUE, actual=onos_status,
                                    onpass="Test step PASS",
                                    onfail="Test step FAIL")
            statusResult = (statusResult and onos_status)
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

        # configure apps
        main.CLIs[0].setCfg("org.onosproject.provider.nil.NullProviders", "deviceCount", value=8)
        main.CLIs[0].setCfg("org.onosproject.provider.nil.NullProviders", "topoShape", value="reroute")
        main.CLIs[0].setCfg("org.onosproject.provider.nil.NullProviders", "enabled", value="true")
        main.CLIs[0].setCfg("org.onosproject.store.flow.impl.DistributedFlowRuleStore", "backupEnabled", value="false")

        time.sleep(main.startUpSleep)

        # Balance Master
        main.CLIs[0].balanceMasters()
        if len(main.ONOSip) > 1:
            main.CLIs[0].deviceRole("null:0000000000000003", main.ONOSip[0])
            main.CLIs[0].deviceRole("null:0000000000000004", main.ONOSip[0])
        time.sleep( main.setMasterSleep )

    def CASE2( self, main ):
        import time
        import numpy
        import datetime
        import json
        # from scipy import stats

        ts = time.time()
        print(main.intentsList)
        for batchSize in main.intentsList:
            main.log.report("Intent Batch size: " + str(batchSize) + "\n      ")
            main.LatencyList = []
            validRun = 0
            invalidRun = 0
            while validRun <= main.warmUp + main.sampleSize and invalidRun <= 20:
                if validRun >= main.warmUp:
                    main.log.info("================================================")
                    main.log.info("Starting test iteration: {} ".format(validRun - main.warmUp))
                    main.log.info("Total iteration: {}".format(validRun + invalidRun))
                    main.log.info("================================================")
                else:
                    main.log.info("====================Warm Up=====================")

                # push intents
                main.CLIs[0].pushTestIntents(main.ingress, main.egress, batchSize,
                                             offset=1, options="-i", timeout=main.timeout)

                # check links and flows
                k = 0
                verify = main.FALSE
                linkCheck = 0
                flowsCheck = 0
                while k <= main.verifyAttempts:
                    time.sleep(main.verifySleep)
                    summary = json.loads(main.CLIs[0].summary(timeout=main.timeout))
                    linkCheck = summary.get("links")
                    flowsCheck = summary.get("flows")
                    if linkCheck == 16 and flowsCheck == batchSize * 7:
                        main.log.info("links: {}, flows: {} ".format(linkCheck, flowsCheck))
                        verify = main.TRUE
                        break
                    k += 1
                if not verify:
                    main.log.warn("Links or flows number are not match!")
                    main.log.warn("links: {}, flows: {} ".format(linkCheck, flowsCheck))
                    # bring back topology
                    main.CLIs[0].removeAllIntents(purge=True, sync=True, timeout=main.timeout)
                    time.sleep(1)
                    main.CLIs[0].purgeWithdrawnIntents()
                    main.CLIs[0].setCfg("org.onosproject.provider.nil.NullProviders", "deviceCount", value=0)
                    main.CLIs[0].setCfg("org.onosproject.provider.nil.NullProviders", "enabled", value="false")
                    main.CLIs[0].setCfg("org.onosproject.provider.nil.NullProviders", "deviceCount", value=8)
                    main.CLIs[0].setCfg("org.onosproject.provider.nil.NullProviders", "enabled", value="true")
                    if validRun >= main.warmUp:
                        invalidRun += 1
                        continue
                    else:
                        validRun += 1
                        continue

                # Bring link down
                main.CLIs[0].link("0000000000000004/1", "0000000000000003/2", "down",
                                  timeout=main.timeout, showResponse=False)
                verify = main.FALSE
                k = 0
                topoManagerLog = ""
                while k <= main.verifyAttempts:
                    time.sleep(main.verifySleep)
                    summary = json.loads(main.CLIs[0].summary(timeout=main.timeout))
                    linkCheck = summary.get("links")
                    flowsCheck = summary.get("flows")
                    if linkCheck == 14:
                        main.log.info("links: {}, flows: {} ".format(linkCheck, flowsCheck))
                        verify = main.TRUE
                        break
                    k += 1
                if not verify:
                    main.log.warn("Links number are not match in TopologyManager log!")
                    main.log.warn(topoManagerLog)
                    # bring back topology
                    main.CLIs[0].removeAllIntents(purge=True, sync=True, timeout=main.timeout)
                    time.sleep(1)
                    main.CLIs[0].purgeWithdrawnIntents()
                    main.CLIs[0].setCfg("org.onosproject.provider.nil.NullProviders", "deviceCount", value=0)
                    main.CLIs[0].setCfg("org.onosproject.provider.nil.NullProviders", "enabled", value="false")
                    main.CLIs[0].setCfg("org.onosproject.provider.nil.NullProviders", "deviceCount", value=8)
                    main.CLIs[0].setCfg("org.onosproject.provider.nil.NullProviders", "enabled", value="true")
                    if validRun >= main.warmUp:
                        invalidRun += 1
                        continue
                    else:
                        validRun += 1
                        continue

                try:
                    # expect twice to clean the pexpect buffer
                    main.ONOSbench.handle.sendline("")
                    main.ONOSbench.handle.expect("\$")
                    main.ONOSbench.handle.expect("\$")
                    # send line by using bench, can't use driver because pexpect buffer problem
                    cmd = "onos-ssh $OC1 cat /opt/onos/log/karaf.log | grep TopologyManager| tail -1"
                    main.ONOSbench.handle.sendline(cmd)
                    time.sleep(1)
                    main.ONOSbench.handle.expect(":~")
                    topoManagerLog = main.ONOSbench.handle.before
                    topoManagerLogTemp = topoManagerLog.splitlines()
                    # To make sure we get correct topology log
                    for lines in topoManagerLogTemp:
                        if "creationTime" in lines:
                            topoManagerLog = lines
                    main.log.info("Topology Manager log:")
                    print(topoManagerLog)
                    cutTimestamp = float(topoManagerLog.split("creationTime=")[1].split(",")[0])
                except:
                    main.log.error("Topology Log is not correct!")
                    print(topoManagerLog)
                    # bring back topology
                    verify = main.FALSE
                    main.CLIs[0].removeAllIntents(purge=True, sync=True, timeout=main.timeout)
                    time.sleep(1)
                    main.CLIs[0].purgeWithdrawnIntents()
                    main.CLIs[0].setCfg("org.onosproject.provider.nil.NullProviders", "deviceCount", value=0)
                    main.CLIs[0].setCfg("org.onosproject.provider.nil.NullProviders", "enabled", value="false")
                    main.CLIs[0].setCfg("org.onosproject.provider.nil.NullProviders", "deviceCount", value=8)
                    main.CLIs[0].setCfg("org.onosproject.provider.nil.NullProviders", "enabled", value="true")
                    if validRun >= main.warmUp:
                        invalidRun += 1
                    else:
                        validRun += 1
                    # If we got wrong Topology log, we should skip this iteration, and continue for next one
                    continue

                installedTemp = []
                time.sleep(1)
                for cli in main.CLIs:
                    tempJson = json.loads(cli.intentsEventsMetrics())
                    Installedtime = tempJson.get('intentInstalledTimestamp').get('value')
                    installedTemp.append(float(Installedtime))
                for i in range(0, len(installedTemp)):
                    main.log.info("ONOS Node {} Installed Time stemp: {}".format((i + 1), installedTemp[i]))
                maxInstallTime = float(max(installedTemp))
                if validRun >= main.warmUp and verify:
                    main.log.info("Installed time stemp: {0:f}".format(maxInstallTime))
                    main.log.info("CutTimestamp: {0:f}".format(cutTimestamp))
                    # Both timeStemps are milliseconds
                    main.log.info("Latency: {0:f}".format(float(maxInstallTime - cutTimestamp)))
                    main.LatencyList.append(float(maxInstallTime - cutTimestamp))
                # We get valid latency, validRun + 1
                validRun += 1

                # Verify Summary after we bring up link, and withdrawn intents
                main.CLIs[0].link("0000000000000004/1", "0000000000000003/2", "up",
                                  timeout=main.timeout)
                k = 0
                verify = main.FALSE
                linkCheck = 0
                flowsCheck = 0
                while k <= main.verifyAttempts:
                    time.sleep(main.verifySleep)
                    main.CLIs[0].removeAllIntents(purge=True, sync=True, timeout=main.timeout)
                    time.sleep(1)
                    main.CLIs[0].purgeWithdrawnIntents()
                    summary = json.loads(main.CLIs[0].summary())
                    linkCheck = summary.get("links")
                    flowsCheck = summary.get("flows")
                    intentCheck = summary.get("intents")
                    if linkCheck == 16 and flowsCheck == 0 and intentCheck == 0:
                        main.log.info("links: {}, flows: {}, intents: {} ".format(linkCheck, flowsCheck, intentCheck))
                        verify = main.TRUE
                        break
                    k += 1
                if not verify:
                    main.log.error("links, flows, or intents are not correct!")
                    main.log.info("links: {}, flows: {}, intents: {} ".format(linkCheck, flowsCheck, intentCheck))
                    # bring back topology
                    main.log.info("Bring back topology...")
                    main.CLIs[0].removeAllIntents(purge=True, sync=True, timeout=main.timeout)
                    time.sleep(1)
                    main.CLIs[0].purgeWithdrawnIntents()
                    main.CLIs[0].setCfg("org.onosproject.provider.nil.NullProviders", "deviceCount", value=0)
                    main.CLIs[0].setCfg("org.onosproject.provider.nil.NullProviders", "enabled", value="false")
                    main.CLIs[0].setCfg("org.onosproject.provider.nil.NullProviders", "deviceCount", value=8)
                    main.CLIs[0].setCfg("org.onosproject.provider.nil.NullProviders", "enabled", value="true")
                    continue

            aveLatency = 0
            stdLatency = 0
            aveLatency = numpy.average(main.LatencyList)
            stdLatency = numpy.std(main.LatencyList)
            main.log.report("Scale: " + str(main.numCtrls) + "  \tIntent batch: " + str(batchSize))
            main.log.report("Latency average:................" + str(aveLatency))
            main.log.report("Latency standard deviation:....." + str(stdLatency))
            main.log.report("________________________________________________________")

            if not (numpy.isnan(aveLatency) or numpy.isnan(stdLatency)):
                # check if got NaN for result
                resultsDB = open(main.dbFileName, "a")
                resultsDB.write("'" + main.commit + "',")
                resultsDB.write(str(main.numCtrls) + ",")
                resultsDB.write(str(batchSize) + ",")
                resultsDB.write(str(aveLatency) + ",")
                resultsDB.write(str(stdLatency) + "\n")
                resultsDB.close()
        del main.scale[0]
