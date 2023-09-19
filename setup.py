#!/usr/env/bin python


"""Install packages as defined in this file into the Python environment."""
from setuptools import setup, find_packages

# The version of this tool is based on the following steps:
# https://packaging.python.org/guides/single-sourcing-package-version/
VERSION = {}

with open("./pymnp/__init__.py") as fp:
    # pylint: disable=W0122
    exec(fp.read(), VERSION)

setup(
    name="pymnp",
    author="Dr. Youri Hoogstrate",
    author_email="y.hoogstrate {at} erasmusmc dot nl",
    url="https://github.com/yhoogstrate/pymnp",
    description="pymnp: python api for the MolecularNeuropathology web portal",
    version=VERSION.get("__version__", "0.0.0"),
    scripts=['bin/api_example_download_all.py'],
    packages=find_packages(where=".", exclude=["tests"]),
    install_requires=["tqdm", "requests"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Programming Language :: Python :: 3.0",
        "Topic :: Utilities",
    ],
)
