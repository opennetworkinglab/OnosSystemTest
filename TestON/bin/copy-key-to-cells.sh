#!/bin/bash
# ------------------------------------------------------------------------
# This script is a workaround for the key collision issue when loging into
# onos cli from both test-station and onos cells with identical user names.
# It copies both private and public keys of localhost (test-station) to
# all remote hosts specified in your cell.
# It also backs up the original keys of the remote hosts before
# overwriting them.
# Setting up passwordless login is recommended before running the script.
# ------------------------------------------------------------------------

ADDRESSES=()
# Check if OC1 to OC7 exist
for i in $(seq 1 7); do
    if [ -n "$OC$i" ]; then
        TEMP=OC$i
        ADDRESSES+=(${!TEMP})
    fi
done

# Check if OCN exists
[ -n "$OCN" ] && ADDRESSES+=($OCN)

# Copy keys to remote hosts
for address in "${ADDRESSES[@]}"; do
    echo "Backing up remote keys on" $address
    ssh sdn@$address "cd ~/.ssh; \
    cp id_rsa id_rsa.old; \
    cp id_rsa.pub id_rsa.pub.old; "

    echo "Copying keys to" $address
    scp ~/.ssh/id_rsa sdn@$address:~/.ssh/
    scp ~/.ssh/id_rsa.pub sdn@$address:~/.ssh/
done
