import os.path
from pythonci.task import BaseTask


NUMPY_ZIP = 'https://files.pythonhosted.org/packages/01/1b/d3ddcabd5817be02df0e6ee20d64f77ff6d0d97f83b77f65e98c8a651981/numpy-1.18.5.zip'


class Task(BaseTask):
    name = "numpy"

    def _install(self):
        # rely on Fedora to provide OpenBLAS or pull it differently?

        self.app.install_cython()

        self.app.download_extract_zip(NUMPY_ZIP, self.dirname)
        self.app.chdir(self.dirname)

        self.app.patch('numpy.patch')
        self.app.remove_cython_files()

        self.app.run_python(["setup.py", "install"], cwd=self.dirname)

        self.app.pip_install_update(["nose", "pytest"])

    def _run_tests(self):
        script = os.path.join(self.dirname, 'tools', 'test-installed-numpy.py')
        self.app.run_python([script, "--mode=full"])
