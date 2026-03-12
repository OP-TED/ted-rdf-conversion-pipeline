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

# Bake tool JARs into the image at /home/airflow so that airflow-init-lib can copy them
# at runtime into the airflow-opt ephemeral volume at /opt/airflow (per installation manual)
COPY --chown=airflow:root libraries /home/airflow

# requirements.txt must be available from the ted-sws GitHub repository
# Copy to /opt/airflow for pip install (pip runs at build time)
COPY requirements.txt /opt/airflow/requirements.txt

WORKDIR /opt/airflow

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt \
      --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.10.5/constraints-no-providers-3.10.txt"
