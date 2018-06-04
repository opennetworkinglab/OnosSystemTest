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
// it has some general functionality of making database command, basic graph part, and get list of the test

// make the init part of the database command
def database_command_create( pass, host, port, user ){
    return pass + "|psql --host=" + host + " --port=" + port + " --username=" + user + " --password --dbname onostest -c "
}

// make the basic graph part for the Rscript
def basicGraphPart( rFileName, host, port, user, pass, subject, branchName ){
    return " Rscript " + rFileName + " " + host + " " + port + " " + user + " " + pass + " " + subject + " " + branchName
}

// get the list of the test as dictionary then return as a string
def getTestList( tests ){
    def list = ""
    for ( String test : tests.keySet() ){
        list += test + ","
    }
    return list[ 0..-2 ]
}

return this
