#!/usr/bin/python3

# metadata_transformer.py
# Date:  22/02/2022
# Author: Kolea PLESCO
# Email: kalean.bl@gmail.com

"""
This module provides transformers of notice metadata (original or normalized)
into data structures needed to render the templates.
This transformed metadata is what adapters expect.
"""
import abc

from ted_sws.domain.model.metadata import NormalisedMetadata
from ted_sws.notice_packager.model.metadata import PackagerMetadata
from typing import Dict


class MetadataTransformer:
    def __init__(self, normalised_metadata: NormalisedMetadata):
        self.normalised_metadata = normalised_metadata

    def template_metadata(self) -> Dict:
        return PackagerMetadata.from_normalised_metadata(self.normalised_metadata)
