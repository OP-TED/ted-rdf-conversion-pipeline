FROM docker.io/python:3.8-slim-buster
EXPOSE 8000

WORKDIR /usr/src/api/id_manager
COPY . /usr/src/api/id_manager/
COPY digest_service /usr/src/api/id_manager

RUN pip install --upgrade pip
RUN pip install -r digest_service/requirements.txt
RUN pip install -r digest_service/project_requirements.txt

# Create a non-root user and group
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set the appropriate permissions for the directories and files
RUN chown -R appuser:appuser /usr/src/api/id_manager

# Switch to the non-root user
USER appuser

ENTRYPOINT uvicorn --host 0.0.0.0 --port 8000 ted_sws.notice_transformer.entrypoints.api.digest_service.main:app
