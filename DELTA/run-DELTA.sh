#!/bin/bash
# This script automates DELTA tests (All-In-One Single Machine mode). It
# installs DELTA and all dependencies; brings up VMs and configures the
# network; triggers tests using a python script (run-DELTA.py); cleans
# up the environment after tests are done.
# Note: run-DELTA.py and this script should be put in the same folder

set -e

DELTA_PATH=/home/sdn

# Install DELTA and dependencies
function init_delta() {
    echo "*** Initialize DELTA ***"
    if [ ! -d "$DELTA_DIR" ]
    then
        echo "Downloading DELTA..."
        (cd $DELTA_PATH && git clone https://github.com/OpenNetworkingFoundation/DELTA.git)
        cd $DELTA_DIR
        echo "Installing DELTA dependencies..."
        ./tools/dev/delta-setup/delta-setup-devenv-ubuntu
        echo "Building DELTA..."
        source ./tools/dev/delta-setup/bash_profile
        mvn clean install
        echo "Installing virtualbox and vagrant..."
        ./tools/dev/delta-setup/delta-setup-vms-ubuntu
        # TODO: change ./tools/config/manager.cfg
        cd -
    fi
}

# Bring up VMs and config network
function setup_vm() {
    echo "*** Setting up VMs ***"
    echo "Bringing up VMs..."
    cd $DELTA_DIR"/tools/dev/vagrant/"
    vagrant up >/dev/null 2>&1
    echo "Checking if all VMs are up..."
    vagrant status | grep controller | grep running
    vagrant status | grep channel | grep running
    vagrant status | grep mininet | grep running
    echo "Setting up NAT network..."
    VBoxManage natnetwork add --netname NatNetwork --network 10.0.2.0/24 --enable --dhcp on
    VBoxManage controlvm $(VBoxManage list vms | grep mininet | awk '{print $1}' | sed 's/"//g') nic1 natnetwork NatNetwork
    VBoxManage controlvm $(VBoxManage list vms | grep mininet | awk '{print $1}' | sed 's/"//g') nicpromisc1 allow-all
    source ../delta-setup/bash_profile
    if [[ $INIT_VM -eq 1 ]]
    then
        INIT_VM=0
        echo "Setting up passwordless login..."
        for vm in $DELTA_APP $DELTA_CHANNEL $DELTA_HOST
        do
            IFS=@ read name ip <<< $vm
            ssh-keygen -f "$HOME/.ssh/known_hosts" -R $ip
            cat ~/.ssh/id_rsa.pub | sshpass -p "vagrant" ssh -o StrictHostKeyChecking=no $vm 'cat >> .ssh/authorized_keys'
        done
        echo "Setting up DELTA_APP VM..."
        ssh $DELTA_APP "sudo echo 'export JAVA_HOME=/usr/lib/jvm/java-8-oracle' | sudo tee --append /etc/environment;\
                        sudo echo 'export ONOS_APPS=drivers,openflow,proxyarp,mobility,fwd' | sudo tee --append /etc/environment"
        echo "Copying files to VMs..."
        ../onos-setup/onos-1.6.0-scp
        ../delta-setup/delta-agents-scp
    fi
    echo "Setting up ONOS..."
    ssh $DELTA_APP "echo 'Downloading ONOS nightly build...';\
                    set -e;\
                    wget -c http://downloads.onosproject.org/nightly/$NIGHTLY_FILE_NAME.tar.gz >/dev/null 2>&1;\
                    tar xzf $NIGHTLY_FILE_NAME.tar.gz;\
                    rm $NIGHTLY_FILE_NAME.tar.gz;\
                    if [ -d onos ]; then rm -r onos; fi;\
                    mv onos-*-SNAPSHOT onos;\
                    cp delta-agent-app-onos-1.6-1.0-SNAPSHOT.jar onos/apache-karaf-*/deploy/"
    cd -
}

# Run DELTA tests
function run_test() {
    echo "*** Run tests ***"
    cd $DELTA_DIR
    source ./tools/dev/delta-setup/bash_profile
    cd -
    ./run-DELTA.py $DELTA_DIR
}

# Clean up
function teardown_vm() {
    echo "*** Tearing down VMs ***"
    echo "Killing DELTA..."
    sudo kill -9 $(ps -ef | grep delta-manager | grep -v grep | awk '{print $2}')
    echo "Deleting NAT network..."
    VBoxManage controlvm $(VBoxManage list vms | grep mininet | awk '{print $1}' | sed 's/"//g') nic1 nat || echo "nic1 of mininet VM not reset"
    VBoxManage natnetwork remove --netname NatNetwork || echo "NAT network not removed"
    echo "Bringing down VMs..."
    cd $DELTA_DIR"/tools/dev/vagrant/"
    if [[ $INIT_VM -eq 1 ]]
    then
        vagrant destroy -f
        echo "Checking if all VMs are gone..."
        vagrant status | grep controller | grep "not created"
        vagrant status | grep channel | grep "not created"
        vagrant status | grep mininet | grep "not created"
    else
        vagrant halt
        echo "Checking if all VMs are down..."
        vagrant status | grep controller | grep poweroff
        vagrant status | grep channel | grep poweroff
        vagrant status | grep mininet | grep poweroff
    fi
    cd -
}

INIT_DELTA=0
INIT_VM=0
NIGHTLY_FILE_NAME="onos-1.10.0.20170223-NIGHTLY"

while getopts "hdvo:p:" opt; do
    case ${opt} in
        h )
            echo "Usage:"
            echo "-h        show this help message"
            echo "-d        initialize DELTA repo, build and configure DELTA"
            echo "-v        destroy and reinstall vagrant VMs"
            echo "-o <name> specify name of ONOS nightly build file"
            echo "-p <path> specify path of DELTA"
            exit 0
        ;;
        d ) INIT_DELTA=1
        ;;
        v ) INIT_VM=1
        ;;
        o ) NIGHTLY_FILE_NAME=$OPTARG
        ;;
        p ) DELTA_PATH=$OPTARG
        ;;
        \? ) echo "Invalid option: -$OPTARG"
            exit 1
            ;;
    esac
done

DELTA_DIR=$DELTA_PATH"/DELTA"

teardown_vm

if [[ $INIT_DELTA -eq 1 ]]
then
    init_delta
fi

setup_vm

run_test

teardown_vm

echo "Done"
exit 0
