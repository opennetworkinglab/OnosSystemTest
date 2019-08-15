#!groovy
// Copyright 2019 Open Networking Foundation (ONF)
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

//     When there is a new version of ONOS about to release, run this job to create all necessary
//         test result wiki pages.
//
//     In order to create the sub-pages, you need to know the page IDs of the parent pages; for
//         example, if you want to generate the test category pages, you will need the page ID
//         of the top level branch results.

test_list = evaluate readTrusted( 'TestON/JenkinsFile/dependencies/JenkinsTestONTests.groovy' )
test_list.init()

runningNode = "QA"

// set default onos_v to be current_version.
// onos_v needs to be in the format #.##, do not include "ONOS" or "onos"
wikiTestResultsPageID = 1048618
onos_v = params.version
onos_bird = params.bird
top_level_page_id = params.top_level_page_id.toInteger()
FUNC_page_id = params.FUNC_page_id.toInteger()
HA_page_id = params.HA_page_id.toInteger()
SCPF_page_id = params.SCPF_page_id.toInteger()
USECASE_page_id = params.USECASE_page_id.toInteger()
SR_page_id = params.SR_page_id.toInteger()
onos_branch = "ONOS-" + onos_v

SCPF_system_environment = [  "Server: Dual XeonE5-2670 v2 2.5GHz; 64GB DDR3; 512GB SSD",
                             "System clock precision is +/- 1 ms",
                             "1Gbps NIC",
                             "JAVA_OPTS=\"\${JAVA_OPTS:--Xms8G -Xmx8G}\"" ]

// get the name of the job.
jobName = env.JOB_NAME

String[] pagesToPublish = []
String[] pageNames = []
parentID = -1
pageIDProvided = false

if ( top_level_page_id > -1 ){
    pageNames += onos_v + "-CHO"
    pagesToPublish += createCHOpageContents()

    pageNames += onos_v + "-Functionality"
    pagesToPublish += createGeneralPageContents( "FUNC" )

    pageNames += onos_v + "-HA"
    pagesToPublish += createGeneralPageContents( "HA" )

    pageNames += onos_v + "-Performance and Scale-out"
    pagesToPublish += createSCPFpageContents()

    pageNames += onos_v + "-USECASE"
    pagesToPublish += createGeneralPageContents( "USECASE" )

    // pagesToPublish += createGeneralPageContents( "SRHA" )

    parentID = top_level_page_id

    pageIDProvided = true
}

if ( FUNC_page_id > -1 ){
    pageNames += createIndividualPagesNames( "FUNC" )
    pagesToPublish += createIndividualPagesContents( "FUNC" )
    parentID = FUNC_page_id
    pageIDProvided = true
}

if ( HA_page_id > -1 ){
    pageNames += createIndividualPagesNames( "HA" )
    pagesToPublish += createIndividualPagesContents( "HA" )
    parentID = HA_page_id
    pageIDProvided = true
}

if ( SCPF_page_id > -1 ){
    pageNames += onos_v + ": Experiment A&B - Topology (Switch, Link) Event Latency"
    pagesToPublish += createSwitchPortLatPage()

    pageNames += onos_v + ": Experiment C - Intent Install/Remove/Re-route Latency"
    pagesToPublish += createIntentLatencyPage()

    pageNames += onos_v + ": Experiment D - Intents Operations Throughput"
    pagesToPublish += createIntentEventThroughputPage()

    pageNames += onos_v + ": Experiment E - Topology Scaling Operation"
    pagesToPublish += createScaleTopoPage()

    pageNames += onos_v + ": Experiment F - Flow Subsystem Burst Throughput"
    pagesToPublish += createFlowThroughputPage()

    pageNames += onos_v + ": Experiment G - Single-node ONOS Cbench"
    pagesToPublish += createCbenchPage()

    pageNames += onos_v + ": Experiment I - Single Bench Flow Latency Test"
    pagesToPublish += createBatchFlowPage()

    pageNames += onos_v + ": Experiment L - Host Add Latency"
    pagesToPublish += createHostAddLatencyPage()

    pageNames += onos_v + ": Experiment M - Mastership Failover Latency"
    pagesToPublish += createMastershipFailoverLatPage()

    parentID = SCPF_page_id

    pageIDProvided = true
}

if ( USECASE_page_id > -1 ){
    pageNames += onos_v + "-Segment Routing"
    pagesToPublish += createGeneralPageContents( "SR" )
    pageNames += createIndividualPagesNames( "USECASE" )
    pagesToPublish += createIndividualPagesContents( "USECASE" )

    parentID = USECASE_page_id

    pageIDProvided = true
}

if ( SR_page_id > -1 ){
    pageNames += createIndividualPagesNames( "SR" )
    pagesToPublish += createIndividualPagesContents( "SR" )
    parentID = SR_page_id
    pageIDProvided = true
}

