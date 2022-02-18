#!/usr/bin/python3

# mets_xml_dmd_rdf_generator.py
# Date:  11/02/2022
# Author: Kolea Plesco
# Email: kaleanych@gmail.com

""" """
from . import tpl_generator

TPL = 'mets_xml_dmd_rdf.jinja2'


def generate_tpl(data):
    return tpl_generator.generate_tpl(TPL, data)

