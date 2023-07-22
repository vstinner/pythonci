import os.path
from pythonci.task import BaseTask


TARBALL = 'https://files.pythonhosted.org/packages/7f/a2/fd5ced5dd33597ef291861bfadd46820de417b41bcb6ca2fa0b5f6fa8152/Cython-3.0.0.tar.gz'


class Task(BaseTask):
    name = "Cython"

    def _install(self):
        self.app.download_extract_tarball(TARBALL, self.dirname)
        self.app.chdir(self.dirname)

        self.app.run_python(["setup.py", "install"], cwd=self.dirname)

    def _run_tests(self):
        print("DIRNAME", self.dirname)
        self.app.run_python(['runtests.py', '-vv', '--no-pyregr'],
                            cwd=self.dirname)
