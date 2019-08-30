from pythonci.task import Task


NUMPY_ZIP = 'https://files.pythonhosted.org/packages/da/32/1b8f2bb5fb50e4db68543eb85ce37b9fa6660cd05b58bddfafafa7ed62da/numpy-1.17.0.zip'


class Numpy(Task):
    name = "numpy"

    def _install(self):
        # rely on Fedora to provide OpenBLAS or pull it differently?
        self.app.pip_install_update(["Cython"])

        self.app.download_extract_zip(NUMPY_ZIP, self.dirname)
        self.app.chdir(self.dirname)

        # Force to run Cython: regenerate C files generated by Cython
        cmd = r"rm -f -v $(grep -rl '/\* Generated by Cython') PKG-INFO"
        self.app.run_command([cmd], shell=True, cwd=self.dirname)

        self.app.run_python(["setup.py", "install"], cwd=self.dirname)

    def _run_tests(self):
        self.app.pip_install_update(["nose", "pytest"])
        self.app.run_python([os.path.join(self.dirname, 'tools', 'test-installed-numpy.py'), "--mode=full"])

