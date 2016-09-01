import abc
import os
import shutil
import subprocess
import tarfile
import tempfile
import zipfile

from six.moves import urllib
from watchmaker.logger import LogHandler as log


class ManagerBase(object):
    """
    Base class for operating system managers.

    Forces all child classes to require consistent methods for coherence.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self):
        return

    @staticmethod
    def _get_s3_file(url, bucket_name, key_name, destination):
        """
        :param url:
        :param bucket_name:
        :param key_name:
        :param destination:
        :return:
        """

        try:
            import boto3
            from botocore.client import ClientError
        except ImportError as exc:
            log(exc, log_type='critical')

        try:
            s3 = boto3.resource("s3")
            s3.meta.client.head_bucket(Bucket=bucket_name)
            s3.Object(bucket_name, key_name).download_file(destination)
        except ClientError as exc:
            log(
                'Bucket does not exist.  bucket = {0}.  Exception: {1}'
                .format(bucket_name, exc),
                log_type='error', exc=exc
            )
        except Exception as exc:
            log(
                'Unable to download file from S3 bucket.  url = {0}.  '
                'bucket = {1}.  key = {2}.  file = {3}.  Exception: {4}'
                .format(url, bucket_name, key_name, destination, exc),
                log_type='error', exc=exc
            )

    @abc.abstractmethod
    def download_file(self, url, filename, sourceiss3bucket):
        """
        :param url:
        :param filename:
        :param sourceiss3bucket:
        :return:
        """
        log('Downloading: {0}'.format(url), log_type='debug')
        log('Destination: {0}'.format(filename), log_type='debug')
        log('S3: {0}'.format(sourceiss3bucket), log_type='debug')

        # TODO Rework this to properly reflect logic flow cleanly.
        if sourceiss3bucket:
            try:
                import boto3
                from botocore.client import ClientError
            except ImportError as exc:
                log(exc, log_type='critical')

            bucket_name = url.split('/')[3]
            key_name = '/'.join(url.split('/')[4:])

            log('Bucket Name: {0}'.format(bucket_name), log_type='debug')
            log('key_name: {0}'.format(key_name), log_type='debug')

            try:
                s3 = boto3.resource('s3')
                s3.meta.client.head_bucket(Bucket=bucket_name)
                s3.Object(bucket_name, key_name).download_file(filename)
            except (NameError, ClientError):
                log('NameError: {0}'.format(ClientError), log_type='error')
                try:
                    bucket_name = url.split('/')[2].split('.')[0]
                    key_name = '/'.join(url.split('/')[3:])
                    s3 = boto3.resource("s3")
                    s3.meta.client.head_bucket(Bucket=bucket_name)
                    s3.Object(bucket_name, key_name).download_file(filename)
                except Exception as exc:
                    log(
                        'Unable to download file from S3 bucket.  url = {0}.  '
                        'bucket = {1}.  key = {2}.  file = {3}.  '
                        'Exception: {4}'
                        .format(url, bucket_name, key_name, filename, exc),
                        log_type='error', exc=exc
                    )
            except Exception as exc:
                log(
                    'Unable to download file from S3 bucket.  url = {0}.  '
                    'bucket = {1}.  key = {2}.  file = {3}.  Exception: {4}'
                    .format(url, bucket_name, key_name, filename, exc),
                    log_type='error', exc=exc
                )
            log(
                'Downloaded file from S3 bucket  --  url = {0}.  '
                'filename = {1}'.format(url, filename)
            )
        else:
            try:
                response = urllib.request.urlopen(url)
                with open(filename, 'wb') as outfile:
                    shutil.copyfileobj(response, outfile)
            except Exception as exc:
                # TODO: Update `except` logic
                log(
                    'Unable to download file from web server.  url = {0}.  '
                    'filename = {1}.  Exception: {2}'
                    .format(url, filename, exc),
                    log_type='error', exc=exc
                )
            log(
                'Downloaded file from web server  --  url = {0}.  '
                'filename = {1}'.format(url, filename)
            )

    @abc.abstractmethod
    def create_working_dir(self, basedir, prefix):
        """

        :param basedir:
        :param prefix:
        :return:
        """
        log('Creating a working directory.')
        workingdir = None
        original_umask = os.umask(0)
        try:
            workingdir = tempfile.mkdtemp(prefix=prefix, dir=basedir)
        except Exception as exc:
            log(
                'Could not create workingdir in {0}.  Exception: {1}'
                .format(basedir, exc), log_type='critical'
            )
        log(
            'Working directory: {0}'.format(workingdir), log_type='debug'
        )
        self.workingdir = workingdir
        os.umask(original_umask)

    @abc.abstractmethod
    def call_process(self, cmd):
        if not isinstance(cmd, list):
            log(
                'Command is not a list: {0}'.format(str(cmd)),
                log_type='critical'
            )
        rsp = subprocess.call(cmd)

        if rsp != 0:
            log('Command failed: {0}'.format(str(cmd)), log_type='critical')

    @abc.abstractmethod
    def cleanup(self):
        """

        :return:
        """
        log('Cleanup Time...')
        try:
            log(
                '{0} being cleaned up.'.format(self.workingdir),
                log_type='debug'
            )
            shutil.rmtree(self.workingdir)
        except Exception as exc:
            # TODO: Update `except` logic
            log(
                'Cleanup Failed!  Exception: {0}'.format(exc),
                log_type='critical'
            )

        log(
            'Removed temporary data in working directory -- {0}'
            .format(self.workingdir)
        )
        log('Exiting cleanup routine...')

    @abc.abstractmethod
    def extract_contents(self, filepath, to_directory, create_dir):
        """

        :param filepath:
        :param to_directory:
        :param create_dir:
        :return:
        """
        opener = None
        mode = None

        if filepath.endswith('.zip'):
            log('File Type: zip', log_type='debug')
            opener, mode = zipfile.ZipFile, 'r'
        elif filepath.endswith('.tar.gz') or filepath.endswith('.tgz'):
            log('File Type: GZip Tar', log_type='debug')
            opener, mode = tarfile.open, 'r:gz'
        elif filepath.endswith('.tar.bz2') or filepath.endswith('.tbz'):
            log('File Type: Bzip Tar', log_type='debug')
            opener, mode = tarfile.open, 'r:bz2'
        else:
            log(
                'Could not extract "{0}" as no appropriate extractor '
                'is found.'.format(filepath), log_type='critical'
            )

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

        print('Extracted file -- \n'
              '    source = {0}\n'
              '    dest   = {1}'.format(filepath, to_directory))


class LinuxManager(ManagerBase):
    """
    Base class for Linux Managers.

    Serves as a foundational class to keep OS consitency.
    """

    def __init__(self):
        super(LinuxManager, self).__init__()
        self.workingdir = None

    def _install_from_yum(self, packages):
        """

        :param packages:
        :return:
        """

        yum_cmd = ['sudo', 'yum', '-y', 'install']
        if isinstance(packages, list):
            yum_cmd.extend(packages)
        else:
            yum_cmd.append(packages)
        rsp = subprocess.call(yum_cmd)
        log(packages, log_type='debug')
        log('Return code of yum install: {0}'.format(rsp), log_type='debug')

        if rsp != 0:
            log('Installing Salt from Yum has failed!', log_type='critical')

    def download_file(self, url, filename, sourceiss3bucket=False):
        """

        :param url:
        :param filename:
        :param sourceiss3bucket:
        :return:
        """
        super(LinuxManager, self).download_file(
            url,
            filename,
            sourceiss3bucket
        )

    def call_process(self, cmd):
        super(LinuxManager, self).call_process(cmd)

    def create_working_dir(self, basedir, prefix):
        """
        Create a directory in `basedir` with a prefix of `prefix`.

        Args:
            prefix (str):
                Prefix to prepend to the working directory
            basedir (str):
                The directory in which to create the working directory
        """
        super(LinuxManager, self).create_working_dir(basedir, prefix)

    def cleanup(self):
        """
        Removes temporary files loaded to the system.
            :return: bool
        """
        super(LinuxManager, self).cleanup()

    def extract_contents(self, filepath, to_directory='.', create_dir=None):
        """
        Extracts a compressed file to the specified directory.
        Supports files that end in .zip, .tar.gz, .tgz, tar.bz2, or tbz.
        :param create_dir:
        :param filepath: str, path to the compressed file
        :param to_directory: str, path to the target directory
        :raise ValueError: error raised if file extension is not supported
        """
        super(LinuxManager, self).extract_contents(
            filepath,
            to_directory,
            create_dir
        )


class WindowsManager(ManagerBase):
    """

    """

    def __init__(self):
        super(WindowsManager, self).__init__()
        self.workingdir = None

    def download_file(self, url, filename, sourceiss3bucket=False):
        """

        :param url:
        :param filename:
        :param sourceiss3bucket:
        :return:
        """
        super(WindowsManager, self).download_file(
            url,
            filename,
            sourceiss3bucket
        )

    def call_process(self, cmd):
        super(WindowsManager, self).call_process(cmd)

    def create_working_dir(self, basedir, prefix):
        """
        Create a directory in `basedir` with a prefix of `prefix`.

        Args:
            prefix (str):
                Prefix to prepend to the working directory
            basedir (str):
                The directory in which to create the working directory
        """
        super(WindowsManager, self).create_working_dir(basedir, prefix)

    def cleanup(self):
        """
        Removes temporary files loaded to the system.
            :return: bool
        """
        super(WindowsManager, self).cleanup()

    def extract_contents(self, filepath, to_directory='.', create_dir=None):
        """
        Extracts a compressed file to the specified directory.
        Supports files that end in .zip, .tar.gz, .tgz, tar.bz2, or tbz.
        :param create_dir:
        :param filepath: str, path to the compressed file
        :param to_directory: str, path to the target directory
        :raise ValueError: error raised if file extension is not supported
        """
        super(WindowsManager, self).extract_contents(
            filepath,
            to_directory,
            create_dir
        )


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
