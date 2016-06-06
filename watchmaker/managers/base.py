import os
import abc
import boto
import shutil
import logging
import tarfile
import zipfile
import urllib2
import tempfile
import subprocess

from watchmaker.exceptions import SystemFatal as exceptionhandler


class ManagerBase(object):
    """
    Base class for operating system managers.  This forces all child classes to require consistent methods
    for coherence.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def _get_s3_file(self, url, bucket_name, key_name, destination):
        """


        :param url:
        :param bucket_name:
        :param key_name:
        :param destination:
        :return:
        """

        return

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
    This is the base import for Linux Managers.  It serves as a foundational class to keep OS consitency.

    """

    def __init__(self):
        self.workingdir = None

    def _get_s3_file(self, url, bucket_name, key_name, destination):

        try:
            conn = boto.connect_s3()
            bucket = conn.get_bucket(bucket_name)
            key = bucket.get_key(key_name)
            key.get_contents_to_filename(filename=destination)
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

    def _install_from_yum(self, packages):
        """

        :param packages:
        :return:
        """
        rsp = subprocess.call(['sudo','yum', '-y', 'install', ' '.join(packages)])
        logging.debug(packages)
        logging.debug('Return code of yum install: {0}'.format(rsp))

        if rsp != 0:
            exceptionhandler('Installing Salt from Yum has failed!')

    def _install_from_git(self, repos):
        pass

    def download_file(self, url, filename, sourceiss3bucket=False):
        """

        :param url:
        :param filename:
        :param sourceiss3bucket:
        :return:
        """
        conn = None

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
                conn = boto.connect_s3()
                bucket = conn.get_bucket(bucket_name)
                key = bucket.get_key(key_name)
                key.get_contents_to_filename(filename=filename)
            except (NameError, boto.exception.BotoClientError):
                logging.error('NameError: {0}'.format(boto.exception.BotoClientError))
                try:
                    bucket_name = url.split('/')[2].split('.')[0]
                    key_name = '/'.join(url.split('/')[3:])
                    bucket = conn.get_bucket(bucket_name)
                    key = bucket.get_key(key_name)
                    key.get_contents_to_filename(filename=filename)
                except Exception as exc:
                    logging.error('Unable to download file from S3 bucket.\n'
                                      'url = {0}\n'
                                      'bucket = {1}\n'
                                      'key = {2}\n'
                                      'file = {3}\n'
                                      'Exception: {4}'
                                      .format(url, bucket_name, key_name,
                                              filename, exc))
                    raise SystemError('Unable to download file from S3 bucket.\n'
                                      'url = {0}\n'
                                      'bucket = {1}\n'
                                      'key = {2}\n'
                                      'file = {3}\n'
                                      'Exception: {4}'
                                      .format(url, bucket_name, key_name,
                                              filename, exc))
            except Exception as exc:
                logging.error('Unable to download file from S3 bucket.\n'
                                  'url = {0}\n'
                                  'bucket = {1}\n'
                                  'key = {2}\n'
                                  'file = {3}\n'
                                  'Exception: {4}'
                                  .format(url, bucket_name, key_name,
                                          filename, exc))
                raise SystemError('Unable to download file from S3 bucket.\n'
                                  'url = {0}\n'
                                  'bucket = {1}\n'
                                  'key = {2}\n'
                                  'file = {3}\n'
                                  'Exception: {4}'
                                  .format(url, bucket_name, key_name,
                                          filename, exc))
            logging.debug('Downloaded file from S3 bucket -- \n'
                  '    url      = {0}\n'
                  '    filename = {1}'.format(url, filename))
        else:
            try:
                response = urllib2.urlopen(url)
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

    def create_working_dir(self, basedir, prefix):
        """
        Creates a directory in `basedir` with a prefix of `dirprefix`.
        The directory will have a random 5 character string appended to `dirprefix`.
        Returns the path to the working directory.

        :rtype : str
        :param basedir: str, the directory in which to create the working directory
        :param dirprefix: str, prefix to prepend to the working directory
        """

        logging.info('Creating a working directory.')
        workingdir = None
        try:
            workingdir = tempfile.mkdtemp(prefix=prefix, dir=basedir)
        except Exception as exc:
            # TODO: Update `except` logic
            raise SystemError('Could not create workingdir in {0}.\n'
                              'Exception: {1}'.format(basedir, exc))
        logging.debug('Working directory: {0}'.format(workingdir))
        self.workingdir = workingdir

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

        logging.info('Removed temporary data in working directory -- {0}'.format(self.workingdir))
        logging.info('Exiting cleanup routine...')
        logging.info('-+' * 40)

    def extract_contents(self, filepath, to_directory='.', create_dir=None):
        """
        Extracts a compressed file to the specified directory.
        Supports files that end in .zip, .tar.gz, .tgz, tar.bz2, or tbz.
        :param filepath: str, path to the compressed file
        :param to_directory: str, path to the target directory
        :raise ValueError: error raised if file extension is not supported
        """
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
            exceptionhandler('{0}'.format('Could not extract `"{0}`" as no appropriate '
                             'extractor is found'.format(filepath)))


        if create_dir:
            to_directory = os.sep.join((to_directory,
                                               '.'.join(filepath.split(os.sep)[-1].split('.')[:-1])))

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
        pass

    def _get_s3_file(self, url, bucket_name, key_name, destination):
        pass

    def download_file(self, url, filename, sourceiss3bucket):
        pass

    def create_working_dir(self, basedir, prefix):
        pass

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
