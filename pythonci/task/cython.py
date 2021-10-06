import os.path
from pythonci.task import BaseTask


TARBALL = 'https://files.pythonhosted.org/packages/59/e3/78c921adf4423fff68da327cc91b73a16c63f29752efe7beb6b88b6dd79d/Cython-0.29.24.tar.gz'


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
