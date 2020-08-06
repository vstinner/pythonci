from pythonci.task import BaseTask


JINJA_TARBALL = 'https://files.pythonhosted.org/packages/64/a7/45e11eebf2f15bf987c3bc11d37dcc838d9dc81250e67e4c5968f6008b6c/Jinja2-2.11.2.tar.gz'



class Task(BaseTask):
    name = 'Jinja2'

    def _install(self):
        self.app.download_extract_tarball(JINJA_TARBALL, self.dirname)
        self.app.chdir(self.dirname)

        self.app.run_python(["setup.py", "install"], cwd=self.dirname)
        self.app.pip_install_update(["pytest"])

    def _run_tests(self):
        self.app.run_python(["-m", "pytest", "--tb=short"])
