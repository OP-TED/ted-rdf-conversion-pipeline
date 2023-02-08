from ted_sws.workbench_tools.notice_publisher.cli.cmd_s3_rdf_publisher import main as cli_main, run as cli_run


def test_cmd_s3_rdf_publisher(cli_runner, fake_mapping_suite_id, fake_repository_path, notice_rdf_s3_bucket_name,
                              fake_rdf_file, s3_publisher):
    notice_id1 = "292288-2021"
    notice_id2 = "348503-2021"
    object_name1 = f"object_name_for_{notice_id1}.ttl"
    object_name2 = f"object_name_for_{notice_id2}.ttl"
    object_name3 = f"object_name_for_rdf_file.ttl"

    response = cli_runner.invoke(cli_main, ["--mapping-suite-id", fake_mapping_suite_id, "--mappings-folder",
                                            fake_repository_path, "--notice-id", notice_id1, "--notice-id", notice_id2,
                                            "--object-name", object_name1, "--object-name", object_name2,
                                            "--object-name", object_name3, "--bucket-name", notice_rdf_s3_bucket_name,
                                            "--rdf-file", fake_rdf_file])
    assert response.exit_code == 0
    assert fake_mapping_suite_id in response.output
    assert "object_name_for_" in response.output
    assert notice_id1 in response.output
    assert notice_id2 in response.output
    assert "SUCCESS" in response.output

    cli_run(
        mapping_suite_id=fake_mapping_suite_id,
        bucket_name=notice_rdf_s3_bucket_name,
        s3_publisher=s3_publisher,
        skip_notice_id=[],
        mappings_folder=fake_repository_path
    )

    for obj in s3_publisher.client.list_objects(notice_rdf_s3_bucket_name):
        assert s3_publisher.is_published(bucket_name=notice_rdf_s3_bucket_name, object_name=obj.object_name)
        s3_publisher.remove_object(bucket_name=notice_rdf_s3_bucket_name, object_name=obj.object_name)

    s3_publisher.remove_bucket(bucket_name=notice_rdf_s3_bucket_name)