if ( !pageIDProvided ){
    pageNames += "ONOS-" + onos_v + " (" + onos_bird + ")"
    pagesToPublish += createTopLevelPageContents()

    parentID = wikiTestResultsPageID
}

echoForDebug( pageNames, pagesToPublish )
node ( label: runningNode ) {
    for ( i in 0..pagesToPublish.length - 1 ){
        publishToConfluence( pageNames[ i ], pagesToPublish[ i ], parentID )
    }
}

def createIndividualPagesNames( category ){
    result = []
    testsFromCategory = test_list.getTestsFromCategory( category )

    for ( String test in testsFromCategory.keySet() ){
        result += onos_v + "-" + testsFromCategory[ test ][ "wikiName" ]
    }
    return result
}

def createIndividualPagesContents( category ){
    result = []
    testsFromCategory = test_list.getTestsFromCategory( category )

    for ( String test in testsFromCategory.keySet() ){
        result += "<p>This test has not run on ONOS-" + onos_v + " yet. Please check again on a later date.</p>"
    }
    return result
}

def publishToConfluence( pageName, contents, parentID ){
    // publish HTML script to wiki confluence
    // isPostResult : string "true" "false"
    // file : name of the file to be published

    if ( parentID > -1 ){
        publishConfluence siteName: 'wiki.onosproject.org', pageName: pageName, spaceName: 'ONOS',
                          attachArchivedArtifacts: true, buildIfUnstable: true, parentId: parentID,
                          editorList: [ confluenceWritePage( confluenceText( contents ) ) ]
    } else {
        publishConfluence siteName: 'wiki.onosproject.org', pageName: pageName, spaceName: 'ONOS',
                          attachArchivedArtifacts: true, buildIfUnstable: true,
                          editorList: [ confluenceWritePage( confluenceText( contents ) ) ]
    }
}

def echoForDebug( pageNames, pagesToPublish ){
    for ( i in 0..pagesToPublish.length - 1 ){
        echo pageNames[ i ]
        echo pagesToPublish[ i ]
    }
}

def makeImage( imageClass, imageLink, width=-1 ){
    if ( width == -1 ){
        return "<p><img class=\"" + imageClass + "\" src=\"" + imageLink + "\" data-image-src=\"" + imageLink + "\"></img></p>"
    } else {
        return "<p><img class=\"" + imageClass + "\" width=\"" + width + "\" src=\"" + imageLink + "\" data-image-src=\"" + imageLink + "\"></img></p>"
    }

}

def pageTree( category, testsFromCategory ){
    pTree = "<ul>"
    if ( category == "USECASE" ){
        pTree += "<li><h3><a href=\"https://wiki.onosproject.org/display/ONOS/" onos_v + "-Segment+Routing" + "\">"
        pTree += "2.2-Segment Routing" + "</a></h3></li>"
    }
    for ( String test in testsFromCategory.keySet() ){
        testTitle = onos_v + "-" + testsFromCategory[ test ][ "wikiName" ]
        pTree += "<li><h3><a href=\"https://wiki.onosproject.org/display/ONOS/" + testTitle + "\">"
        pTree += testTitle + "</a></h3></li>"
    }

    pTree += "</ul>"
    return pTree
}

def createTopLevelPageContents(){
    result = ""
    graphLinkPrefix = "https://jenkins.onosproject.org/view/QA/job/postjob-VM/lastSuccessfulBuild/artifact/ALL_onos-" + onos_v + "_build-latest_"
    executed = graphLinkPrefix + "executed_pieChart.jpg"
    passfail = graphLinkPrefix + "passfail_pieChart.jpg"
    ts_summary = graphLinkPrefix + "test-suite-summary.jpg"

    imageClass = "confluence-embedded-image confluence-external-resource confluence-content-image-border"
    imagesHTML = makeImage( imageClass, executed, 400 ) +
                 makeImage( imageClass, passfail, 400 ) +
                 makeImage( imageClass, ts_summary, 500 )

    pTreeLinkPrefix = "https://wiki.onosproject.org/display/ONOS/"
    pTreeHTML = "<ul>" +
                "<li><h3><a href=\"" + pTreeLinkPrefix + onos_v + "-CHO" + "\">" + onos_v + "-CHO" + "</a></h3></li>" +
                "<li><h3><a href=\"" + pTreeLinkPrefix + onos_v + "-Functionality" + "\">" + onos_v + "-Functionality" + "</a></h3></li>" +
                "<li><h3><a href=\"" + pTreeLinkPrefix + onos_v + "-HA" + "\">" + onos_v + "-HA" + "</a></h3></li>" +
                "<li><h3><a href=\"" + pTreeLinkPrefix + onos_v + "-Performance+and+Scale-out" + "\">" + onos_v + "-Performance and Scale-out" + "</a></h3></li>" +
                "<li><h3><a href=\"" + pTreeLinkPrefix + onos_v + "-USECASE" + "\">" + onos_v + "-USECASE" + "</a></h3></li>" +
                "</ul>"

    result = imagesHTML + pTreeHTML

    return result
}

