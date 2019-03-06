#!/bin/bash

set -xe -o pipefail

echo "***********************************************************************"
echo "Prepping for Docker Watchmaker build on $(lsb_release -a)"
echo "***********************************************************************"

echo "Remove old docker versions..."
# if unable to remove, it is not a problem
sudo apt-get -y remove docker docker-engine docker.io || true

echo "Install new docker..."
# https://docs.docker.com/install/linux/docker-ce/ubuntu/
sudo apt-get update
sudo apt-get -y install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo apt-key fingerprint 0EBFCD88

sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
sudo apt-get update
sudo apt-get -y install docker-ce docker-ce-cli containerd.io

if [ -n "${DOCKER_SLUG}" ]; then

  echo "Installing Docker container..."
  sudo docker pull "${DOCKER_SLUG}":latest

  DOCKER_INSTANCE_NAME="${DOCKER_INSTANCE_NAME:-wam-builder}"
  echo "DOCKER_INSTANCE_NAME:${DOCKER_INSTANCE_NAME}"
  echo "DOCKER_SLUG:${DOCKER_SLUG}"

  WORKDIR="${WORKDIR:-${TRAVIS_BUILD_DIR}}"
  WORKDIR="${WORKDIR:-${PWD}}"

  if [ -n "${WORKDIR}" ]; then

    echo "Building using container and workdir (${WORKDIR})..."
    sudo docker run --detach --privileged \
      --volume="${WORKDIR}":"${WORKDIR}" \
      --workdir "${WORKDIR}" \
      --name "${DOCKER_INSTANCE_NAME}" \
      "${DOCKER_SLUG}":latest \
      init

    sudo docker exec "${DOCKER_INSTANCE_NAME}" chmod +x ci/build.sh
    sudo docker exec "${DOCKER_INSTANCE_NAME}" ci/build.sh

    sudo docker stop "${DOCKER_INSTANCE_NAME}"

  else

    echo "No WORKDIR provided so not building..."

  fi

else

  echo "No DOCKER_SLUG provided so not installing container..."

fi
