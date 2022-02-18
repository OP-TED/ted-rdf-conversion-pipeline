from . import tester
from ted_sws.notice_packager.adapters import mets2create_mets_xml_generator as tpl_generator

TEST_TPL = "196390_2016_mets2create.mets.xml"


def test_tpl_generator():
    data = {
    }

    tester.test(tpl_generator, data, TEST_TPL)


