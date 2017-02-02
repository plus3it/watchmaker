# -*- coding: utf-8 -*-
"""Watchmaker yum worker."""
import json
import re

from watchmaker.exceptions import WatchmakerException
from watchmaker.managers.base import LinuxManager


class Yum(LinuxManager):
    """Install yum repos."""

    def __init__(self):  # noqa: D102
        super(Yum, self).__init__()
        self.dist = None
        self.version = None
        self.epel_version = None

    @staticmethod
    def _get_amazon_epel_version(version):
        # All amzn linux distros currently available use el6-based packages.
        # When/if amzn linux switches a distro to el7, rethink this.
        return '6'

    def _validate(self):
        """Validate the Linux distro and set associated attributes."""
        self.dist = None
        self.version = None
        self.epel_version = None

        supported_dists = ('amazon', 'centos', 'red hat')

        match_supported_dist = re.compile(r"^({0})"
                                          "(?:[^0-9]+)"
                                          "([\d]+[.][\d]+)"
                                          "(?:.*)"
                                          .format('|'.join(supported_dists)))

        # Read first line from /etc/system-release
        try:
            with open(name='/etc/system-release', mode='rb') as f:
                release = f.readline().strip()
        except:
            self.log.critical(
                'Failed to read /etc/system-release. Cannot determine system '
                'distribution!'
            )
            raise

        # Search the release file for a match against _supported_dists
        matched = match_supported_dist.search(release.lower())
        if matched is None:
            # Release not supported, exit with error
            msg = (
                'Unsupported OS distribution. OS must be one of: {0}'
                .format(', '.join(supported_dists))
            )
            self.log.critical(msg)
            raise WatchmakerException(msg)

        # Assign dist,version from the match groups tuple, removing any spaces
        self.dist, self.version = (
            x.translate(None, ' ') for x in matched.groups()
        )

        # Determine epel_version
        if 'amazon' == self.dist:
            self.epel_version = self._get_amazon_epel_version(self.version)
        else:
            self.epel_version = self.version.split('.')[0]

        if self.epel_version is None:
            msg = (
                'Unsupported OS version! dist = {0}, version = {1}.'
                .format(self.dist, self.version)
            )
            self.log.critical(msg)
            raise WatchmakerException(msg)

        self.log.debug('Dist\t\t{0}'.format(self.dist))
        self.log.debug('Version\t\t{0}'.format(self.version))
        self.log.debug('EPEL Version\t{0}'.format(self.epel_version))

    def _repo(self, config):
        """Validate the ``yumrepomap`` is properly formed."""
        if not isinstance(config['yumrepomap'], list):
            msg = '`yumrepomap` must be a list!'
            self.log.critical(msg)
            raise WatchmakerException(msg)

    def install(self, configuration):
        """
        Install yum repos defined in config file.

        Args:
            configuration (:obj:`json`):
                The configuration data required to install the yum repos.
        """
        try:
            config = json.loads(configuration)
        except ValueError:
            msg = (
                'The configuration passed was not properly formed JSON.'
                'Execution halted.'
            )
            self.log.critical(msg)
            raise

        if 'yumrepomap' in config and config['yumrepomap']:
            self._repo(config)
        else:
            self.log.info('yumrepomap did not exist or was empty.')

        self._validate()

        # TODO This block is weird.  Correct and done.
        for repo in config['yumrepomap']:

            if repo['dist'] in [self.dist, 'all']:
                self.log.debug(
                    '{0} in {1} or all'.format(repo['dist'], self.dist)
                )
                if 'epel_version' in repo and \
                        str(repo['epel_version']) != str(self.epel_version):
                    self.log.debug(
                        'Skipping repo - epel_version ({0}) is not valid for '
                        'this repo ({1}).'
                        .format(self.epel_version, repo['url'])
                    )
                else:
                    self.log.info(
                        'All requirements have been validated for repo - {0}.'
                        .format(self.epel_version, repo['url'])
                    )
                    # Download the yum repo definition to /etc/yum.repos.d/
                    url = repo['url']
                    repofile = '/etc/yum.repos.d/{0}'.format(
                        url.split('/')[-1])
                    self.download_file(url, repofile)
            else:
                self.log.debug(
                    '{0} NOT in {1} or all'.format(repo['dist'], self.dist)
                )
