+++++++++
Python CI
+++++++++

Build a CI to test popular numpy on the master branch of Python.

* https://etherpad.gnome.org/p/python-master-ci
* https://github.com/vstinner/python-ci

Projects which should be tested to modify Python:

* setuptools
* pip
* numpy
* jinja2
* docutils
* Sphinx

This project is a proof-of-concept.

Usage::

    python3 -m pythonci test numpy

Cleanup::

    python3 -m pythonci clean numpy

Cleanup all::

    python3 -m pythonci cleanall numpy

Contact: Victor Stinner (Red Hat), vstinner@python.org

TODO:

* coverage runs tests using tox, but tox uses Python 3.7 rather than the Python
  program used to run pythonci.
