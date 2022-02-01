SHELL=/bin/bash -o pipefail
BUILD_PRINT = STEP:

CURRENT_UID := $(shell id -u)
export CURRENT_UID
#This are constants used for make targets so we can start prod and staging services on the same machine
STAGING := staging
PRODUCTION := prod
PROD_ENV_FILE := .env
STAGING_ENV_FILE := $(PROD_ENV_FILE).staging

# include .env files if they exist
-include .env
-include .env.staging

build-externals:
	@ echo "$(BUILD_PRINT)Creating the necessary volumes, networks and folders and setting the special rights"
	@ docker network create proxy-net || true


#SERVER SERVICES
start-traefik: build-externals
	@ echo "$(BUILD_PRINT)Starting the Traefik services"
	@ docker-compose --file ./infra/traefik/docker-compose.yml --env-file ${PROD_ENV_FILE} up -d

stop-traefik:
	@ echo "$(BUILD_PRINT)Stopping the Traefik services"
	@ docker-compose --file ./infra/traefik/docker-compose.yml --env-file ${PROD_ENV_FILE} down

start-portainer: build-externals
	@ echo "$(BUILD_PRINT)Starting the Portainer services"
	@ docker-compose --file ./infra/portainer/docker-compose.yml --env-file ${PROD_ENV_FILE} up -d

stop-portainer:
	@ echo "$(BUILD_PRINT)Stopping the Portainer services"
	@ docker-compose --file ./infra/portainer/docker-compose.yml --env-file ${PROD_ENV_FILE} down

start-server-services: | start-traefik start-portainer
stop-server-services: | stop-traefik stop-portainer

#PROJECT SERVICES
create-env-airflow:
	@ echo "$(BUILD_PRINT) Create Airflow env"
	@ mkdir -p infra/airflow/logs infra/airflow/plugins
#	@ cd infra/airflow/ && ln -s -f ../../dags && ln -s -f ../../ted_sws
	@ cd infra/airflow/ && ln -s -f ../../ted_sws
	@ echo -e "AIRFLOW_UID=$(CURRENT_UID)" >infra/airflow/.env

build-airflow: create-env-airflow build-externals
	@ echo "$(BUILD_PRINT) Build Airflow services"
	@ docker-compose -p ${PRODUCTION} --file ./infra/airflow/docker-compose.yaml --env-file ${PROD_ENV_FILE} build --no-cache --force-rm
	@ docker-compose -p ${PRODUCTION} --file ./infra/airflow/docker-compose.yaml --env-file ${PROD_ENV_FILE} up -d --force-recreate

start-airflow: build-externals
	@ echo "$(BUILD_PRINT)Starting Airflow servies"
	@ docker-compose -p ${PRODUCTION} --file ./infra/airflow/docker-compose.yaml --env-file ${PROD_ENV_FILE} up -d

stop-airflow:
	@ echo "$(BUILD_PRINT)Stoping Airflow services"
	@ docker-compose -p ${PRODUCTION} --file ./infra/airflow/docker-compose.yaml --env-file ${PROD_ENV_FILE} down

start-allegro-graph: build-externals
	@ echo "$(BUILD_PRINT)Starting Allegro-Graph servies"
	@ docker-compose -p ${PRODUCTION} --file ./infra/allegro-graph/docker-compose.yaml --env-file ${PROD_ENV_FILE} up -d

stop-allegro-graph:
	@ echo "$(BUILD_PRINT)Stoping Allegro-Graph services"
	@ docker-compose -p ${PRODUCTION} --file ./infra/allegro-graph/docker-compose.yaml --env-file ${PROD_ENV_FILE} down


build-elasticsearch: build-externals
	@ echo "$(BUILD_PRINT) Build Elasticsearch services"
	@ docker-compose -p ${PRODUCTION} --file ./infra/elasticsearch/docker-compose.yml --env-file ${PROD_ENV_FILE} build --no-cache --force-rm
	@ docker-compose -p ${PRODUCTION} --file ./infra/elasticsearch/docker-compose.yml --env-file ${PROD_ENV_FILE} up -d --force-recreate

start-elasticsearch: build-externals
	@ echo "$(BUILD_PRINT)Starting the Elasticsearch services"
	@ docker-compose -p ${PRODUCTION} --file ./infra/elasticsearch/docker-compose.yml --env-file ${PROD_ENV_FILE} up -d

stop-elasticsearch:
	@ echo "$(BUILD_PRINT)Stopping the Elasticsearch services"
	@ docker-compose -p ${PRODUCTION} --file ./infra/elasticsearch/docker-compose.yml --env-file ${PROD_ENV_FILE} down


start-minio: build-externals
	@ echo "$(BUILD_PRINT)Starting the Minio services"
	@ docker-compose -p ${PRODUCTION} --file ./infra/minio/docker-compose.yml --env-file ${PROD_ENV_FILE} up -d

