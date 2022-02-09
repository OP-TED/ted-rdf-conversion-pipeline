
SHELL=/bin/bash -o pipefail
BUILD_PRINT = \e[1;34mSTEP:
END_BUILD_PRINT = \e[0m

#-----------------------------------------------------------------------------
# PIP Install commands
#-----------------------------------------------------------------------------

install:
	@ echo -e "$(BUILD_PRINT)Installing the requirements$(END_BUILD_PRINT)"
	@ pip install --upgrade pip
	@ pip install -r requirements.dev.txt

test:
	@ echo -e "$(BUILD_PRINT)Testing ...$(END_BUILD_PRINT)"
	@ pytest


build-open-semantic-search:
	@ echo -e "$(BUILD_PRINT)Build open-semantic-search$(END_BUILD_PRINT)"
	@ cd infra && rm -rf open-semantic-search
	@ cd infra && git clone --recurse-submodules --remote-submodules https://github.com/opensemanticsearch/open-semantic-search.git
	@ cd infra/open-semantic-search/ && ./build-deb
	@ echo -e "Patch open-semantic-search configs$(END_BUILD_PRINT)"
	@ cat infra/docker-compose-configs/open-semantic-search-compose-patch.yml > infra/open-semantic-search/docker-compose.yml
	@ cd infra/open-semantic-search/ && docker-compose rm -fsv
	@ cd infra/open-semantic-search/ && docker-compose build


start-open-semantic-search:
	@ echo -e "$(BUILD_PRINT)Start open-semantic-search$(END_BUILD_PRINT)"
	@ cd infra/open-semantic-search/ && docker-compose up -d


stop-open-semantic-search:
	@ echo -e "$(BUILD_PRINT)Stop open-semantic-search$(END_BUILD_PRINT)"
	@ cd infra/open-semantic-search/ && docker-compose down


start-silk-service:
	@ echo -e "$(BUILD_PRINT)Start silk service$(END_BUILD_PRINT)"
	@ cd infra/silk/ && docker-compose up -d


stop-silk-service:
	@ echo -e "$(BUILD_PRINT)Stop silk service$(END_BUILD_PRINT)"
	@ cd infra/silk/ && docker-compose down

