from pythonci.task import BaseTask


JINJA_TARBALL = 'https://files.pythonhosted.org/packages/7b/db/1d037ccd626d05a7a47a1b81ea73775614af83c2b3e53d86a0bb41d8d799/Jinja2-2.10.3.tar.gz'


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
