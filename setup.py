#!/usr/bin/python3

# __init__.py
# Date:  07/02/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com
# Package PIP install location: https://github.com/OP-TED/ted-rdf-conversion-pipeline/archive/main.zip
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
    url="https://github.com/OP-TED/ted-rdf-conversion-pipeline",
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
            "resources_injector = ted_sws.mapping_suite_processor.entrypoints.cli.cmd_resources_injector:main",
            "rml_modules_injector = ted_sws.mapping_suite_processor.entrypoints.cli.cmd_rml_modules_injector:main",
            "sparql_generator = ted_sws.mapping_suite_processor.entrypoints.cli.cmd_sparql_generator:main",
            "rml_report_generator = ted_sws.rml_to_html.entrypoints.cli.cmd_rml_report_generator:main",
            "mapping_runner = ted_sws.notice_transformer.entrypoints.cli.cmd_mapping_runner:main",
            "xpath_coverage_runner = ted_sws.notice_validator.entrypoints.cli.cmd_xpath_coverage_runner:main",
            "sparql_runner = ted_sws.notice_validator.entrypoints.cli.cmd_sparql_runner:main",
            "shacl_runner = ted_sws.notice_validator.entrypoints.cli.cmd_shacl_runner:main",
            "validation_summary_runner = ted_sws.notice_validator.entrypoints.cli.cmd_validation_summary_runner:main",
            "triple_store_loader = ted_sws.mapping_suite_processor.entrypoints.cli.cmd_triple_store_loader:main",
            "mapping_suite_validator = ted_sws.mapping_suite_processor.entrypoints.cli.cmd_mapping_suite_validator:main",
            "metadata_generator = ted_sws.mapping_suite_processor.entrypoints.cli.cmd_metadata_generator:main",
            "conceptual_mapping_differ = ted_sws.mapping_suite_processor.entrypoints.cli.cmd_conceptual_mapping_differ:main",
            "rdf_differ = ted_sws.rdf_differ.entrypoints.cli.cmd_rdf_differ:main",

            "mapping_suite_processor = ted_sws.mapping_suite_processor.entrypoints.cli.cmd_mapping_suite_processor:main",
            "yarrrml2rml_converter = ted_sws.mapping_suite_processor.entrypoints.cli.cmd_yarrrml2rml_converter:main",
            "normalisation_resource_generator = ted_sws.data_manager.entrypoints.cli.cmd_generate_mapping_resources:main",
            "s3_rdf_publisher = ted_sws.notice_publisher.entrypoints.cli.cmd_s3_rdf_publisher:main",
            "bulk_packager = ted_sws.notice_packager.entrypoints.cli.cmd_bulk_packager:main",
            "api-digest_service-start-server = ted_sws.notice_transformer.entrypoints.api.digest_service.server:api_server_start",
            "rdf_component_detector = ted_sws.rdf_component_detector.entrypoints.cli.cmd_rdf_component_detector:main"
        ],
    },
    include_package_data=True,
    **kwargs,
)
