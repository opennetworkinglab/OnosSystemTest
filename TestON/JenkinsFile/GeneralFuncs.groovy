#!groovy

def database_command_create( pass, host, port, user ){
  return pass + "|psql --host=" + host + " --port=" + port + " --username=" + user + " --password --dbname onostest -c "
}
def basicGraphPart( rFileName, host, port, user, pass, subject, branchName ){
  return " Rscript " + rFileName + " " + host + " " + port + " " + user + " " + pass + " " + subject + " " + branchName
}
def initBasicVars(){
  rScriptLocation = "~/OnosSystemTest/TestON/JenkinsFile/scripts/"
}
def getTestList( tests ){
    list = ""
    for( String test : tests.keySet() )
        list += test + ","
    return list[ 0..-2 ]
}
return this;