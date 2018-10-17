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
// This will provide the SCPF specific functions

fileRelated = evaluate readTrusted( 'TestON/JenkinsFile/dependencies/JenkinsPathAndFiles.groovy' )

fileRelated.init()

def init(){
    // init step for SCPF functions. It has some mandatory init steps

    // none, batches, neighbors, times : to be used for extra parameters for generating graphs.
    def none = [ "" ]
    def batches = [ 1, 100, 1000 ]
    def neighbors = [ 'y', 'n' ]
    def times = [ 'y', 'n' ]

    //flows : whether the test is affected by oldFlow or newFlow
    // test : command of the test to be executed when running the test
    // table : name of the view table on database
    // result : name of the actual table on database
    // file : name of the file that contains the result of the test to be used to insert data to database
    // rFile : specific Rscript file name to be used to generate each SCPF graph. For with flowObj graphs, you need to put 'n' or 'y' after the test name
    // extra : extra condition that will be used for Rscript parameter. Some of the Rscript requires extra parameters like if it has
    //         neighbors or batches. In this case, it will generate Rscript x times of what extra has. So that it will generate one with
    //         neighbor = y and the other with neighbor = n
    // finalResult : If you want to generate overall graph for the front page.
    // graphTitle : title for the graph. It should contain n numbers depends on how many graphs you are generating.
    // [Optional]
    // dbCols : specific dbColumns to choose for 50 data overall graph if there is one.
    // dbWhere : specific where statement that has some condition for 50 data overall graph if there is one.
    // y_axis : title of the y_axis to be shown for 50 data overall graph if there is one.

    SCPF = [
            SCPFcbench: [ flows: false,
                          test: 'SCPFcbench',
                          table: 'cbench_bm_tests',
                          results: 'cbench_bm_results',
                          file: 'CbenchDB',
                          rFile: 'SCPFcbench.R',
                          extra: none,
                          finalResult: 1,
                          graphTitle: [ 'Cbench Test' ],
                          dbCols: 'avg',
                          dbWhere: '',
                          y_axis: 'Throughput (Responses/sec)' ],
            SCPFhostLat: [ flows: false,
                           test: 'SCPFhostLat',
                           table: 'host_latency_tests',
                           results: 'host_latency_results',
                           file: 'HostAddLatency',
                           rFile: 'SCPFhostLat.R',
                           extra: none,
                           finalResult: 1,
                           graphTitle: [ 'Host Latency Test' ],
                           dbCols: 'avg',
                           dbWhere: 'AND scale=5',
                           y_axis: 'Latency (ms)' ],
            SCPFportLat: [ flows: false,
                           test: 'SCPFportLat',
                           table: 'port_latency_details',
                           results: 'port_latency_results',
                           file: '/tmp/portEventResultDb',
                           rFile: 'SCPFportLat.R',
                           extra: none,
                           finalResult: 1,
                           graphTitle: [ 'Port Latency Test - Port Up', 'Port Latency Test - Port Down' ],
                           dbCols: [ 'up_ofp_to_dev_avg, up_dev_to_link_avg, up_link_to_graph_avg',
                                     'down_ofp_to_dev_avg, down_dev_to_link_avg, down_link_to_graph_avg' ],
                           dbWhere: 'AND scale=5', y_axis: 'Latency (ms)' ],
            SCPFflowTp1g: [ flows: true,
                            test: 'SCPFflowTp1g',
                            table: 'flow_tp_tests',
                            results: 'flow_tp_results',
                            file: 'flowTP1gDB',
                            rFile: 'SCPFflowTp1g.R n',
                            extra: neighbors,
                            finalResult: 1,
                            graphTitle: [ 'Flow Throughput Test - neighbors=0',
                                          'Flow Throughput Test - neighbors=4' ],
                            dbCols: 'avg',
                            dbWhere: [ 'AND scale=5 AND neighbors=0 ',
                                       'AND scale=5 AND NOT neighbors=0' ],
                            y_axis: 'Throughput (,000 Flows/sec)' ],
            SCPFflowTp1gWithFlowObj: [ flows: true,
                                       test: 'SCPFflowTp1g --params TEST/flowObj=True',
                                       table: 'flow_tp_fobj_tests',
                                       results: 'flow_tp_fobj_results',
                                       file: 'flowTP1gDBFlowObj',
                                       rFile: 'SCPFflowTp1g.R y',
                                       extra: neighbors,
                                       finalResult: 0 ],
            SCPFscaleTopo: [ flows: false,
                             test: 'SCPFscaleTopo',
                             table: 'scale_topo_latency_details',
                             results: 'scale_topo_latency_results',
                             file: '/tmp/scaleTopoResultDb',
                             rFile: 'SCPFscaleTopo.R',
                             extra: none,
                             finalResult: 1,
                             graphTitle: [ 'Scale Topology Test' ],
                             dbCols: [ 'first_connection_to_last_connection, last_connection_to_last_role_request, last_role_request_to_last_topology' ],
                             dbWhere: 'AND scale=20',
                             y_axis: 'Latency (s)' ],
            SCPFswitchLat: [ flows: false,
                             test: 'SCPFswitchLat',
                             table: 'switch_latency_details',
                             results: 'switch_latency_results',
                             file: '/tmp/switchEventResultDb',
                             rFile: 'SCPFswitchLat.R',
                             extra: none,
                             finalResult: 1,
                             graphTitle: [ 'Switch Latency Test - Switch Up',
                                           'Switch Latency Test - Switch Down' ],
                             dbCols: [ 'tcp_to_feature_reply_avg,feature_reply_to_device_avg,up_device_to_graph_avg',
                                       'fin_ack_to_ack_avg,ack_to_device_avg,down_device_to_graph_avg' ],
                             dbWhere: 'AND scale=5',
                             y_axis: 'Latency (ms)' ],
            SCPFbatchFlowResp: [ flows: true,
                                 test: 'SCPFbatchFlowResp',
                                 table: 'batch_flow_tests',
                                 results: 'batch_flow_results',
                                 file: 'SCPFbatchFlowRespData',
                                 rFile: 'SCPFbatchFlowResp.R',
                                 extra: none,
                                 finalResult: 1,
                                 graphTitle: [ 'Batch Flow Test - Post',
                                               'Batch Flow Test - Del' ],
                                 dbCols: [ 'elapsepost, posttoconfrm',
                                           'elapsedel, deltoconfrm' ],
                                 dbWhere: '',
                                 y_axis: 'Latency (s)' ],
            SCPFintentEventTp: [ flows: true,
                                 test: 'SCPFintentEventTp',
                                 table: 'intent_tp_tests',
                                 results: 'intent_tp_results',
                                 file: 'IntentEventTPDB',
                                 rFile: 'SCPFintentEventTp.R n',
                                 extra: neighbors,
                                 finalResult: 1,
                                 graphTitle: [ 'Intent Throughput Test - neighbors=0',
                                               'Intent Throughput Test - neighbors=4' ],
                                 dbCols: 'SUM( avg ) as avg',
                                 dbWhere: [ 'AND scale=5 AND neighbors=0 GROUP BY date,build',
                                            'AND scale=5 AND NOT neighbors=0 GROUP BY date,build' ],
                                 y_axis: 'Throughput (Ops/sec)' ],
            SCPFintentRerouteLat: [ flows: true,
                                    test: 'SCPFintentRerouteLat',
                                    table: 'intent_reroute_latency_tests',
                                    results: 'intent_reroute_latency_results',
                                    file: 'IntentRerouteLatDB',
                                    rFile: 'SCPFIntentInstallWithdrawRerouteLat.R n',
                                    extra: batches,
                                    finalResult: 1,
                                    graphTitle: [ 'Intent Reroute Test' ],
                                    dbCols: 'avg',
                                    dbWhere: 'AND scale=5 AND batch_size=100',
                                    y_axis: 'Latency (ms)' ],
            SCPFscalingMaxIntents: [ flows: true,
                                     test: 'SCPFscalingMaxIntents',
                                     table: 'max_intents_tests',
                                     results: 'max_intents_results',
                                     file: 'ScalingMaxIntentDB',
                                     rFile: 'SCPFscalingMaxIntents.R n',
                                     extra: none,
                                     finalResult: 0 ],
            SCPFintentEventTpWithFlowObj: [ flows: true,
                                            test: 'SCPFintentEventTp --params TEST/flowObj=True',
                                            table: 'intent_tp_fobj_tests',
                                            results: 'intent_tp_fobj_results',
                                            file: 'IntentEventTPflowObjDB',
                                            rFile: 'SCPFintentEventTp.R y',
                                            extra: neighbors,
                                            finalResult: 0 ],
            SCPFintentInstallWithdrawLat: [ flows: true,
                                            test: 'SCPFintentInstallWithdrawLat',
                                            table: 'intent_latency_tests',
                                            results: 'intent_latency_results',
                                            file: 'IntentInstallWithdrawLatDB',
                                            rFile: 'SCPFIntentInstallWithdrawRerouteLat.R n',
                                            extra: batches,
                                            finalResult: 1,
                                            graphTitle: [ 'Intent Installation Test',
                                                          'Intent Withdrawal Test' ],
                                            dbCols: [ 'install_avg', 'withdraw_avg' ],
                                            dbWhere: 'AND scale=5 AND batch_size=100',
                                            y_axis: 'Latency (ms)' ],
            SCPFintentRerouteLatWithFlowObj: [ flows: true,
                                               test: 'SCPFintentRerouteLat --params TEST/flowObj=True',
                                               table: 'intent_reroute_latency_fobj_tests',
                                               results: 'intent_reroute_latency_fobj_results',
                                               file: 'IntentRerouteLatDBWithFlowObj',
                                               rFile: 'SCPFIntentInstallWithdrawRerouteLat.R y',
                                               extra: batches,
                                               finalResult: 0 ],
            SCPFscalingMaxIntentsWithFlowObj: [ flows: true,
                                                test: 'SCPFscalingMaxIntents --params TEST/flowObj=True',
                                                table: 'max_intents_fobj_tests',
                                                results: 'max_intents_fobj_results',
                                                file: 'ScalingMaxIntentDBWFO',
                                                rFile: 'SCPFscalingMaxIntents.R y',
                                                extra: none,
                                                finalResult: 0 ],
            SCPFintentInstallWithdrawLatWithFlowObj: [ flows: true,
                                                       test: 'SCPFintentInstallWithdrawLat --params TEST/flowObj=True',
                                                       table: 'intent_latency_fobj_tests',
                                                       results: 'intent_latency_fobj_results',
                                                       file: 'IntentInstallWithdrawLatDBWFO',
                                                       rFile: 'SCPFIntentInstallWithdrawRerouteLat.R y',
                                                       extra: batches,
                                                       finalResult: 0 ],
            SCPFmastershipFailoverLat: [ flows: false,
                                         test: 'SCPFmastershipFailoverLat',
                                         table: 'mastership_failover_tests',
                                         results: 'mastership_failover_results',
                                         file: 'mastershipFailoverLatDB',
                                         rFile: 'SCPFmastershipFailoverLat.R',
                                         extra: none,
                                         finalResult: 1,
                                         graphTitle: [ 'Mastership Failover Test' ],
                                         dbCols: [ 'kill_deact_avg,deact_role_avg' ],
                                         dbWhere: 'AND scale=5',
                                         y_axis: 'Latency (ms)' ]
    ]
    graph_saved_directory = fileRelated.jenkinsWorkspace + "postjob-BM/"
}

