import abc
import logging
import os
import shutil
import subprocess
import tarfile
import tempfile
import zipfile

import boto3
from botocore.client import ClientError
from six.moves import urllib

from watchmaker.exceptions import SystemFatal as exceptionhandler


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
            s3 = boto3.resource("s3")
            s3.meta.client.head_bucket(Bucket=bucket_name)
            s3.Object(bucket_name, key_name).download_file(destination)
        except ClientError as exc:
            logging.error('Bucket does not exist.\n'
                          'bucket = {0}\n'
                          'Exception: {1}'
                          .format(bucket_name, exc))
            raise SystemError('Bucket does not exist.\n'
                              'bucket = {0}\n'
                              'Exception: {1}'
                              .format(bucket_name, exc))
        except Exception as exc:
            logging.error('Unable to download file from S3 bucket.\n'
                          'url = {0}\n'
                          'bucket = {1}\n'
                          'key = {2}\n'
                          'file = {3}\n'
                          'Exception: {4}'
                          .format(url, bucket_name, key_name,
                                  destination, exc))
            raise SystemError('Unable to download file from S3 bucket.\n'
                              'url = {0}\n'
                              'bucket = {1}\n'
                              'key = {2}\n'
                              'file = {3}\n'
                              'Exception: {4}'
                              .format(url, bucket_name, key_name,
                                      destination, exc))

    @abc.abstractmethod
    def download_file(self, url, filename, sourceiss3bucket):
        """

        :param url:
        :param filename:
        :param sourceiss3bucket:
        :return:
        """

        return

    @abc.abstractmethod
    def create_working_dir(self, basedir, prefix):
        """

        :param basedir:
        :param prefix:
        :return:
        """

        return

    @abc.abstractmethod
    def call_process(self, cmd):
        return

    @abc.abstractmethod
    def cleanup(self):
        """

        :return:
        """

        return

    @abc.abstractmethod
    def extract_contents(self, filepath, to_directory, create_dir):
        """

        :param filepath:
        :param to_directory:
        :param create_dir:
        :return:
        """

        return


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
        logging.debug(packages)
        logging.debug('Return code of yum install: {0}'.format(rsp))

        if rsp != 0:
            exceptionhandler('Installing Salt from Yum has failed!')

    def download_file(self, url, filename, sourceiss3bucket=False):
        """

        :param url:
        :param filename:
        :param sourceiss3bucket:
        :return:
        """

        logging.debug('Downloading: {0}'.format(url))
        logging.debug('Destination: {0}'.format(filename))
        logging.debug('S3: {0}'.format(sourceiss3bucket))

        # TODO Rework this to properly reflect logic flow cleanly.
        if sourceiss3bucket:
            bucket_name = url.split('/')[3]
            key_name = '/'.join(url.split('/')[4:])

            logging.debug('Bucket Name: {0}'.format(bucket_name))
            logging.debug('key_name: {0}'.format(key_name))

            try:
                s3 = boto3.resource("s3")
                s3.meta.client.head_bucket(Bucket=bucket_name)
                s3.Object(bucket_name, key_name).download_file(filename)
            except (NameError, ClientError):
                logging.error('NameError: {0}'.format(ClientError))
                try:
                    bucket_name = url.split('/')[2].split('.')[0]
                    key_name = '/'.join(url.split('/')[3:])
                    s3 = boto3.resource("s3")
                    s3.meta.client.head_bucket(Bucket=bucket_name)
                    s3.Object(bucket_name, key_name).download_file(filename)
                except Exception as exc:
                    logging.error(
                        'Unable to download file from S3 bucket.\n'
                        'url = {0}\n'
                        'bucket = {1}\n'
                        'key = {2}\n'
                        'file = {3}\n'
                        'Exception: {4}'
                        .format(url, bucket_name, key_name, filename, exc)
                    )
                    raise SystemError(
                        'Unable to download file from S3 bucket.\n'
                        'url = {0}\n'
                        'bucket = {1}\n'
                        'key = {2}\n'
                        'file = {3}\n'
                        'Exception: {4}'
                        .format(url, bucket_name, key_name, filename, exc)
                    )
            except Exception as exc:
                logging.error(
                    'Unable to download file from S3 bucket.\n'
                    'url = {0}\n'
                    'bucket = {1}\n'
                    'key = {2}\n'
                    'file = {3}\n'
                    'Exception: {4}'
                    .format(url, bucket_name, key_name, filename, exc)
                )
                raise SystemError(
                    'Unable to download file from S3 bucket.\n'
                    'url = {0}\n'
                    'bucket = {1}\n'
                    'key = {2}\n'
                    'file = {3}\n'
                    'Exception: {4}'
                    .format(url, bucket_name, key_name, filename, exc))
            logging.debug('Downloaded file from S3 bucket -- \n'
                          '    url      = {0}\n'
                          '    filename = {1}'.format(url, filename))
        else:
            try:
                response = urllib.request.urlopen(url)
                with open(filename, 'wb') as outfile:
                    shutil.copyfileobj(response, outfile)
            except Exception as exc:
                # TODO: Update `except` logic
                logging.error('Unable to download file from web server.\n'
                              'url = {0}\n'
                              'filename = {1}\n'
                              'Exception: {2}'
                              .format(url, filename, exc))
                raise SystemError('Unable to download file from web server.\n'
                                  'url = {0}\n'
                                  'filename = {1}\n'
                                  'Exception: {2}'
                                  .format(url, filename, exc))
            logging.debug('Downloaded file from web server -- \n'
                          '    url      = {0}\n'
                          '    filename = {1}'.format(url, filename))

    def call_process(self, cmd):
        if not isinstance(cmd, list):
            exceptionhandler('Command is not a list.\n{0}'.format(str(cmd)))
        rsp = subprocess.call(cmd)

        if rsp != 0:
            exceptionhandler('Command failed.\n{0}'.format(str(cmd)))

    def create_working_dir(self, basedir, prefix):
        """
        Create a directory in `basedir` with a prefix of `prefix`.

        Args:
            prefix (str):
                Prefix to prepend to the working directory
            basedir (str):
                The directory in which to create the working directory
        """
        logging.info('Creating a working directory.')
        workingdir = None
        original_umask = os.umask(0)
        try:
            workingdir = tempfile.mkdtemp(prefix=prefix, dir=basedir)
        except Exception as exc:
            exceptionhandler('Could not create workingdir in {0}.\n'
                             'Exception: {1}'.format(basedir, exc))
        logging.debug('Working directory: {0}'.format(workingdir))
        self.workingdir = workingdir
        os.umask(original_umask)

    def cleanup(self):
        """
        Removes temporary files loaded to the system.
            :return: bool
        """
        logging.info('+-' * 40)
        logging.info('Cleanup Time...')
        try:
            logging.debug('{0} being cleaned up.'.format(self.workingdir))
            shutil.rmtree(self.workingdir)
        except Exception as exc:
            # TODO: Update `except` logic
            logging.fatal('Cleanup Failed!\nException: {0}'.format(exc))
            exceptionhandler('Cleanup Failed.\nAborting.')

        logging.info('Removed temporary data in working directory -- {0}'
                     .format(self.workingdir))
        logging.info('Exiting cleanup routine...')
        logging.info('-+' * 40)

    def extract_contents(self, filepath, to_directory='.', create_dir=None):
        """
        Extracts a compressed file to the specified directory.
        Supports files that end in .zip, .tar.gz, .tgz, tar.bz2, or tbz.
        :param create_dir:
        :param filepath: str, path to the compressed file
        :param to_directory: str, path to the target directory
        :raise ValueError: error raised if file extension is not supported
        """
        opener = None
        mode = None

        if filepath.endswith('.zip'):
            logging.debug('File Type: zip')
            opener, mode = zipfile.ZipFile, 'r'
        elif filepath.endswith('.tar.gz') or filepath.endswith('.tgz'):
            logging.debug('File Type: GZip Tar')
            opener, mode = tarfile.open, 'r:gz'
        elif filepath.endswith('.tar.bz2') or filepath.endswith('.tbz'):
            logging.debug('File Type: Bzip Tar')
            opener, mode = tarfile.open, 'r:bz2'
        else:
            exceptionhandler('Could not extract "{0}" as no appropriate '
                             'extractor is found'.format(filepath))

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


class WindowsManager(ManagerBase):
    """

    """

    def __init__(self):
        super(WindowsManager, self).__init__()
        self.workingdir = None

    def download_file(self, url, filename, sourceiss3bucket):
        pass

    def call_process(self, cmd):
        pass

    def create_working_dir(self, basedir, prefix):
        """
        Create a directory in `basedir` with a prefix of `prefix`.

        Args:
            prefix (str):
                Prefix to prepend to the working directory
            basedir (str):
                The directory in which to create the working directory
        """
        logging.info('Creating a working directory.')
        workingdir = None
        original_umask = os.umask(0)
        try:
            workingdir = tempfile.mkdtemp(prefix=prefix, dir=basedir)
        except Exception as exc:
            exceptionhandler('Could not create workingdir in {0}.\n'
                             'Exception: {1}'.format(basedir, exc))
        logging.debug('Working directory: {0}'.format(workingdir))
        self.workingdir = workingdir
        os.umask(original_umask)

    def cleanup(self):
        pass

    def extract_contents(self, filepath, to_directory, create_dir):
        pass


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
