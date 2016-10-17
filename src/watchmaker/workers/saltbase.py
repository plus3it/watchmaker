import abc
import os
import shutil

import yaml


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

    def _get_formulas_conf(self):
        # Obtain & extract any Salt formulas specified in formulastoinclude.
        formulas_conf = []
        for source_loc in self.formulastoinclude:
            filename = source_loc.split('/')[-1]
            file_loc = os.sep.join((self.workingdir, filename))
            self.download_file(source_loc, file_loc)
            self.extract_contents(
                filepath=file_loc,
                to_directory=self.saltformularoot
            )
            filebase = '.'.join(filename.split('.')[:-1])
            formulas_loc = os.sep.join((self.saltformularoot, filebase))

            for string in self.formulaterminationstrings:
                if filebase.endswith(string):
                    newformuladir = formulas_loc[:-len(string)]
                    if os.path.exists(newformuladir):
                        shutil.rmtree(newformuladir)
                    shutil.move(formulas_loc, newformuladir)
                    formulas_loc = newformuladir
            formulas_conf.append(formulas_loc)
        return formulas_conf

    @abc.abstractmethod
    def _build_salt_formula(self):
        if self.config['saltcontentsource']:
            self.saltcontentfilename = self.config[
                'saltcontentsource'].split('/')[-1]
            self.saltcontentfile = os.sep.join((
                self.workingdir,
                self.saltcontentfilename
            ))
            self.download_file(
                self.config['saltcontentsource'],
                self.saltcontentfile,
                self.sourceiss3bucket
            )
            self.extract_contents(
                filepath=self.saltcontentfile,
                to_directory=self.saltsrv
            )

        if not os.path.exists(os.path.join(self.saltconfpath, 'minion.d')):
            os.mkdir(os.path.join(self.saltconfpath, 'minion.d'))

        with open(
            os.path.join(self.saltconfpath, 'minion.d', 'watchmaker.conf'),
            'w'
        ) as f:
            yaml.dump(self.salt_conf, f, default_flow_style=False)
