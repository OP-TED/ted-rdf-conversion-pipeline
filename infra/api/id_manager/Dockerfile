FROM python:3.8-slim-buster
EXPOSE $ID_MANAGER_API_PORT

WORKDIR /usr/src/api/id_manager
COPY . /usr/src/api/id_manager

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install -r infra/api/requirements.txt

ENTRYPOINT uvicorn --host 0.0.0.0 --port ${ID_MANAGER_API_PORT} ted_sws.id_manager.entrypoints.api.main:app --reload
