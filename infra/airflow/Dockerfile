FROM apache/airflow:2.2.3-python3.8

# quick sudo
USER root
RUN apt-get update && apt-get install make && apt-get install build-essential git -y

# back to normal user
USER airflow

# requirements-airflow.txt shall be made availble from teh **sem-covid** GitHub repository
COPY requirements-airflow.txt /opt/airflow

# working in the /opt/airflow
WORKDIR /opt/airflow

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements-airflow.txt --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.2.3/constraints-no-providers-3.8.txt"
