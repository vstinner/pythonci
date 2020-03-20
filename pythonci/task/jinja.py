from pythonci.task import BaseTask


JINJA_TARBALL = 'https://files.pythonhosted.org/packages/d8/03/e491f423379ea14bb3a02a5238507f7d446de639b623187bccc111fbecdf/Jinja2-2.11.1.tar.gz'



class Task(BaseTask):
    name = 'Jinja2'

    def _install(self):
        self.app.download_extract_tarball(JINJA_TARBALL, self.dirname)
        self.app.chdir(self.dirname)

        self.app.run_python(["setup.py", "install"], cwd=self.dirname)
        self.app.pip_install_update(["pytest"])

    def _run_tests(self):
        # FIXME: test with -Werror?
        self.app.run_python(["-m", "pytest", "--tb=short"])
