from setuptools import setup, find_packages
from codecs import open
import os

__author__ = "Alexander Urban"
__email__ = "aurban@atomistic.net"

here = os.path.abspath(os.path.dirname(__file__))
package_name = 'aetoms'
package_description = 'py3Dmol wrapper for atomic structure visualization'

# Get the long description from the README file
with open(os.path.join(here, 'README.md'), encoding='utf-8') as fp:
    long_description = fp.read()

# Get version number from the VERSION file
with open(os.path.join(here, package_name, 'VERSION')) as fp:
    version = fp.read().strip()

setup(
    name=package_name,
    version=version,
    description=package_description,
    long_description=long_description,
    author=__author__,
    author_email=__email__,
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Scientific/Engineering :: Chemistry',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ],
    keywords=['materials science', 'crystal structure', 'visualization'],
    packages=find_packages(exclude=['tests']),
    install_requires=['py3Dmol']
)
