import os.path
from pythonci.task import BaseTask


NUMPY_ZIP = 'https://files.pythonhosted.org/packages/84/1e/ff467ac56bfeaea51d4a2e72d315c1fe440b20192fea7e460f0f248acac8/numpy-1.18.2.zip'



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
