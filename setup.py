#!/usr/bin/env python3

# Prepare a release:
#
#  - git pull --rebase
#  - update version in setup.py, pythonci/__init__.py and doc/conf.py
#  - set release date in doc/changelog.rst
#  - git commit -a -m "prepare release x.y"
#  - Remove untracked files/dirs: git clean -fdx
#  - run tests: tox
#  - git push
#  - check Travis CI status:
#    https://travis-ci.org/vstinner/pythonci
#
# Release a new version:
#
#  - git tag VERSION
#  - git push --tags
#  - Remove untracked files/dirs: git clean -fdx
#  - python3 setup.py sdist bdist_wheel
#  - twine upload dist/*
#
# After the release:
#
#  - set version to n+1
#  - git commit -a -m "post-release"
#  - git push

VERSION = '1.6.1'

DESCRIPTION = 'Python module to run and analyze benchmarks'
CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3',
    'Topic :: Software Development :: Libraries :: Python Modules',
]


# put most of the code inside main() to be able to import setup.py in
# test_tools.py, to ensure that VERSION is the same than
# pythonci.__version__.
def main():
    import os.path
    from setuptools import setup

    with open('README.rst', encoding="utf8") as fp:
        long_description = fp.read().strip()

    requirements = [os.path.join('pythonci', 'requirements.txt')]
    patch_dir = os.path.join('pythonci', 'patches')
    patches = [os.path.join(patch_dir, name)
               for name in os.listdir(patch_dir)]
    data_files = [
        ('pythonci', requirements),
        (os.path.join('pythonci', 'patches'), patches),
    ]

    options = {
        'name': 'pythonci',
        'version': VERSION,
        'license': 'MIT license',
        'description': DESCRIPTION,
        'long_description': long_description,
        'url': 'https://github.com/vstinner/pythonci',
        'author': 'Victor Stinner',
        'author_email': 'vstinner@python.org',
        'classifiers': CLASSIFIERS,
        'packages': ['pythonci'],
        'data_files': data_files,
    }
    setup(**options)


if __name__ == '__main__':
    main()
