#!/usr/bin/env bash

# TestON install script for Ubuntu (Debian and Fedora)

# Fail on error
set -e

# Fail on unset var usage
set -o nounset

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

# Check OnosSystemTest is cloned in home directory.
if [ ! -d ~/OnosSystemTest ]; then
    echo "Could not find OnosSystemTest in your home directory."
    echo "Exiting from running install script."
    exit 1
fi

# Install TestON dependencies
echo "Installing TestON dependencies"
if [ "$DIST" = "Fedora" ]; then
    # Fedora may have vlan enabled by default. Still need to confirm and update later
    $install python-pip build-essential python-dev pep8 arping
    $pipinstall pexpect==3.2 configobj==4.7.2 numpy
else
    $install python-pip build-essential python-dev pep8 vlan arping
    $pipinstall pexpect==3.2 configobj==4.7.2 numpy
fi

# Add check here to make sure OnosSystemTest is cloned into home directory (place holder)

# Add symbolic link to main TestON folder in Home dir
pushd ~
sudo ln -s ~/OnosSystemTest/TestON TestON
echo "Added symbolic link to TestON folder in HOME directory."
popd

# OnosSystemTest git pre-commit hooks
pushd ~/OnosSystemTest
cp .git/hooks/pre-commit.sample .git/hooks/pre-commit
popd

# Add symbolic link to TestON cli in /usr/local/bin
pushd /usr/local/bin
sudo ln -s $HOME/OnosSystemTest/TestON/bin/cli.py teston
echo "Added symbolic link to TestON CLI in /usr/local/bin."
popd

# Add log rotation configuration for TestON logs here (place holder)

echo "Completed running install.sh script"
echo "Run TestON CLI by typing teston at bash prompt"
echo "Example: teston run <TestSuite Name>"