def getGraphCommand( rFileName, extras, host, port, user, pass, testName, branchName, isOldFlow ){
    // generate the list of Rscript command for individual graphs

    result = ""
    for ( extra in extras ){
        result += generateGraph( rFileName, " " + extra, host, port, user, pass, testName, branchName, isOldFlow ) + ";"
    }
    return result
}

def generateGraph( rFileName, batch, host, port, user, pass, testName, branchName, isOldFlow ){
    //  generate the Rscript command for individual graphs

    return generalFuncs.basicGraphPart( fileRelated.SCPFSpecificLocation + rFileName,
                                        host, port, user, pass, testName, branchName ) +
           " " + batch + " " + usingOldFlow( isOldFlow, testName ) + graph_saved_directory
}

def generateCombinedResultGraph( host, port, user, pass, testName, branchName, isOldFlow ){
    // generate Rscript for overall graph for the front page.
    def result = ""

    for ( int i = 0; i < SCPF[ testName ][ 'graphTitle' ].size(); i++ ){
        result += generalFuncs.basicGraphPart( fileRelated.trendSCPF,
                                               host,
                                               port,
                                               user,
                                               pass,
                                               "\"" + SCPF[ testName ][ 'graphTitle' ][ i ] + "\"",
                                               branchName ) +
                  " " + 50 + " \"SELECT " +
                  checkIfList( testName, 'dbCols', i ) +
                  ", build FROM " + SCPF[ testName ][ 'table' ] + " WHERE  branch=\'" + branchName + "\' " +
                  sqlOldFlow( isOldFlow, testName ) +
                  checkIfList( testName, 'dbWhere', i ) +
                  " ORDER BY date DESC LIMIT 50\" \"" +
                  SCPF[ testName ][ 'y_axis' ] + "\" " +
                  hasOldFlow( isOldFlow, testName ) +
                  graph_saved_directory + ";"
    }
    return result
}

