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
// This will provide the portion that will set up the environment of the machine
//      and trigger the corresponding jobs.


def init( commonFuncs ){
    funcs = commonFuncs
}

def lastCommaRemover( str ){
    // function that will remove the last comma from the string

    if ( str.size() > 0 && str[ str.size() - 1 ] == ',' ){
        str = str.substring( 0, str.size() - 1 )
    }
    return str
}

def printDaysForTest( AllTheTests ){
    // Print the days for what test has.

    result = ""
    for ( String test in AllTheTests.keySet() ){
        result += test + " : \n"
        for ( String each in AllTheTests[ test ].keySet() ){
            AllTheTests[ test ][ each ][ "day" ] = lastCommaRemover( AllTheTests[ test ][ each ][ "day" ] )
            result += "    " + each + ":[" + AllTheTests[ test ][ each ][ "day" ] + "]\n"
        }
        result += "\n"
    }
    return result
}

def runTestSeq( testList ){
    // Running the test sequentially
    return {
        for ( test in testList.keySet() ){
            testList[ test ].call()
        }
    }
}

def print_tests( tests ){
    // print the list of the tsets to be run

    for ( String test in tests.keySet() ){
        if ( tests[ test ][ "tests" ] != "" ){
            println test + ":"
            println tests[ test ][ "tests" ]
        }
    }
}

def organize_tests( tests, testcases ){
    // organize the test to its category using its name.
    // most of the time it will use the first two character of the test name
    // but there are some exceptions like FUNCbgpls or FUNCvirNetNB since they are now under USECASE

    // depends on the first two letters of the test name, it will decide which category to put the test into.
    def prefixes = [
            "FU": "FUNC",
            "HA": "HA",
            "PL": "USECASE",
            "SA": "USECASE",
            "SC": "SCPF",
            "SR": "SR",
            "US": "USECASE",
            "VP": "USECASE"
    ]

    def testList = tests.tokenize( "\n;, " )
    for ( String test in testList ){
        String prefix = ( test == "FUNCbgpls" || test == "FUNCvirNetNB" ) ? "US" : ( test[ 0..1 ] )
        testcases[ prefixes[ prefix ] ][ "tests" ] += test + ","
    }
    return testcases
}

def trigger( branch, tests, nodeName, jobOn, manuallyRun, onosTag ){
    // triggering function that will setup the environment and determine which pipeline to trigger

    println "Job name: " + jobOn + "-pipeline-" + ( manuallyRun ? "manually" : branch )
    def wiki = branch
    def onos_branch = funcs.branchWithPrefix( branch )
    def test_branch = funcs.testBranchWithPrefix( branch )
    println "onos_branch with prefix: " + onos_branch
    println "test_branch with prefix: " + test_branch
    node( "TestStation-" + nodeName + "s" ) {
        envSetup( onos_branch, test_branch, onosTag, jobOn, manuallyRun )
        exportEnvProperty( onos_branch, test_branch, wiki, tests, post_result, manuallyRun, onosTag, isOldFlow )
    }

    jobToRun = jobOn + "-pipeline-" + ( manuallyRun ? "manually" : wiki )
    build job: jobToRun, propagate: false
}

def trigger_pipeline( branch, tests, nodeName, jobOn, manuallyRun, onosTag ){
    // nodeName : "BM" or "VM"
    // jobOn : "SCPF" or "USECASE" or "FUNC" or "HA"
    // this will return the function by wrapping them up with return{} to prevent them to be
    // executed once this function is called to assign to specific variable.
    return {
        trigger( branch, tests, nodeName, jobOn, manuallyRun, onosTag )
    }
}

