#!/bin/bash
# SPDX-FileCopyrightText: Copyright 2021-present Open Networking Foundation.
# SPDX-License-Identifier: Apache-2.0
# Usage:
# ./build.sh [--wk] [--di]
#
# Options:
# --wk: with user's SSH key.
# --di: with DeepInsight utility library(from a private repo)

set -euo pipefail

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
TEST_ON_DIR="$(cd ${THIS_DIR}/.. && pwd)"
CONTAINER_FS="${THIS_DIR}/fs"
DI_UTIL_REPO="git@github.com:opennetworkinglab/bf-di-scripts.git"

mkdir -p "${CONTAINER_FS}/tmp"
rm -rf "${CONTAINER_FS}/tmp/additional-py-pkgs.txt"
touch "${CONTAINER_FS}/tmp/additional-py-pkgs.txt"

for op in $@; do
    case $op in
        '--wk' )
            rm -rf "${CONTAINER_FS}/home/jenkins/.ssh"
            cp -r "${HOME}/.ssh" "${CONTAINER_FS}/home/jenkins/.ssh"
        ;;
        '--di' )
            rm -rf "${CONTAINER_FS}/tmp/bf-di-scripts"
            git clone "${DI_UTIL_REPO}" "${CONTAINER_FS}/tmp/bf-di-scripts"
            echo "/tmp/bf-di-scripts/4/utility" > "${CONTAINER_FS}/tmp/additional-py-pkgs.txt"
        ;;
    esac
done

docker build -t teston -f "${THIS_DIR}/Dockerfile" "${TEST_ON_DIR}"
