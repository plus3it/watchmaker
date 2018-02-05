# -*- coding: utf-8 -*-
"""Extends urllib with additional handlers."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import io
from email import message_from_string

from six.moves import urllib

HAS_BOTO3 = False
try:
    import boto3
    HAS_BOTO3 = True
except ImportError:
    pass


class BufferedIOS3Key(io.BufferedIOBase):
    """Add a read method to S3 key object."""

    def __init__(self, key):
        self.read = key.get()['Body'].read


class S3Handler(urllib.request.BaseHandler):
    """Define urllib handler for S3 objects."""

    def s3_open(self, req):
        """Open S3 objects."""
        # Credit: <https://github.com/ActiveState/code/tree/master/recipes/Python/578957_Urllib_handler_AmazS3>  # noqa: E501

        # The implementation was inspired mainly by the code behind
        # urllib.request.FileHandler.file_open().

        try:
            # py3 urllib
            selector = req.selector
        except AttributeError:
            # py2 urllib2
            selector = req.get_selector()

        bucket_name = req.host
        key_name = selector[1:]

        if not bucket_name or not key_name:
            raise urllib.error.URLError(
                'url must be in the format s3://<bucket>/<key>'
            )

        try:
            s3 = self._s3
        except AttributeError:
            s3 = self._s3 = boto3.resource("s3")

        key = s3.Object(bucket_name=bucket_name, key=key_name)

        origurl = 's3://{}/{}'.format(bucket_name, key_name)

        if key is None:
            raise urllib.error.URLError('no such resource: {}'.format(origurl))

        headers = [
            ('Content-type', key.content_type),
            ('Content-encoding', key.content_encoding),
            ('Content-language', key.content_language),
            ('Content-length', key.content_length),
            ('Etag', key.e_tag),
            ('Last-modified', key.last_modified),
        ]

        headers = message_from_string(
            '\n'.join(
                '{0}: {1}'.format(header, value) for header, value in headers
                if value is not None
            )
        )

        return urllib.response.addinfourl(
            BufferedIOS3Key(key), headers, origurl
        )


if HAS_BOTO3:
    s3_opener = urllib.request.build_opener(S3Handler)
    urllib.request.install_opener(s3_opener)

urlopen = urllib.request.urlopen
