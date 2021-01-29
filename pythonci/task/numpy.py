import os.path
from pythonci.task import BaseTask


NUMPY_ZIP = 'https://files.pythonhosted.org/packages/51/60/3f0fe5b7675a461d96b9d6729beecd3532565743278a9c3fe6dd09697fa7/numpy-1.19.5.zip'


class Task(BaseTask):
    name = "numpy"

    def _install(self):
        # rely on Fedora to provide OpenBLAS or pull it differently?

        self.app.install_cython()

        self.app.download_extract_zip(NUMPY_ZIP, self.dirname)
        self.app.chdir(self.dirname)

        self.app.remove_cython_files()

        self.app.run_python(["setup.py", "install"], cwd=self.dirname)

        self.app.pip_install_update(["nose", "pytest", "hypothesis"])

    def _run_tests(self):
        script = os.path.join(self.dirname, 'runtests.py')
        self.app.run_python([script, "--mode=full"])
