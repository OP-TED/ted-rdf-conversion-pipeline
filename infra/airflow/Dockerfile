FROM docker.io/apache/airflow:2.10.5-python3.10

# quick sudo
USER root

RUN apt-get update && apt-get install -y \
    build-essential=12.9 \
    default-jre=2:1.17-74 \
    git=1:2.39.5-0+deb12u2 \
    make=4.3-4.1 \
    wget=1.21.3-1+deb12u1 \
    unzip=6.0-28 \
    gosu=1.14-1+b10 \
    && rm -rf /var/lib/apt/lists/*

# back to normal user
USER airflow

COPY libraries /opt/airflow
# requirements.txt shall be made availble from the **ted-sws** GitHub repository
COPY requirements.txt /opt/airflow

# working in the /opt/airflow
WORKDIR /opt/airflow

RUN mkdir -p ./dags ./ted_sws


RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.10.5/constraints-no-providers-3.10.txt"