def checkIfList( testName, forWhich, pos ){
    // check if some dictionary has list or string.

    return SCPF[ testName ][ forWhich ].getClass().getName() != "java.lang.String" ?
           SCPF[ testName ][ forWhich ][ pos ] :
           SCPF[ testName ][ forWhich ]
}

def sqlOldFlow( isOldFlow, testName ){
    // sql where command part for checking old flows.

    return SCPF[ testName ][ 'flows' ] ? " AND " + ( isOldFlow ? "" : "NOT " ) + "is_old_flow " : ""
}

def oldFlowRuleCheck( isOldFlow, branch ){
    // checking if it is old flow

    this.isOldFlow = isOldFlow
    if ( !isOldFlow ){
        SCPF[ 'SCPFflowTp1g' ][ 'test' ] += " --params TEST/flows=" + ( branch == "onos-1.11" ? "4000" : "3500" )
    }
}

def affectedByOldFlow( isOldFlow, testName ){
    // For sql command :  if the test is affect by old flow, it will return parameters for old flow
    return SCPF[ testName ][ 'flows' ] ? "" + isOldFlow + ", " : ""
}

def usingOldFlow( isOldFlow, testName ){
    // For Rscript command : if it is using old flow.

    return SCPF[ testName ][ 'flows' ] ? ( isOldFlow ? "y" : "n" ) + " " : ""
}

