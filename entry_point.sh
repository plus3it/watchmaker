#!/usr/bin/env bash
set -e

LOGTAG=systemprep
WORKINGDIR=/usr/tmp/"${LOGTAG}"
BOOTSTRAP="https://s3.amazonaws.com/systemprep/Rewrite/BootStrapScripts/SystemPrep-Bootstrap--Linux.sh"

if [[ -n "${BOOTSTRAP}" ]]; then
    BOOTSTRAP_FILENAME=$(echo ${BOOTSTRAP} | awk -F'/' '{ print ( $(NF) ) }')
    BOOTSTRAP_FULLPATH=${WORKINGDIR}/${BOOTSTRAP_FILENAME}
    cd ${WORKINGDIR}
    echo "Downloading aws cli -- ${BOOTSTRAP}"
    curl -L -O -s -S ${BOOTSTRAP} || \
            ( echo "Could not download file. Check the url and whether 'curl' is in the path. Quitting..." && exit 1 )
    bash ${BOOTSTRAP_FULLPATH}
fi