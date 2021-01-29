from pythonci.task import BaseTask


URL = 'https://files.pythonhosted.org/packages/29/83/9429871de6c7ec9ff113e12246af75aad4f0a7f31c66d0a499a0b7443a71/coverage-5.4.tar.gz'


class Task(BaseTask):
    name = 'coverage'

    def _install(self):
        self.app.download_extract_tarball(URL, self.dirname)
        self.app.chdir(self.dirname)
        self.app.pip_install_update(["tox"])
        self.app.patch_tox_basepython()

    def _run_tests(self):
        self.app.chdir(self.dirname)
        # tox -e py run tests with the Python executable used to run tox
        # https://github.com/nedbat/coveragepy/issues/1001
        self.app.run_python(["-m", "tox", "-e", "py"])
