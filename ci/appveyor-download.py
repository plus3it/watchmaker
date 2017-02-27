#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Use the AppVeyor API to download Windows artifacts.

Taken from: <https://bitbucket.org/ned/coveragepy/src/tip/ci/download_appveyor.py>  # noqa: E501
# Licensed under the Apache License: <http://www.apache.org/licenses/LICENSE-2.0>  # noqa: E501
# For details: <https://bitbucket.org/ned/coveragepy/src/default/NOTICE.txt>
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import argparse
import logging
import os
import zipfile

import requests

logformat = '[%(name)s]: %(message)s'
logging.basicConfig(format=logformat, level=logging.INFO)
log = logging.getLogger('appveyor-download')


def make_auth_headers():
    """Make the authentication headers needed to use the Appveyor API."""
    path = os.path.expanduser("~/.appveyor.token")
    if not os.path.exists(path):
        raise RuntimeError(
            "Please create a file named `.appveyor.token` in your home "
            "directory. You can get the token from "
            "<https://ci.appveyor.com/api-token>"
        )
    with open(path) as f:
        token = f.read().strip()

    headers = {
        'Authorization': 'Bearer {}'.format(token),
    }
    return headers


def download_latest_artifacts(account_project, build_id):
    """Download all the artifacts from the latest build."""
    appveyor_projects = "https://ci.appveyor.com/api/projects"
    appveyor_builds = "https://ci.appveyor.com/api/buildjobs"
    if build_id is None:
        url = "{}/{}".format(appveyor_projects, account_project)
    else:
        url = "{}/{}/build/{}".format(
            appveyor_projects,
            account_project,
            build_id)
    build = requests.get(url, headers=make_auth_headers()).json()
    jobs = build['build']['jobs']
    log.info(
        "Build %s, %s jobs: %s",
        build['build']['version'], len(jobs), build['build']['message']
    )

    for job in jobs:
        name = job['name']
        log.info(
            "  %s: %s, %s artifacts",
            name, job['status'], job['artifactsCount']
        )

        url = "{}/{}/artifacts".format(appveyor_builds, job['jobId'])
        response = requests.get(url, headers=make_auth_headers())
        artifacts = response.json()

        for artifact in artifacts:
            is_zip = artifact['type'] == "Zip"
            filename = artifact['fileName']
            log.info("    %s, %s bytes", filename, artifact['size'])

            url = "{}/{}/artifacts/{}".format(
                appveyor_builds,
                job['jobId'],
                filename)
            download_url(url, filename, make_auth_headers())

            if is_zip:
                unpack_zipfile(filename)
                os.remove(filename)


def ensure_dirs(filename):
    """Make sure the directories exist for `filename`."""
    dirname, _ = os.path.split(filename)
    if dirname and not os.path.exists(dirname):
        os.makedirs(dirname)


def download_url(url, filename, headers):
    """Download a file from `url` to `filename`."""
    ensure_dirs(filename)
    response = requests.get(url, headers=headers, stream=True)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(16 * 1024):
                f.write(chunk)
    else:
        log.info("    Error downloading %s: %s", url, response)


def unpack_zipfile(filename):
    """Unpack a zipfile, using the names in the zip."""
    with open(filename, 'rb') as fzip:
        z = zipfile.ZipFile(fzip)
        for name in z.namelist():
            log.info("      extracting %s", name)
            ensure_dirs(name)
            z.extract(name)

parser = argparse.ArgumentParser(  # noqa: E305
    description='Download artifacts from AppVeyor.')
parser.add_argument('--id',
                    metavar='PROJECT_ID',
                    default='lorengordon/pyro',
                    help='Project ID in AppVeyor.')
parser.add_argument('build',
                    nargs='?',
                    metavar='BUILD_ID',
                    help='Build ID in AppVeyor. Eg: master-123')

if __name__ == "__main__":
    # import logging
    # logging.basicConfig(level="DEBUG")
    args = parser.parse_args()
    download_latest_artifacts(args.id, args.build)
