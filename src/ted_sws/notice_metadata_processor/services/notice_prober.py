import io
from typing import List, Union
from xml.etree import ElementTree

from mapping_suite_sdk.mapping_suite.models import MappingSuite
from mapping_suite_sdk.mapping_suite.models.mapping_suite import DocumentProbingSpec
from pymongo import MongoClient
from saxonche import PySaxonProcessor

from src.ted_sws import config
from src.ted_sws.core.model.manifestation import XMLManifestation
from src.ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryMongoDB
from src.ted_sws.resources.mapping_files_registry import MappingSuiteConfigError


class NoticeProber:
    PROBE_MUST_EXIST = 'must_exist'
    PROBE_MUST_NOT_EXIST = 'must_not_exist'
    DEFAULT_XML_NS_PREFIX: str = ''

    def __init__(self, xml_manifestation: XMLManifestation, mongodb_client: MongoClient = None):
        self.xml = xml_manifestation.object_data
        if not mongodb_client:
            mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
        self.mapping_suite_repository = MappingSuiteRepositoryMongoDB(mongodb_client=mongodb_client)

    def get_mapping_suite(self) -> Union[MappingSuite, None]:
        mapping_suites: List[MappingSuite] = self.mapping_suite_repository.list()
        if not mapping_suites:
            raise MappingSuiteConfigError(
                "No MappingSuite found in the database. Please ensure at least one "
                "mapping suite is loaded before attempting the notice probing."
            )
        return next((ms for ms in mapping_suites if self.probe_document(ms)), None)

    def extract_namespaces(self, xml_content):
        """
        Extracts all namespaces from the XML string and returns a dict {prefix: uri}.
        """
        xml_file = io.StringIO(xml_content)
        namespaces = dict()
        for event, elem in ElementTree.iterparse(xml_file, events=('start-ns',)):
            ns, url = elem
            if ns == '':
                ns = self.DEFAULT_XML_NS_PREFIX
            if url:
                namespaces[ns] = url
        return namespaces

    @classmethod
    def extract_ns_prefixes_from_xpath(cls, xpath_expr):
        """
        Robustly extracts all namespace prefixes used in an XPath expression.
        Returns a set of prefixes (strings).
        Handles string literals and avoids function calls.
        """
        import re
        # Remove string literals (single and double quotes)
        xpath_expr = re.sub(r'("[^"]*"|\'[^"]*\')', '', xpath_expr)
        # Match prefixes before element/attribute names, not function calls
        # e.g., cbc:ID, ns:foo, but not local-name()
        pattern = r'(?<![a-zA-Z0-9_])([a-zA-Z_][\w\-]*)\:(?![\w\-]*\()'
        return set(re.findall(pattern, xpath_expr))

    def probe_document(self, mapping_suite: MappingSuite):
        """
        Probes the XML document using document_type_probing conditions from the mapping suite,
        using Saxon/Che for XPath evaluation.
        Returns True if all conditions are satisfied, False otherwise.
        """
        probing_conditions: List[DocumentProbingSpec] = (
                mapping_suite.mapping_suite_config.metadata_config.document_type_probing or []
        )

        if not probing_conditions:
            return False

        with (PySaxonProcessor(license=False) as proc):
            doc = proc.parse_xml(xml_text=self.xml)
            xpath_proc = proc.new_xpath_processor()
            xpath_proc.set_context(xdm_item=doc)

            # Extract and register namespaces
            namespaces = self.extract_namespaces(self.xml)
            for prefix, uri in namespaces.items():
                xpath_proc.declare_namespace(prefix, uri)

            for cond in probing_conditions:
                assert isinstance(
                    cond, DocumentProbingSpec
                ), "Each probing condition must be of DocumentProbingSpec type"
                expression = cond.formal_expression
                method = cond.probing_method

                # Check if all prefixes in the XPath are declared
                prefixes_in_xpath = self.extract_ns_prefixes_from_xpath(expression)
                if not prefixes_in_xpath.issubset(set(namespaces.keys())):
                    return False
                # Evaluate XPath
                result = xpath_proc.evaluate(expression)
                exists = bool(result and result.size > 0)
                if method == self.PROBE_MUST_EXIST and not exists:
                    return False
                if method == self.PROBE_MUST_NOT_EXIST and exists:
                    return False
        return True
