import pytest

from tests.fakes.fake_dag_context import FakeDAGContext


@pytest.fixture
def fake_dag_context() -> FakeDAGContext:
    return FakeDAGContext()
