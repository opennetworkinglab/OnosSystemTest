#!groovy
// Copyright 2017 Open Networking Foundation (ONF)
//
// Please refer questions to either the onos test mailing list at <onos-test@onosproject.org>,
// the System Testing Plans and Results wiki page at <https://wiki.onosproject.org/x/voMg>,
// or the System Testing Guide page at <https://wiki.onosproject.org/x/WYQg>
//
//     TestON is free software: you can redistribute it and/or modify
//     it under the terms of the GNU General Public License as published by
//     the Free Software Foundation, either version 2 of the License, or
//     (at your option) any later version.
//
//     TestON is distributed in the hope that it will be useful,
//     but WITHOUT ANY WARRANTY; without even the implied warranty of
//     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//     GNU General Public License for more details.
//
//     You should have received a copy of the GNU General Public License
//     along with TestON.  If not, see <http://www.gnu.org/licenses/>.

import groovy.time.TimeCategory
import groovy.time.TimeDuration

// read the dependency files
graphs = evaluate readTrusted( 'TestON/JenkinsFile/dependencies/JenkinsGraphs.groovy' )
test_list = evaluate readTrusted( 'TestON/JenkinsFile/dependencies/JenkinsTestONTests.groovy' )
fileRelated = evaluate readTrusted( 'TestON/JenkinsFile/dependencies/JenkinsPathAndFiles.groovy' )
SCPFfuncs = evaluate readTrusted( 'TestON/JenkinsFile/dependencies/PerformanceFuncs.groovy' )

category = null
prop = null
testsToRun = null
testsToRunStrList = null
branch = null
branchWithPrefix = null
start = null
nodeLabel = null
testStation = null
testsOverride = null
isGraphOnly = false
isSCPF = false
testsFromList = [:]
graphPaths = [:]
pipeline = [:]

main()

def main(){
    init()
    runTests()
    generateGraphs()
    sendToSlack()
}

def init(){
    fileRelated.init()
    test_list.init()
    readParams()

    if ( category == "SCPF" ){
        isSCPF = true
        SCPFfuncs.init()
        graphs.initialize( category, SCPFfuncs );
        prop = getProperties()
        isOldFlow = ( prop[ "isOldFlow" ] == "true" )
        SCPFfuncs.oldFlowRuleCheck( isOldFlow, prop[ "ONOSBranch" ] )
    } else {
        isSCPF = false
        graphs.initialize()
        prop = getProperties()
    }

    // get the list of the test and init branch to it.
    testsFromList = test_list.getTestsFromCategory( category )

    initGraphPaths()
    tokenizeTokens = "\n;, "

    if ( testsOverride == "" || testsOverride == null ){
        testsToRunStrList = prop[ "Tests" ].tokenize( tokenizeTokens )
    } else {
        testsToRunStrList = testsOverride.tokenize( tokenizeTokens )
    }
    testsToRun = test_list.getTestsFromStringList( testsToRunStrList )
}

def readParams(){
    category = params.Category       // "FUNC", "HA", "USECASE", etc.
    branch = params.Branch           // "1.15", "2.1", "master", etc.
    branchWithPrefix = test_list.addPrefixToBranch( branch )
    testStation = params.TestStation // "TestStation-BMs", etc.
    nodeLabel = params.NodeLabel     // "BM", "VM", "Fabric-1.x", etc.
    testsOverride = params.TestsOverride // "FUNCflow, FUNCintent, [...]", overrides property file
    isGraphOnly = params.OnlyRefreshGraphs // true or false
}

def getProperties(){
    // get the properties of the test by reading the TestONOS.property

    filePath = '''/var/jenkins/TestONOS-''' + category + '''-''' + branchWithPrefix + '''.property'''

    node( testStation ) {
        return readProperties( file: filePath )
    }
}

def getCurrentTime(){
    // get time of the PST zone.

    TimeZone.setDefault( TimeZone.getTimeZone( 'PST' ) )
    return new Date()
}

