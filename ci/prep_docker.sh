#!/bin/bash

set -eu -o pipefail

echo "***********************************************************************"
echo "Prepping for Docker Watchmaker build on $(lsb_release -ds 2>/dev/null || echo 'Unknown Linux')"
echo "***********************************************************************"

DOCKER_INSTANCE_NAME=wam-builder
echo "DOCKER_INSTANCE_NAME:${DOCKER_INSTANCE_NAME}"

WORKDIR="${WORKDIR:-${TRAVIS_BUILD_DIR:-}}"
WORKDIR="${WORKDIR:-${PWD}}"
echo "WORKDIR:${WORKDIR}"

if [ -n "${WORKDIR}" ]; then

  # Clean up any existing container with the same name
  if docker ps -a --format '{{.Names}}' | grep -q "^${DOCKER_INSTANCE_NAME}$"; then
    echo "Removing existing container ${DOCKER_INSTANCE_NAME}..."
    docker stop "${DOCKER_INSTANCE_NAME}" || true
    docker rm "${DOCKER_INSTANCE_NAME}"
  fi

  echo "Building Docker container..."
  docker build \
    --build-arg USER_UID="$(id -u)" \
    --build-arg USER_GID="$(id -g)" \
    -t $DOCKER_INSTANCE_NAME -f "${WORKDIR}/ci/Dockerfile" .

  # Detect if using podman and set appropriate userns flag
  USERNS_FLAG=""
  if command -v podman &> /dev/null && docker --version 2>&1 | grep -qi podman; then
    echo "Detected Podman, using --userns=keep-id"
    USERNS_FLAG="--userns=keep-id"
  fi

  echo "Building using container and workdir (${WORKDIR})..."
  docker run --detach --privileged \
    --user "$(id -u):$(id -g)" \
    ${USERNS_FLAG} \
    --volume="${WORKDIR}:${WORKDIR}" \
    --workdir "${WORKDIR}" \
    --name "${DOCKER_INSTANCE_NAME}" \
    "${DOCKER_INSTANCE_NAME}:latest" \
    init

  # Ensure container cleanup happens on exit
  cleanup() {
    echo "Stopping the docker container ${DOCKER_INSTANCE_NAME}..."
    docker stop "${DOCKER_INSTANCE_NAME}" 2>/dev/null || true
    echo "Removing the docker container ${DOCKER_INSTANCE_NAME}..."
    docker rm "${DOCKER_INSTANCE_NAME}" 2>/dev/null || true
  }
  trap cleanup EXIT

  echo "Building the standalone using ci/build.sh..."
  docker exec "${DOCKER_INSTANCE_NAME}" chmod +x ci/build.sh
  docker exec "${DOCKER_INSTANCE_NAME}" ci/build.sh

else

  echo "No WORKDIR provided so not building..."

fi
