import pytest
from airflow.models import DagBag
from airflow.utils.state import DagRunState

from src.dags import TEDSWSPipelineDAGException
from src.dags.dags_utils import (
    parse_notice_statuses_from_string,
    has_notices_with_failure_status,
    is_last_active_dag_run,
    trigger_dag,
)
from src.ted_sws.core.model.notice import NoticeStatus


def test_validate_notice_statuses_string_variable():
    # Valid inputs with multiple statuses
    assert parse_notice_statuses_from_string('INELIGIBLE_FOR_TRANSFORMATION\nPUBLISHED') == [
        NoticeStatus.INELIGIBLE_FOR_TRANSFORMATION, NoticeStatus.PUBLISHED]

    # Valid input with extra whitespace
    assert parse_notice_statuses_from_string('  INELIGIBLE_FOR_TRANSFORMATION  \n  PUBLISHED  ') == [
        NoticeStatus.INELIGIBLE_FOR_TRANSFORMATION, NoticeStatus.PUBLISHED]

    # Single status
    assert parse_notice_statuses_from_string('PUBLISHED') == [NoticeStatus.PUBLISHED]

    # Valid input with empty lines (should be filtered out)
    assert parse_notice_statuses_from_string('INELIGIBLE_FOR_TRANSFORMATION\n\nPUBLISHED\n') == [
        NoticeStatus.INELIGIBLE_FOR_TRANSFORMATION, NoticeStatus.PUBLISHED]

    # Empty string should raise exception
    with pytest.raises(TEDSWSPipelineDAGException):
        parse_notice_statuses_from_string('')

    # String with only whitespace should raise exception
    with pytest.raises(TEDSWSPipelineDAGException):
        parse_notice_statuses_from_string('   \n  \n  ')

    # Invalid status name should raise exception
    with pytest.raises(TEDSWSPipelineDAGException):
        parse_notice_statuses_from_string('INELIGIBLE_FOR_TRANSFORMATION\nINVALID_STATUS')

    # Non-string input should raise exception
    with pytest.raises(TEDSWSPipelineDAGException):
        parse_notice_statuses_from_string(['INELIGIBLE_FOR_TRANSFORMATION', 'PUBLISHED'])

    # Non-string input (number) should raise exception
    with pytest.raises(TEDSWSPipelineDAGException):
        parse_notice_statuses_from_string(123)


def test_has_notices_with_failure_status():
    # All notices have success statuses
    notices_status = {"notice1": NoticeStatus.PUBLISHED, "notice2": NoticeStatus.TRANSFORMED}
    success_statuses = [NoticeStatus.PUBLISHED, NoticeStatus.TRANSFORMED]
    assert has_notices_with_failure_status(notices_status, success_statuses) is False

    # Some notices have failure statuses
    notices_status = {"notice1": NoticeStatus.PUBLISHED, "notice2": NoticeStatus.RAW}
    success_statuses = [NoticeStatus.PUBLISHED, NoticeStatus.TRANSFORMED]
    assert has_notices_with_failure_status(notices_status, success_statuses) is True


def test_is_last_active_dag_run_true_when_one_running_zero_queued(dag_bag: DagBag):
    # Use a real DAG from the dag_bag and real Airflow session/model instead of fakes
    from airflow.models import DagRun
    from airflow.utils.session import create_session
    from datetime import datetime, timezone

    dag_id = next(iter(dag_bag.dags.keys()))

    with create_session() as session:
        session.query(DagRun).filter(DagRun.dag_id == dag_id).delete()
        session.commit()

        dr_running = DagRun(
            dag_id=dag_id,
            run_id="test_run_running",
            state=DagRunState.RUNNING,
            execution_date=datetime.now(timezone.utc),
            run_type="manual",
        )
        session.add(dr_running)
        session.commit()

        assert is_last_active_dag_run(session=session, dagrun_model=DagRun, dag_id=dag_id) is True


