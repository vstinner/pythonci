import os.path
from pythonci.task import BaseTask


NUMPY_ZIP = 'https://files.pythonhosted.org/packages/f1/2c/717bdd12404c73ec0c8c734c81a0bad7048866bc36a88a1b69fd52b01c07/numpy-1.19.0.zip'


class Task(BaseTask):
    name = "numpy"

    def _install(self):
        # rely on Fedora to provide OpenBLAS or pull it differently?

        self.app.install_cython()

        self.app.download_extract_zip(NUMPY_ZIP, self.dirname)
        self.app.chdir(self.dirname)

        self.app.remove_cython_files()

        self.app.run_python(["setup.py", "install"], cwd=self.dirname)

        self.app.pip_install_update(["nose", "pytest"])

    def _run_tests(self):
        script = os.path.join(self.dirname, 'tools', 'test-installed-numpy.py')
        self.app.run_python([script, "--mode=full"])
