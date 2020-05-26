import os.path
from pythonci.task import BaseTask


TARBALL = 'https://files.pythonhosted.org/packages/79/36/69246177114d0b6cb7bd4f9aef177b434c0f4a767e05201b373e8c8d7092/Cython-0.29.19.tar.gz'



class Task(BaseTask):
    name = "Cython"

    def _install(self):
        self.app.download_extract_tarball(TARBALL, self.dirname)
        self.app.chdir(self.dirname)
        self.app.patch('cython.patch')

        self.app.run_python(["setup.py", "install"], cwd=self.dirname)

    def _run_tests(self):
        print("DIRNAME", self.dirname)
        self.app.run_python(['runtests.py', '-vv', '--no-pyregr'],
                            cwd=self.dirname)