def hasOldFlow( isOldFlow, testName ){
    // For Rscript command for 50 data

    return ( SCPF[ testName ][ 'flows' ] && isOldFlow ? "y" : "n" ) + " "
}

def sqlCommand( testName ){
    // sql command for inserting data into the database

    if ( testName == "SCPFscaleTopo" || testName == "SCPFswitchLat" || testName == "SCPFportLat" ){
        return "\"INSERT INTO " + SCPF[ testName ][ 'table' ] + " VALUES( '\$DATE','" +
               SCPF[ testName ][ 'results' ] + "','\$BUILD_NUMBER', \$line, '\$ONOSBranch');\""
    }
    return "\"INSERT INTO " + SCPF[ testName ][ 'table' ] + " VALUES( '\$DATE','" + SCPF[ testName ][ 'results' ] +
           "','\$BUILD_NUMBER', '\$ONOSBranch', " + affectedByOldFlow( isOldFlow, testName ) + "\$line);\""
}

def cleanupDatabaseFile( testName ){
    // clean up the database file created under /tmp
    return 'rm /tmp/' + SCPF[ testName ][ 'file' ]
}

def databasePart( testName, database_command ){
    // read the file from the machine and insert it to the database

    return '''
    cd /tmp
    while read line
    do
    echo \$line
    echo ''' + database_command + '''
    done< ''' + SCPF[ testName ][ 'file' ]
}

def getGraphGeneratingCommand( host, port, user, pass, testName, prop ){
    // returns the combined Rscript command for each test.

    return getGraphCommand( SCPF[ testName ][ 'rFile' ],
                            SCPF[ testName ][ 'extra' ],
                            host, port, user, pass, testName,
                            prop[ "ONOSBranch" ], isOldFlow ) + '''
    ''' + ( SCPF[ testName ][ 'finalResult' ] ?
            generateCombinedResultGraph( host, port, user, pass, testName, prop[ "ONOSBranch" ], isOldFlow ) : "" )
}

return this
