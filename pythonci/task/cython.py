import os.path
from pythonci.task import BaseTask


TARBALL = 'https://files.pythonhosted.org/packages/3f/61/16a435de52fcda15246597a602aab6132cea50bedeb0919cb8874a068a20/Cython-0.29.20.tar.gz'


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