def initGraphPaths(){
    graphPaths.put( "trendIndividual", fileRelated.rScriptPaths[ "scripts" ][ "trendIndividual" ] )
    if ( category == "SR" ){
        graphPaths.put( "saveDirectory", fileRelated.workspaces[ "base" ] + "postjob-" + ( testStation - "TestStation-" - "s" ) + "/" )
    } else if ( category == "SRHA" ) {
        graphPaths.put( "saveDirectory", fileRelated.workspaces[ "Fabric" ] )
    } else if ( category == "SCPF" || category == "USECASE" ){
        graphPaths.put( "saveDirectory", fileRelated.workspaces[ "BM" ] )
    } else {
        graphPaths.put( "saveDirectory", fileRelated.workspaces[ "VM" ] )
    }
}

def runTests(){
    // run the test sequentially and save the function into the dictionary.
    for ( String test : testsToRun.keySet() ){
        toBeRun = test
        stepName = ( toBeRun ? "" : "Not " ) + "Running $test"
        pureTestName = ( testsToRun[ test ].containsKey( "test" ) ? testsToRun[ test ][ "test" ].split().head() : test )
        pipeline[ stepName ] = runTest( test,
                                        toBeRun,
                                        prop,
                                        pureTestName,
                                        isGraphOnly,
                                        testsToRun,
                                        graphPaths[ "trendIndividual" ],
                                        graphPaths[ "saveDirectory" ] )
    }

    // get the start time of the test.
    start = getCurrentTime()

    // run the tests sequentially.
    for ( test in pipeline.keySet() ){
        pipeline[ test ].call()
    }
}

def initTest(){
    return '''#!/bin/bash -l
        set -i # interactive
        set +e
        shopt -s expand_aliases # expand alias in non-interactive mode
        export PYTHONUNBUFFERED=1
        ifconfig
        echo "ONOS Branch is: $ONOSBranch"
        echo "TestON Branch is: $TestONBranch"
        echo "Test date: "
        date
        cd ~
        export PATH=$PATH:onos/tools/test/bin
        timeout 240 stc shutdown | head -100
        timeout 240 stc teardown | head -100
        timeout 240 stc shutdown | head -100
        cd ~/OnosSystemTest/TestON/bin
        git log | head
        ./cleanup.sh -f || true
        '''
}

def runTestCli_py( testName, testCategory ){
    // Bash script that will run the test.
    // testName : name of the test
    // testCategory : (SR,FUNC ... )

    return '''cd ~/OnosSystemTest/TestON/bin
           ./cli.py run ''' +
           testName +
           ''' --params GRAPH/nodeCluster=''' + nodeLabel
}

def concludeRunTest(){
    return '''cd ~/OnosSystemTest/TestON/bin
              ./cleanup.sh -f || true
              # cleanup config changes
              cd ~/onos/tools/package/config
              git clean -df'''
}

def copyLogs(){
    // bash script to copy the logs and other necessary element for SR tests.

    result = ""
    if ( category == "SR" ){
        result = '''
      sudo rm /var/jenkins/workspace/SR-log-${WikiPrefix}/*
      sudo cp *karaf.log.* /var/jenkins/workspace/SR-log-${WikiPrefix}/
      sudo cp *Flows* /var/jenkins/workspace/SR-log-${WikiPrefix}/
      sudo cp *Groups* /var/jenkins/workspace/SR-log-${WikiPrefix}/
      sudo cp *.tar.gz /var/jenkins/workspace/SR-log-${WikiPrefix}/
      sudo cp t3-* /var/jenkins/workspace/SR-log-${WikiPrefix}/
      '''
    }
    return result
}

def cleanAndCopyFiles( testName ){
    // clean up some files that were in the folder and copy the new files from the log
    // testName : name of the test

    return '''#!/bin/bash -i
        set +e
        echo "ONOS Branch is: ${ONOSBranch}"
        echo "TestON Branch is: ${TestONBranch}"
        echo "Job name is: "''' + testName + '''
        echo "Workspace is: ${WORKSPACE}/"
        echo "Wiki page to post is: ${WikiPrefix}-"
        # remove any leftover files from previous tests
        sudo rm ${WORKSPACE}/*Wiki.txt
        sudo rm ${WORKSPACE}/*Summary.txt
        sudo rm ${WORKSPACE}/*Result.txt
        sudo rm ${WORKSPACE}/*Alarm.txt || true
        sudo rm ${WORKSPACE}/*.csv
        #copy files to workspace
        cd `ls -t ~/OnosSystemTest/TestON/logs/*/ | head -1 | sed 's/://'`
        ''' + copyLogs() + '''
        sudo cp *.txt ${WORKSPACE}/
        sudo cp *.csv ${WORKSPACE}/
        cd ${WORKSPACE}/
        for i in *.csv
            do mv "$i" "$WikiPrefix"-"$i"
        done
        ls -al
        cd '''
}

