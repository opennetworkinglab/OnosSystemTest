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

// This is the dependency Jenkins script.
// it has some common functions that runs test and generate graph.

import groovy.time.TimeCategory
import groovy.time.TimeDuration

generalFuncs = evaluate readTrusted( 'TestON/JenkinsFile/dependencies/GeneralFuncs.groovy' )
fileRelated = evaluate readTrusted( 'TestON/JenkinsFile/dependencies/JenkinsPathAndFiles.groovy' )
test_list = evaluate readTrusted( 'TestON/JenkinsFile/dependencies/JenkinsTestONTests.groovy' )

fileRelated.init()
test_list.init()

def initializeTrend( machine ){
    // For initializing any trend graph jobs
    // machine : Either VM,BM, or Fabric#

    table_name = "executed_test_tests"
    result_name = "executed_test_results"
    testMachine = "TestStation-" + machine + "s"
    this.machine = machine
    isSCPF = false
    isTrend = true
}

def initialize( type, SCPFfuncs=null ){
    // initializing for FUNC,HA,SR, and USECASE
    // type : type of the test ( SR,FUNC,SCPF... )

    init( type )
    isSCPF = ( type == "SCPF" )
    SCPFfunc = SCPFfuncs

    table_name = "executed_test_tests"
    result_name = "executed_test_results"
    trend_generator_file = fileRelated.trendMultiple
    build_stats_generator_file = fileRelated.histogramMultiple
}

def init( type ){
    // type : type of the test ( SR,FUNC,SCPF... )

    machineType = [ "FUNC": "VM",
                    "HA": "VM",
                    "SR": "Fabric",
                    "SCPF": "BM",
                    "USECASE": "BM" ]
    testType = type
    testMachine = "TestStation-" + machineType[ type ] + "s"
    isTrend = false
}

def additionalInitForSR( branch ){
    // additional setup for SegmentRouting tests to determine the machine depends on the branch it is running.
    // branch : branch of the onos. ( master, 2.1, 1.15... )

    testMachine = ( ( new StringBuilder( testMachine ) ).insert( testMachine.size() - 1, fabricOn( branch ) ) ).
            toString()
    if ( isTrend ){
        machine += fabricOn( branch )
    }
    else {
        machineType[ testType ] += fabricOn( branch )
    }
    print testMachine
}

def fabricOn( branch ){
    // gets the fabric machines with the branch of onos.
    // branch : master, 2.1, 1.15...
    // branch.reverse().take(4).reverse() will get last 4 characters of the string.
    switch ( branch.reverse().take( 3 ).reverse() ){
        case "ter": return "4"
        case "2.1": return "3"
        case "2.0": return "3"
        case ".15": return "2"
        case ".14": return "3"
        case ".13": return "2"
        case ".12": return "3"
        default: return "4"
    }
}

def getProperties( category, branchWithPrefix ){
    // get the properties of the test by reading the TestONOS.property

    filePath = '''/var/jenkins/TestONOS-''' + category + '''-''' + branchWithPrefix + '''.property'''

    node( testMachine ) {
        return readProperties( file: filePath )
    }
}

def getTestsToRun( testList ){
    // get test to run by tokenizing the list.

    testList.tokenize( "\n;, " )
}

def getCurrentTime(){
    // get time of the PST zone.

    TimeZone.setDefault( TimeZone.getTimeZone( 'PST' ) )
    return new Date()
}

def sendResultToSlack( start, isManualRun, branch ){
    // send the result of the test to the slack when it is not manually running.
    // start : start time of the test
    // isManualRun : string that is whether "false" or "true"
    // branch : branch of the onos.

    try {
        if ( isManualRun == "false" ){
            end = getCurrentTime()
            TimeDuration duration = TimeCategory.minus( end, start )
            // FIXME: for now we disable notifications of normal test results
            /*
            slackSend( color: "#5816EE",
                       message: testType + "-" + branch + " tests ended at: " + end.toString() +
                                "\nTime took : " + duration )
            */
        }
    }
    catch ( all ){
    }
}