def createCHOpageContents(){
    result = ""
    testPlan = "https://wiki.onosproject.org/pages/viewpage.action?pageId=2131208"
    description =   "<p>ONOS Apps:</p>" +
                    "<ul>" +
                        "<li>drivers</li>" +
                        "<li>openflow</li>" +
                        "<li>segmentrouting</li>" +
                        "<li>fpm</li>" +
                        "<li>dhcprelay</li>" +
                        "<li>netcfghostprovider</li>" +
                        "<li>routeradvertisement</li>" +
                        "<li>t3</li>" +
                        "<li>hostprobingprovider</li>" +
                    "</ul>" +
                    "<p>Topology:</p>" +
                    "<ul>" +
                        "<li>H-AGG</li>" +
                    "</ul>" +
                    "<p>For more details, check out the <a href=\"" + testPlan + "\"> test plans for CHO</a><br /></p>"

    CHOevents = "https://jenkins.onosproject.org/view/QA/job/postjob-Fabric5/lastSuccessfulBuild/artifact/CHO_Events_onos-" + onos_v + "_168-maxData_graph.jpg"
    CHOfailures = "https://jenkins.onosproject.org/view/QA/job/postjob-Fabric5/lastSuccessfulBuild/artifact/CHO_Failure-Check_onos-" + onos_v + "_168-maxData_graph.jpg"
    CHOerrors = "https://jenkins.onosproject.org/job/postjob-Fabric5/lastSuccessfulBuild/artifact/CHO_Errors_onos-" + onos_v + "_168-maxData_graph.jpg"

    imageClass = "confluence-embedded-image confluence-external-resource confluence-content-image-border"
    images = makeImage( imageClass, CHOevents, 500 ) +
             makeImage( imageClass, CHOfailures, 500 ) +
             makeImage( imageClass, CHOerrors, 500 )

    result = description + images

    return result
}

def createGeneralPageContents( category ){
    result = ""

    overallTrendLink = "https://jenkins.onosproject.org/view/QA/job/postjob-VM/lastSuccessfulBuild/artifact/" + category + "_onos-" + onos_v + "_overview.jpg"
    overallTrendClass = "confluence-embedded-image confluence-external-resource confluence-content-image-border"
    overallTrendHTML = makeImage( overallTrendClass, overallTrendLink, 500 )

    testTrendPrefix = "https://jenkins.onosproject.org/view/QA/job/postjob-VM/lastSuccessfulBuild/artifact/"
    switch ( category ){
        case "FUNC":
            title = "Functionality (FUNC)"
            testPlanLink = "https://wiki.onosproject.org/pages/viewpage.action?pageId=1048600"
            break
        case "HA":
            title = "High Availability (HA)"
            testPlanLink = "https://wiki.onosproject.org/pages/viewpage.action?pageId=1048602"
            break
        case "SR":
            title = "Segment Routing (SR)"
            testPlanLink = "https://wiki.opencord.org/display/CORD/Test+Plan+-+Fabric+Control"
            testTrendPrefix = "https://jenkins.onosproject.org/view/QA/job/postjob-Fabric3/lastSuccessfulBuild/artifact/"
            overallTrendHTML = ""
            break
        case "SRHA":
            title = "Segment Routing High Availability (SRHA)"
            testPlanLink = "https://wiki.opencord.org/display/CORD/Test+Plan+-+Fabric+Control"
            testTrendPrefix = "https://jenkins.onosproject.org/view/QA/job/postjob-Fabric3/lastSuccessfulBuild/artifact/"
            overallTrendHTML = ""
            break
        case "USECASE":
            title = "USECASE"
            testPlanLink = "https://wiki.onosproject.org/pages/viewpage.action?pageId=4163047"
            testTrendPrefix = "https://jenkins.onosproject.org/view/QA/job/postjob-BM/lastSuccessfulBuild/artifact/"
            overallTrendHTML = ""
            break
        default:
            echo "Invalid category: " + category
            return
    }

    titleHTML = "<h1>Test Results - " + title + "</h1>"

    testsFromCategory = test_list.getTestsFromCategory( category )
    pageTreeHTML = pageTree( category, testsFromCategory )

    descriptionHTML = "<p>For test details, check out the <a href=\"" + testPlanLink + "\">test plans for " + category + " test cases</a>.</p>"

    // get the image links for all category tests
    testTrendSuffix = "_onos-" + onos_v + "_20-builds_graph.jpg"

    testGraphsHTML = ""
    testGraphsClass = "confluence-embedded-image confluence-external-resource confluence-content-image-border"


    for ( String key in testsFromCategory.keySet() ){
        imageLink = testTrendPrefix + key + testTrendSuffix
        testGraphsHTML += makeImage( testGraphsClass, imageLink, 500 )
    }
    result = overallTrendHTML + titleHTML + pageTreeHTML + descriptionHTML + testGraphsHTML

    return result
}

