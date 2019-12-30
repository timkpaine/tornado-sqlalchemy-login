from setuptools import setup, find_packages
from codecs import open
import os.path
import io

pjoin = os.path.join
here = os.path.abspath(os.path.dirname(__file__))
name = 'tornado_sqlalchemy_login'


def get_version(file, name='__version__'):
    path = os.path.realpath(file)
    version_ns = {}
    with io.open(path, encoding="utf8") as f:
        exec(f.read(), {}, version_ns)
    return version_ns[name]

version = get_version(pjoin(here, name, '_version.py'))

with open(pjoin(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

requires = [
    'jinja2>=2.10',
    'sqlalchemy>=1.3.0',
    'tornado>=6.0.3',
    'ujson>=1.35',
]

requires_dev = [
    'flake8>=3.7.8',
    'mock>=3.0.5',
    'pybind11>=2.4.0',
    'pytest>=4.3.0',
    'pytest-cov>=2.6.1',
    'Sphinx>=1.8.4',
    'sphinx-markdown-builder>=0.5.2',
] + requires

setup(
    name=name,
    version=version,
    description='Simple Python Utilities',
    long_description=long_description,
    url='https://github.com/timkpaine/tornado_sqlalchemy_login',
    author='Tim Paine',
    author_email='timothy.k.paine@gmail.com',
    license='Apache 2.0',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],

    keywords='utilities for python',
    zip_safe=False,
    packages=find_packages(exclude=[]),
    include_package_data=True,
    install_requires=requires,
    extras_require={
        'dev': requires_dev,
    },
)
