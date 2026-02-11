FROM  public.ecr.aws/docker/library/python:3.14-alpine

COPY requirements/basics.txt requirements/basics.txt
COPY requirements/docs.txt requirements/docs.txt
COPY requirements/docs-check.txt requirements/docs-check.txt
COPY ci/local/build_dox.sh /bin

RUN pip install -r requirements/basics.txt
RUN uv pip install --system -r requirements/docs.txt && \
    uv pip install --system -r requirements/docs-check.txt

CMD build_dox.sh
