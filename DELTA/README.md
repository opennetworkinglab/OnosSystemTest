The scripts in this directory automates DELTA security tests against ONOS.

run-DELTA.sh automates DELTA tests (All-In-One Single Machine mode). It installs DELTA and all dependencies; brings up VMs and configures the network; triggers tests using a python script (run-DELTA.py); cleans up the environment after tests are done.
Usage of run-DELTA.sh:
-h        show help message
-d        initialize DELTA repo, build and configure DELTA
-v        destroy and reinstall vagrant VMs
-o <name> specify name of ONOS nightly build file
-p <path> specify path of DELTA

run-DELTA.py uses pexpect to talk to DELTA manager and triggers all CONTROL_PLANE_OF and ADVANCED test cases. It also reads the DELTA log and prints the results for each test case. run-DELTA.py can take one argument for specifying DELTA directory.

Note: run-DELTA.sh and run-DELTA.py should be put into the same folder.

For more information of DELTA, please go to https://github.com/OpenNetworkingFoundation/delta
