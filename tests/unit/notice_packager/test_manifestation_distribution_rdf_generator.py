from . import helper
from ted_sws.notice_packager.adapters import manifestation_distribution_rdf_generator as tpl_generator

TEST_TPL = "196390_2016.rdf"


def test_tpl_generator():
    data = {
    }

    helper.test(tpl_generator, data, TEST_TPL)




