from ted_sws.domain.model.metadata import TEDMetadata


def test_metadata():
    metadata = TEDMetadata(**{"AA": "Value here", "No_key": "Value"})
    assert metadata.AA == "Value here"
    assert "No_key" not in metadata.dict().keys()
