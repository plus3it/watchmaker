FROM public.ecr.aws/docker/library/almalinux:8@sha256:9cf50481aca02c0112131e589e9eac358fb43977bcf2350b542a6de1d2484178

ARG USER=wam-builder
ARG USER_UID
ARG USER_GID

ARG PYTHON_BUILD_STANDALONE_VERSION=
ENV PYTHON_VERSION=3.14
ENV PYTHON=/opt/python/bin/python${PYTHON_VERSION}
ENV PATH="/opt/python/bin:${PATH}"

USER root

RUN if [[ ${USER_UID} -eq 0 ]] ; then adduser ${USER} ; \
    else if ! getent group "$USER_GID" ; then groupadd --gid ${USER_GID} ${USER} ; \
    else GROUP_NAME=$(getent group $USER_GID | awk -F':' '{print $1}') ; groupmod -n ${USER} "$GROUP_NAME" ; fi \
    && adduser --uid ${USER_UID} --gid ${USER_GID} ${USER} ; fi

COPY --chown=${USER}:${USER} requirements/basics.txt /requirements/basics.txt
COPY .github/workflows/dependabot_hack.yml /tmp/dependabot_hack.yml

RUN dnf install -y curl ca-certificates tar gzip \
    && dnf clean all

RUN if [[ -z "${PYTHON_BUILD_STANDALONE_VERSION}" ]]; then \
        PYTHON_BUILD_STANDALONE_VERSION=$(sed -n 's/.*python-build-standalone@//p' /tmp/dependabot_hack.yml); \
    fi \
    && if [[ -z "${PYTHON_BUILD_STANDALONE_VERSION}" ]]; then \
        echo "Error: Could not determine python-build-standalone version"; \
        exit 1; \
    fi \
    && PYTHON_RELEASE_URL="https://github.com/astral-sh/python-build-standalone/releases/expanded_assets/${PYTHON_BUILD_STANDALONE_VERSION}" \
    && PYTHON_FULL_VERSION=$(curl -sSL "$PYTHON_RELEASE_URL" | \
        grep -oE "cpython-${PYTHON_VERSION}\\.[0-9]+\\+${PYTHON_BUILD_STANDALONE_VERSION}-x86_64-unknown-linux-gnu-install_only_stripped\\.tar\\.gz" | \
        head -n 1 | \
        sed -E "s/^cpython-(${PYTHON_VERSION}\\.[0-9]+)\\+.*$/\\1/") \
    && if [[ -z "$PYTHON_FULL_VERSION" ]]; then \
        echo "Error: Could not determine Python ${PYTHON_VERSION} patch version from release ${PYTHON_BUILD_STANDALONE_VERSION}"; \
        exit 1; \
    fi \
    && PYTHON_RELEASE="cpython-${PYTHON_FULL_VERSION}+${PYTHON_BUILD_STANDALONE_VERSION}-x86_64-unknown-linux-gnu-install_only_stripped.tar.gz" \
    && PYTHON_URL="https://github.com/astral-sh/python-build-standalone/releases/download/${PYTHON_BUILD_STANDALONE_VERSION}/${PYTHON_RELEASE}" \
    && curl -sSL -o /tmp/python.tar.gz "$PYTHON_URL" \
    && mkdir -p /opt/python \
    && tar -xzf /tmp/python.tar.gz -C /opt/python --strip-components=1 \
    && rm -f /tmp/python.tar.gz

RUN ${PYTHON} -m ensurepip --upgrade --default-pip \
    && ${PYTHON} -m pip install -r /requirements/basics.txt \
    && ${PYTHON} -m pip list

USER ${USER}

ENV HOME="/home/${USER}"
