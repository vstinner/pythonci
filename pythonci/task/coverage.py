from pythonci.task import BaseTask


URL = 'https://files.pythonhosted.org/packages/fe/4d/3d892bdd21acba6c9e9bec6dc93fbe619883a0967c62f976122f2c6366f3/coverage-5.1.tar.gz'


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
        self.app.run_python(["-m", "tox", "-e", "py"])
