FROM apache/airflow:2.2.5-python3.8

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
RUN mkdir -p ./.rmlmapper
RUN wget -c https://api.bitbucket.org/2.0/repositories/Dragos0000/rml-mapper/src/master/rmlmapper.jar -P ./.rmlmapper


RUN wget -c https://kumisystems.dl.sourceforge.net/project/saxon/Saxon-HE/10/Java/SaxonHE10-6J.zip -P .saxon/
RUN cd .saxon && unzip SaxonHE10-6J.zip && rm -rf SaxonHE10-6J.zip


RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.2.5/constraints-no-providers-3.8.txt"
