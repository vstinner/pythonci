+++++++++
Python CI
+++++++++

pythonci
========

Build a CI to test popular PyPI projects on the master branch of Python.

* https://etherpad.gnome.org/p/python-master-ci
* https://github.com/vstinner/python-ci

Available tasks:

* coverage
* cython
* jinja
* numpy
* lxml

This project is a proof-of-concept.

There are different goals:

* Test if incompatible changes are going to break projects
* Run tests with warnings treated as errors, especially DeprecationWarning.

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

Goals
=====

* Report issues to core developers who authored changes which broken projects.
* Report issues to broken projects to help them to be prepared for the next
  Python.
* Increase the number of compatible projects when a new Python version
  is released.
* Estimate how many projects are broken by a change, before pushing the change.
* Reduce the workload of Fedora which currently is one of the first to detect
  incompatible changes and broken packages.

Use Cases
=========

Check if a future Python change breaks third-party projects
-----------------------------------------------------------

Examples:

* PEP 620 incompatible C API changes.
* Remove "U" mode of the open() function: deprecated function.

Detect projects broken by Python incompatible changes
-----------------------------------------------------

Some Python changes are not seen by their authors as incompatible changes,
but sometimes there are 5 or more projects broken by such change. If the
authors of such change would be notified earlier of broken packages, they
can enhance the documentation explaining how to port the code, they can help
to fix these broken packages, and they can consider to revert the change
and only reapply it once enough projects are fixed.

Check for DeprecationWarning
----------------------------

Run the test suite using: python3 -Werror.

Test in development mode
------------------------

Run the test suite using: python3 -X dev.


TODO
====

Projects which should be tested:

* django
* docutils
* pillow
* pip
* psycopg2
* scipy
* setuptools
* sphinx

Bugs:

* jinja: DeprecationWarning crash:
  https://github.com/pallets/jinja/issues/1276

Tasks:

* jinja: run tests with -Werror?
* coverage runs tests using tox, but tox uses Python 3.7 rather than the Python
  program used to run pythonci.
* Compile and install master branch of Python
* What are build dependencies? python3, gcc, etc.?
* Make builds more reproducible: https://reproducible-builds.org/

Fedora COPR
===========

In Fedora, "COPR" are created: rebuild some Fedora package with a newer Python.

* Based on Fedora Rawhide
* Need to identify the bootstrap sequence: dnf, compose tool, bodhi
* Test 10 popular Python projects: cython, scipy, django, ...
* Need to change COPR to avoid updates unrelated to Python: kernel, GCC, glibc

Update the python package every N weeks.

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

Existing CIs
============

* https://conda-forge.org/
* Travis CI "nightly" Python

See also: https://pythondev.readthedocs.io/test_next_python.html