def initAndRunTest( testName, testCategory ){
    // Bash script that will
    // Initialize the environment to the machine and run the test.
    // testName : name of the test
    // testCategory : (SR,FUNC ... )

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
        ./cleanup.sh -f
        ''' + "./cli.py run " +
          testName +
           " --params GRAPH/nodeCluster=" + machineType[ testType ] + '''
        ./cleanup.sh -f
        # cleanup config changes
        cd ~/onos/tools/package/config
        git clean -df'''
}

def copyLogs(){
    // bash script to copy the logs and other necessary element for SR tests.

    result = ""
    if ( testType == "SR" ){
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

def isPostingResult( manual, postresult ){
    // check if it is posting the result.
    // posting when it is automatically running or has postResult condition from the manual run

    return manual == "false" || postresult == "true"
}

def postResult( prop, graphOnly ){
    // post the result by triggering postjob.
    // prop : property dictionary that was read from the machine.
    // graphOnly : if it is graph generating job

    if ( graphOnly || isPostingResult( prop[ "manualRun" ], prop[ "postResult" ] ) ){
        def post = build job: "postjob-" + ( graphOnly ? machine : machineType[ testType ] ), propagate: false
    }
}

def postLogs( testName, prefix ){
    // posting logs of the onos jobs specifically SR tests
    // testName : name of the test
    // prefix : branch prefix ( master, 2.1, 1.15 ... )

    resultURL = ""
    if ( testType == "SR" ){
        def post = build job: "SR-log-" + prefix, propagate: false
        resultURL = post.getAbsoluteUrl()
    }
    return resultURL
}

def getSlackChannel(){
    // get name of the slack channel.
    // if the test is SR, it will return sr-failures

    // FIXME: For now we move all notifications to #jenkins-related
    // return "#" + ( testType == "SR" ? "sr-failures" : "jenkins-related" )
    return "#jenkins-related"
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

    node( testMachine ) {
        def alarmFile = workSpace + "/" + pureTestName + "Alarm.txt"
        if ( fileExists( alarmFile ) ) {
            def alarmContents = readFile( alarmFile )
            slackSend( channel: getSlackChannel(),
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
            print "Test results are normal."
        }
    }
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
                    node( testMachine ) {
                        withEnv( [ 'ONOSBranch=' + prop[ "ONOSBranch" ],
                                   'ONOSJAVAOPTS=' + prop[ "ONOSJAVAOPTS" ],
                                   'TestONBranch=' + prop[ "TestONBranch" ],
                                   'ONOSTag=' + prop[ "ONOSTag" ],
                                   'WikiPrefix=' + prop[ "WikiPrefix" ],
                                   'WORKSPACE=' + workSpace ] ) {
                            if ( !graphOnly ){
                                if ( isSCPF ){
                                    // Remove the old database file
                                    sh SCPFfunc.cleanupDatabaseFile( testName )
                                }
                                sh initAndRunTest( testName, testCategory )
                                // For the Wiki page
                                sh cleanAndCopyFiles( pureTestName )
                            }
                            databaseAndGraph( prop, testName, pureTestName, graphOnly,
                                              graph_generator_file, graph_saved_directory )
                            if ( !graphOnly ){
                                sh fetchLogs( pureTestName )
                                if ( !isSCPF ){
                                    publishToConfluence( prop[ "manualRun" ], prop[ "postResult" ],
                                                         prop[ "WikiPrefix" ] + "-" + testCategory[ testName ][ 'wikiName' ],
                                                         workSpace + "/" + testCategory[ testName ][ 'wikiFile' ] )
                                }
                            }
                        }
                    }
                    postResult( prop, graphOnly )
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

def databaseAndGraph( prop, testName, pureTestName, graphOnly, graph_generator_file, graph_saved_directory ){
    // part where it insert the data into the database.
    // It will use the predefined encrypted variables from the Jenkins.
    // prop : property dictionary that was read from the machine
    // testName : Jenkins name for the test
    // pureTestName : TestON name for the test
    // graphOnly : boolean whether it is graph only or not
    // graph_generator_file : Rscript file with the full path.
    // graph_saved_directory : where the generated graph will be saved to.
    if ( graphOnly || isPostingResult( prop[ "manualRun" ], prop[ "postResult" ] ) ){
        // Post Results
        withCredentials( [
                string( credentialsId: 'db_pass', variable: 'pass' ),
                string( credentialsId: 'db_user', variable: 'user' ),
                string( credentialsId: 'db_host', variable: 'host' ),
                string( credentialsId: 'db_port', variable: 'port' ) ] ) {
            def database_command = generalFuncs.database_command_create( pass, host, port, user ) +
                                   ( !isSCPF ? sqlCommand( testName ) : SCPFfunc.sqlCommand( testName ) )
            sh '''#!/bin/bash
              export DATE=\$(date +%F_%T)
              cd ~
              pwd ''' + ( graphOnly ? "" :
                          ( !isSCPF ? databasePart( prop[ "WikiPrefix" ], pureTestName, database_command ) :
                            SCPFfunc.databasePart( testName, database_command ) ) ) + '''
              ''' + ( !isSCPF ? graphGenerating( host, port, user, pass, testName, prop, graph_saved_directory,
                                                 graph_generator_file ) :
                      SCPFfunc.getGraphGeneratingCommand( host, port, user, pass, testName, prop ) )
        }
    }
}

def generateCategoryStatsGraph( testMachineOn, manualRun, postresult, stat_file, pie_file, type, branch, testListPart,
                                save_path, pieTestListPart ){
    // function that will generate the category stat graphs for the overall test.
    // testMachineOn : the machine the graph will be generated. It will be TestStation-VMs for the most cases
    // manualRun : string of "true" or "false"
    // postresult : string of "true" or "false"
    // stat_file : file name with full path for Rscript for the stat graph
    // pie_file : file name with full path for Rscript for the pie graph
    // type : type of the test ( USECASE, FUNC, HA )
    // branch : branch of the test ( master, onos-2.1, onos-1.15 )
    // testListPart : list of the test to be included
    // save_path : path that will save the graphs to
    // pieTestListPart : list of the test for pie graph

    if ( isPostingResult( manualRun, postresult ) ){
        node( testMachineOn ) {

            withCredentials( [
                    string( credentialsId: 'db_pass', variable: 'pass' ),
                    string( credentialsId: 'db_user', variable: 'user' ),
                    string( credentialsId: 'db_host', variable: 'host' ),
                    string( credentialsId: 'db_port', variable: 'port' ) ] ) {
                sh '''#!/bin/bash
              ''' + generalFuncs.basicGraphPart( stat_file, host, port, user, pass, type,
                                                 branch ) + " \"" + testListPart + "\" latest " + save_path + '''
              ''' + getOverallPieGraph( pie_file, host, port, user, pass, branch, type, pieTestListPart, 'y',
                                        save_path ) + '''
              ''' +
                   getOverallPieGraph( pie_file, host, port, user, pass, branch, type, pieTestListPart, 'n', save_path )
            }
        }
        postResult( [ ], true )
    }
}


def generateOverallGraph( prop, testCategory, graph_saved_directory ){
    // generate the overall graph for the test

    if ( isPostingResult( prop[ "manualRun" ], prop[ "postResult" ] ) ){
        node( testMachine ) {

            withCredentials( [
                    string( credentialsId: 'db_pass', variable: 'pass' ),
                    string( credentialsId: 'db_user', variable: 'user' ),
                    string( credentialsId: 'db_host', variable: 'host' ),
                    string( credentialsId: 'db_port', variable: 'port' ) ] ) {
                testList = generalFuncs.getTestList( testCategory )
                sh '''#!/bin/bash
                   ''' +
                   generalFuncs.basicGraphPart( trend_generator_file, host, port,
                                                user, pass, testType,
                                                prop[ "ONOSBranch" ] ) + " " + testList + " 20 " + graph_saved_directory
            }
        }
        postResult( prop, false )
    }
}

def getOverallPieGraph( file, host, port, user, pass, branch, type, testList, yOrN, path ){
    // Rcommand for the pie graph

    return generalFuncs.basicGraphPart( file, host, port, user, pass, type, branch ) +
           " \"" + testList + "\" latest " + yOrN + " " + path
}

def sqlCommand( testName ){
    // get the inserting sqlCommand for non-SCPF tests.

    return "\"INSERT INTO " + table_name + " VALUES('\$DATE','" + result_name + "','" +
           testName + "',\$BUILD_NUMBER, '\$ONOSBranch', \$line);\" "
}

def graphGenerating( host, port, user, pass, testName, prop, graph_saved_directory, graph_generator_file ){
    // get the graphGenerating R command for non-SCPF tests

    return generalFuncs.basicGraphPart( graph_generator_file, host, port, user, pass, testName,
                                        prop[ "ONOSBranch" ] ) + " 20 " + graph_saved_directory
}

def databasePart( wikiPrefix, testName, database_command ){
    // to read and insert the data from .csv to the database

    return '''
    sed 1d ''' + workSpace + "/" + wikiPrefix + "-" + testName + '''.csv | while read line
    do
    echo \$line
    echo ''' + database_command + '''
    done '''
}

def generateStatGraph( testMachineOn, onos_branch, stat_graph_generator_file, pie_graph_generator_file,
                       graph_saved_directory ){

    // Will generate the stats graph.
    FUNCtestsStr = test_list.getTestListAsString( test_list.getTestsFromCategory( "FUNC" ) )
    HAtestsStr = test_list.getTestListAsString( test_list.getTestsFromCategory( "HA" ) )
    USECASEtestsStr = test_list.getTestListAsString( test_list.getTestsFromCategory( "USECASE" ) )

    testListParam = "FUNC-"     + FUNCtestsStr + ";" +
                    "HA-"       + HAtestsStr   + ";" +
                    "USECASE-"  + USECASEtestsStr

    pieTestListParam = FUNCtestsStr + "," +
                       HAtestsStr   + "," +
                       USECASEtestsStr

    generateCategoryStatsGraph( testMachineOn, "false", "true", stat_graph_generator_file, pie_graph_generator_file,
                                "ALL", onos_branch, testListParam, graph_saved_directory, pieTestListParam )
}

return this
