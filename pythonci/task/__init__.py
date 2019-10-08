import os.path


PYTHONCI_PREFIX = 'python-ci-'


class BaseTask:
    name = None

    def __init__(self, app):
        self.app = app
        self._install_marker_file = None
        self.dirname = self.app.package_directory(self.name)

    def _install(self):
        pass

    def install(self):
        self.app.setup_env()
        self._install_marker_file = os.path.join(self.app.task_dir,
                                                 PYTHONCI_PREFIX + 'install_marker_file')

        if os.path.exists(self._install_marker_file):
            self.app.log("%s is already installed in: %s"
                         % (self.name, self.dirname))
            return

        try:
            self._install()
        except:  # noqa
            self.app.unlink(self._install_marker_file)
            raise

        self.app.log("%s installed in: %s" % (self.name, self.dirname))
        self.app.create_empty_file(self._install_marker_file)

    def _run_tests(self):
        pass

    def run_tests(self):
        self.install()
        self._run_tests()