def createSCPFpageContents(){
    result = ""

    descriptionHTML =  "<p>" +
                       "The purpose of this page is to track performane trend and regression through the last 50 Jenkins " +
                       "nightly builds on a subset of the full performance evaluation metrics.  Child pages contain full " +
                       "result details on the latest build. Note that results in this tracking may fluctuate from build to " +
                       "build, due to various experiments and changes made in ONOS." +
                       "</p>"

    testPlanLink = "https://wiki.onosproject.org/pages/viewpage.action?pageId=3441823"
    testPlanHTML = "<p>For test details, check out the <a href=\"" + testPlanLink + "\">test plans for Scale-Out and Performance</a>.</p>"

    graphsPrefix = "https://jenkins.onosproject.org/view/QA/job/postjob-BM/lastSuccessfulBuild/artifact/SCPF_Front_Page_"

    testLinkPrefix = "https://wiki.onosproject.org/display/ONOS/"
    graphsClass = "confluence-embedded-image confluence-external-resource confluence-content-image-border"

    switchPortLatencyLink = testLinkPrefix + onos_v + "%3A+Experiment+A%26B+-+Topology+%28Switch,+Link%29+Event+Latency"
    switchLatencyGraphs = [ graphsPrefix + "Switch_Latency_Test_-_Switch_Up_onos-" + onos_v + "_50-dates_graph.jpg",
                            graphsPrefix + "Switch_Latency_Test_-_Switch_Down_onos-" + onos_v + "_50-dates_graph.jpg" ]

    portLatencyGraphs = [ graphsPrefix + "Port_Latency_Test_-_Port_Down_onos-" + onos_v + "_50-dates_graph.jpg",
                          graphsPrefix + "Port_Latency_Test_-_Port_Up_onos-" + onos_v + "_50-dates_graph.jpg" ]

    intentLatencyLink = testLinkPrefix + onos_v + "%3A+Experiment+C+-+Intent+Install%2FRemove%2FRe-route+Latency"
    intentLatencyGraphs = [ graphsPrefix + "Intent_Installation_Test_onos-" + onos_v + "_50-dates_OldFlow_graph.jpg",
                            graphsPrefix + "Intent_Withdrawal_Test_onos-" + onos_v + "_50-dates_OldFlow_graph.jpg",
                            graphsPrefix + "Intent_Reroute_Test_onos-" + onos_v + "_50-dates_OldFlow_graph.jpg" ]

    intentThroughputLink = testLinkPrefix + onos_v + "%3A+Experiment+D+-+Intents+Operations+Throughput"
    intentThroughputGraphs = [ graphsPrefix + "Intent_Throughput_Test_-_neighbors=0_onos-" + onos_v + "_50-dates_OldFlow_graph.jpg" ,
                               graphsPrefix + "Intent_Throughput_Test_-_neighbors=4_onos-" + onos_v + "_50-dates_OldFlow_graph.jpg"]

    scaleTopoLink = testLinkPrefix + onos_v + "%3A+Experiment+E+-+Topology+Scaling+Operation"
    scaleTopoGraphs = [ graphsPrefix + "Scale_Topology_Test_onos-" + onos_v + "_50-dates_graph.jpg" ]

    flowTpLink = testLinkPrefix + onos_v + "%3A+Experiment+F+-+Flow+Subsystem+Burst+Throughput"
    flowTpGraphs = [ graphsPrefix + "Flow_Throughput_Test_-_neighbors=0_onos-" + onos_v + "_50-dates_OldFlow_graph.jpg",
                     graphsPrefix + "Flow_Throughput_Test_-_neighbors=4_onos-" + onos_v + "_50-dates_OldFlow_graph.jpg" ]

    cbenchLink = testLinkPrefix + onos_v + "%3A+Experiment+G+-+Single-node+ONOS+Cbench"
    cbenchGraphs = [ graphsPrefix + "Cbench_Test_onos-" + onos_v + "_50-dates_graph.jpg" ]

    batchFlowLink = testLinkPrefix + onos_v + "%3A+Experiment+I+-+Single+Bench+Flow+Latency+Test"
    batchFlowGraphs = [ graphsPrefix + "Batch_Flow_Test_-_Post_onos-" + onos_v + "_50-dates_OldFlow_graph.jpg",
                        graphsPrefix + "Batch_Flow_Test_-_Del_onos-" + onos_v + "_50-dates_OldFlow_graph.jpg" ]

    hostAddLink = testLinkPrefix + onos_v + "%3A+Experiment+L+-+Host+Add+Latency"
    hostAddLatencyGraphs = [ graphsPrefix + "Host_Latency_Test_onos-" + onos_v + "_50-dates_graph.jpg" ]

    mastershipFailoverLatencyLink = testLinkPrefix + onos_v + "%3A+Experiment+M+-+Mastership+Failover+Latency"
    mastershipFailoverLatencyGraphs = [ graphsPrefix + "Mastership_Failover_Test_onos-" + onos_v + "_50-dates_graph.jpg" ]

    // Create the HTML for the SCPF page

    switchLatencyHTML = "<h3><a href=\"" + switchPortLatencyLink + "\">Switch Latency</a>: Last 50 Builds - \"SwitchUp\" and \"SwitchDown\" Latency Tests</h3>" +
                              "<ul><li><h3>5-Node Cluster</h3></li></ul>" +
                              makeImage( graphsClass, switchLatencyGraphs[ 0 ], 500 ) +
                              makeImage( graphsClass, switchLatencyGraphs[ 1 ], 500 )

    portLatencyHTML = "<h3><a href=\"" + switchPortLatencyLink + "\">Port Latency</a>: Last 50 Builds - \"PortUp\" and \"PortDown\" Latency Tests</h3>" +
                            "<ul><li><h3>5-Node Cluster</h3></li></ul>" +
                            makeImage( graphsClass, portLatencyGraphs[ 0 ], 500 ) +
                            makeImage( graphsClass, portLatencyGraphs[ 1 ], 500 )

    intentLatencyHTML =   "<h3><a href=\"" + intentLatencyLink + "\">Intent Latency</a>: Last 50 Builds - \"IntentInstallLat\", \"IntentWithdrawLat\" and \"IntentRerouteLat\"Tests</h3>" +
                                "<ul>" +
                                    "<li><h3>5-Node Cluster</h3></li>" +
                                    "<li><h3>100 Intent Batch Size</h3></li>" +
                                "</ul>" +
                                makeImage( graphsClass, intentLatencyGraphs[ 0 ], 500 ) +
                                makeImage( graphsClass, intentLatencyGraphs[ 1 ], 500 ) +
                                makeImage( graphsClass, intentLatencyGraphs[ 2 ], 500 )

    intentThroughputHTML =  "<h3><a href=\"" + intentThroughputLink + "\">Intent Latency</a>: Last 50 Builds - \"IntentEventTP\" Test</h3>" +
                            "<ul>" +
                                "<li><h3>5-Node Cluster</h3></li>" +
                            "</ul>" +
                            makeImage( graphsClass, intentThroughputGraphs[ 0 ], 500 ) +
                            makeImage( graphsClass, intentThroughputGraphs[ 1 ], 500 )

    scaleTopoHTML = "<h3><a href=\"" + scaleTopoLink + "\">Scale Topo Test</a>: Last 50 Builds - \"scaleTopo\" Test</h3>" +
                    "<ul>" +
                        "<li><h3>3-Node Cluster</h3></li>" +
                        "<li><h3>20 Scaling</h3></li>" +
                    "</ul>" +
                    makeImage( graphsClass, scaleTopoGraphs[ 0 ], 500 )

    flowThroughputHTML = "<h3><a href=\"" + flowTpLink + "\">Flow Throughput</a>: Last 50 Builds - \"flowTP1g\" Test</h3>" +
                         "<ul>" +
                             "<li><h3>5-Node Cluster</h3></li>" +
                         "</ul>" +
                         makeImage( graphsClass, flowTpGraphs[ 0 ], 500 ) +
                         makeImage( graphsClass, flowTpGraphs[ 1 ], 500 )

    cbenchHTML = "<h3><a href=\"" + cbenchLink + "\">Cbench</a>: Last 50 Builds - \"CbenchBM\" Test</h3>" +
                 "<ul>" +
                     "<li><h3>Single-Node</h3></li>" +
                     "<li><h3>Throughput Mode</h3></li>" +
                 "</ul>" +
                 makeImage( graphsClass, cbenchGraphs[ 0 ], 500 )

    batchFlowHTML = "<h3><a href=\"" + batchFlowLink + "\">Single Bench Flow Latency Test</a>: Last 50 Builds - \"SingleBenchFlow\" Latency Test</h3>" +
                    makeImage( graphsClass, batchFlowGraphs[ 0 ], 500 ) +
                    makeImage( graphsClass, batchFlowGraphs[ 1 ], 500 )

    hostAddHTML = "<h3><a href=\"" + hostAddLink + "\">Host Add Latency</a>: Last 50 Builds - \"HostAddLatency\" Test</h3>" +
                  "<ul>" +
                      "<li><h3>5-Node Cluster</h3></li>" +
                  "</ul>" +
                  makeImage( graphsClass, hostAddLatencyGraphs[ 0 ], 500 )

    mastershipFailoverLatencyHTML = "<h3><a href=\"" + mastershipFailoverLatencyLink + "\">Mastership Failover Latency</a>: Last 50 Builds - \"MastershipFailoverLat\" Test</h3>" +
                                    "<ul>" +
                                        "<li><h3>5-Node Cluster</h3></li>" +
                                    "</ul>" +
                                    makeImage( graphsClass, mastershipFailoverLatencyGraphs[ 0 ], 500 )

    result = descriptionHTML +
             testPlanHTML +
             switchLatencyHTML +
             portLatencyHTML +
             intentLatencyHTML +
             intentThroughputHTML +
             scaleTopoHTML +
             flowThroughputHTML +
             cbenchHTML +
             batchFlowHTML +
             hostAddHTML +
             mastershipFailoverLatencyHTML

    return result
}

