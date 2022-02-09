#!/usr/bin/python3

# metadata.py
# Date:  09/02/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
from ted_sws.domain.model import PropertyBaseModel


class Metadata(PropertyBaseModel):
    ...


class TEDMetadata(Metadata):
    AA: str = None
