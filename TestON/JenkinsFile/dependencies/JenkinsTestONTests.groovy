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

allTests = [:]
schedules = [:]
branches = [:]

def init(){
    def tests_buffer = readTrusted( "TestON/JenkinsFile/dependencies/tests.json" )
    def schedules_buffer = readTrusted( "TestON/JenkinsFile/dependencies/schedule.json" )
    def branches_buffer = readTrusted( "TestON/JenkinsFile/dependencies/branches.json" )
    allTests = readJSON text: tests_buffer
    schedules = readJSON text: schedules_buffer
    branches = readJSON text: branches_buffer
}

// ***************
// General Methods
// ***************

// returns the entire set of TestON tests from the json file
def getAllTests(){
    return allTests
}

// returns the entire set of schedules from the json file
def getSchedules(){
    return schedules
}

// returns a list of days corresponding to the given schedule code
def convertScheduleKeyToDays( sch ){
    return schedules[ sch ]
}

// given a test dictionary, returns a list of tests as a string
def getTestListAsString( tests ){
    str_result = ""
    for ( String test in tests.keySet() ){
        str_result += test + ","
    }
    return str_result[ 0..-2 ]
}

def getTestsFromStringList( list ){
    testsResult = [:]
    for ( item in list ){
        if ( allTests.keySet().contains( item ) ){
            testsResult.put( item, allTests[ item ] )
        }
    }
    return testsResult
}

// Get a given test property from the schedules list for a given test
// Example: getTestScheduleProperty( "FUNCflow", "nodeLabel" ) gets all node labels for each branch
def getTestScheduleProperty( test_name, property, tests=[:] ){
    schedulePropertyResult = [:]

    if ( tests == [:] ){
        tests = allTests
    }
    for ( subDict in tests[ test_name ][ "schedules" ] ){
        schedulePropertyResult.put( subDict[ "branch" ], subDict[ property ] )
    }

    return schedulePropertyResult
}

def getAllBranches(){
    return branches
}

// ********
// Branches
// ********

// given a day, returns all branches that are run on that day
def getBranchesFromDay( day, tests=[:] ){
    branchesFromDayResult = []
    if ( tests == [:] ){
        tests = allTests
    }
    validSchedules = getValidSchedules( day )

    for ( String key in tests.keySet() ){
        for ( subDict in tests[ key ][ "schedules" ] ){
            sch = subDict[ "day" ]
            if ( validSchedules.contains( sch ) && !branchesFromDayResult.contains( sch ) ){
                branchesFromDayResult += convertBranchCodeToBranch( subDict[ "branch" ] )
            }
        }
    }
    return branchesFromDayResult
}

// Converts a branch code to an actual ONOS branch.
// Example: converts onos-1.x to onos-1.15
def convertBranchCodeToBranch( branch_code, withPrefix=true ){
    for ( String branch_type in branches.keySet() ){
        for ( String b in branches[ branch_type ].keySet() ){
            if ( branch_code == b ){
                return withPrefix ? ( "onos-" + branches[ branch_type ][ b ] ) : branches[ branch_type ][ b ]
            }
        }
    }
    return branch_code
}

def convertBranchToBranchCode( branch ){
    if ( branch == "master" || branch.substring( 0, 1 ) == "o" ){
        return branch
    } else {
        return "onos-" + branch.substring( 0, 1 ) + ".x"
    }
}

// *************
// Test Category
// *************

// given a test category ("FUNC", "HA", etc.), returns all tests associated with that category
def getTestsFromCategory( category, tests=[:] ){
    testsFromCategoryResult = [:]
    if ( tests == [:] ){
        tests = allTests
    }
    for ( String test_name in tests.keySet() ){
        if ( getCategoryOfTest( test_name ) == category ){
            testsFromCategoryResult.put( test_name, tests[ test_name ] )
        }
    }
    return testsFromCategoryResult
}

def getCategoryOfTest( test_name, tests=[:] ){
    if ( tests == [:] ){
        tests = allTests
    }
    return tests[ test_name ][ "category" ]
}

def getAllTestCategories( tests=[:] ){
    testCategoriesResult = []
    if ( tests == [:] ){
        tests = allTests
    }
    for ( String test_name in tests.keySet() ){
        category = getCategoryOfTest( test_name, tests )
        if ( !testCategoriesResult.contains( category ) ){
            testCategoriesResult += category
        }
    }
    return testCategoriesResult
}

// ********************
// Test Schedule / Days
// ********************

// given a day, returns schedules that contain that day
def getValidSchedules( day ){
    validSchedules = []
    for ( String key in schedules.keySet() ){
        if ( schedules[ key ].contains( day ) ){
            validSchedules += key
        }
    }
    return validSchedules
}

// given a day and branch, returns all tests that run on the given day on the given branch
def getTestsFromDay( day, tests=[:] ){
    resultDict = [:]
    if ( tests == [:] ){
        tests = allTests
    }
    validSchedules = getValidSchedules( day )
    for ( String key in tests.keySet() ){
        scheduleProperty = getTestScheduleProperty( key, "day", tests )
        for ( b in scheduleProperty.keySet() ){
            if ( validSchedules.contains( scheduleProperty[ b ] ) ){
                resultDict.put( key, tests[ key ] )
                break
            }
        }
    }
    return resultDict
}

// **********
// Node Label
// **********

// Given a node label and branch, return all tests that run on that node.
def getTestsFromNodeLabel( nodeLabel, branch, tests=[:] ){
    nodeLabelTestsResult = [:]
    if ( tests == [:] ){
        tests = allTests
    }
    for ( String key in tests.keySet() ){
        branchNodeLabelMap = getTestScheduleProperty( key, "nodeLabel", tests )
        if ( branchNodeLabelMap[ convertBranchToBranchCode( branch ) ] == nodeLabel ){
            nodeLabelTestsResult.put( key, tests[ key ] )
        }
    }
    return nodeLabelTestsResult
}

// Given a test name and branch, return the node label associated.
def getNodeLabel( test_name, branch, tests ){
    if ( tests == [:] ){
        tests = allTests
    }
    result = getTestScheduleProperty( test_name, "nodeLabel", tests )
    if ( result == [:] ){
        return "UNKNOWN"
    } else {
        return result[ convertBranchToBranchCode( branch ) ]
    }
}

def getAllNodeLabels( branch, tests ){
    nodeLabelResult = []
    if ( tests == [:] ){
        tests = allTests
    }
    for ( test_name in tests.keySet() ){
        nodeLabel = getNodeLabel( test_name, branch, tests )
        if ( !nodeLabelResult.contains( nodeLabel ) && nodeLabel != null ){
            nodeLabelResult += nodeLabel
        }
    }
    return nodeLabelResult
}

return this
