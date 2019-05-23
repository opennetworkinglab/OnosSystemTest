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

// returns the entire set of TestON tests from the json file
def getAllTests(){
    return allTests
}

// returns the entire set of schedules from the json file
def getSchedules(){
    return schedules
}

def getAllBranches(){
    return branches
}

// given a test category ("FUNC", "HA", etc.), returns all tests associated with that category
def getTestsFromCategory( category, tests=[:] ){
    result = [:]
    if ( tests == [:] ){
        tests = allTests
    }
    for ( String key in tests.keySet() ){
        if ( tests[ key ][ "category" ] == category ){
            result.put( key, tests[ key ] )
        }
    }
    return result
}

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
def getTestsFromDay( day, branch, tests=[:] ){
    result = [:]
    if ( tests == [:] ){
        tests = allTests
    }
    validSchedules = getValidSchedules( day )
    for ( String key in tests.keySet() ){
        schedule = tests[ key ][ "schedule" ][ branch ]
        if ( validSchedules.contains( schedule ) ){
            result.put( key, tests[ key ] )
        }
    }
    return result
}

// given a day, returns all branches that are run on that day
def getBranchesFromDay( day, tests=[:] ){
    result = []
    if ( tests == [:] ){
        tests = allTests
    }
    validSchedules = getValidSchedules( day )

    for ( String key in tests.keySet() ){
        for ( String branch in tests[ key ][ "schedule" ].keySet() ){
            sch = tests[ key ][ "schedule" ][ branch ]
            if ( validSchedules.contains( sch ) && !result.contains( sch ) ){
                result += convertBranchCodeToBranch( branch )
            }
        }
    }
    return result
}

// given a nodeLabel ("vm", "bm", etc.), returns all tests that run on that node.
def getTestsFromNodeLabel( nodeLabel, tests=[:] ){
    if ( tests == [:] ){
        tests = allTests
    }
    for ( String key in tests.keySet() ){
        if ( tests[ key ][ "nodeLabel" ] == nodeLabel ){
            result.put( key, tests[ key ] )
        }
    }
}

// returns the test list as a string
def getTestListAsString( tests ){
    result = ""
    for ( String test in tests.keySet() ){
        result += test + ","
    }
    return result[ 0..-2 ]
}

// returns the schedule for a given test
def getTestSchedule( test ){
    return allTests[ test ][ "schedule" ]
}

// returns a list of days from the given schedule
def convertScheduleKeyToDays( sch ){
    return schedules[ sch ]
}

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

return this
