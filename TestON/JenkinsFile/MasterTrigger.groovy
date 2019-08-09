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

import groovy.time.TimeCategory
import groovy.time.TimeDuration

// set the functions of the dependencies.
graphs = evaluate readTrusted( 'TestON/JenkinsFile/dependencies/JenkinsGraphs.groovy' )
fileRelated = evaluate readTrusted( 'TestON/JenkinsFile/dependencies/JenkinsPathAndFiles.groovy' )
test_list = evaluate readTrusted( 'TestON/JenkinsFile/dependencies/JenkinsTestONTests.groovy' )

INITIALIZATION_TIMEOUT_MINUTES = 10 // timeout init() function if it takes too long.

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
pipelineTimeOut = null

dayMap = [:]
fullDayMap = [:]
all_testcases = [:]
runTest = [:]
selectedTests = [:]
graphPaths = [:]

main()

def main() {
    timeout( time: INITIALIZATION_TIMEOUT_MINUTES, unit: "MINUTES" ){
        init()
    }
    if ( selectedTests == [:] && manually_run ){
        echo "No valid tests provided. Check if the provided test(s) is/are in test.json, and try again.\n\nProvided Tests:\n" + testsParam
        throw new Exception( "No valid tests provided. Check if the provided test(s) is/are in test.json, and try again." )
    }
    timeout( time: pipelineTimeOut, unit: "MINUTES" ){
        runTests()
        generateGraphs()
    }
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
    isOldFlow = true // hardcoding to true since we are always using oldFlow.
    testsParam = params.Tests
    isFabric = params.isFabric
    simulateDay = params.simulate_day
    pipelineTimeOut = params.TimeOut.toInteger()
}

// Set tests based on day of week
def initDates(){
    echo "-> initDates()"
    now = getCurrentTime()
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

def getCurrentTime(){
    // get time of the PST zone.

    TimeZone.setDefault( TimeZone.getTimeZone( 'PST' ) )
    return new Date()
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
    graphPaths.put( "histogramMultiple", fileRelated.rScriptPaths[ "scripts" ][ "histogramMultiple" ] )
    graphPaths.put( "pieMultiple", fileRelated.rScriptPaths[ "scripts" ][ "pieMultiple" ] )
    graphPaths.put( "saveDirectory", fileRelated.workspaces[ "VM" ] )
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
                        printDaysForTest() )
}

def printDaysForTest(){
    // Print the days for what test has.
    AllTheTests = test_list.getAllTests()

    result = ""
    for ( String test in AllTheTests.keySet() ){
        result += test + ": ["
        test_schedule = AllTheTests[ test ][ "schedules" ]
        for ( String sch_dict in test_schedule ){
            for ( String day in test_list.convertScheduleKeyToDays( sch_dict[ "branch" ] ) ){
                result += day + " "
            }
        }
        result += "]\n"
    }
    return result
}

// *********
// Run Tests
// *********

def tagCheck( onos_tag, onos_branch ){
    // check the tag for onos if it is not empty

    result = "git checkout "
    if ( onos_tag == "" ){
        //create new local branch
        result += onos_branch
    }
    else {
        //checkout the tag
        result += onos_tag
    }
    return result
}

def preSetup( onos_branch, test_branch, onos_tag, isManual ){
    // pre setup part which will clean up and checkout to corresponding branch.

    result = ""
    if ( !isManual ){
        result = '''echo -e "\n#####  Set TestON Branch #####"
        echo "TestON Branch is set on: ''' + test_branch + '''"
        cd ~/OnosSystemTest/
        git checkout HEAD~1      # Make sure you aren't pn a branch
        git branch | grep -v "detached from" | xargs git branch -d # delete all local branches merged with remote
        git branch -D ''' + test_branch + ''' # just in case there are local changes. This will normally result in a branch not found error
        git clean -df # clean any local files
        git fetch --all # update all caches from remotes
        git reset --hard origin/''' + test_branch + '''  # force local index to match remote branch
        git clean -df # clean any local files
        git checkout ''' + test_branch + ''' #create new local branch
        git branch
        git log -1 --decorate
        echo -e "\n#####  Set ONOS Branch #####"
        echo "ONOS Branch is set on: ''' + onos_branch + '''"
        echo -e "\n #### check karaf version ######"
        env |grep karaf
        cd ~/onos
        git checkout HEAD~1      # Make sure you aren't pn a branch
        git branch | grep -v "detached from" | xargs git branch -d # delete all local branches merged with remote
        git branch -D ''' + onos_branch + ''' # just incase there are local changes. This will normally result in a branch not found error
        git clean -df # clean any local files
        git fetch --all # update all caches from remotes
        git reset --hard origin/''' + onos_branch + '''  # force local index to match remote branch
        git clean -df # clean any local files
        rm -rf buck-out
        rm -rf bazel-*
        ''' + tagCheck( onos_tag, onos_branch ) + '''
        git branch
        git log -1 --decorate
        echo -e "\n##### set jvm heap size to 8G #####"
        echo ${ONOSJAVAOPTS}
        inserted_line="export JAVA_OPTS=\"\${ONOSJAVAOPTS}\""
        sed -i "s/bash/bash\\n$inserted_line/" ~/onos/tools/package/bin/onos-service
        echo "##### Check onos-service setting..... #####"
        cat ~/onos/tools/package/bin/onos-service
        export JAVA_HOME=/usr/lib/jvm/java-8-oracle'''
    } else {
        result = '''echo "Since this is a manual run, we'll use the current ONOS and TestON branch:"
                    echo "ONOS branch:"
                    cd ~/OnosSystemTest/
                    git branch
                    echo "TestON branch:"
                    cd ~/TestON/
                    git branch'''
    }
    return result
}

