FROM docker.io/apache/airflow:2.5.1-python3.8

# quick sudo
USER root

RUN apt-get update && apt-get install -y \
    build-essential=12.9 \
    default-jre=2:1.11-72 \
    git=1:2.30.2-1+deb11u2 \
    make=4.3-4.1 \
    wget=1.21-1+deb11u1 \
    unzip=6.0-26+deb11u1 \
    && rm -rf /var/lib/apt/lists/*

# back to normal user
USER airflow

COPY libraries /home/airflow
# requirements.txt shall be made availble from the **ted-sws** GitHub repository
COPY requirements.txt /opt/airflow

# working in the /opt/airflow
WORKDIR /opt/airflow

RUN mkdir -p ./dags ./ted_sws


RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.5.1/constraints-no-providers-3.8.txt"