def test_is_last_active_dag_run_false_when_multiple_running_or_any_queued(dag_bag):
    from airflow.models import DagRun
    from airflow.utils.session import create_session
    from datetime import datetime, timezone, timedelta

    dag_id = next(iter(dag_bag.dags.keys()))

    with create_session() as session:
        session.query(DagRun).filter(DagRun.dag_id == dag_id).delete()
        session.commit()

        now = datetime.now(timezone.utc)

        session.add_all([
            DagRun(dag_id=dag_id, run_id="run_running_1", state=DagRunState.RUNNING,
                   execution_date=now - timedelta(minutes=1),
                   run_type="manual"),
            DagRun(dag_id=dag_id, run_id="run_running_2", state=DagRunState.RUNNING, execution_date=now,
                   run_type="manual"),
        ])
        session.commit()
        assert is_last_active_dag_run(session=session, dagrun_model=DagRun, dag_id=dag_id) is False

        session.query(DagRun).filter(DagRun.dag_id == dag_id).delete()
        session.commit()

        session.add_all([
            DagRun(dag_id=dag_id, run_id="run_running", state=DagRunState.RUNNING, execution_date=now,
                   run_type="manual"),
            DagRun(dag_id=dag_id, run_id="run_queued_1", state=DagRunState.QUEUED,
                   execution_date=now + timedelta(minutes=1),
                   run_type="manual"),
        ])
        session.commit()
        assert is_last_active_dag_run(session=session, dagrun_model=DagRun, dag_id=dag_id) is False


def test_trigger_dag_forwards_params_and_returns_response(dag_bag):
    # Use a real DAG from the dag_bag and verify a DagRun is created with given parameters
    from airflow.models import DagRun
    from airflow.utils.session import create_session
    from airflow.utils.state import DagRunState
    from datetime import datetime, timezone
    from airflow.models.serialized_dag import SerializedDagModel

    dag_id = next(iter(dag_bag.dags.keys()))
    dag = dag_bag.get_dag(dag_id)
    dag.sync_to_db()

    SerializedDagModel.write_dag(dag)

    with create_session() as session:
        session.query(DagRun).filter(DagRun.dag_id == dag_id).delete()
        session.commit()

    conf = {"a": 1}
    run_id = "manual__123"
    execution_date_dt = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)

    trigger_dag(
        dag_id=dag_id,
        conf=conf,
        run_id=run_id,
        execution_date=execution_date_dt,
        replace_microseconds=False,
    )

    with create_session() as session:
        runs = session.query(DagRun).filter(DagRun.dag_id == dag_id).all()
        assert len(runs) == 1
        dr = runs[0]
        assert dr.run_id == run_id
        assert dr.conf == conf
        assert dr.execution_date.replace(tzinfo=timezone.utc).isoformat().startswith("2024-01-01T00:00:00+")
        assert dr.state in {DagRunState.RUNNING, DagRunState.QUEUED, DagRunState.SUCCESS, DagRunState.FAILED}


def test_trigger_dag_defaults(dag_bag):
    from airflow.models import DagRun
    from airflow.utils.session import create_session

    dag_id = next(iter(dag_bag.dags.keys()))
    dag = dag_bag.get_dag(dag_id)
    dag.sync_to_db()
    from airflow.models.serialized_dag import SerializedDagModel
    SerializedDagModel.write_dag(dag)

    with create_session() as session:
        session.query(DagRun).filter(DagRun.dag_id == dag_id).delete()
        session.commit()

    trigger_dag(dag_id=dag_id)

    with create_session() as session:
        runs = session.query(DagRun).filter(DagRun.dag_id == dag_id).order_by(DagRun.execution_date.desc()).all()
        assert len(runs) == 1
        dr = runs[0]
        assert isinstance(dr.run_id, str) and len(dr.run_id) > 0
        assert isinstance(dr.conf, dict)
        assert dr.execution_date is not None

    notices_status = {"notice1": NoticeStatus.RAW, "notice2": NoticeStatus.INELIGIBLE_FOR_TRANSFORMATION}
    success_statuses = [NoticeStatus.PUBLISHED, NoticeStatus.TRANSFORMED]
    assert has_notices_with_failure_status(notices_status, success_statuses) is True

    notices_status = {}
    success_statuses = [NoticeStatus.PUBLISHED, NoticeStatus.TRANSFORMED]
    assert has_notices_with_failure_status(notices_status, success_statuses) is False

    notices_status = {"notice1": NoticeStatus.PUBLISHED, "notice2": NoticeStatus.TRANSFORMED}
    success_statuses = []
    assert has_notices_with_failure_status(notices_status, success_statuses) is True
