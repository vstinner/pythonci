import argparse
import ast
import io
import os.path
import shlex
import shutil
import subprocess
import sys
import textwrap
import urllib.parse


# FIXME what are (build) dependencies? python3, gcc, ???
# FIXME: reproduce build


def get_url_filename(url, suffix):
    filename = urllib.parse.urlparse(url).path
    filename = filename.split('/')[-1]
    if not filename.endswith(suffix):
        raise Exception("%r filename doesn't end with %r suffix; url=%r"
                        % (filename, suffix, url))
    return filename


def add_version(package_name, version):
    if version is not None:
        return '%s==%s' % (package_name, version)
    else:
        return package_name


class CI:
    def __init__(self):
        self.source_dir = os.path.abspath(os.path.dirname(__file__))
        self.root_dir = os.path.abspath('work')
        self.set_task_dir()

        self.python_warnings = []
        # self.python_warnings.append('error')
        self.python_dev_mode = True
        # self.python_bytes_warnings = None

        # 2 stands for '-bb'
        self.python_bytes_warnings = 0
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
        self._python_version_str = None
        self._orig_python_args = None
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
        return env

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
        if self._orig_python_args is None:
            self._orig_python_args = self.python_args

    def run_command(self, args, quiet=False, **kw):
        cmd_str = ' '.join(shlex.quote(arg) for arg in args)
        cmd_str = cmd_str.replace("\n", "\\n")
        if not quiet:
            text = "Run command: %s" % cmd_str
            if 'cwd' in kw:
                text += ' in %s' % kw['cwd']
            self.log(text)
        if 'stdin' not in kw:
            kw['stdin'] = subprocess.DEVNULL
        if 'env' in kw:
            raise NotImplementedError("cannot override env")
        kw['env'] = self.env

        proc = subprocess.run(args, **kw)

        exitcode = proc.returncode
        if exitcode:
            raise Exception("%s command failed with exit code %s"
                            % (cmd_str, exitcode))

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
        if not packages:
            raise ValueError
        args = ["-m", "pip", "install", "--upgrade"]
        for name in packages:
            try:
                version = self.package_versions[name]
            except KeyError:
                raise Exception("unversionned package: %r" % name)
            arg = add_version(name, version)
            args.append(arg)
        return self.run_python(args)

    def get_python_version(self):
        if self._python_version is not None:
            return self._python_version

        code = "import sys; print(sys.version_info[:3])"
        proc = self.run_python(["-c", code],
                               stdout=subprocess.PIPE,
                               universal_newlines=True,
                               quiet=True)
        line = proc.stdout.rstrip()
        self._python_version = ast.literal_eval(line)
        return self._python_version

    def get_python_version_str(self):
        # Get the Python version string including the Python implementation
        # name. Example: 'cpython-3.8.0b4'
        if self._python_version_str is not None:
            return self._python_version_str

        code = textwrap.dedent("""
            import sys

            if hasattr(sys, 'implementation'):
                name = sys.implementation.name
            else:
                import platform
                name = platform.python_implementation()
            name = name.lower()

            version = sys.version.split()[0]

            print("%s-%s" % (name, version))
        """)

        proc = self.run_python(["-c", code],
                               stdout=subprocess.PIPE,
                               universal_newlines=True,
                               quiet=True)
        self._python_version_str = proc.stdout.rstrip()
        return self._python_version_str

    def download(self, url, filename):
        self.mkdir(self.download_dir)

        filename = os.path.basename(filename)
        filename = os.path.join(self.download_dir, filename)

        # already downloaded: do nothing
        if os.path.exists(filename):
            return filename

        try:
            self.run_command(["wget", "-O", filename, url])
        except:  # noqa
            self.unlink(filename)
            raise

        return filename

        # FIXME: validate a checksum?

    def create_empty_file(self, filename):
        open(filename, 'wb', 0).close()

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

    def package_directory(self, name):
        # Create an absolute path
        # Example: "/path/to/numpy-1.17.2"
        version = self.package_versions[name]
        dirname = "%s-%s" % (name, version)
        return os.path.join(self.task_dir, dirname)

    def task_directory_name(self, name):
        # Example: "cpython-3.8_numpy-1.16.2"
        python = self.get_python_version_str()
        version = self.package_versions[name]
        dirname = "%s_%s-%s" % (python, name, version)
        if self.args.dev:
            dirname += "-dev"
        return dirname

    def download_extract_zip(self, url, dirname):
        filename = get_url_filename(url, '.zip')
        filename = self.download(url, filename)

        self.rmtree(dirname)
        self.run_command(["unzip", "-d", self.task_dir, filename])

    def download_extract_tarball(self, url, dirname):
        filename = get_url_filename(url, '.tar.gz')
        filename = self.download(url, filename)

        self.rmtree(dirname)
        self.run_command(["tar", "-xf", filename])

    def apply_patches(self, patches, dirname):
        for filename in patches:
            self.patch(filename, dirname)

    def patch_pip(self):
        ver = self.get_python_version()
        venv_libdir = os.path.join(self.venv_dir, 'lib', 'python%s.%s' % (ver[0], ver[1]), 'site-packages')
        self.patch('pip2.patch', venv_libdir)

    def setup_venv(self):
        create_venv = not os.path.exists(self.venv_dir)

        if create_venv:
            try:
                self.run_python(["-m", "venv", self.venv_dir])
            except:   # noqa
                self.rmtree(self.venv_dir)
                raise
        else:
            self.log("venv already exists: %s" % self.venv_dir)

        self.set_python(os.path.join(self.venv_dir, "bin", "python"))

        if create_venv:
            self.pip_install_update(["setuptools", "pip"])
            self.patch_pip()

    def get_tasks(self):
        task_dir = os.path.join(self.source_dir, 'task')
        names = [name[:-3] for name in os.listdir(task_dir)
                 if not name.startswith("__init__.") and name.endswith(".py")]
        return names

    def parse_options(self):
        tasks = self.get_tasks()
        parser = argparse.ArgumentParser(description='Process some integers.')
        parser.add_argument('command',
                            choices='install test clean cleanall'.split())
        parser.add_argument('task',
                            choices=sorted(tasks))
        parser.add_argument('--dev', action="store_true")
        self.args = parser.parse_args()

    def set_task_dir(self, name=None):
        if name:
            self.task_dir = os.path.join(self.root_dir, name)
        else:
            self.task_dir = self.root_dir
        self.download_dir = os.path.join(self.root_dir, 'download')
        self.venv_dir = os.path.join(self.task_dir, 'venv')

    def chdir(self, path):
        self.log("Change directory: %s" % path)
        os.chdir(path)

    def setup_env(self):
        self.mkdir(self.root_dir)
        self.mkdir(self.task_dir)
        self.chdir(self.task_dir)
        self.setup_venv()

    def _get_task(self):
        task_name = self.args.task

        modname = 'pythonci.task.' + task_name
        mod = __import__(modname).task
        mod = getattr(mod, task_name)
        task_class = mod.Task
        return task_class(self)

    def patch_tox_basepython(self):
        # rely on the current working directory
        filename = 'tox.ini'

        with open(filename, encoding="utf-8") as fp:
            content = fp.read()

        # Don't pass arguments, only the executable
        # Don't use the Python of the venv, but the original Python
        #python = self._orig_python_args[0]
        python = self.python_args[0]
        line = f"basepython = {python}\n"

        testenv = "[testenv]\n"
        pos = content.find(testenv)
        if pos:
            pos += len(testenv)
            content = content[:pos] + line + content[pos:]
        else:
            content = f"{testenv}{line}" + content

        with open(filename, "w", encoding="utf-8") as fp:
            fp.write(content)
            fp.flush()

        self.log(f"basepython overriden in {filename}")

    def main(self):
        self.parse_options()
        if self.args.command == 'cleanall':
            self.rmtree(self.root_dir)
            return

        task = self._get_task()

        command = self.args.command
        if command == 'clean':
            self.rmtree(self.task_dir)
        else:
            if command == 'install':
                task.install()
            elif command == 'test':
                task.run_tests()
            else:
                raise Exception("unknown command: %r" % command)

    def remove_cython_files(self):
        # Force to run Cython: regenerate C files generated by Cython
        # in the current directory and subdirectories.
        cmd = r"rm -f -v $(grep -rl '/\* Generated by Cython') PKG-INFO"
        self.run_command([cmd], shell=True)

    def install_cython(self):
        if self.args.dev:
            url = "git+git://github.com/cython/cython.git@0.29x" # "#egg=Cython"
            self.run_python(["-m", "pip", "install", url])
        else:
            self.pip_install_update(["Cython"])