def fetchLogs( testName ){
    // fetch the logs of onos from onos nodes to onos System Test logs
    // testName: name of the test

    return '''#!/bin/bash
  set +e
  cd ~/OnosSystemTest/TestON/logs
  echo "TestON test name is: "''' + testName + '''
  TestONlogDir=$(ls -t | grep ${TEST_NAME}_  |head -1)
  echo "########################################################################################"
  echo "#####  copying ONOS logs from all nodes to TestON/logs directory: ${TestONlogDir}"
  echo "########################################################################################"
  cd $TestONlogDir
  if [ $? -eq 1 ]
  then
      echo "Job name does not match any test suite name to move log!"
  else
      pwd
      for i in $OC{1..7}; do onos-fetch-logs $i || echo log does not exist for onos $i; done
      for i in $OC{1..7}; do atomix-fetch-logs $i || echo log does not exist for atomix $i; done
  fi
  cd'''
}

def publishToConfluence( isManualRun, isPostResult, wikiLink, file ){
    // publish HTML script to wiki confluence
    // isManualRun : string "true" "false"
    // isPostResult : string "true" "false"
    // wikiLink : link of the wiki page to publish
    // file : name of the file to be published

    if ( isPostingResult( isManualRun, isPostResult ) ){
        publishConfluence siteName: 'wiki.onosproject.org', pageName: wikiLink, spaceName: 'ONOS',
                          attachArchivedArtifacts: true, buildIfUnstable: true,
                          editorList: [ confluenceWritePage( confluenceFile( file ) ) ]
    }
}

def postLogs( testName, prefix ){
    // posting logs of the onos jobs specifically SR tests
    // testName : name of the test
    // prefix : branch prefix ( master, 2.1, 1.15 ... )

    resultURL = ""
    if ( category == "SR" ){
        def post = build job: "SR-log-" + prefix, propagate: false
        resultURL = post.getAbsoluteUrl()
    }
    return resultURL
}

def analyzeResult( prop, workSpace, pureTestName, testName, resultURL, wikiLink, isSCPF ){
    // analyzing the result of the test and send to slack if any abnormal result is logged.
    // prop : property dictionary
    // workSpace : workSpace where the result file is saved
    // pureTestName : TestON name of the test
    // testName : Jenkins name of the test. Example: SCPFflowTPFobj
    // resultURL : url for the logs for SR tests. Will not be posted if it is empty
    // wikiLink : link of the wiki page where the result was posted
    // isSCPF : Check if it is SCPF. If so, it won't post the wiki link.

    node( testStation ) {
        def alarmFile = workSpace + "/" + pureTestName + "Alarm.txt"
        if ( fileExists( alarmFile ) ) {
            def alarmContents = readFile( alarmFile )
            slackSend( channel: "#jenkins-related",
                       color: "FF0000",
                       message: "[" + prop[ "ONOSBranch" ] + "]" + testName + " : triggered alarms:\n" +
                                alarmContents + "\n" +
                                "[TestON log] : \n" +
                                "https://jenkins.onosproject.org/blue/organizations/jenkins/${ env.JOB_NAME }/detail/${ env.JOB_NAME }/${ env.BUILD_NUMBER }/pipeline" +
                                ( isSCPF ? "" : ( "\n[Result on Wiki] : \n" +
                                                  "https://wiki.onosproject.org/display/ONOS/" +
                                                  wikiLink.replaceAll( "\\s", "+" ) ) ) +
                                ( resultURL != "" ? ( "\n[Karaf log] : \n" +
                                                      resultURL + "artifact/" ) : "" ),
                       teamDomain: 'onosproject' )
            throw new Exception( "Abnormal test result." )
        }
        else {
            print "Test results are OK."
        }
    }
}

