TestON, a testing infastructure by Paxterra
=======================================
TestON is the testing platform that all the ONOS tests are being run on curretly. 


Setup 
-------------

0. Pull the git repo from https://github.com/OPENNETWORKINGLAB/ONLabTest.git 

    $ git clone https://github.com/OPENNETWORKINGLAB/ONLabTest.git

1. Make a symbolic link for TestON on the HOMEDIR 
   Execute the following from the home directory  

    $ ln -s ONLab/TestON TestON

2. Make sure python path is correct 

    $ export PYTHONPATH={PATH TO HOMEDIR}/TestON/

    $ echo $PYTHONPATH 


Dependencies
------------
1. Zookeeper

2. Cassandra

3. ONOS

4. Mininet

Configuration
------------

1. Config file at TestON/config/teston.cfg

    Change the file paths to the appropriate paths

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

    - This is written in Openspeak, an word based languaged developed by Paxterra.

    - It defines the cases that the test runs as the sequence of events in general 

2. .py file
 
    - This file serves the same exact function as the openspeak file. 

    - It will only be run when the test is called if there is NO .ospk file, so if you like python, delete or rename the .ospk file 
 
3. .topo file  

    - This defines all the components that TestON creates for that test and includes data such as IP address, login info, and device drivers  
 
    - The Components must be defined in this file to be uesd in the openspeak or python files. 
    
4. .params file

    - Defines all the test-specific variables that are used by the test. 

    - NOTE: The variable `testcases` which defines which testcases run when the test is ran. 

TODO: 
-----------------------------------------------