// export Environment properties.
def exportEnvProperty( onos_branch, test_branch, wiki, tests, postResult, manually_run, onosTag, isOldFlow ){
    // export environment properties to the machine.

    stage( "export Property" ) {
        sh '''
            echo "ONOSBranch=''' + onos_branch + '''" > /var/jenkins/TestONOS.property
            echo "TestONBranch=''' + test_branch + '''" >> /var/jenkins/TestONOS.property
            echo "ONOSTag=''' + onosTag + '''" >> /var/jenkins/TestONOS.property
            echo "WikiPrefix=''' + wiki + '''" >> /var/jenkins/TestONOS.property
            echo "ONOSJVMHeap=''' + env.ONOSJVMHeap + '''" >> /var/jenkins/TestONOS.property
            echo "Tests=''' + tests + '''" >> /var/jenkins/TestONOS.property
            echo "postResult=''' + postResult + '''" >> /var/jenkins/TestONOS.property
            echo "manualRun=''' + manually_run + '''" >> /var/jenkins/TestONOS.property
            echo "isOldFlow=''' + isOldFlow + '''" >> /var/jenkins/TestONOS.property
        '''
    }
}

// Initialize the environment Setup for the onos and OnosSystemTest
def envSetup( onos_branch, test_branch, onos_tag, jobOn, manuallyRun ){
    // to setup the environment using the bash script
    println "onos_branch is set to " + onos_branch
    println "test_branch is set to " + test_branch
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
    // check the tag for onos if it is not empty

    result = "git checkout "
    if ( onos_tag == "" ){
        //create new local branch
        result += onos_branch
    }
    else {
        //checkout the tag
        result += onos_tag
    }
    return result
}

def preSetup( onos_branch, test_branch, onos_tag, isManual ){
    // pre setup part which will clean up and checkout to corresponding branch.

    result = ""
    if ( !isManual ){
        result = '''echo -e "\n#####  Set TestON Branch #####"
        echo "TestON Branch is set on: ''' + test_branch + '''"
        cd ~/OnosSystemTest/
        git checkout HEAD~1      # Make sure you aren't pn a branch
        git branch | grep -v "detached from" | xargs git branch -d # delete all local branches merged with remote
        git branch -D ''' + test_branch + ''' # just in case there are local changes. This will normally result in a branch not found error
        git clean -df # clean any local files
        git fetch --all # update all caches from remotes
        git reset --hard origin/''' + test_branch + '''  # force local index to match remote branch
        git clean -df # clean any local files
        git checkout ''' + test_branch + ''' #create new local branch
        git branch
        git log -1 --decorate
        echo -e "\n#####  Set ONOS Branch #####"
        echo "ONOS Branch is set on: ''' + onos_branch + '''"
        echo -e "\n #### check karaf version ######"
        env |grep karaf
        cd ~/onos
        git checkout HEAD~1      # Make sure you aren't pn a branch
        git branch | grep -v "detached from" | xargs git branch -d # delete all local branches merged with remote
        git branch -D ''' + onos_branch + ''' # just incase there are local changes. This will normally result in a branch not found error
        git clean -df # clean any local files
        git fetch --all # update all caches from remotes
        git reset --hard origin/''' + onos_branch + '''  # force local index to match remote branch
        git clean -df # clean any local files
        rm -rf buck-out
        rm -rf bazel-*
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
    // part that will check if it is oldFlow. If so, it will switch to use old flow. Only affected with SCPF.

    result = ""
    if ( jobOn == "SCPF" && ( onos_branch == "master" || onos_branch == "onos-1.12" ) )
        result = '''sed -i -e 's/@Component(immediate = true)/@Component(enabled = false)/g' ~/onos/core/store/dist/src/main/java/org/onosproject/store/flow/impl/''' + ( isOldFlow ? "DistributedFlowRuleStore" : "ECFlowRuleStore" ) + '''.java
        sed -i -e 's/@Component(enabled = false)/@Component(immediate = true)/g' ~/onos/core/store/dist/src/main/java/org/onosproject/store/flow/impl/''' + ( isOldFlow ? "ECFlowRuleStore" : "DistributedFlowRuleStore" ) + ".java"
    return result
}

def postSetup( onos_branch, test_branch, onos_tag, isManual ){
    // setup that will build ONOS

    result = ""
    if ( !isManual ){
        result = '''echo -e "\n##### build ONOS skip unit tests ######"
        cd ~/onos
        . tools/dev/bash_profile
        op
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
    // generate cluster-key of the onos

    try {
        sh '''
        #!/bin/bash -l
        set +e
        . ~/.bashrc
        env
        onos-push-bits-through-proxy
        onos-gen-cluster-key -f
        '''
    } catch ( all ){
    }
}

return this
