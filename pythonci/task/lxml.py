import os.path
from pythonci.task import BaseTask


TARBALL = 'https://files.pythonhosted.org/packages/db/f7/43fecb94d66959c1e23aa53d6161231dca0e93ec500224cf31b3c4073e37/lxml-4.6.2.tar.gz'


class Task(BaseTask):
    name = "lxml"

    def _install(self):
        self.app.install_cython()
        self.app.download_extract_tarball(TARBALL, self.dirname)
        self.app.chdir(self.dirname)
        self.app.remove_cython_files()

        cpu_count = os.cpu_count()
        cmd = ["setup.py", "build_ext", "--inplace", "--warnings", "--with-coverage"]
        if cpu_count:
            cmd.append(f"-j{cpu_count}")
        self.app.run_python(cmd)

    def _run_tests(self):
        self.app.chdir(self.dirname)
        # -p: progress bar
        # -v: verbose
        self.app.run_python(["test.py", "-p", "-v"])