def postSetup( onos_branch, test_branch, onos_tag, isManual ){
    // setup that will build ONOS

    result = ""
    if ( !isManual ){
        result = '''echo -e "Installing bazel"
        cd ~
        rm -rf ci-management
        git clone https://gerrit.onosproject.org/ci-management
        cd ci-management/jjb/onos/
        export GERRIT_BRANCH="''' + onos_branch + '''"
        chmod +x install-bazel.sh
        ./install-bazel.sh
        '''
    } else {
        result = '''echo -e "Since this is a manual run, we will not install Bazel."'''
    }
    return result
}

def generateKey(){
    // generate cluster-key of the onos

    try {
        sh script: '''
        #!/bin/bash -l
        set +e
        . ~/.bashrc
        env
        onos-push-bits-through-proxy
        onos-gen-cluster-key -f
        ''', label: "Generate Cluster Key", returnStdout: false
    } catch ( all ){
    }
}

// Initialize the environment Setup for the onos and OnosSystemTest
def envSetup( onos_branch, test_branch, onos_tag, jobOn, manuallyRun, nodeLabel ){
    // to setup the environment using the bash script
    stage( "Environment Setup: " + onos_branch + "-" + nodeLabel + "-" + jobOn ) {
        // after env: ''' + borrow_mn( jobOn ) + '''
        sh script: '''#!/bin/bash -l
        set +e
        . ~/.bashrc
        env
        ''' + preSetup( onos_branch, test_branch, onos_tag, manuallyRun ), label: "Repo Setup", returnStdout: false
        sh script: postSetup( onos_branch, test_branch, onos_tag, manuallyRun ), label: "Install Bazel", returnStdout: false
        generateKey()
    }
}

// export Environment properties.
def exportEnvProperty( onos_branch, test_branch, jobOn, wiki, tests, postResult, manually_run, onosTag, isOldFlow, nodeLabel ){
    // export environment properties to the machine.

    filePath = "/var/jenkins/TestONOS-" + jobOn + "-" + onos_branch + ".property"

    stage( "Property Export: " + onos_branch + "-" + nodeLabel + "-" + jobOn ) {
        sh script: '''
            echo "ONOSBranch=''' + onos_branch + '''" > ''' + filePath + '''
            echo "TestONBranch=''' + test_branch + '''" >> ''' + filePath + '''
            echo "ONOSTag=''' + onosTag + '''" >> ''' + filePath + '''
            echo "WikiPrefix=''' + wiki + '''" >> ''' + filePath + '''
            echo "ONOSJAVAOPTS=''' + env.ONOSJAVAOPTS + '''" >> ''' + filePath + '''
            echo "Tests=''' + tests + '''" >> ''' + filePath + '''
            echo "postResult=''' + postResult + '''" >> ''' + filePath + '''
            echo "manualRun=''' + manually_run + '''" >> ''' + filePath + '''
            echo "isOldFlow=''' + isOldFlow + '''" >> ''' + filePath + '''
        ''', label: "Exporting Property File: " + filePath
    }
}

def trigger( branch, tests, nodeLabel, jobOn, manuallyRun, onosTag ){
    // triggering function that will setup the environment and determine which pipeline to trigger

    println "Job name: " + jobOn + "-pipeline-" + ( manuallyRun ? "manually" : branch )
    def wiki = branch
    def onos_branch = test_list.addPrefixToBranch( branch )
    def test_branch = test_list.addPrefixToBranch( branch )
    assignedNode = null
    node( label: nodeLabel ) {
        envSetup( onos_branch, test_branch, onosTag, jobOn, manuallyRun, nodeLabel )
        exportEnvProperty( onos_branch, test_branch, jobOn, wiki, tests, post_result, manuallyRun, onosTag, isOldFlow, nodeLabel )
        assignedNode = env.NODE_NAME
    }

    jobToRun = jobOn + "-pipeline-" + ( manuallyRun ? "manually" : wiki )
    build job: jobToRun, propagate: false, parameters: [ [ $class: 'StringParameterValue', name: 'Category', value: jobOn ],
                                                         [ $class: 'StringParameterValue', name: 'Branch', value: branch ],
                                                         [ $class: 'StringParameterValue', name: 'TestStation', value: assignedNode ],
                                                         [ $class: 'StringParameterValue', name: 'NodeLabel', value: nodeLabel ],
                                                         [ $class: 'StringParameterValue', name: 'TimeOut', value: pipelineTimeOut.toString() ] ]
}

def trigger_pipeline( branch, tests, nodeLabel, jobOn, manuallyRun, onosTag ){
    // nodeLabel : nodeLabel from tests.json
    // jobOn : "SCPF" or "USECASE" or "FUNC" or "HA"
    // this will return the function by wrapping them up with return{} to prevent them to be
    // executed once this function is called to assign to specific variable.
    return {
        trigger( branch, tests, nodeLabel, jobOn, manuallyRun, onosTag )
    }
}

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
                    runList.put( branch + "-" + nodeLabel + "-" + category, trigger_pipeline( branch, exeTestList, nodeLabel, category, manually_run, onos_tag ) )
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
            graphs.generateStatGraph( "TestStation-VMs",
                                     test_list.addPrefixToBranch( b ),
                                     graphPaths[ "histogramMultiple" ],
                                     graphPaths[ "pieMultiple" ],
                                     graphPaths[ "saveDirectory" ],
                                     "VM" )
        }
    }
}
