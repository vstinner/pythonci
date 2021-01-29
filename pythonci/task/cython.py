import os.path
from pythonci.task import BaseTask


TARBALL = 'https://files.pythonhosted.org/packages/6c/9f/f501ba9d178aeb1f5bf7da1ad5619b207c90ac235d9859961c11829d0160/Cython-0.29.21.tar.gz'


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
