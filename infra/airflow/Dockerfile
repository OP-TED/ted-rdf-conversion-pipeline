FROM docker.io/apache/airflow:2.4.1-python3.8

# quick sudo
USER root
RUN apt-get update && apt-get install make && apt-get install build-essential git -y && apt-get install -y wget && apt-get install -y unzip
RUN apt install -y default-jre

# back to normal user
USER airflow

# requirements.txt shall be made availble from the **ted-sws** GitHub repository
COPY requirements.txt /opt/airflow

# working in the /opt/airflow
WORKDIR /opt/airflow
RUN mkdir -p ./.rmlmapper ./dags ./ted_sws ./temp
RUN wget -c https://github.com/RMLio/rmlmapper-java/releases/download/v6.0.0/rmlmapper-6.0.0-r363-all.jar -O ./.rmlmapper/rmlmapper.jar


RUN wget -c https://kumisystems.dl.sourceforge.net/project/saxon/Saxon-HE/10/Java/SaxonHE10-6J.zip -P .saxon/
RUN cd .saxon && unzip SaxonHE10-6J.zip && rm -rf SaxonHE10-6J.zip

RUN mkdir -p ./.limes
RUN wget -c https://github.com/dice-group/LIMES/releases/download/1.7.9/limes.jar -P ./.limes


RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.4.1/constraints-no-providers-3.8.txt"
