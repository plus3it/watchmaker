FROM centos:centos7@sha256:0f4ec88e21daf75124b8a9e5ca03c37a5e937e0e108a255d890492430789b60e

ARG USER=wam-builder
ARG USER_UID
ARG USER_GID

RUN yum -y install python3 \
    && yum clean all

RUN groupadd --gid ${USER_GID} ${USER} \
    && adduser --uid ${USER_UID} --gid ${USER_GID} ${USER}

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
