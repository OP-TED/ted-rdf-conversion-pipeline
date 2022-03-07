from ted_sws.notice_packager.model.metadata import NoticeMetadata, WorkMetadata, ExpressionMetadata, \
    ManifestationMetadata


def test_notice_metadata(sample_notice):
    md = NoticeMetadata(**sample_notice)
    print(md.dict())


def test_work_metadata(sample_work):
    md = WorkMetadata(**sample_work)
    print(md.dict())


def test_expression_metadata(sample_expression):
    md = ExpressionMetadata(**sample_expression)
    print(md.dict())


def test_manifestation_metadata(sample_manifestation):
    md = ManifestationMetadata(**sample_manifestation)
    print(md.dict())


# def test_work_metadata(sample_work):
#     # work = WorkMetadata(**sample_work)
#     work = WorkMetadata(do_not_index=False)
#     # work.do_not_index = False
#     # print(work.dict())
#
#     # assert work.do_not_index == sample_work["do_not_index"]
#     # assert work.work_created_by_agent == sample_work["work_created_by_agent"]