stop-minio:
	@ echo "$(BUILD_PRINT)Stopping the Minio services"
	@ docker-compose -p ${PRODUCTION} --file ./infra/minio/docker-compose.yml --env-file ${PROD_ENV_FILE} down

start-mongo: build-externals
	@ echo "$(BUILD_PRINT)Starting the Minio services"
	@ docker-compose -p ${PRODUCTION} --file ./infra/mongo/docker-compose.yml --env-file ${PROD_ENV_FILE} up -d

stop-mongo:
	@ echo "$(BUILD_PRINT)Stopping the Minio services"
	@ docker-compose -p ${PRODUCTION} --file ./infra/mongo/docker-compose.yml --env-file ${PROD_ENV_FILE} down


start-project-prod-services: | start-airflow start-elasticsearch start-allegro-graph start-minio start-mongo
stop-project-prod-services: | stop-airflow stop-elasticsearch stop-allegro-graph stop-minio stop-mongo


start-airflow-staging: build-externals
	@ echo "$(BUILD_PRINT)Starting Airflow servies"
	@ docker-compose -p ${STAGING} --file ./infra/airflow/docker-compose.yaml --env-file ${STAGING_ENV_FILE} up -d

stop-airflow-staging:
	@ echo "$(BUILD_PRINT)Stoping Airflow services"
	@ docker-compose -p ${STAGING} --file ./infra/airflow/docker-compose.yaml --env-file ${STAGING_ENV_FILE} down

start-allegro-graph-staging: build-externals
	@ echo "$(BUILD_PRINT)Starting Allegro-Graph servies"
	@ docker-compose -p ${STAGING} --file ./infra/allegro-graph/docker-compose.yaml --env-file ${STAGING_ENV_FILE} up -d

stop-allegro-graph-staging:
	@ echo "$(BUILD_PRINT)Stoping Allegro-Graph services"
	@ docker-compose -p ${STAGING} --file ./infra/allegro-graph/docker-compose.yaml --env-file ${STAGING_ENV_FILE} down

start-elasticsearch-staging: build-externals
	@ echo "$(BUILD_PRINT)Starting the Elasticsearch services"
	@ docker-compose -p ${STAGING} --file ./infra/elasticsearch/docker-compose.yml --env-file ${STAGING_ENV_FILE} up -d

stop-elasticsearch-staging:
	@ echo "$(BUILD_PRINT)Stopping the Elasticsearch services"
	@ docker-compose -p ${STAGING} --file ./infra/elasticsearch/docker-compose.yml --env-file ${STAGING_ENV_FILE} down


start-minio-staging: build-externals
	@ echo "$(BUILD_PRINT)Starting the Minio services"
	@ docker-compose -p ${STAGING} --file ./infra/minio/docker-compose.yml --env-file ${STAGING_ENV_FILE} up -d

stop-minio-staging:
	@ echo "$(BUILD_PRINT)Stopping the Minio services"
	@ docker-compose -p ${STAGING} --file ./infra/minio/docker-compose.yml --env-file ${STAGING_ENV_FILE} down

start-mongo-staging: build-externals
	@ echo "$(BUILD_PRINT)Starting the Minio services"
	@ docker-compose -p ${STAGING} --file ./infra/mongo/docker-compose.yml --env-file ${STAGING_ENV_FILE} up -d

stop-mongo-staging:
	@ echo "$(BUILD_PRINT)Stopping the Minio services"
	@ docker-compose -p ${STAGING} --file ./infra/mongo/docker-compose.yml --env-file ${STAGING_ENV_FILE} down

start-project-staging-services: | start-airflow-staging start-elasticsearch-staging start-allegro-graph-staging start-minio-staging start-mongo-staging
stop-project-staging-services: | stop-airflow-staging stop-elasticsearch-staging stop-allegro-graph-staging stop-minio-staging stop-mongo-staging




#build-open-semantic-search:
#	@ echo "Build open-semantic-search"
#	@ cd infra && rm -rf open-semantic-search
#	@ cd infra && git clone --recurse-submodules --remote-submodules https://github.com/opensemanticsearch/open-semantic-search.git
#	@ cd infra/open-semantic-search/ && ./build-deb
#	@ echo "Patch open-semantic-search configs"
#	@ cat infra/docker-compose-configs/open-semantic-search-compose-patch.yml > infra/open-semantic-search/docker-compose.yml
#	@ cd infra/open-semantic-search/ && docker-compose rm -fsv
#	@ cd infra/open-semantic-search/ && docker-compose build
#
#start-open-semantic-search:
#	@ echo "Start open-semantic-search"
#	@ cd infra/open-semantic-search/ && docker-compose up -d
#
#
#stop-open-semantic-search:
#	@ echo "Stop open-semantic-search"
#	@ cd infra/open-semantic-search/ && docker-compose down
#
#
#start-silk-service:
#	@ echo "Start silk service"
#	@ cd infra/silk/ && docker-compose up -d
#
#stop-silk-service:
#	@ echo "Stop silk service"
#	@ cd infra/silk/ && docker-compose down

