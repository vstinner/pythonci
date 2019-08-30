from pythonci.task import Task


JINJA_TARBALL = 'https://files.pythonhosted.org/packages/93/ea/d884a06f8c7f9b7afbc8138b762e80479fb17aedbbe2b06515a12de9378d/Jinja2-2.10.1.tar.gz'


class Jinja(Task):
    name = 'Jinja2'

    def _install(self):
        self.app.download_extract_tarball(JINJA_TARBALL, self.dirname)
        self.app.chdir(self.dirname)
        self.app.apply_patches(['Jinja2-2.10.1-collections_abc.patch'], self.dirname)

        self.app.run_python(["setup.py", "install"], cwd=self.dirname)
        self.app.pip_install_update(["pytest"])

    def _run_tests(self):
        # FIXME: test with -Werror?
        self.app.run_python(["-m", "pytest", "--tb=short"])
