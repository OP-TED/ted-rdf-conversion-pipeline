import semantic_version

from ted_sws.mapping_suite_processor.services.mapping_suite_validation_service import validate_mapping_suite


def test_validate_mapping_suite(mapping_suite):
    assert validate_mapping_suite(mapping_suite)


def test_semantic_versioning():
    assert semantic_version.Version("1.0.0") > semantic_version.Version("0.0.1")
    assert semantic_version.Version("1.0.0") > semantic_version.Version("0.1.0")
    assert semantic_version.Version("1.0.0") > semantic_version.Version("1.0.0-rc.1")
    assert semantic_version.Version("1.0.0") > semantic_version.Version("1.0.0-beta.11")
    assert semantic_version.Version("1.0.0") > semantic_version.Version("1.0.0-alpha.1")
    assert semantic_version.Version("1.0.0") > semantic_version.Version("1.0.0-alpha.beta")
    assert semantic_version.Version("1.0.0") > semantic_version.Version("1.0.0-alpha")
    assert semantic_version.Version("1.0.0") > semantic_version.Version("1.0.0-0.3.7")
    assert semantic_version.Version("1.0.0") > semantic_version.Version("1.0.0-x.7.z.92")
    assert semantic_version.Version("1.0.0") > semantic_version.Version("1.0.0-x-y-z.-")
    assert semantic_version.Version("1.0.0") > semantic_version.Version("1.0.0-alpha+001")
    assert semantic_version.Version("2.1.1") > semantic_version.Version("2.1.1-rc.1")
    assert semantic_version.Version("2.1.1-TDArc.2") > semantic_version.Version("2.1.1-TDArc.1")
    assert semantic_version.Version("2.1.2-rc.1") > semantic_version.Version("2.1.2-beta.1")
    assert semantic_version.Version("2.1.2-beta.1") > semantic_version.Version("2.1.2-alpha.1")
    assert semantic_version.Version("2.1.2-alpha.1") > semantic_version.Version("2.1.2-TDArc.1")
