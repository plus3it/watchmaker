# -*- coding: utf-8 -*-
"""Watchmaker yum worker."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import io
import re

import distro
import six

import watchmaker.utils
from watchmaker.exceptions import WatchmakerError
from watchmaker.managers.platform import LinuxPlatformManager
from watchmaker.workers.base import WorkerBase


class Yum(WorkerBase, LinuxPlatformManager):
    """
    Install yum repos.

    Args:
        repo_map: (:obj:`list`)
            List of dictionaries containing a map of yum repo files to systems.
            (*Default*: ``[]``)

    """

    SUPPORTED_DISTS = ('amazon', 'centos', 'red hat', 'rhel')

    # Pattern used to match against the first line of /etc/system-release. A
    # match will contain two groups: the dist name (e.g. 'red hat' or 'amazon')
    # and the dist version (e.g. '6.8' or '2016.09').
    DIST_PATTERN = re.compile(
        r"^({0})"
        "(?:[^0-9]+)"
        r"([\d]|[\d]+[.][\d])"
        "(?:.*)"
        .format('|'.join(SUPPORTED_DISTS))
    )

    def __init__(self, *args, **kwargs):
        # Pop arguments used by Yum
        self.yumrepomap = kwargs.pop('repo_map', None) or []

        # Init inherited classes
        super(Yum, self).__init__(*args, **kwargs)
        self.dist_info = self.get_dist_info()

    def _get_amazon_el_version(self, version):
        # All amzn linux distros currently available use el6-based packages.
        # When/if amzn linux switches a distro to el7, rethink this.
        self.log.debug('Amazon Linux, version=%s', version)
        return '6'

    def get_dist_info(self):
        """Validate the Linux distro and return info about the distribution."""
        os_dist = dist.id()
        version = dist.version()[0]
        el_version = None

        # Determine el_version
        if os_dist == 'amazon':
            el_version = self._get_amazon_el_version(version)
        else:
            el_version = dist.version()[0]

        if el_version is None:
            msg = (
                'Unsupported OS version! dist = {0}, version = {1}.'
                .format(dist, version)
            )
            self.log.critical(msg)
            raise WatchmakerError(msg)

        dist_info = {
            'dist': os_dist,
            'el_version': el_version
        }
        self.log.debug('dist_info=%s', dist_info)
        return dist_info

    def _validate_config(self):
        """Validate the config is properly formed."""
        if not self.yumrepomap:
            self.log.warning('`yumrepomap` did not exist or was empty.')
        elif not isinstance(self.yumrepomap, list):
            msg = '`yumrepomap` must be a list!'
            self.log.critical(msg)
            raise WatchmakerError(msg)

    def _validate_repo(self, repo):
        """Check if a repo is applicable to this system."""
        # Check if this repo applies to this system's dist and el_version.
        # repo['dist'] must match this system's dist or the keyword 'all'
        # repo['el_version'] is optional, but if present then it must match
        # this system's el_version.
        dist = self.dist_info['dist']
        el_version = self.dist_info['el_version']

        repo_dists = repo['dist']
        if isinstance(repo_dists, six.string_types):
            # ensure repo_dist is a list
            repo_dists = [repo_dists]

        # is repo dist applicable to this system?
        check_dist = bool(set(repo_dists).intersection([dist, 'all']))

        # is repo el_version applicable to this system?
        check_el_version = (
            'el_version' in repo and
            str(repo['el_version']) == str(el_version)
        )

        # return True if all checks pass, otherwise False
        return check_dist and check_el_version

    def before_install(self):
        """Validate configuration before starting install."""
        pass

    def install(self):
        """Install yum repos defined in config file."""
        self._validate_config()

        for repo in self.yumrepomap:
            if self._validate_repo(repo):
                # Download the yum repo definition to /etc/yum.repos.d/
                self.log.info('Installing repo: %s', repo['url'])
                url = repo['url']
                repofile = '/etc/yum.repos.d/{0}'.format(
                    watchmaker.utils.basename_from_uri(url))
                self.retrieve_file(url, repofile)
            else:
                self.log.debug(
                    'Skipped repo because it is not valid for this system: '
                    'dist_info=%s',
                    self.dist_info
                )
                self.log.debug('Skipped repo=%s', repo)
