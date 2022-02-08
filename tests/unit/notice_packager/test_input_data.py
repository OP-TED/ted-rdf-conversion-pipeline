#!/usr/bin/python3

# test_input_data.py
# Date:  07/02/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """


def test_sample_metadata(sample_metadata):
    print(sample_metadata)
    assert sample_metadata.title
    assert sample_metadata.author == "http://publications.europa.eu/resource/authority/corporate_body/PUBL"


def test_sample_content(sample_rdf):
    print()
