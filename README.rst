+++++++++
Python CI
+++++++++

pythonci
========

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
* psycopg2

This project is a proof-of-concept.

Python 2 is not supported: pythonci requires Python 3.6 or newer.

The tested Python is the Python used to run the command.

Test numpy (stable releases)::

    python3 -m pythonci test numpy

Test development versions::

    python3 -m pythonci test numpy --dev

Cleanup::

    python3 -m pythonci clean numpy

Cleanup all::

    python3 -m pythonci cleanall numpy

Contact: Victor Stinner (Red Hat), vstinner@python.org

TODO
====

* coverage runs tests using tox, but tox uses Python 3.7 rather than the Python
  program used to run pythonci.
* Compile and install master branch of Python

Status
======

2019-10-28
----------

* jinja: PASS
* coverage: FAIL
* numpy: FAIL

coverage job fails with pip 19.1.1 which is not compatible with Python 3.9:

      File "work/cpython-3.9.0a0_coverage-4.5.4/venv/lib/python3.9/site-packages/virtualenv_support/pip-19.1.1-py2.py3-none-any.whl/pip/_vendor/html5lib/_trie/_base.py", line 3, in <module>
    ImportError: cannot import name 'Mapping' from 'collections' (/home/vstinner/myprojects/pythonci/work/cpython-3.9.0a0_coverage-4.5.4/coverage-4.5.4/.tox/py37/lib/python3.9/collections/__init__.py)

Cython 0.29.13 is broken by Python 3.9, use collections.Iterable

* Need a Cython release
* Fixed by: https://github.com/cython/cython/commit/35fe19096c223b65ba3dfb4b7df185e2389b1f87#diff-7709661204b9afb11dad99f803bb188a
