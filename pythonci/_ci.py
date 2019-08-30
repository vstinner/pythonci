import argparse
import ast
import io
import os.path
import shlex
import shutil
import subprocess
import sys
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
        self.set_work_dir()

        self.python_warnings = []
        # self.python_warnings.append('error')
        self.python_dev_mode = True
        # self.python_bytes_warnings = None

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

    def run_command(self, args, **kw):
        cmd_str = ' '.join(shlex.quote(arg) for arg in args)
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

    def project_directory(self, name):
        version = self.package_versions[name]
        return os.path.join(self.work_dir, "%s-%s" % (name, version))

    def download_extract_zip(self, url, dirname):
        filename = get_url_filename(url, '.zip')
        filename = self.download(url, filename)

        self.rmtree(dirname)
        self.run_command(["unzip", "-d", self.work_dir, filename])

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
        self.patch('setuptools.patch', venv_libdir)

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
        self.args = parser.parse_args()

    def set_work_dir(self, name=None):
        if name:
            self.work_dir = os.path.join(self.root_dir, name)
        else:
            self.work_dir = self.root_dir
        self.download_dir = os.path.join(self.root_dir, 'download')
        self.venv_dir = os.path.join(self.work_dir, 'venv')

    def chdir(self, path):
        self.log("Change directory: %s" % path)
        os.chdir(path)

    def setup_env(self, name):
        self.mkdir(self.root_dir)
        self.mkdir(self.work_dir)
        self.chdir(self.work_dir)
        self.setup_venv()

    def main(self):
        self.parse_options()
        if self.args.command == 'cleanall':
            self.rmtree(self.root_dir)
            return

        task_name = self.args.task
        command = self.args.command

        if self.args.command == 'clean':
            self.rmtree(self.work_dir)
        else:
            pyver = self.get_python_version()
            self.set_work_dir(task_name + "-py%s.%s" % pyver[:2])

            modname = 'pythonci.task.' + task_name
            mod = __import__(modname).task
            mod = getattr(mod, task_name)
            task_class = mod.Task
            task = task_class(self)

            if command == 'install':
                task.install()
            elif command == 'test':
                task.run_tests()
            else:
                raise Exception("unknown command: %r" % command)