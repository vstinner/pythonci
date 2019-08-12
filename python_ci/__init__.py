import argparse
import ast
import io
import os.path
import subprocess
import sys
import shlex
import shutil

# Fedora build dependencies:
# python3
# gcc
# ???

VENV_DIR = 'venv'

# FIXME: reproduce env vars
# FIXME: reproduce build

NUMPY_ZIP = 'https://files.pythonhosted.org/packages/da/32/1b8f2bb5fb50e4db68543eb85ce37b9fa6660cd05b58bddfafafa7ed62da/numpy-1.17.0.zip'
JINJA_TARBALL = 'https://files.pythonhosted.org/packages/93/ea/d884a06f8c7f9b7afbc8138b762e80479fb17aedbbe2b06515a12de9378d/Jinja2-2.10.1.tar.gz'


def add_version(package_name, version):
    if version is not None:
        return '%s==%s' % (package_name, version)
    else:
        return package_name


class CI:
    def __init__(self):
        self.source_dir = os.path.abspath(os.path.dirname(__file__))

        self.work_dir = os.path.abspath('work')
        self.mkdir(self.work_dir)
        self.download_dir =  os.path.join(self.work_dir, 'download')

        self.python_warnings = []
        #self.python_warnings.append('error')
        self.python_dev_mode = True
        #self.python_bytes_warnings = None
        # 2 stands for '-bb'
        self.python_bytes_warnings = 2
        self.read_package_versions()

        if self.python_bytes_warnings and self.python_bytes_warnings > 1:
            self.python_warnings.append('error::BytesWarning')

        self.env = self.create_environ()
        self.python_options = []
        if self.python_bytes_warnings:
            self.python_options.append('-' + 'b' * self.python_bytes_warnings)
        if self.python_dev_mode:
            self.python_options.extend(['-X', 'dev'])
        for warn in self.python_warnings:
            self.python_options.append('-W%s' % warn)

        self._python_version = None
        self.venv_dir = os.path.join(self.work_dir, 'venv')
        self.set_python(sys.executable)

    def create_environ(self):
        env = dict(os.environ)
        for key in list(env):
            if key.startswith('PYTHON'):
                del env[key]
        if self.python_dev_mode:
            env['PYTHONDEVMODE'] = '1'
        if self.python_warnings:
            env['PYTHONWARNINGS'] = ','.join(self.python_warnings)

    def log(self, message):
        print(message)

    def mkdir(self, path):
        if os.path.exists(path):
            return
        self.log("Create directory: %s" % path)
        os.mkdir(path)

    def set_python(self, python):
        python = os.path.abspath(python)
        self.python_args = [python] + self.python_options

    def run_command(self, args, **kw):
        cmd_str = ' '.join(shlex.quote(arg) for arg in args)
        text = "Run command: %s" % cmd_str
        if 'cwd' not in kw:
            kw['cwd'] = self.work_dir
        text += ' in %s' % kw['cwd']
        self.log(text)
        if 'stdin' not in kw:
            kw['stdin'] = subprocess.DEVNULL
        proc = subprocess.run(args, **kw)
        if proc.returncode:
            raise Exception(proc)
        return proc

    def run_python(self, args, **kw):
        return self.run_command(self.python_args + args, **kw)

    def patch(self, filename, directory=os.path.curdir, level=1):
        filename = os.path.join(self.source_dir, 'patches', filename)
        with open(filename) as fp:
            # --force: do not ask any questions
            self.run_command(['patch', '-p%s' % level, '--force'],
                             stdin=fp,
                             cwd=directory)

    def read_package_versions(self):
        # parse requirements.txt
        self.package_versions = {}
        filename = os.path.join(self.source_dir, 'requirements.txt')
        with io.open(filename, encoding='utf8') as fp:
            for line in fp:
                line = line.rstrip()
                if '==' in line:
                    name, version = line.split('==', 1)
                else:
                    name = line
                    version = None
                self.package_versions[name] = version

    def pip_install_update(self, packages):
        args = []
        for name in packages:
            try:
                version = self.package_versions[name]
            except KeyError:
                raise Exception("unversionned package: %r" % name)
            arg = add_version(name, version)
            args.append(arg)
        return self.run_python(["-m", "pip", "install", "--upgrade"] + list(args))

    def get_python_version(self):
        if self._python_version is None:
            proc = self.run_python(["-c", "import sys; print(sys.version_info[:3])"],
                                   stdout=subprocess.PIPE,
                                   universal_newlines=True)
            line = proc.stdout.rstrip()
            self._python_version = ast.literal_eval(line)
        return self._python_version

    def download(self, url, filename):
        self.mkdir(self.download_dir)

        filename = os.path.basename(filename)
        filename = os.path.join(self.download_dir, filename)

        # already downloaded: do nothing
        if os.path.exists(filename):
            return filename

        try:
            self.run_command(["wget", "-O", filename, url])
        except:
            self.unlink(filename)
            raise

        return filename

        # FIXME: validate a checksum?

    def unlink(self, filename):
        if not os.path.exists(filename):
            return
        self.log("Remove file: %s" % filename)
        os.unlink(filename)

    def rmtree(self, dirname):
        if not os.path.exists(dirname):
            return
        self.log("Remove directory: %s" % dirname)
        shutil.rmtree(dirname)

    def install_numpy(self, run_tests=True):
        # rely on Fedora to provide OpenBLAS or pull it differently?
        self.pip_install_update(["Cython"])

        version = self.package_versions['numpy']
        url = NUMPY_ZIP
        dirname = os.path.abspath("numpy-%s" % version)
        filename = self.download(url, 'numpy-%s.zip' % version)

        if 1:
            self.rmtree(dirname)
            self.run_command(["unzip", "-d", ".", filename])

            # Force to run Cython: regenerate C files generated by Cython
            cmd = r"rm -f -v $(grep -rl '/\* Generated by Cython') PKG-INFO"
            self.run_command([cmd], shell=True, cwd=dirname)

            self.run_python(["setup.py", "install"], cwd=dirname)

        if run_tests:
            if 0:
                self.pip_install_update(["tox", "pytest"])

                ver = self.get_python_version()
                env = 'py%s%s' % ver[:2]
                self.run_python(["-m", "tox", "-e", env], cwd=dirname)
            else:
                self.pip_install_update(["nose", "pytest"])
                self.run_python([os.path.join(dirname, 'tools', 'test-installed-numpy.py'), "--mode=full"])

    def install_jinja(self, run_tests=True):
        version = self.package_versions['Jinja2']
        url = JINJA_TARBALL
        dirname = os.path.join(self.work_dir, "Jinja2-%s" % version)
        filename = self.download(url, 'Jinja2-%s.tar.gz' % version)

        if 1:
            self.rmtree(dirname)
            self.run_command(["tar", "-xf", filename])

            self.patch('Jinja2-2.10.1-collections_abc.patch', dirname)

            self.run_python(["setup.py", "install"], cwd=dirname)

        if run_tests:
            self.pip_install_update(["pytest"])
            #self.run_python(["-m", "pytest", "--tb=short", "-Werror"])
            self.run_python(["-m", "pytest", "--tb=short"])

    def patch_pip(self):
        ver = self.get_python_version()
        venv_libdir = os.path.join(self.venv_dir, 'lib', 'python%s.%s' % (ver[0], ver[1]), 'site-packages')
        self.patch('pip2.patch', venv_libdir)
        self.patch('setuptools.patch', venv_libdir)

    def setup_venv(self):
        create_venv = not os.path.exists(self.venv_dir)
        if create_venv:
            try:
                self.run_python(["-m", "venv", self.venv_dir])
                self.patch_pip()
            except:
                self.rmtree(self.venv_dir)
                raise

        self.set_python(os.path.join(self.venv_dir, "bin", "python"))
        if create_venv:
            self.pip_install_update(["setuptools", "pip"])
            self.patch_pip()

    def parse_options(self):
        parser = argparse.ArgumentParser(description='Process some integers.')
        parser.add_argument('command', nargs='?',
                            choices='run clean'.split(),
                            default='run')
        self.args = parser.parse_args()

    def run(self):
        self.setup_venv()
        #self.install_numpy()
        self.install_jinja()

    def cleanup(self):
        self.rmtree(self.work_dir)

    def main(self):
        self.parse_options()
        if self.args.command == 'clean':
            self.cleanup()
        else:
            self.run()
