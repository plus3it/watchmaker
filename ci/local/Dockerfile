FROM  public.ecr.aws/docker/library/python:3.12-alpine

ENV PIP_ROOT_USER_ACTION=ignore

COPY requirements/pip.txt requirements/pip.txt
COPY requirements/basics.txt requirements/basics.txt
COPY requirements/docs.txt requirements/docs.txt
COPY requirements/docs-check.txt requirements/docs-check.txt

RUN pip install -r requirements/pip.txt ; \
    pip install -r requirements/basics.txt ; \
    pip install -r requirements/docs.txt ; \
    pip install -r requirements/docs-check.txt
