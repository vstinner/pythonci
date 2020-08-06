from pythonci.task import BaseTask


URL = 'https://files.pythonhosted.org/packages/20/c0/0df91b7bde75063316f0aa5fa699f76b2bbb4514f190a2f68580b18d2f31/coverage-5.2.1.tar.gz'


class Task(BaseTask):
    name = 'coverage'

    def _install(self):
        self.app.download_extract_tarball(URL, self.dirname)
        self.app.chdir(self.dirname)
        # FIXME: don't use tox
        self.app.pip_install_update(["tox"])
        self.app.patch_tox_basepython()

    def _run_tests(self):
        self.app.chdir(self.dirname)
        # tox -e py run tests with the Python executable used to run tox
        # https://github.com/nedbat/coveragepy/issues/1001
        self.app.run_python(["-m", "tox", "-e", "py"])
