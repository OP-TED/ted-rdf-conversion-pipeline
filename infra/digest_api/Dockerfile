FROM docker.io/python:3.8-slim-buster
EXPOSE 8000

WORKDIR /usr/src/api/id_manager
COPY ted_sws /usr/src/api/id_manager/ted_sws
COPY digest_service /usr/src/api/id_manager

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install -r project_requirements.txt

ENTRYPOINT uvicorn --host 0.0.0.0 --port 8000 ted_sws.notice_transformer.entrypoints.api.digest_service.main:app
