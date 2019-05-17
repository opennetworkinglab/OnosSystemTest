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
// This will initialize the paths of the jenkins file and paths.

import groovy.json.*

jenkinsFiles = ""
rScriptPaths = [:]      // paths of r script files that generate wiki graphs
workspaces = [:]        // postjob workspaces

// init both directory and file paths.
def init(){
    def paths_buffer = readTrusted( "TestON/JenkinsFile/dependencies/paths.json" )
    paths_json = readJSON text: paths_buffer

    jenkinsFiles = paths_json[ "jenkinsFiles" ]
    workspaces = paths_json[ "workspaces" ]
    rScriptPaths = paths_json[ "rScript" ]
}

return this
