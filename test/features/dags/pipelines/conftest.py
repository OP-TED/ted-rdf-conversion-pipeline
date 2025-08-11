from typing import List

import pytest

from src.ted_sws.core.model.notice import Notice


@pytest.fixture
def dummy_list_of_3_notices_to_be_published(publish_eligible_notice) -> List[Notice]:
    list_of_notices: List[Notice] = []

    for i in range(3):
        notice = publish_eligible_notice.model_copy(deep=True, update={'ted_id': f"test_notice {i}"})
        list_of_notices.append(notice)

    return list_of_notices
