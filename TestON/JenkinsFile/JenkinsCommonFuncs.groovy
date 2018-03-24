#!groovy
import groovy.time.*
generalFuncs = evaluate readTrusted( 'TestON/JenkinsFile/GeneralFuncs.groovy' )

def initializeTrend( machine ){
  table_name = "executed_test_tests"
  result_name = "executed_test_results"
  testMachine = "TestStation-" + machine + "s";
  this.machine = machine
  isSCPF = false
  generalFuncs.initBasicVars();
}
def initialize( type, SCPFfuncs ){
  init( type )
  SCPFfunc = SCPFfuncs
  isSCPF = true
  machine = machineType[ type ]
}
def initialize( type ){
  init( type )
  SCPFfunc = null
  table_name = "executed_test_tests"
  result_name = "executed_test_results"
  trend_generator_file = generalFuncs.rScriptLocation + "testCategoryTrend.R"
  build_stats_generator_file = generalFuncs.rScriptLocation + "testCategoryBuildStats.R"
  isSCPF = false
}
def init( type ){
  machineType = [ "FUNC"    : "VM",
                  "HA"      : "VM",
                  "SR"      : "Fabric",
                  "SCPF"    : "BM",
                  "USECASE" : "BM" ]
  testType = type;
  testMachine = "TestStation-" + machineType[ type ] + "s";
  generalFuncs.initBasicVars();
}

