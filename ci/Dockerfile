FROM public.ecr.aws/docker/library/almalinux:8@sha256:9cf50481aca02c0112131e589e9eac358fb43977bcf2350b542a6de1d2484178

ARG USER=wam-builder
ARG USER_UID
ARG USER_GID

ENV PYTHON_VERSION=3.14
ENV PYTHON=/opt/python/bin/python${PYTHON_VERSION}
ENV PATH="/opt/python/bin:${PATH}"

USER root

RUN if [[ ${USER_UID} -eq 0 ]] ; then adduser ${USER} ; \
    else if ! getent group "$USER_GID" ; then groupadd --gid ${USER_GID} ${USER} ; \
    else GROUP_NAME=$(getent group $USER_GID | awk -F':' '{print $1}') ; groupmod -n ${USER} "$GROUP_NAME" ; fi \
    && adduser --uid ${USER_UID} --gid ${USER_GID} ${USER} ; fi

COPY --chown=${USER}:${USER} requirements/basics.txt /requirements/basics.txt

RUN dnf install -y curl ca-certificates \
    && dnf clean all

RUN UV_VERSION=$(grep -oE 'uv==[0-9.]+' /requirements/basics.txt | cut -d= -f3) \
    && curl -LsSf "https://astral.sh/uv/${UV_VERSION}/install.sh" | UV_INSTALL_DIR=/usr/local/bin sh \
    && uv python install "${PYTHON_VERSION}" --install-dir /opt/uv-python --no-bin \
    && PYTHON_DIR=$(find /opt/uv-python -mindepth 1 -maxdepth 1 -type d -name "cpython-${PYTHON_VERSION}.*" | head -n 1) \
    && ln -sf "$PYTHON_DIR" /opt/python

USER ${USER}

ENV HOME="/home/${USER}"
