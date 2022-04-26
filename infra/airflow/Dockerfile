FROM apache/airflow:2.2.5-python3.8

# quick sudo
USER root
RUN apt-get update && apt-get install make && apt-get install build-essential git -y && apt-get install -y wget

# back to normal user
USER airflow

# requirements.txt shall be made availble from the **ted-sws** GitHub repository
COPY requirements.txt /opt/airflow

# working in the /opt/airflow
WORKDIR /opt/airflow
RUN wget -c https://github.com/RMLio/rmlmapper-java/releases/download/v5.0.0/rmlmapper-5.0.0-r362-all.jar -P .rmlmapper/
RUN mv .rmlmapper/rmlmapper-5.0.0-r362-all.jar .rmlmapper/rmlmapper.jar 2>/dev/null

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.2.5/constraints-no-providers-3.8.txt"
