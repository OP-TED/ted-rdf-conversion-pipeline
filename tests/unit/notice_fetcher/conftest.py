import pathlib

import pytest as pytest


@pytest.fixture(scope="session")
def xml_notice():
    return get_xml_notice()


def get_xml_notice():
    path = pathlib.Path(__file__).parent.parent.parent / "test_data" / "notices" / "2021-OJS237-623049.xml"
    return path.read_text()