def printType(){
  echo testType;
  echo testMachine;
}
def getProperties(){
  node( testMachine ){
    return readProperties( file:'/var/jenkins/TestONOS.property' );
  }
}
def getTestsToRun( testList ){
  testList.tokenize("\n;, ")
}
def getCurrentTime(){
  TimeZone.setDefault( TimeZone.getTimeZone('PST') )
  return new Date();
}
def getTotalTime( start, end ){
  return TimeCategory.minus( end, start );
}
def printTestToRun( testList ){
  for ( String test : testList ) {
      println test;
  }
}
def sendResultToSlack( start, isManualRun, branch ){
  try{
    if( isManualRun == "false" ){
        end = getCurrentTime();
        TimeDuration duration = TimeCategory.minus( end , start );
        slackSend( color:"#5816EE",
                   message: testType + "-" + branch + " tests ended at: " + end.toString() + "\nTime took : " + duration )
    }
  }
  catch( all ){}
}
def initAndRunTest( testName, testCategory ){
  // after ifconfig : ''' + borrowCell( testName ) + '''
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
        git log |head
        ./cleanup.sh -f
        ''' + "./cli.py run " + ( !isSCPF ? testName : testCategory[ testName ][ 'test' ] )  + '''
        ./cleanup.sh -f
        # cleanup config changes
        cd ~/onos/tools/package/config
        git clean -df'''
}
def copyLogs( testName ){
  result = ""
    if( testType == "SR" ){
      result = '''
      sudo rm /var/jenkins/workspace/SR-log-${WikiPrefix}/*
      sudo cp *karaf.log.* /var/jenkins/workspace/SR-log-${WikiPrefix}/
      sudo cp *Flows* /var/jenkins/workspace/SR-log-${WikiPrefix}/
      sudo cp *Groups* /var/jenkins/workspace/SR-log-${WikiPrefix}/
      '''
  }
  return result
}
def cleanAndCopyFiles( testName ){
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
        sudo rm ${WORKSPACE}/*.csv
        #copy files to workspace
        cd `ls -t ~/OnosSystemTest/TestON/logs/*/ | head -1 | sed 's/://'`
        ''' + copyLogs( testName ) + '''
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
  return '''#!/bin/bash
  set +e
  cd ~/OnosSystemTest/TestON/logs
  echo "Job Name is: " + ''' + testName + '''
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
      for i in $OC{1..7}; do onos-fetch-logs $i || echo log does not exist; done
  fi
  cd'''
}
def isPostingResult( manual, postresult ){
  return manual == "false" || postresult == "true"
}
def postResult( prop, graphOnly ){
  if( graphOnly || isPostingResult( prop[ "manualRun" ], prop[ "postResult" ] ) ){
    def post = build job: "postjob-" + ( graphOnly ? machine : machineType[ testType ] ), propagate: false
  }
}
def postLogs( testName, prefix ){
  resultURL = ""
  if( testType == "SR" ){
    def post = build job: "SR-log-" + prefix, propagate: false
    resultURL = post.getAbsoluteUrl()
  }
  return resultURL
}
def getSlackChannel(){
  return "#" + ( testType == "SR" ? "sr-failures" : "jenkins-related" )
}
def analyzeResult( prop, workSpace, testName, otherTestName, resultURL, wikiLink, isSCPF ){
  node( testMachine ){
    resultContents = readFile workSpace + "/" + testName + "Result.txt"
    resultContents = resultContents.split("\n")
    if( resultContents[ 0 ] == "1" ){
        print "All passed"
    }else{
        print "Failed"
      if( prop[ "manualRun" ] == "false" ){
        slackSend( channel:getSlackChannel(), color:"FF0000", message: "[" + prop[ "ONOSBranch" ] + "]"
                                            + otherTestName + " : Failed!\n" + resultContents[ 1 ] + "\n"
                                            + "[TestON log] : \n"
                                            + "https://jenkins.onosproject.org/blue/organizations/jenkins/${env.JOB_NAME}/detail/${env.JOB_NAME}/${env.BUILD_NUMBER}/pipeline"
                                            + ( isSCPF ? "" : ( "\n[Result on Wiki] : \n" + "https://wiki.onosproject.org/display/ONOS/" + wikiLink.replaceAll( "\\s","+" ) ) )
                                            + ( resultURL != "" ? ( "\n[Karaf log] : \n" + resultURL + "artifact/" ) : "" ),
                   teamDomain: 'onosproject' )
      }
        Failed
    }
  }
}
def publishToConfluence( isManualRun, isPostResult, wikiLink, file ){
  if( isPostingResult( isManualRun, isPostResult ) ){
    publishConfluence siteName: 'wiki.onosproject.org', pageName: wikiLink, spaceName: 'ONOS',
                  attachArchivedArtifacts: true, buildIfUnstable: true,
                  editorList: [
                      confluenceWritePage( confluenceFile( file ) )
                  ]
  }

}
def runTest( testName, toBeRun, prop, pureTestName, graphOnly, testCategory, graph_generator_file, graph_saved_directory ) {
  return {
      catchError{
          stage( testName ) {
              if ( toBeRun ){
                  workSpace = "/var/jenkins/workspace/" + testName
                  def fileContents = ""
                  node( testMachine ){
                      withEnv( [ 'ONOSBranch=' + prop[ "ONOSBranch" ],
                                 'ONOSJVMHeap=' + prop[ "ONOSJVMHeap" ],
                                 'TestONBranch=' + prop[ "TestONBranch" ],
                                 'ONOSTag=' + prop[ "ONOSTag" ],
                                 'WikiPrefix=' + prop[ "WikiPrefix" ],
                                 'WORKSPACE=' + workSpace ] ){
                        if( ! graphOnly ){
                          sh initAndRunTest( testName, testCategory )
                          // For the Wiki page
                          sh cleanAndCopyFiles( pureTestName )
                        }
                          databaseAndGraph( prop, testName, graphOnly, graph_generator_file, graph_saved_directory )
                        if( ! graphOnly ){
                          sh fetchLogs( pureTestName )
                          if( !isSCPF )
                            publishToConfluence( prop[ "manualRun" ], prop[ "postResult" ],
                                                 testCategory[ testName ][ 'wiki_link' ],
                                                 workSpace + "/" + testCategory[ testName ][ 'wiki_file' ] )
                        }
                      }


                  }
                    postResult( prop, graphOnly )
                  if( ! graphOnly ){
                    resultURL = postLogs( testName, prop[ "WikiPrefix" ] )
                    analyzeResult( prop, workSpace, pureTestName, testName, resultURL, isSCPF ? "" : testCategory[ testName ][ 'wiki_link' ], isSCPF )
                  }
              }
          }
      }
  }
}
def borrowCell( testName ){
  result = ""
  if( testType == "SR" ){
      result = '''
      cd
      source ~/borrow.cell
      '''
  }
  return result
}
def databaseAndGraph( prop, testName, graphOnly, graph_generator_file, graph_saved_directory ){
  if( graphOnly || isPostingResult( prop[ "manualRun" ], prop[ "postResult" ] ) ){
      // Post Results
      withCredentials( [
          string( credentialsId: 'db_pass', variable: 'pass' ),
          string( credentialsId: 'db_user', variable: 'user' ),
          string( credentialsId: 'db_host', variable: 'host' ),
          string( credentialsId: 'db_port', variable: 'port' ) ] ) {
              def database_command =  generalFuncs.database_command_create( pass, host, port, user ) + ( !isSCPF ? sqlCommand( testName ) : SCPFfunc.sqlCommand( testName ) )
              sh '''#!/bin/bash
              export DATE=\$(date +%F_%T)
              cd ~
              pwd ''' + ( graphOnly ? "" : ( !isSCPF ? databasePart( prop[ "WikiPrefix" ], testName, database_command )  :
                         SCPFfunc.databasePart( testName, database_command ) ) ) + '''
              ''' + ( !isSCPF ? graphGenerating( host, port, user, pass, testName, prop, graph_saved_directory, graph_generator_file ) : SCPFfunc.getGraphGeneratingCommand( host, port, user, pass, testName, prop ) )
      }
  }
}
def generateCategoryStatsGraph( manualRun, postresult, stat_file, pie_file, type, branch, testListPart, save_path, pieTestListPart ){

  if( isPostingResult( manualRun, postresult ) ){
    node( testMachine ){

      withCredentials( [
          string( credentialsId: 'db_pass', variable: 'pass' ),
          string( credentialsId: 'db_user', variable: 'user' ),
          string( credentialsId: 'db_host', variable: 'host' ),
          string( credentialsId: 'db_port', variable: 'port' ) ] ) {
              sh '''#!/bin/bash
              ''' + generalFuncs.basicGraphPart( generalFuncs.rScriptLocation + stat_file, host, port, user, pass, type, branch ) + " \"" + testListPart + "\" latest " + save_path + '''
              ''' + getOverallPieGraph( generalFuncs.rScriptLocation + pie_file, host, port, user, pass, branch, type, pieTestListPart, 'y', save_path ) + '''
              ''' + getOverallPieGraph( generalFuncs.rScriptLocation + pie_file, host, port, user, pass, branch, type, pieTestListPart, 'n', save_path )
          }
        }
      postResult( [], true )
    }
}
def makeTestList( list, commaNeeded ){
  return generalFuncs.getTestList( list ) + ( commaNeeded ? "," : "" )
}
def createStatsList( testCategory, list, semiNeeded ){
  return testCategory + "-" + generalFuncs.getTestList( list ) + ( semiNeeded ? ";" : "" )
}
def generateOverallGraph( prop, testCategory, graph_saved_directory ){

  if( isPostingResult( prop[ "manualRun" ], prop[ "postResult" ] ) ){
    node( testMachine ){

      withCredentials( [
          string( credentialsId: 'db_pass', variable: 'pass' ),
          string( credentialsId: 'db_user', variable: 'user' ),
          string( credentialsId: 'db_host', variable: 'host' ),
          string( credentialsId: 'db_port', variable: 'port' ) ] ) {
              testList = generalFuncs.getTestList( testCategory )
              sh '''#!/bin/bash
              ''' + generalFuncs.basicGraphPart( trend_generator_file, host, port, user, pass, testType, prop[ "ONOSBranch" ] ) + " " + testList + " 20 " + graph_saved_directory
          }
        }
      postResult( prop, false )
    }
}
def getOverallPieGraph( file, host, port, user, pass, branch, type, testList, yOrN, path ){
   return generalFuncs.basicGraphPart( file, host, port, user, pass, type, branch ) + " \"" + testList + "\" latest " + yOrN + " " + path
}
def sqlCommand( testName ){
  return "\"INSERT INTO " + table_name + " VALUES('\$DATE','" + result_name + "','" + testName + "',\$BUILD_NUMBER, '\$ONOSBranch', \$line);\" "
}
def graphGenerating( host, port, user, pass, testName, prop, graph_saved_directory, graph_generator_file ){
  return generalFuncs.basicGraphPart( graph_generator_file, host, port, user, pass, testName, prop[ "ONOSBranch" ] ) + " 20 " + graph_saved_directory
}
def databasePart( wikiPrefix, testName, database_command ){
  return '''
    sed 1d ''' + workSpace + "/" + wikiPrefix + "-" + testName + '''.csv | while read line
    do
    echo \$line
    echo ''' + database_command + '''
    done '''
}
def generateStatGraph( onos_branch, AllTheTests, stat_graph_generator_file, pie_graph_generator_file, graph_saved_directory ){
    testListPart = createStatsList( "FUNC", AllTheTests[ "FUNC" ], true ) +
                   createStatsList( "HA", AllTheTests[ "HA" ], true ) +
                   createStatsList( "USECASE", AllTheTests[ "USECASE" ], false )
    pieTestList = makeTestList( AllTheTests[ "FUNC" ], true ) +
                  makeTestList( AllTheTests[ "HA" ], true ) +
                  makeTestList( AllTheTests[ "USECASE" ], false )
    generateCategoryStatsGraph( "false", "true", stat_graph_generator_file, pie_graph_generator_file, "ALL", onos_branch, testListPart, graph_saved_directory, pieTestList )
}
def branchWithPrefix( branch ){
    return ( ( branch != "master" ) ? "onos-" : "" ) + branch
}
return this;
