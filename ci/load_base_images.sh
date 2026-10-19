#!/bin/bash
#
# Make the base images used by a Dockerfile available to the local docker
# daemon, preferring a cached tarball over pulling from the registry.
#
# Pulls from public registries are anonymous in CI and can be rate limited
# (HTTP 429), so the tarball is stored in the actions cache between runs.
#
# Usage: ci/load_base_images.sh <cache_dir> <dockerfile>

set -eu -o pipefail

CACHE_DIR="${1:?Usage: $0 <cache_dir> <dockerfile>}"
DOCKERFILE="${2:?Usage: $0 <cache_dir> <dockerfile>}"
TARBALL="${CACHE_DIR}/base-images.tar"

mkdir -p "${CACHE_DIR}"

# Collect the external image from each FROM line, ignoring stage references
# (a FROM that names an earlier `AS` stage) and scratch
mapfile -t IMAGES < <(
  sed -En 's/^FROM[[:space:]]+(--[^[:space:]]+[[:space:]]+)*([^[:space:]]+).*/\2/p' \
    "${DOCKERFILE}" \
    | grep -v '^scratch$' | sort -u
)
echo "Base images: ${IMAGES[*]}"

if [ -f "${TARBALL}" ]; then
  echo "Loading base images from cache (${TARBALL})..."
  docker load --input "${TARBALL}" || echo "Failed to load cache, will pull"
fi

PULLED=false
for image in "${IMAGES[@]}"; do
  if docker image inspect "${image}" > /dev/null 2>&1; then
    echo "Using local image: ${image}"
    continue
  fi

  echo "Pulling image: ${image}"
  for attempt in 1 2 3; do
    if docker pull "${image}"; then
      PULLED=true
      break
    fi
    [ "${attempt}" -lt 3 ] || { echo "Failed to pull ${image}"; exit 1; }
    sleep $((attempt * 10))
  done
done

if [ "${PULLED}" = true ] || [ ! -f "${TARBALL}" ]; then
  echo "Saving base images to ${TARBALL}..."
  docker save --output "${TARBALL}" "${IMAGES[@]}"
fi
