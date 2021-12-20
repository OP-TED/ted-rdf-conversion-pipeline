
build-open-semantic-search:
	@ echo "Build open-semantic-search"
	@ cd infra && rm -rf open-semantic-search
	@ cd infra && git clone --recurse-submodules --remote-submodules https://github.com/opensemanticsearch/open-semantic-search.git
	@ cd infra/open-semantic-search/ && ./build-deb
	@ echo "Patch open-semantic-search configs"
	@ cat infra/docker-compose-configs/open-semantic-search-compose-patch.yml > infra/open-semantic-search/docker-compose.yml
	@ cd infra/open-semantic-search/ && docker-compose rm -fsv
	@ cd infra/open-semantic-search/ && docker-compose build

start-open-semantic-search:
	@ echo "Start open-semantic-search"
	@ cd infra/open-semantic-search/ && docker-compose up -d


stop-open-semantic-search:
	@ echo "Stop open-semantic-search"
	@ cd infra/open-semantic-search/ && docker-compose down


start-silk-service:
	@ echo "Start silk service"
	@ cd infra/silk/ && docker-compose up -d

stop-silk-service:
	@ echo "Stop silk service"
	@ cd infra/silk/ && docker-compose down

