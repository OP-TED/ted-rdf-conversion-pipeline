import pandas as pd


def filter_df_by_variables(df: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """
    Filter a dataframe by different variables
    :param df:
    :param kwargs:
    :return:
    """
    query_string = " and ".join([f"{key}=='{value}'" for key, value in kwargs.items() if value])
    return df.query(query_string)