def makeSCPFInfoSection( title, list ){
    result = "<p>" + title + ":</p><ul>"
    for ( String app in list ){
        result += "<li>" + app + "</li>"
    }
    result += "</ul>"
    return result
}

def makeSCPFindividualGraphs( graphsList ){
    result = ""
    graphsClass = "confluence-embedded-image confluence-external-resource confluence-content-image-border"
    for ( String graph in graphsList ){
        result += makeImage( graphsClass, graph, 500 )
    }
    return result
}

def makeSCPFnote( note ){
    return "<p>" + note + "</p>"
}

def makeErrorBarsDisclaimer(){
    return "<p>Note: Error bars in the graphs below represent standard deviations. Only the upper error bars are shown.</p>"
}

def makeOldFlowDisclaimer(){
    return "<p>Following graphs include results using flow rule stores with both strong consistency and eventual consistency models. The ONOS team is still working on performance improvements for flow rule store with strong consistency.</p>"
}

def createSwitchPortLatPage(){
    result = ""
    result += makeSCPFInfoSection( "System Env", SCPF_system_environment )

    result += makeSCPFInfoSection( "ONOS Apps", [ "drivers",
                                                  "metrics",
                                                  "openflow" ] )

    result += makeSCPFInfoSection( "ONOS Config", [ "cfg set org.onosproject.net.topology.impl.DefaultTopologyProvider maxEvents 1",
                                                    "cfg set org.onosproject.net.topology.impl.DefaultTopologyProvider maxBatchMs 0",
                                                    "cfg set org.onosproject.net.topology.impl.DefaultTopologyProvider maxIdleMs 0" ] )

    result += makeSCPFInfoSection( "Test Procedure", [ "Switch event generate on ONOS1 by connecting ovs switch to it.",
                                                       "Record tshark (tcp syn-ack) and graph event timestamp to calculate differences."] )

    result += makeErrorBarsDisclaimer()

    graphLinkPrefix = "https://jenkins.onosproject.org/view/QA/job/postjob-BM/lastSuccessfulBuild/artifact/"
    result += makeSCPFindividualGraphs( [ graphLinkPrefix + "SCPFswitchLat_onos-" + onos_v + "_UpErrBarWithStack.jpg",
                                          graphLinkPrefix + "SCPFswitchLat_onos-" + onos_v + "_DownErrBarWithStack.jpg",
                                          graphLinkPrefix + "SCPFportLat_onos-" + onos_v + "_UpErrBarWithStack.jpg",
                                          graphLinkPrefix + "SCPFportLat_onos-" + onos_v + "_DownErrBarWithStack.jpg" ] )

    return result
}

