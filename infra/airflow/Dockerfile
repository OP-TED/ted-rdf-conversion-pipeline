FROM apache/airflow:2.2.4-python3.8

# quick sudo
USER root
RUN apt-get update && apt-get install make && apt-get install build-essential git -y

# back to normal user
USER airflow

# requirements.txt shall be made availble from the **ted-sws** GitHub repository
COPY requirements.txt /opt/airflow

# working in the /opt/airflow
WORKDIR /opt/airflow

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.2.4/constraints-no-providers-3.8.txt"
