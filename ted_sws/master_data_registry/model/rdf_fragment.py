#!/usr/bin/python3

# rdf_fragment.py
# Date:  29.07.2022
# Author: Stratulat Ștefan
# Email: stefan.stratulat1997@gmail.com
from typing import List, Tuple

from rdflib.term import URIRef

from ted_sws.core.model import PropertyBaseModel


class RDFFragment(PropertyBaseModel):
    """
        This class is used to store an RDFFragment.
    """
    rdf_content: str
    sparql_query: str
    rdf_fragment_triples: List[Tuple[URIRef, URIRef, URIRef]]


