import pytest

from test.fakes.fake_dag_context import FakeDAGContext


@pytest.fixture
def fake_dag_context() -> FakeDAGContext:
    return FakeDAGContext()


@pytest.fixture
def notice_id() -> str:
    return "NOTICE_ID"


@pytest.fixture
def mapping_package_id() -> str:
    return "MAPPING_PACKAGE_ID"
