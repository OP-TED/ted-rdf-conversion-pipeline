#!/usr/bin/python3

# __init__.py
# Date:  07/02/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com
# Package PIP install location: https://github.com/meaningfy-ws/ted-sws/archive/main.zip
""" """

import codecs
import os
import pathlib
import re

from pkg_resources import parse_requirements
from setuptools import setup, find_packages

kwargs = {}

with pathlib.Path('requirements.txt').open() as requirements:
    kwargs["install_requires"] = [str(requirement) for requirement in parse_requirements(requirements)]

kwargs["tests_require"] = []
kwargs["extras_require"] = {
}


def find_version(filename):
    _version_re = re.compile(r'__version__ = "(.*)"')
    for line in open(filename):
        version_match = _version_re.match(line)
        if version_match:
            return version_match.group(1)


def open_local(paths, mode="r", encoding="utf8"):
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), *paths)
    return codecs.open(path, mode, encoding)


with open_local(["README.md"], encoding="utf-8") as readme:
    long_description = readme.read()

version = find_version("ted_sws/__init__.py")

packages = find_packages(exclude=("examples*", "test*"))

setup(
    name="ted_sws",
    version=version,
    description="TED SWS is an awesome system",
    author="Meaningfy",
    author_email="eugen@meaningfy.ws",
    maintainer="Meaningfy Team",
    maintainer_email="ted-sws@meaningfy.ws",
    url="https://github.com/meaningfy-ws/ted-sws",
    license="Apache License 2.0",
    platforms=["any"],
    python_requires=">=3.7",
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=packages,
    entry_points={
        "console_scripts": [
            "transformer = ted_sws.notice_transformer.entrypoints.cmd_mapping_suite_transformer:main",
            "normalisation_resource_generator = ted_sws.data_manager.entrypoints.generate_mapping_resources:main"
        ],
    },
    include_package_data=True,
    **kwargs,
)
