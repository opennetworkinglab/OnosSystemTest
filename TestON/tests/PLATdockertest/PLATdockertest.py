
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
        global DOCKERREPO, DOCKERTAG
        global IPlist
        global CTIDlist
        global NODElist

        DOCKERREPO = "onosproject/onos"
        DOCKERTAG = "latest"

    def CASE1( self, main ):
        """
        1) set up test params;
        """
        import re

        main.case("Set case test params")
        main.step("Initialize test params")
        NODElist = main.params["SCALE"]["nodelist"].split(',')
        main.log.info("onos container names are: " + ",".join(NODElist) )
        IPlist = list()
        main.testOnDirectory = re.sub( "(/tests)$", "", main.testDir )
        DOCKERREPO = main.params[ 'DOCKER' ][ 'repo' ]
        DOCKERTAG = main.params[ 'DOCKER' ][ 'tag' ]
        CTIDlist = list()
        utilities.assert_equals( expect = main.TRUE, actual = main.TRUE,
                                    onpass = "Params set",
                                    onfail = "Failed to set params")

    def CASE5(self, main):
        """
        Pull (default) "onosproject/onos:latest" image
        """

        main.case( "Pull latest onos docker image from onosproject/onos - \
                    it may take sometime if this is a first time pulling." )
        stepResult = main.FALSE
        main.step( "pull latest image from onosproject/onos")
        stepResult = main.ONOSbenchDocker.dockerPull( onosRepo = DOCKERREPO, onosTag = DOCKERTAG )
        utilities.assert_equals( expect = main.TRUE, actual = stepResult,
                                    onpass = "Succeeded in pulling " + DOCKERREPO + ":" + DOCKERTAG,
                                    onfail = "Failed to pull " + DOCKERREPO + ":" + DOCKERTAG )

    def CASE10( self, main ):
        """
        Start docker containers for list of onos nodes, only if not already existed
        """
        import re

        main.case( "Start onos container(s)")
        image = DOCKERREPO + ":" + DOCKERTAG

        main.step( "Create and (re)start docker container(s) if not already exist")
        #stepResult = main.FALSE

        for ct in xrange(0, len(NODElist)):
            if not main.ONOSbenchDocker.dockerCheckCTName( ctName = NODElist[ct] ):
                main.log.info( "Create new container for onos" + str(ct + 1) )
                createResult, ctid = main.ONOSbenchDocker.dockerCreateCT( onosImage = image, onosNode = NODElist[ct])
                CTIDlist.append(ctid)
                startResult = main.ONOSbenchDocker.dockerStartCT( ctID = ctid )
            else:
                main.log.info("Container exists for node onos" + str(ct + 1) + "; restart container with latest image" )
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

        startupSleep = int(main.params["SLEEP"]["startup"])

        appToAct = main.params["CASE110"]["apps"]
        stepResult = main.FALSE

        main.log.info( "Wait for startup, sleep (sec): " + str(startupSleep))
        time.sleep(startupSleep)

        main.step( "Check initial app states from onos1")
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
        if stepResult is main.FALSE: main.skipCase

        main.step( "Form onos cluster using 'Dependency/onos-form-cluster' util")
        stepResult = main.FALSE
        clcmdpath = main.params["CASE110"]["clustercmdpath"]
        main.log.info("onos-form-cluster cmd path is: " + clcmdpath)
        dkruser = main.params["DOCKER"]["user"]
        dkrpasswd = main.params["DOCKER"]["password"]
        main.ONOSbenchDocker.onosFormCluster(cmdPath = clcmdpath, onosIPs=IPlist, user=dkruser, passwd = dkrpasswd)
        main.log.info("Wait for cluster to form with sleep time of " + str(startupSleep))
        time.sleep(startupSleep)
        status, response = main.ONOSbenchRest.send(ip=IPlist[0],port=8181, url="/cluster")
        main.log.debug("Rest call response: " + str(status) + " - " + response)
        if status == 200:
            jrsp = json.loads(response)
            clusterIP = [item["ip"]for item in jrsp["nodes"] if item["status"]== "ACTIVE"]
            if set(IPlist) == set(clusterIP): stepResult = main.TRUE

        utilities.assert_equals( expect = main.TRUE, actual = stepResult,
                                    onpass = "ONOS successfully started",
                                    onfail = "Failed to start ONOS correctly" )
        if stepResult is main.FALSE: main.skipCase

        main.step( "Check cluster app status")
        stepResult = main.TRUE
        response = main.ONOSbenchRest.apps( ip=IPlist[0], port = 8181 )
        if response is not main.FALSE:
            for item in json.loads(response):
                if item["state"] not in ["ACTIVE", "INSTALLED"]:
                    main.log.info("Some bundles are not in correct state. ")
                    main.log.info("App states are: " + response)
                    stepResult = main.FALSE
                    break;
                if (item["description"] == "Builtin device drivers") and (item["state"] != "ACTIVE"):
                    main.log.info("Driver app is not in 'ACTIVE' state, but in: " + item["state"])
                    stepResult = main.FALSE
                    break;
        utilities.assert_equals( expect = main.TRUE, actual = stepResult,
                                    onpass = "ONOS successfully started",
                                    onfail = "Failed to start ONOS correctly" )
        if stepResult is main.FALSE: main.skipCase

        main.step(" Activate an APP from REST and check APP status")
        appResults = list()
        stepResult = main.TRUE
        applist = main.params["CASE110"]["apps"].split(",")
        main.log.info("List of apps to activate: " + str(applist) )
        for app in applist:
            time.sleep(5)
            appRslt = main.ONOSbenchRest.activateApp(appName=app, ip=IPlist[0], port=8181, check=True)
            appResults.append(appRslt)
            stepResult = stepResult and appRslt
        main.log.debug("Apps activation result for " + ",".join(applist) + ": " + str(appResults) ) 
        utilities.assert_equals( expect = main.TRUE, actual = stepResult,
                                    onpass = "Successfully activate apps",
                                    onfail = "Failed to activate apps correctly" )
        if stepResult is main.FALSE: main.skipCase

        main.step(" Deactivate an APP from REST and check APP status")
        appResults = list()
        stepResult = main.TRUE
        applist = main.params["CASE110"]["apps"].split(",")
        main.log.info("Apps to activae: " + str(applist) )
        for app in applist:
            time.sleep(5)
            appRslt = main.ONOSbenchRest.deactivateApp(appName=app, ip=IPlist[0], port=8181, check=True)
            appResults.append(appRslt)
            stepResult = stepResult and appRslt
        main.log.debug("Apps deactivation result for " + ",".join(applist) + ": " + str(appResults) )
        utilities.assert_equals( expect = main.TRUE, actual = stepResult,
                                    onpass = "Successfully deactivate apps",
                                    onfail = "Failed to deactivate apps correctly" )
        if stepResult is main.FALSE: main.skipCase

    def CASE1000( self, main ):

        """
        Cleanup after tests - stop and delete the containers created; delete "onosproject/onos:latest image
        """
        import time

        main.step("Stop onos containers")
        stepResult = main.TRUE
        for ctname in NODElist:
            if main.ONOSbenchDocker.dockerCheckCTName(ctName = "/" + ctname):
                main.log.info( "stopping docker container: /" + ctname)
                stopResult = main.ONOSbenchDocker.dockerStopCT( ctName = "/" + ctname )
                time.sleep(10)
                rmResult = main.ONOSbenchDocker.dockerRemoveCT( ctName = "/" + ctname)
                stepResult = stepResult and stopResult and rmResult
        utilities.assert_equals( expect = main.TRUE, actual = stepResult,
                                    onpass = "Container successfully stopped",
                                    onfail = "Failed to stopped the container" )

        #main.step( "remove exiting onosproject/onos images")
        #stepResult = main.ONOSbenchDocker.dockerRemoveImage( image = DOCKERREPO + ":" + DOCKERTAG )
        main.step( "remove exiting 'none:none' images")
        stepResult = main.ONOSbenchDocker.dockerRemoveImage( image = "<none>:<none>" )
        utilities.assert_equals( expect = main.TRUE, actual = stepResult,
                                    onpass = "Succeeded in deleting image " + "<none>:<none>",
                                    onfail = "Failed to delete image " + "<none>:<none>" )

