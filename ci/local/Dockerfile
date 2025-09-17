FROM public.ecr.aws/docker/library/almalinux

ENV PIP_ROOT_USER_ACTION=ignore

COPY requirements/pip.txt requirements/pip.txt
COPY requirements/basics.txt requirements/basics.txt
COPY requirements/docs.txt requirements/docs.txt
COPY requirements/docs-check.txt requirements/docs-check.txt

RUN dnf install -y python3-pip ; \
    python3 -m pip install -r requirements/pip.txt ; \
    python3 -m pip install -r requirements/basics.txt ; \
    python3 -m pip install -r requirements/docs.txt ; \
    python3 -m pip install -r requirements/docs-check.txt ; \
    python3 -m pip install myst_parser ; \
    python3 -m pip install sphinx-rtd-theme ; \
    python3 -m pip install --upgrade sphinx
