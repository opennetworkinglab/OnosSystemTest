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

test_list = evaluate readTrusted( 'TestON/JenkinsFile/dependencies/JenkinsTestONTests.groovy' )
fileRelated = evaluate readTrusted( 'TestON/JenkinsFile/dependencies/JenkinsPathAndFiles.groovy' )

category = null
prop = null
testsToRun = null
testsToRunStrList = null
branch = null
branchWithPrefix = null
nodeLabel = null
testStation = null
testsOverride = null
pipelineTimeout = null

testsFromList = [:]
pipeline = [:]

def main(){
    pipelineTimeout = params.TimeOut.toInteger() // integer minutes until the entire pipeline times out. Usually passed from upstream master-trigger job.
    timeout( time: pipelineTimeout, unit: "MINUTES" ){
        init()
        runTests()
    }
}

main()

def init(){
    fileRelated.init()
    test_list.init()
    readParams()

    if ( branch == "manually" ){
        echo '''Warning: entered branch was: "manually". Defaulting to master branch.'''
        branch = "master"
        branchWithPrefix = test_list.addPrefixToBranch( branch )
    }
    prop = getProperties()

    // get the list of the tests from category
    testsFromList = test_list.getTestsFromCategory( category )

    tokenizeTokens = "\n;, "

    if ( testsOverride == "" || testsOverride == null ){
        testsToRunStrList = prop[ "Tests" ].tokenize( tokenizeTokens )
    } else {
        testsToRunStrList = testsOverride.tokenize( tokenizeTokens )
    }
    testsToRun = test_list.getTestsFromStringList( testsToRunStrList )
}

def getProperties(){
    // get the properties of the test by reading the TestONOS.property

    filePath = '''/var/jenkins/TestONOS-''' + category + '''-''' + branchWithPrefix + '''.property'''

    node( testStation ) {
        return readProperties( file: filePath )
    }
}

def readParams(){
    category = params.Category       // "MO", etc.
    branch = params.Branch           // "1.15", "2.1", "master", etc.
    branchWithPrefix = test_list.addPrefixToBranch( branch )
    testStation = params.TestStation // "TestStation-BMs", etc.
    nodeLabel = params.NodeLabel     // "BM", "VM", "Fabric-1.x", etc.
    testsOverride = params.TestsOverride // "FUNCflow, FUNCintent, [...]", overrides property file
}

def runTests(){
    // run the test sequentially and save the function into the dictionary.
    for ( String test : testsFromList.keySet() ){
        toBeRun = testsToRun.keySet().contains( test )
        stepName = ( toBeRun ? "" : "Not " ) + "Running $test"
        pipeline[ stepName ] = runMOtest( test,
                                          toBeRun )
    }

    // run the tests sequentially.
    for ( test in pipeline.keySet() ){
        pipeline[ test ].call()
    }
}

def runMOtest( test, toBeRun ){
    return {
        catchError {
            stage( test ){
                if ( toBeRun ){
                    node( testStation ) {
                        sh script: '''. ~/.profile
                                      cd ~/onos-test
                                      make clean
                                      make integration
                                   ''', label: "make integration"
                    }
                }
            }
        }
    }
}
