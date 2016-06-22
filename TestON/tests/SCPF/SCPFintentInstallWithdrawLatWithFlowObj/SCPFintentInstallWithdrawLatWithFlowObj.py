"""
SCPFintentInstallWithdrawLatWithFlowObj:
    - Test the latency of intent installed and withdrawn
    - Use Push-test-intents command to push intents
    - Use Null provider with 7 devices and linear topology
    - Always push intents between 1/6 and 7/5
    - The batch size is defined in parm file. (default 1,100)
    - org.onosproject.net.intent.impl.compiler.IntentConfigurableRegistrator useFlowObjectives set
     to true
    yunpeng@onlab.us
"""

import sys
import os.path


class SCPFintentInstallWithdrawLatWithFlowObj:
    def __init__( self ):
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
        main.cellName = main.params['ENV']['cellName']
        main.scale = (main.params['SCALE']).split(",")
        main.dbFileName = main.params['DATABASE']['file']
        main.timeout = int(main.params['SLEEP']['timeout'])
        main.startUpSleep = int(main.params['SLEEP']['startup'])
        main.installSleep = int(main.params['SLEEP']['install'])
        main.verifySleep = int(main.params['SLEEP']['verify'])
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
        # Clean up test environment and set up
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
        main.CLIs[0].setCfg("org.onosproject.provider.nil.NullProviders", "deviceCount", value=7)
        main.CLIs[0].setCfg("org.onosproject.provider.nil.NullProviders", "topoShape", value="linear")
        main.CLIs[0].setCfg("org.onosproject.provider.nil.NullProviders", "enabled", value="true")
        main.CLIs[0].setCfg("org.onosproject.net.intent.impl.IntentManager",
        "skipReleaseResourcesOnWithdrawal", value="true")
        main.CLIs[0].setCfg("org.onosproject.net.intent.impl.compiler.IntentConfigurableRegistrator",
                            "useFlowObjectives", value="true")
        time.sleep(main.startUpSleep)

        # balanceMasters
        main.CLIs[0].balanceMasters()
        time.sleep(main.startUpSleep)

    def CASE2( self, main ):
        import time
        import numpy
        import json
        print(main.intentsList)
        for batchSize in main.intentsList:
            main.log.report("Intent Batch size: {}".format(batchSize))
            main.installLatList = []
            main.withdrawLatList = []
            validrun = 0
            invalidrun = 0
            # we use two variables to control the iteration
            while validrun <= main.warmUp + main.sampleSize and invalidrun < 20:
                if validrun >= main.warmUp:
                    main.log.info("================================================")
                    main.log.info("Starting test iteration " + str(validrun - main.warmUp))
                    main.log.info("Total test iteration: " + str(invalidrun + validrun))
                    main.log.info("================================================")
                else:
                    main.log.info("====================Warm Up=====================")

                # push intents
                installResult = main.CLIs[0].pushTestIntents(main.ingress, main.egress, batchSize,
                                                             offset=1, options="-i", timeout=main.timeout,
                                                             getResponse=True)
                if type(installResult) is str:
                    if "Failure" in installResult:
                        main.log.error("Install Intents failure, ignore this iteration.")
                        if validrun < main.warmUp:
                            validrun += 1
                            continue
                        else:
                            invalidrun += 1
                            continue

                    try:
                        latency = int(installResult.split()[5])
                        main.log.info(installResult)
                    except:
                        main.log.error("Failed to get latency, ignore this iteration.")
                        main.log.error("Response from ONOS:")
                        print(installResult)
                        if validrun < main.warmUp:
                            validrun += 1
                            continue
                        else:
                            invalidrun += 1
                            continue

                    if validrun >= main.warmUp:
                        main.installLatList.append(latency)
                else:
                    invalidrun += 1
                    continue
                time.sleep(2)
                # Withdraw Intents
                withdrawResult = main.CLIs[0].pushTestIntents(main.ingress, main.egress, batchSize,
                                                              offset=1, options="-w", timeout=main.timeout,
                                                              getResponse=True)

                if type(withdrawResult) is str:
                    if "Failure" in withdrawResult:
                        main.log.error("withdraw Intents failure, ignore this iteration.")
                        if validrun < main.warmUp:
                            validrun += 1
                            continue
                        else:
                            invalidrun += 1
                            continue

                    try:
                        latency = int(withdrawResult.split()[5])
                        main.log.info(withdrawResult)
                    except:
                        main.log.error("Failed to get latency, ignore this iteration.")
                        main.log.error("Response from ONOS:")
                        print(withdrawResult)
                        if validrun < main.warmUp:
                            validrun += 1
                            continue
                        else:
                            invalidrun += 1
                            continue

                    if validrun >= main.warmUp:
                        main.withdrawLatList.append(latency)
                else:
                    invalidrun += 1
                    continue
                time.sleep(2)
                main.CLIs[0].purgeWithdrawnIntents()
                validrun += 1
            installave = numpy.average(main.installLatList)
            installstd = numpy.std(main.installLatList)
            withdrawave = numpy.average(main.withdrawLatList)
            withdrawstd = numpy.std(main.withdrawLatList)
            # log report
            main.log.report("----------------------------------------------------")
            main.log.report("Scale: " + str(main.numCtrls))
            main.log.report("Intent batch: " + str(batchSize))
            main.log.report("Install average: {}    std: {}".format(installave, installstd))
            main.log.report("Withdraw average: {}   std: {}".format(withdrawave, withdrawstd))
            # write result to database file
            if not (numpy.isnan(installave) or numpy.isnan(installstd) or \
                    numpy.isnan(withdrawstd) or numpy.isnan(withdrawave)):
                databaseString = "'" + main.commit + "',"
                databaseString += str(main.numCtrls) + ","
                databaseString += str(batchSize) + ","
                databaseString += str(installave) + ","
                databaseString += str(installstd) + ","
                databaseString += str(withdrawave) + ","
                databaseString += str(withdrawstd) + "\n"
                resultsDB = open(main.dbFileName, "a")
                resultsDB.write(databaseString)
                resultsDB.close()
        del main.scale[0]
