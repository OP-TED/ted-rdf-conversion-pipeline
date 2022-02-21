#!/usr/bin/python3

# mets_xml_dmd_rdf_generator.py
# Date:  11/02/2022
# Author: Kolea Plesco
# Email: kaleanych@gmail.com

"""
This module provides template generators for all needed package templates,
that must be uploaded.
"""
from . import TEMPLATES

ACCEPTED_ACTIONS = ["create", "update"]


def __generate_template(template, data):
    template_render = TEMPLATES.get_template(template).render(data)
    return template_render


def mets_xml_dmd_rdf_generator(data):
    template = 'mets_xml_dmd_rdf.jinja2'
    return __generate_template(template, data)


def tmd_rdf_generator(data):
    template = 'tmd_rdf.jinja2'
    return __generate_template(template, data)


def mets2action_mets_xml_generator(data):
    action = data["notice"]["action"]["type"]
    if action not in ACCEPTED_ACTIONS:
        raise ValueError('No such action: %s' % action)

    template = 'mets2action_mets_xml.jinja2'
    return __generate_template(template, data)
