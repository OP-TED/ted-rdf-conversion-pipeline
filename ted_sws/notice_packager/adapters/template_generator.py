#!/usr/bin/python3

# template_generator.py
# Date:  11/02/2022
# Author: Kolea PLESCO
# Email: kalean.bl@gmail.com

"""
This module provides template generators for all needed package templates.
"""

from jinja2 import Environment, PackageLoader

from ted_sws.notice_packager.model.metadata import PackagerMetadata, validate_notice_action_type

TEMPLATES = Environment(loader=PackageLoader("ted_sws.notice_packager.resources", "templates"))


class TemplateGenerator:
    @classmethod
    def __generate_template(cls, template, data: PackagerMetadata = None):
        template_render = TEMPLATES.get_template(template).render(data.dict())
        return template_render

    @classmethod
    def mets_xml_dmd_rdf_generator(cls, data: PackagerMetadata = None):
        template = 'mets_xml_dmd_rdf.jinja2'
        return cls.__generate_template(template, data)

    @classmethod
    def tmd_rdf_generator(cls, data: PackagerMetadata = None):
        template = 'tmd_rdf.jinja2'
        return cls.__generate_template(template, data)

    @classmethod
    def mets2action_mets_xml_generator(cls, data: PackagerMetadata = None):
        action = data.notice.action.type
        validate_notice_action_type(action)

        template = 'mets2action_mets_xml.jinja2'
        return cls.__generate_template(template, data)
