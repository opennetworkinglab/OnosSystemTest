#!/bin/bash
# SPDX-FileCopyrightText: Copyright 2021-present Open Networking Foundation.
# SPDX-License-Identifier: Apache-2.0
set -euo pipefail
SSH_PORT=${SSH_PORT:-2222}
THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
TEST_ON_DIR="$(cd ${THIS_DIR}/.. && pwd)"

function cleanup() {
    echo "Stopping TestON container"
    docker stop teston
}
trap cleanup EXIT

echo "Starting TestON container..."

docker run -d --rm --init --name teston \
           -p $SSH_PORT:22 \
           -v $TEST_ON_DIR:/home/jenkins/teston \
           teston

echo "SSH server listen on $SSH_PORT"
echo "Attaching to the container..."
docker exec -it -u jenkins teston bash -c "cd /home/jenkins && bash"