def createIntentLatencyPage(){
    result = ""
    result += makeSCPFInfoSection( "System Env", SCPF_system_environment )

    result += makeSCPFInfoSection( "ONOS Apps", [ "drivers",
                                                  "null" ] )

    result += makeSCPFInfoSection( "ONOS Config", [ "cfg set org.onosproject.net.intent.impl.compiler.IntentConfigurableRegistrator useFlowObjectives true (when using flow objective intents compiler)",
                                                    "cfg set org.onosproject.net.intent.impl.compiler.IntentConfigurableRegistrator defaultFlowObjectiveCompiler org.onosproject.net.intent.impl.compiler.LinkCollectionIntentObjectiveCompiler (when using flow objective intents compiler)",
                                                    "cfg set org.onosproject.net.intent.impl.IntentManager skipReleaseResourcesOnWithdrawal true" ] )

    result += makeSCPFInfoSection( "Test Procedure", [ "Intent batch installed from ONOS1",
                                                       "Record returned response time"] )

    result += makeErrorBarsDisclaimer()
    result += makeOldFlowDisclaimer()

    graphLinkPrefix = "https://jenkins.onosproject.org/view/QA/job/postjob-BM/lastSuccessfulBuild/artifact/"
    result += makeSCPFindividualGraphs( [ graphLinkPrefix + "SCPFIntentInstallWithdrawRerouteLat_onos-" + onos_v + "_OldFlow_1-batchSize_graph.jpg",
                                          graphLinkPrefix + "SCPFIntentInstallWithdrawRerouteLat_onos-" + onos_v + "_OldFlow_100-batchSize_graph.jpg",
                                          graphLinkPrefix + "SCPFIntentInstallWithdrawRerouteLat_onos-" + onos_v + "_OldFlow_1000-batchSize_graph.jpg",
                                          graphLinkPrefix + "SCPFIntentInstallWithdrawRerouteLat_onos-" + onos_v + "_fobj_OldFlow_1-batchSize_graph.jpg",
                                          graphLinkPrefix + "SCPFIntentInstallWithdrawRerouteLat_onos-" + onos_v + "_fobj_OldFlow_100-batchSize_graph.jpg",
                                          graphLinkPrefix + "SCPFIntentInstallWithdrawRerouteLat_onos-" + onos_v + "_fobj_OldFlow_1000-batchSize_graph.jpg" ] )

    return result
}

