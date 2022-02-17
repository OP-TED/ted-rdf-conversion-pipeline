#!/usr/bin/python3

# __init__.py

from jinja2 import Environment, PackageLoader

TEMPLATES = Environment(loader=PackageLoader("ted_sws.notice_packager.resources", "templates"))