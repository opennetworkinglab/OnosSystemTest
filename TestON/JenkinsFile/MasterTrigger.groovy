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

// This is the Jenkins script for master-trigger

// set the functions of the dependencies.
funcs = evaluate readTrusted( 'TestON/JenkinsFile/dependencies/JenkinsCommonFuncs.groovy' )
triggerFuncs = evaluate readTrusted( 'TestON/JenkinsFile/dependencies/TriggerFuncs.groovy' )
fileRelated = evaluate readTrusted( 'TestON/JenkinsFile/dependencies/JenkinsPathAndFiles.groovy' )
test_list = evaluate readTrusted( 'TestON/JenkinsFile/dependencies/JenkinsTestONTests.groovy' )

onos_tag = null
manually_run = null
now = null
today = null
onos_branches = null
day = null
post_result = null
branchesParam = null
isFabric = null
testsParam = null
simulateDay = null

dayMap = [:]
fullDayMap = [:]
all_testcases = [:]
runTest = [:]
selectedTests = [:]
graphPaths = [:]

main()

def main() {
    init()
    runTests()
    generateGraphs()
}

// **************
// Initialization
// **************

// initialize file scope vars
def init(){
    // get the name of the job.
    jobName = env.JOB_NAME

    // set the versions of the onos
    fileRelated.init()
    test_list.init()
    readParams()

    // list of the tests to be run will be saved in each choices.
    day = ""

    initDates()
    onos_branches = getONOSBranches()
    selectedTests = getONOSTests()

    initGraphPaths()

    echo "selectedTests: " + selectedTests
    echo "onos_branches: " + onos_branches
}

def readParams(){
    // get post result from the params for manually run.
    post_result = params.PostResult
    manually_run = params.manual_run
    onos_tag = params.ONOSTag
    branchesParam = params.branches
    isOldFlow = params.isOldFlow
    testsParam = params.Tests
    isFabric = params.isFabric
    simulateDay = params.simulate_day
}

// Set tests based on day of week
def initDates(){
    echo "-> initDates()"
    now = funcs.getCurrentTime()
    dayMap = [ ( Calendar.MONDAY )    : "mon",
               ( Calendar.TUESDAY )   : "tue",
               ( Calendar.WEDNESDAY ) : "wed",
               ( Calendar.THURSDAY )  : "thu",
               ( Calendar.FRIDAY )    : "fri",
               ( Calendar.SATURDAY )  : "sat",
               ( Calendar.SUNDAY )    : "sun" ]
    fullDayMap = [ ( Calendar.MONDAY )    : "Monday",
                   ( Calendar.TUESDAY )   : "Tuesday",
                   ( Calendar.WEDNESDAY ) : "Wednesday",
                   ( Calendar.THURSDAY )  : "Thursday",
                   ( Calendar.FRIDAY )    : "Friday",
                   ( Calendar.SATURDAY )  : "Saturday",
                   ( Calendar.SUNDAY )    : "Sunday" ]
    if ( simulateDay == "" ){
        today = now[ Calendar.DAY_OF_WEEK ]
        day = dayMap[ today ]
        print now.toString()
    } else {
        day = simulateDay
    }
}

// gets ONOS branches from params or string parameter
def getONOSBranches(){
    echo "-> getONOSBranches()"
    if ( manually_run ){
        return branchesParam.tokenize( "\n;, " )
    } else {
        return test_list.getBranchesFromDay( day )
    }
}

def getONOSTests(){
    echo "-> getONOSTests()"
    if ( manually_run ){
        return test_list.getTestsFromStringList( testsParam.tokenize( "\n;, " ) )
    } else {

        return test_list.getTestsFromDay( day )
    }
}

// init paths for the files and directories.
def initGraphPaths(){
    graphPaths.put( "histogramMultiple", fileRelated.histogramMultiple )
    graphPaths.put( "pieMultiple", fileRelated.pieMultiple )
    graphPaths.put( "saveDirectory", fileRelated.jenkinsWorkspace + "postjob-VM/" )
}

// **********************
// Determine Tests to Run
// **********************

def printTestsToRun( runList ){
    if ( manually_run ){
        println "Tests to be run manually:"
    } else {
        if ( isFabric ){
            postToSlackSR()
        }
        if ( today == Calendar.MONDAY ){
            postToSlackTestsToRun()
        }
        println "Defaulting to " + day + " tests:"
    }
    for ( list in runList ){
        echo "" + list
    }
}

def postToSlackSR(){
    // If it is automated running, it will post the beginning message to the channel.
    slackSend( channel: 'sr-failures', color: '#03CD9F',
               message: ":sparkles:" * 16 + "\n" +
                        "Starting tests on : " + now.toString() +
                        "\n" + ":sparkles:" * 16 )
}

def postToSlackTestsToRun(){
    slackSend( color: '#FFD988',
               message: "Tests to be run this weekdays : \n" +
                        triggerFuncs.printDaysForTest() )
}

// *********
// Run Tests
// *********

def generateRunList(){
    runList = [:]
    validSchedules = test_list.getValidSchedules( day )
    echo "validSchedules: " + validSchedules
    for ( branch in onos_branches ){
        runBranch = []
        nodeLabels = test_list.getAllNodeLabels( branch, selectedTests )
        for ( nodeLabel in nodeLabels ){
            selectedNodeLabelTests = test_list.getTestsFromNodeLabel( nodeLabel, branch, selectedTests )
            selectedNodeLabelCategories = test_list.getAllTestCategories( selectedNodeLabelTests )
            for ( category in selectedNodeLabelCategories ){
                selectedNodeLabelCategoryTests = test_list.getTestsFromCategory( category, selectedNodeLabelTests )

                filteredList = [:]
                for ( key in selectedNodeLabelCategoryTests.keySet() ){
                    for ( sch in selectedNodeLabelCategoryTests[ key ][ "schedules" ] ){
                        if ( validSchedules.contains( sch[ "day" ] ) && sch[ "branch" ] == test_list.convertBranchToBranchCode( branch ) || manually_run ){
                            filteredList.put( key, selectedNodeLabelCategoryTests[ key ] )
                            break
                        }
                    }
                }

                echo "=========================================="
                echo "BRANCH: " + branch
                echo "CATEGORY: " + category
                echo "TESTS: " + filteredList
                if ( filteredList != [:] ){
                    exeTestList = test_list.getTestListAsString( filteredList )
                    runList.put( branch + "-" + nodeLabel + "-" + category, triggerFuncs.trigger_pipeline( branch, exeTestList, nodeLabel, category, manually_run, onos_tag ) )
                }

            }
        }
    }
    return runList
}

def runTests(){
    runList = generateRunList()
    printTestsToRun( runList )
    parallel runList
}

// ***************
// Generate Graphs
// ***************

def generateGraphs(){
    // If it is automated running, it will generate the stats graph on VM.
    if ( !manually_run ){
        for ( String b in onos_branches ){
            funcs.generateStatGraph( "TestStation-VMs",
                                     test_list.addPrefixToBranch( b ),
                                     graphPaths[ "histogramMultiple" ],
                                     graphPaths[ "pieMultiple" ],
                                     graphPaths[ "saveDirectory" ] )
        }
    }
}
