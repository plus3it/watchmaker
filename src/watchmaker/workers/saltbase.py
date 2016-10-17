import abc


class SaltBase(object):
    @abc.abstractmethod
    def __init__(self):
        self.config = None
        self.formulastoinclude = list()
        self.formulaterminationstrings = list()
        self.salt_conf = None
        self.sourceiss3bucket = None
        self.workingdir = None

        self.entenv = None
        self.saltbootstrapfilename = None
        self.yum_pkgs = [
            'policycoreutils-python',
            'selinux-policy-targeted',
            'salt-minion',
        ]
