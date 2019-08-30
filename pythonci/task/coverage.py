from pythonci.task import BaseTask


URL = 'https://files.pythonhosted.org/packages/85/d5/818d0e603685c4a613d56f065a721013e942088047ff1027a632948bdae6/coverage-4.5.4.tar.gz'


class Task(BaseTask):
    name = 'coverage'

    def _install(self):
        self.app.download_extract_tarball(URL, self.dirname)
        # FIXME: don't use tox
        self.app.pip_install_update(["tox"])

    def _run_tests(self):
        self.app.chdir(self.dirname)
        # FIXME: don't test Python 3.7 but Python used by pythonci!
        self.app.run_python(["-m", "tox", "-e", "py37"])
