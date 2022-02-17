#!/usr/bin/python3

# mets_xml_dmd_rdf_generator.py
# Date:  11/02/2022
# Author: Kolea Plesco
# Email: kaleanych@gmail.com

""" """
from . import helper

TPL = 'mets2create_mets_xml.jinja2'


def generate_tpl(data):
    return helper.generate_tpl(TPL, data)

