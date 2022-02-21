import json
import xml.etree.ElementTree as ET

import xmltodict

from ted_sws.notice_fetcher.services.notice_fetcher import NoticeFetcher


def test_somethig():
    myDoc = ET.parse("2022-OJS033-086071.xml")
    root = myDoc.getroot()
    ceva = root.find("./")
    print(root.findall("./CODED_DATA_SECTION/"))


def test_from_string(ted_document_search):
    document_id = "067623-2022"
    notice = NoticeFetcher(ted_api_adapter=ted_document_search).get_notice_by_id(
        document_id=document_id)

    xml_content = notice.xml_manifestation.object_data

    doc_root = ET.fromstring(xml_content)

    print(doc_root.findall("./TECHNICAL_SECTION/RECEPTION_ID"))

    xml_dict = xmltodict.parse(xml_content)
    print(type(xml_dict))

    notice_pub_no = xml_dict["TED_EXPORT"]["@DOC_ID"]
    print(notice_pub_no)


def test_extract_metadata(ted_document_search):
    document_id = "067623-2022"
    notice = NoticeFetcher(ted_api_adapter=ted_document_search).get_notice_by_id(
        document_id=document_id)

    xml_manifestation = notice.xml_manifestation.object_data

    xml_manifestation_dict = xmltodict.parse(xml_manifestation)

    dict = {
        # "title": xml_manifestation_dict["TED_EXPORT"]["TRANSLATION_SECTION"]["ML_TITLES"]["ML_TI_DOC"][0],
        "notice_publication_number": xml_manifestation_dict["TED_EXPORT"]["@DOC_ID"],
        "publication_date": xml_manifestation_dict["TED_EXPORT"]["CODED_DATA_SECTION"]["REF_OJS"]["DATE_PUB"],
        "ojs_issue_number": xml_manifestation_dict["TED_EXPORT"]["CODED_DATA_SECTION"]["REF_OJS"]["NO_OJ"],
        # "city_of_buyer":
        #     xml_manifestation_dict["TED_EXPORT"]["FORM_SECTION"]["CONTRACT_DEFENCE"]["FD_CONTRACT_DEFENCE"][
        #         "CONTRACTING_AUTHORITY_INFORMATION_DEFENCE"]["NAME_ADDRESSES_CONTACT_CONTRACT"][
        #         "CA_CE_CONCESSIONAIRE_PROFILE"]["TOWN"],
        # "name_of_buyer": FORM SECTION,
        "original_language": xml_manifestation_dict["TED_EXPORT"]["CODED_DATA_SECTION"]["NOTICE_DATA"]["LG_ORIG"],
        # "country_of_buyer": None,
        "type_of_buyer": f'{xml_manifestation_dict["TED_EXPORT"]["CODED_DATA_SECTION"]["CODIF_DATA"]["AA_AUTHORITY_TYPE"]["@CODE"]}-{xml_manifestation_dict["TED_EXPORT"]["CODED_DATA_SECTION"]["CODIF_DATA"]["AA_AUTHORITY_TYPE"]["#text"]}',
        # "eu_institution": None,
        "document_sent_date": xml_manifestation_dict["TED_EXPORT"]["CODED_DATA_SECTION"]["CODIF_DATA"]["DS_DATE_DISPATCH"],
        # "deadline_for_submission": xml_manifestation_dict["TED_EXPORT"]["CODED_DATA_SECTION"]["CODIF_DATA"]["DT_DATE_FOR_SUBMISSION"],
        "type_of_contract": xml_manifestation_dict["TED_EXPORT"]["CODED_DATA_SECTION"]["CODIF_DATA"]["NC_CONTRACT_NATURE"],
        "type_of_procedure": xml_manifestation_dict["TED_EXPORT"]["CODED_DATA_SECTION"]["CODIF_DATA"]["PR_PROC"],
        "notice_type": xml_manifestation_dict["TED_EXPORT"]["CODED_DATA_SECTION"]["CODIF_DATA"]["TD_DOCUMENT_TYPE"]["#text"],
        "regulation": xml_manifestation_dict["TED_EXPORT"]["CODED_DATA_SECTION"]["CODIF_DATA"]["RP_REGULATION"]["#text"],
        "type_of_bid": xml_manifestation_dict["TED_EXPORT"]["CODED_DATA_SECTION"]["CODIF_DATA"]["TY_TYPE_BID"]["#text"],
        "award_criteria": xml_manifestation_dict["TED_EXPORT"]["CODED_DATA_SECTION"]["CODIF_DATA"]["AC_AWARD_CRIT"]["#text"],
        "common_procurement": xml_manifestation_dict["TED_EXPORT"]["CODED_DATA_SECTION"]["NOTICE_DATA"]["ORIGINAL_CPV"],
        "place_of_performance": xml_manifestation_dict["TED_EXPORT"]["CODED_DATA_SECTION"]["NOTICE_DATA"]["n2021:PERFORMANCE_NUTS"]["@CODE"],
        "internet_address": None,
        "legal_basis_directive": None}

    print(dict)
