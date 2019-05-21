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

def init(){
    def tests_buffer = readTrusted( "TestON/JenkinsFile/dependencies/tests.json" )
    def schedules_buffer = readTrusted( "TestON/JenkinsFile/dependencies/schedule.json" )
    allTests = readJSON text: tests_buffer
    schedules = readJSON text: schedules_buffer
}

def getAllTests(){
    return allTests
}

def getSchedules(){
    return schedules
}

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

def getTestsFromDay( day, branch, tests=[:] ){
    result = [:]
    if ( tests == [:] ){
        tests = allTests
    }
    validSchedules = []
    for ( String key in schedules.keySet() ){
        if ( schedules[ key ].contains( day ) ){
            validSchedules += key
        }
    }
    echo validSchedules.toString()
    for ( String key in tests.keySet() ){
        schedule = tests[ key ][ "schedule" ][ branch ]
        if ( validSchedules.contains( schedule ) ){
            result.put( key, tests[ key ] )
        }
    }
    return result
}

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

def getTestListAsString( tests ){
    result = ""
    for ( String key in tests.keySet() ){
        result += test + ","
    }
    return result[ 0..-2 ]
}

def getTestSchedule( test ){
    return allTests[ test ][ "schedule" ]
}

def convertScheduleKeyToDays( sch ){
    return schedules[ sch ]
}

return this