def createIntentEventThroughputPage(){
    result = ""
    result += makeSCPFInfoSection( "System Env", SCPF_system_environment )

    result += makeSCPFInfoSection( "ONOS Apps", [ "drivers",
                                                  "null",
                                                  "intentpref" ] )

    result += makeSCPFInfoSection( "ONOS Config", [ "cfg set org.onosproject.net.intent.impl.IntentManager skipReleaseResourcesOnWithdrawal true",
                                                    "cfg set org.onosproject.net.intent.impl.compiler.IntentConfigurableRegistrator useFlowObjectives true (when using flow objective intents compiler)",
                                                    "cfg set org.onosproject.net.intent.impl.compiler.IntentConfigurableRegistrator defaultFlowObjectiveCompiler org.onosproject.net.intent.impl.compiler.LinkCollectionIntentObjectiveCompiler (when using flow objective intents compiler)" ] )

    result += makeSCPFInfoSection( "\"Constant-Load\" Test Conditions", [ "new NumKeys - 40000",
                                                                          "with eventually consistent flow rule - 40000",
                                                                          "with Flow Obj - 4000"] )

    result += makeOldFlowDisclaimer()

    graphLinkPrefix = "https://jenkins.onosproject.org/view/QA/job/postjob-BM/lastSuccessfulBuild/artifact/"
    result += makeSCPFindividualGraphs( [ graphLinkPrefix + "SCPFintentEventTp_onos-" + onos_v + "_no-neighbors_OldFlow_graph.jpg",
                                          graphLinkPrefix + "SCPFintentEventTp_onos-" + onos_v + "_all-neighbors_OldFlow_graph.jpg",
                                          graphLinkPrefix + "SCPFintentEventTpWithFlowObj_onos-" + onos_v + "_no-neighbors_flowObj_OldFlow_graph.jpg",
                                          graphLinkPrefix + "SCPFintentEventTpWithFlowObj_onos-" + onos_v + "_all-neighbors_flowObj_OldFlow_graph.jpg" ] )

    return result
}

def createScaleTopoPage(){
    result = ""
    result += makeSCPFInfoSection( "System Env", SCPF_system_environment )

    result += makeSCPFInfoSection( "ONOS Apps", [ "drivers",
                                                  "openflow" ] )

    result += makeSCPFnote( "Note: We use 3-node ONOS cluster and torus Mininet topology in this test. In the figure below, scale N on x-axis means N x N torus topology. (E.g. scale 5 means 25 switches and 100 links)" )

    graphLinkPrefix = "https://jenkins.onosproject.org/view/QA/job/postjob-BM/lastSuccessfulBuild/artifact/"
    result += makeSCPFindividualGraphs( [ graphLinkPrefix + "SCPFscaleTopo_onos-" + onos_v + "_graph.jpg" ] )

    return result
}

