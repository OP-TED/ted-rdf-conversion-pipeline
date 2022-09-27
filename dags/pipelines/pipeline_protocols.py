from typing import Protocol

from ted_sws.core.model.notice import Notice


class NoticePipelineOutput:

    def __init__(self, notice: Notice, processed: bool = True, store_result: bool = True):
        self.notice = notice
        self.processed = processed
        self.store_result = store_result


class NoticePipelineCallable(Protocol):

    def __call__(self, notice: Notice) -> NoticePipelineOutput:
        """

        """
