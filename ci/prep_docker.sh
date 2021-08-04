#!/bin/bash

set -eu -o pipefail

echo "***********************************************************************"
echo "Prepping for Docker Watchmaker build on $(lsb_release -a)"
echo "***********************************************************************"

DOCKER_INSTANCE_NAME=wam-builder
echo "DOCKER_INSTANCE_NAME:${DOCKER_INSTANCE_NAME}"

WORKDIR="${WORKDIR:-${TRAVIS_BUILD_DIR:-}}"
WORKDIR="${WORKDIR:-${PWD}}"
echo "WORKDIR:${WORKDIR}"

if [ -n "${WORKDIR}" ]; then

  echo "Building Docker container..."
  docker build \
    --build-arg USER_UID="$(id -u)" \
    --build-arg USER_GID="$(id -g)" \
    -t $DOCKER_INSTANCE_NAME -f "${WORKDIR}/ci/Dockerfile" .

  echo "Building using container and workdir (${WORKDIR})..."
  docker run --detach --privileged \
    --user "$(id -u):$(id -g)" \
    --volume="${WORKDIR}:${WORKDIR}" \
    --workdir "${WORKDIR}" \
    --name "${DOCKER_INSTANCE_NAME}" \
    "${DOCKER_INSTANCE_NAME}:latest" \
    init

  echo "Building the standalone using ci/build.sh..."
  docker exec "${DOCKER_INSTANCE_NAME}" chmod +x ci/build.sh
  docker exec "${DOCKER_INSTANCE_NAME}" ci/build.sh

  echo "Stopping the docker container ${DOCKER_INSTANCE_NAME}..."
  docker stop "${DOCKER_INSTANCE_NAME}"
  echo "Removing the docker image ${DOCKER_INSTANCE_NAME}..."
  docker rm "${DOCKER_INSTANCE_NAME}"

else

  echo "No WORKDIR provided so not building..."

fi
