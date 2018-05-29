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

// init the paths for the directory
def initLocation(){
    jenkinsFolder = "~/OnosSystemTest/TestON/JenkinsFile/"
    rScriptLocation = jenkinsFolder + "wikiGraphRScripts/"
    jenkinsWorkspace = "/var/jenkins/workspace/"
    SCPFSpecificLocation = rScriptLocation + "SCPFspecificGraphRScripts/"
    CHOScriptDir = "~/CHO_Jenkins_Scripts/"
}

// init the paths for the files.
def initFiles(){
    trendIndividual = rScriptLocation + "trendIndividualTest.R"
    trendMultiple = rScriptLocation + "trendMultipleTests.R"
    trendSCPF = rScriptLocation + "trendSCPF.R"
    trendCHO = rScriptLocation + "trendCHO.R"
    histogramMultiple = rScriptLocation + "histogramMultipleTestGroups.R"
    pieMultiple = rScriptLocation + "pieMultipleTests.R"
}

// init both directory and file paths.
def init(){
    initLocation()
    initFiles()
}

return this

