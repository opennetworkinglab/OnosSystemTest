#!/usr/bin/env bash

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

# TestON install script for Ubuntu (Debian and Fedora)

# Fail on error
set -e

# Fail on unset var usage
set -o nounset

function init {
    # Identify Linux release
    DIST=Unknown
    RELEASE=Unknown
    CODENAME=Unknown

    ARCH=`uname -m`
    if [ "$ARCH" = "x86_64" ]; then ARCH="amd64"; fi
    if [ "$ARCH" = "i686" ]; then ARCH="i386"; fi

    if [ -e /etc/debian_version ]; then DIST="Debian"; fi
    if [ -e /etc/fedora-release ]; then DIST="Debian"; fi
    grep Ubuntu /etc/lsb-release &> /dev/null && DIST="Ubuntu"

    if [ "$DIST" = "Ubuntu" ] || [ "$DIST" = "Debian" ]; then
        install='sudo apt-get -y install'
        remove='sudo apt-get -y remove'
        pipinstall='sudo pip install'
        # Prereqs for this script
        if ! which lsb_release &> /dev/null; then
            $install lsb-release
        fi
    fi

    if [ "$DIST" = "Fedora" ]; then
        install='sudo yum -y install'
        remove='sudo yum -y erase'
        pipinstall='sudo pip install'
        # Prereqs for this script
        if ! which lsb_release &> /dev/null; then
            $install redhat-lsb-core
        fi
    fi
    if which lsb_release &> /dev/null; then
        DIST=`lsb_release -is`
        RELEASE=`lsb_release -rs`
        CODENAME=`lsb_release -cs`
    fi
    echo "Detected Linux distribution: $DIST $RELEASE $CODENAME $ARCH"

    if ! echo $DIST | egrep 'Ubuntu|Debian|Fedora'; then
        echo "Install.sh currently only supports Ubuntu, Debian and Fedora."
        exit 1
    fi

    #Get location of TestON dir
    SOURCE="${BASH_SOURCE[0]}"
    while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
        DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
        SOURCE="$(readlink "$SOURCE")"
        [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
    done
    DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
    echo "Found TestON at $DIR"
}

function requirements {
    system_reqs
    python_reqs
}

function system_reqs {
    # Specify a specific command with $1
    set +o nounset
    if [ -z $1 ]
    then
        cmd=$install
    else
        cmd=$1
    fi
    set -o nounset
    # Install TestON dependencies
    echo "Installing TestON dependencies"
    if [ "$DIST" = "Fedora" ]; then
        # Fedora may have vlan enabled by default. Still need to confirm and update later
        $cmd python-pip build-essential python-dev pep8 python3-requests
    else
        $cmd python-pip build-essential python-dev pep8 vlan python3-requests
    fi

    # Some Distos have this already from another package
    if which arping > /dev/null ; then
        echo "Arping command detected, skipping package installation."
    else
        $cmd arping
    fi
}

function python_reqs {
    # Specify a specific pip command with $1
    set +o nounset
    if [ -z $1 ]
    then
        cmd=$pipinstall
    else
        cmd=$1' install'
    fi
    set -o nounset
    $cmd -r requirements.txt
}

function jenkins_req {
    set +o nounset
    if [ -z $1 ]
    then
        dir='/var/jenkins'
    else
        dir=$1
    fi
    set -o nounset
    # make sure default jenkin's directory exists and is owned by current user?
    set +e
    sudo mkdir $dir
    set -e
    sudo chown $USER:$USER $dir
    # Postgresql for storing results in the db
    echo "Installing dependencies required for Jenkins test-station"
    $install postgresql postgresql-contrib
    # R for generating graphs for the wiki summary
    $install r-base-core libpq-dev
    echo 'cat(".Rprofile: Setting UK repository"); r = getOption("repos"); r["CRAN"] = "http://cran.uk.r-project.org"; options(repos = r); rm(r)' > ~/.Rprofile
    sudo R -e 'install.packages( c( "ggplot2", "reshape2", "RPostgreSQL" ) )'
}
function symlinks {
    set +e
    # Add symbolic link to main TestON folder in Home dir
    pushd ~
    sudo ln -s $DIR && echo "Added symbolic link to TestON folder in HOME directory."
    popd

    # Add symbolic link to TestON cli in /usr/local/bin
    pushd /usr/local/bin
    sudo ln -s $DIR/bin/cli.py teston && echo "Added symbolic link to TestON CLI in /usr/local/bin."
    popd

    # Add symlink to get bash completion
    pushd /etc/bash_completion.d
    sudo cp $DIR/bin/.teston_completion teston_completion
    echo "Bash completion will now be enabled for new shells"
    popd
    set -e
}

function git {
    # OnosSystemTest git pre-commit hooks
    pushd $DIR/..
    cp .git/hooks/pre-commit.sample .git/hooks/pre-commit
    popd
}

function get_pypy {
    echo "Getting pypy"
    pushd ~
    if [ ! -e pypy2-v5.3.1-linux64.tar.bz2 ]
    then
        wget https://bitbucket.org/pypy/pypy/downloads/pypy2-v5.3.1-linux64.tar.bz2
    fi
    tar xf pypy2-v5.3.1-linux64.tar.bz2
    python_impl=~/pypy2-v5.3.1-linux64/bin/pypy
    popd
    venv $python_impl "venv-teston-pypy"
}

# Optionally install in virtual env
function venv {
    # $1 is the path to python implementation, $2 is the venv-name
    echo "Installing virtual env for TestON..."
    pushd $DIR
    set +o nounset
    if [ -z "$2" ]
    then
        venv_name="venv-teston"
    else
        venv_name=$2
    fi
    pip install virtualenv

    # Setup virtual env
    if [ -z "$1" ]; then
        echo "No python implementation specified for virtual env, using default."
        virtualenv $venv_name
    else
        python_impl=$1
        echo "Using $python_impl for python in virtual env."
        virtualenv -p $python_impl $venv_name
    fi
    python_reqs $venv_name/bin/pip
    set -o nounset
    popd
}


function default {
    requirements
    symlinks
    git
}

function finished {
    echo ""
    echo "Completed running install.sh script"
    echo "Run TestON CLI by typing teston at bash prompt"
    echo "Example: teston run <TestSuite Name>"
}

# TODO Add log rotation configuration for TestON logs here (place holder)
# TODO Add bash tab completion script to this

function usage {
    printf "Usage: $(basename $0) [-dgjprsv] \n"
    printf "Usage: $(basename $0) -y [PATH] \n\n"
    printf "This install script attempts to install dependencies needed to run teston\n"
    printf "and any tests included in the official repository. If a test still does \n"
    printf "not run after running this script, you can try looking at the test's README\n"
    printf "or the driver files used by the tests. There are some software components\n"
    printf "such as software switches that this script does not attempt to install as\n"
    printf "they are more complicated.\n\n"

    printf "Options:\n"
    printf "\t -d (default) requirements, symlinks and git hooks\n"
    printf "\t -g install git hooks\n"
    printf "\t -j install requirments for running this node as a Jenkin's test-station\n"
    printf "\t -p install pypy in a virtual env\n"
    printf "\t -r install requirements for TestON/tests\n"
    printf "\t -s install symlinks\n"
    printf "\t -v install a python virtual environment for teston using the default python implementation\n"
    printf "\t -y <PATH> install a python virtual environment for teston using a specific python implementation at PATH.\n"

}

if [ $# -eq 0 ]
then
    init
    default
elif [ $1 == "--help" ]
then
    usage
else
    init
    while getopts 'dgjprsvy:' OPTION
    do
      case $OPTION in
      d)    default;;
      g)    git;;
      j)    jenkins_req;;
      p)    get_pypy;;
      r)    requirements;;
      s)    symlinks;;
      v)    venv;;
      y)    venv $OPTARG;;
      ?)    usage;;
      esac
  done
  shift $(($OPTIND -1))
  finished
fi
