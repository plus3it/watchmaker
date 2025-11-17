FROM  public.ecr.aws/docker/library/python:3.12-alpine

COPY requirements/basics.txt requirements/basics.txt
COPY requirements/docs.txt requirements/docs.txt
COPY requirements/docs-check.txt requirements/docs-check.txt

RUN pip install -r requirements/basics.txt
RUN uv pip install --system -r requirements/docs.txt && \
    uv pip install --system -r requirements/docs-check.txt