def runTest( testName, toBeRun, prop, pureTestName, graphOnly, testCategory, graph_generator_file,
             graph_saved_directory ){
    // run the test on the machine that contains all the steps : init and run test, copy files, publish result ...
    // testName : name of the test in Jenkins
    // toBeRun : boolean value whether the test will be run or not. If not, it won't be run but shows up with empty
    //           result on pipeline view
    // prop : dictionary property on the machine
    // pureTestName : Pure name of the test. ( ex. pureTestName of SCPFflowTpFobj will be SCPFflowTp )
    // graphOnly : check if it is generating graph job. If so, it will only generate the generating graph part
    // testCategory : Map for the test suit ( SCPF, SR, FUNC, ... ) which contains information about the tests
    // graph_generator_file : Rscript file with the full path.
    // graph_saved_directory : where the generated graph will be saved to.

    return {
        catchError {
            stage( testName ) {
                if ( toBeRun ){
                    def workSpace = "/var/jenkins/workspace/" + testName
                    def fileContents = ""
                    node( testStation ) {
                        withEnv( [ 'ONOSBranch=' + prop[ "ONOSBranch" ],
                                   'ONOSJAVAOPTS=' + prop[ "ONOSJAVAOPTS" ],
                                   'TestONBranch=' + prop[ "TestONBranch" ],
                                   'ONOSTag=' + prop[ "ONOSTag" ],
                                   'WikiPrefix=' + prop[ "WikiPrefix" ],
                                   'WORKSPACE=' + workSpace ] ) {
                            if ( !graphOnly ){
                                if ( isSCPF ){
                                    // Remove the old database file
                                    sh SCPFfuncs.cleanupDatabaseFile( testName )
                                }
                                sh script: initTest(), label: "Test Initialization: stc shutdown; stc teardown; ./cleanup.sh"
                                catchError{
                                    sh script: runTestCli_py( testName, testCategory ), label: ( "Run Test: ./cli.py run " + testName )
                                }
                                catchError{
                                    sh script: concludeRunTest(), label: "Conclude Running Test: ./cleanup.sh; git clean -df"
                                }
                                catchError{
                                    // For the Wiki page
                                    sh script: cleanAndCopyFiles( pureTestName ), label: "Clean and Copy Files"
                                }
                            }
                            graphs.databaseAndGraph( prop, testName, pureTestName, graphOnly,
                                                    graph_generator_file, graph_saved_directory )
                            if ( !graphOnly ){
                                sh script: fetchLogs( pureTestName ), label: "Fetch Logs"
                                if ( !isSCPF ){
                                    publishToConfluence( prop[ "manualRun" ], prop[ "postResult" ],
                                                         prop[ "WikiPrefix" ] + "-" + testCategory[ testName ][ 'wikiName' ],
                                                         workSpace + "/" + testCategory[ testName ][ 'wikiFile' ] )
                                }
                            }
                        }
                    }
                    graphs.postResult( prop, graphOnly, nodeLabel )
                    if ( !graphOnly ){
                        def resultURL = postLogs( testName, prop[ "WikiPrefix" ] )
                        analyzeResult( prop, workSpace, pureTestName, testName, resultURL,
                                       isSCPF ? "" : testCategory[ testName ][ 'wikiName' ],
                                       isSCPF )
                    }
                }
            }
        }
    }
}

def generateGraphs(){
    if ( category != "SCPF" ){
        // generate the overall graph of the non SCPF tests.
        graphs.generateOverallGraph( prop, testsToRun, graphPaths[ "saveDirectory" ], nodeLabel, category )
    }
}

def sendToSlack(){
    // send the result of the test to the slack when it is not manually running.
    // start : start time of the test
    // isManualRun : string that is whether "false" or "true"
    // branch : branch of the onos.

    try {
        if ( prop[ "manualRun" ] == "false" ){
            end = getCurrentTime()
            TimeDuration duration = TimeCategory.minus( end, start )
            // FIXME: for now we disable notifications of normal test results
            /*
            slackSend( color: "#5816EE",
                       message: category + "-" + prop[ "WikiPrefix" ] + " tests ended at: " + end.toString() +
                                "\nTime took : " + duration )
            */
        }
    }
    catch ( all ){
    }
}
