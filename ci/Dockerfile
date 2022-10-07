FROM quay.io/centos7/python-38-centos7:centos7@sha256:c51abeede0558a0d1451e0ec6c2a312fd33f383a02c6b1890c95f7ef1fd1effd

ARG USER=wam-builder
ARG USER_UID
ARG USER_GID

USER root

RUN if [[ ${USER_UID} -eq 0 ]] ; then adduser ${USER} ; \
    else if ! getent group "$USER_GID" ; then groupadd --gid ${USER_GID} ${USER} ; \
    else GROUP_NAME=$(getent group $USER_GID | awk -F':' '{print $1}') ; groupmod -n ${USER} "$GROUP_NAME" ; fi \
    && adduser --uid ${USER_UID} --gid ${USER_GID} ${USER} ; fi

COPY --chown=${USER}:${USER} requirements/pip.txt /requirements/pip.txt
COPY --chown=${USER}:${USER} requirements/basics.txt /requirements/basics.txt

RUN python3 -m ensurepip --upgrade --default-pip \
    && python3 -m pip install -r /requirements/pip.txt \
    && python3 -m pip --version \
    && python3 -m pip install -r /requirements/basics.txt \
    && python3 -m pip list

USER ${USER}

ENV LC_ALL=en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV HOME="/home/${USER}"
