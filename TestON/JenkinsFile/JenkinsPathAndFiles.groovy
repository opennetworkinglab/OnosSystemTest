#!groovy

def initLocation(){
    jenkinsFolder = "~/OnosSystemTest/TestON/JenkinsFile/"
    rScriptLocation = jenkinsFolder + "wikiGraphRScripts/"
    jenkinsWorkspace = "/var/jenkins/workspace/"
    SCPFSpecificLocation = rScriptLocation + "SCPFspecificGraphRScripts/"
    CHOScriptDir = "~/CHO_Jenkins_Scripts/"
}
def initFiles(){
    trendIndividual = rScriptLocation + "trendIndividualTest.R"
    trendMultiple = rScriptLocation + "trendMultipleTests.R"
    trendSCPF = rScriptLocation + "trendSCPF.R"
    trendCHO = rScriptLocation + "trendCHO.R"
    histogramMultiple = rScriptLocation + "histogramMultipleTestGroups.R"
    pieMultiple = rScriptLocation + "pieMultipleTests.R"
}
def init(){
    initLocation()
    initFiles()
}
return this;

