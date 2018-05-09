#!groovy

def init( commonFuncs ){
    funcs = commonFuncs
}
def lastCommaRemover( str ){
    if ( str.size() > 0 && str[ str.size() - 1 ] == ',' ){
        str = str.substring( 0,str.size() - 1 )
    }
    return str
}
def printDaysForTest( AllTheTests ){
    result = ""
    for ( String test in AllTheTests.keySet() ){
        result += test + " : \n"
        for( String each in AllTheTests[ test ].keySet() ){
            AllTheTests[ test ][ each ][ "day" ] = lastCommaRemover( AllTheTests[ test ][ each ][ "day" ] )
            result += "    " + each + ":[" + AllTheTests[ test ][ each ][ "day" ] + "]\n"
        }
        result += "\n"
    }
    return result
}
def runTestSeq( testList ){
    return{
        for ( test in testList.keySet() ){
            testList[ test ].call()
        }
    }
}
def print_tests( tests ){
    for( String test in tests.keySet() ){
        if( tests[ test ][ "tests" ] != "" ){
            println test + ":"
            println tests[ test ][ "tests" ]
        }
    }
}
def organize_tests( tests, testcases ){
    testList = tests.tokenize( "\n;, " )
    for( String test in testList )
        testcases [ Prefix_organizer[ ( test == "FUNCbgpls" || test == "FUNCvirNetNB" ? "US" : ( test[ 0 ] + test[ 1 ] ) ) ] ][ "tests" ] += test + ","
    return testcases
}
def borrow_mn( jobOn ){
    result = ""
    if( jobOn == "SR" ){
        result = "~/cell_borrow.sh"
    }
    return result
}
def trigger( branch, tests, nodeName, jobOn, manuallyRun, onosTag ){
    println jobOn + "-pipeline-" + manuallyRun ? "manually" : branch
    def wiki = branch
    branch = funcs.branchWithPrefix( branch )
    test_branch = "master"
    node( "TestStation-" + nodeName + "s" ){
        envSetup( branch, test_branch, onosTag, jobOn, manuallyRun )

        exportEnvProperty( branch, test_branch, wiki, tests, post_result, manuallyRun, onosTag, isOldFlow )
    }

    jobToRun = jobOn + "-pipeline-" + ( manuallyRun ? "manually" : wiki )
    build job: jobToRun, propagate: false
}
def trigger_pipeline( branch, tests, nodeName, jobOn, manuallyRun, onosTag ){
// nodeName : "BM" or "VM"
// jobOn : "SCPF" or "USECASE" or "FUNC" or "HA"
    return{
        trigger( branch, tests, nodeName, jobOn, manuallyRun, onosTag )
    }
}
// export Environment properties.
def exportEnvProperty( onos_branch, test_branch, wiki, tests, postResult, manually_run, onosTag, isOldFlow ){
    stage( "export Property" ){
        sh '''
            echo "ONOSBranch=''' + onos_branch +'''" > /var/jenkins/TestONOS.property
            echo "TestONBranch=''' + test_branch +'''" >> /var/jenkins/TestONOS.property
            echo "ONOSTag='''+ onosTag +'''" >> /var/jenkins/TestONOS.property
            echo "WikiPrefix=''' + wiki +'''" >> /var/jenkins/TestONOS.property
            echo "ONOSJVMHeap='''+ env.ONOSJVMHeap +'''" >> /var/jenkins/TestONOS.property
            echo "Tests=''' + tests +'''" >> /var/jenkins/TestONOS.property
            echo "postResult=''' + postResult +'''" >> /var/jenkins/TestONOS.property
            echo "manualRun=''' + manually_run +'''" >> /var/jenkins/TestONOS.property
            echo "isOldFlow=''' + isOldFlow +'''" >> /var/jenkins/TestONOS.property
        '''
    }
}
// Initialize the environment Setup for the onos and OnosSystemTest
def envSetup( onos_branch, test_branch, onos_tag, jobOn, manuallyRun ){
    stage( "envSetup" ) {
        // after env: ''' + borrow_mn( jobOn ) + '''
        sh '''#!/bin/bash -l
        set +e
        . ~/.bashrc
        env
        ''' + preSetup( onos_branch, test_branch, onos_tag, manuallyRun ) + '''
        ''' + oldFlowCheck( jobOn, onos_branch ) + '''
        ''' + postSetup( onos_branch, test_branch, onos_tag, manuallyRun )
        generateKey()
    }
}
def tagCheck( onos_tag, onos_branch ){
    result = "git checkout "
    if ( onos_tag == "" )
        result += onos_branch //create new local branch
    else
        result += onos_tag //checkout the tag
    return result
}
def preSetup( onos_branch, test_branch, onos_tag, isManual ){
    result = ""
    if( !isManual ){
        result = '''echo -e "\n#####  Set TestON Branch #####"
        echo "TestON Branch is set on: ''' + test_branch + '''"
        cd ~/OnosSystemTest/
        git checkout HEAD~1      # Make sure you aren't pn a branch
        git branch | grep -v "detached from" | xargs git branch -d # delete all local branches merged with remote
        git branch -D ''' + test_branch + ''' # just incase there are local changes. This will normally result in a branch not found error
        git clean -df # clean any local files
        git fetch --all # update all caches from remotes
        git reset --hard origin/''' + test_branch +'''  # force local index to match remote branch
        git clean -df # clean any local files
        git checkout ''' + test_branch + ''' #create new local branch
        git branch
        git log -1 --decorate
        echo -e "\n#####  Set ONOS Branch #####"
        echo "ONOS Branch is set on: ''' + onos_branch + '''"
        echo -e "\n #### check karaf version ######"
        env |grep karaf
        cd ~/onos
        rm -rf buck-out/*
        ~/onos/tools/build/onos-buck clean
        git checkout HEAD~1      # Make sure you aren't pn a branch
        git branch | grep -v "detached from" | xargs git branch -d # delete all local branches merged with remote
        git branch -D ''' + onos_branch + ''' # just incase there are local changes. This will normally result in a branch not found error
        git clean -df # clean any local files
        git fetch --all # update all caches from remotes
        git reset --hard origin/''' + onos_branch + '''  # force local index to match remote branch
        git clean -df # clean any local files
        ''' + tagCheck( onos_tag, onos_branch ) + '''
        git branch
        git log -1 --decorate
        echo -e "\n##### set jvm heap size to 8G #####"
        echo ${ONOSJVMHeap}
        inserted_line="export JAVA_OPTS=\"\${ONOSJVMHeap}\""
        sed -i "s/bash/bash\\n$inserted_line/" ~/onos/tools/package/bin/onos-service
        echo "##### Check onos-service setting..... #####"
        cat ~/onos/tools/package/bin/onos-service
        export JAVA_HOME=/usr/lib/jvm/java-8-oracle'''
    }
    return result
}
def oldFlowCheck( jobOn, onos_branch ){
    result = ""
    if( jobOn == "SCPF" && ( onos_branch== "master" || onos_branch=="onos-1.12" ) )
        result = '''sed -i -e 's/@Component(immediate = true)/@Component(enabled = false)/g' ~/onos/core/store/dist/src/main/java/org/onosproject/store/flow/impl/''' + ( isOldFlow ? "DistributedFlowRuleStore" : "ECFlowRuleStore" ) + '''.java
        sed -i -e 's/@Component(enabled = false)/@Component(immediate = true)/g' ~/onos/core/store/dist/src/main/java/org/onosproject/store/flow/impl/''' + ( isOldFlow ? "ECFlowRuleStore" : "DistributedFlowRuleStore" ) + ".java"
    return result
}
def postSetup( onos_branch, test_branch, onos_tag, isManual ){
    result = ""
    if( !isManual ){
        result = '''echo -e "\n##### build ONOS skip unit tests ######"
        #mvn clean install -DskipTests
        # Force buck update
        rm -f ~/onos/bin/buck
        ~/onos/tools/build/onos-buck build onos
        sleep 30
        echo -e "\n##### Stop all running instances of Karaf #####"
        kill $(ps -efw | grep karaf | grep -v grep | awk '{print $2}')
        sleep 30
        git branch
        '''
    }
    return result
}
def generateKey(){
    try{
        sh '''
        #!/bin/bash -l
        set +e
        . ~/.bashrc
        env
        onos-push-bits-through-proxy
        onos-gen-cluster-key -f
        '''
    }catch( all ){}
}
def returnCell( nodeName ){
    node( "TestStation-" + nodeName + "s" ){
        sh '''#!/bin/bash -l
            set +e
            . ~/.bashrc
            env
            ~/./return_cell.sh
            '''
    }
}

return this;
