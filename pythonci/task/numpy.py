import os.path
from pythonci.task import BaseTask


TARBALL = 'https://files.pythonhosted.org/packages/cf/7a/f68d1d658a0e68084097beb212fa9356fee7eabff8b57231cc4acb555b12/numpy-1.25.1.tar.gz'


class Task(BaseTask):
    name = "numpy"

    def _install(self):
        # rely on Fedora to provide OpenBLAS or pull it differently?

        self.app.install_cython()

        self.app.download_extract_tarball(TARBALL, self.dirname)
        self.app.chdir(self.dirname)

        self.app.remove_cython_files()

        self.app.run_python(["setup.py", "install"], cwd=self.dirname)

        self.app.pip_install_update(["nose", "pytest", "hypothesis"])

    def _run_tests(self):
        script = os.path.join(self.dirname, 'runtests.py')
        self.app.run_python([script, "--mode=full"])
