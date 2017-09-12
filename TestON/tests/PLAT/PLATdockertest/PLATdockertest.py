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

# This is a basic platform test suite.
# Additional platform test cases can be added on this test suite where appropriate.

class PLATdockertest:
    """
    This testsuite performs the following tests:
    1) checkout onos docker image;
    2) test image start up in single and clustered mode;
    3) test onos app activation and deactivation;

    Prerequisites:
    1) docker-engine installed on test station (localhost);
    2) python docker client (docker-py) installed on test station
    """

    def __init__( self ):
        self.default = ''
        global DOCKERREPO, DOCKERTAG, INITDOCKERTAG
        global IPlist
        global CTIDlist
        global NODElist

        DOCKERREPO = "onosproject/onos"
        DOCKERTAG = "latest"

    def CASE0( self, main ):
        """
        Pull all docker images and get a list of image tags
        """
        main.case( "Pull all docker images and get a list of image tags" )
        import os
        DOCKERREPO = main.params[ 'DOCKER' ][ 'repo' ]
        os.system( "docker pull -a " + DOCKERREPO )
        imageTagList = list()
        imageTagCounter = 0
        duplicateTagDetected = 0
        imageTagList, duplicateTagDetected = main.ONOSbenchDocker.getListOfImages( DOCKERREPO )
        stepResult = main.FALSE
        main.step( "Check for duplicate Tags for a given image" )
        if not duplicateTagDetected:
            stepResult = main.TRUE
        utilities.assert_equals( expect = main.TRUE, actual = stepResult,
                                    onpass = "no duplicate image tags",
                                    onfail = "duplicate image tags detected!!" )
        main.step( "Get a list of image tags" )
        stepResult = main.FALSE
        if imageTagList is not []:
            main.log.info( "The Image tag list is: " + str(imageTagList) )
            stepResult = main.TRUE
        utilities.assert_equals( expect = main.TRUE, actual = stepResult,
                                    onpass = "image tag list pulled successfully",
                                    onfail = "image tag list not pulled" )

    def CASE1( self, main ):
        """
        1) set up test params;
        """
        import re
        import time
        import subprocess

        if imageTagCounter < len( imageTagList ):
            DOCKERTAG = imageTagList[imageTagCounter]
        if not imageTagCounter:
            INITDOCKERTAG = DOCKERTAG
        imageTagCounter += 1

        main.case("Set case test params for onos image {}".format( DOCKERTAG ))
        main.step("Initialize test params")
        NODElist = main.params["SCALE"]["nodelist"].split(',')
        main.log.info("onos container names are: " + ",".join(NODElist) )
        IPlist = list()
        main.testOnDirectory = re.sub( "(/tests)$", "", main.testDir )
        CTIDlist = list()

        main.log.info("Check docker status, it not running, try restart it")
        iter = 0
        stepResult = main.TRUE
        while subprocess.call("sudo service docker status", shell=True) and iter <= 3:
            subprocess.call("sudo service docker restart", shell=True)
            time.sleep(5)
            iter += 1
            if iter == 3: stepResult = main.FALSE

        utilities.assert_equals( expect = main.TRUE, actual = stepResult,
                                    onpass = "docker is running",
                                    onfail = "docker is not running")
        if stepResult == main.FALSE:
            main.log.warn("docker is not running - exiting test")
            main.cleanAndExit()
        if imageTagCounter > len( imageTagList ):
            main.log.info("All images have been tested")
            main.cleanAndExit()

    def CASE5(self, main):
        """
        Pull the specified image
        """

        main.case( "Pull onos docker image {} from {} - \
                    it may take sometime if this is a first time pulling.".format( DOCKERTAG, DOCKERREPO ) )
        stepResult = main.FALSE
        main.step( "pull image {} from {}".format( DOCKERTAG, DOCKERREPO ) )
        stepResult = main.ONOSbenchDocker.dockerPull( onosRepo = DOCKERREPO, onosTag = DOCKERTAG )
        utilities.assert_equals( expect = main.TRUE, actual = stepResult,
                                    onpass = "Succeeded in pulling " + DOCKERREPO + ":" + DOCKERTAG,
                                    onfail = "Failed to pull " + DOCKERREPO + ":" + DOCKERTAG )
        if stepResult == main.FALSE: main.skipCase()

    def CASE10( self, main ):
        """
        Start docker containers for list of onos nodes, only if not already existed
        """
        import re
        createResult = main.TRUE
        startResult = main.TRUE
        main.case( "Start onos container(s) for onos image {}".format( DOCKERTAG ))
        image = DOCKERREPO + ":" + DOCKERTAG

        main.step( "Create and (re)start docker container(s) for onos image {} if not already exist".format( DOCKERTAG ))
        #stepResult = main.FALSE

        for ct in xrange(0, len(NODElist)):
            if not main.ONOSbenchDocker.dockerCheckCTName( ctName = NODElist[ct] ):
                main.log.info( "Create new container for onos" + str(ct + 1) )
                createResult, ctid = main.ONOSbenchDocker.dockerCreateCT( onosImage = image, onosNode = NODElist[ct])
                CTIDlist.append(ctid)
                startResult = main.ONOSbenchDocker.dockerStartCT( ctID = ctid )
            else:
                main.log.info("Container exists for node onos" + str(ct + 1) + "; restart container with {} image".format( DOCKERTAG ) )
                startResult = main.ONOSbenchDocker.dockerRestartCT( ctName = NODElist[ct ] )

        utilities.assert_equals( expect = main.TRUE, actual = createResult and startResult,
                                    onpass = "Container successfully created",
                                    onfail = "Failed to create the container" )

        main.step( "Get IP address on onos containers" )
        stepResult = main.FALSE

        for ct in xrange(0,len(NODElist)):
            IPlist.append(main.ONOSbenchDocker.dockerIP( ctName = NODElist[ct] ))
        main.log.info("Container IPs are: " +  ', '.join( IPlist ))

        if IPlist is not []:stepResult = main.TRUE
        utilities.assert_equals( expect = main.TRUE, actual = stepResult,
                                    onpass = "Container successfully started",
                                    onfail = "Failed to start the container" )

    def CASE110(self,main):
        """
        Steps:
        1) check default startup standalone onos applications status;
        2) form onos cluster with all nodes;
        3) check onos applications status;
        4) activate apps per params and check app status;
        5) deactivate apps and check app status

        """
        import time
        import json

        main.case( "Form onos cluster and check status of onos apps for onos image {}".format( DOCKERTAG ) )

        startupSleep = int(main.params["SLEEP"]["startup"])

        appToAct = main.params["CASE110"]["apps"]
        stepResult = main.FALSE

        main.log.info( "Wait for startup, sleep (sec): " + str(startupSleep))
        time.sleep(startupSleep)

        main.step( "Check initial app states from onos1 for onos image {}".format( DOCKERTAG ))
        stepResult = main.TRUE
        response = main.ONOSbenchRest.apps( ip=IPlist[0], port = 8181 )
        main.log.debug("Rest call response is: " + response)
        if response is not main.FALSE:
            for item in json.loads(response):
                if item["state"] not in ["ACTIVE", "INSTALLED"]:
                    main.log.info("Some bundles are not in correct state. ")
                    main.log.info("App states are: " + response)
                    stepResult = main.FALSE
                    break;
                if (item["description"] == "Builtin device drivers") and (item["state"] !=  "ACTIVE"):
                    main.log.info("Driver app is not in 'ACTIVE' state, but in: " + item["state"])
                    stepResult = main.FALSE
                    break;
        utilities.assert_equals( expect = main.TRUE, actual = stepResult,
                                    onpass = "ONOS successfully started",
                                    onfail = "Failed to start ONOS correctly" )
        if stepResult is main.FALSE: main.skipCase()

        main.step( "Form onos cluster using 'dependencies/onos-form-cluster' util")
        stepResult = main.FALSE
        clcmdpath = main.params["CASE110"]["clustercmdpath"]
        main.log.info("onos-form-cluster cmd path is: " + clcmdpath)
        dkruser = main.params["DOCKER"]["user"]
        dkrpasswd = main.params["DOCKER"]["password"]
        main.ONOSbenchDocker.onosFormCluster(cmdPath = clcmdpath, onosIPs=IPlist, user=dkruser, passwd = dkrpasswd)
        main.log.info("Wait for cluster to form with sleep time of " + str(startupSleep))
        time.sleep(startupSleep)
        status, response = main.ONOSbenchRest.send(ip=IPlist[0], port=8181, url="/cluster")
        main.log.debug("Rest call response: " + str(status) + " - " + response)
        if status == 200:
            jrsp = json.loads(response)
            if DOCKERTAG == "1.2" or DOCKERTAG == "1.3" or DOCKERTAG == "1.4" or DOCKERTAG == "1.5":
                clusterIP = [item["ip"]for item in jrsp["nodes"] if item["status"]== "ACTIVE"]
            else:
                clusterIP = [item["ip"]for item in jrsp["nodes"] if item["status"]== "READY"]
            main.log.debug(" IPlist is:" + ",".join(IPlist))
            main.log.debug(" cluster IP is" + ",".join(clusterIP))
            if set(IPlist) == set(clusterIP): stepResult = main.TRUE

        utilities.assert_equals( expect = main.TRUE, actual = stepResult,
                                    onpass = "ONOS successfully started",
                                    onfail = "Failed to start ONOS correctly" )
        if stepResult is main.FALSE: main.skipCase()

        main.step( "Check cluster app status")
        stepResult = main.TRUE
        response = main.ONOSbenchRest.apps( ip=IPlist[0], port = 8181 )
        if response is not main.FALSE:
            for item in json.loads(response):
                if item["state"] not in ["ACTIVE", "INSTALLED"]:
                    main.log.info("Some bundles are not in correct state. ")
                    main.log.info("App states are: " + response)
                    stepResult = main.FALSE
                    break
                if (item["description"] == "Builtin device drivers") and (item["state"] != "ACTIVE"):
                    main.log.info("Driver app is not in 'ACTIVE' state, but in: " + item["state"])
                    stepResult = main.FALSE
                    break
        utilities.assert_equals( expect = main.TRUE, actual = stepResult,
                                    onpass = "ONOS successfully started",
                                    onfail = "Failed to start ONOS correctly" )
        if stepResult is main.FALSE: main.skipCase()

        main.step(" Activate an APP from REST and check APP status")
        appResults = list()
        stepResult = main.TRUE
        applist = main.params["CASE110"]["apps"].split(",")
        main.log.info("List of apps to activate: " + str(applist) )
        for app in applist:
            appRslt = main.ONOSbenchRest.activateApp(appName=app, ip=IPlist[0], port=8181, check=True)
            time.sleep(5)
            appResults.append(appRslt)
            stepResult = stepResult and appRslt
        main.log.debug("Apps activation result for " + ",".join(applist) + ": " + str(appResults) )
        utilities.assert_equals( expect = main.TRUE, actual = stepResult,
                                    onpass = "Successfully activated apps",
                                    onfail = "Failed to activated apps correctly" )
        if stepResult is main.FALSE: main.skipCase()

        main.step(" Deactivate an APP from REST and check APP status")
        appResults = list()
        stepResult = main.TRUE
        applist = main.params["CASE110"]["apps"].split(",")
        main.log.info("Apps to deactivate: " + str(applist) )
        for app in applist:
            time.sleep(5)
            appRslt = main.ONOSbenchRest.deactivateApp(appName=app, ip=IPlist[0], port=8181, check=True)
            appResults.append(appRslt)
            stepResult = stepResult and appRslt
        main.log.debug("Apps deactivation result for " + ",".join(applist) + ": " + str(appResults) )
        utilities.assert_equals( expect = main.TRUE, actual = stepResult,
                                    onpass = "Successfully deactivated apps",
                                    onfail = "Failed to deactivated apps correctly" )
        if stepResult is main.FALSE: main.skipCase()

    def CASE900(self,main):
        """
        Check onos logs for exceptions after tests
        """
        import pexpect
        import time
        import re

        logResult = main.TRUE

        user = main.params["DOCKER"]["user"]
        pwd = main.params["DOCKER"]["password"]

        main.case("onos Exceptions check with onos image {}".format( DOCKERTAG ))
        main.step("check onos for any exceptions")

        for ip in IPlist:
            spawncmd = "ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -p 8101 " + user + "@" + ip
            main.log.info("log on node using cmd: " + spawncmd)
            try:
                handle = pexpect.spawn(spawncmd)
                #handle.expect("yes/no")
                #handle.sendline("yes")
                #print("yes is sent")
                #this extra statement is sent to get around some
                #pexpect issue of not seeing the next expected string
                handle.expect("Password:")
                handle.sendline(pwd)
                time.sleep(5)
                handle.expect("onos>")
                handle.sendline("log:exception-display")
                handle.expect("onos>")
                result = handle.before
                if re.search("Exception", result):
                    main.log.info("onos: " + ip + " Exceptions:" + result)
                    logResult = logResult and main.FALSE
                else:
                    main.log.info("onos: " + ip + " Exceptions: None")
                    logResult = logResult and main.TRUE
            except Exception:
                main.log.exception("Uncaught exception when getting log from onos:" + ip)
                logResult = logResult and main.FALSE

        utilities.assert_equals( expect = main.TRUE, actual = logResult,
                                    onpass = "onos exception check passed",
                                    onfail = "onos exeption check failed" )

    def CASE1000( self, main ):

        """
        Cleanup after tests - stop and delete the containers created; delete the image
        """
        import time

        main.case("Clean up  images (ex. none:none tagged) and containers")
        main.step("Stop onos containers")
        stepResult = main.TRUE
        for ctname in NODElist:
            if main.ONOSbenchDocker.dockerCheckCTName( ctName="/" + ctname ):
                main.log.info( "stopping docker container: /" + ctname )
                stopResult = main.ONOSbenchDocker.dockerStopCT( ctName="/" + ctname )
                time.sleep(10)
                rmResult = main.ONOSbenchDocker.dockerRemoveCT( ctName="/" + ctname )
                stepResult = stepResult and stopResult and rmResult
        utilities.assert_equals( expect = main.TRUE, actual = stepResult,
                                    onpass = "Container successfully stopped",
                                    onfail = "Failed to stopped the container" )

        #main.step( "remove exiting onosproject/onos images")
        #stepResult = main.ONOSbenchDocker.dockerRemoveImage( image = DOCKERREPO + ":" + DOCKERTAG )
        main.step( "remove dangling 'none:none' images")
        stepResult = main.ONOSbenchDocker.dockerRemoveImage()
        utilities.assert_equals( expect = main.TRUE, actual = stepResult,
                                    onpass = "Succeeded in cleaning up images",
                                    onfail = "Failed in cleaning up images" )

    def CASE1001( self, main ):

        """
        Create a file for publishing results on wiki in tabular form
        """

        main.case( "Create a file for publishing on wiki in tabular form" )
        import re
        imageTagCounter = 0
        testCaseCounter = 0
        resultCounter = 0
        resultDictionary = {}
        testCaseList = []
        totalNumOfTestCases = 6
        try:
            main.tableFileName = main.logdir + "/" + main.TEST + "TableWiki.txt"
            main.wikiTableFile = open(main.tableFileName, "a+")
            main.wikiFileHandle = open(main.WikiFileName, "r")
            for imageTag in imageTagList:
                resultDictionary[ imageTag ] = []
            for line in main.wikiFileHandle:
                matchObj = re.search("(?!.*Case 0).*<h3>(.+?)<\/h3>", line)
                if testCaseCounter < totalNumOfTestCases:
                    if matchObj:
                        wordsToRemove = re.compile("latest|- PASS|- FAIL|- No Result")
                        testCaseName = wordsToRemove.sub("", matchObj.group(1))
                        testCaseName = testCaseName.replace( INITDOCKERTAG,'' )
                        testCaseList.append(testCaseName)
                        testCaseCounter += 1
                if matchObj:
                    if "- PASS" in line:
                        resultDictionary[ imageTagList[ imageTagCounter ] ].append("PASS")
                    if "- FAIL" in line:
                        resultDictionary[ imageTagList[ imageTagCounter ] ].append("FAIL")
                    if "- No Result" in line:
                        resultDictionary[ imageTagList[ imageTagCounter ] ].append("No Result")
                    resultCounter += 1
                if resultCounter == totalNumOfTestCases:
                    imageTagCounter += 1
                    resultCounter = 0
            main.wikiTableFile.write( "<table style=\"width:100%\">\n" )
            main.wikiTableFile.write( "<tr>\n" )
            main.wikiTableFile.write( "<th>ONOS Version</th>\n" )
            for testCaseName in testCaseList:
                main.wikiTableFile.write( "<th>" + testCaseName + "</th>\n" )
            main.wikiTableFile.write( "</tr>\n" )
            for imageTag in imageTagList:
                main.wikiTableFile.write( "<tr>\n" )
                main.wikiTableFile.write( "<td>" + imageTag + "</td>\n" )
                for resultValue in resultDictionary[ imageTag ]:
                    if resultValue == "PASS":
                        emoticonValue = "\"tick\""
                    if resultValue == "FAIL":
                        emoticonValue = "\"cross\""
                    if resultValue == "No Result":
                        emoticonValue = "\"warning\""
                    main.wikiTableFile.write( "<td>" + resultValue + "  <ac:emoticon ac:name=" + emoticonValue + " /></td>\n" )
                main.wikiTableFile.write( "</tr>\n" )
            main.wikiTableFile.write( "</table>\n" )
            main.wikiTableFile.close()
            main.wikiFileHandle.close()
            logResult = main.TRUE
        except Exception:
            main.log.exception( "Exception while writing to the table file" )
            logResult = main.FALSE
        utilities.assert_equals( expect = main.TRUE, actual = logResult,
                                    onpass = "onos exception check passed",
                                    onfail = "onos exception check failed" )
