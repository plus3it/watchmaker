import pytest  # noqa: F401
import requests  # noqa: F401
import responses

from watchmaker.utils.imds.detect.providers.aws_provider import AWSProvider


def test_reading_invalid_vendor_file():
    provider = AWSProvider()
    assert provider.check_vendor_file() is False


# @responses.activate
def test_valid_metadata_server_check():
    # mocking_url = "http://testing_metadata_url.com"
    # responses.add(
    #     responses.GET,
    #     "http://testing_metadata_url.com",
    #     json={"imageId": "ami-12312412", "instanceId": "i-ec12as"},
    # )

    provider = AWSProvider()
    # provider.metadata_url = mocking_url
    assert provider.check_metadata_server() is True


# @responses.activate
def test_invalid_metadata_server_check():
    # mocking_url = "http://testing_metadata_url.com"
    # responses.add(
    #     responses.GET,
    #     "http://testing_metadata_url.com",
    #     json={"imageId": "some_ID", "instanceId": "some_Instance"},
    # )

    provider = AWSProvider()
    # provider.metadata_url = mocking_url
    assert provider.check_metadata_server() is False
