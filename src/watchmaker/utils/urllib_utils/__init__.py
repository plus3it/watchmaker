"""Exposes urllib imports with additional request handlers."""


from six.moves.urllib import error, parse, request  # type:ignore # noqa F401

from watchmaker.conditions import HAS_BOTO3

if HAS_BOTO3:
    from watchmaker.utils.urllib_utils.request_handlers import S3Handler

    request.install_opener(request.build_opener(S3Handler))
