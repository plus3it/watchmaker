import abc
import logging
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile

from six.moves import urllib

m_log = logging.getLogger('ManagerBase')
lm_log = logging.getLogger('LinuxManager')


class ManagerBase(object):
    """
    Base class for operating system managers.

    All child classes will have access to methods unless overridden by
    similarly-named method in the child class.
    """
    boto3 = None
    boto_client = None

    def __init__(self):
        self.working_dir = None
        return

    def _import_boto3(self):
        if self.boto3:
            return

        m_log.info("Dynamically importing boto3 ...")
        try:
            self.boto3 = __import__("boto3")
            self.boto_client = __import__(
                "botocore.client",
                globals(),
                locals(),
                ["ClientError"],
                -1
            )
        except ImportError as exc:
            m_log.critical(exc)
            sys.exit(1)

    def _get_s3_file(self, url, bucket_name, key_name, destination):
        self._import_boto3()

        try:
            s3 = self.boto3.resource("s3")
            s3.meta.client.head_bucket(Bucket=bucket_name)
            s3.Object(bucket_name, key_name).download_file(destination)
        except self.boto_client.ClientError as exc:
            msg = ('Bucket does not exist.  bucket = {0}.  Exception: {1}'
                   .format(bucket_name, exc))
            m_log.error(msg)
            raise SystemError(msg)
        except Exception as exc:
            msg = ('Unable to download file from S3 bucket.  url = {0}.  '
                   'bucket = {1}.  key = {2}.  file = {3}.  Exception: {4}'
                   .format(url, bucket_name, key_name, destination, exc))
            m_log.error(msg)
            raise SystemError(msg)

    def download_file(self, url, filename, sourceiss3bucket=False):
        m_log.debug('Downloading: {0}'.format(url))
        m_log.debug('Destination: {0}'.format(filename))
        m_log.debug('S3: {0}'.format(sourceiss3bucket))

        # TODO Rework this to properly reflect logic flow cleanly.
        if sourceiss3bucket:
            self._import_boto3()

            bucket_name = url.split('/')[3]
            key_name = '/'.join(url.split('/')[4:])

            m_log.debug('Bucket Name: {0}'.format(bucket_name))
            m_log.debug('key_name: {0}'.format(key_name))

            try:
                s3 = self.boto3.resource('s3')
                s3.meta.client.head_bucket(Bucket=bucket_name)
                s3.Object(bucket_name, key_name).download_file(filename)
            except (NameError, self.boto_client.ClientError):
                m_log.error(
                    'NameError: {0}'.format(self.boto_client.ClientError)
                )
                try:
                    bucket_name = url.split('/')[2].split('.')[0]
                    key_name = '/'.join(url.split('/')[3:])
                    s3 = self.boto3.resource("s3")
                    s3.meta.client.head_bucket(Bucket=bucket_name)
                    s3.Object(bucket_name, key_name).download_file(filename)
                except Exception as exc:
                    msg = ('Unable to download file from S3 bucket.  '
                           'url = {0}.  bucket = {1}.  key = {2}.  '
                           'file = {3}.  Exception: {4}'
                           .format(url, bucket_name, key_name, filename, exc))
                    m_log.error(msg)
                    raise SystemError(msg)
            except Exception as exc:
                msg = ('Unable to download file from S3 bucket.  url = {0}.  '
                       'bucket = {1}.  key = {2}.  file = {3}.  Exception: {4}'
                       .format(url, bucket_name, key_name, filename, exc))
                m_log.error(msg)
                raise SystemError(msg)
            m_log.info(
                'Downloaded file from S3 bucket  --  url = {0}.  '
                'filename = {1}'.format(url, filename)
            )
        else:
            try:
                response = urllib.request.urlopen(url)
                with open(filename, 'wb') as outfile:
                    shutil.copyfileobj(response, outfile)
            except Exception as exc:
                msg = ('Unable to download file from web server.  url = {0}.  '
                       'filename = {1}.  Exception: {2}'
                       .format(url, filename, exc))
                m_log.error(msg)
                raise SystemError(msg)
            m_log.info(
                'Downloaded file from web server  --  url = {0}.  '
                'filename = {1}'.format(url, filename)
            )

    def create_working_dir(self, basedir, prefix):
        """
        Create a directory in `basedir` with a prefix of `prefix`.

        Args:
            prefix (str):
                Prefix to prepend to the working directory
            basedir (str):
                The directory in which to create the working directory
        """
        m_log.info('Creating a working directory.')
        original_umask = os.umask(0)
        try:
            working_dir = tempfile.mkdtemp(prefix=prefix, dir=basedir)
        except Exception as exc:
            m_log.critical(
                'Could not create a working dir in {0}.  Exception: {1}'
                .format(basedir, exc)
            )
            sys.exit(1)
        m_log.debug('Working directory: {0}'.format(working_dir))
        self.working_dir = working_dir
        os.umask(original_umask)

    @staticmethod
    def call_process(cmd):
        if not isinstance(cmd, list):
            m_log.critical('Command is not a list: {0}'.format(str(cmd)))
            sys.exit(1)
        rsp = subprocess.call(cmd)

        if rsp != 0:
            m_log.critical('Command failed: {0}'.format(str(cmd)))
            sys.exit(1)

    def cleanup(self):
        m_log.info('Cleanup Time...')
        try:
            m_log.debug('{0} being cleaned up.'.format(self.working_dir))
            shutil.rmtree(self.working_dir)
        except Exception as exc:
            m_log.critical('Cleanup Failed!  Exception: {0}'.format(exc))
            sys.exit(1)

        m_log.info(
            'Removed temporary data in working directory -- {0}'
            .format(self.working_dir)
        )
        m_log.info('Exiting cleanup routine...')

    @staticmethod
    def extract_contents(filepath, to_directory, create_dir=False):
        """
        Extracts a compressed file to the specified directory.
        Supports files that end in .zip, .tar.gz, .tgz, tar.bz2, or tbz.

        Args:
            filepath (str):
                Path to the compressed file
            to_directory (str):
                Path to the target directory
            create_dir (bool):
                If true, create subdirectory within to_directory
                that represents original path of compressed file
        """
        if filepath.endswith('.zip'):
            m_log.debug('File Type: zip')
            opener, mode = zipfile.ZipFile, 'r'
        elif filepath.endswith('.tar.gz') or filepath.endswith('.tgz'):
            m_log.debug('File Type: GZip Tar')
            opener, mode = tarfile.open, 'r:gz'
        elif filepath.endswith('.tar.bz2') or filepath.endswith('.tbz'):
            m_log.debug('File Type: Bzip Tar')
            opener, mode = tarfile.open, 'r:bz2'
        else:
            m_log.critical(
                'Could not extract "{0}" as no appropriate extractor '
                'is found.'.format(filepath)
            )
            sys.exit(1)

        if create_dir:
            to_directory = os.sep.join((
                to_directory,
                '.'.join(filepath.split(os.sep)[-1].split('.')[:-1])
            ))

        try:
            os.makedirs(to_directory)
        except OSError:
            if not os.path.isdir(to_directory):
                raise

        cwd = os.getcwd()
        os.chdir(to_directory)

        try:
            openfile = opener(filepath, mode)
            try:
                openfile.extractall()
            finally:
                openfile.close()
        finally:
            os.chdir(cwd)

        m_log.info(
            'Extracted file  --  source = {0}  dest   = {1}'
            .format(filepath, to_directory)
        )


class LinuxManager(ManagerBase):
    """
    Base class for Linux Managers.

    Serves as a foundational class to keep OS consitency.
    """

    def __init__(self):
        super(LinuxManager, self).__init__()

    @staticmethod
    def _install_from_yum(packages):
        yum_cmd = ['sudo', 'yum', '-y', 'install']
        if isinstance(packages, list):
            yum_cmd.extend(packages)
        else:
            yum_cmd.append(packages)
        rsp = subprocess.call(yum_cmd)
        lm_log.debug(packages)
        lm_log.debug('Return code of yum install: {0}'.format(rsp))

        if rsp != 0:
            lm_log.critical('Installing Salt from Yum has failed!')
            sys.exit(1)


class WindowsManager(ManagerBase):
    """

    """

    def __init__(self):
        super(WindowsManager, self).__init__()


class WorkersManagerBase(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def _worker_execution(self):
        return

    @abc.abstractmethod
    def _worker_validation(self):
        return

    @abc.abstractmethod
    def worker_cadence(self):
        return

    @abc.abstractmethod
    def cleanup(self):
        return
