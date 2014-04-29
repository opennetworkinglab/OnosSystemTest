TestON, a testing infastructure by Paxterra
=======================================
TestON is the testing platform that all the ONOS tests are being run on currently. 


Setup 
-------------

0. Pull the git repo from https://github.com/OPENNETWORKINGLAB/ONLabTest.git 

    $ git clone https://github.com/OPENNETWORKINGLAB/ONLabTest.git

1. Make a symbolic link for TestON on the HOMEDIR 
   Execute the following from the home directory  

    $ ln -s ONLabTest/TestON TestON

2. Make sure python path is correct 

    $ export PYTHONPATH={PATH TO HOMEDIR}/TestON/

    $ echo $PYTHONPATH 


Dependencies
------------
1. Zookeeper

2. Cassandra

3. ONOS

4. Mininet

5. Install python packages configObj and pexpect. they can be installed as :

     $ sudo pip install configObj

     $ sudo easy_install pexpect 

Configuration
------------

1. Config file at TestON/config/teston.cfg

    Change the file paths to the appropriate paths

2. The .topo file for each test
 
    Must change the IPs/login/etc to point to the nodes you want to run on

Running TestON
------------

1. TestON must be ran from its bin directory 

    $ cd TestON/bin

2. Launch cli

    $ ./cli.py 

3. Run the test 

    teston> run MininetTest 

The Tests
-----------------------------------------------

The tests are all located it TestON/tests/
Each test has its own folder with the following files: 

1. .ospk file

    - This is written in Openspeak, an word based language developed by Paxterra.

    - It defines the cases and sequence of events for the test 

2. .py file
 
    - This file serves the same exact function as the openspeak file. 

    - It will only be used if there is NO .ospk file, so if you like python, delete or rename the .ospk file 
 
3. .topo file  

    - This defines all the components that TestON creates for that test and includes data such as IP address, login info, and device drivers  
 
    - The Components must be defined in this file to be uesd in the openspeak or python files. 
    
4. .params file

    - Defines all the test-specific variables that are used by the test. 

    - NOTE: The variable `testcases` which defines which testcases run when the test is ran. 

Troubleshooting
-----------------------------------------------
Here are a few things to check if it doesn't work

1. Double check the topo file for that specific test the nodes must be able to run that specific component ( Mininet IP -> machine with mn installed)

2. Enable passwordless logins between your nodes and the TestON node.  
