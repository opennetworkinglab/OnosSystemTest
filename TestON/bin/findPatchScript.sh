#!/bin/bash

# Copyright 2015 Open Networking Foundation (ONF)
#
# Please refer questions to either the onos test mailing list at <onos-test@onosproject.org>,
# the System Testing Plans and Results wiki page at <https://wiki.onosproject.org/x/voMg>,
# or the System Testing Guide page at <https://wiki.onosproject.org/x/WYQg>
#
#     TestON is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 2 of the License, or
#     (at your option) any later version.
#
#     TestON is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with TestON.  If not, see <http://www.gnu.org/licenses/>.
#
#    Usage : ./findPatchScript.sh -t <testName> (optional choices : -n <# : number of run on each commit>
#                                                                   -s <# : number of commits to skip every iteration>

#source $ONOS_ROOT/tools/dev/bash_profile

#!/bin/bash
usage() { echo "Usage:$0 [-t <test_name>] Optional:{ -n <number_of_running_test_on_each_commit>
                                                       -s <number_of_skipping_commit> }"; 1>&2; exit 1;  }

NUM_RUN=1
SKIP_COMMIT=1
LOG_FILE="/home/sdn/OnosSystemTest/TestON/logs/findCommitLog.txt"
while getopts ":t:n:s:" ARGS; do
    case $ARGS in
        t)
            TESTNAME=${OPTARG}
            ;;
        n)
            NUM_RUN=${OPTARG}
            ((NUM_RUN > 0)) || usage
            ;;
        s)
            SKIP_COMMIT=${OPTARG}
            ((SKIP_COMMIT > 0)) || usage
            ;;
        *)
            usage
            ;;
    esac
done

if [ -z "${TESTNAME}" ]; then
    usage
fi

exportMsg() {
    echo "Log exported to $LOG_FILE"
}
runScript() {
    echo -n > "$LOG_FILE"
    PREVIOUS_COMMIT=""
    while true; do
        TEST_RESULT="1"
        for ((i=0; i < NUM_RUN; i++))
        do
            cd ~/onos
            COMMIT=$(git log -1 --pretty=fuller | grep -m1 -Po "(?<=commit\s)\w+")
            echo "Current Commit : $COMMIT"
            echo "Current Commit : $COMMIT" >> "$LOG_FILE"
            echo "1" > /tmp/findPatchResult.txt
            cd ~/OnosSystemTest/TestON/bin
            ./cleanup.sh
            ./cli.py run $TESTNAME
            TEST_RESULT=$(cat /tmp/findPatchResult.txt)
            echo $TEST_RESULT
            if [ "$TEST_RESULT" == "0" ]; then
                break
            fi
        done
        if [ "$TEST_RESULT" == "1" ]; then
            echo "Found the commit that has no problem : $(tput setaf 2)$COMMIT$(tput sgr 0)"
            echo "Found the commit that has no problem : $COMMIT" >> $LOG_FILE
            echo "Last commit that had a problem : $(tput setaf 1)$PREVIOUS_COMMIT$(tput sgr 0)"
            echo "Last commit that had a problem : $PREVIOUS_COMMIT" >> $LOG_FILE
            break
        fi

        cd ~/onos
        COMMIT=$(git log -1 --skip $SKIP_COMMIT --pretty=fuller | grep -m1 -Po "(?<=commit\s)\w+")
        echo "New commit to be tested : $COMMIT"
        echo "New commit to be tested : $COMMIT" >> $LOG_FILE
        PREVIOUS_COMMIT=$COMMIT
        STASH_RESULT=$(git stash)
        git checkout $COMMIT
        if [ "$STASH_RESULT" != "No local changes to save" ]; then
            git stash pop
        fi
    done
}

runScript
echo >> $LOG_FILE
echo >> $LOG_FILE
exportMsg