def createFlowThroughputPage(){
    result = ""
    result += makeSCPFInfoSection( "System Env", SCPF_system_environment )

    result += makeSCPFInfoSection( "ONOS Apps", [ "drivers",
                                                  "null",
                                                  "demo" ] )

    result += makeSCPFInfoSection( "ONOS Config", [ "cfg set org.onosproject.provider.nil.NullProviders deviceCount 35",
                                                    "cfg set org.onosproject.provider.nil.NullProviders topoShape linear",
                                                    "cfg set org.onosproject.provider.nil.NullProviders enabled true" ] )

    result += makeSCPFInfoSection( "\"Constant-Load\" Test Conditions", [ "F = eventually consistent flows rule - 122500, 10000 with FlowObj - total # of flows installed",
                                                                          "N: # of neighboring ONOS's for flows to be installed when ONOS1 is the server installing flows",
                                                                          "S: #servers installing flows",
                                                                          "SW = 35 - total # of switches (Null Devices) connected to ONOS cluster evenly distributed to active ONOS nodes",
                                                                          "FL: # flows to be installed on each switch" ] )

    result += makeSCPFInfoSection( "Command", [ "python3 \$ONOS_ROOT/tools/tests/bin/flow-tester.py -f FL -n N -s servers" ] )

    result += makeErrorBarsDisclaimer()
    result += makeOldFlowDisclaimer()

    graphLinkPrefix = "https://jenkins.onosproject.org/view/QA/job/postjob-BM/lastSuccessfulBuild/artifact/"
    result += makeSCPFindividualGraphs( [ graphLinkPrefix + "SCPFflowTp1g_onos-" + onos_v + "_no-neighbors_OldFlow_graph.jpg",
                                          graphLinkPrefix + "SCPFflowTp1g_onos-" + onos_v + "_all-neighbors_OldFlow_graph.jpg",
                                          graphLinkPrefix + "SCPFflowTp1gWithFlowObj_onos-" + onos_v + "_no-neighbors_flowObj_OldFlow_graph.jpg",
                                          graphLinkPrefix + "SCPFflowTp1gWithFlowObj_onos-" + onos_v + "_all-neighbors_flowObj_OldFlow_graph.jpg" ] )

    return result
}

def createCbenchPage(){
    result = ""
    result += makeSCPFInfoSection( "System Env", SCPF_system_environment )

    result += makeSCPFInfoSection( "ONOS Apps", [ "drivers",
                                                  "openflow-base",
                                                  "_OldFlow_DelGraph" ] )

    result += makeSCPFInfoSection( "ONOS Config", [ "cfg set org.onosproject.fwd.ReactiveForwarding packetOutOnly true" ] )

    result += makeErrorBarsDisclaimer()

    graphLinkPrefix = "https://jenkins.onosproject.org/view/QA/job/postjob-BM/lastSuccessfulBuild/artifact/"
    result += makeSCPFindividualGraphs( [ graphLinkPrefix + "SCPFcbench_onos-" + onos_v + "_errGraph.jpg" ] )

    return result
}

def createBatchFlowPage(){
    result = ""
    result += makeSCPFInfoSection( "System Env", SCPF_system_environment )

    result += makeSCPFInfoSection( "ONOS Apps", [ "drivers",
                                                  "openflow-base" ] )

    result += makeSCPFInfoSection( "\"Constant-Load\" Test Conditions", [ "batchSize = eventually consistent flows rule - 200" ] )

    result += makeOldFlowDisclaimer()

    graphLinkPrefix = "https://jenkins.onosproject.org/view/QA/job/postjob-BM/lastSuccessfulBuild/artifact/"
    result += makeSCPFindividualGraphs( [ graphLinkPrefix + "SCPFbatchFlowResp_onos-" + onos_v + "_OldFlow_PostGraph.jpg",
                                          graphLinkPrefix + "SCPFbatchFlowResp_onos-" + onos_v + "_OldFlow_DelGraph.jpg" ] )

    return result
}

def createHostAddLatencyPage(){
    result = ""

    result += makeSCPFInfoSection( "System Env", SCPF_system_environment )

    result += makeSCPFInfoSection( "ONOS Apps", [ "drivers",
                                                  "metrics",
                                                  "openflow",
                                                  "proxyarp" ] )

    result += makeSCPFInfoSection( "ONOS Config", [ "cfg set org.onosproject.net.topology.impl.DefaultTopologyProvider maxEvents 1",
                                                    "cfg set org.onosproject.net.topology.impl.DefaultTopologyProvider maxBatchMs 0",
                                                    "cfg set org.onosproject.net.topology.impl.DefaultTopologyProvider maxIdleMs 0" ] )

    result += makeErrorBarsDisclaimer()

    graphLinkPrefix = "https://jenkins.onosproject.org/view/QA/job/postjob-BM/lastSuccessfulBuild/artifact/"
    result += makeSCPFindividualGraphs( [ graphLinkPrefix + "SCPFhostLat_onos-" + onos_v + "_errGraph.jpg" ] )

    return result
}

def createMastershipFailoverLatPage(){
    result = ""

    result += makeSCPFInfoSection( "System Env", SCPF_system_environment )

    result += makeSCPFInfoSection( "ONOS Apps", [ "drivers",
                                                  "openflow",
                                                  "events" ] )

    result += makeErrorBarsDisclaimer()

    graphLinkPrefix = "https://jenkins.onosproject.org/view/QA/job/postjob-BM/lastSuccessfulBuild/artifact/"
    result += makeSCPFindividualGraphs( [ graphLinkPrefix + "SCPFmastershipFailoverLat_onos-" + onos_v + "_stackedGraph.jpg",
                                          graphLinkPrefix + "SCPFmastershipFailoverLat_onos-" + onos_v + "_errGraph.jpg" ] )

    return result
}
