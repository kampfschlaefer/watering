import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

if sys.version_info <= (3, 4):
    raise NotImplementedError(
        'This package uses asyncio from python 3.4. You can\'t install it on '
        'python below that.'
    )


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # imported here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(
    name='watering',
    version='0.1',
    author='Arnold Krille',
    author_email='arnold@arnoldarts.de',
    license='GPLv2',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'watering_simulator = watering.simulation:run',
            'pumpcontroller = watering.pumpcontroller:run',
        ]
    },
    dependency_links=[
        'https://github.com/pytest-dev/pytest-asyncio/archive/v0.1.3.tar.gz'
        '#egg=pytest_asyncio'
    ],
    install_requires=[
        'pifacecommon==4.1.2',
        'pifacedigitalio==3.0.5',
        'err>=2.2.0',
    ],
    tests_require=[
        'pytest',
        'pytest-xdist',
        'pytest-cov',
        'pytest_asyncio==0.1.3',
        'pytest-flake8',
    ],
    cmdclass={'test': PyTest},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Programming Language :: Python :: 3.4',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: POSIX :: Linux',
        'Topic :: Home Automation',
    ],
)
