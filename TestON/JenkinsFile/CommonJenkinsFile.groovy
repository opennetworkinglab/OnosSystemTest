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
testsToRunStrList = null
branch = null
branchWithPrefix = null
start = null
nodeLabel = null
testStation = null
testsOverride = null
isGraphOnly = false
isSCPF = false
pipelineTimeout = null

testsToRun = [:]
testsFromList = [:]
graphPaths = [:]
pipeline = [:]

main()

def main(){
    pipelineTimeout = params.TimeOut.toInteger() // integer minutes until the entire pipeline times out. Usually passed from upstream master-trigger job.
    timeout( time: pipelineTimeout, unit: "MINUTES" ){
        init()
        runTests()
        generateGraphs()
        sendToSlack()
    }
}

def init(){
    fileRelated.init()
    test_list.init()
    readParams()

    if ( branch == "manually" ){
        echo '''Warning: entered branch was: "manually". Defaulting to master branch.'''
        branch = "master"
        branchWithPrefix = test_list.addPrefixToBranch( branch )
    }

    if ( category == "SCPF" ){
        isSCPF = true
        SCPFfuncs.init()
        graphs.initialize( SCPFfuncs );
        prop = getProperties()
        isOldFlow = ( prop[ "isOldFlow" ] == "true" )
        SCPFfuncs.oldFlowRuleCheck( isOldFlow, prop[ "ONOSBranch" ] )
    } else {
        isSCPF = false
        graphs.initialize()
        prop = getProperties()
    }

    // get the list of the tests from category
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
    if ( category == "SR" || category == "SR-StratumBMv2" || category == "SR-Tofino" ){
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
    for ( String JenkinsLabel : testsFromList.keySet() ){
        toBeRun = testsToRun.keySet().contains( JenkinsLabel )
        stepName = ( toBeRun ? "" : "Not " ) + "Running $JenkinsLabel"

        TestONTest = ( toBeRun && testsToRun[ JenkinsLabel ].keySet().contains( "test" ) ) ? testsToRun[ JenkinsLabel ][ "test" ] : JenkinsLabel

        pipeline[ stepName ] = runTest( JenkinsLabel,
                                        toBeRun,
                                        prop,
                                        TestONTest,
                                        isGraphOnly,
                                        testsToRun,
                                        graphPaths[ "trendIndividual" ],
                                        graphPaths[ "saveDirectory" ] )
    }

    // get the start time of the test.
    start = getCurrentTime()

    // run the tests sequentially.
    for ( JenkinsLabel in pipeline.keySet() ){
        pipeline[ JenkinsLabel ].call()
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

def configureJavaVersion(){
    java_1_8_branches = [ "1.15" ]
    return '''#!/bin/bash -l
        ''' + ( java_1_8_branches.contains( branch ) ? '''SET_JAVA_VER=java-8-oracle''' : '''SET_JAVA_VER=java-1.11.0-openjdk-amd64''' ) +
        '''
           CELL_COUNT=$( env | egrep "OC[1-9]+" | wc -l )
           for i in $(seq 1 $CELL_COUNT)
           do
               CELL_TO_SET=$( env | egrep "OC$i" | cut -c5- )
               echo "Setting java to $SET_JAVA_VER on $CELL_TO_SET"
               eval ssh $CELL_TO_SET 'sudo update-java-alternatives -s $SET_JAVA_VER'
           done
        '''
}

def runTestCli_py( testName, testArguments ){
    // Bash script that will run the test.
    // testName : name of the test in TestON
    // testArguments : Arguments to be passed to the test framework

    command = '''cd ~/OnosSystemTest/TestON/bin
                 ./cli.py run ''' + testName + ''' --params GRAPH/nodeCluster=''' + graphs.getPostjobType( nodeLabel ) + ''' ''' + testArguments
    echo command

    return command


}

def concludeRunTest(){
    // TODO: Add cleanup for if we use docker containers
    return '''cd ~/OnosSystemTest/TestON/bin
              ./cleanup.sh -f || true
              # cleanup config changes
              cd ~/onos/tools/package/config
              git clean -df'''
}

def copyLogs(){
    // bash script to copy the logs and other necessary element for SR tests.

    result = ""
    if ( category == "SR" || category == "SR-StratumBMv2" || category == "SR-Tofino" ){
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

def cleanAndCopyFiles( JenkinsLabel ){
    // clean up some files that were in the folder and copy the new files from the log
    // JenkinsLabel : name of the test in Jenkins

    return '''#!/bin/bash -i
        set +e
        echo "ONOS Branch is: ${ONOSBranch}"
        echo "TestON Branch is: ${TestONBranch}"
        echo "Job name is: "''' + JenkinsLabel + '''
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

def fetchLogs( JenkinsLabel ){
    // fetch the logs of onos from onos nodes to onos System Test logs
    // JenkinsLabel : name of the test in Jenkins

    return '''#!/bin/bash
  set +e
  cd ~/OnosSystemTest/TestON/logs
  echo "TestON test name is: "''' + JenkinsLabel + '''
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

    if ( graphs.isPostingResult( isManualRun, isPostResult ) ){
        publishConfluence siteName: 'wiki.onosproject.org', pageName: wikiLink, spaceName: 'ONOS',
                          attachArchivedArtifacts: true, buildIfUnstable: true,
                          editorList: [ confluenceWritePage( confluenceFile( file ) ) ]
    }
}

def postLogs( prefix ){
    // posting logs of the onos jobs specifically SR tests
    // prefix : branch prefix ( master, 2.1, 1.15 ... )

    resultURL = ""
    if ( category == "SR" || category == "SR-StratumBMv2" || category == "SR-Tofino" ){
        def post = build job: "SR-log-" + prefix, propagate: false
        resultURL = post.getAbsoluteUrl()
    }
    return resultURL
}

def analyzeResult( prop, workSpace, TestONTest, JenkinsLabel, resultURL, wikiLink, isSCPF ){
    // analyzing the result of the test and send to slack if any abnormal result is logged.
    // prop : property dictionary
    // workSpace : workSpace where the result file is saved
    // TestONTest : TestON name of the test
    // JenkinsLabel : Jenkins name of the test. Example: SCPFflowTPFobj
    // resultURL : url for the logs for SR tests. Will not be posted if it is empty
    // wikiLink : link of the wiki page where the result was posted
    // isSCPF : Check if it is SCPF. If so, it won't post the wiki link.

    node( testStation ) {
        def alarmFile = workSpace + "/" + TestONTest + "Alarm.txt"
        if ( fileExists( alarmFile ) ) {
            def alarmContents = readFile( alarmFile )
            slackSend( channel: "#jenkins-related",
                       color: "FF0000",
                       message: "[" + prop[ "ONOSBranch" ] + "] " + JenkinsLabel + " : triggered alarms:\n" +
                                alarmContents + "\n" +
                                "[TestON log] : \n" +
                                "https://jenkins.onosproject.org/blue/organizations/jenkins/${ env.JOB_NAME }/detail/${ env.JOB_NAME }/${ env.BUILD_NUMBER }/pipeline" +
                                ( isSCPF ? "" : ( "\n[Result on Wiki] : \n" +
                                                  "https://wiki.onosproject.org/display/ONOS/" +
                                                  wikiLink.replaceAll( "\\s", "+" ) ) ) +
                                ( resultURL != "" ? ( "\n[Karaf log] : \n" +
                                                      resultURL + "artifact/" ) : "" ),
                       teamDomain: 'onosproject' )
            print "Abnormal test result."
            throw new Exception( "Abnormal test result." )
        }
        else {
            print "Test results are OK."
        }
    }
}

def runTest( JenkinsLabel, toBeRun, prop, TestONTest, graphOnly, testCategory,
             graph_generator_file, graph_saved_directory ){
    // run the test on the machine that contains all the steps : init and run test, copy files, publish result ...
    // JenkinsLabel : name of the test in Jenkins
    // toBeRun : boolean value whether the test will be run or not. If not, it won't be run but shows up with empty
    //           result on pipeline view
    // prop : dictionary property on the machine
    // TestONTest : Pure name of the test. ( ex. TestONTest of SCPFflowTpFobj will be SCPFflowTp )
    // graphOnly : check if it is generating graph job. If so, it will only generate the generating graph part
    // testCategory : Map for the test suit ( SCPF, SR, FUNC, ... ) which contains information about the tests
    // graph_generator_file : Rscript file with the full path.
    // graph_saved_directory : where the generated graph will be saved to.

    return {
        catchError {
            stage( JenkinsLabel ) {
                if ( toBeRun ){
                    def workSpace = "/var/jenkins/workspace/" + JenkinsLabel
                    def fileContents = ""
                    testArguments = testCategory[ JenkinsLabel ].keySet().contains( "arguments" ) ? testCategory[ JenkinsLabel ][ "arguments" ] : ""
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
                                    sh SCPFfuncs.cleanupDatabaseFile( JenkinsLabel )
                                }
                                sh script: configureJavaVersion(), label: "Configure Java Version"
                                sh script: initTest(), label: "Test Initialization: stc shutdown; stc teardown; ./cleanup.sh"
                                catchError{
                                    sh script: runTestCli_py( TestONTest, testArguments ), label: ( "Run Test: ./cli.py run " + TestONTest + " " + testArguments )
                                }
                                catchError{
                                    sh script: concludeRunTest(), label: "Conclude Running Test: ./cleanup.sh; git clean -df"
                                }
                                catchError{
                                    // For the Wiki page
                                    sh script: cleanAndCopyFiles( TestONTest ), label: "Clean and Copy Files"
                                }
                            }
                            graphs.databaseAndGraph( prop, JenkinsLabel, TestONTest, graphOnly,
                                                     graph_generator_file, graph_saved_directory )
                            if ( !graphOnly ){
                                sh script: fetchLogs( TestONTest ), label: "Fetch Logs"
                                if ( !isSCPF ){
                                    publishToConfluence( prop[ "manualRun" ], prop[ "postResult" ],
                                                         prop[ "WikiPrefix" ] + "-" + testCategory[ JenkinsLabel ][ 'wikiName' ],
                                                         workSpace + "/" + testCategory[ JenkinsLabel ][ 'wikiFile' ] )
                                }
                            }
                        }
                    }
                    graphs.postResult( prop, graphOnly, nodeLabel )
                    if ( !graphOnly ){
                        def resultURL = postLogs( prop[ "WikiPrefix" ] )
                        analyzeResult( prop, workSpace, TestONTest, JenkinsLabel, resultURL,
                                       isSCPF ? "" : testCategory[ JenkinsLabel ][ 'wikiName' ],
                                       isSCPF )
                    }
                } else {
                    echo JenkinsLabel + " is not being run today. Leaving the rest of stage contents blank."
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
