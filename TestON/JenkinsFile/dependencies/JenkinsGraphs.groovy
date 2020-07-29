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

fileRelated = evaluate readTrusted( 'TestON/JenkinsFile/dependencies/JenkinsPathAndFiles.groovy' )
test_list = evaluate readTrusted( 'TestON/JenkinsFile/dependencies/JenkinsTestONTests.groovy' )

fileRelated.init()
test_list.init()

testStation = null
isSCPF = null

def initialize( SCPFf=null ){
    isSCPF = ( SCPFf != null )
    SCPFfunc = SCPFf
    trend_generator_file = fileRelated.rScriptPaths[ "scripts" ][ "trendMultiple" ]
    build_stats_generator_file = fileRelated.rScriptPaths[ "scripts" ][ "histogramMultiple" ]
}

def getPostjobType( nodeL ){
    switch ( nodeL ){
        case "Fabric-1.x":
            return "Fabric2"
            break
        case "Fabric-2.x":
            return "Fabric3"
            break
        case "Fabric-master":
            return "Fabric4"
            break
        default:
            return nodeL
            break
    }
}

def postResult( prop, graphOnly, nodeLabel ){
    // post the result by triggering postjob.
    // prop : property dictionary that was read from the machine.
    // graphOnly : if it is graph generating job

    if ( graphOnly || isPostingResult( prop[ "manualRun" ], prop[ "postResult" ] ) ){
        postjob_type = getPostjobType( nodeLabel )
        def post = build job: "postjob-" + postjob_type, propagate: false
    }
}

def isPostingResult( manual, postresult ){
    // check if it is posting the result.
    // posting when it is automatically running or has postResult condition from the manual run

    return manual == "false" || postresult == "true"
}

def database_command_create( pass, host, port, user ){
    return pass + "|psql --host=" + host + " --port=" + port + " --username=" + user + " --password --dbname onostest -c "
}

def databaseAndGraph( prop, JenkinsLabel, TestONTest, graphOnly, graph_generator_file, graph_saved_directory ){
    // part where it insert the data into the database.
    // It will use the predefined encrypted variables from the Jenkins.
    // prop : property dictionary that was read from the machine
    // JenkinsLabel : Jenkins name for the test
    // TestONTest : TestON name for the test
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
            def database_command = database_command_create( pass, host, port, user ) +
                                   ( !isSCPF ? sqlCommand( JenkinsLabel ) : SCPFfunc.sqlCommand( JenkinsLabel ) )
            sh script: '''#!/bin/bash
              export DATE=\$(date +%F_%T)
              cd ~
              pwd ''' + ( graphOnly ? "" :
                          ( !isSCPF ? databasePart( prop[ "WikiPrefix" ], TestONTest, database_command ) :
                            SCPFfunc.databasePart( JenkinsLabel, database_command ) ) ), label: "Database"
            sh script: ( !isSCPF ? graphGenerating( host, port, user, pass, JenkinsLabel, prop, graph_saved_directory,
                                                 graph_generator_file ) :
                      SCPFfunc.getGraphGeneratingCommand( host, port, user, pass, JenkinsLabel, prop ) ), label: "Generate Test Graph"
        }
    }
}

// make the basic graph part for the Rscript
def basicGraphPart( rFileName, host, port, user, pass, subject, branchName ){
    return " Rscript " + rFileName + " " + host + " " + port + " " + user + " " + pass + " " + subject + " " + branchName
}

def generateCategoryStatsGraph( testMachineOn, manualRun, postresult, stat_file, pie_file, type, branch, testListPart,
                                save_path, pieTestListPart, nodeLabel ){
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
                sh script: ( '''#!/bin/bash
              ''' + basicGraphPart( stat_file, host, port, user, pass, type,
                                                 branch ) + " \"" + testListPart + "\" latest " + save_path + '''
              ''' + getOverallPieGraph( pie_file, host, port, user, pass, branch, type, pieTestListPart, 'y',
                                        save_path ) + '''
              ''' + getOverallPieGraph( pie_file, host, port, user, pass, branch, type, pieTestListPart, 'n', save_path ) ), label: "Generate Stats Graphs"
            }
        }
        postResult( [ ], true, nodeLabel )
    }
}


def generateOverallGraph( prop, tests, graph_saved_directory, nodeLabel, testType ){
    // generate the overall graph for the test

    if ( isPostingResult( prop[ "manualRun" ], prop[ "postResult" ] ) ){
        node( testStation ) {

            withCredentials( [
                    string( credentialsId: 'db_pass', variable: 'pass' ),
                    string( credentialsId: 'db_user', variable: 'user' ),
                    string( credentialsId: 'db_host', variable: 'host' ),
                    string( credentialsId: 'db_port', variable: 'port' ) ] ) {
                testList = test_list.getTestListAsString( tests )
                sh script: ( '''#!/bin/bash
                             ''' +
                   basicGraphPart( trend_generator_file, host, port,
                                                user, pass, testType,
                                                prop[ "ONOSBranch" ] ) + " " + testList + " 20 " + graph_saved_directory ), label: "Generate Overall Graph"
            }
        }
        postResult( prop, false, nodeLabel )
    }
}

def getOverallPieGraph( file, host, port, user, pass, branch, type, testList, yOrN, path ){
    // Rcommand for the pie graph

    return basicGraphPart( file, host, port, user, pass, type, branch ) +
           " \"" + testList + "\" latest " + yOrN + " " + path
}

def sqlCommand( testName ){
    // get the inserting sqlCommand for non-SCPF tests.
    // testName : the name the the test results are stored under in the db.
    //            This is usually the same as the Jenkins Test name
    table_name = "executed_test_tests"
    result_name = "executed_test_results"

    return "\"INSERT INTO " + table_name + " VALUES('\$DATE','" + result_name + "','" +
           testName + "',\$BUILD_NUMBER, '\$ONOSBranch', \$line);\" "
}

def graphGenerating( host, port, user, pass, testName, prop, graph_saved_directory, graph_generator_file ){
    // get the graphGenerating R command for non-SCPF tests

    return basicGraphPart( graph_generator_file, host, port, user, pass, testName,
                                        prop[ "ONOSBranch" ] ) + " 20 " + graph_saved_directory
}

def databasePart( wikiPrefix, TestONTest, database_command ){
    // to read and insert the data from .csv to the database

    return '''
    sed 1d ''' + workSpace + "/" + wikiPrefix + "-" + TestONTest + '''.csv | while read line
    do
    echo \$line
    echo ''' + database_command + '''
    done '''
}

def generateStatGraph( testMachineOn, onos_branch, stat_graph_generator_file,
                       pie_graph_generator_file, graph_saved_directory, nodeLabel ){

    table_name = "executed_test_tests"
    result_name = "executed_test_results"

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
                                "ALL", onos_branch, testListParam, graph_saved_directory, pieTestListParam, nodeLabel )
}

return this
