import json
from typing import Any, List

from airflow.operators.python import get_current_context

from dags import TEDSWSPipelineDAGException
from ted_sws.core.model.notice import NoticeStatus

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


def validate_notice_statuses_json_variable(variable: str) -> List[NoticeStatus]:
    error_message: str = 'Use json valid structure.\nExample: ["PUBLISHED", "INELIGIBLE_FOR_TRANSFORMATION"]'
    try:
        notice_statuses_list = json.loads(variable)
    except json.JSONDecodeError as e:
        raise TEDSWSPipelineDAGException(f"{e}\n{error_message}")

    if not isinstance(notice_statuses_list, list):
        raise TEDSWSPipelineDAGException(f"The variable must be a JSON-encoded list of strings.\n{error_message}")

    validated_statuses = []
    for item in notice_statuses_list:
        if not isinstance(item, str):
            raise TEDSWSPipelineDAGException(f"Expected string values in list, got {type(item).__name__}: {item}.\n{error_message}")
        try:
            validated_statuses.append(NoticeStatus[item])
        except KeyError:
            raise TEDSWSPipelineDAGException(f"Invalid notice status name: '{item}'\n{error_message}")

    return validated_statuses