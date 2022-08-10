from abc import ABC
from ted_sws.core.model.notice import Notice


class NoticePublisherABC(ABC):
    def upload(self, source_path, remote_path=None) -> bool:
        pass
