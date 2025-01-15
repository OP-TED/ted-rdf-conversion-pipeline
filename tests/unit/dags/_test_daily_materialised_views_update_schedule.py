# import os
#
# from airflow import DAG
# from airflow.models import DagBag, Variable
# from airflow.timetables.trigger import CronTriggerTimetable
#
# from ted_sws import DAG_MATERIALIZED_VIEW_UPDATE_DEFAULT_TIMETABLE
#
#
# def test_daily_materialised_view_change_timetable_from_airflow_variable_after_reparse(dag_bag: DagBag,
#                                                                                       dag_materialised_view_update_schedule_variable_name: str,
#                                                                                       daily_materialised_views_dag_id: str,
#                                                                                       example_dag_cron_table: CronTriggerTimetable,
#                                                                                       airflow_timetable_import_error_message: str):
#     daily_materialised_view_dag: DAG = dag_bag.get_dag(dag_id=daily_materialised_views_dag_id)
#
#     assert daily_materialised_view_dag is not None
#     assert daily_materialised_view_dag.schedule_interval != example_dag_cron_table._expression
#
#     Variable.set(key=dag_materialised_view_update_schedule_variable_name, value=example_dag_cron_table._expression)
#     dag_bag.collect_dags(only_if_updated=False)
#     daily_materialised_view_dag: DAG = dag_bag.get_dag(dag_id=daily_materialised_views_dag_id)
#
#     assert daily_materialised_view_dag is not None
#     assert daily_materialised_view_dag.schedule_interval == example_dag_cron_table._expression
#     assert all(airflow_timetable_import_error_message not in error for error in dag_bag.import_errors.values())
#
#
# def test_daily_materialised_view_change_timetable_from_env_variable_after_reparse(dag_bag: DagBag,
#                                                                                   dag_materialised_view_update_schedule_variable_name: str,
#                                                                                   daily_materialised_views_dag_id: str,
#                                                                                   example_dag_cron_table: CronTriggerTimetable,
#                                                                                   airflow_timetable_import_error_message: str):
#     fetcher_dag: DAG = dag_bag.get_dag(dag_id=daily_materialised_views_dag_id)
#
#     assert fetcher_dag is not None
#     assert fetcher_dag.schedule_interval != example_dag_cron_table._expression
#
#     os.environ[dag_materialised_view_update_schedule_variable_name] = example_dag_cron_table._expression
#     dag_bag.collect_dags(only_if_updated=False)
#     fetcher_dag: DAG = dag_bag.get_dag(dag_id=daily_materialised_views_dag_id)
#
#     assert fetcher_dag is not None
#     assert fetcher_dag.schedule_interval == example_dag_cron_table._expression
#     assert all(airflow_timetable_import_error_message not in error for error in dag_bag.import_errors.values())
#
#
# def test_daily_materialised_view_has_default_timetable_if_no_variable_is_set_after_reparse(dag_bag: DagBag,
#                                                                                            dag_materialised_view_update_schedule_variable_name: str,
#                                                                                            daily_materialised_views_dag_id: str,
#                                                                                            airflow_timetable_import_error_message: str):
#     env_var_value = os.getenv(dag_materialised_view_update_schedule_variable_name)
#     is_env_var_set: bool = True if env_var_value is not None else False
#     if is_env_var_set:
#         del os.environ[dag_materialised_view_update_schedule_variable_name]
#     airflow_var_value = Variable.get(key=dag_materialised_view_update_schedule_variable_name, default_var=None)
#     is_airflow_var_set: bool = True if airflow_var_value is not None else False
#     if is_airflow_var_set:
#         Variable.delete(key=dag_materialised_view_update_schedule_variable_name)
#
#     dag_bag.collect_dags(only_if_updated=False)
#     fetcher_dag: DAG = dag_bag.get_dag(dag_id=daily_materialised_views_dag_id)
#
#     assert fetcher_dag is not None
#     assert fetcher_dag.schedule_interval == DAG_MATERIALIZED_VIEW_UPDATE_DEFAULT_TIMETABLE
#     assert all(airflow_timetable_import_error_message not in error for error in dag_bag.import_errors.values())
#
#     if is_env_var_set:
#         os.environ[dag_materialised_view_update_schedule_variable_name] = env_var_value
#     if is_airflow_var_set:
#         Variable.set(key=dag_materialised_view_update_schedule_variable_name, value=airflow_var_value)
#
#
# def test_daily_materialised_view_gets_incorrect_timetable_after_reparse(dag_bag: DagBag,
#                                                                         dag_materialised_view_update_schedule_variable_name: str,
#                                                                         daily_materialised_views_dag_id: str,
#                                                                         example_wrong_cron_table: str,
#                                                                         airflow_timetable_import_error_message: str):
#     fetcher_dag: DAG = dag_bag.get_dag(dag_id=daily_materialised_views_dag_id)
#
#     assert fetcher_dag is not None
#
#     Variable.set(key=dag_materialised_view_update_schedule_variable_name, value=example_wrong_cron_table)
#
#     dag_bag.collect_dags(only_if_updated=False)
#
#     assert any(airflow_timetable_import_error_message in error for error in dag_bag.import_errors.values())
