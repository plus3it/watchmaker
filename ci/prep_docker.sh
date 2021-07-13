#!/bin/bash

set -xe -o pipefail

echo "***********************************************************************"
echo "Prepping for Docker Watchmaker build on $(lsb_release -a)"
echo "***********************************************************************"

if [ -n "${DOCKER_SLUG}" ]; then

  echo "Installing Docker container..."
  docker pull "${DOCKER_SLUG}":latest

  DOCKER_INSTANCE_NAME="${DOCKER_INSTANCE_NAME:-wam-builder}"
  echo "DOCKER_INSTANCE_NAME:${DOCKER_INSTANCE_NAME}"
  echo "DOCKER_SLUG:${DOCKER_SLUG}"

  WORKDIR="${WORKDIR:-${TRAVIS_BUILD_DIR}}"
  WORKDIR="${WORKDIR:-${PWD}}"

  if [ -n "${WORKDIR}" ]; then

    echo "Building using container and workdir (${WORKDIR})..."
    docker run --detach --privileged \
      --volume="${WORKDIR}":"${WORKDIR}" \
      --workdir "${WORKDIR}" \
      --name "${DOCKER_INSTANCE_NAME}" \
      "${DOCKER_SLUG}":latest \
      init

    docker exec "${DOCKER_INSTANCE_NAME}" chmod +x ci/build.sh
    docker exec "${DOCKER_INSTANCE_NAME}" ci/build.sh

    docker stop "${DOCKER_INSTANCE_NAME}"
    docker rm "${DOCKER_INSTANCE_NAME}"

  else

    echo "No WORKDIR provided so not building..."

  fi

else

  echo "No DOCKER_SLUG provided so not installing container..."

fi
