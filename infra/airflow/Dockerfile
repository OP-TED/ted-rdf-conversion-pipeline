FROM apache/airflow:2.2.5-python3.8

# quick sudo
USER root
RUN apt-get update && apt-get install make && apt-get install build-essential git -y && apt-get install -y wget
RUN apt install -y default-jre

# back to normal user
USER airflow

# requirements.txt shall be made availble from the **ted-sws** GitHub repository
COPY requirements.txt /opt/airflow

# working in the /opt/airflow
WORKDIR /opt/airflow
RUN mkdir ./.rmlmapper
RUN wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1MckjzpvrCoChy_IRYC2S54tf3dFQNwEt' -O- | sed -rn \'s/.*confirm=\([0-9A-Za-z_]+).*/\1\n/p\'\)&id=1MckjzpvrCoChy_IRYC2S54tf3dFQNwEt" -O ./.rmlmapper/rmlmapper.jar && rm -rf /tmp/cookies.txt


RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.2.5/constraints-no-providers-3.8.txt"
