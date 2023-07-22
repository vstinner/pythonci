import os.path
from pythonci.task import BaseTask


TARBALL = 'https://files.pythonhosted.org/packages/30/39/7305428d1c4f28282a4f5bdbef24e0f905d351f34cf351ceb131f5cddf78/lxml-4.9.3.tar.gz'


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
