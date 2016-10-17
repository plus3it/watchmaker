import abc
import os


class SaltBase(object):
    @abc.abstractmethod
    def __init__(self):
        self.config = None
        self.entenv = None
        self.formulastoinclude = list()
        self.formulaterminationstrings = list()
        self.salt_conf = None
        self.sourceiss3bucket = None
        self.workingdir = None

    @abc.abstractmethod
    def _install_package(self):
        return

    @abc.abstractmethod
    def _prepare_for_install(self):
        if self.config['formulastoinclude']:
            self.formulastoinclude = self.config['formulastoinclude']

        if self.config['formulaterminationstrings']:
            self.formulaterminationstrings = self.config[
                'formulaterminationstrings']

        self.computername = self.config['computername']
        self.entenv = self.config['entenv']
        self.sourceiss3bucket = self.config['sourceiss3bucket']

        self.create_working_dir(self.saltworkingdir, self.saltworkingdirprefix)

        self.salt_results_logfile = self.config['salt_results_log'] or \
            os.sep.join((self.workingdir, 'saltcall.results.log'))

        self.salt_debug_logfile = self.config['salt_debug_log'] or \
            os.sep.join((self.workingdir, 'saltcall.debug.log'))

        self.saltcall_arguments = [
            '--out', 'yaml', '--out-file', self.salt_results_logfile,
            '--return', 'local', '--log-file', self.salt_debug_logfile,
            '--log-file-level', 'debug'
        ]

        for saltdir in [self.saltfileroot,
                        self.saltbaseenv,
                        self.saltformularoot]:
            try:
                os.makedirs(saltdir)
            except OSError:
                if not os.path.isdir(saltdir):
                    raise
