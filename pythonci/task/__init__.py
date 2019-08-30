import os.path


PYTHONCI_PREFIX = 'python-ci-'


class Task:
    name = None

    def __init__(self, app):
        self.app = app
        self._install_marker_file = None
        self.dirname = self.app.project_directory(self.name)

    def _install(self):
        pass

    def install(self):
        self.app.setup_env(self.name)
        self._install_marker_file = os.path.join(self.app.work_dir,
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
        self.app.create_empty_file(self._install_marker_file)

    def _run_tests(self):
        pass

    def run_tests(self):
        self.install()
        self._run_tests()
