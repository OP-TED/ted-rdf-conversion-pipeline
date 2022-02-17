#!/usr/bin/python3

# mets_xml_dmd_rdf_generator.py
# Date:  11/02/2022
# Author: Kolea Plesco
# Email: kaleanych@gmail.com

""" """
from . import TEMPLATES


def generate_tpl(tpl, data):
    tpl = TEMPLATES.get_template(tpl)
    tpl_render = tpl.render(data)
    return tpl_render

