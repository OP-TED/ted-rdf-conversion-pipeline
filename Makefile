SHELL=/bin/bash -o pipefail
BUILD_PRINT = \e[1;34mSTEP:
END_BUILD_PRINT = \e[0m

CURRENT_UID := $(shell id -u)
export CURRENT_UID
# These are constants used for make targets so we can start prod and staging services on the same machine
ENV_FILE := .env

# include .env files if they exist
-include .env

PROJECT_PATH = $(shell pwd)
AIRFLOW_INFRA_FOLDER ?= ${PROJECT_PATH}/.airflow
RML_MAPPER_PATH = ${PROJECT_PATH}/.rmlmapper/rmlmapper.jar
XML_PROCESSOR_PATH = ${PROJECT_PATH}/.saxon/saxon-he-10.6.jar

#-----------------------------------------------------------------------------
# Dev commands
#-----------------------------------------------------------------------------
install: install-dev
	@ echo -e "$(BUILD_PRINT)Installing the requirements$(END_BUILD_PRINT)"
	@ pip install --upgrade pip
	@ pip install -r requirements.txt

install-dev:
	@ echo -e "$(BUILD_PRINT)Installing the dev requirements$(END_BUILD_PRINT)"
	@ pip install --upgrade pip
	@ pip install -r requirements.dev.txt

test: test-unit

test-unit:
	@ echo -e "$(BUILD_PRINT)Unit Testing ...$(END_BUILD_PRINT)"
	@ tox -e unit

test-features:
	@ echo -e "$(BUILD_PRINT)Gherkin Features Testing ...$(END_BUILD_PRINT)"
	@ tox -e features

test-e2e:
	@ echo -e "$(BUILD_PRINT)End to End Testing ...$(END_BUILD_PRINT)"
	@ tox -e e2e

test-all-parallel:
	@ echo -e "$(BUILD_PRINT)Complete Testing ...$(END_BUILD_PRINT)"
	@ tox -p

test-all:
	@ echo -e "$(BUILD_PRINT)Complete Testing ...$(END_BUILD_PRINT)"
	@ tox

build-externals:
	@ echo -e "$(BUILD_PRINT)Creating the necessary volumes, networks and folders and setting the special rights"
	@ docker network create proxy-net || true
	@ docker network create common-ext-${ENVIRONMENT} || true


#-----------------------------------------------------------------------------
# SERVER SERVICES
#-----------------------------------------------------------------------------
start-traefik: build-externals
	@ echo -e "$(BUILD_PRINT)Starting the Traefik services $(END_BUILD_PRINT)"
	@ docker-compose -p common --file ./infra/traefik/docker-compose.yml --env-file ${ENV_FILE} up -d

stop-traefik:
	@ echo -e "$(BUILD_PRINT)Stopping the Traefik services $(END_BUILD_PRINT)"
	@ docker-compose -p common --file ./infra/traefik/docker-compose.yml --env-file ${ENV_FILE} down

start-portainer: build-externals
	@ echo -e "$(BUILD_PRINT)Starting the Portainer services $(END_BUILD_PRINT)"
	@ docker-compose -p common --file ./infra/portainer/docker-compose.yml --env-file ${ENV_FILE} up -d

stop-portainer:
	@ echo -e "$(BUILD_PRINT)Stopping the Portainer services $(END_BUILD_PRINT)"
	@ docker-compose -p common --file ./infra/portainer/docker-compose.yml --env-file ${ENV_FILE} down

start-server-services: | start-traefik start-portainer
stop-server-services: | stop-traefik stop-portainer

#-----------------------------------------------------------------------------
# PROJECT SERVICES
#-----------------------------------------------------------------------------
create-env-airflow:
	@ echo -e "$(BUILD_PRINT) Create Airflow env $(END_BUILD_PRINT)"
	@ echo -e "$(BUILD_PRINT) ${AIRFLOW_INFRA_FOLDER} ${ENVIRONMENT} $(END_BUILD_PRINT)"
	@ mkdir -p ${AIRFLOW_INFRA_FOLDER}/logs ${AIRFLOW_INFRA_FOLDER}/plugins ${AIRFLOW_INFRA_FOLDER}/.env
	@ ln -s -f -n ${PROJECT_PATH}/dags ${AIRFLOW_INFRA_FOLDER}/dags
	@ ln -s -f -n ${PROJECT_PATH}/ted_sws ${AIRFLOW_INFRA_FOLDER}/ted_sws
	@ chmod 777 ${AIRFLOW_INFRA_FOLDER}/logs ${AIRFLOW_INFRA_FOLDER}/plugins ${AIRFLOW_INFRA_FOLDER}/.env
	@ cp requirements.txt ./infra/airflow/

build-airflow: guard-ENVIRONMENT create-env-airflow build-externals
	@ echo -e "$(BUILD_PRINT) Build Airflow services $(END_BUILD_PRINT)"
	@ docker-compose -p ${ENVIRONMENT} --file ./infra/airflow/docker-compose.yaml --env-file ${ENV_FILE} build --no-cache --force-rm
	@ docker-compose -p ${ENVIRONMENT} --file ./infra/airflow/docker-compose.yaml --env-file ${ENV_FILE} up -d --force-recreate

start-airflow: build-externals
	@ echo -e "$(BUILD_PRINT)Starting Airflow servies $(END_BUILD_PRINT)"
	@ docker-compose -p ${ENVIRONMENT} --file ./infra/airflow/docker-compose.yaml --env-file ${ENV_FILE} up -d

stop-airflow:
	@ echo -e "$(BUILD_PRINT)Stoping Airflow services $(END_BUILD_PRINT)"
	@ docker-compose -p ${ENVIRONMENT} --file ./infra/airflow/docker-compose.yaml --env-file ${ENV_FILE} down

#	------------------------
start-allegro-graph: build-externals
	@ echo -e "$(BUILD_PRINT)Starting Allegro-Graph servies $(END_BUILD_PRINT)"
	@ docker-compose -p ${ENVIRONMENT} --file ./infra/allegro-graph/docker-compose.yml --env-file ${ENV_FILE} up -d

stop-allegro-graph:
	@ echo -e "$(BUILD_PRINT)Stoping Allegro-Graph services $(END_BUILD_PRINT)"
	@ docker-compose -p ${ENVIRONMENT} --file ./infra/allegro-graph/docker-compose.yml --env-file ${ENV_FILE} down

#	------------------------
build-elasticsearch: build-externals
	@ echo -e "$(BUILD_PRINT) Build Elasticsearch services $(END_BUILD_PRINT)"
	@ docker-compose -p ${ENVIRONMENT} --file ./infra/elasticsearch/docker-compose.yml --env-file ${ENV_FILE} build --no-cache --force-rm
	@ docker-compose -p ${ENVIRONMENT} --file ./infra/elasticsearch/docker-compose.yml --env-file ${ENV_FILE} up -d --force-recreate

start-elasticsearch: build-externals
	@ echo -e "$(BUILD_PRINT)Starting the Elasticsearch services $(END_BUILD_PRINT)"
	@ docker-compose -p ${ENVIRONMENT} --file ./infra/elasticsearch/docker-compose.yml --env-file ${ENV_FILE} up -d

stop-elasticsearch:
	@ echo -e "$(BUILD_PRINT)Stopping the Elasticsearch services $(END_BUILD_PRINT)"
	@ docker-compose -p ${ENVIRONMENT} --file ./infra/elasticsearch/docker-compose.yml --env-file ${ENV_FILE} down


start-minio: build-externals
	@ echo -e "$(BUILD_PRINT)Starting the Minio services $(END_BUILD_PRINT)"
	@ docker-compose -p ${ENVIRONMENT} --file ./infra/minio/docker-compose.yml --env-file ${ENV_FILE} up -d

stop-minio:
	@ echo -e "$(BUILD_PRINT)Stopping the Minio services $(END_BUILD_PRINT)"
	@ docker-compose -p ${ENVIRONMENT} --file ./infra/minio/docker-compose.yml --env-file ${ENV_FILE} down


start-mongo: build-externals
	@ echo -e "$(BUILD_PRINT)Starting the Mongo services $(END_BUILD_PRINT)"
	@ docker-compose -p ${ENVIRONMENT} --file ./infra/mongo/docker-compose.yml --env-file ${ENV_FILE} up -d

stop-mongo:
	@ echo -e "$(BUILD_PRINT)Stopping the Mongo services $(END_BUILD_PRINT)"
	@ docker-compose -p ${ENVIRONMENT} --file ./infra/mongo/docker-compose.yml --env-file ${ENV_FILE} down

init-rml-mapper:
	@ echo -e "RMLMapper folder initialisation!"
	@ wget -c https://github.com/RMLio/rmlmapper-java/releases/download/v5.0.0/rmlmapper-5.0.0-r362-all.jar -P .rmlmapper/
	@ mv .rmlmapper/rmlmapper-5.0.0-r362-all.jar .rmlmapper/rmlmapper.jar 2>/dev/null

init-saxon:
	@ echo -e "$(BUILD_PRINT)Saxon folder initialization $(END_BUILD_PRINT)"
	@ wget -c https://kumisystems.dl.sourceforge.net/project/saxon/Saxon-HE/10/Java/SaxonHE10-6J.zip -P .saxon/
	@ cd .saxon && unzip SaxonHE10-6J.zip && rm -rf SaxonHE10-6J.zip

start-project-services: | start-airflow start-mongo init-rml-mapper
stop-project-services: | stop-airflow stop-mongo

#-----------------------------------------------------------------------------
# VAULT SERVICES
#-----------------------------------------------------------------------------
# Testing whether an env variable is set or not
guard-%:
	@ if [ "${${*}}" = "" ]; then \
        echo -e "$(BUILD_PRINT)Environment variable $* not set $(END_BUILD_PRINT)"; \
        exit 1; \
	fi

# Testing that vault is installed
vault-installed: #; @which vault1 > /dev/null
	@ if ! hash vault 2>/dev/null; then \
        echo -e "$(BUILD_PRINT)Vault is not installed, refer to https://www.vaultproject.io/downloads $(END_BUILD_PRINT)"; \
        exit 1; \
	fi
# Get secrets in dotenv format
staging-dotenv-file: guard-VAULT_ADDR guard-VAULT_TOKEN vault-installed
	@ echo -e "$(BUILD_PRINT)Creating .env.staging file $(END_BUILD_PRINT)"
	@ echo VAULT_ADDR=${VAULT_ADDR} > .env
	@ echo VAULT_TOKEN=${VAULT_TOKEN} >> .env
	@ echo DOMAIN=ted-data.eu >> .env
	@ echo ENVIRONMENT=staging >> .env
	@ echo SUBDOMAIN=staging. >> .env
	@ echo RML_MAPPER_PATH=${RML_MAPPER_PATH} >> .env
	@ echo ELK_HOST=localhost >> .env
	@ echo ELK_PORT=5959 >> .env
	@ echo ELK_VERSION=1 >> .env
	@ echo LOGGING_TYPE=PY,ELK >> .env
	@ echo XML_PROCESSOR_PATH=${XML_PROCESSOR_PATH} >> .env
	@ echo AIRFLOW_INFRA_FOLDER=~/airflow-infra/staging >> .env
	@ vault kv get -format="json" ted-staging/airflow | jq -r ".data.data | keys[] as \$$k | \"\(\$$k)=\(.[\$$k])\"" >> .env
	@ vault kv get -format="json" ted-staging/mongo-db | jq -r ".data.data | keys[] as \$$k | \"\(\$$k)=\(.[\$$k])\"" >> .env

dev-dotenv-file: guard-VAULT_ADDR guard-VAULT_TOKEN vault-installed
	@ echo -e "$(BUILD_PRINT)Create .env file $(END_BUILD_PRINT)"
	@ echo VAULT_ADDR=${VAULT_ADDR} > .env
	@ echo VAULT_TOKEN=${VAULT_TOKEN} >> .env
	@ echo DOMAIN=localhost >> .env
	@ echo ENVIRONMENT=dev >> .env
	@ echo SUBDOMAIN= >> .env
	@ echo RML_MAPPER_PATH=${RML_MAPPER_PATH} >> .env
	@ echo ELK_HOST=localhost >> .env
	@ echo ELK_PORT=5959 >> .env
	@ echo ELK_VERSION=1 >> .env
	@ echo LOGGING_TYPE=PY,ELK >> .env
	@ echo XML_PROCESSOR_PATH=${XML_PROCESSOR_PATH} >> .env
	@ echo AIRFLOW_INFRA_FOLDER=${AIRFLOW_INFRA_FOLDER} >> .env
	@ vault kv get -format="json" ted-dev/airflow | jq -r ".data.data | keys[] as \$$k | \"\(\$$k)=\(.[\$$k])\"" >> .env
	@ vault kv get -format="json" ted-dev/mongo-db | jq -r ".data.data | keys[] as \$$k | \"\(\$$k)=\(.[\$$k])\"" >> .env


prod-dotenv-file: guard-VAULT_ADDR guard-VAULT_TOKEN vault-installed
	@ echo -e "$(BUILD_PRINT)Create .env file $(END_BUILD_PRINT)"
	@ echo VAULT_ADDR=${VAULT_ADDR} > .env
	@ echo VAULT_TOKEN=${VAULT_TOKEN} >> .env
	@ echo DOMAIN=ted-data.eu >> .env
	@ echo ENVIRONMENT=prod >> .env
	@ echo SUBDOMAIN= >> .env
	@ echo RML_MAPPER_PATH=${RML_MAPPER_PATH} >> .env
	@ echo ELK_HOST=localhost >> .env
	@ echo ELK_PORT=5959 >> .env
	@ echo ELK_VERSION=1 >> .env
	@ echo LOGGING_TYPE=PY,ELK >> .env
	@ echo XML_PROCESSOR_PATH=${XML_PROCESSOR_PATH} >> .env
	@ echo AIRFLOW_INFRA_FOLDER=~/airflow-infra/prod >> .env
	@ vault kv get -format="json" ted-prod/airflow | jq -r ".data.data | keys[] as \$$k | \"\(\$$k)=\(.[\$$k])\"" >> .env
	@ vault kv get -format="json" ted-prod/mongo-db | jq -r ".data.data | keys[] as \$$k | \"\(\$$k)=\(.[\$$k])\"" >> .env

local-dotenv-file: rml-mapper-path-add-dotenv-file elk-add-dotenv-file logging-add-dotenv-file

rml-mapper-path-add-dotenv-file:
	@ echo -e "$(BUILD_PRINT)Add rml-mapper path to local .env file $(END_BUILD_PRINT)"
	@ sed -i '/^RML_MAPPER_PATH/d' .env
	@ echo RML_MAPPER_PATH=${RML_MAPPER_PATH} >> .env

elk-add-dotenv-file:
	@ echo -e "$(BUILD_PRINT)Add elk config to local .env file $(END_BUILD_PRINT)"
	@ sed -i '/^ELK_HOST/d' .env
	@ echo ELK_HOST=localhost >> .env
	@ sed -i '/^ELK_PORT/d' .env
	@ echo ELK_PORT=5959 >> .env
	@ sed -i '/^ELK_VERSION/d' .env
	@ echo ELK_VERSION=1 >> .env

logging-add-dotenv-file:
	@ echo -e "$(BUILD_PRINT)Add logging config to local .env file $(END_BUILD_PRINT)"
	@ sed -i '/^LOGGING_TYPE/d' .env
	@ echo LOGGING_TYPE=PY,ELK >> .env

refresh-normaliser-mapping-files:
	@ python -m ted_sws.metadata_normaliser.entrypoints.generate_mapping_resources

#clean-mongo-db:
#	@ export PYTHONPATH=$(PWD) && python ./tests/clean_mongo_db.py


#build-open-semantic-search:
#	@ echo -e "Build open-semantic-search"
#	@ cd infra && rm -rf open-semantic-search
#	@ cd infra && git clone --recurse-submodules --remote-submodules https://github.com/opensemanticsearch/open-semantic-search.git
#	@ cd infra/open-semantic-search/ && ./build-deb
#	@ echo -e "Patch open-semantic-search configs"
#	@ cat infra/docker-compose-configs/open-semantic-search-compose-patch.yml > infra/open-semantic-search/docker-compose.yml
#	@ cd infra/open-semantic-search/ && docker-compose rm -fsv
#	@ cd infra/open-semantic-search/ && docker-compose build
#
#start-open-semantic-search:
#	@ echo -e "Start open-semantic-search"
#	@ cd infra/open-semantic-search/ && docker-compose up -d
#
#
#stop-open-semantic-search:
#	@ echo -e "Stop open-semantic-search"
#	@ cd infra/open-semantic-search/ && docker-compose down
#
#
#start-silk-service:
#	@ echo -e "Start silk service"
#	@ cd infra/silk/ && docker-compose up -d
#
#stop-silk-service:
#	@ echo -e "Stop silk service"
#	@ cd infra/silk/ && docker-compose down