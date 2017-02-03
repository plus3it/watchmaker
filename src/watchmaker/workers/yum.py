# -*- coding: utf-8 -*-
"""Watchmaker yum worker."""
import json
import re

from watchmaker.exceptions import WatchmakerException
from watchmaker.managers.base import LinuxManager


class Yum(LinuxManager):
    """Install yum repos."""

    SUPPORTED_DISTS = ('amazon', 'centos', 'red hat')

    # Pattern used to match against the first line of /etc/system-release. A
    # match will contain two groups: the dist name (e.g. 'red hat' or 'amazon')
    # and the dist version (e.g. '6.8' or '2016.09').
    DIST_PATTERN = re.compile(
        r"^({0})"
        "(?:[^0-9]+)"
        "([\d]+[.][\d]+)"
        "(?:.*)"
        .format('|'.join(SUPPORTED_DISTS))
    )

    def __init__(self):  # noqa: D102
        super(Yum, self).__init__()
        self.dist_info = self.get_dist_info()

    @staticmethod
    def _get_amazon_el_version(version):
        # All amzn linux distros currently available use el6-based packages.
        # When/if amzn linux switches a distro to el7, rethink this.
        return '6'

    def get_dist_info(self):
        """Validate the Linux distro and return info about the distribution."""
        dist = None
        version = None
        el_version = None

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
        matched = self.DIST_PATTERN.search(release.lower())
        if matched is None:
            # Release not supported, exit with error
            msg = (
                'Unsupported OS distribution. OS must be one of: {0}'
                .format(', '.join(self.SUPPORTED_DISTS))
            )
            self.log.critical(msg)
            raise WatchmakerException(msg)

        # Assign dist,version from the match groups tuple, removing any spaces
        dist, version = (
            x.translate(None, ' ') for x in matched.groups()
        )

        # Determine el_version
        if dist == 'amazon':
            el_version = self._get_amazon_el_version(version)
        else:
            el_version = version.split('.')[0]

        if el_version is None:
            msg = (
                'Unsupported OS version! dist = {0}, version = {1}.'
                .format(dist, version)
            )
            self.log.critical(msg)
            raise WatchmakerException(msg)

        dist_info = {
            'dist': dist,
            'el_version': el_version
        }
        self.log.debug('dist_info = {0}'.format(dist_info))
        return dist_info

    def _validate_config(self, configuration):
        """Validate the config is properly formed."""
        config = {}
        try:
            config = json.loads(configuration)
        except ValueError:
            msg = (
                'The configuration passed was not properly formed JSON.'
                'Execution halted.'
            )
            self.log.critical(msg)
            raise

        if not ('yumrepomap' in config and config['yumrepomap']):
            self.log.warning('yumrepomap did not exist or was empty.')
        elif not isinstance(config['yumrepomap'], list):
            msg = '`yumrepomap` must be a list!'
            self.log.critical(msg)
            raise WatchmakerException(msg)

        return config

    def install(self, configuration):
        """
        Install yum repos defined in config file.

        Args:
            configuration (:obj:`json`):
                The configuration data required to install the yum repos.
        """
        dist = self.dist_info['dist']
        el_version = self.dist_info['el_version']

        config = self._validate_config(configuration)

        # TODO This block is weird.  Correct and done.
        for repo in config.get('yumrepomap', []):
            if repo['dist'] in [dist, 'all']:
                self.log.debug(
                    '{0} in {1} or all'.format(repo['dist'], dist)
                )
                if 'el_version' in repo and \
                        str(repo['el_version']) != str(el_version):
                    self.log.debug(
                        'Skipping repo - el_version ({0}) is not valid for '
                        'this repo ({1}).'
                        .format(el_version, repo['url'])
                    )
                else:
                    self.log.info(
                        'All requirements have been validated for repo - {0}.'
                        .format(el_version, repo['url'])
                    )
                    # Download the yum repo definition to /etc/yum.repos.d/
                    url = repo['url']
                    repofile = '/etc/yum.repos.d/{0}'.format(
                        url.split('/')[-1])
                    self.download_file(url, repofile)
            else:
                self.log.debug(
                    '{0} NOT in {1} or all'.format(repo['dist'], dist)
                )
