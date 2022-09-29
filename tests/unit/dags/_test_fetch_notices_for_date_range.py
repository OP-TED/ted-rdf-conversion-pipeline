from dags.fetch_notices_for_date_range import generate_daily_dates, generate_wild_card_by_date


def test_fetch_notices_for_date_range(dag_bag):
    assert dag_bag.import_errors == {}
    dag = dag_bag.get_dag(dag_id="fetch_notices_for_date_range")
    assert dag is not None
    assert dag.has_task("trigger_fetch_notices_workers_for_date_range")


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
