from typing import Any, List, Dict, Optional

from airflow.operators.python import get_current_context

from src.dags import TEDSWSPipelineDAGException
from src.ted_sws.core.model.notice import NoticeStatus

TASK_INSTANCE = "ti"


def select_first_non_none(data):
    """

    :param data:
    :return:
    """
    return next((item for item in data if item is not None), None)


def pull_dag_upstream(key, task_ids=None):
    """

    :param key:
    :param task_ids:
    :return:
    """
    context = get_current_context()
    return select_first_non_none(
        context[TASK_INSTANCE].xcom_pull(key=str(key),
                                         task_ids=task_ids if task_ids else context['task'].upstream_task_ids))


def push_dag_downstream(key, value):
    """
    
    :param key:
    :param value:
    :return:
    """
    context = get_current_context()
    return context[TASK_INSTANCE].xcom_push(key=str(key), value=value)


def smart_xcom_pull(key: str):
    context = get_current_context()
    task_id = context[TASK_INSTANCE].task_id
    selected_upstream_task_ids = [selected_task_id
                                  for selected_task_id in context[TASK_INSTANCE].xcom_pull(key=task_id,
                                                                                           task_ids=context[
                                                                                               'task'].upstream_task_ids)
                                  if selected_task_id
                                  ]
    if selected_upstream_task_ids:
        return select_first_non_none(context[TASK_INSTANCE].xcom_pull(key=key, task_ids=selected_upstream_task_ids))
    return None


def smart_xcom_push(key: str, value: Any, destination_task_id: str = None):
    context = get_current_context()
    current_task_id = context[TASK_INSTANCE].task_id
    task_ids = [destination_task_id] if destination_task_id else context['task'].downstream_task_ids
    for task_id in task_ids:
        context[TASK_INSTANCE].xcom_push(key=task_id, value=current_task_id)
    context[TASK_INSTANCE].xcom_push(key=key, value=value)


def smart_xcom_forward(key: str, destination_task_id: str = None):
    value = smart_xcom_pull(key=key)
    if value:
        smart_xcom_push(key=key, value=value, destination_task_id=destination_task_id)


def get_dag_param(key: str, raise_error: bool = False, default_value: Any = None):
    """

    """
    context = get_current_context()
    dag_params = context["dag_run"].conf
    if key in dag_params.keys():
        return dag_params[key]
    if raise_error:
        raise Exception(f"Config key [{key}] is not present in dag context")
    return default_value


def parse_notice_statuses_from_string(variable: str) -> List[NoticeStatus]:
    """
    Parses and validates a string containing newline-separated notice statuses, converting them to NoticeStatus enum values.

    :param variable: A string with notice status names separated by newlines
    :return: A list of NoticeStatus enum values
    :raises TEDSWSPipelineDAGException: If the string contains invalid notice status names

    Example input: "PUBLISHED\nINELIGIBLE_FOR_TRANSFORMATION"
    """

    error_message: str = 'Use newline-separated notice status names.\nExample: "PUBLISHED\\nINELIGIBLE_FOR_TRANSFORMATION"'

    if not isinstance(variable, str):
        raise TEDSWSPipelineDAGException(f"Expected string input, got {type(variable).__name__}.\n{error_message}")

    # Split by newlines and clean up each line
    notice_statuses_list = [line.strip() for line in variable.split('\n') if line.strip()]

    if not notice_statuses_list:
        raise TEDSWSPipelineDAGException(f"No valid notice status names found in input.\n{error_message}")

    validated_statuses = []
    for item in notice_statuses_list:
        try:
            validated_statuses.append(NoticeStatus[item])
        except KeyError:
            raise TEDSWSPipelineDAGException(f"Invalid notice status name: '{item}'\n{error_message}")

    return validated_statuses


def has_notices_with_failure_status(notices_status: Dict[str, NoticeStatus],
                                    success_statuses: List[NoticeStatus]) -> bool:
    """
    Check if any notices have a status that is not in the list of success statuses.

    This function determines if there are any notices with statuses that are considered failures
    by comparing the set of actual notice statuses against the provided set of success statuses.

    Args:
        notices_status (Dict[str, NoticeStatus]): A dictionary mapping notice identifiers to their status
        success_statuses (List[NoticeStatus]): A list of statuses that are considered successful

    Returns:
        bool: True if any notice has a status that is not in the success_statuses list,
              False if all notices have statuses that are in the success_statuses list

    Example:
        If success_statuses = [NoticeStatus.PUBLISHED, NoticeStatus.INELIGIBLE_FOR_TRANSFORMATION],
        and a notice has NoticeStatus.RAW, the function will return True.
    """
    return len(set(notices_status.values()) - set(success_statuses)) > 0


def is_last_active_dag_run(session,
                           dagrun_model,
                           dag_id: str,
                           running_state: str = "running",
                           queued_state: str = "queued") -> bool:
    """
    Check if the given DAG is on its last active run in the system, defined as:
      - number of running DagRuns for dag_id is == 1
      - number of queued DagRuns for dag_id is == 0

    This function is intentionally generic — the caller provides the SQLAlchemy session
    and the DagRun model (to avoid importing Airflow internals here), along with the
    target dag_id and optional state names.

    Args:
        session: SQLAlchemy session to use for queries.
        dagrun_model: Airflow DagRun model class (e.g., airflow.models.DagRun).
        dag_id: The DAG ID to check.
        running_state: The value representing a running state. Default: "running".
        queued_state: The value representing a queued state. Default: "queued".

    Returns:
        bool: True if it's the last active run (<=1 running and 0 queued), False otherwise.
    """
    running_count = session.query(dagrun_model).filter(
        dagrun_model.dag_id == dag_id, dagrun_model.state == running_state
    ).count()
    queued_count = session.query(dagrun_model).filter(
        dagrun_model.dag_id == dag_id, dagrun_model.state == queued_state
    ).count()
    return running_count == 1 and queued_count == 0


def trigger_dag(
        dag_id: str,
        conf: Optional[Dict[str, Any]] = None,
        run_id: Optional[str] = None,
        execution_date: Optional[str] = None,
        replace_microseconds: bool = True,
):
    """
    Trigger a DAG run using Airflow's local API client.

    Args:
        dag_id: ID of the DAG to trigger.
        conf: Optional configuration dict for the DAG run.
        run_id: Optional custom run_id.
        execution_date: Optional execution date (ISO format string). If omitted, Airflow sets now().
        replace_microseconds: Whether to strip microseconds from execution_date when provided.

    Returns:
        The response returned by the Airflow client (may vary by version).

    Raises:
        Any exception raised by the Airflow client will propagate to the caller.
    """

    from airflow.api.client.local_client import Client

    client = Client(api_base_url=None, auth=None)
    return client.trigger_dag(
        dag_id=dag_id,
        conf=conf,
        run_id=run_id,
        execution_date=execution_date,
        replace_microseconds=replace_microseconds,
    )
