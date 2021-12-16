
build-open-semantic-search:
	@ echo "Build open-semantic-search"
	@ cd infra && rm -rf open-semantic-search
	@ cd infra && git clone https://github.com/opensemanticsearch/open-semantic-search.git
	@ cd infra/open-semantic-search/ && ./build-deb
	@ echo "Patch open-semantic-search configs"
	@ cat infra/docker-compose-configs/open-semantic-search-compose-patch.yml > infra/open-semantic-search/docker-compose.yml

start-open-semantic-search:
	@ echo "Start open-semantic-search"
	@ cd infra/open-semantic-search/ && docker-compose build
	@ cd infra/open-semantic-search/ && docker-compose up -d


stop-open-semantic-search:
	@ echo "Stop open-semantic-search"
	@ cd infra/open-semantic-search/ && docker-compose rm -fsv