from typing import Any

from airflow.operators.python import get_current_context

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
