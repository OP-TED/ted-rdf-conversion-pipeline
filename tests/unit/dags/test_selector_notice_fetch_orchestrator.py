from dags.notice_fetch_and_load_in_mongodb import generate_daily_dates, generate_wild_card_by_date


def test_selector_notice_fetch_orchestrator(dag_bag):
    assert dag_bag.import_errors == {}
    dag = dag_bag.get_dag(dag_id="selector_notice_fetch_orchestrator")
    assert dag is not None
    assert dag.has_task("fetch_notice_from_ted")


def test_generate_daily_dates():
    start_date = "20200202"
    end_date = "20200202"
    dates = generate_daily_dates(start_date=start_date, end_date=end_date)

    assert isinstance(dates, list)
    assert len(dates) == 1
    assert "20200202" in dates

    start_date = "20200202"
    end_date = "20200205"
    dates = generate_daily_dates(start_date=start_date, end_date=end_date)
    assert len(dates) == 4
    assert "20200202" in dates


def test_generate_wild_card_by_date():
    assert "20200202*" == generate_wild_card_by_date(date="20200202")
