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

// read the dependency files
funcs = evaluate readTrusted( 'TestON/JenkinsFile/dependencies/JenkinsCommonFuncs.groovy' )
test_list = evaluate readTrusted( 'TestON/JenkinsFile/dependencies/JenkinsTestONTests.groovy' )
fileRelated = evaluate readTrusted( 'TestON/JenkinsFile/dependencies/JenkinsPathAndFiles.groovy' )
SCPFfuncs = evaluate readTrusted( 'TestON/JenkinsFile/dependencies/PerformanceFuncs.groovy' )

category = null
prop = null
testsToRun = null
testsToRunStrList = null
branch = null
start = null
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
        // SCPF needs to obtain properties earlier
        funcs.initialize( category, SCPFfuncs );
        prop = funcs.getProperties( category, test_list.addPrefixToBranch( branch ) )

        SCPFfuncs.init()
        isOldFlow = prop[ "isOldFlow" ] == "true"
        SCPFfuncs.oldFlowRuleCheck( isOldFlow, prop[ "ONOSBranch" ] )
    } else if ( category == "SR" ){
        funcs.initialize( category );
        // get the name of the Jenkins job.
        jobName = env.JOB_NAME
        // additional setup for Segment routing because it is running multiple branch concurrently on different machines.
        funcs.additionalInitForSR( jobName )
        prop = funcs.getProperties( category, test_list.addPrefixToBranch( branch ) )
    } else {
        funcs.initialize( category );
        prop = funcs.getProperties( category, test_list.addPrefixToBranch( branch ) )
    }

    // get the list of the test and init branch to it.
    testsFromList = test_list.getTestsFromCategory( category )

    initGraphPaths()

    testsToRunStrList = funcs.getTestsToRun( prop[ "Tests" ] )
    testsToRun = test_list.getTestsFromStringList( testsToRunStrList )
}

def readParams(){
    category = params.Category // "FUNC", "HA", "USECASE", etc.
    branch = params.Branch
}

def initGraphPaths(){
    graphPaths.put( "trendIndividual", fileRelated.trendIndividual )
    if ( category == "SR" ){
        graphPaths.put( "saveDirectory", fileRelated.jenkinsWorkspace + "postjob-Fabric" + funcs.fabricOn( prop[ "ONOSBranch" ] ) + "/" )
    } else if ( category == "SRHA" ) {
        graphPaths.put( "saveDirectory", fileRelated.jenkinsWorkspace + "postjob-Fabric" + "/" )
    } else if ( category == "SCPF" || category == "USECASE" ){
        graphPaths.put( "saveDirectory", fileRelated.jenkinsWorkspace + "postjob-BM/" )
    } else {
        graphPaths.put( "saveDirectory", fileRelated.jenkinsWorkspace + "postjob-VM/" )
    }
}

def runTests(){
    // run the test sequentially and save the function into the dictionary.
    for ( String test : testsToRun.keySet() ){
        def toBeRun = test
        def stepName = ( toBeRun ? "" : "Not " ) + "Running $test"
        def pureTestName = ( testsToRun[ test ].containsKey( "test" ) ? testsToRun[ test ][ "test" ].split().head() : test )
        pipeline[ stepName ] = funcs.runTest( test, toBeRun, prop, pureTestName, false,
                                           testsToRun, graphPaths[ "trendIndividual" ], graphPaths[ "saveDirectory" ] )
    }

    // get the start time of the test.
    start = funcs.getCurrentTime()

    // run the tests sequentially.
    for ( test in pipeline.keySet() ){
        pipeline[ test ].call()
    }
}

def generateGraphs(){
    if ( category == "SCPF" ){
        jobToRun = "manual-graph-generator-SCPF"
        ONOSbranchParam = [ $class: 'StringParameterValue', name: 'ONOSbranch', value: test_list.addPrefixToBranch( branch ) ]
        isOldFlowParam = [ $class: 'BooleanParameterValue', name: 'isOldFlow', value: true ]
        // leaving Test param empty to use default values
        build job: jobToRun, propagate: false, parameters: [ ONOSbranchParam, isOldFlowParam ]

        isOldFlowParam = [ $class: 'BooleanParameterValue', name: 'isOldFlow', value: false ]
        build job: jobToRun, propagate: false, parameters: [ ONOSbranchParam, isOldFlowParam ]
    } else {
        // generate the overall graph of the FUNC tests.
        funcs.generateOverallGraph( prop, testsToRunStrList, graphPaths[ "saveDirectory" ] )
    }
}

def sendToSlack(){
    // send the notification to Slack that running FUNC tests was ended.
    funcs.sendResultToSlack( start, prop[ "manualRun" ], prop[ "WikiPrefix" ] )
}
