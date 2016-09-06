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

mlog = logging.getLogger('ManagerBase')
lmlog = logging.getLogger('LinuxManager')


class ManagerBase(object):
    """
    Base class for operating system managers.

    Forces all child classes to require consistent methods for coherence.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self):
        return

    def _get_s3_file(self, url, bucket_name, key_name, destination):
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
            mlog.critical(exc)
            sys.exit(1)

        try:
            s3 = boto3.resource("s3")
            s3.meta.client.head_bucket(Bucket=bucket_name)
            s3.Object(bucket_name, key_name).download_file(destination)
        except ClientError as exc:
            msg = ('Bucket does not exist.  bucket = {0}.  Exception: {1}'
                   .format(bucket_name, exc))
            mlog.error(msg)
            raise SystemError(msg)
        except Exception as exc:
            msg = ('Unable to download file from S3 bucket.  url = {0}.  '
                   'bucket = {1}.  key = {2}.  file = {3}.  Exception: {4}'
                   .format(url, bucket_name, key_name, destination, exc))
            mlog.error(msg)
            raise SystemError(msg)

    @abc.abstractmethod
    def download_file(self, url, filename, sourceiss3bucket):
        """
        :param url:
        :param filename:
        :param sourceiss3bucket:
        :return:
        """
        mlog.debug('Downloading: {0}'.format(url))
        mlog.debug('Destination: {0}'.format(filename))
        mlog.debug('S3: {0}'.format(sourceiss3bucket))

        # TODO Rework this to properly reflect logic flow cleanly.
        if sourceiss3bucket:
            try:
                import boto3
                from botocore.client import ClientError
            except ImportError as exc:
                mlog.critical(exc)
                sys.exit(1)

            bucket_name = url.split('/')[3]
            key_name = '/'.join(url.split('/')[4:])

            mlog.debug('Bucket Name: {0}'.format(bucket_name))
            mlog.debug('key_name: {0}'.format(key_name))

            try:
                s3 = boto3.resource('s3')
                s3.meta.client.head_bucket(Bucket=bucket_name)
                s3.Object(bucket_name, key_name).download_file(filename)
            except (NameError, ClientError):
                mlog.error('NameError: {0}'.format(ClientError))
                try:
                    bucket_name = url.split('/')[2].split('.')[0]
                    key_name = '/'.join(url.split('/')[3:])
                    s3 = boto3.resource("s3")
                    s3.meta.client.head_bucket(Bucket=bucket_name)
                    s3.Object(bucket_name, key_name).download_file(filename)
                except Exception as exc:
                    msg = ('Unable to download file from S3 bucket.  '
                           'url = {0}.  bucket = {1}.  key = {2}.  '
                           'file = {3}.  Exception: {4}'
                           .format(url, bucket_name, key_name, filename, exc))
                    mlog.error(msg)
                    raise SystemError(msg)
            except Exception as exc:
                msg = ('Unable to download file from S3 bucket.  url = {0}.  '
                       'bucket = {1}.  key = {2}.  file = {3}.  Exception: {4}'
                       .format(url, bucket_name, key_name, filename, exc))
                mlog.error(msg)
                raise SystemError(msg)
            mlog.info(
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
                mlog.error(msg)
                raise SystemError(msg)
            mlog.info(
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
        mlog.info('Creating a working directory.')
        workingdir = None
        original_umask = os.umask(0)
        try:
            workingdir = tempfile.mkdtemp(prefix=prefix, dir=basedir)
        except Exception as exc:
            mlog.critical(
                'Could not create workingdir in {0}.  Exception: {1}'
                .format(basedir, exc)
            )
            sys.exit(1)
        mlog.debug('Working directory: {0}'.format(workingdir))
        self.workingdir = workingdir
        os.umask(original_umask)

    @abc.abstractmethod
    def call_process(self, cmd):
        if not isinstance(cmd, list):
            mlog.critical('Command is not a list: {0}'.format(str(cmd)))
            sys.exit(1)
        rsp = subprocess.call(cmd)

        if rsp != 0:
            mlog.critical('Command failed: {0}'.format(str(cmd)))
            sys.exit(1)

    @abc.abstractmethod
    def cleanup(self):
        """

        :return:
        """
        mlog.info('Cleanup Time...')
        try:
            mlog.debug('{0} being cleaned up.'.format(self.workingdir))
            shutil.rmtree(self.workingdir)
        except Exception as exc:
            mlog.critical('Cleanup Failed!  Exception: {0}'.format(exc))
            sys.exit(1)

        mlog.info(
            'Removed temporary data in working directory -- {0}'
            .format(self.workingdir)
        )
        mlog.info('Exiting cleanup routine...')

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
            mlog.debug('File Type: zip')
            opener, mode = zipfile.ZipFile, 'r'
        elif filepath.endswith('.tar.gz') or filepath.endswith('.tgz'):
            mlog.debug('File Type: GZip Tar')
            opener, mode = tarfile.open, 'r:gz'
        elif filepath.endswith('.tar.bz2') or filepath.endswith('.tbz'):
            mlog.debug('File Type: Bzip Tar')
            opener, mode = tarfile.open, 'r:bz2'
        else:
            mlog.critical(
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

        mlog.info(
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
        lmlog.debug(packages)
        lmlog.debug('Return code of yum install: {0}'.format(rsp))

        if rsp != 0:
            lmlog.critical('Installing Salt from Yum has failed!')
            sys.exit(1)

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
