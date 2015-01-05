import time
import sys
import os
import re
import time
import json
import itertools

class OnosCHO:
    def __init__(self):
        self.default = ''
        global deviceDPIDs
        global hostMACs
        global deviceLinks
        global deviceActiveLinksCount
        global devicePortsEnabledCount
        global installedIntents
        global randomLink1, randomLink2, randomLink3, numSwitches, numLinks
    def CASE1(self, main):
        '''
        Startup sequence:
        git pull
        mvn clean install
        onos-package
        cell <name>
        onos-verify-cell
        onos-install -f
        onos-wait-for-start
        '''
        import time
        cell_name = main.params['ENV']['cellName']
        git_pull = main.params['GIT']['autoPull']
        numCtrls = main.params['CTRL']['numCtrl']
        git_branch = main.params['GIT']['branch']

        main.case("Set up test environment")
        main.log.report("Set up test environment")
        main.log.report("_______________________")
                
        main.step("Git checkout and pull "+git_branch)
        if git_pull == 'on':
            checkout_result = main.ONOSbench.git_checkout(git_branch)
            pull_result = main.ONOSbench.git_pull()
            cp_result = (checkout_result and pull_result)
        else:
            checkout_result = main.TRUE
            pull_result = main.TRUE
            main.log.info("Skipped git checkout and pull")
            cp_result = (checkout_result and pull_result)
        utilities.assert_equals(expect=main.TRUE, actual=cp_result,
                onpass="Test step PASS",
                onfail="Test step FAIL")
		
        main.step("mvn clean & install")
        mvn_result = main.ONOSbench.clean_install()
        utilities.assert_equals(expect=main.TRUE, actual=mvn_result,
                onpass="Test step PASS",
                onfail="Test step FAIL")

        main.ONOSbench.get_version(report=True)

        main.step("Apply Cell environment for ONOS")
        cell_result = main.ONOSbench.set_cell(cell_name)
        utilities.assert_equals(expect=main.TRUE, actual=cell_result,
                onpass="Test step PASS",
                onfail="Test step FAIL")

        main.step("Create ONOS package")
        packageResult = main.ONOSbench.onos_package()
        utilities.assert_equals(expect=main.TRUE, actual=packageResult,
                onpass="Test step PASS",
                onfail="Test step FAIL")

        main.step("Uninstall ONOS package on all Nodes")
        uninstallResult=main.TRUE
        for i in range(1,int(numCtrls)+1):
            ONOS_ip = main.params['CTRL']['ip'+str(i)]
            main.log.info("Unintsalling package on ONOS Node IP: "+ONOS_ip)
            u_result= main.ONOSbench.onos_uninstall(ONOS_ip)
            utilities.assert_equals(expect=main.TRUE, actual=u_result,
                onpass="Test step PASS",
                onfail="Test step FAIL")
            uninstallResult=(uninstallResult and u_result)

        main.step("Removing copy-cat logs from ONOS nodes")
        main.ONOSbench.onos_remove_raft_logs()

        main.step("Install ONOS package on all Nodes")
        installResult=main.TRUE
        for i in range(1,int(numCtrls)+1):
            ONOS_ip = main.params['CTRL']['ip'+str(i)]
            main.log.info("Intsalling package on ONOS Node IP: "+ONOS_ip)
            i_result= main.ONOSbench.onos_install(node=ONOS_ip)
            utilities.assert_equals(expect=main.TRUE, actual=i_result,
                onpass="Test step PASS",
                onfail="Test step FAIL")
            installResult=(installResult and i_result)

        main.step("Verify ONOS nodes UP status")
        statusResult=main.TRUE
        for i in range(1,int(numCtrls)+1):
            ONOS_ip = main.params['CTRL']['ip'+str(i)]
            main.log.info("ONOS Node "+ONOS_ip+" status:")
            onos_status = main.ONOSbench.onos_status(node=ONOS_ip)
            utilities.assert_equals(expect=main.TRUE, actual=onos_status,
                onpass="Test step PASS",
                onfail="Test step FAIL")
            statusResult=(statusResult and onos_status)   

        main.step("Start ONOS CLI on all nodes")
        cliResult = main.TRUE
        time.sleep(15) # need to wait here for sometime. This will be removed once ONOS is stable enough
        for i in range(1,int(numCtrls)+1):
            ONOS_ip = main.params['CTRL']['ip'+str(i)]
            ONOScli = 'ONOScli'+str(i)
            main.log.info("ONOS Node "+ONOS_ip+" cli start:")
            exec "startcli=main."+ONOScli+".start_onos_cli(ONOS_ip)"
            utilities.assert_equals(expect=main.TRUE, actual=startcli,
                onpass="Test step PASS",
                onfail="Test step FAIL")
            cliResult = (cliResult and startcli) 

        case1Result = (cp_result and cell_result 
                and packageResult and installResult and statusResult and cliResult)
        utilities.assert_equals(expect=main.TRUE, actual=case1Result,
                onpass="Set up test environment PASS",
                onfail="Set up test environment FAIL")

    def CASE2(self, main):
        ''' 
        This test script still needs more refactoring
        '''
        import re
        import time
        import copy
        numCtrls = main.params['CTRL']['numCtrl']
        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS2_ip = main.params['CTRL']['ip2']
        ONOS3_ip = main.params['CTRL']['ip3']
        ONOS4_ip = main.params['CTRL']['ip4']
        ONOS5_ip = main.params['CTRL']['ip5']
        ONOS1_port = main.params['CTRL']['port1']
        ONOS2_port = main.params['CTRL']['port2']
        ONOS3_port = main.params['CTRL']['port3']
        ONOS4_port = main.params['CTRL']['port4']
        ONOS5_port = main.params['CTRL']['port5']

        numCtrls = main.params['CTRL']['numCtrl']
        main.log.report("Assign and Balance all Mininet switches across controllers")
        main.log.report("_________________________________________________________")
        time.sleep(15) # need to wait here for sometime. This will be removed once ONOS is stable enough
        main.case("Assign and Balance all Mininet switches across controllers")
        main.step("Assign switches to controllers")
        for i in range(1,26): #1 to (num of switches +1)
            main.Mininet1.assign_sw_controller(sw=str(i),count=int(numCtrls), 
                    ip1=ONOS1_ip, port1=ONOS1_port,
                    ip2=ONOS2_ip, port2=ONOS2_port,
		            ip3=ONOS3_ip, port3=ONOS3_port, ip4=ONOS4_ip, port4=ONOS4_port, 
			    ip5=ONOS5_ip, port5=ONOS5_port)

        switch_mastership = main.TRUE
        for i in range (1,26):
            response = main.Mininet1.get_sw_controller("s"+str(i))
            print("Response is " + str(response))
            if re.search("tcp:"+ONOS1_ip,response):
                switch_mastership = switch_mastership and main.TRUE
            else:
                switch_mastership = main.FALSE

        if switch_mastership == main.TRUE:
            main.log.report("Controller assignment successfull")
        else:
             main.log.report("Controller assignment failed")
        time.sleep(5)

        main.step("Balance devices across controllers")
        for i in range(int(numCtrls)):
            balanceResult = main.ONOScli1.balance_masters()
            time.sleep(3) # giving some breathing time for ONOS to complete re-balance

        utilities.assert_equals(expect=main.TRUE, actual=balanceResult,
                onpass="Assign and Balance devices test PASS",
                onfail="Assign and Balance devices test FAIL")

    def CASE3(self,main) :
        ''' 
        This Test case will be extended to collect and store more data related
        ONOS state.
        '''
        import re
        import copy
        deviceDPIDs = []
        hostMACs = []
        deviceLinks = []
        deviceActiveLinksCount = []
        devicePortsEnabledCount = []

        main.log.report("Collect and Store topology details from ONOS before running any Tests")
        main.log.report("____________________________________________________________________")        
        main.case ("Collect and Store Topology Deatils from ONOS")

        main.step("Collect and store current number of switches and links")
        topology_output = main.ONOScli1.topology()
        topology_result = main.ONOSbench.get_topology(topology_output)
        numSwitches = topology_result['devices']
        numLinks = topology_result['links']
        main.log.info("Currently there are %s switches and %s links"  %(str(numSwitches), str(numLinks)))

        main.step("Store Device DPIDs")
        for i in range(1,26):
            deviceDPIDs.append("of:00000000000000"+format(i, '02x'))
        print "Device DPIDs in Store: \n", str(deviceDPIDs)

        main.step("Store Host MACs")
        for i in range(1,26):
            hostMACs.append("00:00:00:00:00:"+format(i, '02x')+"/-1")
        print "Host MACs in Store: \n", str(hostMACs)

        main.step("Collect and store all Devices Links")
        linksResult = main.ONOScli1.links(json_format=False)
        ansi_escape = re.compile(r'\x1b[^m]*m')
        linksResult = ansi_escape.sub('', linksResult)
        linksResult = linksResult.replace(" links","").replace("\r\r","")
        linksResult=linksResult.splitlines()
        linksResult = linksResult[1:]
        deviceLinks = copy.copy(linksResult)
        print "Device Links Stored: \n", str(deviceLinks)
        print "Length of Links Store", len(deviceLinks) # this will be asserted to check with the params provided count of links

        main.step("Collect and store each Device ports enabled Count")
        for i in range(1,26):
            portResult = main.ONOScli1.getDevicePortsEnabledCount("of:00000000000000"+format(i, '02x'))
            portTemp = re.split(r'\t+', portResult)
            portCount = portTemp[1].replace("\r\r\n\x1b[32m","")
            devicePortsEnabledCount.append(portCount)
        print "Device Enabled Port Counts Stored: \n", str(devicePortsEnabledCount)

        main.step("Collect and store each Device active links Count")
        for i in range(1,26):
            linkCountResult = main.ONOScli1.getDeviceLinksActiveCount("of:00000000000000"+format(i, '02x'))
            linkCountTemp = re.split(r'\t+', linkCountResult)
            linkCount = linkCountTemp[1].replace("\r\r\n\x1b[32m","")
            deviceActiveLinksCount.append(linkCount)
        print "Device Active Links Count Stored: \n", str(deviceActiveLinksCount)

        caseResult = main.TRUE  # just returning TRUE for now as this one just collects data
        utilities.assert_equals(expect=main.TRUE, actual=case1Result,
                onpass="Saving ONOS topology data test PASS",
                onfail="Saving ONOS topology data test FAIL")

    def CASE4(self,main) :
        ''' 
        Enable onos-app-fwd, Verify Reactive forwarding through ping all and Disable it 
        '''
        import re
        import copy
        import time
        numCtrls = main.params['CTRL']['numCtrl']
        main.log.report("Enable Reactive forwarding and Verify ping all")
        main.log.report("______________________________________________")        
        main.case ("Enable Reactive forwarding and Verify ping all")
        main.step("Enable Reactive forwarding")
        installResult = main.TRUE
        for i in range(1,int(numCtrls)+1):
            onosFeature = 'onos-app-fwd'
            ONOS_ip = main.params['CTRL']['ip'+str(i)]
            ONOScli = 'ONOScli'+str(i)
            main.log.info("Enabling Reactive mode on ONOS Node "+ONOS_ip)
            exec "inResult=main."+ONOScli+".feature_install(onosFeature)"
            installResult = inResult and installResult

        time.sleep(5)

        main.step("Verify Pingall")
        ping_result = main.FALSE
        time1 = time.time()
        ping_result = main.Mininet1.pingall()
        time2 = time.time()
        timeDiff = round((time2-time1),2)
        main.log.report("Time taken for Ping All: "+str(timeDiff)+" seconds")

        if ping_result == main.TRUE:
            main.log.report("Pingall Test in Reactive mode successful")
        else:
            main.log.report("Pingall Test in Reactive mode failed")

        main.step("Disable Reactive forwarding")
        uninstallResult = main.TRUE
        for i in range(1,int(numCtrls)+1):
            onosFeature = 'onos-app-fwd'
            ONOS_ip = main.params['CTRL']['ip'+str(i)]
            ONOScli = 'ONOScli'+str(i)
            main.log.info("Disabling Reactive mode on ONOS Node "+ONOS_ip)
            exec "unResult=main."+ONOScli+".feature_uninstall(onosFeature)"
            uninstallResult = unResult and uninstallResult

        #Waiting for reative flows to be cleared.
        time.sleep(10)

        case3Result = installResult and ping_result and uninstallResult
        utilities.assert_equals(expect=main.TRUE, actual=case3Result,
                onpass="Reactive Mode Pingall test PASS",
                onfail="Reactive Mode Pingall test FAIL")

    def CASE5(self,main) :
        '''
        Compare current ONOS topology with reference data
        '''  
        import re
        devicesDPID_tmp = []
        hostMACs_tmp = []
        deviceLinks_tmp = []
        deviceActiveLinksCount_tmp = []
        devicePortsEnabledCount_tmp = []

        main.log.report("Compare ONOS topology with reference data in Stores")
        main.log.report("__________________________________________________")        
        main.case ("Compare ONOS topology with reference data")
	     
        main.step("Compare current Device ports enabled with reference")
        for i in range(1,26):
            portResult = main.ONOScli1.getDevicePortsEnabledCount("of:00000000000000"+format(i, '02x'))
            portTemp = re.split(r'\t+', portResult)
            portCount = portTemp[1].replace("\r\r\n\x1b[32m","")
            devicePortsEnabledCount_tmp.append(portCount)
            time.sleep(2)
        print ("Device Enabled ports EXPECTED: \n"+ str(devicePortsEnabledCount))
        print ("Device Enabled ports ACTUAL: \n"+ str(devicePortsEnabledCount_tmp))
        if (cmp(devicePortsEnabledCount,devicePortsEnabledCount_tmp)==0):
            stepResult1 = main.TRUE
        else:
            stepResult1 = main.FALSE

        main.step("Compare Device active links with reference")
        for i in range(1,26):
            linkResult = main.ONOScli1.getDeviceLinksActiveCount("of:00000000000000"+format(i, '02x'))
            linkTemp = re.split(r'\t+', linkResult)
            linkCount = linkTemp[1].replace("\r\r\n\x1b[32m","")
            deviceActiveLinksCount_tmp.append(linkCount)
            time.sleep(3)
        print ("Device Active links EXPECTED: \n"+str(deviceActiveLinksCount))
        print ("Device Active links ACTUAL: \n"+str(deviceActiveLinksCount_tmp))
        if (cmp(deviceActiveLinksCount,deviceActiveLinksCount_tmp)==0):
            stepResult2 = main.TRUE
        else:
            stepResult2 = main.FALSE

        '''
        place holder for comparing devices, hosts and paths if required. 
        Links and ports data would be incorrect with out devices anyways.
        '''

        caseResult=(stepResult1 and stepResult2)
        utilities.assert_equals(expect=main.TRUE, actual=case1Result,
                onpass="Compare Topology test PASS",
                onfail="Compare Topology test FAIL")
        if caseResult == main.TRUE:
            main.log.report("Compare Topology test Pass")

    def CASE6(self):
        '''
        Install 300 host intents and verify ping all
        '''
        main.log.report("Add 300 host intents and verify pingall")
        main.log.report("_______________________________________")
        import itertools
        main.case("Install 300 host intents")
        main.step("Add host Intents")
        intentResult=main.TRUE
        hostCombos = list(itertools.combinations(hostMACs, 2))
        for i in range(len(hostCombos)):
            iResult = main.ONOScli1.add_host_intent(hostCombos[i][0],hostCombos[i][1])
            intentResult=(intentResult and iResult)

        main.step("Verify Ping across all hosts")
        pingResult = main.FALSE
        time1 = time.time()
        pingResult = main.Mininet1.pingall()
        time2 = time.time()
        timeDiff = round((time2-time1),2)
        main.log.report("Time taken for Ping All: "+str(timeDiff)+" seconds")
        utilities.assert_equals(expect=main.TRUE, actual=pingResult,
                onpass="PING ALL PASS",
                onfail="PING ALL FAIL")

        case4Result=(intentResult and pingResult)
        utilities.assert_equals(expect=main.TRUE, actual=case4Result,
                onpass="Install 300 Host Intents and Ping All test PASS",
                onfail="Install 300 Host Intents and Ping All test FAIL")

    def CASE7(self,main):
        '''
        Randomly bring some core links down and verify ping all
        '''
        import random
        ONOS1_ip = main.params['CTRL']['ip1']
        link1End1 = main.params['CORELINKS']['linkS3a']
        link1End2 = main.params['CORELINKS']['linkS3b'].split(',')
        link2End1 = main.params['CORELINKS']['linkS14a']
        link2End2 = main.params['CORELINKS']['linkS14b'].split(',')
        link3End1 = main.params['CORELINKS']['linkS18a']
        link3End2 = main.params['CORELINKS']['linkS18b'].split(',')
        switchLinksToToggle = main.params['CORELINKS']['toggleLinks']
        link_sleep = int(main.params['timers']['LinkDiscovery'])

        main.log.report("Randomly bring some core links down and verify ping all")
        main.log.report("____________________________________________________")        
        main.case("Randomly bring some core links down and verify ping all")
        main.step("Verify number of Switch links to toggle on each Core Switch are between 1 - 5")
        if (int(switchLinksToToggle) == 0 or int(switchLinksToToggle) > 5):
            main.log.info("Please check you PARAMS file. Valid range for number of switch links to toggle is between 1 to 5")
            main.cleanup()
            main.exit()
        else:
            main.log.info("User provided Core switch links range to toggle is correct, proceeding to run the test")

        main.step("Cut links on Core devices using user provided range")
        randomLink1 = random.sample(link1End2,int(switchLinksToToggle))
        randomLink2 = random.sample(link2End2,int(switchLinksToToggle))
        randomLink3 = random.sample(link3End2,int(switchLinksToToggle))
        for i in range(int(switchLinksToToggle)):
            main.Mininet1.link(END1=link1End1,END2=randomLink1[i],OPTION="down")
            main.Mininet1.link(END1=link2End1,END2=randomLink2[i],OPTION="down")
            main.Mininet1.link(END1=link3End1,END2=randomLink3[i],OPTION="down")
        time.sleep(link_sleep)

        topology_output = main.ONOScli2.topology()
        linkDown = main.ONOSbench.check_status(topology_output,numSwitches,str(int(numLinks)-int(switchLinksToToggle)*6))
        utilities.assert_equals(expect=main.TRUE,actual=linkDown,
                onpass="Link Down discovered properly",
                onfail="Link down was not discovered in "+ str(link_sleep) + " seconds")

        main.step("Verify Ping across all hosts")
        pingResultLinkDown = main.FALSE
        time1 = time.time()
        pingResultLinkDown = main.Mininet1.pingall()
        time2 = time.time()
        timeDiff = round((time2-time1),2)
        main.log.report("Time taken for Ping All: "+str(timeDiff)+" seconds")
        utilities.assert_equals(expect=main.TRUE, actual=pingResultLinkDown,
                onpass="PING ALL PASS",
                onfail="PING ALL FAIL")

        caseResult7 = linkDown and pingResultLinkDown
        utilities.assert_equals(expect=main.TRUE, actual=caseResult7,
                onpass="Random Link cut Test PASS",
                onfail="Random Link cut Test FAIL")

    def CASE8(self,main):
        '''
        Bring the core links up that are down and verify ping all
        '''
        import random
        ONOS1_ip = main.params['CTRL']['ip1']
        link1End1 = main.params['CORELINKS']['linkS3a']
        link2End1 = main.params['CORELINKS']['linkS14a']
        link3End1 = main.params['CORELINKS']['linkS18a']
        link_sleep = int(main.params['timers']['LinkDiscovery'])
        switchLinksToToggle = main.params['CORELINKS']['toggleLinks']

        main.log.report("Bring the core links up that are down and verify ping all")
        main.log.report("_____________________________________________________")        
        main.case("Bring the core links up that are down and verify ping all")
        main.step("Bring randomly cut links on Core devices up")
        for i in range(int(switchLinksToToggle)): 
            main.Mininet1.link(END1=link1End1,END2=randomLink1[i],OPTION="up")
            main.Mininet1.link(END1=link2End1,END2=randomLink2[i],OPTION="up")
            main.Mininet1.link(END1=link3End1,END2=randomLink3[i],OPTION="up")
        time.sleep(link_sleep)

        topology_output = main.ONOScli2.topology()
        linkUp = main.ONOSbench.check_status(topology_output,numSwitches,str(numLinks))
        utilities.assert_equals(expect=main.TRUE,actual=linkUp,
                onpass="Link up discovered properly",
                onfail="Link up was not discovered in "+ str(link_sleep) + " seconds")

        main.step("Verify Ping across all hosts")
        pingResultLinkUp = main.FALSE
        time1 = time.time()
        pingResultLinkUp = main.Mininet1.pingall()
        time2 = time.time()
        timeDiff = round((time2-time1),2)
        main.log.report("Time taken for Ping All: "+str(timeDiff)+" seconds")
        utilities.assert_equals(expect=main.TRUE, actual=pingResultLinkUp,
                onpass="PING ALL PASS",
                onfail="PING ALL FAIL")

        caseResult8 = linkUp and pingResultLinkUp
        utilities.assert_equals(expect=main.TRUE, actual=caseResult8,
                onpass="Link Up Test PASS",
                onfail="Link Up Test FAIL")    

    def CASE9(self):
        '''
        Install 114 point intents and verify Ping all works
        '''
        import copy
        main.log.report("Install 114 point intents and verify Ping all")
        main.log.report("___________________________________________")        
        main.case("Install 114 point intents and Ping all")
        deviceLinks_copy = copy.copy(deviceLinks)
        main.step("Install 114 point intents")
        for i in range(len(deviceLinks_copy)):
            pointLink = str(deviceLinks_copy[i]).replace("src=","").replace("dst=","").split(',')
            point1 = pointLink[0].split('/')
            point2 = pointLink[1].split('/')
            installResult = main.ONOScli1.add_point_intent(point1[0],point2[0],int(point1[1]),int(point2[1]))
            if installResult == main.TRUE:
                print "Installed Point intent between :",point1[0], int(point1[1]), point2[0], int(point2[1])

        main.step("Obtain the intent id's")
        intentsList = main.ONOScli1.getAllIntentIds()
        ansi_escape = re.compile(r'\x1b[^m]*m')
        intentsList = ansi_escape.sub('', intentsList)
        intentsList = intentsList.replace(" onos:intents | grep id=","").replace("id=","").replace("\r\r","")
        intentsList=intentsList.splitlines()
        intentsList = intentsList[1:]
        intentIdList = []
        for i in range(len(intentsList)):
            intentsTemp = intentsList[i].split(',')
            intentIdList.append(intentsTemp[0])
        print "Intent IDs: ", intentIdList
        print "Total Intents installed: ", len(intentIdList)

        main.step("Verify Ping across all hosts")
        pingResult = main.FALSE
        time1 = time.time()
        pingResult = main.Mininet1.pingall()
        time2 = time.time()
        timeDiff = round((time2-time1),2)
        main.log.report("Time taken for Ping All: "+str(timeDiff)+" seconds")
        utilities.assert_equals(expect=main.TRUE, actual=pingResult,
                onpass="PING ALL PASS",
                onfail="PING ALL FAIL")

        case8_result = installResult and pingResult
        utilities.assert_equals(expect=main.TRUE, actual=case8_result,
                onpass="Ping all test after Point intents addition successful",
                onfail="Ping all test after Point intents addition failed")

    def CASE10(self):
        '''
         Remove all Intents
        ''' 
        main.log.report("Remove all intents that were installed previously")
        main.log.report("______________________________________________")        
        main.log.info("Remove all intents")
        main.case("Removing intents")
        main.step("Obtain the intent id's first")
        intentsList = main.ONOScli1.getAllIntentIds()
        ansi_escape = re.compile(r'\x1b[^m]*m')
        intentsList = ansi_escape.sub('', intentsList)
        intentsList = intentsList.replace(" onos:intents | grep id=","").replace("id=","").replace("\r\r","")
        intentsList=intentsList.splitlines()
        intentsList = intentsList[1:]
        intentIdList = []
        step1Result = main.TRUE
        if (len(intentsList) > 1):
            for i in range(len(intentsList)):
                intentsTemp = intentsList[i].split(',')
                intentIdList.append(intentsTemp[0])
            print "Intent IDs: ", intentIdList
            for id in range(len(intentIdList)):
                print "Removing intent id (round 1) :", intentIdList[id]
                main.ONOScli1.remove_intent(intent_id = intentIdList[id])
                time.sleep(1)

            main.log.info("Verify all intents are removed and if any leftovers try remove one more time")
            intentsList1 = main.ONOScli1.getAllIntentIds()
            ansi_escape = re.compile(r'\x1b[^m]*m')
            intentsList1 = ansi_escape.sub('', intentsList1)
            intentsList1 = intentsList1.replace(" onos:intents | grep id=","").replace(" state=","").replace("\r\r","")
            intentsList1=intentsList1.splitlines()
            intentsList1 = intentsList1[1:]
            print "Round 2 (leftover) intents to remove: ", intentsList1
            intentIdList1 = []
            if (len(intentsList1) > 1):
                for i in range(len(intentsList1)):
                    intentsTemp1 = intentsList[i].split(',')
                    intentIdList1.append(intentsTemp1[0])
                print "Leftover Intent IDs: ", intentIdList1
                for id in range(len(intentIdList1)):
                    print "Removing intent id (round 2):", intentIdList1[id]
                    main.ONOScli1.remove_intent(intent_id = intentIdList1[id])
                    time.sleep(2)
            else:
                print "There are no more intents that need to be removed"
                step1Result = main.TRUE
        else:
            print "No Intent IDs found in Intents list: ", intentsList
            step1Result = main.FALSE

        caseResult7 = step1Result
        utilities.assert_equals(expect=main.TRUE, actual=caseResult7,
                onpass="Intent removal test successful",
                onfail="Intent removal test failed")