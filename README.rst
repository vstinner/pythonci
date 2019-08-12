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

    python3 -m python_ci

Cleanup::

    python3 -m python_ci clean

Contact: Victor Stinner (Red Hat)
