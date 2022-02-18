from . import tester
from ted_sws.notice_packager.adapters import tmd_rdf_generator as tpl_generator

TEST_TPL = "techMDID001.tmd.rdf"


def test_tpl_generator():
    data = {
    }

    tester.test(tpl_generator, data, TEST_TPL)


