from pythonci.task import BaseTask


JINJA_TARBALL = 'https://files.pythonhosted.org/packages/7a/ff/75c28576a1d900e87eb6335b063fab47a8ef3c8b4d88524c4bf78f670cce/Jinja2-3.1.2.tar.gz'


class Task(BaseTask):
    name = 'Jinja2'

    def _install(self):
        self.app.download_extract_tarball(JINJA_TARBALL, self.dirname)
        self.app.chdir(self.dirname)

        self.app.run_python(["-m", "pip", "install", "."], cwd=self.dirname)
        self.app.pip_install_update(["pytest"])

    def _run_tests(self):
        self.app.run_python(["-m", "pytest", "--tb=short"])
