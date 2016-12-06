import json
import logging
import re

from watchmaker.exceptions import ExcLevel, wm_exit
from watchmaker.managers.base import LinuxManager

ylog = logging.getLogger('Yum')


class Yum(LinuxManager):
    """
    Handles linux distro validation and repo installation.
    """

    def __init__(self):
        """
        Instatiates the class.
        """
        super(Yum, self).__init__()
        self.dist = None
        self.version = None
        self.epel_version = None

    def _validate(self):
        """
        Validates the linux distrbution uses yum and is configurable.
        """
        self.dist = None
        self.version = None
        self.epel_version = None

        supported_dists = ('amazon', 'centos', 'red hat')

        match_supported_dist = re.compile(r"^({0})"
                                          "(?:[^0-9]+)"
                                          "([\d]+[.][\d]+)"
                                          "(?:.*)"
                                          .format('|'.join(supported_dists)))
        amazon_epel_versions = {
            '2014.03': '6',
            '2014.09': '6',
            '2015.03': '6',
            '2015.09': '6',
        }

        # Read first line from /etc/system-release
        try:
            with open(name='/etc/system-release', mode='rb') as f:
                release = f.readline().strip()
        except Exception as exc:
            raise SystemError('Could not read /etc/system-release. '
                              'Error: {0}'.format(exc))

        # Search the release file for a match against _supported_dists
        matched = match_supported_dist.search(release.lower())
        if matched is None:
            # Release not supported, exit with error
            raise SystemError(
                'Unsupported OS distribution. OS must be one of: {0}'
                .format(', '.join(supported_dists))
            )

        # Assign dist,version from the match groups tuple, removing any spaces
        self.dist, self.version = (
            x.translate(None, ' ') for x in matched.groups()
        )

        # Determine epel_version
        if 'amazon' == self.dist:
            self.epel_version = amazon_epel_versions.get(self.version, None)
        else:
            self.epel_version = self.version.split('.')[0]

        if self.epel_version is None:
            raise SystemError(
                'Unsupported OS version! dist = {0}, version = {1}.'
                .format(self.dist, self.version)
            )

        ylog.debug('Dist\t\t{0}'.format(self.dist))
        ylog.debug('Version\t\t{0}'.format(self.version))
        ylog.debug('EPEL Version\t{0}'.format(self.epel_version))

    def _repo(self, config):
        """
        Private method that validates that the config is properly formed.
        """
        if not isinstance(config['yumrepomap'], list):
            msg = '`yumrepomap` must be a list!'
            ylog.error(msg, Exception(msg))

    def install(self, configuration):
        """
        Checks the distribution version and installs yum repo definition files
        that are specific to that distribution.

        Args:
            configuration (JSON):
                The configuration data required to install the yum repos.
        """
        try:
            config = json.loads(configuration)
        except ValueError:
            wm_exit(
                'The configuration passed was not properly formed JSON.'
                'Execution halted.', ExcLevel.Critical, True
            )

        if 'yumrepomap' in config and config['yumrepomap']:
            self._repo(config)
        else:
            ylog.info('yumrepomap did not exist or was empty.')

        self._validate()

        # TODO This block is weird.  Correct and done.
        for repo in config['yumrepomap']:

            if repo['dist'] in [self.dist, 'all']:
                ylog.debug(
                    '{0} in {1} or all'.format(repo['dist'], self.dist)
                )
                if 'epel_version' in repo and \
                        str(repo['epel_version']) != str(self.epel_version):
                    ylog.debug(
                        'Skipping repo - epel_version ({0}) is not valid for '
                        'this repo ({1}).'
                        .format(self.epel_version, repo['url'])
                    )
                else:
                    ylog.info(
                        'All requirements have been validated for repo - {0}.'
                        .format(self.epel_version, repo['url'])
                    )
                    # Download the yum repo definition to /etc/yum.repos.d/
                    url = repo['url']
                    repofile = '/etc/yum.repos.d/{0}'.format(
                        url.split('/')[-1])
                    self.download_file(url, repofile)
            else:
                ylog.debug(
                    '{0} NOT in {1} or all'.format(repo['dist'], self.dist)
                )
