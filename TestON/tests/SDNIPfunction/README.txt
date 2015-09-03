In this test case, we use 2 VMs. One is running Mininet testbed together with
Quagga, the other one is running ONOS.

Step 1: Install and configure Quagga.
SDN-IP application uses Quagga as the BGP speaker. You need to install Quagga
on the mininet VM.
After installation, check whether the Quagga directory is /usr/lib/quagga,
otherwise you need to change the directory in SDNIPfuntionMininet.py.
Then, generate Quagga configuration files.
$cd ~/OnosSystemTest/TestON/tests/SDNIPfunction/Dependency/as4quaggas/
$./quagga-config-gen.sh

Step 2: SDN-IP/ONOS configuration.
Copy the SDN-IP/ONOS file to your ONOS directory and set the cell.
$cp ~/OnosSystemTest/TestON/tests/SDNIPfunction/network-cfg.json ~/onos/tools/package/config/network-cfg.json
$cp ~/OnosSystemTest/TestON/tests/SDNIPfunction/sdnip_single_instance ~/onos/tools/test/cells/sdnip_single_instance
Then enable the cell file:
$cell sdnip_single_instance

Step 3: copy .bash_killcmd file to ~/.bash_killcmd on Mininet VM.
Add "source .bash_killcmd " into the ~/.bashrc file, then run:
$source ~/.baschrc

Note: you only need to do Step 1, 2, and 3 once.

Step 4: each time, before starting the test, run the following command to clean
the environment.
$ killTestONall

Step 5: run Mininet testbed to setup the test environment.
$sudo ~/OnosSystemTest/TestON/tests/SDNIPfunction/Dependency/SDNIPfuntionMininet.py

Step 6: set up tunnel on Mninet VM to ONOS VM.
$ssh -nNT -o "PasswordAuthentication no" -o "StrictHostKeyChecking no" -l sdn -L 1.1.1.2:2000:10.128.4.52:2000 10.128.4.52 &

Step 7: finally you can run testOn script.
$cd ~/OnosSystemTest/TestON/bin
$./cli.py run SDNIPfunction