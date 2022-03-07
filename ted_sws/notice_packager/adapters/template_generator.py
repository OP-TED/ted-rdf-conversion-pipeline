#!/usr/bin/python3

# template_generator.py
# Date:  11/02/2022
# Author: Kolea PLESCO
# Email: kalean.bl@gmail.com

"""
This module provides template generators for all needed package templates,
that must be uploaded.
"""
from . import TEMPLATES
from ted_sws.notice_packager.model.metadata import validate_notice_action_type
from typing import Dict


class TemplateGenerator:
    def __init__(self, data: Dict):
        self.data = data

    def __generate_template(self, template):
        template_render = TEMPLATES.get_template(template).render(self.data)
        return template_render

    def mets_xml_dmd_rdf_generator(self):
        template = 'mets_xml_dmd_rdf.jinja2'
        return self.__generate_template(template)

    def tmd_rdf_generator(self):
        template = 'tmd_rdf.jinja2'
        return self.__generate_template(template)

    def mets2action_mets_xml_generator(self):
        action = self.data["notice"]["action"]["type"]
        validate_notice_action_type(action)

        template = 'mets2action_mets_xml.jinja2'
        return self.__generate_template(template)
